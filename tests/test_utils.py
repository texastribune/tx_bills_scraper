from nose.tools import eq_
from fabfile._utils import convert_to_url
from fabfile._utils import extract_bill_from_file
from fabfile._utils import to_url
from fabfile._utils import to_text_url
import random

house_data = (
    ("HB16", "HB00016I.htm"),
    ("HCR17", "HC00017I.htm"),
    ("HJR5", "HJ00005I.htm"),
    ("HR16", "HR00016I.htm"),
)

def test_can_extract_house_info():
    for expected, raw in house_data:
        eq_(expected, extract_bill_from_file(raw))

def test_can_handle_stupid_test_data():
    eq_(None, extract_bill_from_file("HB09000H.htm"))

senate_data = (
    ("SB26", "SB00026I.htm"),
    ("SR12", "SR00012I.htm"),
    ("SJR12", "SJ00012I.htm"),
    ("SCR2", "SC00002I.htm"),
)

def test_can_extract_senate_info():
    for expected, raw in senate_data:
        eq_(expected, extract_bill_from_file(raw))

def test_can_turn_a_session_and_billtext_file_into_a_url():
    session = "82R"
    url_template = "http://www.capitol.state.tx.us/BillLookup/History.aspx?LegSess=%s&Bill=%s"
    data = house_data + senate_data
    for id, billtext in data:
        expected_url = url_template % (session, id)
        eq_(expected_url, convert_to_url(session, billtext))

def test_can_generate_a_simple_url_based_on_session_and_id():
    session = "82R"
    url_template = "http://www.capitol.state.tx.us/BillLookup/History.aspx?LegSess=%s&Bill=%s"
    data = house_data + senate_data
    for id, billtext in data:
        expected_url = url_template % (session, id)
        actual_bill = extract_bill_from_file(billtext)
        eq_(expected_url, to_url(session, actual_bill))

def test_can_geneate_text_version_url_based_on_session_and_id():
    session = "82R"
    url_template = "http://www.capitol.state.tx.us/BillLookup/Text.aspx?LegSess=%s&Bill=%s"
    data = house_data + senate_data
    for id, billtext in data:
        expected_url = url_template % (session, id)
        actual_bill = extract_bill_from_file(billtext)
        eq_(expected_url, to_text_url(session, actual_bill))

