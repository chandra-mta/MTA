#!/proj/sot/ska3/flight/bin/python

#################################################################################    
#                                                                               #
#       process_dea_data_full.py: create full resolution dea data fits files    #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Feb 04, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
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
import mta_common_functions     as mcf
import envelope_common_function as ecf
#
#--- set a temporary file name
#
rtail  = int(time.time() *random.random())
zspace = '/tmp/zspace' + str(rtail)

dea_data_dir = bin_dir + 'DEA/RDB/'

#-------------------------------------------------------------------------------------------
#-- process_dea_data_full: create full resolution dea data fits files                    ---
#-------------------------------------------------------------------------------------------

def process_dea_data_full(year):
    """
    convert deahk related rdb data into fits files
    input:  part    ---- indictor whether temp or elec to run;default: '' run both
            it also read from the deahk rdb files
    output: <data_dir>/deahk<#>_<period>_data.fits
    """
    if year == '':
        year = int(float(time.strftime('%Y', time.gmtime())))
#
#--- for the first couple of days of the year, take care the last year's data
#
        yday = int(float(time.strftime('%Y', time.gmtime())))
        if yday < 3:
            year -= 1
#
#--- compress fits file of the last year
#
        if yday >= 3 and yday < 5:
            lyear = year - 1
            cmd = 'gzip -fq ' + deposit_dir + 'Deahk_save/*/deahk*_full_data_' 
            cmd = cmd + str(lyear) + '.fits'
            os.system(cmd)


    print("Processing Year: " + str(year))
#
#--- dea temp
#
    drange = list(range(1,14)) + list(range(15,17))
    group  = 'Deahk_temp'

    dhead  = dea_data_dir + 'deahk_temp_week'
    print("DEAHK Temp")
    create_full_dea_data(dhead, group, drange, year)
#
#--- dea elec
#
    drange = list(range(17,21)) + list(range(25,41))
    group  = 'Deahk_elec'

    dhead  = dea_data_dir + 'deahk_elec_week'
    print("DEAHK Elec")
    create_full_dea_data(dhead, group, drange, year)

#-------------------------------------------------------------------------------------------
#-- create_full_dea_data: convert week time rdb data files into a long term data fits files 
#-------------------------------------------------------------------------------------------

def create_full_dea_data(dhead, group,  drange, pyear):
    """
    convert week time rdb data files into a long term data fits files
    input:  dhead   --- data file name header
            group   --- group name
            drange  --- deahk data number list
            pyear   --- year to create the fits data
    output: <data_dir>/deahk<#>_data.fits
    """
#
#--- set name; they may not be countinuous
#
    name_list = []
    for k in drange:
        dname = 'deahk' + str(k)
        name_list.append(dname)
#
#--- how may dea entries
#
    ntot = len(drange)
#
#--- read data
#
    dfile = dhead + str(pyear) + '.rdb'
    data  = mcf.read_data_file(dfile)
    if len(data) < 1:
        print("No Data")
        return False
#
#--- starting time/stopping time and how many columns in the data
#
    atemp = re.split('\s+', data[0])
    tot   = len(atemp)
    start = float(atemp[0])

    xtemp = re.split('\s+', data[-1])
    stop = float(xtemp[0])
#
#--- separate each column into a list
#
    dlist = []              #--- will keep the lists of daily avg of each columns
    for k in range(0, tot):
        dlist.append([])

    for ent in data:
        atemp = re.split('\s+', ent)
        if len(atemp) < tot:
            continue

        for k in range(0, tot):
            dlist[k].append(float(atemp[k]))
#
#--- each fits file has 15 entries, but a half of them are dummy entries
#
    mstop = 1
    dlen = len(dlist[0])
    odir = deposit_dir + 'Deahk_save/' +  group 
    cmd  = 'mkdir -p ' + odir
    os.system(cmd)
    for k in range(0, ntot):
        msid = name_list[k]
        print('MSID:  ' + msid)

        fits = odir + '/' + msid  + '_full_data_' + str(pyear) + '.fits'
        cols  = ['time', msid]
        cdata = [dlist[0], dlist[k+1]]

        ecf.create_fits_file(fits, cols, cdata)

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

    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = ''

    process_dea_data_full(year)
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")