import os
import sys
<<<<<<< HEAD
import subprocess
from datetime import datetime
=======
>>>>>>> b32afcfced2786729e3c978758c0902cece8ecdd

import rcdb
from rcdb.provider import RCDBProvider

<<<<<<< HEAD
LHRS_ref = {
    "LQ1":118.50,
    "LQ2":407.70,
    "LQ3":450.76,
    "LD1":0.352789,
}
RHRS_ref = {
    "RQ1":118.55,
    "RQ2":404.07,
    "RQ3":446.90,
    "RD1":0.353584
}

threshold = 0.01

def get_HRS_info(brun, erun):
    dd = {}

#    query_str = "(run_type != 'Junk' and run_type != 'Test' and run_type != 'Cosmics') and '208Pb' in target_type"
    query_str = "run_type == 'Production' and '208Pb' in target_type"
=======
def get_HRS_info(brun, erun):
    dd = {}

    query_str = "(run_type != 'Junk' and run_type != 'Test') and '208Pb' in target_type"
>>>>>>> b32afcfced2786729e3c978758c0902cece8ecdd
    con_str = "mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"
    db = rcdb.RCDBProvider(con_str)
    result = db.select_runs(query_str, brun, erun)

    for run in result:
        run_num = str(run.number)
<<<<<<< HEAD
        start_time = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")

        dd[run_num] = {}

        check_start = get_halog_data(run_num, dd, "start")
        if check_start > 0:
            dd[run_num]['start'] = {}
            get_epics_data(start_time, 'start', run_num, dd)

        check_end = get_halog_data(run_num, dd, "end")
        if check_end > 0:
            dd[run_num]['end'] = {}
            get_epics_data(end_time, 'end', run_num, dd)

    list_sngL = []
    list_sngR = []
    list_twoarm = []
    check_stability(dd, list_sngL, list_sngR, list_twoarm)

    print
    print "====================================="
    print "LEFT ONLY"
    for x in list_sngL:
        print x

    print
    print "====================================="
    print "RIGHT ONLY"
    for x in list_sngR:
        print x

def is_number(s):
  try:
    float(s) # for int, long, float and complex
  except ValueError:
    return False
  return True

def check_stability(dd, list_sngL, list_sngR, list_twoarm):
    for key in dd:
        LHRS_OK = True
        for hrs_name, ref in LHRS_ref.iteritems():

            if not is_number(dd[key]['start'][hrs_name]):
                print "channel value invalid: ", key, 'start', hrs_name, dd[key]['start'][hrs_name]
                continue
            if not is_number(dd[key]['end'][hrs_name]):
                print "channel value invalid: ", key, 'end', hrs_name, dd[key]['end'][hrs_name]
                continue

            if 'start' in dd[key]:
                diff_start = abs(float(dd[key]['start'][hrs_name]) - float(ref))/float(ref)
                if diff_start > threshold:
                    print key, hrs_name, "start", dd[key]['start'][hrs_name], ref, diff_start
                    LHRS_OK = False
            if 'end' in dd[key]:
                diff_end = abs(float(dd[key]['end'][hrs_name]) - float(ref))/float(ref)
                if diff_end > threshold:
                    print key, hrs_name, "end", dd[key]['end'][hrs_name], ref, diff_end
                    LHRS_OK = False

        RHRS_OK = True
        for hrs_name, ref in RHRS_ref.iteritems():
            if 'start' in dd[key]:
                diff_start = abs(float(dd[key]['start'][hrs_name]) - float(ref))/float(ref)
                if diff_start > threshold:
                    print key, hrs_name, "start", dd[key]['start'][hrs_name], ref, diff_start
                    RHRS_OK = False
            if 'end' in dd[key]:
                diff_end = abs(float(dd[key]['end'][hrs_name]) - float(ref))/float(ref)
                if diff_end > threshold:
                    print key, hrs_name, "end", dd[key]['end'][hrs_name], ref, diff_end
                    RHRS_OK = False

        if LHRS_OK and RHRS_OK:
            list_twoarm.append(key)
        elif not LHRS_OK and not RHRS_OK:
            print "both arm has problem", key
        elif LHRS_OK and not RHRS_OK:
            list_sngL.append(key)
        elif RHRS_OK and not LHRS_OK:
            list_sngR.append(key)

def get_halog_data(run_num, dd, this_time):
=======
        print run_num

        dd[run_num] = {}
        get_halog_data(run_num, dd, "start")
        get_halog_data(run_num, dd, "end")

    print dd


def get_halog_data(run_num, dd, this_time):
    dd[run_num][this_time] = {}

>>>>>>> b32afcfced2786729e3c978758c0902cece8ecdd
    if this_time == 'start':
        epics_file = "/adaqfs/home/apar/epics/runfiles/halog_start_" + run_num + ".epics"
    elif this_time == 'end':
        epics_file = "/adaqfs/home/apar/epics/runfiles/halog_end_" + run_num + ".epics"
    else:
        print "wrong input, should be start or end"
        sys.exit(1)

    if not os.path.exists(epics_file):
<<<<<<< HEAD
        #print this_time, "epics file does not exit for ", run_num
        return 1

    if run_num not in dd:
        dd[run_num] = {}

    dd[run_num][this_time] = {}

    """
    search_list = {
        "Left Arm Q1 power supply current":"LQ1",
        "Left Arm Q2 power supply current":"LQ2",
        "Left Arm D1 NMR":"LD1",
        "Left Arm Q3 power supply current":"LQ3",
        "Right Arm Q1 power supply current":"RQ1",
        "Right Arm Q2 power supply current":"RQ2",
        "Right Arm D1 NMR":"RD1",
        "Right Arm Q3 power supply current":"RQ3"
    }
    """

    with open(epics_file, 'rb') as f:
=======
        print "epics file does not exit for ", run_num
        return

    with open(start_file, 'rb') as f:
>>>>>>> b32afcfced2786729e3c978758c0902cece8ecdd
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
<<<<<<< HEAD
    return 0

def get_epics_data(time_str, this_time, run_num, dd):

    epics_list = {
        "MQ171LM":"LQ1",
        "HacL_Q2_HP3458A:IOUT":"LQ2",
        "HacL_Q3_HP3458A:IOUT":"LQ3",
        "HacL_D1_NMR:SIG":"LD1",
        "MQ172RM":"RQ1",
        "HacR_Q2_HP3458A:IOUT":"RQ2",
        "HacR_Q3_HP3458A:IOUT":"RQ3",
        "HacR_D1_NMR:SIG":"RD1"
    }

    for epics_name, cond_name in epics_list.iteritems():
        try:
            cmds = ["myget", "-c", epics_name, "-t", time_str]
            cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)
            for line in cond_out.stdout:
                value = line.strip().split()[2]
                if "Invalid" in value:
                    dd[run_num][this_time][cond_name] = -999
                else:
                    dd[run_num][this_time][cond_name] = value
                #print cond_name, value
        except Exception as e:
            print e

=======
>>>>>>> b32afcfced2786729e3c978758c0902cece8ecdd

if __name__ == '__main__':
    brun = sys.argv[1]
    erun = sys.argv[2]
    get_HRS_info(brun, erun)
