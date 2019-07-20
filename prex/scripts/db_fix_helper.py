import os
import glob
import sys
import xml.etree.ElementTree as Et
from subprocess import check_output
from datetime import datetime

def get_run_end_info_from_data(run_number):
    """
    get run end time, total events
    from coda file directly
    mostly to be used for the post update
    when prompt analysis output is not available
    :returns condition array with names ("end_time", "total_events")
    """
    conditions = {}

    if "QW_DATA" in os.environ:
        data_path = os.environ["QW_DATA"]
    else:
        print ("QW_DATA is not set, force to /adaq1/data1/apar")
        data_path = "/adaq1/data1/apar"

    num_files = len([files for files in glob.glob(data_path+"/*"+run_number+".dat*")])
    if num_files < 1:
        print "no file found for ", run_number
        sys.exit(1)

    # last file
    index_last = num_files-1
    coda_file = files.split('.')[0]+".dat."+str(index_last)

    # Start time (to fix the case when run was too short)
    conditions["run_start_time"] = None
    coda_file0 = files.split('.')[0]+".dat.0"
    start_time = get_start_time_from_data(coda_file0)
    conditions["run_start_time"] = start_time

    cmds = ["evio2xml", "-ev", "20", "-xtod", "-max", "1", coda_file]
    out = check_output(cmds)
    xml_root = Et.ElementTree(Et.fromstring(out)).getroot()
    xml_check = xml_root.find("event")
    if xml_check is None:
        print "No event with tag=20 found in the file:"
        print coda_file
        print "Use last modified time instead\n"
        # Most likely the run was not end properly
        conditions["run_end_time"] = get_last_modifed_time(coda_file)
        conditions["event_count"] = get_total_events_from_prompt(run_number)
        conditions["has_run_end"] = False
    else:
        for xml_result in xml_root.findall("event"):
            run_end_time = int(xml_result.text.split(None)[0])
            event_count = int(xml_result.text.split(None)[2])
        
            conditions["run_end_time"] = datetime.fromtimestamp(run_end_time).strftime("%Y-%m-%d %H:%M:%S")
            conditions["event_count"] = event_count
            conditions["has_run_end"] = True

    # Get user comment and config name
    conditions["user_comment"] = get_user_comment(run_number)
    conditions["run_config"] = get_run_config(run_number)

    return conditions

def get_start_time_from_data(coda_file):
    start_time = None
    cmds = ["evio2xml", "-ev", "18", "-xtod", "-max", "1", coda_file]
    out = check_output(cmds)
    xml_root = Et.ElementTree(Et.fromstring(out)).getroot()
    xml_check = xml_root.find("event")
    if xml_check is None:
        print "No event with tag=18 found in the file:"
        print coda_file
        return start_time
    else:
        for xml_result in xml_root.findall("event"):
            time_data = int(xml_result.text.split(None)[0])
            start_time = datetime.fromtimestamp(time_data).strftime("%Y-%m-%d %H:%M:%S")
        return start_time

def get_last_modifed_time(coda_file):
    last_modified_time = None
    try:
        # use last modified time instead
        mtime = os.path.getmtime(coda_file)
        last_modified_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as ex:
        log.warning("Unable to get last modified time for the coda file: " + str(ex))

    return last_modified_time

def get_total_events_from_prompt(run_number):
    summary_file="/adaqfs/home/apar/PREX/prompt/japanOutput/summary_" + run_number + ".txt"
    nevts = None

    if not os.path.exists(summary_file):
        return nevts

    with open(summary_file, 'rb') as f:
        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if "events processed" in line:
                nevts = line.split(":")[1].strip()
                break
    return nevts

def get_total_events_from_runfile(run_number):
    """    
    get total events
    Files are sitting at ~/epics/runfiles/
    """
    runfile = "/adaqfs/home/apar/epics/runfiles/End_of_Parity_Run_" + run_number + ".epics"

    nevts = None
    with open(runfile, 'rb') as f:
        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if "Total Events" in line:
                nevts = line.split(":")[1].strip()
                break

    #Total Events: 
    if nevts is None or nevts == "":
        print "Fail to parse total number of events from End_of_Parity_Run file"
        sys.exit(1)

    return nevts

def get_run_config(run_number):
    halog_file = "/adaqfs/home/apar/epics/runfiles/Start_of_Run_" + run_number + ".epics"

    config_name = None
    if not os.path.exists(halog_file):
        return config_name

    with open(halog_file, 'rb') as f:
        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if "CODA Configuration" in line:
                config_name = line.split(":")[1].strip()
                break
    return config_name

def get_user_comment(run_number):
    halog_file = "/adaqfs/home/apar/epics/runfiles/Start_of_Run_" + run_number + ".epics"
    comment = None

    if not os.path.exists(halog_file):
        return comment

    with open(halog_file, 'rb') as f:
        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if "Comment:" in line:
                comment = line.split(":")[1].strip()
                break
    return comment
