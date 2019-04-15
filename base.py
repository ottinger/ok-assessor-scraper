# base.py
#
# Contains the declarative base. It's in its own file (at least for now) since we have classes
# in multiple .py files that need to call it.

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()