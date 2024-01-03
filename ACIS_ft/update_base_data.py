#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#           update_base_data.py: update .../Short_term/<data_file>                      #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 03, 2021                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import re
import Chandra.Time
import unittest
import getpass
import glob
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; setenv ACISTOOLSDIR /home/pgf', shell='tcsh')

#
#--- directory list
#
BIN_DIR = '/data/mta/Script/ACIS/Focal/Script/'
HOUSE_KEEPING = '/data/mta/Script/ACIS/Focal/Script/house_keeping/'
SHORT_TERM = '/data/mta/Script/ACIS/Focal/Short_term/'

#
#--- append path to a private folder
#
sys.path.append(BIN_DIR)

#-------------------------------------------------------------------------------
#-- update_base_data: update acis focal temperature data files                --
#-------------------------------------------------------------------------------

def update_base_data():
    """
    update acis focal temperature data files 
    input: none but read from /dsops/GOT/input/*_Dump_EM_*.gz
    output: <short_term>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
#
#--- read already processed data list
#
    ifile = f"{HOUSE_KEEPING}old_list_short"
    with open(ifile,'r') as f:
        olist = [x.strip() for x in f.readlines()]
    os.system(f"mv -f {ifile} {ifile}~")
    os.system(f"ls /dsops/GOT/input/*_Dump_EM_*.gz > {ifile}")
    with open(ifile,'r') as f:
        clist = [x.strip() for x in f.readlines()]
    nlist = list(set(clist).difference(set(olist)))
    
    plist = extract_data_from_dump(nlist)
#-------------------------------------------------------------------------------
#-- extract_data_from_dump: extract focal data from dump data                 --
#-------------------------------------------------------------------------------

"""def extract_data_from_dump(nlist, test=0):"""
def extract_data_from_dump(nlist):
    """
    extract focal data from dump data
    input:  nlist   --- a list of new dump data file names
    output: extracted data: <short_term>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
    plist = []
    for ent in nlist:
        nfile = create_out_name(ent)
        plist.append(nfile)

        cmd = f"/usr/bin/env PERL5LIB=  gzip -dc {ent} | {BIN_DIR}getnrt -O $* | {BIN_DIR}acis_ft_fptemp.pl >> {nfile}"
        bash(cmd,  env=ascdsenv)

    return plist

#-------------------------------------------------------------------------------
#-- create_out_name: create an output data file name                          --
#-------------------------------------------------------------------------------

def create_out_name(ifile):
    """
    create an output data file name
    input:  ifile   --- dump_em file name
    output: ofile   --- output file name in <short_term>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
    atemp = ifile.split("/")
    btemp = atemp[-1].split('_Dump')
    ofile = f"{SHORT_TERM}data_{btemp[0]}"

    return ofile


if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

    update_base_data()
#
#--- Remove lock file once process is completed
#
    os.system(f'rm /tmp/{user}/{name}.lock')