import datetime
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
        self.argument_date = None
        self.granted_date = None
        self.originating_court = None
        self.case_code = None

        self.set_fields(**kwargs)

    def __unicode__(self):
        return "(%s) %s" % (self.term, self.casename)

class Load(object):

    def __init__(self):
        self.cases = []

    def scrape(self):
        for term in range(2007, int(current_term()) + 1):
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

                if u"Court:" in line:
                    continued = False
                    if u"Granted:" in line:
                        cases[current_case]['originating_court'] = line.split(u'Court:')[1].split(u'Granted:')[0].strip()
                        cases[current_case]['granted_date'] = line.split(u'Granted:')[1].strip()
                elif u"Argument Date:" in line:
                    continued = False
                    cases[current_case]['argument_date'] = line.split(u'Argument Date:')[1].strip()

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
