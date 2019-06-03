import logging
import os
import sys
from datetime import datetime

#parity
from parity_rcdb import ParityConditions
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
test_mode = True

def parse_end_run_info(run_number):

    # for the record
    script_start_clock = time.clock()
    script_start_time = time.time()

    # Run end time
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # DB Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://pvdb@localhost/pvdb"

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
                    "Considering there was no GO, only prestart and then Stop ", parse_result.run_number))
        # FIXME: add to error list
        return

    run.end_time = end_time_str

    # FIXME: total number of events? (maybe add at the end of prompt analysis)

    # epics info: consistency check and update
    epics_conditions = {}
    epics_conditions = epics_helper.get_end_run_conds(run)

    # total run length
    total_run_time = datetime.strptime(run.end_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(run.start_time, "%Y-%m-%d %H:%M:%S")
    # charge = run length * average beam current
    charge = float(total_run_time.seconds) * float(epics_conditions["beam_current"])

    if test_flag:
        print("Avg. Beam Current:\t %.2f" % (float(epics_conditions["beam_current"])))
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
        conditions.append((DefaultConditions.RUN_LENGTH, total_run_time.seconds))
        conditions.append((ParityConditions.BEAM_CURRENT, epics_conditions["beam_current"]))
        conditions.append((ParityConditions.TOTAL_CHARGE, epics_conditions["total_charge"]))
        #    conditions.append(('evio_last_file', files))
        #    conditions.append(('evio_file_count', num_files))

        # Save conditions
        db.add_conditions(run, conditions, replace=True)
        db.session.commit()

        db.add_log_record("", 
                          "End of udpate. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                          .format(now_clock - script_start_clock,
                                  time.time() - script_start_time,
                                  datetime.now()), run_number)

if __name__== '__main__':
    parser = argparse.ArgumentParser(description= "Update PVDB")
    parser.add_argument("--run", type=str, help="Run number", default="")
    args = parser.parse_args()
    run_number = args.run

    parse_end_run_info(run_number):    
