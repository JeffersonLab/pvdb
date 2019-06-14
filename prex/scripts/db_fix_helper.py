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
    conditions = []

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
    coda_file = files

    cmds = ["evio2xml", "-ev", "20", "-xtod", "-max", "3", coda_file]
    out = check_output(cmds)
    xml_root = Et.ElementTre(Et.fromstring(out)).getroot()
    xml_check = xml_root.find("event")
    if xml_check is None:
        print "No event with tag=20 found in the file"
        sys.exit(1)

    for xml_result in xml_root.findall("event"):
        run_end_time = int(xml_result.text.split(None)[0])
        event_count = int(xml_result.text.split(None)[2])
        
        conditions["end_time"] = datetime.fromtimestamp(run_end_time).strftime("%Y-%m-%d %H:%M:%S")
        conditions["total_events"] = event_count
    return conditions

def get_total_events_from_runfile(run_number):
    """    
    get total events
    Files are sitting at ~/epics/runfiles/
    """
    runfile = "/adaqfs/home/apar/epics/runfiles/End_of_Parity_Run_" + run_number + ".epics"

    nevts = None
    with open(runfile, 'rb') as f:
        for line in lines:
            if "Total Events" in line:
                nevts = line.split(":")[1].strip()
                break

    #Total Events: 
    if nevts is None or nevts == "":
        print "Fail to parse total number of events from End_of_Parity_Run file"
        sys.exit(1)

    return nevts
