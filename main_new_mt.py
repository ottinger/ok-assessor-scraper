import real_property
import search_assessor

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import threading
import time

engine = create_engine('sqlite:///results.db',
                       connect_args={'check_same_thread': False})
Session = scoped_session(sessionmaker(bind=engine))
Session.configure(bind=engine)
session = Session

real_property.Base.metadata.create_all(engine)

# Multithreading stuff
qs_sem = threading.BoundedSemaphore(value=10) # Limit it to 5 threads for now
lock = threading.Lock()

# do_squarter_section()
#
# Obtain properties from quarter section qs, and add them to database. We will have each thread run this function.
def do_quarter_section(qs):
    propertyid_list = search_assessor.map_number_search(map_number=qs)

    qs_sem.acquire()

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

            # now save the property. this needs to be thread safe
            lock.acquire()
            try:
                session.add(cur_property)
                session.commit()
            finally:
                lock.release()
            print("ADDED: " + str(cur_property) + " (QS " + str(qs) + ")")
        else:
            print("ALREADY EXISTS: " + str(p) + " (QS " + str(qs) + ")")

    qs_sem.release()

nw_central_quarter_sections = [2661,2662,2663,2664,2665,2666,2667,2668,2669,2670,2671,2672,2849,2850,2852,2851,
                               2896,2893,2895,2894,2673,2674,2675,2676,2677,2678,2679,2680,2681,2682,2683,2684,
                               2897,2898,2899,2900,2717,2718,2719,2720,2713,2714,2715,2716,2709,2710,2711,2712,
                               2941,2942,2943,2944,2721,2722,2723,2724,2725,2726,2727,2728,2729,2730,2731,2732]
                            # between santa fe and portland, and reno and nw 50
quarter_sections = nw_central_quarter_sections
for qs in quarter_sections:
    print("Thread for qs " + str(qs) + " created")
    t = threading.Thread(target=do_quarter_section, args=(qs,))
    t.start()
    time.sleep(1)
