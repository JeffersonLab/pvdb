#!/bin/bash

PLOT_FLAG=1

script_dir=/adaqfs/home/apar/pvdb/prex/examples

# get charge for each run
python $script_dir/acc_charge.py

# Other examples
# 1) Set run range
# python $script_dir/acc_charge.py --run=3000-4000
# 2) Use a run list
# python $script_dir/acc_charge.py --list list.txt
# 3) Select runs marked as Good only
# python $script_dir/acc_charge.py --list list.txt --goodrun=True

if [ $PLOT_FLAG -eq 1 ]; then
    root -b -q ${script_dir}/DrawChargeMon.C
    evince charge_mon.pdf&
fi
