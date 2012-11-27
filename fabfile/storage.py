# import couchdb
import sys
import re
import MySQLdb as Database

# from django.conf import settings
# from texastribune.officials.models import Name

BILL_TYPE_EXTRACTOR = re.compile('^([HS][CJRB]{1,2})')

def extract_type(type):
    result = BILL_TYPE_EXTRACTOR.search(type)
    if not result:
        raise Exception("Unable to determine type")
    return result.groups()[0]

"""
TODO: rewrite this to store to a collection of Postgres tables
(since this is tied to officials, can't do the Postgres conversion until that app is also converted)
"""
# couch = couchdb.Server('http://tswicegood:password@127.0.0.1:5984/')
# db = couch['texas']

def store(data, log=None):
    data['_id'] = "%s-%s" % (data['session'], data['bill'])
    data['bill_type'] = extract_type(data['bill'])
    data['chamber'] = data['bill_type'][0:1]
    data['type'] = 'bill'
    log.debug("attempting to store: %s" % data['_id'])
    try:
        new_data = db[data['_id']]
        log.debug("updating existing data")
        new_data.update(data)
    except couchdb.http.ResourceNotFound:
        log.debug("creating new data")
        new_data = data
    db.save(new_data)
    log.debug("bill %s successfully saved" % data['_id'])

def store_leg_name(data, session):
    """
    Store legislator's (officeholder's) designated name for a given session
    """
    # db = settings.DATABASES['default']
    db = Database.connect("localhost", "root", "", "tribune_dev") # mysql5dev
    cursor = db.cursor()

    for datum in data:
        # print datum["leg_id"], session, datum["name"]
        sql = """INSERT INTO officials_name(officeholder_id, session_id, name)
                 SELECT * FROM 
                 (SELECT officials_officeholder.id FROM officials_officeholder 
                     WHERE officials_officeholder.lege_code = '%s') AS officeholder_id, 
                 (SELECT officials_session.id FROM officials_session 
                     WHERE officials_session.session = '%s') AS session_id, 
                 (SELECT '%s') AS name 
                 ON DUPLICATE KEY UPDATE 
                     name='%s';""" % (datum["leg_id"], session, datum["name"].strip(), datum["name"].strip())
        # print sql
        cursor.execute(sql)

    cursor.close()
    db.close()

