import datetime
import os
import re

from bs4 import BeautifulSoup
import requests

JUSTICE_MAP = {
    'A': '112',
    'AK': '106',
    'AS': '105',
    'B': '110',
    'D': None,
    'EK': '114',
    'G': '109',
    'PC': None,
    'R': '111',
    'SS': '113',
    'T': '108'
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
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

class MeritsCase(BaseObject):
    def __init__(self, **kwargs):
        self.casename = None
        self.term = None
        self.docket = None
        self.datedecided = None
        self.majopinionwriter = None
        self.opinion_pdf_url = None

        self.set_fields(**kwargs)

    def __unicode__(self):
        return "(%s) %s" % (self.term, self.casename)

class Load(BaseObject):

    def __init__(self, **kwargs):
        self.cases = []
        self.terms = [int(current_term())] # 06 is the first term, but 06-09 are broken on the SCOTUS site.

        self.set_fields(**kwargs)

    def scrape(self):
        for term in self.terms:
            URL = 'http://www.supremecourt.gov/opinions/slipopinion/%s' % str(term)[2:4]
            print "Scraping %s" % term

            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'lxml')

            rows = soup.select('#mainbody center table tr')[1:]

            for row in rows:
                case_dict = {}
                cells = row.select('td')
                case_dict['casename'] = cells[3].text.strip()
                case_dict['datedecided'] = cells[1].text.strip()
                case_dict['docket'] = cells[2].text.strip()
                case_dict['majopinionwriter'] = JUSTICE_MAP[cells[5].text.strip()]
                case_dict['opinion_pdf_url'] = 'http://supremecourt.gov' + cells[3].select('a')[0].attrs['href']
                case_dict['term'] = term
                self.cases.append(MeritsCase(**case_dict))
