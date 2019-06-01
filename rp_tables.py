# rp_tables.py
#
# Contains classes for table entries on the Real Property page. All of these classes will
# have relationships with real_property.RealProperty.

# These (will) include:
# * ValuationHistory
# * PropertyAccountStatus (low priority)
# * TransactionHistory
# * NoticeOfValue (low priority)
# * BuildingPermitHistory
# * BuildingTableEntry

from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

import requests
from bs4 import BeautifulSoup
import re

from base import Base

class ValuationHistory(Base):
    __tablename__ = "valuationhistory"

    id = Column(Integer, primary_key=True)
    local_property_id = Column(Integer, ForeignKey('realproperty.id')) # Not to be confused with "propertyid" (assigned by assessor site)
    property = relationship("RealProperty", back_populates="valuations")

    year = Column(Integer)
    market_value = Column(Integer)
    taxable_market_value = Column(Integer)
    gross_assessed = Column(Integer)
    exemption = Column(Integer)
    net_assessed = Column(Integer)
    millage = Column(Float)
    tax = Column(Float)
    tax_savings = Column(Float)