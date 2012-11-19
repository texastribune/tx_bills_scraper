import couchdb
import sys
import re

BILL_TYPE_EXTRACTOR = re.compile('^([HS][CJRB]{1,2})')

def extract_type(type):
    result = BILL_TYPE_EXTRACTOR.search(type)
    if not result:
        raise Exception("Unable to determine type")
    return result.groups()[0]

couch = couchdb.Server('http://tswicegood:password@127.0.0.1:5984/')
db = couch['texas']

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
