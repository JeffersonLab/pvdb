#!/bin/csh

set curr_dir=`pwd`
set RCDB_DIR=$curr_dir/rcdb
set PREX_DIR=$curr_dir/prex

# RCDB environment 
if ( ! $?RCDB_HOME ) then
    setenv RCDB_HOME $RCDB_DIR
endif

if ( ! $?LD_LIBRARY_PATH ) then
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib
else
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib:$LD_LIBRARY_PATH
endif

if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH $RCDB_HOME/python
else
    setenv PYTHONPATH $RCDB_HOME/python:$PYTHONPATH
endif

setenv PATH "$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

# PREX environment
setenv PYTHONPATH "$PREX_DIR":$PYTHONPATH

# connection string
if ( "$HOSTNAME" =~ *"adaq"* ) then
    setenv RCDB_CONNECTION mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb
else
    setenv RCDB_CONNECTION mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb
endif
