import os, sys
from datetime import datetime

from rcdb import RCDBProvider
from rcdb.model import ConditionType, Run
from rcdb import DefaultConditions

from scripts import db_fix_helper
from scripts import epics_helper

#pvdb
from parity_rcdb import ParityConditions


TESTMODE=False

def fix_condition(run, cond_name):
    

def get_epics_condition(run):
    
    start_time_str = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")

    cmds = ["myget", "-c", epics_name, "-t", end_time_str]
    cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                    
    for line in cond_out.stdout:
        value = line.strip().split()[2]
        if "<<" in value:
            conditions[cond_name] = "-999"
        else:



def update_all():
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
    
