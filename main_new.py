import real_property
import search_assessor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///results.db')
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

real_property.Base.metadata.create_all(engine)

nw_central_quarter_sections = [2661,2662,2663,2664,2665,2666,2667,2668,2669,2670,2671,2672,2849,2850,2852,2851,
                               2896,2893,2895,2894,2673,2674,2675,2676,2677,2678,2679,2680,2681,2682,2683,2684,
                               2897,2898,2899,2900,2717,2718,2719,2720,2713,2714,2715,2716,2709,2710,2711,2712,
                               2941,2942,2943,2944,2721,2722,2723,2724,2725,2726,2727,2728,2729,2730,2731,2732]
                            # between santa fe and portland, and reno and nw 50


quarter_sections = nw_central_quarter_sections

print(session.query(real_property.RealProperty))

for qs in quarter_sections:
    propertyid_list = search_assessor.map_number_search(map_number=qs)

    for p in propertyid_list:
        if session.query(real_property.RealProperty).\
                filter(real_property.RealProperty.propertyid==p).count() == 0:
            print("starting propertyid "+p)
            cur_property = real_property.RealProperty(propertyid=p)
            cur_property.extractRealPropertyData(propertyid=p)
            print("extractRealPropertyData finished for propertyid "+p)
            cur_property.extractValuationHistory(p)
            print("extractValuationHistory finished for propertyid "+p)
            cur_property.extractBuildings(p)
            print("extractBuildings finished for propertyid "+p)
            session.add(cur_property)
            session.commit()
            print("ADDED: " + str(cur_property))
        else:
            print("ALREADY EXISTS: " + str(p))