import datetime
import os
import re

from bs4 import BeautifulSoup
import requests

ORDERS_TYPES = ['PROHIBITION','REHEARINGS','MANDAMUS','HABEAS CORPUS','CERTIORARI','PENDING CASES']

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

        self.set_fields(**kwargs)

    def __unicode__(self):
        return "%s - %s" % (self.date, self.orders_type)

class Load(BaseObject):

    def __init__(self, **kwargs):
        self.orders = []
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
                orders_dict['date'] = row.select('span')[0].text.strip()
                orders_dict['orders_pdf_url'] = 'http://supremecourt.gov' + row.select('span')[1].select('a')[0].attrs['href']
                orders_dict['orders_type'] = row.select('span')[1].select('a')[0].text.strip()

                if orders_dict['date'] and orders_dict['orders_type']:
                    self.orders.append(Orders(**orders_dict))

