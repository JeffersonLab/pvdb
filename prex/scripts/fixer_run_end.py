import os, sys
from datetime import datetime

from rcdb import RCDBProvider
from rcdb.model import ConditionType, Run
from rcdb import DefaultConditions

from scripts import db_fix_helper

TESTMODE=True

def update_run(run_number):
    # DB Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"

    db = RCDBProvider(con_str)

    run = db.get_run(run_number)
    if not run:
        print ("Run %s is not found in DB" % run_number)
        sys.exit(1)

    conditions = {}
    conditions = db_fix_helper.get_run_end_info_from_data(run_number)

    #Replace with the start from the data file.. there are some cases where we have total time < 0
    #because the run was too short... there is 30sec delay in start script 
    #delay was introduced to give enough time to the end run log before a new run log appears
    #run_length = (datetime.strptime(conditions["run_end_time"], "%Y-%m-%d %H:%M:%S") - run.start_time).total_seconds()
    run_length = (datetime.strptime(conditions["run_end_time"], "%Y-%m-%d %H:%M:%S") - 
                  datetime.strptime(conditions["run_start_time"], "%Y-%m-%d %H:%M:%S")).total_seconds()

    event_rate = None
    if float(run_length) > 0 and conditions["event_count"] is not None:
        event_rate = float(conditions["event_count"]) / float(run_length)
    else:
        if not float(run_length) > 0:
            print ("ERROR: run_length < 0....skip the update")
            print "Reported start time:", conditions["run_start_time"]
            print "Reported end time:", conditions["run_end_time"]
            print
        if conditions["event_count"] is None:
            print ("ERROR: event_count not available")

    if TESTMODE:
        print ("Run start time:\t %s" % conditions["run_start_time"])
        print ("Run end time:\t %s" % conditions["run_end_time"])
        print ("Total Events:\t %s" % conditions["event_count"])
        print ("Run length  :\t %s" % run_length)
        print ("Event rate  :\t %s" % event_rate)
    else:
        run.start_time = conditions["run_start_time"]
        run.end_time = conditions["run_end_time"]
        db.add_condition(run, DefaultConditions.RUN_LENGTH, run_length, True)
        db.add_condition(run, DefaultConditions.IS_VALID_RUN_END, conditions["has_run_end"], True)

        if conditions["event_count"] is not None:
            db.add_condition(run, DefaultConditions.EVENT_COUNT, conditions["event_count"], True)
        if event_rate is not None:
            db.add_condition(run, DefaultConditions.EVENT_RATE, event_rate, True)
        db.session.commit()

#def update_runs(runs):
# update runs

if __name__=='__main__':
    update_run(sys.argv[1])
