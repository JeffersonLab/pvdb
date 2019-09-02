import os
import sys

#rcdb
from rcdb import RCDBProvider

# parity
from parity_rcdb import ParityConditions

TESTMODE = False

def update_arm_flag():

    # get run list to update
    runs=sys.argv[1]
    if "-" in runs:
        brun = runs.split("-")[0]
        erun = runs.split("-")[1]
    else:
        brun = runs
        erun = runs

    #arm_flag number
    arm_flag=sys.argv[2]
    print "Update ARM_FLAG for run ", runs

    if TESTMODE:
        print "Would change arm flag to be ",arm_flag ," for runs ", brun,"-", erun
        for runno in range(int(brun), int(erun)+1):
            print runno, arm_flag 
    else:
        # DB Connection
        con_str = os.environ["RCDB_CONNECTION"] \
            if "RCDB_CONNECTION" in os.environ.keys() \
            else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"

        db = RCDBProvider(con_str)

        for run_number in range(int(brun), int(erun)+1):
            run = db.get_run(run_number)
            if not run:
                print ("Run %s is not found in DB.. skip this run" % run_number)
                continue
#            arm_flag = find_arm_flag_number(run_number)
            db.add_condition(run, ParityConditions.ARM_FLAG, arm_flag, True)


if __name__== '__main__':
    update_arm_flag()
