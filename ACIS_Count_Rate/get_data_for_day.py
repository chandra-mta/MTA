#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#       get_data_for_day.py: get a month amount of data and update data files       #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           Last Update: Mar 02, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import os.path
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits
import time
import Chandra.Time
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Count_rate/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions       as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------
#--- get_data_for_day: extract one month amount of data and update data files         
#-------------------------------------------------------------------------------

def get_data_for_day(year, month, day=''):
    """
    extract one month amount of data and update data files
    input:  year    --- year of the data
            month   --- month of the data
    output: updated data files:
                <MMM><YYYY>/ccd# 
                <MMM><YYYY>/ephin_data
        Note: there is no ephin data after 2018 Nov
    """
#
#--- if the date is given...
#
    chk = 0
    if year != '':
        lmon = mcf.add_leading_zero(month)
        lday = mcf.add_leading_zero(day)
        if day != '':
            start = str(year) + ':' + lmon + ':' + lday + ':00:00:00'
            stop  = str(year) + ':' + lmon + ':' + lday + ':23:59:59'
#
#-- if the day part is not given, compute for the entire month
#
        else:
            nyear = year
            nmon  = mon + 1
            if nmon > 12:
                nyear += 1
                nmon   = 1
            nmon = mcf.add_leading_zero(nmon)

            start = str(year)  + ':' + lmon + ':' + ':01:00:00:00'
            stop  = str(nyear) + ':' + nmom + ':' + ':01:00:00:00'
            chk   = 1

        start = mcf.convert_date_format(start, ifmt='%Y:%m:%d:%H:%M:%S', ofmt='chandra')
        stop  = mcf.convert_date_format(stop,  ifmt='%Y:%m:%d:%H:%M:%S', ofmt='chandra')
#
#--- if the year/month are not given, extract data of the day before
#
    if year == '':
        out   = time.strftime('%Y:%j:00:00:00', time.gmtime())
        stop  = Chandra.Time.DateTime(out).secs
        start = stop - 86400.0
        out   = mcf.convert_date_format(start, ifmt='chandra', ofmt='%Y:%m')
        out   = re.split(':', out)
        year  = int(float(out[0]))
        month = int(float(out[1]))
#
#--- set output directory name
#
    cmonth   = mcf.change_month_format(month)           #--- convert digit to letter month
    ucmon    = cmonth.upper()
    dir_name = data_dir + '/' + ucmon + str(year) + '/'  #--- output directory

    if not os.path.isdir(dir_name):
        cmd = 'mkdir -p ' + dir_name
        os.system(cmd)
#
#--- if the entire month data needs to be extracted, remove all previous data
#
    if chk == 1:
        cmd = 'rm -rf ' + dir_name + '/ccd*'
        os.system(cmd)
#
#--- get acis count rate data
#
    extract_acis_count_rate(start, stop, dir_name)
#
#--- get ephin rate data; no data after Nov 2018
#
    if year < 2018:
        get_ephin_data(start, stop, dir_name)

    elif (year == 2018) and (month < 11):
        get_ephin_data(start, stop, dir_name)
#
#-- clean the data files
#
    cleanUp(dir_name)

#------------------------------------------------------------------------------
#-- extract_acis_count_rate: extract acis count rate data                     --
#-------------------------------------------------------------------------------

def extract_acis_count_rate(start, stop, dir_name):
    """
    extract acis count rate data
    input:  year        --- year    
            month       --- month
            dir_name    --- output dir name
    output: <dir_name>/ccd<#ccd>
    """
#
#--- make a list of data fits file
#
    data_list = get_data_list_from_archive(start, stop)

    if len(data_list) == 0:
        print("No data")
        exit(1)

    for ifile in data_list:
#
#--- extract the fits file with arc5gl
#
        line = 'operation=retrieve\n'
        line = line + 'dataset=flight\n'
        line = line + 'detector=acis\n'
        line = line + 'level=1\n'
        line = line + 'filetype=evt1\n'
        line = line + 'filename=' + ifile + '\n'
        line = line + 'go\n'
    
        out = mcf.run_arc5gl_process(line)

        cmd = 'gzip -d ' + ifile + '.gz'
        os.system(cmd)
#
#--- extract data and update/create the count rate data
#
        print("Extracting: " + ifile)
        extract_data(ifile, dir_name)

        mcf.rm_files(ifile)

#-------------------------------------------------------------------------------
#-- get_data_list_from_archive: compare the current input list to the old one and select data 
#-------------------------------------------------------------------------------

def get_data_list_from_archive(start, stop):
    """
    compare the current input list to the old one and select out the data which are not used
    input:  start       --- start time in seconds from 1998.1.1
            stop        --- stop time in seconds from 1998.1.1
    output: file_list   --- a list of acis evt1 file list
    """
#
#--- create data list with arc5gl
#
    line = 'operation=browse\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=evt1\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'

    data = mcf.run_arc5gl_process(line)
#
#--- choose files with only non-calibration data
#
    file_list = []
    for ent in data:
        mc = re.search('acisf', ent)
        if mc is None:
            continue 

        ftemp = re.split('\s+', ent)
        atemp = re.split('acisf', ftemp[0])
        btemp = re.split('_', atemp[1])
        ctemp = re.split('N', btemp[0])
        mark  = int(ctemp[0])

        if mark < 50000:
            file_list.append(ftemp[0])

    return file_list

#---------------------------------------------------------------------------------
#--- extract_data: extract time and ccd_id from the fits file and create count rate data
#---------------------------------------------------------------------------------

def extract_data(fits, out_dir):
    """
    extract time and ccd_id from the fits file and create count rate data
    input:  fits    --- fits file data
            out_dir --- the directory in which data will be saved
    output: ccd<ccd>--- 5 min accumulated count rate data file
    """
#
#--- find the last entry times
#
    t_list = [0 for x in range(0, 10)]
    for k in range(0, 10):
        ifile = out_dir + 'ccd' + str(k)
        if os.path.isfile(ifile):
            data      = mcf.read_data_file(ifile)
            if len(data) > 0:
                atemp     = re.split('\s+', data[-1])
                t_list[k] = float(atemp[0])
#
#--- extract time and ccd id information from the given file
#
    data      = pyfits.getdata(fits, 0)
    time_col  = data.field('TIME')
    ccdid_col = data.field('CCD_ID')
#
#--- initialize
#
    diff  = 0
    chk   = 0
    ccd_c = [0  for x in range(0, 10)]
    ccd_h = [[] for x in range(0, 10)]
    ftime = -999
#
#--- check each line and count the numbers of ccd in the each 300 sec intervals
#
    for k in range(0, len(time_col)):
        try:
            stime  = float(time_col[k])
            ccd_id = int(float(ccdid_col[k]))
            if stime <= t_list[ccd_id]:
                continue
        except:
            continue

        if ftime < 0:
            ftime = stime
            diff  = 0
        else:
            diff  = stime - ftime

        if diff >= 300.0:
#
#--- save counts after accumunrating for 300 sec 
#
            for i in range(0, 10):
                line = str(ftime) + '\t' + str(ccd_c[i]) + '\n'
                ccd_h[i].append(line)
#
#--- reinitialize for the next round
#
                ccd_c[i] = 0

            ccd_c[ccd_id] += 1
            ftime  = stime
            diff   = 0
#
#--- accumurate the count until the 300 sec interval is reached
#
        else:
            ccd_c[ccd_id] += 1
#
#--- for the case the last interval is less than 300 sec, 
#--- estimate the the numbers of hit and adjust
#
    if diff > 0 and diff < 300:
        ratio = 300.0 / diff

        for i in range(0, 10):
            ccd_c[i] *= ratio
            ccd_c[i] = int(ccd_c[i])

            line = str(stime) + '\t' + str(ccd_c[i]) + '\n'
            ccd_h[i].append(line)
#
#--- print out the results
#
    for i in range(0, 10):
        ofile = out_dir + '/ccd' + str(i)
        with open(ofile, 'a') as fo:
            for ent in ccd_h[i]:
                fo.write(ent)

#-------------------------------------------------------------------------------
#-- get_ephin_data: extract ephin data and create ephin_data file             --
#-------------------------------------------------------------------------------

def get_ephin_data(start, stop, out_dir):
    """
    extract ephin data and create ephin_data file
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            out_dir --- output directory
    output: out_dir/ehin_data
    """
#
#--- first create a list of ephin fits file for the month
#
    line  = 'operation=browse\n'
    line  = line + 'dataset=flight\n'
    line  = line + 'detector=ephin\n'
    line  = line + 'level=1\n'
    line  = line + 'filetype=ephrates\n'
    line  = line + 'tstart=' + start + '\n'
    line  = line + 'tstop='  + stop  + '\n'
    line  = line + 'go\n'

    data  = mcf.run_arc5gl_process(line)
#
#--- extract ephin fits file one by one and analyze
#
    for ent in data:
        mc = re.search('fits', ent)
        if mc is not None:
            atemp = re.split('\s+', ent)
            fits  = atemp[0]
            line  = 'operation=retrieve\n'
            line  = line + 'dataset=flight\n'
            line  = line + 'detector=ephin\n'
            line  = line + 'level=1\n'
            line  = line + 'filetype=ephrates\n'
            line  = line + 'filename=' + fits + '\n'
            line  = line + 'go\n'
        
            chk   = mcf.run_arc5gl_process(line)

            cmd = 'gzip -d *fits.gz'
            os.system(cmd)
    
            extract_ephin_data(fits, out_dir)

#-------------------------------------------------------------------------------
#-- extract_ephin_data: extract ephine data from a given data file name and save it in out_dir
#-------------------------------------------------------------------------------

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
    ephin_data = []
#
#--- sdata[0]: scp4, sdata[1]: sce150, sdata[2]: sce300, and sdata[3]: sce1300
#
    sdata = [0 for x in range(0,4)]
    ftime = -999
#
#--- check each line and count the numbers of ccd in the each 300 sec intervals
#
    for k in range(0, len(time_r)):
        try:
            stime  = float(time_r[k])
            if stime <= 0:
                continue
            sd0    = float(scp4_r[k])
            sd1    = float(sce150_r[k])
            sd2    = float(sce300_r[k])
            sd3    = float(sce1500_r[k])
        except:
            continue

        if ftime < 0:
            ftime = stime
            diff  = 0
        else:
            diff  = stime - ftime

        if diff >= 300.0:
#
#--- save counts per 300 sec 
#
            line = str(ftime)
            for j in range(0, 4):
                line = line + '\t%4.4f' % (round(sdata[j],4))
            line = line + '\n'
            ephin_data.append(line)
#
#--- re-initialize for the next round
#
            sdata[0] = sd0
            sdata[1] = sd1
            sdata[2] = sd2
            sdata[3] = sd3
            ftime    = stime
#
#--- accumurate the count until the 300 sec interval is reached
#
        else:
            sdata[0] += sd0
            sdata[1] += sd1
            sdata[2] += sd2
            sdata[3] += sd3
            diff = stime - ftime
#
#--- for the case the last interval is less than 300 sec, 
#--- estimate the the numbers of hit and adjust
#
    if (diff > 0) and (diff < 300):

        line = str(ftime)

        ratio = 300.0 / diff
        for j in range(0, 4):
            var  = sdata[j] * ratio
            line = line + '\t%4.4f' % (round(var,4))

        line = line + '\n'
        ephin_data.append(line)
#
#--- print out the data
#
    ofile = out_dir + '/ephin_rate'
    with open(ofile, 'a') as fo:
        for ent in ephin_data:
            fo.write(ent)

    mcf.rm_files(ifile)

#-------------------------------------------------------------------------------
#-- cleanUp: sort and remove duplicated lines in all files in given data directory               ---
#-------------------------------------------------------------------------------

def cleanUp(cdir):
    
    """
    sort and remove duplicated lines in all files in given data directory
    Input       cdir        --- directory name
    Output      cdir/files  --- cleaned up files

    """
    if os.path.isdir(cdir):
        cmd = 'ls ' + cdir + '/* > ' +  zspace
        os.system(cmd)
        flist = mcf.read_data_file(zspace, remove=1)
    
        for ifile in flist:
            data = mcf.read_data_file(ifile)
            if len(data) < 2:
                continue

            data = sorted(data)
            prev = data[0]
            line = data[0] + '\n'
            for comp in data[1:]:
                if comp == prev:
                    continue
                else:
                    line = line + comp + '\n'
                    prev = comp
     
            with open(ifile, 'w') as fo:
                fo.write(line)


#------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 1:
        year  = ''
        month = ''
        day   = ''

    elif len(sys.argv) == 3:
        year  = int(sys.argv[1])
        month = int(sys.argv[2])
        day   = ''

    elif len(sys.argv) == 4:
        year  = int(sys.argv[1])
        month = int(sys.argv[2])
        day   = int(sys.argv[3])

    get_data_for_day(year, month, day)


