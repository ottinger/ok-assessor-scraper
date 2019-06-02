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
    hvac_type = Column(String)

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