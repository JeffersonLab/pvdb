Run database for the PREX and CREX

Setting up from scratch
1) Clone the repository
git clone https://github.com/JeffersonLab/pvdb

2) Download rcdb submodule
> cd pvdb
> git submodule init
> git submodule update

3) Set environment variables
> source environment.csh

4) Check if things are set properly
> rcnd
This should show the list of condition types

-----------------------------------------------

Note:

* Connection string:
Please use the read-only copy
> setenv RCDB_CONNECTION mysql://rcdb@hallcdb.jlab.org:3306/a-rcdb

* Questions, bug report: sanghwa@jlab.org
