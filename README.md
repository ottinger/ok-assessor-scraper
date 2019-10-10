# ok-assessor-scraper

The goal of this project is to develop a scraper/API to capture data from the Oklahoma County, OK Assessor Database at https://ariisp1.oklahomacounty.org/AssessorWP5/DefaultSearch.asp.

This scraper captures assessor data to a sqlite database using SQLAlchemy ORM.

As of present, data captured includes:
* Information about the property owner and the parcel itself (from the top of the page) in table **realproperty**
* Information about the valuation/taxation history of the parcel in table **valuationhistory**
* Some information about the buildings on the parcel in table **buildings**

*Note that this project is still very much a work in progress, and that a lot of functionality has not been fully implemented yet.*

### HOW TO USE:
* Use Python 3 (3.6.5 recommended)
* Install the dependencies in pip (bs4, lxml, requests)
* Choose the quarter sections you want data for; map with quarter section numbers available at https://ariisp1.oklahomacounty.org/assessor/Searches/City_Map_with_Map_Numbers.PDF. Add them to the quarter_sections list in main.py.
* Run main_new_mt.py (multithreaded). Database will be saved to results.db.

### DEPENDENCIES NEEDED:
* bs4 (BeautifulSoup)
* lxml
* requests
* sqlalchemy

### TO DO LIST:
* Finish implementing fields in RealProperty (there are a couple left)
* Implement parsing for tables on main page: property status/adjustments/exemptions, deed transaction history, notice of value history, building permit history
* Add support for Personal/Central property results
* Implement a nicer way to run the scraper
* Improve test coverage
* General cleanup