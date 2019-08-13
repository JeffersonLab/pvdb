import sys
import subprocess
from datetime import datetime

import rcdb
from rcdb.provider import RCDBProvider

TESTMODE=True

def main():
    
    first_run = sys.argv[1]
    last_run = sys.argv[2]

    # DB Connection                                                           
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"
    #con_str = "mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"
    db = rcdb.RCDBProvider(con_str)

    result = db.select_runs("run_type != 'Junk'", first_run, last_run)
    for run in result:
        start_time = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
        try:
            cmds = ["myget", "-c", "FlipState", "-t", start_time]
            cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()
            value = cond_out.split()[2]
            if int(value) == 2:
                flip = 'RIGHT'
            elif int(value) == 3:
                flip = 'LEFT'
            else:
                print "flip state value sometime else....", value, " skip this run", run.number
                continue

            if TESTMODE:
                print run.number, value
            else:
                db.add_condition(run, ParityConditions.FLIPSTATE, flip, True)
        except Exception as e:
            print e

if __name__=='__main__':
    main()
