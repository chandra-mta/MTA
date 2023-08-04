#!/proj/sot/ska3/flight/bin/python
#####################################################################################    
#                                                                                   #
#           convert_dea_data_to_fits.py: concert dea data into fits data files      #
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
#import numpy
#print(f"pathing: {sys.path}")
import astropy.io.fits  as pyfits
import Chandra.Time
import random
import getpass
#
#--- reading directory list
#
#path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
path = '/data/mta4/testDEA/Scripts/house_keeping/dir_list'
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
sys.path.append("/data/mta4/Script/Python3.10/MTA")
#
#--- import several functions
#
import mta_common_functions     as mcf  #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
#
#--- set a temporary file name
#
rtail  = int(time.time() *random.random())
zspace = '/tmp/zspace' + str(rtail)

dea_data_dir = bin_dir + 'DEA/RDB/'

#-------------------------------------------------------------------------------------------
#-- process_dea_data: convert deahk related rdb data into fits files                     ---
#-------------------------------------------------------------------------------------------

def process_dea_data(part):
    """
    convert deahk related rdb data into fits files
    input:  part    ---- indictor whether temp or elec to run;default: '' run both
            it also read from the deahk rdb files
    output: <data_dir>/deahk<#>_<period>_data.fits
    """
#
#--- dea temp
#
    if part == '' or part == 'temp':
        drange = list(range(1,14)) + list(range(15,17))
        group  = 'Deahk_temp'

        dhead  = dea_data_dir + 'deahk_temp_week'
        period = '_week'
        print("Temp Week")
        create_dea_fits_file(dhead, group, period, drange)
    
        dhead  = dea_data_dir + 'deahk_temp_short'
        period = '_short'
        print("Temp Short")
        create_dea_fits_file(dhead, group, period, drange)
    
        dhead  = dea_data_dir + 'deahk_temp_week'
        print("Temp Full")
        create_long_term_dea_data(dhead, group, drange)
#
#--- dea elec
#
    if part == '' or part == 'elec':
        drange = list(range(17,21)) + list(range(25,41))
        group  = 'Deahk_elec'

        dhead  = dea_data_dir + 'deahk_elec_week'
        period = '_week'
        print("Elec Week")
        create_dea_fits_file(dhead, group, period, drange)
    
        dhead  = dea_data_dir + 'deahk_elec_short'
        period = '_short'
        print("Elec Short")
        create_dea_fits_file(dhead, group, period, drange)
    
        dhead  = dea_data_dir + 'deahk_elec_week'
        print("Elec Full")
        create_long_term_dea_data(dhead, group, drange)

#-------------------------------------------------------------------------------------------
#-- create_dea_fits_file: convert week and short time rdb data files into fits files     ---
#-------------------------------------------------------------------------------------------

def create_dea_fits_file(dhead, group, period, drange):
    """
    convert week and short time rdb data files into fits files
    input:  dhead   --- data file name header
            group   --- group name
            period  --- week or short
            drange  --- deahk data number list
    output: <data_dir>/deahk<#>_week_data.fits
            <data_dir>/deahk<#>_short_data.fits
    """
#
#--- find today date in seconds from 1998.1.1
#
    today = time.strftime("%Y:%j:00:00:00", time.gmtime())
    atemp = re.split(':', today)
    tyear = int(atemp[0])
    today = Chandra.Time.DateTime(today).secs
#
#--- how many dea entries
#
    ntot = len(drange)
#
#--- set name; they may not be countinuous
#
    name_list = []
    for k in drange:
        dname = 'deahk' + str(k)
        name_list.append(dname)
#
#--- set data period
#
    cut = 0
    if period == '_short':
        cut    = today - 31536000.0     #--- a year ago
    elif period == '_week':
        cut    = today - 604800.0       #--- two weeks ago

    lcut   = Chandra.Time.DateTime(cut).date
    atemp  = re.split(':', lcut)
    lyear  = int(atemp[0])
#
#--- read data
#
    if period == '_short':
        dfile = dhead + '.rdb'
        data = mcf.read_data_file(dfile)

    elif period == '_week':
        data = []
        for pyear in range(lyear, tyear+1):
            dfile = dhead +  str(pyear) +'.rdb'
            out   = mcf.read_data_file(dfile)
            data  = data + out
#
#--- how many columns in the data
#
    tot  = len(re.split('\s+', data[0]))
#
#--- separate each column into a list
#
    dlist = []
    for k in range(0, tot):
        dlist.append([])

    chk = 0
    for ent in data:
        atemp = re.split('\s+', ent)
        if float(atemp[0]) > cut and len(atemp) == tot:
            chk += 1
            for k in range(0, tot):
                dlist[k].append(atemp[k])
#
#--- if no new data, stop
#
    if chk == 0:
        if period == '_short':
            nline = 'No new data for Short term'
        else:
            nline = 'No new data for Week data'
        return nline
#
#--- each fits file has 15 entries, but a half of them are dummy entries
#
    mstop = 1
    for k in range(0, ntot):
        msid = name_list[k]

        print("MSID: " + msid)

        fits = data_dir + group + '/' + msid + period + '_data.fits'
        cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower',\
                 'yupper', 'rlower', 'rupper', 'dcount',\
                 'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper', 'state']

        mstart = mstop
        mstop  = mstart + 5
#
#--- the following quantities are not in the database; add default values
#
        tlen   = len(dlist[0])
        ylr    = [0] * tlen
        yur    = [0] * tlen
        rlr    = [0] * tlen
        rur    = [0] * tlen
        yl     = [-9e9] * tlen
        yu     = [ 9e9] * tlen
        rl     = [-9e9] * tlen
        ru     = [ 9e9] * tlen
        dc     = [-999] * tlen
        state  = ['none'] * tlen

        cdata  = [dlist[0]]
        cdata  = cdata + dlist[mstart:mstop] + [ylr, yur, rlr, rur, dc, yl, yu, rl, ru, state]
#
#--- create/update the fits file
#
        cmd = 'chmod 766 ' + fits
        os.system(cmd)
        cmd = 'rm -rf ' + fits
        os.system(cmd)

        ecf.create_fits_file(fits, cols, cdata)

    if period == '_short':
        nline = 'short data fits file update'
    else:
        nline = 'week data fits file update'

    return nline

#-------------------------------------------------------------------------------------------
#-- create_long_term_dea_data: convert week time rdb data files into a long term data fits files 
#-------------------------------------------------------------------------------------------

def create_long_term_dea_data(dhead, group,  drange):
    """
    convert week time rdb data files into a long term data fits files
    input:  dhead   --- data file name header
            group   --- group name
            period  --- week or short
            drange  --- deahk data number list
    output: <data_dir>/deahk<#>_data.fits
    """
#
#--- find today date in seconds from 1998.1.1
#
    today = time.strftime("%Y:%j:00:00:00", time.gmtime())
    atemp = re.split(':', today)
    tyear = int(atemp[0])
    today = Chandra.Time.DateTime(today).secs
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
#--- checking the last entry date 
#
    efits = data_dir + group + '/' + name_list[0] + '_data.fits'

    if os.path.isfile(efits):
        ltime = ecf.find_the_last_entry_time(efits)
        try:
            ltime = find_starting_of_the_day(ltime) 
            out   = Chandra.Time.DateTime(ltime)
            atemp = re.split(':', out)
            syear = int(atemp[0])
            lchk  = 1
        except:
            ltime = 52185599.0
            syear = 1999
            lchk  = 0
    else:
        ltime = 52185599.0
        syear = 1999
        lchk  = 0
#
#--- read data
#
    fchk = 0
    for pyear in range(syear, tyear+1):
        dfile = dhead + str(pyear) + '.rdb'
        data  = mcf.read_data_file(dfile)
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
        if fchk == 0:               #--- initialize once at the beginning of the loop
            dlist = []              #--- will keep the lists of daily avg of each columns
            for k in range(0, tot):
                dlist.append([])
            fchk = 1

        dsum  = []                  #--- will keep the sums of each columns for a given 
                                    #--- time interval (a day)
        for k in range(0, tot):
            dsum.append(0)

        chk = 0
        cnt = 0
        ntime = ltime + 86400.0

        while ntime < start:
            ltime = ntime 
            ntime = ltime + 86400.0
        tlist = []

        dlen = len(data)

        for ent in data:
            atemp = re.split('\s+', ent)
            ftime = float(atemp[0])
            if ftime >= ltime:

                chk += 1
                if ftime < ntime and len(atemp) == tot:
                    tlist.append(ftime)
                    for k in range(0, tot):
                        dsum[k] += float(atemp[k])
                        cnt += 1
                else:
                    if cnt == 0 or len(tlist) == 0:
                        ltime = ntime
                        ntime = ltime + 86400.0
                        continue
#
#--- take mid point for the time and take averages for the other quantities
#
                    dlist[0].append(tlist[int(0.5*len(tlist))])
                    for k in range(1, tot):
    
                        dlist[k].append(dsum[k] / cnt)
                        dsum[k] = 0

                    ltime = ntime
                    ntime = ltime + 86400.0
                    tlist = []
                    cnt   = 0
#
#--- if no new data, stop
#
    if chk == 0:
        return 'No new data'
#
#--- each fits file has 15 entries, but a half of them are dummy entries
#
    mstop = 1
    for k in range(0, ntot):
        msid = name_list[k]

        print('MSID:  ' + msid)

        fits = data_dir + group + '/' + msid  + '_data.fits'
        cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower',\
                 'yupper', 'rlower', 'rupper', 'dcount',\
                 'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper', 'state']

        mstart = mstop
        mstop  = mstart + 5
#
#--- the following quantities are not in the database; add default values
#
        tlen   = len(dlist[0])
        ylr    = [0] * tlen
        yur    = [0] * tlen
        rlr    = [0] * tlen
        rur    = [0] * tlen
        yl     = [-9e9] * tlen
        yu     = [ 9e9] * tlen
        rl     = [-9e9] * tlen
        ru     = [ 9e9] * tlen
        dc     = [-999] * tlen
        state  = ['none'] * tlen

        cdata  = [dlist[0]]
        cdata  = cdata + dlist[mstart:mstop] + [ylr, yur, rlr, rur, dc, yl, yu, rl, ru, state]
#
#---  creat new fits file
#
        if lchk == 0:
            ecf.create_fits_file(fits, cols, cdata)
#
#--- append to the existing fits file
        else:
            ecf.update_fits_file(fits, cols, cdata)

    return 'New data added'

#-------------------------------------------------------------------------------------------
#-- find_starting_of_the_day: set the time to the beginning of the day                   ---
#-------------------------------------------------------------------------------------------

def find_starting_of_the_day(time):
    """
    set the time in seconds from 1998.1.1 to the beginning of the day 
    input:  time    --- time in seconds from 1998.1.1
    output: time    --- time in seconds from 1998.1.1 but the time is 00:00:00
    """
    out   = Chandra.Time.DateTime(time).date
    atemp = re.split(':', out)
    dtime = atemp[0] + ':' + atemp[1] + ':00:00:00'
    time  = Chandra.Time.DateTime(dtime).secs

    return time

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
        part = sys.argv[1]
    else:
        part = ''

    process_dea_data(part)
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")