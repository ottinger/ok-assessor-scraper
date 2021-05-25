# get_real_tables.py
#
# Contains a method, get_table_rows(), to obtain any table from the main property record
# page.
#
# May eventually be expanded to parse tables for individual buildings.
import requests
from bs4 import BeautifulSoup
import helpers
import re


def get_valuation_list(id):
    return get_table_rows(7, id)


def get_sae_list(id):
    return get_table_rows(8, id)


def get_transaction_list(id):
    return get_table_rows(10, id)


def get_permit_list(id):
    return get_table_rows(12, id)


def get_building_list(id):
    return get_table_rows(13, id)

# get_table_rows()
#
# Gets a list of rows in a table, across multiple pages if needed. Returns a dictionary.
#
# table_number: 7 for valuation record, 10 for transaction record
def get_table_rows(table_number, id):
    # We need a session to go between pages properly. Otherwise it goes like: 1, 2, 2, 3, 2, 3, 2, ... forever
    sesh = requests.session()
    # get the first page
    req = sesh.get("https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PROPERTYID="+str(id))
    data = req.text

    the_soup = BeautifulSoup(data, features="lxml")
    rows = the_soup.find_all('table')[table_number].tbody.find_all('tr')

    done = False
    valuation_list = []
    while done == False: # Iterate over pages
        for r in rows:
            if r.find_all('p'): # Get this page
                if table_number==7: # Valuation History
                    cur_dict = get_valuation_record(r)
                elif table_number==8: # Account Status/Adjustments/Exemptions
                    cur_dict = get_sae_record(r)
                elif table_number==10: # Transaction History (table_number==10)
                    cur_dict = get_transaction_record(r)
                elif table_number==12: # Building permits
                    cur_dict = get_permit_record(r)
                elif table_number==13:
                    cur_dict = get_building_record(r)
                valuation_list.append(cur_dict)

        # see if we are on last page
        if not rows[len(rows)-1].find_all('input', attrs={'value' : "  >   "}):
            done = True

        # get the next page now
        if table_number == 7: # Valuation History
            input_name = 'fpdbr_24_PagingMove'
        elif table_number == 12: # Building Permit
            input_name = 'fpdbr_16_PagingMove'
        elif table_number == 13: # Building Record
            input_name = 'fpdbr_18_PagingMove' # building record. (propertyid 134581 has more than 1 page of bldgs)
        else: # Transaction History
            input_name = 'fpdbr_13_PagingMove'
        req = sesh.post("https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp", cookies = req.cookies,
                            data = { 'PropertyID' : str(id), input_name : '  >   '})
        data = req.text
        the_soup = BeautifulSoup(data, features="lxml")
        rows = the_soup.find_all('table')[table_number].tbody.find_all('tr')

    return valuation_list

# get_valuation_record()
#
# Returns a unit of valuation history for one year. Takes a row from the beautifulsoup
# object as an arg.
def get_valuation_record(my_row):
    cur_tds = my_row.find_all('td')
    cur_year = cur_tds[0].font.string.strip()

    cur_dict = {}
    cur_dict['year'] = helpers.get_int(cur_year)
    cur_dict['market_value'] = helpers.get_int(cur_tds[1].font.string.strip())
    cur_dict['taxable_market_value'] = helpers.get_int(cur_tds[2].font.string.strip())
    cur_dict['gross_assessed'] = helpers.get_int(cur_tds[3].font.string.strip())
    cur_dict['exemption'] = helpers.get_int(cur_tds[4].font.string.strip())
    cur_dict['net_assessed'] = helpers.get_int(cur_tds[5].font.string.strip())
    cur_dict['millage'] = helpers.get_float(cur_tds[6].font.string.strip())
    cur_dict['tax'] = helpers.get_float(cur_tds[7].font.string.strip())
    cur_dict['tax_savings'] = helpers.get_float(cur_tds[8].font.string.strip())
    return cur_dict

# get_sae_record()
#
# Returns a record in the Property Account Status/Adjustments/Exemptions table.
#
# NOT TESTED
def get_sae_record(my_row): # table_number==9
    cur_tds = my_row.find_all('td')

    cur_dict = {}
    cur_dict['account_number'] = cur_tds[0].font.string.strip()
    cur_dict['grant_year'] = cur_tds[1].font.string.strip()
    cur_dict['exemption_description'] = cur_tds[2].font.string.strip()
    cur_dict['amount'] = helpers.get_int(cur_tds[3].font.string.strip())

    return cur_dict

# get_transaction_record()
#
# Returns a transaction record as a dict. To be interchangeable with get_valuation_record()
def get_transaction_record(my_row): # table_number==10
    cur_tds = my_row.find_all('td')

    cur_dict = {}
    cur_dict['date'] = cur_tds[0].font.string.strip()
    # td 1 is link to record lookup, we won't be using that. just book/page
    cur_dict['type'] = cur_tds[2].font.string.strip()
    cur_dict['book'] = helpers.get_int(cur_tds[3].a.string.strip())
    cur_dict['page'] = helpers.get_int(cur_tds[4].a.string.strip())
    cur_dict['price'] = helpers.get_int(cur_tds[5].font.string.strip())
    cur_dict['grantor'] = cur_tds[6].font.string.strip()
    cur_dict['grantee'] = cur_tds[7].font.string.strip()

    return cur_dict

# get_mailed_nov_record()
#
# Returns a Mailed Notice Of Value record as a dict
def get_mailed_nov_record(my_row): # table_number==11
    pass # NOT IMPLEMENTED

# get_permit_record()
#
# Returns a building permit record as a dict
def get_permit_record(my_row):
    cur_tds = my_row.find_all('td')

    cur_dict = {}
    cur_dict['date'] = cur_tds[0].font.string.strip()
    cur_dict['permit_number'] = cur_tds[1].font.string.strip()
    cur_dict['provided_by'] = cur_tds[2].font.string.strip()
    cur_dict['building_number'] = helpers.get_int(cur_tds[3].font.string.strip())
    cur_dict['description'] = cur_tds[4].font.string.strip()
    cur_dict['estimated_cost'] = helpers.get_int(cur_tds[5].font.string.strip())
    cur_dict['status'] = cur_tds[6].font.string.strip()

    return cur_dict

# get_building_record()
#
# Returns a record for a building on a parcel as a dict
def get_building_record(my_row): # table_number==13
    cur_tds = my_row.find_all('td')

    cur_dict = {}
    cur_dict['building_number'] = helpers.get_int(cur_tds[1].font.font.string.strip()) # Yo dawg I heard you like font tags
    cur_dict['vacant_or_improved'] = cur_tds[2].font.string.strip()
    cur_dict['building_description'] = cur_tds[3].font.string.strip()
    try:
        cur_dict['year_built'] = int(cur_tds[4].font.string.strip())
    except ValueError:
        cur_dict['year_built'] = -1
    cur_dict['square_feet_str'] = cur_tds[5].font.string.strip() # needs converted to int
    try:
        cur_dict['square_feet'] = helpers.get_sq_ft(cur_dict['square_feet_str']) if \
            cur_dict['square_feet_str'] != '' else 0
    except ValueError:
        cur_dict['square_feet'] = -1
    cur_dict['stories_str'] = cur_tds[6].font.string.strip()
    try:
        # needs to be float since it can be "1.5" stories
        cur_dict['stories'] = float(re.findall(r'([0-9]+(?:\.[0-9]+)*)', cur_dict['stories_str'])[0])
    except (ValueError,IndexError):
        cur_dict['stories'] = -1
    return cur_dict