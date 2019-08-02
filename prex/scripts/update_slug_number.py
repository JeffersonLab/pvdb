import os
import sys

#rcdb
from rcdb import RCDBProvider

# parity
from parity_rcdb import ParityConditions
from parity_rcdb.parity_coda_parser import GetSlugNumber

TESTMODE = False

def update_slug():

    # get run list to update
    runs=sys.argv[1]
    if "-" in runs:
        brun = runs.split("-")[0]
        erun = runs.split("-")[1]
    else:
        brun = runs
        erun = runs

    #slug number
    slug=sys.argv[2]

    print "Update SLUGNUMBER for run ", runs

    if TESTMODE:
        for runno in range(int(brun), int(erun)+1):
            print runno, find_slug_number(runno)
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
#            slug = find_slug_number(run_number)
            db.add_condition(run, ParityConditions.SLUG, slug, True)

def find_slug_number(run_num):
    slug_num =  None

    slug_bank = [1, 2, 3, 4, 5, 6, 7, 8]
    first_run = [3305, 3346, 3398, 3404, 3424, 3434, 3444, 3453, 9999]

    if int(run_num) < first_run[0]:
        slug_num = 0
    else:
        for x in range(0, 8):
            if int(run_num) >= first_run[x] and int(run_num) < first_run[x+1]:
                slug_num = slug_bank[x]
                
    return slug_num

if __name__== '__main__':
    update_slug()
