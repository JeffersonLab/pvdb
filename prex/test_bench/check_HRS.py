import os
import sys

import rcdb
from rcdb.provider import RCDBProvider

def get_HRS_info(brun, erun):
    dd = {}

    query_str = "(run_type != 'Junk' and run_type != 'Test') and '208Pb' in target_type"
    con_str = "mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"
    db = rcdb.RCDBProvider(con_str)
    result = db.select_runs(query_str, brun, erun)

    for run in result:
        run_num = str(run.number)
        print run_num

        dd[run_num] = {}
        get_halog_data(run_num, dd, "start")
        get_halog_data(run_num, dd, "end")

    print dd


def get_halog_data(run_num, dd, this_time):
    dd[run_num][this_time] = {}

    if this_time == 'start':
        epics_file = "/adaqfs/home/apar/epics/runfiles/halog_start_" + run_num + ".epics"
    elif this_time == 'end':
        epics_file = "/adaqfs/home/apar/epics/runfiles/halog_end_" + run_num + ".epics"
    else:
        print "wrong input, should be start or end"
        sys.exit(1)

    if not os.path.exists(epics_file):
        print "epics file does not exit for ", run_num
        return

    with open(start_file, 'rb') as f:
        for line in f:
            if "Left Arm Q1 power supply current" in line:
                dd[run_num][this_time]['LQ1'] = line.split(":")[1].strip()
            if "Left Arm Q2 power supply current" in line:
                dd[run_num][this_time]['LQ2'] = line.split(":")[1].strip()
            if "Left Arm D1 NMR" in line:
                dd[run_num][this_time]['LD1'] = line.split(":")[1].strip()
            if "Left Arm Q3 power supply current" in line:
                dd[run_num][this_time]['LQ3'] = line.split(":")[1].strip()
            if "Right Arm Q1 power supply current" in line:
                dd[run_num][this_time]['RQ1'] = line.split(":")[1].strip()
            if "Right Arm Q2 power supply current" in line:
                dd[run_num][this_time]['RQ2'] = line.split(":")[1].strip()
            if "Right Arm D1 NMR" in line:
                dd[run_num][this_time]['RD1'] = line.split(":")[1].strip()
            if "Right Arm Q3 power supply current" in line:
                dd[run_num][this_time]['RQ3'] = line.split(":")[1].strip()

if __name__ == '__main__':
    brun = sys.argv[1]
    erun = sys.argv[2]
    get_HRS_info(brun, erun)
