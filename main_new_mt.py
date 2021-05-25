import real_property
import search_assessor

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import logging
import threading
import time

logging.basicConfig(filename='scraper.log', filemode='w', level=logging.DEBUG)

engine = create_engine('sqlite:///results.db')
Session = scoped_session(sessionmaker(bind=engine))
Session.configure(bind=engine)
session = Session # With a scoped_session, this is the same as Session()

real_property.Base.metadata.create_all(engine)

# Multithreading stuff
qs_sem = threading.BoundedSemaphore(value=5) # Limit it to 5 threads for now

# We will have threads save RealProperty objects here, then the main thread will save/commit them.
global_property_list = []
# This lock is for global_property_list, NOT the database! The main thread will do the committing.
lock = threading.Lock()

# do_quarter_section()
#
# Obtain properties from quarter section qs, and add them to database. We will have each thread run this function.
def do_quarter_section(qs):
    propertyid_list = search_assessor.map_number_search(map_number=qs)

    qs_sem.acquire()

    for p in propertyid_list:
        if p not in extant_propertyids:
            print("starting propertyid "+str(p))
            cur_property = real_property.RealProperty(propertyid=p)
            cur_property.extractRealPropertyData(propertyid=p)
            print("extractRealPropertyData finished for propertyid "+str(p))
            cur_property.extractValuationHistory(p)
            print("extractValuationHistory finished for propertyid "+str(p))
            cur_property.extractBuildings(p)
            print("extractBuildings finished for propertyid "+str(p))
            cur_property.extractDeedHistory(p)
            print("extractDeedHistory finished for propertyid "+str(p))
            cur_property.extractBuildingPermits(p)
            print("extractBuildingPermits finished for propertyid "+str(p))

            # Now save the RealProperty to list. The main thread will save/commit it.
            lock.acquire()
            try:
                global_property_list.append(cur_property)
            finally:
                lock.release()
            print("COMPLETED: " + str(cur_property) + " (QS " + str(qs) + ")")

    qs_sem.release()
    print("QS " + str(qs) + " finished")

'''
nw_central_quarter_sections = [2661,2662,2663,2664,2665,2666,2667,2668,2669,2670,2671,2672,2849,2850,2852,2851,
                               2896,2893,2895,2894,2673,2674,2675,2676,2677,2678,2679,2680,2681,2682,2683,2684,
                               2897,2898,2899,2900,2717,2718,2719,2720,2713,2714,2715,2716,2709,2710,2711,2712,
                               2941,2942,2943,2944,2721,2722,2723,2724,2725,2726,2727,2728,2729,2730,2731,2732]
                            # between santa fe and portland, and reno and nw 50
quarter_sections = nw_central_quarter_sections
# quarter_sections = [1002, 1003, 1004, 1006]
'''

quarter_sections = [x for x in range(1001, 4945)]

# Find assessor PROPERTYIDs that already exist in the realproperty table
extant_propertyids = [x[0] for x in session.query(real_property.RealProperty.propertyid)]

# Create threads
threads_list = []
for qs in quarter_sections:
    print("Thread for qs " + str(qs) + " created")
    t = threading.Thread(target=do_quarter_section, args=(qs,))
    t.start()
    threads_list.append(t)
    time.sleep(1)

# Wait for workers to return objects, then save them to the database. Keep going as long as we have running threads
# and/or properties to commit
while len(threading.enumerate()) > 1 or len(global_property_list) > 0:
    lock.acquire()
    try:
        if len(global_property_list) > 0:
            for p in global_property_list:
                session.add(p)
                session.commit()
                global_property_list.remove(p)
                print("ADDED: " + str(p))
    finally:
        lock.release()
    time.sleep(5) # Check only every 5 seconds


print("All quarter sections finished")
