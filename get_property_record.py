from data_grabber import OklahomaCountyAssessorRecordDataGrabber
from data_parser import OklahomaCountyAssessorDataParser

# Stuff in this file should not touch the outside internet. We use data_grabber for that.

def get_record(propertyid):
    out_dict = {}
    grabber = OklahomaCountyAssessorRecordDataGrabber()

    # Get main page and parse it.
    main_page = grabber.get_initial_page(propertyid)
    top_table = OklahomaCountyAssessorDataParser.parse_main_page_top_table_property_data(main_page)
    out_dict.update(top_table)

    return out_dict

    pass