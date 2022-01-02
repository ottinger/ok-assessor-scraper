import data_parser
from data_grabber import OklahomaCountyAssessorRecordDataGrabber, PaginatedTableTypes
from data_parser import OklahomaCountyAssessorDataParser

# Stuff in this file should not touch the outside internet. We use data_grabber for that.

def get_record(propertyid):
    out_dict = {}
    grabber = OklahomaCountyAssessorRecordDataGrabber()

    # Get main page and parse it.
    main_page = grabber.get_initial_page(propertyid)
    top_table = OklahomaCountyAssessorDataParser.parse_main_page_top_table_property_data(main_page)
    out_dict.update(top_table)

    for table_type in PaginatedTableTypes:
        table_pages = grabber.get_paginated_table_from_main_page(propertyid, table_type)
        table_dict = data_parser.MultiPageRecordDataParser.parse_paginated_tables(table_pages, table_type)

        out_dict[table_type.name.lower()] = table_dict

    return out_dict