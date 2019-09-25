# buildings.py
#
# Contains a class representing each building, including data in both the buildings
# table (which was previously in rp_tables.py) as well as the buildings page for each
# building.
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from base import Base

import requests
import get_tables
import time
import urllib3

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
    number_stories = Column(Integer)

    # Fields from building detail page

    # NOTE: We'll only be getting certain fields for now.
    #
    # Some buildings also have multiple detail pages, which seem to mainly be to indicate different
    # unit sizes for residential units. We'll be ignoring that for now, especially since the
    # accuracy/quality of the data may be a little uncertain.

    remodel_year = Column(Integer)
    frame_description = Column(String)
    quality_description = Column(String)
    physical_condition = Column(String)
    avg_floor_height = Column(Integer)
    percent_sprinkled = Column(Integer)
    number_res_units = Column(Integer)
    number_comm_units = Column(Integer)
    hvac_type = Column(String)

    # extract()
    #
    # Static method called from RealProperty class. Given a propertyid, extracts a list of the
    # buildings from the table on main page and creates Building objects. DOES NOT obtain data
    # from building detail pages.
    def extract(propertyid):
        try:
            building_dicts = get_tables.get_building_list(propertyid)
        # Occasionally the connection will fail. If so, wait a few and call the function again
        except (ConnectionError,TimeoutError,urllib3.exceptions.NewConnectionError,
                urllib3.exceptions.MaxRetryError, requests.ConnectionError) as e:
            print("Exception caught: "+str(e))
            time.sleep(10)
            return Building.extract(propertyid)

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
        print(detail_url)

        try:
            html = requests.get(detail_url).text
        # Occasionally the connection will fail. If so, wait a few and call the function again
        except (ConnectionError,TimeoutError,urllib3.exceptions.NewConnectionError,
                urllib3.exceptions.MaxRetryError, requests.ConnectionError) as e:
            print("Exception caught: "+str(e))
            time.sleep(10)
            return self.extractBuildingDetails()


        mySoup = BeautifulSoup(html, features="lxml")
        rows = mySoup.find_all('table')[3].tbody.find_all('tr')

        try:
            self.remodel_year = int(rows[6].find_all('td')[1].font.string.strip())
        except ValueError:
            self.remodel_year = -1
        self.frame_description = rows[10].find_all('td')[1].font.string.strip()
        self.quality_description = rows[9].find_all('td')[1].font.string.strip()
        self.physical_condition = rows[24].find_all('td')[1].string.strip()
        try:
            self.avg_floor_height = int(rows[15].find_all('td')[1].font.string.strip())
        except ValueError:
            self.avg_floor_height = -1
        try:
            self.percent_sprinkled = int(rows[16].find_all('td')[1].font.string.strip())
        except ValueError:
            self.percent_sprinkled = -1
        try:
            self.number_res_units = int(rows[25].find_all('td')[1].font.string.strip())
        except ValueError:
            self.number_res_units = -1
        try:
            self.number_comm_units = int(rows[26].find_all('td')[1].font.string.strip())
        except ValueError:
            self.number_comm_units = -1
        self.hvac_type = rows[21].find_all('td')[1].font.string.strip()