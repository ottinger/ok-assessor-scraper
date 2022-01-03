# data_grabber.py
#
# Contains the parts that actually make contact with the County Assessor website.
# We don't do any parsing here (except for possibly in the search parser).
#
# we should use class for this because it stores session+cookies!
import enum
import re
import requests

from bs4 import BeautifulSoup


class PaginatedTableTypes(enum.Enum):
    VALUE_HISTORY = 7
    S_A_E = 8
    DEED_TRANSACTIONS = 10
    NOTICE_OF_VALUE = 11
    BUILDING_PERMITS = 12
    BUILDINGS = 13


    def __str__(self):
        return str(self.name)


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
        elif table_number == 8:  # Status/Adjustments/Exemptions
            input_name = None
        elif table_number == 10:  # Transaction History
            input_name = 'fpdbr_13_PagingMove'
        elif table_number == 11:  # Last Mailed Notice Of Value
            input_name = 'fpdbr_22_PagingMove'
        elif table_number == 12:  # Building Permit
            input_name = 'fpdbr_16_PagingMove'
        elif table_number == 13:  # Building Record
            input_name = 'fpdbr_18_PagingMove'  # building record. (propertyid 134581 has more than 1 page of bldgs)
        else:
            input_name = None
        return input_name

    # get_paginated_table_from_main_page()
    #
    # Gets page data for an individual table on the main page. (eg: valuation history, transaction, etc)
    # These tables are paginated and the Assessor webapp requires you to send a POST request (with cookies and session)
    # to switch between pages.
    #
    # Pass in a constant from PAGINATED_TABLE_TYPES
    def get_paginated_table_from_main_page(self, propertyid, table_enum):
        table_id = table_enum.value
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
            results.append(data)
            stop = self._table_on_last_page(data, table_id) if input_name else True
        return results


# OklahomaCountyAssessorSearchDataGrabber
#
# This class is used to get a list of property ids for a given search query.
class OklahomaCountyAssessorSearchDataGrabber(DataGrabber):
    def __init__(self):
        super().__init__()

        self.search_params = None

    def _do_search(self, search_web_address, input_params):
        self.session = requests.session()
        # get the front search page to establish session
        req = self.session.get("https://docs.oklahomacounty.org/AssessorWP5/DefaultSearch.asp")

        all_rows = []
        done = False
        while done == False:
            req = self.session.post(search_web_address, cookies=req.cookies,
                                   data=input_params)
            data = req.text
            the_soup = BeautifulSoup(data, features="lxml")
            cur_page_rows = the_soup.find_all('table')[3].tbody.find_all('tr')

            # add the rows
            for r in cur_page_rows:
                if not r.find_all('form'):
                    all_rows.append(r)

            # see if there's a next page, go to next page if so
            if not cur_page_rows[len(cur_page_rows) - 1].find_all('input', attrs={'value': "  >   "}):
                done = True
            else:
                input_params["fpdbr_0_PagingMove"] = '  >   '  # for subdivision or map number search
                input_params["fpdbr_1_PagingMove"] = '  >   '  # for name or addr search

        return all_rows

    def _extract_propertyids_from_rows(self, rows):
        results_list = []
        for r in rows:
            cur_url = r.find_all('a')[0]['href']
            cur_propertyid = re.findall(r".*\.asp\?PROPERTYID=([0-9]+)", cur_url, re.IGNORECASE)[0]
            results_list.append(int(cur_propertyid))
        return results_list

    # subdivision_search()
    #
    # Calls _do_search() to perform a subdivision search. Returns a list of PROPERTYIDs
    # for the args passed (subdivision, block, lot)
    def subdivision_search(self, subdivision, block='', lot=''):
        search_address = 'https://docs.oklahomacounty.org/AssessorWP5/SubdivisionSearch.asp'
        input_params = {'SubdivisionName': subdivision,
                        'Block': block,
                        'Lot': lot}
        rows = self._do_search(search_address, input_params)
        return self._extract_propertyids_from_rows(rows)

    # map_number_search()
    #
    # Calls _do_search() to perform a map number/quarter section search.
    def map_number_search(self, map_number):
        search_address = 'https://docs.oklahomacounty.org/AssessorWP5/MapNumberSearch.asp'
        input_params = {'MapNumber': str(map_number)}
        rows = self._do_search(search_address, input_params)
        return self._extract_propertyids_from_rows(rows)

    # name_search()
    #
    # Calls _do_search() to perform a search by name of property owner.
    def name_search(self, name):
        search_address = 'https://docs.oklahomacounty.org/AssessorWP5/NameSearch.asp'
        input_params = {'name': str(name)}
        rows = self._do_search(search_address, input_params)
        return self._extract_propertyids_from_rows(rows)

    # address_search()
    #
    # Calls _do_search() to perform a search by address.
    def address_search(self, address):
        search_address = 'https://docs.oklahomacounty.org/AssessorWP5/AddressSearch.asp'
        input_params = {'FormattedLocation': str(address)}
        rows = self._do_search(search_address, input_params)
        return self._extract_propertyids_from_rows(rows)