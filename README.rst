Testing locally
============

In /path/to/texastribune/tx_bills_scraper/:

1. In celeryconfig.py, uncomment this line:

:: 
    CELERY_ALWAYS_EAGER = True


Bill scraper - testing locally
============

2. Set DEBUG to True and run 'fab scrape', passing in valid session and bill IDs, e.g.:

::
    DEBUG=1 fab scrape:83R,HB25


Legislator scraper - testing locally
============

2. Set DEBUG to True and run 'fab scrape', passing in a valid session, e.g.:

::    
    DEBUG=1 fab scrape_leg:83R

