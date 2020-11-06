#!/bin/bash
slug=0
if [ $# -le 1 ]; then
  slug=$1
  python /adaqfs/home/apar/pvdb/prex/examples/make_run_list.py --run=2000-8000 --type=Production --current=20 --target=48Ca --slug=${slug}
  mv list.txt slug${slug}.list
fi
