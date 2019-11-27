# buildings.py
#
# Contains a class representing each building, including data in both the buildings
# table (which was previously in rp_tables.py) as well as the buildings page for each
# building.
from sqlalchemy import Column, Integer, Float, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from base import Base

import requests
import get_tables
import re

from bs4 import BeautifulSoup

import real_property

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True)
    local_property_id = Column(Integer, ForeignKey('realproperty.id'))
    property = relationship("RealProperty", back_populates="buildings")

    # Fields in the buildings table on the main property page
    bldg_id = Column(Integer) # this is specific to the property (starting with 1 for each property)
    vacant_or_improved = Column(String)
    bldg_description = Column(String)
    year_built = Column(Integer)
    sq_ft = Column(Integer)
    number_stories = Column(Numeric) # Change to float?

    # Fields from building detail page

    # NOTE: We'll only be getting certain fields for now.
    #
    # Some buildings also have multiple detail pages, which seem to mainly be to indicate different
    # unit sizes for residential units. We'll be ignoring that for now, especially since the
    # accuracy/quality of the data may be a little uncertain.

    remodel_year = Column(Integer)
    building_name = Column(String) # new
    alt_land_use_desc = Column(String) # new
    quality_description = Column(String)
    frame_description = Column(String)
    foundation_description = Column(String) # new
    exterior = Column(String) # new
    roof_type = Column(String) # new
    roof_cover = Column(String) # new
    avg_floor_height = Column(Integer)
    percent_sprinkled = Column(Integer)
    total_rooms = Column(Integer)
    bedrooms = Column(Integer)
    full_bathrooms = Column(Integer)
    three_quarters_bathrooms = Column(Integer)
    half_bathrooms = Column(Integer)
    hvac_type = Column(String)
    physical_condition = Column(String)
    number_res_units = Column(Integer)
    number_comm_units = Column(Integer)

    # extract()
    #
    # Static method called from RealProperty class. Given a propertyid, extracts a list of the
    # buildings from the table on main page and creates Building objects. DOES NOT obtain data
    # from building detail pages.
    @staticmethod
    def extract(propertyid):
        building_dicts = get_tables.get_building_list(propertyid)

        building_list = []
        for d in building_dicts:
            b = Building()
            b.bldg_id = d['building_number']
            b.vacant_or_improved = d['vacant_or_improved']
            b.bldg_description = d['building_description']
            b.year_built = d['year_built']
            b.sq_ft = d['square_feet']
            b.number_stories = d['stories']

            building_list.append(b)

        return building_list

    # extractBuildingDetails()
    #
    # Extract data from building detail page. This is not a static method (as with extract()),
    # but rather to be run on an existing Building object.
    def extractBuildingDetails(self):
        propertyid = self.property.propertyid
        detail_url = "https://ariisp1.oklahomacounty.org/AssessorWP5/BLDG_Detail.asp?PropertyID=" +\
                str(propertyid) + "&BuildingSequence=" + str(self.bldg_id)

        html = requests.get(detail_url, timeout=15).text


        mySoup = BeautifulSoup(html, features="lxml")
        rows = mySoup.find_all('table')[3].tbody.find_all('tr')

        try:
            self.remodel_year = int(rows[6].find_all('td')[1].font.string.strip())
        except ValueError:
            self.remodel_year = -1
        self.building_name = rows[7].find_all('td')[1].font.string.strip()
        self.alt_land_use_desc = rows[8].find_all('td')[1].font.string.strip()
        self.quality_description = rows[9].find_all('td')[1].font.string.strip()
        self.frame_description = rows[10].find_all('td')[1].font.string.strip()
        self.foundation_description = rows[11].find_all('td')[1].font.string.strip() # new
        self.exterior = rows[12].find_all('td')[1].font.string.strip() # new
        self.roof_type = rows[13].find_all('td')[1].font.string.strip() # new
        self.roof_cover = rows[14].find_all('td')[1].font.string.strip() # new
        try:
            self.avg_floor_height = int(rows[15].find_all('td')[1].font.string.strip())
        except ValueError:
            self.avg_floor_height = -1
        try:
            self.percent_sprinkled = int(rows[16].find_all('td')[1].font.string.strip())
        except ValueError:
            self.percent_sprinkled = -1

        try:
            self.total_rooms = int(rows[18].find_all('td')[1].font.string.strip())
        except ValueError:
            self.total_rooms = -1

        # Number of units with bedrooms. We'll use this for single family homes since
        # it has number of bedrooms. But for multifamily buildings, we'll just use the
        # number of units/number of sqft (at least for now).
        bedrooms_re = r'# of units \(([0-9]+)\) with ([0-9]+) Bedrooms'
        bedrooms_str = ' '.join(rows[19].find_all('td')[1].font.string.strip().split()) # must remove newlines
        bedrooms_match = re.match(bedrooms_re, bedrooms_str)
        if bedrooms_match:
            bedrooms_str = bedrooms_match.group(2)
            try:
                self.bedrooms = int(bedrooms_str) # Again, ONLY FOR SFH's!
            except ValueError:
                self.bedrooms = -1
        else:
            self.bedrooms = -1

        bathrooms_re = r'\(([0-9]+)\)-Full, \(([0-9]+)\)-3\/4, \(([0-9]+)\)-half'
        bathrooms_str = ' '.join(rows[20].find_all('td')[1].font.string.strip().split()) # must remove newlines
        bathrooms_match = re.match(bathrooms_re, bathrooms_str)
        if bathrooms_match:
            try:
                self.full_bathrooms = int(bathrooms_match.group(1))
                self.three_quarters_bathrooms = int(bathrooms_match.group(2))
                self.half_bathrooms = int(bathrooms_match.group(3))
            except ValueError:
                self.full_bathrooms, self.three_quarters_bathrooms, self.half_bathrooms = -1, -1, -1
        else:
            self.full_bathrooms, self.three_quarters_bathrooms, self.half_bathrooms = -1, -1, -1


        self.hvac_type = rows[21].find_all('td')[1].font.string.strip()

        self.physical_condition = rows[24].find_all('td')[1].string.strip()
        try:
            self.number_res_units = int(rows[25].find_all('td')[1].font.string.strip())
        except ValueError:
            self.number_res_units = -1
        try:
            self.number_comm_units = int(rows[26].find_all('td')[1].font.string.strip())
        except ValueError:
            self.number_comm_units = -1
