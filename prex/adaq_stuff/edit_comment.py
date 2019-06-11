import os
import sys
import traceback

# rcdb
import rcdb
from rcdb.provider import RCDBProvider

# parity
from parity_rcdb import ParityConditions

def edit_comment(run_number, comment, replace):

    # DB Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://apcoda@cdaqdb1.jlab.org:3306/pvdb"

    db = rcdb.RCDBProvider(con_str)

    # Check if the run exists in the DB
    run = db.get_run(run_number)
    if not db.get_run(run_number):
        print
        print ("ERROR: Run %s is not found in DB" % run_number)
        print ("Check Run DB page!")
        print ("For help: contact sanghwa@jlab.org")
        print
        sys.exit(1)

    if "yes" in replace:
        # add the condition value to the DB
        db.add_condition(run, ParityConditions.SL_COMMENT, comment, replace=True)
    elif "no" in replace:
        # Get the initial comment
        try:
            initial_comment = db.get_condition(run, "sl_comment").value
        except Exception as e:
            print "Problem reading the initial comment"
            print e
            sys.exit(1)
        new_comment = initial_comment + ", " + comment
        db.add_condition(run, ParityConditions.SL_COMMENT, new_comment, replace=True)
    else:
        print "Invalid flag: ", replace

if __name__== '__main__':
    run_num=sys.argv[1].strip()
    comment=sys.argv[2].strip()
    replace_flag=sys.argv[3].strip()
#    print run_num, comment, replace_flag

    if not run_num.isdigit():
        print "Invalid run number: ", run_num
        sys.exit(1)
    if comment == "":
        print "Empty comment... abort"
        sys.exit(1)
    if replace_flag != "yes" and replace_flag != "no":
        print "Invalid replace flag:", replace_flag
        sys.exit(1)

#    print "you reached here"
    edit_comment(run_num, comment, replace_flag)
