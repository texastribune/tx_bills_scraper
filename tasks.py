from celery.decorators import task
from fabfile.extractors import data_extractor, leg_extractor
from fabfile import storage
import os

@task
def scrape(session, bill, **kwargs):
    """
    Scrape for a specific session/bill combination
    """
    data = data_extractor(session, bill)
    data['session'] = session
    data['bill'] = bill

    if 'DEBUG' in os.environ:
        from pprint import PrettyPrinter
        pp = PrettyPrinter(indent=2)
        pp.pprint(data)
    else:
        storage.store(data, scrape.get_logger(**kwargs))

@task
def scrape_leg(session):
    """
    Scrape for a simple list of legislators in a specific session
    """
    data = leg_extractor(session)

    from pprint import PrettyPrinter
    pp = PrettyPrinter(indent=2)
    pp.pprint(data)

    """
    For the move to postgres, don't do the storage here.
    Call the scraper from the bills app and store it through
    the models.
    """
    # storage.store(data, scrape.get_logger(**kwargs))

    return data

