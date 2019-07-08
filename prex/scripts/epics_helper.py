import logging
import os, sys
import rcdb
import subprocess
import socket
from datetime import datetime

#pvdb
from parity_rcdb import ParityConditions

#rcdb stuff
from rcdb.model import ConditionType, Condition
from rcdb.log_format import BraceMessage as Lf

"""
EPICS variables

:IGL1I00OD16_16: Insertable waveplate, string (IN/OUT)
:psub_pl_pos: Rotating waveplate (Readback)
:HWienAngle: Horizontal wien angle
:VWienAngle: Vertical wien angle
:haBDSPOS: Target encoder pos. Not filled for APEX. APEXPOS is used. Need to check before PREX
:APEXPOS":ParityConditions.TARGET_ENCODER # used for data taken during APEX
PREX has two target ladders
45 Deg target (warm): pcrex45BDSPOS.VAL
90 Deg target (cold): pcrex90BDSPOS.VAL
"""
epics_list = {
    "HALLA:p":ParityConditions.BEAM_ENERGY,
    "IBC1H04CRCUR2":ParityConditions.BEAM_CURRENT,
    "pcrex45BDSPOS.VAL":ParityConditions.TARGET_45ENCODER,
    "pcrex90BDSPOS.VAL":ParityConditions.TARGET_90ENCODER,
    "IGL1I00OD16_16":ParityConditions.IHWP,
    "psub_pl_pos":ParityConditions.RQWP,
    "HWienAngle":ParityConditions.HWIEN,
    "VWienAngle":ParityConditions.VWIEN,
    "HELPATTERNd":ParityConditions.HELICITY_PATTERN,
    "HELFREQ":ParityConditions.HELICITY_FREQUENCY
}

def get_run_conds():
    conditions = {}

    for epics_name, cond_name in epics_list.iteritems():
        cmds = ['caget', '-t', epics_name]
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()
        if "Invalid" in cond_out:
            print "ERROR Invalid epics channel, check with caget again:\t", epics_name
            cond_out = "-999"

        conditions[cond_name] = cond_out
    # PREX target type name
    conditions["target_type"] = get_PREX_target_name(conditions[ParityConditions.TARGET_45ENCODER], conditions[ParityConditions.TARGET_90ENCODER])

    return conditions

def get_end_run_conds(run):
    # This is being used for run_end.py
    conditions = {}

    start_time_str = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
    if run.end_time is not None: 
        end_time_str = run.end_time
    else:
        now_time = datetime.now()
        end_time_str = now_time.strftime("%Y-%m-%d %H:%M:%S")

    for epics_name, cond_name in epics_list.iteritems():
        if "encoder" in cond_name:
            continue
        # Get average beam current
        if "current" in cond_name:
            try:
                cmds = ["myStats", "-b", start_time_str , "-e", end_time_str, "-c", epics_name, "-r", "0:100", "-l", epics_name]
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
            except Exception as ex:
                conditions["beam_current"] = "-999"
        else:
            # get epics info 
            # to check conditions again at the end (mainly consistency check)
            try:
                cmds = ["myget", "-c", epics_name, "-t", end_time_str]
                cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                    

                for line in cond_out.stdout:
                    value = line.strip().split()[2]
                    if "<<" in value:
                        conditions[cond_name] = "-999"
                    else:
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
                conditions[cond_name] = "-999"

    # PREX target type name
    #conditions["target_type"] = get_PREX_target_name(conditions[ParityConditions.TARGET_45ENCODER], conditions[ParityConditions.TARGET_90ENCODER])
    return conditions

def mya_get_run_conds(run, log):

    # get epics information using start_time
    conditions = {}

    start_time_str = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")
    for epics_name, cond_name in epics_list.iteritems():
        end_time_str = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")

        # skip period when APEXPOS was not available 
        if cond_name == "target_encoder" and start_time_str < "2019-02-18 08:00:00":
            conditions[cond_name] = "-999"
            continue
        if "current" in cond_name:
            try:
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
            except Exception as ex:
                log.warn(Lf("Error in beam_current request : '{}'", e))
                conditions["beam_current"] = "-999"
        else:
            try:
                cmds = ["myget", "-c", epics_name, "-t", start_time_str]
                cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)                    

                for line in cond_out.stdout:
                    value = line.strip().split()[2]

                    if "<<" in line:
                        conditions[cond_name] = "-999"
                        continue
                    else:
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
                conditions[cond_name] = "-999"

    # Get target type condition
    conditions["target_type"] = get_PREX_target_name(conditions[ParityConditions.TARGET_45ENCODER], 
                                                     conditions[ParityConditions.TARGET_90ENCODER])

    return conditions

def print_conds():
    # used for test
    conditions = get_run_conds()
#    print conditions[ParityConditions.BEAM_ENERGY]
    print conditions["target_type"]

def get_PREX_target_name(enc_pos45, enc_pos90):

    if enc_pos45 == "-999" and enc_pos90 == "-999":
        return "Invalid"

    tar45_name = get_45target_name(enc_pos45)
    tar90_name = get_90target_name(enc_pos90)

    if tar45_name == "Home" or tar45_name == "Invalid":
        return tar90_name
    else:
        return tar45_name

def get_45target_name(enc_pos):
    """
    Compare encoder position with target BDS table
    Return corresponding target name
    """
    if enc_pos == "-999":
        return "Invalid"

    tar_bds = [13,
               2021386,
               2479033,
               2636350,
               2793666,
               2959982]

    tar_name = ["Home", 
                "WaterCell 2.77%",
                "Tungsten 0.3%",
                "Pb 0.9%",
                "Carbon 0.25%",
                "Carbon Hole"]

    bds_close = min(tar_bds, key=lambda x:abs(x-float(enc_pos)))

    if abs(float(enc_pos)-bds_close) > 100:
        return "Unknown"
    else:
        tar_index = tar_bds.index(bds_close)
        return tar_name[tar_index]

def get_90target_name(enc_pos):
    """
    Compare encoder position with target BDS table
    Return corresponding target name
    Not a full list, to be updated later......
    """
    if enc_pos == "-999":
        return "Invalid"
        
    tar_bds = [0,
               1800388,
               2228306,
               2801491,
               3230535,
               3659579,
               4088623,
               4517667,
               4946711,
               5377332,
               5807953,
               6238573,
               6669194,
               7099815,
               7529422,
               7959873,
               8390325]

    tar_name = ["Home", 
                "Halo",
                "40Ca 6%",
                "Carbon Hole (Cold)",
                "D-208Pb10-D",
                "D-208Pb9-D",
                "D-208Pb8-D",
                "D-208Pb7-D",
                "D-208Pb6-D",
                "D-208Pb5-D",
                "D-208Pb4-D",
                "D-208Pb3-D",
                "D-208Pb2-D",
                "Carbon 1%",
                "C-208Pb-C",
                "D-Pb-D",
                "C-Pb-C"]

    bds_close = min(tar_bds, key=lambda x:abs(x-float(enc_pos)))

    if abs(float(enc_pos)-bds_close) > 100:
        return "Unknown"
    else:
        tar_index = tar_bds.index(bds_close)
        return tar_name[tar_index]

def get_target_name(enc_pos):
    """
    Compare encoder position with target BDS table
    Return corresponding target name
    Based on the APEX target system for now
    Need to udpate for PREX
    """
    if not enc_pos.isdigit():
        return "Invalid"

    if enc_pos == "-999":
        return "Invalid"

    tar_bds = [-18526,
               3197,
               47255,
               165223,
               297861,
               427509,
               603200,
               710189,
               994363,
               1248916,
               1722284,
               1743072]

    tar_name = ["Hard_Stop",
                "Up-hole_2x2",
                "Down-hole_2x2",
                "Optics 1 (UP)",
                "Optics 2 (MIDDLE)",
                "Optics 3 (DOWN)",
                "W wire (for BW)",
                "W wires",
                "HOME",
                "Carbon 0.53%RL",
                "Tungsten 2.8%RL",
                "Hard_Stop"]

    bds_close = min(tar_bds, key=lambda x:abs(x-float(enc_pos)))

    if abs(float(enc_pos)-bds_close) > 100:
        return "Unknown"
    else:
        tar_index = tar_bds.index(bds_close)
        return tar_name[tar_index]


def update_db_conds(db, run, reason):
    """
    add_conditions(run, name_values, replace=True/False)
    :name_values: dictionary or list of name-value pairs
    :replace: default is False?
    :Defined in provider.py, takes care of incorrect ConditionType
    """

    log = logging.getLogger('pvdb.update.epics')
    log.debug(Lf("Running 'update_rcdb_conds(db={},   run={})'", db, run))

    conditions = {}
    
    if reason == "start":
        conditions.update( get_run_conds() )
    if reason == "update" or reason == "end":
        conditions.update( mya_get_run_conds(run, log) )

    db.add_conditions(run, conditions, True)
    log.debug("Commited to DB. End of update_db_conds()")

    return conditions

if __name__ == "__main__":
    # check if it would have caget available 
    host = socket.gethostname()
    if not ("adaq" in host or "aonl" in host or "ops" in host):
        print "You may  not have caget available. Check first"
        sys.exit()

    log = logging.getLogger('pvdb.update')               # create run configuration standard logger
    log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
    log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://pvdb@localhost/pvdb"

    db = rcdb.RCDBProvider(con_str)

    # argv = run number
    update_db_conds(db, int(sys.argv[1]), "update")
