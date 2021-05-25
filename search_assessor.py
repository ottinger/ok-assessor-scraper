# search_assessor.py
#
# Provides functionality to search for a property record on Oklahoma County Assessor website.
#
# Search functionality will be implemented for certain types of searches as needed. No plans
# currently to implement *everything*.
import requests
import re
from bs4 import BeautifulSoup

# subdivision_search()
#
# Calls do_search() to perform a subdivision search. Returns a list of PROPERTYIDs
# for the args passed (subdivision, block, lot)
def subdivision_search(subdivision="university", block="", lot=""):
    rows = do_search(input_params={'SubdivisionName' : subdivision,
                  'Block' : block,
                  'Lot' : lot},
                 search_address="https://docs.oklahomacounty.org/AssessorWP5/SubdivisionSearch.asp")
    results_list = []
    for r in rows:
        cur_url = r.td.find_all('a')[0]['href']
        cur_propertyid = re.findall(r".*\.asp\?PROPERTYID=([0-9]+)", cur_url, re.IGNORECASE)[0]
        results_list.append(int(cur_propertyid))
    return results_list

# map_number_search()
#
# Calls do_search() to perform a map number/quarter section search.
def map_number_search(map_number):
    rows = do_search(input_params={"MapNumber": str(map_number)},
                     search_address="https://docs.oklahomacounty.org/AssessorWP5/MapNumberSearch.asp")
    results_list = []
    for r in rows:
        cur_url = r.find_all('a')[0]['href']
        cur_propertyid = re.findall(r".*\.asp\?PROPERTYID=([0-9]+)", cur_url, re.IGNORECASE)[0]
        results_list.append(int(cur_propertyid))
    return results_list

# do_search()
#
# Takes a search address and parameters, and returns the set of rows across all pages.
# The rows are still beautifulsoup/lxml objects that will need to be processed after
# returned.
#
# (We will probably just be getting the property id's for now, but the other data will
# be left in, in case it is needed later.)
#
# Args:
# * search_address: this is the address we will be POSTing to. It is different for each
#   type of search.
# * input_params: parameters expressing the actual search query (which again vary based
#   on type of search).
def do_search(search_address, input_params):
    # We need a session to go between pages properly.
    sesh = requests.session()
    # get the front search page to establish session
    req = sesh.get("https://docs.oklahomacounty.org/AssessorWP5/DefaultSearch.asp")

    all_rows = []
    done = False
    while done == False:
        req = sesh.post(search_address, cookies = req.cookies,
            data = input_params)
        data = req.text
        the_soup = BeautifulSoup(data, features="lxml")
        cur_page_rows = the_soup.find_all('table')[3].tbody.find_all('tr')

        # add the rows
        for r in cur_page_rows:
            if not r.find_all('form'):
                all_rows.append(r)

        # see if there's a next page, go to next page if so
        if not cur_page_rows[len(cur_page_rows)-1].find_all('input', attrs={'value' : "  >   "}):
            done = True
        else:
            input_params["fpdbr_0_PagingMove"] = '  >   ' # for subdivision or map number search
            input_params["fpdbr_1_PagingMove"] = '  >   ' # for name or addr search

    return all_rows