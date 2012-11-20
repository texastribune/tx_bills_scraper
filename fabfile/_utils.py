from fabric.api import *
from fabric.decorators import task
import glob
import re

URL_TEMPLATE = "http://www.capitol.state.tx.us/BillLookup/History.aspx?LegSess=%s&Bill=%s"
TEXT_URL_TEMPLATE = "http://www.capitol.state.tx.us/BillLookup/Text.aspx?LegSess=%s&Bill=%s"
LEG_URL_TEMPLATE = "http://www.legis.state.tx.us/Reports/BillsBy.aspx?cboLegSess=%s"
LEGISLATOR_URL_TEMPLATE = "http://www.legdir.legis.state.tx.us/MemberInfo.aspx?Chamber=%s&Code=%s"

base_extraction = re.compile('([A-Z]{2})0*([1-9][0-9]*).\.[hH][tT][mM]')
type_map = {
    'HC': 'HCR',
    'HJ': 'HJR',
    'SC': 'SCR',
    'SJ': 'SJR',
}

def extract_bill_from_file(file):
    """
    Takes a file in the schema in available on the state FTP site and turns it
    into the expected bill ID that can be passed to the state website.
    """
    matches = base_extraction.match(file)
    if not matches:
        return None
    type, number = matches.groups()

    # This bill is injected for fun to test things apparently.  We need to
    # ignore it because it doesn't really exist.
    if number == "9000":
        return None

    if type in type_map:
        type = type_map[type]
    return ''.join((type, number))


def convert_to_url(session, file):
    """
    Converts a session and FTP file name to the URL for the state site.
    """
    return to_url(session, extract_bill_from_file(file))


def to_url(session, bill):
    """
    Returns a URL for a given legislative session and bill ID
    """
    return URL_TEMPLATE % (session, bill)


def to_leg_url(session):
    """
    Returns a URL for a given legislative session
    """
    return LEG_URL_TEMPLATE % (session)


def to_text_url(session, bill):
    return TEXT_URL_TEMPLATE % (session, bill)


def unique_bills(session, bill_path):
    bill_files = glob.glob('%s/%s/*/*/*.htm' % (bill_path, session))
    if not bill_files:
        bill_files = glob.glob('%s/%s/*/*/*.HTM' % (bill_path, session))
    bills = []
    for bill_file in bill_files:
        bill = extract_bill_from_file(bill_file.split('/')[-1])
        if bill and not bill in bills:
            bills.append(bill)
    return bills
