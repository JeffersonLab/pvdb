import subprocess
import os, sys
from datetime import datetime
import time
import traceback
import math

import rcdb
from rcdb.provider import RCDBProvider

def get_dpp_run(run_num):
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"

    db = rcdb.RCDBProvider(con_str)
    run = db.get_run(run_num)
    if not db.get_run(run_num):
        print "run not found in DB: ", run_num
        return

    brtime = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
    if run.end_time is not None:
        ertime = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")
    else:
        # use fixer.. abort the program for now
        return

    dpp, sig_dpp = get_dpp(brtime, ertime)
    """
    print "Start: ", brtime
    print "End: ", ertime
    print "get_dpp_run: ", dpp, sig_dpp
    """
    return dpp, sig_dpp

def get_p(brtime, ertime):
    mean = None
    stdev = None

    try:
        # Adjust condition range as needed from "-r", "min:max" ..
        cmds = ["myStats", "-b", brtime, "-e", ertime, "-c", "HALLA:p", "-r", "1000:3000", "-l", "HALLA:p"]
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                            
        for line in cond_out.stdout:
            if "HALLA:p" in line:
                value1 = line.strip().split()[2]
                value2 = line.strip().split()[4]
                if value1 == "N/A":
                    mean = 0
                else:
                    mean = value1
                if value2 == "N/A":
                    stdev = 0
                else:
                    stdev = value2                    
    except Exception as e:
        print >> sys.stderr, "Exception: %s" % str(e)
    return mean, stdev

def get_dpp(brtime, ertime):
    mean = None
    stdev = None

    try:
        # Adjust condition range (beam current) as needed from "-r", "min:max" ..
        cmds = ["myStats", "-b", brtime, "-e", ertime, "-c", "IBC1H04CRCUR2", "-r", "0.2:200", "-l", "HALLA:dpp"]
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                            
        for line in cond_out.stdout:
            if "HALLA:dpp" in line:
                value1 = line.strip().split()[2]
                value2 = line.strip().split()[4]
                if value1 == "N/A":
                    mean = 0
                else:
                    mean = value1
                if value2 == "N/A":
                    stdev = 0
                else:
                    stdev = value2                    
    except Exception as e:
        print >> sys.stderr, "Exception: %s" % str(e)

    return mean, stdev

def get_dpp2(brtime, ertime):
    mean = None
    stdev = None

    ldpp = []
    try:
        cmds = ["myData", "-b", brtime, "-e", ertime, "HALLA:dpp", "-f", 'a != 0']
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                    
        for line in cond_out.stdout:
            # skip the first line
            if "Date" in line:
                continue
            value = line.strip().split()[2]
            if value is not None:
                ldpp.append(float(value))
    except Exception as e:
        print >> sys.stderr, "Exception: %s" % str(e)
        sys.exit(1)

    mean = sum(ldpp)/float(len(ldpp))
    stdev = get_stdev(ldpp, mean)
    return mean, stdev

def get_stdev(ldpp, dpmean):
    sqsum = 0
    for i in ldpp:
        sqsum = sqsum + (float(dpmean)- float(i))*(float(dpmean) - float(i))
    ndpp = len(ldpp)
    return math.sqrt(sqsum/float(ndpp))
    
if __name__== "__main__":
    get_dpp_run(sys.argv[1])
