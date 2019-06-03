import os
import sys
import glob

def main():
    run_number = sys.argv[1]
    print run_number

    # Set data_path
    if "QW_DATA" in os.environ:
        data_path = os.environ["QW_DATA"]
    else:
        print ("QW_DATA is not set, force to /adaq1/data1/apar")
        data_path = "/adaq1/data1/apar"
        
    # when data path was set to /adaq2/data1/apar
    if int(run_number) < 2143:
        data_path = "/adaq2/data1/apar"

    print data_path

    # coda files
    num_files = len([files for files in glob.glob(data_path+"/*"+run_number+".dat*")])
    print num_files
    print files # last file
#    for files in glob.glob(data_path+"/*"+run_number+".dat*"):

if __name__== '__main__':
    main()
