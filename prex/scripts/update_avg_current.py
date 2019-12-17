from __future__ import print_function
#rcdb
from rcdb import RCDBProvider

# parity
from parity_rcdb import ParityConditions
import os
import sys
import subprocess


TESTMODE = False

def update_avg_current():

    # get run list to update
    runs=sys.argv[1]
    if "-" in runs:
        brun = runs.split("-")[0]
        erun = runs.split("-")[1]
    else:
        brun = runs
        erun = runs

    print("Update beam_current for run {}".format(runs))

    if TESTMODE:
        for runno in range(int(brun), int(erun)+1):
            print("{} {}".format(runno, find_avg_current(runno)))
    else:
        # DB Connection
        con_str = os.environ["RCDB_CONNECTION"] \
            if "RCDB_CONNECTION" in os.environ.keys() \
            else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"

        db = RCDBProvider(con_str)

        for run_number in range(int(brun), int(erun)+1):
            run = db.get_run(run_number)
            tmp = find_avg_current(run_number)
            if is_number(tmp):
              newCur = float(tmp)
            else:
              newCur = 0.0
            if not run:
                print("Run %s is not found in DB.. skip this run {}".format(run_number))
                continue
            db.add_condition(run, ParityConditions.BEAM_CURRENT, newCur, True)

def find_avg_current(run_num):
    cmds = ['/adaqfs/home/apar/PREX/prompt/rootMacros/GetTotalCharge', str(run_num)]
    cond_out = "NULL"
    cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip().decode('ascii') # Needs to be decoded... be careful
    return cond_out

def is_number(s):
  try:
    complex(s) # for int, long, float and complex
  except ValueError:
    return False
  return True


if __name__== '__main__':
    update_avg_current()
