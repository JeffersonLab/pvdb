import os
import re
import sys
import json
import urllib2
import requests
import pickle


def get_halog_content(run_number, ddict):
    ddict[run_number] = {}

    author = "apar"
    LOGBOOK = "HALOG"

    url = 'https://logbooks.jlab.org/api/elog/entries'
    url = url + '?book=' + LOGBOOK
    url = url + '&limit=0'

    url = url + '&startdate=2019-07-01'
    url = url + '&enddate=2019-07-31' 

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

#    return {'run_type': run_type, 'user_comment': user_comment}
    ddict[run_number]['run_type'] = run_type
    ddict[run_number]['user_comment'] = user_comment

def get_rcdb_content(run_number):
    result = db.select_runs("", runs[0], runs[1])

def load_halog_content(runs):
    pickle_file = 'halog.pkl'

    ddict = {}
    if os.path.isfile(pickle_file):
        infile = open(pickel_file, 'rb')
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
    print dd['3740']

