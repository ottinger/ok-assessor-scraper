# data_grabber.py
#
# Contains the parts that actually make contact with the County Assessor website.
# We don't do any parsing here.
#
# we should use class for this because it stores session+cookies!
import enum
import requests

from data_parser import OklahomaCountyAssessorDataParser
from bs4 import BeautifulSoup

# TODO: add more table types
PAGINATED_TABLE_TYPES = enum.Enum('PAGINATED_TABLE_TYPES', {'VALUE_HISTORY': 7,
                                                            'BUILDING_PERMITS': 12,
                                                            'BUILDINGS': 13,
                                                            'DEED_TRANSACTIONS': 14})

class DataGrabber:
    def __init__(self):
        self.session = requests.session()
        self.cookies = {}
        pass  # do stuff?

    def get(self, url):
        self.session = self.session if self.session else requests.session()
        self.cookies = self.cookies if self.cookies else {}

        req = self.session.get(url)
        return req.text

    def post(self, url, post_data):
        self.session = self.session if self.session else requests.session()
        self.cookies = self.cookies if self.cookies else {}

        req = self.session.post(url, cookies=self.cookies, data=post_data)
        return req.text

# OklahomaCountyAssessorRecordDataGrabber
#
# This class is used to download all pages needed for an individual property record.
# Parsing will be done by the data_parser.OklahomaCountyAssessorDataParser class.
class OklahomaCountyAssessorRecordDataGrabber(DataGrabber):
    def __init__(self):
        super().__init__()

        self.propertyid = None
        self.url = None
        self.main_page_data = None

    # get_initial_page()
    #
    # Using a GET request, get the content for the main property record page.
    def get_initial_page(self, propertyid):
        self.propertyid = propertyid
        self.url = 'https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PROPERTYID=' + str(propertyid)

        req = self.session.get(self.url)
        self.main_page_data = req.text
        return req.text

    # _table_on_last_page()
    #
    # Used by _get_successive_pages_for_main_page_tables() to see if we are on the last page of the table we are
    # currently grabbing.
    @staticmethod
    def _table_on_last_page(html, table_number):
        the_soup = BeautifulSoup(html, features="lxml")
        rows = the_soup.find_all('table')[table_number].tbody.find_all('tr')

        return not rows[len(rows)-1].find_all('input', attrs={'value': "  >   "})  # Returns a boolean

    # _get_table_post_input_name()
    #
    # Used by _get_successive_pages_for_main_page_tables() to get the input name for the
    @staticmethod
    def _get_table_post_input_name(table_number):
        if table_number == 7:  # Valuation History
            input_name = 'fpdbr_24_PagingMove'
        elif table_number == 12:  # Building Permit
            input_name = 'fpdbr_16_PagingMove'
        elif table_number == 13:  # Building Record
            input_name = 'fpdbr_18_PagingMove'  # building record. (propertyid 134581 has more than 1 page of bldgs)
        else:  # Transaction History
            input_name = 'fpdbr_13_PagingMove'
        return input_name

    # _get_successive_pages_for_main_page_tables()
    #
    # Gets page data for an individual table on the main page. (eg: valuation history, transaction, etc)
    # These tables are paginated and the Assessor webapp requires you to send a POST request (with cookies and session)
    # to switch between pages.
    #
    # Pass in a constant from PAGINATED_TABLE_TYPES
    def get_paginated_tables_from_main_page(self, propertyid, table_id):
        results = []
        stop = False

        if not self.main_page_data or propertyid != self.propertyid:
            self.propertyid = propertyid
            self.url = 'https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PROPERTYID=' + str(propertyid)
            req = self.session.get(self.url)
            self.main_page_data = req.text
        results.append(self.main_page_data)
        stop = self._table_on_last_page(self.main_page_data, table_id)

        input_name = self._get_table_post_input_name(table_id)

        while not stop:
            req = self.session.post("https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp", cookies=self.cookies,
                                    data={'PropertyID': str(propertyid), input_name: '  >   '})
            data = req.text
            stop = self._table_on_last_page(data, table_id)
        return results
