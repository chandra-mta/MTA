#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#   update_data_files.py: update/create ACIS count rate data sets                   #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           Last Update: Apr 04, 2019                                               #
#                                                                                   #
#####################################################################################

import os
import os.path
import sys
import re
import string
import random
import time
import operator
import math
import numpy
import pyfits
import unittest
#
#--- reading directory list
#-
path = '/data/mta/Script/ACIS/Count_rate/Scripts3.6/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions  as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)

#------------------------------------------------------------------------------------------
#--- update_data_files: main function to run all function to create/update ACIS Dose Plots
#-----------------------------------------------------------------------------------------

def update_data_files():
    """
    main function to run all function to create/update ACIS Dose Plots
    input:  none, but data are extracted according to current date
    output: all data, plots, and html 
    """
    (uyear, umon, mon_name) = check_date()          #--- mon_name is this month's data/plot directory
    dir_save = [mon_name]
#
#--- ACIS count rate data
#
    data_list = get_data_list()

    for dfile in data_list:
#
#--- check when the data is created
#
        (tyear, tmonth, tdate) = find_date_obs(dfile)
        if tyear == 1900:
            continue
#
#--- choose an appropriate output directory
#
        cmonth    = mcf.change_month_format(tmonth)    #--- convert digit to letter
        ucmon     = cmonth.upper()
        tmon_name = web_dir + '/' + ucmon + str(tyear)
#
#--- if the directory is not the current output directory (mon_name), add to dir_list
#
        chk = 0
        for test in dir_save:
            if tmon_name == test:
                chk = 1
                break
        if chk == 0:
            dir_save.append(tmon_name)
#
#--- now actually extract data and update/create the count rate data
#
        extract_data(dfile, tmon_name)
#
#--- if date is before Nov 2018, extract ephin data
#
        if (tyear == 2018) and (tmonth < 11):
            ephin_data(dir_save)

        elif tyear < 2018:
            ephin_data(dir_save)
#
#-- clean the data files
#
    for ent in dir_save:
        cleanUp(ent)

    return dir_save

#----------------------------------------------------------------------------------------
#-- ephin_data: extract ephin data                                                     --
#----------------------------------------------------------------------------------------

def ephin_data(dir_save):
    """
    extract ephin data
    input:  dir_save    --- a list of directory
    output: <out_dir>/ephin_data --- ephin data (300 sec accumulation)
    Note: EPHIN data is not available after Nov 2018
    """
    data_list = get_ephin_list()

    for ifile in data_list:
        try:
            (tyear, tmonth, tdate) = find_date_obs(ifile)
            if tyear == 1900:
                continue
    
            cmonth    = mcf.change_month_format(tmonth)
            ucmon     = cmonth.upper()
            tmon_name = web_dir + '/' + ucmon + str(tyear)
    
            chk = 0
            for test in dir_save:
                if tmon_name == test:
                    chk = 1
                    break

            if chk == 0:
                dir_save.append(tmon_name)
    
            extract_ephin_data(ifile, tmon_name)
       except:
           pass

#----------------------------------------------------------------------------------------
#--- check_date: check wether there is an output directory and if it is not, create one 
#---------------------------------------------------------------------------------------

def check_date():
    """
    check wether there is an output directory and if it is not, create one
    input:  none
    output: year   --- the current year
            mon    --- the current month
            mdir   --- the current output direcotry 
    """
#
#--- find today's date
#
    out   = time.strftime('%Y:%j:00:00:00', time.gmtime())
    stime = Chandra.Time.DateTime(out).secs)
#
#--- find 10 days ago and create the output directory based on that date
#
    s10   = stime - 10 * 86400.0
    out   = mcf.convert_date_format(s10, ifmt='chandra', ofmt='%Y:%m:%d')
    atemp = re.split(':', out)
    year  = int(float(atemp[0]))
    mon   = int(float(atemp[1]))
    lmon  = mcf.change_month_format(mon)
    mdir  =  web_dir  + lmon.upper() + str(year)

    if not os.path.isdir(mdir)
        cmd   = 'mkdir -p ' + mfile
        os.system(cmd)
    
    return (year, mon, mdir)

#---------------------------------------------------------------------------------------
#-- get_data_list: compare the current input list to the old one and select data       -
#---------------------------------------------------------------------------------------

def get_data_list():
    """
    compare the current input list to the old one and select out the data which are not used
    input:  house_keeping/old_file_list --- previous data list
            house_keeping/bad_fits_file --- bad fits data list
            the data are read from /dsops/ap/sdp/cache/*/acis/*evt1.fits (if it is an actual run)

    output: input_data --- the data list
    """
#
#--- create a current data file list
#
    cmd = 'ls -d  /dsops/ap/sdp/cache/*/acis/*evt1.fits > ' + zspace
    os.system(cmd)
#
#--- use only non-calibration data files
#
    data = mcf.read_data_file(zspace, remove=1)

    file_list = find_obs_data_files(data)
#
#--- read the old file list
#
    ifile    = house_keeping + 'old_file_list'
    old_list = mcf.read_data_file(ifile)
#
#--- read bad fits file list
#
    try:
        file2    = house_keeping + 'bad_fits_file'
        bad_list = mcf.read_data_file(file2)
    except:
        bad_list = []
#
#--- update "old_file_list"
#
    with  open(ifile, 'w') as fo:
        for line in file_list:
            fo.write(line + '\n')
#
#--- compara two files and select out new file names
#
    n_list = list(numpy.setdiff1d(file_list, old_list))

    if len(bad_list) > 0:
        n_list = list(numpy.setdiff1d(n_list, bad_list))

    return n_list

#---------------------------------------------------------------------------------------
#-- find_obs_data_files: choose files with only non-calibration data files            --
#---------------------------------------------------------------------------------------

def find_obs_data_files(data):
    """
    choose files with only non-calibration data files
    input:  data        --- a list of data file names
    output: file_list   --- a list of non-calibration data file

    """
    file_list = []
    for ent in data:
        atemp = re.split('acisf', ent)
        btemp = re.split('_', atemp[1])
#
#--- for the older format : acisf16218N001_evt1.fits
#--- for the new format :   acisf16218_000N001_evt1.fits
#
        try:
            val = float(btemp[0])     
            mark= int(float(val))
        except:
            ctemp = re.split('N', btemp[1])
            mark  = int(float(ctemp[0]))

        if mark < 50000:
            file_list.append(ent)

    return file_list

#---------------------------------------------------------------------------------------
#--- find_date_obs: find observation time                                            ---
#---------------------------------------------------------------------------------------

def find_date_obs(ifile):
    """ 
    find observation time
    input: file --- input fits file name
    output: year, month, and date
    """
    try:
        dout  = pyfits.open(ifile)
        date  = dout[0].header['DATE-OBS']

        atemp = re.split('T', date)
        btemp = re.split('-', atemp[0])
    
        year  = int(btemp[0])
        month = int(btemp[1])
        date  = int(btemp[2])
    
        return (year, month, date)
    except:
        return (1900, 1, 1)

#---------------------------------------------------------------------------------------
#--- extract_data: extract time and ccd_id from the fits file and create count rate data
#---------------------------------------------------------------------------------------

def extract_data(file, out_dir ):
    """
    extract time and ccd_id from the fits file and create count rate data
    input:  file    --- fits file data
            out_dir --- the directory in which data will be saved
    output: ccd<ccd>--- 5 min accumulated count rate data file
    """
#
#--- extract time and ccd id information from the given file
#
    data      = pyfits.getdata(file, 0)
    time_col  = data.field('TIME')
    ccdid_col = data.field('CCD_ID')
#
#--- initialize
#
    diff  = 0
    chk   = 0
    ccd_c = [0  for x in range(0, 10)]
    ccd_h = [[] for x in range(0, 10)]
#
#--- check each line and count the numbers of ccd in the each 300 sec intervals
#
    for k in range(0, len(time_col)):
        try:
            ftime  = float(time_col[k])
            ccd_id = int(ccdid_col[k])
        except:
            continue

        if ftime > 0:
            if chk == 0:
                ccd_c[ccd_id] += 1
                stime = ftime
                diff   = 0
                chk    = 1
            elif diff >= 300.0:
#
#--- print out counts per 300 sec 
#
                for i in range(0, 10):
                    line = str(stime) + '\t' + str(ccd_c[i]) + '\n'
                    ccd_h[i].append(line)
#
#--- re initialize for the next round
#
                    ccd_c[i] = 0

                ccd_c[ccd_id] += 1
                stime = ftime
                diff   = 0
                chk    = 0
#
#--- accumurate the count until the 300 sec interval is reached
#
            else:
                diff = ftime - stime
                ccd_c[ccd_id] += 1
#
#--- for the case the last interval is less than 300 sec, 
#--- estimate the the numbers of hit and adjust
#
    if diff > 0 and diff < 300:
        ratio = 300.0 / diff

        for i in range(0, 10):
            ccd_c[i] *= ratio

            line = str(stime) + '\t' + str(ccd_c[i]) + '\n'
            ccd_h[i].append(line)

    for i in range(0, 10): 
        ifile = out_dir + '/ccd' + str(i)
        with open(ifile, 'a') as fo:
            for ent in ccd_h[i]:
                fo.write(ent)

#---------------------------------------------------------------------------------------
#--- get_ephin_list: create an ephin data list                                       ---
#---------------------------------------------------------------------------------------

def get_ephin_list():

    """
    create an ephin data list
    input: ephin data ---  /dsops/ap/sdp/cache/*/ephin/*lc1.fits
    output: input_data_list: a list of ephin data file which is not extract
    """
    cmd = 'ls -d  /dsops/ap/sdp/cache/*/ephin/*lc1.fits > '
    cmd = cmd + house_keeping + '/ephin_dir_list'
    os.system(cmd)
#
#--- get a list of the current entries
#
    ifile = house_keeping + '/ephin_dir_list'
    data  = mcf.read_data_file(ifile)
#
#--- read the list which we read the last time
#
    ifile = house_keeping + '/ephin_old_dir_list'
    old   = mcf.read_data_file(ifile)
#
#--- find the last entry of the list
#
    last_entry = old[len(old)-1]
#
#--- select data which is new
#
    input_data_list = []
    chk = 0
    for ent in data:
        if chk == 0:
            if ent == last_entry:
                chk = 1
        else:
            input_data_list.append(ent)
#
#--- replace the old list with the new one
#
    ifile = house_keeping + '/ephin_dir_list'
    if os.path.isfile(ifile):
        cmd = 'mv ' + house_keeping + '/ephin_dir_list ' + house_keeping + '/ephin_old_dir_list'
        os.system(cmd)

    return input_data_list

#---------------------------------------------------------------------------------------
#-- extract_ephin_data: extract ephine data from a given data file name and save it in out_dir 
#---------------------------------------------------------------------------------------

def extract_ephin_data(ifile, out_dir):

    """
    extract ephine data from a given data file name and save it in out_dir
    input:  ifile   --- ephin data file name
            out_dir --- directory which the data is saved
    output: <out_dir>/ephin_data --- ephin data (300 sec accumulation) 
    """
#
#--- extract time and ccd id information from the given file
#
    data      = pyfits.getdata(ifile, 1)
    time_r    = data.field("TIME")
    scp4_r    = data.field("SCP4")
    sce150_r  = data.field("SCE150")
    sce300_r  = data.field("SCE300")
    sce1500_r = data.field("SCE1300")
#
#--- initialize
#
    diff       = 0
    chk        = 0
    ephin_data = []
#
#--- sdata[0]: scp4, sdata[1]: sce150, sdata[2]: sce300, and sdata[3]: sce1300
#
    sdata = [0 for x in range(0, 4)]
#
#--- check each line and count the numbers of ccd in the each 300 sec intervals
#
    for k in range(0, len(time_r)):
        try:
            ftime  = float(time_r[k])
            val1   = float(scp4_r[k])
            val2   = float(sce150_r[k])
            val3   = float(sce300_r[k])
            val4   = float(sce1500_r[k])
        except:
            continue

        if ftime > 0:
            if chk == 0:
                sdata[0] += val1
                sdata[1] += val2
                sdata[2] += val3
                sdata[3] += val4

                stime = ftime
                diff   = 0
                chk    = 1

            elif diff >= 300.0:
#
#--- print out counts per 300 sec 
#
                line = str(stime) + '\t' 
                for j in range(0, 4):
                    line = line + str(sdata[j]) + '\t'
                    sdata[j] = 0
                line = line + '\n'
                ephin_data.append(line)
                chk = 0
#
#--- re initialize for the next round
#
                try:
                    val1   = float(scp4_r[k])
                    val2   = float(sce150_r[k])
                    val3   = float(sce300_r[k])
                    val4   = float(sce1500_r[k])
                except:
                    continue

                sdata[0] += val1
                sdata[1] += val2
                sdata[2] += val3
                sdata[3] += val4

                stime     = ftime
                diff      = 0
#
#--- accumurate the count until the 300 sec interval is reached
#
            else:
                diff = ftime - stime
                try:
                    val1   = float(scp4_r[k])
                    val2   = float(sce150_r[k])
                    val3   = float(sce300_r[k])
                    val4   = float(sce1500_r[k])
                except:
                    continue

                sdata[0] += val1
                sdata[1] += val2
                sdata[2] += val3
                sdata[3] += val4
#
#--- for the case the last interval is less than 300 sec, 
#--- estimate the the numbers of hit and adjust
#
    if diff > 0 and diff < 300:

        line = str(stime) + '\t' 

        ratio = 300.0 / diff
        for j in range(0, 4):
            var  = sdata[j] * ratio
            line = line + str(var) + '\t'

        line = line + '\n'
        ephin_data.append(line)

    ifile = out_dir + '/ephin_rate'
    with open(ifile, 'a') as fo:
        for ent in ephin_data:
            fo.write(ent)

#---------------------------------------------------------------------------------------
#-- cleanUp: sort and remove duplicated lines in all files in given data directory   ---
#---------------------------------------------------------------------------------------

def cleanUp(cdir):
    """
    sort and remove duplicated lines in all files in given data directory
    input       cdir        --- directory name
    output      cdir/files  --- cleaned up files

    """
    if os.listdir(cdir) != []:
        cmd = 'ls ' + cdir + '/* > ' +  zspace
        os.system(cmd)
        data = mcf.read_data_file(zspace, remove=1)

        for ifile in data:
#
#--- avoid html and png files
#
            try:
                m = re.search('\.', ifile)
                if m is None:
                    mcf.remove_duplicated_lines(ifile, chk = 1, srt=1)
            except:
                pass

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions

    """
    def test_check_date(self):

        out = check_date()
        print("YEAR: MON:  Dir: " + str(out))

#------------------------------------------------------------

if __name__ == "__main__":

        unittest.main()
