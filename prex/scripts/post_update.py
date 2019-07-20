import os
import sys
import argparse
import socket
import glob
import logging
import subprocess
from datetime import datetime

# rcdb stuff
import rcdb
from rcdb.log_format import BraceMessage as Lf
from rcdb import ConfigurationProvider, UpdateReasons
from rcdb import UpdateContext, UpdateReasons, DefaultConditions
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType, Condition

# prex stuff
from parity_rcdb import parity_coda_parser
import run_start

from scripts import fixer_run_end

log = logging.getLogger('pvdb') # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
log.setLevel(logging.INFO)  # DEBUG: print everything. Changed to logging. INFO for less output

def get_usage():
    return """
    Usage:
         post_repair.py --run <run_number> -c <db_connection_string> --update=[coda,epics] --reason=[start, update, end]
    """

def update(run_number, update_parts, context):

    host = socket.gethostname()

    """
    coda_path = None
    coda_file_name = None

    if "adaq" in host:
        coda_path = "/adaq1/data1/apar/"
    elif "aonl" in host:
        coda_path = "/adaq1/data1/apar/"
    else:
        coda_path = "/cache/halla/parity/raw/"

    for files in glob.glob(coda_path+"*"+run_number+"*.dat"):
        if not "parity18" in files:
            coda_file_name = files

    if "coda" in update_parts and coda_file_name is None:
        print "CODA file is not found", run_number
        log.info(Lf("Coda file is not found, run={}", run_number))
        sys.exit()
    """

    # Udpate db (coda)
    if "coda" in update_parts:
        log.debug(Lf("Update run, run={}", run_number))
        # Parse coda info (start, end time, ..)
        #        coda_parse_result = parity_coda_parser.parse_coda_data_file(coda_file_name)
        #        run_start.update_parity_coda_conditions(context, coda_parse_result)
        # use fixer script to update coda info
        fixer_run_end.update_run(str(run_number))

    assert isinstance(context.db, RCDBProvider)
    db = context.db

    # Update epics
    if "epics" in update_parts:
        log.debug(Lf("Update epics, run={}", run_number))
        if not "adaq" in host and not "ops" in host:
            print "You probably don't have myget available from your machine"
            sys.exit()
        
        if not db.get_run(run_number):
            log.info(Lf("Run '{}' is not found in DB", run_number))
            return

        run = db.get_run(run_number)
        conditions = {}

        """
        myget -c[channel name] -t[time] 
        :if time is not specified, it returns data for last 1min
        :Use myStats to get the average current where the BCM reads 1-70 uA 
        excluding periods when the beam is off
        """
        import epics_helper
        for epics_name, cond_name in epics_helper.epics_list.iteritems():
            try:
                start_time_str = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
                end_time_str = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")
                if "current" in cond_name:
                    cmds = ["myStats", "-b", start_time_str , "-e", end_time_str, "-c", epics_name, "-r", "1:100", "-l", epics_name]
                    cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)

                    n = 0
                    for line in cond_out.stdout:
                        n += 1
                        if n == 1:    # skip header
                            continue
                        tokens = line.strip().split()
                        if len(tokens) < 3:
                            continue
                        key = tokens[0]
                        value = tokens[2]
                        if value == "N/A":
                            value = 0
                        if key == epics_name:
                            conditions[cond_name] = value
                else:
                    cmds = ["myget", "-c", epics_name, "-t", start_time_str]
                    cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                    

                    for line in cond_out.stdout:
                        value = line.strip().split()[2]
                        if "<<" in line:
                            conditions[cond_name] = "-999"
                            continue

                        if cond_name == "ihwp":
                            if value == "1":
                                conditions[cond_name] = "IN"
                            else:
                                conditions[cond_name] = "OUT"
                        elif cond_name == "helicity_pattern":
                            if value == "1":
                                conditions[cond_name] = "Quartet"
                            elif value == "2":
                                conditions[cond_name] = "Octet"
                            else:
                                conditions[cond_name] = "-999" # undefined
                        else:
                            conditions[cond_name] = value

            except Exception as e:
                log.warn(Lf("Error in epics request : '{}',{}'", cond_name, e))

        # Get target type condition
        conditions["target_type"] = epics_helper.get_PREX_target_name(conditions["target_45encoder"], conditions["target_90encoder"])

        db.add_conditions(run_number, conditions, True)

    # >oO DEBUG log message
    db.add_log_record("",
                      "Post run update. datetime: '{}'"
                      .format(datetime.now()), run_number)

if __name__ == "__main__":

    description = "Script for DB udpate after CODA run end"
    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("--run", type=str, help="Run number", default="")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--update", help="Comma separated, modules to update such as coda,epics", default="")
    parser.add_argument("--reason", help="Reason of the udpate: 'start', 'udpate', 'end' or ''", default="")
    parser.add_argument("-c", "--connection", help="connection string (eg, mysql://pvdb@localhost/pvdb)")
    args = parser.parse_args()

    runs = []
    if "-" in args.run:
        brun=args.run.split("-")[0]
        erun=args.run.split("-")[1]
        for x in range(int(brun), int(erun)+1):
            runs.append(x)
    else:
        runs.append(args.run)

    # Connection
    if args.connection:
        con_string = args.connection
    elif "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a script parameter (-c)")
        sys.exit(2)
    log.debug(Lf("con_string = '{}'", con_string))

   # What to update                                                                   
    update_parts = []                                                                  
    if args.update:                                                                    
        update_parts = args.update.split(',')                                          
    log.debug(Lf("update_parts = {}", update_parts))

   # Update reason
    update_reason = args.reason
    log.debug(Lf("update_reason = '{}'", update_reason))

    # Open DB connection
    db = ConfigurationProvider(con_string)
    
    # Create update context
    update_context = rcdb.UpdateContext(db, update_reason)

    for run_number in range(int(runs[0]), int(runs[-1])+1):
        print "Update run : ", run_number
        update(str(run_number), update_parts, update_context)
