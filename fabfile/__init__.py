from . import storage
from .extractors import data_extractor
from ._utils import *
import os
import sys

import tasks


DEFAULT_BILL_PATH = "BILL_PATH" in os.environ and os.environ["BILL_PATH"] or os.path.expanduser("~/work/tt/tt_bills_data")
DEFAULT_SESSION="82R"
STATE_FTP = "ftp.legis.state.tx.us"
FTP_MIRROR_COMMAND = """
open %s
cd /bills/%s/billtext/html
mirror --parallel=5
""".strip()

# TODO: make sure to parse available versions as part of this
@task
def scrape(session, bill):
    return tasks.scrape.delay(session, bill)


@task
def scrape_leg(session):
    return tasks.scrape_leg.delay(session)


@task
def scrape_all(session=DEFAULT_SESSION, bill_prefix=None, bill_path=DEFAULT_BILL_PATH):
    bills = unique_bills(session, bill_path)
    print "scraping %d bills" % len(bills)
    queued = []
    finished = []
    counter = 0
    for bill in bills:
        counter += 1
        if counter % 10 is 0:
            sys.stdout.write(".")
            sys.stdout.flush()
        if bill_prefix and not bill_prefix == bill[0:len(bill_prefix)]:
            continue
        queued.append(scrape(session, bill))

    timeout = 1200
    counter = 0
    import time
    while True:
        time.sleep(1)
        counter += 1
        if counter > timeout:
            print "Ran out of time?"
            sys.exit(1)
        for a in queued:
            if a.ready() and not a in finished:
                finished.append(a)
        print "%d finished, %d remaining" % (len(finished), len(queued) - len(finished))
        if len(queued) == len(finished):
            break


@task
def sync(session=DEFAULT_SESSION, bill_path=DEFAULT_BILL_PATH):
    full_bill_path = "%s/%s" % (bill_path, session)
    local("if [ ! -d '%s' ]; then mkdir %s; fi" % (full_bill_path, full_bill_path))
    with cd(full_bill_path):
        local("lftp -c \"%s\"" % FTP_MIRROR_COMMAND % (STATE_FTP, session), capture=False)
    print local("date")

@task
def sync_all():
    # TODO: make this query the FTP server for it
    all_sessions_online = [
        '781', '782', '783', '784', '78R', '791', '792', '793', '79R', '80R',
        '811', '81R', '82R', '83R', 
    ]

    for session in all_sessions_online:
        sync(session)

RABBIT_PASSWORD = "va5byzilgul0nuip"
RABBIT_VHOST = "org.texastribune.bills"
RABBIT_USER = "bills"

@task
def init_rabbitmq():
    local("rabbitmqctl add_user %s %s" % (RABBIT_USER, RABBIT_PASSWORD))
    local("rabbitmqctl add_vhost %s" % RABBIT_VHOST)
    local('rabbitmqctl set_permissions -p %s %s ".*" ".*" ".*"' % (RABBIT_VHOST, RABBIT_USER))

