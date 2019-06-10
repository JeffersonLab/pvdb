#!/bin/tcsh

set curr_dir=`pwd`
set RCDB_DIR=$HOME/pvdb/rcdb
set PREX_DIR=$HOME/pvdb/prex

# RCDB environment 
if ( ! $?RCDB_HOME ) then
    setenv RCDB_HOME $RCDB_DIR
endif
if (! $?LD_LIBRARY_PATH) then
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib
else
    setenv LD_LIBRARY_PATH "$RCDB_HOME/cpp/lib":$LD_LIBRARY_PATH
endif

if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH "$RCDB_HOME/python"
else
    setenv PYTHONPATH "$RCDB_HOME/python":$PYTHONPATH
endif
setenv PATH "$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

# PREX environment
setenv PYTHONPATH "$PREX_DIR":$PYTHONPATH

# connection string
if (! $?RCDB_CONNECTION ) then
    setenv RCDB_CONNECTION mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb
endif
