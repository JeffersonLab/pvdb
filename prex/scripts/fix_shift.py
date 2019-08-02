import os
import re
import sys
import json
import urllib2
import requests
import pickle

from scripts import db_fix_helper

import rcdb
from rcdb.provider import RCDBProvider
from rcdb import DefaultConditions

TESTMODE=True

def get_halog_content(run_number, ddict):
    ddict[run_number] = {}

    author = "apar"
    LOGBOOK = "HALOG"

    url = 'https://logbooks.jlab.org/api/elog/entries'
    url = url + '?book=' + LOGBOOK
    url = url + '&limit=0'

    url = url + '&startdate=2019-07-01'
    url = url + '&enddate=2019-08-02' 

    url = url + '&tag=StartOfRun'

    ## Output fields                                                                                                     
    url = url + '&field=title&field=body'

    ## Append query fields
    url = url + "&title=" + "Start_Parity_Run_" + run_number
    url = url + "&author=" + author

    res = requests.get(url)
    res.json()

    dec_json = json.loads(res.text)

    run_type=None
    user_comment=None

    if dec_json['data']['currentItems'] == 0:
        return
    else:
        for line in dec_json['data']['entries'][0]['body']['content'].splitlines():
            if 'Run_type=' in line:
                run_type = line.split('Run_type=')[1].split(',')[0]
            if 'Comment:' in line:
                user_comment = line.split(':')[1].strip().split(',parity')[0]

    #return {'run_type': run_type, 'user_comment': user_comment}
    ddict[run_number]['run_type'] = run_type
    ddict[run_number]['user_comment'] = user_comment

    coment_from_runfile = db_fix_helper.get_user_comment(run_number)
    ddict[run_number]['user_comment2'] = coment_from_runfile
    ddict[run_number]['run_config'] = db_fix_helper.get_run_config(run_number)

def get_rcdb_content(run_number):
    result = db.select_runs("", runs[0], runs[1])

def load_halog_content(runs):
    pickle_file = 'halog.pkl'

    ddict = {}
    if os.path.isfile(pickle_file):
        infile = open(pickle_file, 'rb')
        try:
            ddict = pickle.load(infile)
        except EOFError:
            print "empty data file.. make a new one!"
        infile.close()

    for run in runs:
        run = str(run)
        if run in ddict:
            continue
        else:
            print "check run", run
            get_halog_content(run, ddict)

    with open(pickle_file, 'wb') as ff:
        pickle.dump(ddict, ff)

    print "HALOG data loaded"
    return ddict

if __name__== '__main__':

    dd = {}
    runs = []

    runlist = sys.argv[1]

    if "-" in runlist:
        brun = runlist.split("-")[0]
        erun = runlist.split("-")[1]
        for x in range(int(brun), int(erun)+1):
            runs.append(x)
    else:
        print
        print "Takes input run list"
        print "ex) python fix_shift.py 3300-3400"
        sys.exit(1)

    dd = load_halog_content(runs)


    #con_str = "mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"
    con_str = os.environ["RCDB_CONNECTION"]
    db = rcdb.RCDBProvider(con_str)

    result = db.select_runs("", runs[0], runs[-1])
    row = result.get_values(["run_config", "run_type", "target_type", "user_comment", "run_flag", "wac_comment"])

    skip_runs = [3485, 3488, 3542]

    irow=0
    for run in result:
        if int(run.number) in skip_runs:
            irow += 1
            continue

        # fix comment
        """
        if row[irow][3] != dd[str(run.number)]['user_comment']:
            if TESTMODE:
                print run.number
                print row[irow][3]            
                print row[irow+1][3]            
                print dd[str(run.number)]['user_comment']
                print
            else:
                db.add_condition(run, DefaultConditions.USER_COMMENT, dd[str(run.number)]['user_comment'], True)
        """

        # Fix run type
        """
        if row[irow][1] != dd[str(run.number)]['run_type']:
            if TESTMODE:
                print run.number
                print row[irow][1]            
                print row[irow+1][1]            
                print dd[str(run.number)]['run_type']
                print
            else:
                if dd[str(run.number)]['run_type'] is None:
                    print "Update manually"
                    print run.number
                    print row[irow][1]            
                    print row[irow+1][1]            
                    print dd[str(run.number)]['run_type']
                    print
                else:
                    db.add_condition(run, DefaultConditions.RUN_TYPE, dd[str(run.number)]['run_type'], True)
                
        """

        if row[irow][1] == 'Production':
            if row[irow][4] is None or row[irow][4] != 'Good':
                print
                print run.number
                print row[irow][4]
                print row[irow][5]

        """
        if row[irow][3] != dd[str(run.number)]['user_comment']:
            print run.number
            print row[irow][1], dd[str(run.number)]['run_type']
            print row[irow][3]
            if dd[str(run.number)]['user_comment'] == "" and row[irow][3] is not None:
                print "No user comment but RCDB has comment"
            print dd[str(run.number)]['user_comment']
            print dd[str(run.number)]['user_comment2']
            print row[irow][4]
            print
        """
        
        irow += 1
