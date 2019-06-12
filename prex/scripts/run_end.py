import logging
import argparse
import os
import sys
from datetime import datetime
import time
import traceback
import glob

#parity
from parity_rcdb import ParityConditions
from parity_rcdb import parity_coda_parser
import epics_helper

#rcdb
import rcdb
from rcdb import DefaultConditions
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType, Condition
from rcdb.log_format import BraceMessage as Lf

log = logging.getLogger('pvdb')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

# Test flag, print out parse result but no update to the DB
test_mode = False

def parse_end_run_info(run_number):

    # for the record
    script_start_clock = time.clock()
    script_start_time = time.time()

    # Run end time
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # DB Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"

    db = rcdb.RCDBProvider(con_str)

    # Set data_path
    if "QW_DATA" in os.environ:
        data_path = os.environ["QW_DATA"]
    else:
        print ("QW_DATA is not set, force to /adaq1/data1/apar")
        data_path = "/adaq1/data1/apar"
        
    # when data path was set to /adaq2/data1/apar
    if int(run_number) < 2143:
        data_path = "/adaq2/data1/apar"

    # dat file counts
    num_files = len([files for files in glob.glob(data_path+"/*"+run_number+".dat*")])

    run = db.get_run(run_number)
    if not db.get_run(run_number):
        log.info(Lf("run_end: Run '{}' is not found in DB."
                    "Considering there was no GO, only prestart and then Stop ", run_number))
        # FIXME: add to error list
        return

    run.end_time = end_time_str

    nevts = parity_coda_parser.GetTotalEvents()

    # FIXME: total number of events? (maybe add at the end of prompt analysis)

    # epics info: consistency check and update
    epics_conditions = {}
    epics_conditions = epics_helper.get_end_run_conds(run)

    # total run length
    total_run_time = datetime.strptime(run.end_time, "%Y-%m-%d %H:%M:%S") - run.start_time

    # rough estimation of total charge = run length * average beam current
    charge = float(total_run_time.total_seconds()) * float(epics_conditions["beam_current"])
    epics_conditions["total_charge"] = charge

    if nevts is None:
        nevts = -1
        event_rate = -1
    else:
        event_rate = float(nevts) / float(total_run_time.total_seconds())

    if test_mode:
        print("Run Start time:\t %s" % run.start_time)
        print("Run End time:\t %s" % run.end_time)
        print("Run length:\t %d" % (int(total_run_time.total_seconds())))
        print("Total event counts %d" % (int(nevts)))
        print("Event Rate %.2f" % (float(event_rate)))
        print("Avg.Beam Current:\t %.2f" % (float(epics_conditions["beam_current"])))
        print("Total charge:\t %.2f" % charge)
        print("Beam energy:\t %.2f" % (float(epics_conditions["beam_energy"])))
        print("Target type:\t %s" % (epics_conditions["target_type"]))
        print("Helicity pattern:\t %s" % (epics_conditions["helicity_pattern"]))
        print("Helicity frequency:\t %s Hz" % (epics_conditions["helicity_frequency"]))
        print("IHWP:\t %s" % (epics_conditions["ihwp"]))
        print("Wien angle (H,V):\t %s, %s" % (epics_conditions["horizontal_wien"], epics_conditions["vertical_wien"]))
    else:
        # Add conditions to DB
        conditions = []
        conditions.append((DefaultConditions.IS_VALID_RUN_END, True))
        conditions.append((DefaultConditions.RUN_LENGTH, total_run_time.total_seconds()))
        conditions.append((ParityConditions.BEAM_CURRENT, epics_conditions["beam_current"]))
        conditions.append((ParityConditions.TOTAL_CHARGE, epics_conditions["total_charge"]))
        conditions.append((DefaultConditions.EVENT_COUNT, nevts))
        conditions.append((DefaultConditions.EVENT_RATE, event_rate))

        # Disabled (conditions not added to DB)
        # conditions.append(('evio_last_file', files))
        # conditions.append(('evio_file_count', num_files))

        # Save conditions
        db.add_conditions(run, conditions, replace=True)
        db.session.commit()

        now_clock = time.clock()
        db.add_log_record("", 
                          "End of udpate. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                          .format(now_clock - script_start_clock,
                                  time.time() - script_start_time,
                                  datetime.now()), run_number)

if __name__== '__main__':
    parser = argparse.ArgumentParser(description= "Update the PVDB at the end of a run")
    parser.add_argument("--run", type=str, help="Run number", default="")

    args = parser.parse_args()
    run_number = args.run

    if run_number != "":
        parse_end_run_info(run_number)
    else:
        print "Invalid run number: ", run_number
        print "Example: python run_end.py --run=1234"
