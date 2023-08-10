#!/proj/sot/ska3/flight/bin/python

#####################################################################################    
#                                                                                   #
#           update_sim_flex.py: update sim_flex difference data sets                #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Feb 02, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
import datetime
import random
import getpass
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- update_sim_offset: update sim offset data                                            ---
#-------------------------------------------------------------------------------------------

def update_sim_offset():
    """
    update sim offset data
    input:  none
    output: <out_dir>/Comp_save/Compsimoffset/<msid>_full_data_<year>.fits
    """
    t_file  = 'flexadif_full_data_*.fits*'
    out_dir = deposit_dir + 'Comp_save/Compsimoffset/'
    
    [tstart, tstop, year] = ecf.find_data_collecting_period(out_dir, t_file)
#
#--- update the data
#
    get_data(tstart, tstop, year, out_dir)
#
#--- zip the fits file from the last year at the beginning of the year
#
    ecf.check_zip_possible(out_dir)

#-------------------------------------------------------------------------------------------
#-- get_data: update sim flex offset data for the given data period                       --
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year, out_dir):
    """
    update sim flex offset data for the given data period
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            year    --- data extracted year
            out_dir --- output_directory
    output: <out_dir>/Comp_save/Compsimoffset/<msid>_full_data_<year>.fits
    """
    print(f"Period: {start} <--> {stop} in Year: {year}")

    for msid in ['flexadif', 'flexbdif', 'flexcdif']:

        if  msid == 'flexadif':
            msid_t = '3faflaat'
            msid_s = '3sflxast'
     
        elif msid == 'flexbdif':
            msid_t = '3faflbat'
            msid_s = '3sflxbst'
        else:
            msid_t = '3faflcat'
            msid_s = '3sflxcst'
    
        out   = fetch.MSID(msid_t, start, stop)
        tdat1 = out.vals
        ttime = out.times
        out   = fetch.MSID(msid_s, start, stop)
        tdat2 = out.vals

        tlen1 = len(tdat1)
        tlen2 = len(tdat2)
        if tlen1 == 0 or tlen2 == 0:
            continue

        if tlen1 > tlen2:
            diff = tlen1 - tlen2
            for k in range(0, diff):
                tdat2 = numpy.append(tdat2, tadt2[-1])
        elif tlen1 < tlen2:
            diff = tlen2 - tlen1
            for k in range(0, diff):
                tdat1 = numpy.append(tdat1, tadt1[-1])

        ocols = ['time', msid]
        cdata = [ttime, tdat1 - tdat2]
         
        ofits = out_dir + msid + '_full_data_' + str(year) +'.fits'
        if os.path.isfile(ofits):
            ecf.update_fits_file(ofits, ocols, cdata)
        else:
            ecf.create_fits_file(ofits, ocols, cdata)

#-------------------------------------------------------------------------------------------

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
        
    update_sim_offset()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")