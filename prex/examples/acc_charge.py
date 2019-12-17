import os
import sys
import time
import datetime
import argparse

import rcdb
from rcdb.provider import RCDBProvider
from rcdb.model import Run
from sqlalchemy import desc

fDEBUG = True

def get_summary_output(run_number):

    #summary_file = "/adaqfs/home/apar/PREX/prompt/japanOutput/summary_" + run_number + ".txt"
    summary_file = "/adaqfs/home/apar/PREX/prompt/SummaryText/summary_" + run_number + "_000.txt"
    summary = []

    if not os.path.exists(summary_file):
        return summary
        
    n = 0
    with open(summary_file, 'rb') as f:
        lines = filter(None, (line.strip() for line in f))
        for line in lines:
            if n > 0:
                break
            if "Start Time:" in line:
                value = line.split('Time:')[1]
                summary.append(value)
            if "End Time:" in line:
                value = line.split('Time:')[1]
                summary.append(value)
            if "Number of events processed" in line:
                value = line.split(':')[1]
                summary.append(value)
            if "Percentage of good events" in line:
                value = line.split(None)[4]
                summary.append(value)
            # Cameron: changed behavior of charge getter to select the correct BCM on 7/30/2019 (Kent changed it before)
            if run_number<str(3583):
              if "bcm_an_ds" in line:
                value = line.split("Mean:")[1].split(None)[0]
                summary.append(value)
                n += 1
            elif run_number>=str(3583) and run_number<str(5000):
              if "cav4cQ" in line:
                value = line.split("Mean:")[1].split(None)[0]
                summary.append(value)
                n += 1
            elif run_number>str(5000):
              if "bcm_an_us" in line:
                value = line.split("Mean:")[1].split(None)[0]
                summary.append(value)
                n += 1

    return summary

def get_usage():
    return """
    Get accumulated charge

    Returns text output file
    :run#, start_time, charge_all, good_charge
    :charge_all: for all events, using the average current from epics and run length
    :good_charge: for events in good multiplicity patterns

    How to use
    1) specific run range
    > python acc_charge.py --run=3000-3100

    2) run list (input list file required)
    > python acc_charge.py --list=list.txt

    Set tight selection criteria:
    Select runs marked as Good (run_flag == 'Good')
    > python acc_charge.py --run=3000-3100 --goodrun
    """

def get_info_all():

    use_list = False

    # argv
    parser = argparse.ArgumentParser(description="", usage=get_usage())
    parser.add_argument("--run", type=str, help="run range")
    parser.add_argument("--list", type=str, help="use run list file")
    # However this script is to be used by shift crew to get idea about the time to change IHWP status
    # the default status needs to be False. WAC can copy the script to his/her personal folder and change the default
    parser.add_argument("--goodrun", type=bool, help="select only runs marked as Good", default=False)
    args = parser.parse_args()

    # run list
    runs = []

    if args.run is not None:
        run_range = args.run
        brun = run_range.split("-")[0]
        erun = run_range.split("-")[1]
        for x in range(int(brun), int(erun)+1):
            runs.append(x)

    if args.list is not None:
        use_list = True

    # override run range
    if use_list:
        del runs[:]
        with open(args.list, 'rb') as f:
            lines = filter(None, (line.rstrip() for line in f))
            for line in lines:
                runs.append(line)

    # DB connection
    con_str = "mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"
    db = rcdb.RCDBProvider(con_str)

    if args.run is None and args.list is None:
        # no given run range/list 
        run_query = db.session.query(Run)
        last_run = run_query.order_by(desc(Run.number)).first().number
        runs = [x for x in range(5300, int(last_run)+1)]
        print "For all production runs ", runs[0], runs[-1]

    # search query
    """
    count_str = "event_count > 10000"
    type_str = "run_type in ['Production']"
    target_str = "'208Pb' in target_type"
    flag_str = "run_flag != 'Bad'"
    query_str =  type_str + " and " + target_str + " and " + flag_str
    """

    # dictionary to fill
    dd = {}

    # Output file
    fout = open('out.txt', 'wb')

    nrun = 0
    ngood = 0
    good_sum = 0
    charge_sum = 0

    # Get result
    result = db.select_runs("", runs[0], runs[-1])
    for run in result:

        runno = str(run.number)
        helFlipRate = 120.0
        # PREX2
        if run.number >= 3876 and run.number < 5000:
          helFlipRate = 240.0
        dd[runno] = {}

        # from db 
        run_type = run.get_condition_value("run_type")
        target_type = run.get_condition_value("target_type")
        run_flag = run.get_condition_value("run_flag")
        arm_flag = run.get_condition_value("arm_flag")

        pass_cut = True

        if run_type is None or run_type not in ['Production']:
            pass_cut = False
        if target_type is None or '48Ca' not in target_type:
            pass_cut = False

        good_run_flag = False
        # Tight cut
        if run_flag is not None and run_flag != 'Bad':
            good_run_flag = True

        if args.goodrun:
            if not good_run_flag:
                pass_cut = False

        # conservative selection:
        #if run_flag is not None and run_flag == 'Bad':
        #    good_run_flag = False        
        #if (run_flag != 'Bad' and run_flag != 'Suspicious'):
        #    pass_cut = False            
        
        charge1 = "0"
        charge2 = "0"

        if pass_cut:
            avg_cur = run.get_condition_value("beam_current")
            length = run.get_condition_value("run_length")
            ihwp = run.get_condition_value("ihwp")
            rhwp = run.get_condition_value("rhwp")

            # read prompt summary 
            """
            0: start time
            1: end time
            2: number of events processed
            3: fraction of good events/all
            4: bcm mean
            """
            summary_output = get_summary_output(str(run.number))
        
            # if prompt analysis output exists or not
            if not summary_output:
                # skip the run if there is no prompt summary
                print "=== Prompt summary output does not exist for run: ", runno, ", skip this run for Good charge"
                charge2 = "0"
                prompt_time = "0"
                start_time = run.start_time
            else:
                start_time = summary_output[0]
                if length is None:
                    # use prompt Nevent instead
                    length = float(summary_output[2]) * 1.0/helFlipRate
                # good charge from prompt output
                if 'nan' in summary_output[3]:
                    print "=== No good event processed for run :", runno, " , skip this run"
                    prompt_time = "0"
                    charge2 = "0"
                else:
                    prompt_time = float(summary_output[2]) * float(summary_output[3])*0.01 * 1.0/helFlipRate
                    if run.number >= 3876 and run.number < 5000:
                        charge2 = float(prompt_time) * float(summary_output[4]) * 2
                    else:
                        charge2 = float(prompt_time) * float(summary_output[4])
                    
            if length is None:
                print"=== Run did not end properly...", runno, ", let's skip this"
            else:
                # calculate charge all (from epics)
                charge1 = float(avg_cur) * float(length)

            # If one uses a list, we don't do QA from DB:
            if use_list:
                if runno not in runs:
                    charge1 = "0"
                    charge2 = "0"

            # fill dict
            dd[runno]["avg_cur"] = avg_cur
            dd[runno]["length"] = length
            dd[runno]["charge_all"] = charge1
            dd[runno]["charge_good"] = charge2
            dd[runno]["eff_time"] = prompt_time
            dd[runno]["start_time"] = start_time
        else:
            #print runno, run_type, target_type, run_flag
            dd[runno]["charge_all"] = "0"
            dd[runno]["charge_good"] = "0"
            dd[runno]["start_time"] = run.start_time

        # Sum over all production runs (with 208Pb target)
        charge_sum += float(charge1)
        nrun += 1

        if fDEBUG:
            print runno, charge_sum, float(charge1)*1.e-6

        # Count good runs
        if dd[runno]["charge_all"] != "0":
            ngood += 1
            good_sum += float(dd[runno]["charge_good"])

        print >> fout, runno, dd[runno]["start_time"], dd[runno]["charge_all"], dd[runno]["charge_good"]

    print
    print ("Total runs: %d,\t\tTotal charge sum: %.2f C" %(nrun, float(charge_sum)*1.e-6))
    print ("Total good runs: %d,\tGood charge sum: %.2f C" %(ngood, float(good_sum)*1.e-6))
    
if __name__ == "__main__":
    get_info_all()
