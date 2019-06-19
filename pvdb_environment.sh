#!/bin/bash

curr_dir=`pwd`
RCDB_DIR=/adaqfs/home/apar/pvdb/rcdb
PREX_DIR=/adaqfs/home/apar/pvdb/prex

# RCDB environment 
if [[ -z $RCDB_HOME ]]; then
    export RCDB_HOME=$RCDB_DIR
fi

if [[ -z $LD_LIBRARY_PATH ]]; then
    export LD_LIBRARY_PATH=$RCDB_HOME/cpp/lib
else
    export LD_LIBRARY_PATH="$RCDB_HOME/cpp/lib":$LD_LIBRARY_PATH
fi

if [[ -z $PYTHONPATH ]]; then
    export PYTHONPATH="$RCDB_HOME/python"
else
    export PYTHONPATH="$RCDB_HOME/python":$PYTHONPATH
fi

export PATH="$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

# PREX environment
export PYTHONPATH="$PREX_DIR":$PYTHONPATH

# connection string
if [[ "$HOSTNAME" == *"adaq"* ]]; then
    export RCDB_CONNECTION=mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb
else
    export RCDB_CONNECTION=mysql://prex@hallcdb.jlab.org:3306/a-rcdb
fi
