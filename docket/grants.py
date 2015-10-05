import datetime
import os
import re

from bs4 import BeautifulSoup
import requests

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

        self.set_fields(**kwargs)

    def __unicode__(self):
        return "(%s) %s" % (self.term, self.casename)

class Load(BaseObject):

    def __init__(self, **kwargs):
        self.cases = []
        self.terms = range(2007, int(current_term()) + 1)

        self.set_fields(**kwargs)

    def scrape(self):
        for term in self.terms:
            URL = 'http://www.supremecourt.gov/grantednotedlist/%sgrantednotedlist' % str(term)[2:4]
            print "Scraping %s" % term

            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'lxml')

            rows = soup.select('.WordSection1 p.MsoNormal')

            if len(rows) <1:
                rows = soup.select('.Section1 p')

            cases = {}

            current_case = None
            continued = False
            for idx, row in enumerate(rows):
                line = " ".join(row.text.split())
                line = line.decode('latin-1').encode('utf-8').replace(u'\xa0', u'')
                line = line.replace(u'&nbsp;', '')

                if len(row.select('a')) > 0:
                    current_case = row.select('a')[0].text.replace(u')','').strip()
                    cases[current_case] = {}
                    cases[current_case]['casename'] = line.split(current_case)[1].strip()

                    # Get detail PDF if it doesn't exist already.
                    # These get written as PDFs and then transformed
                    # from PDF to text in two steps.
                    detail_url = row.select('a')[0].attrs['href'].replace('../', 'http://supremecourt.gov/').replace(' ', '%20')
                    pdf_path = '/tmp/%s' % detail_url.split('/')[-1]
                    txt_path = pdf_path.replace('.pdf', '.txt')
                    z = requests.get(detail_url)

                    if not os.path.isfile(pdf_path):
                        with open(pdf_path, 'w') as writefile:
                            writefile.write(z.content)

                    if not os.path.isfile(txt_path):
                        os.system('pdf2txt.py -o %s %s' % (txt_path, pdf_path))

                    with open(txt_path, 'r') as readfile:
                        cases[current_case]['question'] = str(readfile.read()).decode('latin-1')

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

                    cases[current_case]['case_code'] = unicode(case_code).strip()
                    cases[current_case]['casename'] = cases[current_case]['casename'].replace(cases[current_case]['case_code'], '').strip()

            for docket,case in cases.items():
                case['docket'] = docket
                case['term'] = term
                case['casename'] = case['casename'].replace(u')','').replace(u'**', '').replace('*','').replace('#', '').strip()
                self.cases.append(MeritsCase(**case))
