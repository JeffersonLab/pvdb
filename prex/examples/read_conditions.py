import os
import sys

import rcdb
from rcdb.provider import RCDBProvider

# ref: see ~/pvdb/rcdb/python/rcdb/provider.py for functions that are defined already

def read_conditions(run_number):
    # DB Connection
    con_str = os.environ["RCDB_CONNECTION"] \
              if "RCDB_CONNECTION" in os.environ.keys() \
                 else "mysql://apcoda@cdaqdb1.jlab.org:3306/pvdb"

    db = rcdb.RCDBProvider(con_str)

    # returns Run object (None if the run doesn't exsist in DB)
    run = db.get_run(run_number)
    if not run:
        print ("ERROR: Run %s is not found in DB" % run_number)
        sys.exit(1)        

    """
    get condition value
    example: run_length
    returns condition_name and value
    """
    value = db.get_condition(run, "ihwp").value
    print value
#    print "run_length", value

if __name__== '__main__':
    read_conditions(sys.argv[1])
