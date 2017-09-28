import datetime
import os
import re
import subprocess

from bs4 import BeautifulSoup
import requests

CASE_CODE_MAP = {
    "C": "Certiorari",
    "A": "Appeal",
    "Q": "Certified Question",
    "S": "State",
    "F": "U.S. Court of Appeals",
    "T": "Three-Judge District Court",
    "M": "U.S. Court of Appeals for the Armed Forces",
    "O": "Other Court",
    "X": "Civil",
    "Y": "Criminal",
    "H": "Habeas Corpus or other collateral attack",
}

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
        return self.__str__()

    def __str__(self):
        return self.__str__()

class MeritsCase(BaseObject):
    def __init__(self, **kwargs):
        self.casename = None
        self.term = None
        self.docket = None
        self.dateargument = None
        self.dategranted = None
        self.court_originated = None
        self.case_code = None
        self.question = None
        self.question_url = None
        self.jurisdictional_grounds = None
        self.court_below = None
        self.nature_of_case = None

        self.set_fields(**kwargs)

    def __str__(self):
        return "(%s) %s" % (self.term, self.casename)

    def serialize(self):
        payload = dict(self.__dict__)
        for k,v in payload.items():
            try:
                payload[k] = v
            except AttributeError:
                pass
        return payload

class Load(BaseObject):

    def __init__(self, **kwargs):
        self.cases = []
        self.terms = [int(current_term())] # First available term is 2007.

        self.set_fields(**kwargs)

    def scrape(self):
        for term in self.terms:
            URL = 'http://www.supremecourt.gov/grantednotedlist/%sgrantednotedlist' % str(term)[2:4]

            r = requests.get(URL)
            soup = BeautifulSoup(r.text, 'lxml')

            rows = soup.select('.WordSection1 p.MsoNormal')

            if len(rows) <1:
                rows = soup.select('.Section1 p')

            cases = {}

            current_case = None
            continued = False
            for idx, row in enumerate(rows):
                line = " ".join(row.text.split())
                line = line.replace(u'\xa0', u'')
                line = line.replace(u'&nbsp;', '')

                if len(row.select('a')) > 0:
                    current_case = row.select('a')[0].text.replace(u')','').strip()
                    cases[current_case] = {}
                    cases[current_case]['casename'] = line.split(current_case)[1].strip()

                    # Get detail PDF if it doesn't exist already.
                    # These get written as PDFs and then transformed
                    # from PDF to text in two steps.
                    detail_url = row.select('a')[0].attrs['href'].replace('../', 'http://supremecourt.gov/').replace(' ', '%20')
                    cases[current_case]['question_url'] = detail_url
                    pdf_path = '/tmp/%s' % detail_url.split('/')[-1]
                    txt_path = pdf_path.replace('.pdf', '.txt')

                    if not os.path.isfile(pdf_path):
                        subprocess.call(['curl', '-o', pdf_path, detail_url])
                    
                    if not os.path.isfile(txt_path):
                        subprocess.call(['pdf2txt.py', '-o', txt_path, pdf_path])

                    with open(txt_path, 'r') as readfile:
                        cases[current_case]['question'] = str(readfile.read())

                if u"Court:" in line:
                    continued = False
                    if u"Granted:" in line:
                        cases[current_case]['court_originated'] = line.split(u'Court:')[1].split(u'Granted:')[0].strip()
                        cases[current_case]['dategranted'] = line.split(u'Granted:')[1].strip()
                elif u"Argument Date:" in line:
                    continued = False
                    cases[current_case]['dateargument'] = line.split(u'Argument Date:')[1].strip()

                if continued:
                    if len(row.select('b')) > 0:
                        cases[current_case]['casename'] += ' %s' % line

                if len(row.select('a')) > 0:
                    case_code = re.search(r'\s+([C|A|Q][S|F|T|M|O][X|Y|H])\s+', line)
                    if case_code:
                        case_code = case_code.group(0)

                    cases[current_case]['case_code'] = str(case_code).strip()

                    try:
                        cases[current_case]['jurisdictional_grounds'] = CASE_CODE_MAP[str(case_code).strip()[0]]
                        cases[current_case]['court_below'] = CASE_CODE_MAP[str(case_code).strip()[1]]
                        cases[current_case]['nature_of_case'] = CASE_CODE_MAP[str(case_code).strip()[2]]
                    except KeyError:
                        pass

                    cases[current_case]['casename'] = cases[current_case]['casename'].replace(cases[current_case]['case_code'], '').strip()

            for docket,case in cases.items():
                case['docket'] = docket
                case['term'] = term
                case['casename'] = case['casename'].replace(u')','').replace(u'**', '').replace('*','').replace('#', '').strip()
                self.cases.append(MeritsCase(**case))
