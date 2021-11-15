from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship

import requests
from bs4 import BeautifulSoup
import re

from base import Base

import helpers
from rp_tables import ValuationHistory
from rp_tables import DeedTransaction
from rp_tables import BuildingPermit
from old.buildings import Building


class RealProperty(Base):
    __tablename__ = "realproperty"

    # First 2 rows of property record display
    id = Column(Integer, primary_key=True)
    propertyid = Column(Integer) # This is the PROPERTYID=xxxxxx from the url
    account_number = Column(String) # This is usually a letter followed by numbers
    property_type = Column(String) # Change to enum?
    location = Column(String) # This is usually the address of the property
    building_name_occupant = Column(String)
    city = Column(String)

    # Owner contact info
    owner_name_1 = Column(String)
    owner_name_2 = Column(String)
    billing_address_1 = Column(String)
    billing_address_2 = Column(String)
    city_state_zip = Column(String)

    # Other stuff
    quarter_section = Column(Integer)
    parent_acct = Column(String)
    tax_district = Column(String)
    school_system = Column(String)
    land_size = Column(Float) # Square feet
    lot_width = Column(Float)
    lot_depth = Column(Float)
    land_value = Column(Integer)
    quarter_section_description = Column(String)
    subdivision = Column(String)
    block = Column(String) # We will keep block/lot formatted as strings even though they kinda are ints
    lot = Column(String) # see above
    legal_description = Column(String)

    valuations = relationship("ValuationHistory", back_populates="property")
    buildings = relationship("Building", back_populates="property") # NOT to be confused with BuildingDetails
    deedtransactions = relationship("DeedTransaction", back_populates="property")
    buildingpermits = relationship("BuildingPermit", back_populates="property")

    def __repr__(self):
        return "<RealProperty(propertyid='%s', location='%s', city='%s'>" % (self.propertyid, self.location, self.city)

    # extractRealPropertyData()
    #
    # Extracts data from the top table for a real property.
    #
    # Arguments: (one of these two are required)
    # * property_html: contains the html for the page we're scraping.
    # * propertyid: the PROPERTYID for the page we're scraping (which we'll use to get the html)
    def extractRealPropertyData(self, **kwargs):
        if 'property_html' in kwargs:
            html = kwargs['property_html']
        elif 'propertyid' in kwargs:
            html = requests.get("https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PROPERTYID=" +
                                   str(kwargs['propertyid']), timeout=15).text
        else:
            return None


        mySoup = BeautifulSoup(html, features="lxml")
        rows = mySoup.find_all('table')[3].tbody.find_all('tr')

        # TODO: add support for grabbing propertyid from hidden form if it is not passed as an arg
        self.propertyid = kwargs['propertyid']

        # Now let's process rows in the top table
        cur_tds = rows[0].find_all('td')  # Row 0
        self.account_number = cur_tds[0].font.font.string.strip()  # acct #, remove whitespace
        self.property_type = cur_tds[1].font.font.string.strip()
        self.location = cur_tds[4].font.string.strip()

        cur_tds = rows[1].find_all('td')  # row 1
        self.building_name_occupant = cur_tds[1].font.string.strip()
        self.city = cur_tds[3].font.string.strip()

        cur_tds = rows[2].find_all('td')
        self.owner_name_1 = cur_tds[1].font.string.strip()
        self.quarter_section = helpers.get_int(cur_tds[3].font.string.strip())

        cur_tds = rows[3].find_all('td')
        self.owner_name_2 = cur_tds[1].font.string.strip()
        self.parent_acct = cur_tds[3].font.string.strip()

        cur_tds = rows[4].find_all('td')
        self.billing_address_1 = cur_tds[1].font.string.strip()
        self.tax_district = cur_tds[3].input['value'] # "TXD xxx", no link

        cur_tds = rows[5].find_all('td')
        self.billing_address_2 = cur_tds[1].font.string.strip()
        self.school_system = cur_tds[3].font.string.strip()

        cur_tds = rows[6].find_all('td')
        self.city_state_zip = ' '.join(cur_tds[1].font.string.split()) # replace escapes with spaces
        self.land_size_str = ' '.join(cur_tds[3].font.string.split()) # same as above. TODO: Convert this to sqft or acres!
        if re.match(r'(.*) Square Feet', self.land_size_str):
            self.land_size = helpers.get_float(re.match(r'(.*) Square Feet', self.land_size_str).group(1))
        elif re.match(r'(.*) Acres', self.land_size_str):
            land_size_acres = helpers.get_float(re.match(r'(.*) Acres', self.land_size_str).group(1))
            self.land_size = land_size_acres * 43560 # Convert to square feet

        cur_tds = rows[8].find_all('td')
        land_value_str = cur_tds[1].find_all('font')[1].string.strip() # will need to be converted to integer
        self.land_value = helpers.get_int(land_value_str)
        # TODO: Implement lot dimensions

        # Nothing we need on row 8, it is just a link to taxes (using the acct number we already have)

        cur_tds = rows[9].find_all('td')
        self.quarter_section_description = ' '.join(cur_tds[0].font.string.split())
        subdivision_str = ' '.join(cur_tds[1].a.string.split())
        # We had to change the [0-9] for block/lot because some apparently have alpha characters in them...
        self.subdivision, self.block, self.lot = re.findall(
            r'(.+) Block ([a-zA-Z0-9]+) Lot ([a-zA-Z0-9]+)', subdivision_str
        )[0]

        # Get legal description (it's technically in another table)
        rows = mySoup.find_all('table')[4].tbody.find_all('tr')
        cur_tds = rows[0].find_all('td')
        self.legal_description = cur_tds[0].font.text.splitlines()[-1].strip()

        return True # successful

    def extractValuationHistory(self, propertyid):
        vh_list = ValuationHistory.extract(propertyid)
        self.valuations = vh_list
        return vh_list

    def extractDeedHistory(self, propertyid):
        dt_list = DeedTransaction.extract(propertyid)
        self.deedtransactions = dt_list
        return dt_list

    def extractBuildingPermits(self, propertyid):
        bp_list = BuildingPermit.extract(propertyid)
        self.buildingpermits = bp_list
        return bp_list

    def extractBuildings(self, propertyid):
        bldg_list = Building.extract(propertyid)
        self.buildings = bldg_list

        get_details = True
        if get_details:
            for b in bldg_list:
                b.extractBuildingDetails()

        return bldg_list
