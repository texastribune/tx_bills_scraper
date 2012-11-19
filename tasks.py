from celery.decorators import task
from fabfile.extractors import data_extractor
from fabfile import storage
import os

@task
def scrap(session, bill, **kwargs):
    data = data_extractor(session, bill)
    data['session'] = session
    data['bill'] = bill

    if 'DEBUG' in os.environ:
        from pprint import PrettyPrinter
        pp = PrettyPrinter(indent=2)
        pp.pprint(data)
    else:
        storage.store(data, scrap.get_logger(**kwargs))

