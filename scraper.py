from pyquery import PyQuery as pq
import logging
import sys

BASE_URL = "http://www.capitol.state.tx.us/Search/"
BILL_SEARCH_URI = "BillSearchResults.aspx?"
#FIRST_SEARCH_PAGE = "BillSearchResults.aspx?NSP=1&SPL=False&SPC=False&SPA=True&SPS=False&Leg=82&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;;;;;&AuthorCode=&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=S000;S001;H001;&AAO=O&Subjects=&SAO=&TT=&ID=rrUvmj76e"

PAGE_URL_TEMPLATE = "&shCmte=False&shComp=False&shSumm=False&NSP=1&SPL=False&SPC=False&SPA=True&SPS=False&Leg=82&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;;;;;&AuthorCode=&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=S000;S001;H001;&AAO=O&Subjects=&SAO=&TT=&ID="

# This is set here to do a session hijack
#STARTING_URL = "http://www.capitol.state.tx.us/Search/BillSearchResults.aspx?NSP=1&SPL=False&SPC=False&SPA=True&SPS=False&Leg=82&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;;;;;&AuthorCode=&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=S000;S001;H001;&AAO=O&Subjects=&SAO=&TT=&ID=rrUvmj76e"

STARTING_URL = "http://www.capitol.state.tx.us/Search/BillSearchResults.aspx?NSP=1&SPL=False&SPC=False&SPA=True&SPS=False&Leg=82&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;;;;;&AuthorCode=&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=S000;S001;H001;&AAO=O&Subjects=&SAO=&TT=&ID=yds9HuQcI"
STARTING_URL = "http://www.capitol.state.tx.us/Search/BillSearchResults.aspx?NSP=1&SPL=False&SPC=False&SPA=True&SPS=False&Leg=82&Sess=R&ChamberH=True&ChamberS=True&BillType=B;JR;;;;;&AuthorCode=&SponsorCode=&ASAndOr=O&IsPA=True&IsJA=False&IsCA=False&IsPS=True&IsJS=False&IsCS=False&CmteCode=&CmteStatus=&OnDate=&FromDate=&ToDate=&FromTime=&ToTime=&LastAction=False&Actions=S000;S001;H001;&AAO=O&Subjects=&SAO=&TT=&ID=yds9HuQcI"



def quick_out(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def detail_pages(doc):
    return doc('a[href*="../BillLookup/History.aspx?"]')

def unique_secondary_pages(doc):
    print "Finding all pages"
    known_urls = []
    l = doc('.noPrint a[href*="%s"]' % PAGE_URL_TEMPLATE)
    for page_link in l:
        if page_link.attrib['href'] in known_urls:
            continue
        known_urls.append(page_link.attrib['href'])
        quick_out('.')

    print "DONE! Found %d" % len(known_urls)
    return known_urls 

def find_next_page(doc):
    next_img = doc('img[src="../Images/icon_next_active.gif"]')
    if not next_img:
        return None
    next_url = next_img[0].getparent().attrib['href']
    return pq(url=BASE_URL + next_url)

def collect_bill_urls(doc):
    print "Collecting all of the bill URLs"
    #doc = pq(url=BASE_URL + url)
    bill_urls = [a.attrib['href'] for a in detail_pages(doc)]
    quick_out('.')
    print "DONE! Found %d" % len(bill_urls)
    return bill_urls

def grab_value(doc, selector):
    return doc(selector)[0].text

scrapped_values = (
    'LastAction',
    'CaptionVersion',
    'CaptionText',
    'Authors',
    'Subjects',
)

def scrap_value(doc, value):
    ret = doc('#cell%s' % value)[0].text_content()
    if value == "Subjects":
        ret = [a + ')' for a in ret.split(')') if a]
    return ret

def write_to_csv(data):
    import csv, datetime
    now = datetime.datetime.now()
    writer = csv.writer(open("./bills-%d%d%d.csv" % (now.year, now.month, now.day), 'wb'))
    writer.writerow(('id', 'author', 'last_action', 'caption_text', 'caption_version', 'subjects'))
    for row in data:
        values = (
            row['_id'],
            row['Authors'],
            row['LastAction'],
            row['CaptionText'],
            row['CaptionVersion'],
        ) + tuple(row['Subjects'])
        writer.writerow(values)

def write_to_couch(data):
    import couchdb
    couch = couchdb.Server()
    db = couch['bills']
    for row in data:
        db.save(row)


def fetch_bill_data_for_page(doc):
    bill_data = []
    for bill_url in collect_bill_urls(doc):

        bill = pq(url=BASE_URL + bill_url)
        data = {
            '_id': grab_value(bill, '#usrBillInfoTabs_lblBill')
        }
        for v in scrapped_values:
            data[v] = scrap_value(bill, v)
        bill_data.append(data)
        sys.stdout.write('.')
        sys.stdout.flush()
    print "DONE!"
    return bill_data

def main():
    doc = pq(url=STARTING_URL)
    bill_data = fetch_bill_data_for_page(doc)
    doc = find_next_page(doc)
    while doc:
        bill_data += fetch_bill_data_for_page(doc)
        doc = find_next_page(doc)

    #print bill_data
    #print "\n\n"

    write_to_csv(bill_data)
    #write_to_couch(bill_data)

