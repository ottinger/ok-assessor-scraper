import real_property
import search_assessor

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import sys
import threading
import time
import urllib3,requests,socket # for error handling

# We will have threads save RealProperty objects here, then the main thread will save/commit them.
global_property_list = []
# This lock is for global_property_list, NOT the database! The main thread will do the committing.
lock = threading.Lock()

# This is the pool of propertyid's that still have to be done
propertyid_pool = []
# This lock is for propertyid_pool
propertyid_pool_lock = threading.Lock()

########################################################################################

# Main scraper thread
def scraper_thread():
    while propertyid_pool:
        # Get the propertyid to scrape
        propertyid_pool_lock.acquire()
        try:
            cur_propertyid = propertyid_pool.pop()
        finally:
            propertyid_pool_lock.release()
        if cur_propertyid in extant_propertyids:
            continue

        try:
            print("starting propertyid "+str(cur_propertyid))
            cur_property = real_property.RealProperty(propertyid=cur_propertyid)
            cur_property.extractRealPropertyData(propertyid=cur_propertyid)
            print("extractRealPropertyData finished for propertyid "+str(cur_propertyid))
            cur_property.extractValuationHistory(cur_propertyid)
            print("extractValuationHistory finished for propertyid "+str(cur_propertyid))
            cur_property.extractBuildings(cur_propertyid)
            print("extractBuildings finished for propertyid "+str(cur_propertyid))
            cur_property.extractDeedHistory(cur_propertyid)
            print("extractDeedHistory finished for propertyid "+str(cur_propertyid))
            cur_property.extractBuildingPermits(cur_propertyid)
            print("extractBuildingPermits finished for propertyid "+str(cur_propertyid))
        except (ConnectionError,TimeoutError,urllib3.exceptions.NewConnectionError,
                urllib3.exceptions.MaxRetryError, requests.ConnectionError,
                requests.exceptions.ReadTimeout, urllib3.exceptions.ReadTimeoutError,
                socket.timeout) as e:
            # If there's a connection error, just put the propertyid back in the pool
            # and keep going.
            print("Propertyid " + str(cur_propertyid) + " - exception caught: "+str(e))
            propertyid_pool_lock.acquire()
            try:
                propertyid_pool.append(cur_propertyid)
            finally:
                propertyid_pool_lock.release()
            time.sleep(1)
            continue


        # Now save the RealProperty to list. The main thread will save/commit it.
        lock.acquire()
        try:
            global_property_list.append(cur_property)
        finally:
            lock.release()
        print("COMPLETED: " + str(cur_property))

########################################################################################

# Thread to scrape list of properties for each quarter section
def qs_thread(qs):
    qs_list = search_assessor.map_number_search(map_number=qs)

    propertyid_pool_lock.acquire()
    try:
        propertyid_pool.extend(qs_list)
    finally:
        propertyid_pool_lock.release()
    print("List for qs " + str(qs) + " obtained")

########################################################################################

# Process args, figure out what we want to do.
print(sys.argv)
if len(sys.argv) < 2:
    raise Exception("Command is required to proceed, and one was not entered.")
elif sys.argv[1] == 'get_quarter_sections_all':
    # Get all quarter sections, 1001-4944. (Some of these aren't used, find a way to identify them?)
    # 2 arguments or 3 if filename specified
    if len(sys.argv) < 3:
        filename = 'results.db'
    quarter_sections = [x for x in range(1001,4945)]
    action = 'qs'
elif sys.argv[1] == 'get_quarter_sections':
    # 2 arguments or 3 if filename specified
    if len(sys.argv) < 3:
        filename = 'results.db'
    qs_input = input("Please enter the quarter sections you want to search for, delimited by commas: ")
    quarter_sections = qs_input.split(",")
    action = 'qs'
elif sys.argv[1] == 'get_properties':
    # 3 arguments: Filename must be specified.
    if len(sys.argv) < 3:
        raise Exception("Filename for database must be specified to run get_properties.")
    filename = sys.argv[2]
    action = 'properties'
else:
    raise Exception("Command entered was invalid.")

########################################################################################

# Set up DB
engine = create_engine('sqlite:///'+filename)
Session = scoped_session(sessionmaker(bind=engine))
Session.configure(bind=engine)
session = Session # With a scoped_session, this is the same as Session()

real_property.Base.metadata.create_all(engine)

########################################################################################

# Find assessor PROPERTYIDs that already exist in the realproperty table
extant_propertyids = [x[0] for x in session.query(real_property.RealProperty.propertyid)]

# Get list of properties from quarter sections and add them to pool
qs_threads_list = []
for qs in quarter_sections:
    print("Obtaining list for qs " + str(qs))
    t = threading.Thread(target=qs_thread, args=(qs,))
    t.start()
    qs_threads_list.append(t)
    time.sleep(2)

while len(threading.enumerate()) > 1:
    print(qs_threads_list)
    time.sleep(10)

# Create 6 threads
threads_list = []
for i in range(1,7):
    t = threading.Thread(target=scraper_thread)
    t.start()
    threads_list.append(t)

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