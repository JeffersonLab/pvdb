import sys
from datetime import datetime

from rcdb import RCDBProvider
from rcdb.model import ConditionType, Run
from rcdb import DefaultConditions

from scripts import get_run_end_info_from_data
from scripts import get_total_events_from_runfile

def update_run(run_number):
    # DB Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"

    db = rcdb.RCDBProvider(con_str)

    run = db.get_run(run_number)
    if not run:
        print ("Run %s is not found in DB" % run_number)
        sys.exit(1)

    conditions = []
    conditions = get_run_end_info_from_file(run_number)

    total_run_time = datetime.strptime(conditions["end_time"], "%Y-%m-%d %H:%M:%S") - run.start_time

    event_rate = -1

    db.add_condition(run, DefaultConditions.RUN_END_TIME, conditions["end_time"])
    db.add_condition(run, DefaultConditions.EVENT_COUNT, conditions["end_time"])

        
def update_runs(runs):
    # update runs

if __name__=='__main__':
    update_run(sys.argv[1])


