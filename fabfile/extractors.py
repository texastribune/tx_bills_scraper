import copy
from pyquery import PyQuery as pq
import csv
import re
from ._utils import to_text_url
from ._utils import to_url
from ._utils import to_leg_url

import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

_cached_person_dict = {}
def person_to_object(name):
    if not _cached_person_dict:
        print "building..."
        #reader = csv.reader(open("./lawmaker.csv", "r"))
        reader = UnicodeReader(open("./lawmaker.csv", "rb"))
        legend = None
        for row in reader:
            if not legend:
                legend = row
                continue
            try:
                _cached_person_dict[row[0]] = dict(zip(legend, row))
            except Exception, e:
                import ipdb;ipdb.set_trace()
                print "WTF?"
    return _cached_person_dict[name]

def extract_people_html(opts):
    if not opts["doc"]:
        return None
    raw_html = extract_raw_html(opts)
    if not raw_html:
        return None
    return [person_to_object(a.strip()) for a in raw_html.split(u'|')]

def extract_multiline_html(opts):
    raw_html = extract_raw_html(opts)
    if not raw_html:
        return None
    return opts["doc"] and [a for a in raw_html.split('<br/>') if a] or None

def extract_raw_html(opts):
    ret = opts["doc"] and opts["doc"].find('#cell%s' % opts["type"]).html() or None
    if ret:
        ret.replace('&amp;', '&')
    return ret

def extract_committee_name(opts):
    return opts["doc"].find('#cell%s' % opts["type"]).text()

def extract_committee_status(opts):
    return opts["doc"].find('#cell%sStatus' % opts["type"]).text()

def extract_committee_vote(opts):
    raw_votes = opts["doc"].find('#cell%sVote' % opts["type"]).text()
    if not raw_votes:
        return None
    votes = raw_votes.split(u" \xa0 ")
    return dict([(str(a.lower()), int(b)) for a, b in [a.split('=') for a in votes]])

def extract_subcommittee(opts):
    opts["type"] = opts["type"].replace('Committee', 'Subcommittee')
    name = extract_raw_html(opts)
    if not name:
        return None
    return {
        'name': name.split(':')[-1].strip(),
        # TODO: this needs to be able to deal with people names with extra data
        # included such as "Smith (Chair)" and map that to "Smith"
        #'members': extract_people_html({
            #"type": opts["type"] + 'Status',
            #"doc": opts["doc"]}),
    }

def table_extractor(func):
    def inner(opts):
        new_opts = copy.copy(opts)
        id = "#tbl%s" % opts["type"]
        new_opts["doc"] = opts["doc"](id)
        return func(new_opts)
    return inner

@table_extractor
def people_extractor(opts):
    return { opts["type"].lower(): extract_people_html(opts) }

@table_extractor
def multiline_text_extractor(opts):
    return { opts["type"].lower(): extract_multiline_html(opts) }

@table_extractor
def text_extractor(opts):
    return {opts["type"].lower(): extract_raw_html(opts)}

@table_extractor
def committee_extractor(opts):
    if not opts["doc"]:
        return None
    is_house = opts["doc"].parents('body').find('#usrBillInfoTabs_lblBill').text()[0] == 'H'
    if is_house:
        key = 'house_committee' if opts["type"][0:5] == 'Comm1' else 'senate_committee'
    else:
        key = 'senate_committee' if opts["type"][0:5] == 'Comm1' else 'house_committee'
    data = {key: {
        'name': extract_committee_name(opts),
        'status': extract_committee_status(opts),
        'vote': extract_committee_vote(opts),
        'subcommittee': extract_subcommittee(opts)
    }}
    return data

def caption_extractor(opts):
    return { "caption_%s" % opts["type"][7:].lower(): extract_raw_html(opts) }

ACTION_COLUMNS = (
    'status',
    'description',
    'comment',
    'date',
    'time',
    'journal_page',
)

def action_extractor(opts):
    raw_actions = opts["doc"]('#usrBillInfoActions_tblActions + table tr')[1:]
    if not raw_actions:
        return None
    actions = []
    for raw_action_row in raw_actions:
        raw = opts["doc"]('td', raw_action_row)
        actions.append(dict(zip(ACTION_COLUMNS, [opts["doc"](a).text() for a in raw])))
    return {'actions': actions}

def text_version_extractor(opts):
    doc = pq(url=to_text_url(opts["session"], opts["bill"]))
    versions = [re.sub("</?u>|\*", "", doc(a).html()) for a in doc("td:first", doc("tr", doc("#Form1 table:first"))) if a is not None][1:]
    return {"versions": versions}
    

RAW_DATA_CONVERSION = (
    ({"type": 'Authors'}, people_extractor),
    ({"type": 'Coauthors'}, people_extractor),
    ({"type": 'Sponsors'}, people_extractor),
    ({"type": 'Cosponsors'}, people_extractor),
    ({"type": 'Subjects'}, multiline_text_extractor),
    ({"type": 'CaptionVersion'}, caption_extractor),
    ({"type": 'CaptionText'}, caption_extractor),
    ({"type": 'Remarks'}, text_extractor),
    ({"type": 'Comm1Committee'}, committee_extractor),
    ({"type": 'Comm2Committee'}, committee_extractor),
    ({}, action_extractor, ),
    ({}, text_version_extractor, ),
)

def data_extractor(session, bill):
    doc = pq(url=to_url(session, bill))
    ret = {}
    for args in RAW_DATA_CONVERSION:
        func = args[1]
        args = args[0]
        args["doc"] = doc
        args["session"] = session
        args["bill"] = bill
        data = func(args)
        if data:
            ret.update(data)
    return ret


def leg_extractor(session):
    ret = []
    doc = pq(url=to_leg_url(session))
    select = doc('select').filter('#cboAuthors')
    select_list = str(select).split('</option>')
    select_list.pop(0)
    select_list.pop()
    for opt in select_list:
        opt1 = opt.split('">')
        opt2 = opt1[1].split('(')
        opt3 = opt2[1].split('-')

        name = opt2[0]
        chamber = opt3[0]
        leg_id = opt3[1].rstrip(')')
        leg = {'name': name, 'leg_id': leg_id, 'chamber': chamber}
        ret.append(leg)

    return ret

