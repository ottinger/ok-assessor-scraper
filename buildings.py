# buildings.py
#
# Contains classes for the individual building DETAIL pages.
# Not to be confused with entries for the buildings table (found in rp_tables.py)

# Not currently implemented
import requests
import helpers
from bs4 import BeautifulSoup

from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from base import Base

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

    # We'll put fields from the building detail page below