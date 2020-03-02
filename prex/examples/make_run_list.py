import os
import sys
import argparse

import rcdb
from rcdb.provider import RCDBProvider

def get_usage():
    return """
    This script prints out the run table for a given selecting condition
    
    How to use:
    1) For a single run
    python --run=3333
    2) For a run range
    python --run=3000-3500

    Set selection query:
    python --run=3000-3500 --type=Production --target=208Pb --ihwp=IN --rhwp=1 --flag=Good

    By default, it will print out run numbers
    To print out all (run numbers and conditions), set --show=True
    python --run=3000-3500 --type=Production --target=208Pb --ihwp=IN --rhwp=1 --flag=Good --show=True

    One can also set multiple options for a condition.
    For example, to select runs marked either Good or Suspicious:
    python --run=3000-3500 --flag=Good,Suspicous --show=True
    """

def get_list():
    # Get arguments and make a run list to request query

    description=""

    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("--run", help="single run number or range 3000-3100", required=True)
    parser.add_argument("--type", type=str, help="Production, Calibration, Test, Junk (if you want..why not)")
    parser.add_argument("--target", type=str, help="208Pb, D-Pb-D, C-Pb-C, Carbon, 48Ca")
    parser.add_argument("--nevt", type=int, help="Minimum number of events")
    parser.add_argument("--current", type=float, help="Minimum average current")
    parser.add_argument("--ihwp", type=str, help="Insertable 1/2 wave plate IN or OUT")
    parser.add_argument("--rhwp", type=int, help="Rotating 1/2 wave plate")
    parser.add_argument("--slug", type=int, help="slug number")
    parser.add_argument("--flag", type=str, help="Good, NeedCut, Bad, Suspicious")
    parser.add_argument("--is_valid_end", type=bool, help="True or False")
    parser.add_argument("--show", type=bool, help="print option, True=show all, False=print only run numbers, default set to False", default=False)
    parser.add_argument("--debug", type=bool, help="Print to terminal", default=False)
    args = parser.parse_args()


    runs = []

    runlist=args.run
    if "-" in runlist:
        brun=runlist.split("-")[0]
        erun=runlist.split("-")[1]
        for x in range(int(brun), int(erun)+1):
            runs.append(x)
    else:
        runs.append(int(runlist))

    # DB connection
    con_str = "mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb"
    db = rcdb.RCDBProvider(con_str)

    query_str=None

    # Run type
    if args.type is not None:
        args_list = [str(x) for x in args.type.split(',')]
        query_str = "run_type in %s" % args_list

    # Target type    
    if args.target is not None:
        select_str = "'%s' in target_type" % args.target
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

    # event count
    if args.nevt is not None:
        select_str = "event_count > %d" % (int(args.nevt))
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

    # minimum average current
    if args.current is not None:
        select_str = "beam_current > %f" % (float(args.current))
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

    # slug
    if args.slug is not None:
        select_str = "slug == %d" % args.slug
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

    # IHWP IN/OUT
    if args.ihwp is not None:
        select_str = "ihwp == '%s'" % args.ihwp
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

    # RHWP
    if args.rhwp is not None:
        select_str = "((rhwp - %d) >= 0 and (rhwp - %d) < 1)" % (args.rhwp, args.rhwp)
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

    # Run flag (set by WAC)
    if args.flag is not None:
        args_list = [str(x) for x in args.flag.split(',')]
        select_str = "run_flag in %s" % args_list
        if query_str is None:
            query_str = select_str
        else:
            query_str = query_str + " and " + select_str

#    if args.is_valid_end is not None:

    if  query_str is None:
        query_str = ""

    print
    print "Query form: ", query_str
    print

    # get result for the given run range
    result = db.select_runs("%s" % query_str, runs[0], runs[-1])

    row = result.get_values(["run_type", "beam_current", "slug", "ihwp", "rhwp", "is_valid_run_end", "run_flag"])

    # Print out the list
    fout = open('list.txt', 'wb')
    irow=0
    for run in result:
        if row[irow][4] is None:
            row[irow][4] = "None"
        else:
            row[irow][4] = str(int(row[irow][4]))

        if args.show:
            if irow == 0:
                print >> fout, "# runnumber, run_type, avg_cur, slug, IHWP, RHWP, run_end, run_flag"

            ostr = ("%s \t %s \t %s \t %s \t %s \t %s \t %s \t %s" % (run.number, row[irow][0], row[irow][1], row[irow][2], row[irow][3], row[irow][4], row[irow][5], row[irow][6]))
            print >> fout, ostr

            if args.debug:
                if irow == 0:
                    print "# runnumber, run_type, avg_cur, slug, IHWP, RHWP, run_end, run_flag"
                print ostr
        else:
            print >> fout, run.number

            if args.debug:
                print run.number
        irow += 1

if __name__== '__main__':
    get_list()
