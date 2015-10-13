import datetime
import os
import re

from bs4 import BeautifulSoup
import requests

ORDERS_TYPES = ['PROHIBITION','REHEARINGS','MANDAMUS','HABEAS CORPUS','CERTIORARI','PENDING CASES','ORDERS']
DOCKET_REGEX = '^([0-9]{1,}\S[0-9]{2,}$)|([A-Z]{1,}\S[0-9]{2,}$)|([0-9]{1,4}, ORIG.$)'

def current_term():
    now = datetime.datetime.now()
    return "%s" % (now.year - 1 if now.month < 10 else now.year)

class BaseObject(object):

    def set_fields(self, **kwargs):
        fieldnames = self.__dict__.keys()
        for k,v in kwargs.items():
            k = k.lower().strip()
            if k in fieldnames:
                setattr(self, k, v)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

class Orders(BaseObject):
    def __init__(self, **kwargs):
        self.date = None
        self.orders_pdf_url = None
        self.orders_type = None
        self.term = None

        self.set_fields(**kwargs)

    def __unicode__(self):
        return "%s - %s" % (self.date, self.orders_type)


class OrdersCase(BaseObject):
    def __init__(self, **kwargs):
        self.date = None
        self.orders_pdf_url = None
        self.term = None
        self.docket = None
        self.casename = None
        self.text = None
        self.orders_type = None
        self.direction = None

        self.set_fields(**kwargs)

    def __unicode__(self):
        return self.casename


class Load(BaseObject):

    def __init__(self, **kwargs):
        self.orders = []
        self.cases = []
        self.terms = [int(current_term())] # First available term is 2003.

        self.set_fields(**kwargs)

    def scrape(self):
        for term in self.terms:
            URL = 'http://www.supremecourt.gov/orders/ordersofthecourt/%s' % str(term)[2:4]

            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'lxml')

            rows = soup.select('div.column2 div')

            for row in rows:
                orders_dict = {}
                orders_dict['term'] = term
                orders_dict['date'] = row.select('span')[0].text.strip()
                orders_dict['orders_pdf_url'] = 'http://supremecourt.gov' + row.select('span')[1].select('a')[0].attrs['href']
                orders_dict['orders_type'] = row.select('span')[1].select('a')[0].text.strip()

                if orders_dict['date'] and orders_dict['orders_type']:
                    self.orders.append(Orders(**orders_dict))

    def parse(self):
        for order in self.orders:
            pdf_filename = order.orders_pdf_url.split('/')[-1]
            txt_filename = pdf_filename.replace('pdf', 'xml')

            if not os.path.isfile('/tmp/%s' % pdf_filename):
                r = requests.get(order.orders_pdf_url)
                with open('/tmp/%s' % pdf_filename, 'w') as writefile:
                    writefile.write(r.content)

            if not os.path.isfile('/tmp/%s' % txt_filename):
                os.system('pdf2txt.py -o /tmp/%s -t tag /tmp/%s' % (txt_filename, pdf_filename))

            with open('/tmp/%s' % txt_filename, 'r') as readfile:
                raw_xml = str(readfile.read())\
                                .decode('utf-8')\
                                .replace('TH>', 'TD>')\
                                .replace('<TH', '<TD')\
                                .replace('<P', '<TD')\
                                .replace('P>', 'TD>')\
                                .replace(u'\u2019', "'")\
                                .replace(u'\u201c', '"')\
                                .replace(u'\u201d', '"')

            soup = BeautifulSoup(raw_xml, "lxml")
            cells = soup.select("td")
            END = len(cells)

            orders_type = None
            case_direction = None

            # Loop over the bits of text from the parsed PDF.
            for idx, cell in enumerate(cells):
                cell = cell.text.strip()
                match = re.search(DOCKET_REGEX, cell)

                # See if this is one of the header lines.
                # If it is, set a temporary variable
                # with the orders_type and direction since
                # these will continue to be true for the
                # next several cases until we get another
                # header line.
                # (NOTE: This is brittle but it's the best
                # we have right now.)
                for h in ORDERS_TYPES:
                    if h in cell:
                        case_direction = None
                        for d in ["granted", "denied"]:
                            if d in cell.lower():
                                case_direction = d
                        orders_type = h.lower()

                # Alternately, this might be a line with a
                # docket ID in it. The dockets are kinda
                # recognizeable by their struture. So there
                # is a hideous regex for them.
                # (NOTE: This is brittle but it's the best
                # we have right now.)
                if match:
                    case = {}
                    case['docket'] = cell
                    case['casename'] = cells[idx + 1].text.strip()

                    go = True
                    increment = 2

                    # Some cases are combined with others.
                    # These match this pattern.
                    # Skip to the next cell instead.
                    if case['casename'] == ")":
                        case['casename'] = cells[idx + 2].text.strip()
                        increment = 3

                    case['orders_type'] = orders_type
                    case['direction'] = case_direction
                    case['text'] = []

                    # The text for this case might spill over several
                    # lines or it might not exist at all.
                    # Start grabbing lines here.
                    while go:

                        # Don't go past the last cell, because DUH.
                        if idx + increment < END:
                            next_cell = cells[idx + increment]

                            # Make sure the next cell isn't a docket number.
                            if not re.search(DOCKET_REGEX, next_cell.text.strip()):
                                for h in ORDERS_TYPES:

                                    # If this is a header row, give up.
                                    if h in next_cell.text.strip():
                                        increment = 2
                                        go = False
                                        break

                                # If we're still good to continue, grab this row.
                                if go:
                                    increment += 1
                                    case['text'].append(next_cell.text.strip())

                            # If this is a docket, skip.
                            if re.search(DOCKET_REGEX, next_cell.text.strip()):
                                increment = 2
                                go = False
                                break
                        else:

                            # Reset the increment steps and go to the next.
                            increment = 2
                            break

                    # Take all the text lines and join them with a space
                    # into a single block of text.
                    case['text'] = " ".join(case['text'])
                    if case['text'] == ")":
                        case['text'] = ""

                    # Look for some special cases.
                    if "petition for a writ of certiorari is granted" in case['text']:
                        case['direction'] = "granted"
                        case['orders_type'] = "certiorari"

                    case['term'] = order.term
                    case['orders_pdf_url'] = order.orders_pdf_url

                    self.cases.append(OrdersCase(**case))