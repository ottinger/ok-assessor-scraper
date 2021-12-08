from bs4 import BeautifulSoup
import helpers
import re


class MultiPageRecordDataParser:
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
    def get_sae_record(my_row):  # table_number==9
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
    def get_transaction_record(my_row):  # table_number==10
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
    def get_mailed_nov_record(my_row):  # table_number==11
        pass  # NOT IMPLEMENTED

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
    def get_building_record(my_row):  # table_number==13
        cur_tds = my_row.find_all('td')

        cur_dict = {}
        cur_dict['building_number'] = helpers.get_int(
            cur_tds[1].font.font.string.strip())  # Yo dawg I heard you like font tags
        cur_dict['vacant_or_improved'] = cur_tds[2].font.string.strip()
        cur_dict['building_description'] = cur_tds[3].font.string.strip()
        try:
            cur_dict['year_built'] = int(cur_tds[4].font.string.strip())
        except ValueError:
            cur_dict['year_built'] = -1
        cur_dict['square_feet_str'] = cur_tds[5].font.string.strip()  # needs converted to int
        try:
            cur_dict['square_feet'] = helpers.get_sq_ft(cur_dict['square_feet_str']) if \
                cur_dict['square_feet_str'] != '' else 0
        except ValueError:
            cur_dict['square_feet'] = -1
        cur_dict['stories_str'] = cur_tds[6].font.string.strip()
        try:
            # needs to be float since it can be "1.5" stories
            cur_dict['stories'] = float(re.findall(r'([0-9]+(?:\.[0-9]+)*)', cur_dict['stories_str'])[0])
        except (ValueError, IndexError):
            cur_dict['stories'] = -1
        return cur_dict

    # parse_paginated_table_record()
    #
    # Parse a row in the table.
    def parse_paginated_table_record(self, record, table_id):
        pass

    # parse_paginated_tables()
    #
    # Parse the results we get from OklahomaCountyAssessorRecordDataGrabber.get_paginated_tables_from_main_page().
    def parse_paginated_tables(self, page_list, table_enum):
        table_id = table_enum.value

        for cur_page in page_list:
            the_soup = BeautifulSoup(cur_page, features="lxml")
            rows = the_soup.find_all('table')[table_id].tbody.find_all('tr')

            for row in rows:
                pass
            pass
        pass


# We will have 1 instance of this for each property record.....?
# Probably not. All methods static, get_property_record.py will piece it all together.
class OklahomaCountyAssessorDataParser:
    @staticmethod
    def parse_main_page_top_table_property_data(html):
        out_dict = {}
        mySoup = BeautifulSoup(html, features="lxml")
        rows = mySoup.find_all('table')[3].tbody.find_all('tr')

        # Now let's process rows in the top table
        cur_tds = rows[0].find_all('td')  # Row 0
        out_dict['account_number'] = cur_tds[0].font.font.string.strip()  # acct #, remove whitespace
        out_dict['property_type'] = cur_tds[1].font.font.string.strip()
        out_dict['location'] = cur_tds[4].font.string.strip()

        cur_tds = rows[1].find_all('td')  # row 1
        out_dict['building_name_occupant'] = cur_tds[1].font.string.strip()
        out_dict['city'] = cur_tds[3].font.string.strip()

        cur_tds = rows[2].find_all('td')
        out_dict['owner_name_1'] = cur_tds[1].font.string.strip()
        out_dict['quarter_section'] = helpers.get_int(cur_tds[3].font.string.strip())

        cur_tds = rows[3].find_all('td')
        out_dict['owner_name_2'] = cur_tds[1].font.string.strip()
        out_dict['parent_acct'] = cur_tds[3].font.string.strip()

        cur_tds = rows[4].find_all('td')
        out_dict['billing_address_1'] = cur_tds[1].font.string.strip()
        out_dict['tax_district'] = cur_tds[3].input['value'] # "TXD xxx", no link

        cur_tds = rows[5].find_all('td')
        out_dict['billing_address_2'] = cur_tds[1].font.string.strip()
        out_dict['school_system'] = cur_tds[3].font.string.strip()

        cur_tds = rows[6].find_all('td')
        out_dict['city_state_zip'] = ' '.join(cur_tds[1].font.string.split()) # replace escapes with spaces
        out_dict['land_size_str'] = ' '.join(cur_tds[3].font.string.split()) # same as above. TODO: Convert this to sqft or acres!
        if re.match(r'(.*) Square Feet', out_dict['land_size_str']):
            out_dict['land_size'] = helpers.get_float(re.match(r'(.*) Square Feet', out_dict['land_size_str']).group(1))
        elif re.match(r'(.*) Acres', out_dict['land_size_str']):
            land_size_acres = helpers.get_float(re.match(r'(.*) Acres', out_dict['land_size_str']).group(1))
            out_dict['land_size'] = land_size_acres * 43560 # Convert to square feet

        cur_tds = rows[8].find_all('td')
        land_value_str = cur_tds[1].find_all('font')[1].string.strip() # will need to be converted to integer
        out_dict['land_value'] = helpers.get_int(land_value_str)
        # TODO: Implement lot dimensions

        # Nothing we need on row 8, it is just a link to taxes (using the acct number we already have)

        cur_tds = rows[9].find_all('td')
        out_dict['quarter_section_description'] = ' '.join(cur_tds[0].font.string.split())
        subdivision_str = ' '.join(cur_tds[1].a.string.split())
        # We had to change the [0-9] for block/lot because some apparently have alpha characters in them...
        out_dict['subdivision'], out_dict['block'], out_dict['lot'] = re.findall(
            r'(.+) Block ([a-zA-Z0-9]+) Lot ([a-zA-Z0-9]+)', subdivision_str
        )[0]

        # Get legal description (it's technically in another table)
        rows = mySoup.find_all('table')[4].tbody.find_all('tr')
        cur_tds = rows[0].find_all('td')
        out_dict['legal_description'] = cur_tds[0].font.text.splitlines()[-1].strip()

        return out_dict