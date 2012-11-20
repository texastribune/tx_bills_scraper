To test without a local CouchDB instance:
============

In /path/to/texastribune/data.texastribune.org/bills-scraper:

1. celeryconfig.py

  Uncomment this line:

    CELERY_ALWAYS_EAGER = True

2. fabfile/storage.py

  Comment out lines 13-14:

    couch = couchdb.Server('http://tswicegood:password@127.0.0.1:5984/')

    db = couch['texas']

3. tasks.py

  Make sure DEBUG is set to true (see line 13):

    if 'DEBUG' in os.environ:
        from pprint import PrettyPrinter
        pp = PrettyPrinter(indent=2)
        pp.pprint(data)

4. Run 'fab scrape', passing in valid session and bill IDs, e.g.:

    fab scrape:83R,HB25

