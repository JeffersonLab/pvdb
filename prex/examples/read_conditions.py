import os
import sys

import rcdb
from rcdb.provider import RCDBProvider

# ref: see ~/pvdb/rcdb/python/rcdb/provider.py for functions that are defined already

def read_conditions(run_number):
    # DB Connection (read-only)
    con_str="mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"

    db = rcdb.RCDBProvider(con_str)

    # returns Run object (None if the run doesn't exsist in DB)
    run = db.get_run(run_number)
    if not run:
        print ("ERROR: Run %s is not found in DB" % run_number)
        sys.exit(1)        

    #start time and end time
    start_time = run.start_time
    end_time = run.end_time

    """
    get condition value
    example: run_length
    returns condition_name and value
    """
    value = db.get_condition(run, "ihwp").value
    print value

    # to get multiple conditions at once
    # one can for example use get_conditions_by_name(self)
    # which returns dictionary witwh condition name as a ke

if __name__== '__main__':
    read_conditions(sys.argv[1])
