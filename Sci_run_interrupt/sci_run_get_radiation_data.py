#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       sci_run_get_radiation_data.py: get NOAA data for radiaiton plots                #
#                                                                                       #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 09, 2021                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import time
import Chandra.Time
import random

#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)


#-----------------------------------------------------------------------------------------------
#--- sci_run_get_radiation_data: extract radiation data                                      ---
#-----------------------------------------------------------------------------------------------

def sci_run_get_radiation_data():
    """
    create ACE database
    input:  none but read from:
            /data/mta4/Space_Weather/ACE/Data/ace_7day_archive
    output: <data_dir>/rad_dta<year>
    """
#
#--- find today's date
#
    today = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    atemp = re.split(':', today)
    year  = int(float(atemp[0]))
    yday  = int(float(atemp[1]))
#
#--- if this is 1st of the year, start from the last day of the last year
#
    oyear = year
    if yday == 1:
        oyear = year -1
#
#--- read the current data file and find the last entry date/time
#
    ifile = data_dir + 'rad_data' + str(oyear)
    cdata = mcf.read_data_file(ifile)
    try:
        atemp = re.split('\s+', cdata[-1])
        lyear = int(float(atemp[0]))
        ltime = get_data_time(cdata[-1])
    except:
        lyear = oyear
        ltime = 0.0
#
#--- read  new data from noaa site via ace site
#
    ifile = '/data/mta4/Space_Weather/ACE/Data/ace_7day_archive'
    data  = mcf.read_data_file(ifile)
#
#--- set two data lines; one for this year and another for the potential following year
#
    oline = ''
    nline = ''
    for ent in data:
        atemp = re.split('\s+', ent)
        tyear = int(float(atemp[0]))

        stime = get_data_time(ent)

        if stime > ltime:
            if tyear == lyear:
                oline = oline + ent + '\n'
#
#--- a new year started
#
            elif tyear > lyear:
                nline = nline + ent + '\n'
#
#--- print out the data
#
    if len(oline) > 0:
        ofile = data_dir + 'rad_data' + str(oyear)
        with open(ofile, 'a') as fo:
            fo.write(oline)

    if len(nline) > 0:
        ofile = data_dir + 'rad_data' + str(year)
        with open(ofile, 'w') as fo:
            fo.write(oline)

#--------------------------------------------------------------------
#-- get_data_time: find time of the data line given in seconds from 1998.1.1
#--------------------------------------------------------------------

def get_data_time(line):
    """
    find time of the data line given in seconds from 1998.1.1
    input:  line    --- data line with the first few entries are time related
    output: ltime   --- time in seconds from 1998.1.1
    """

    atemp = re.split('\s+', line)

    dyear = int(float(atemp[0]))
    mon   = int(float(atemp[1]))
    day   = int(float(atemp[2]))
    hh    = int(float(atemp[3][0]+atemp[3][1]))
    mm    = int(float(atemp[3][2]+atemp[3][3]))

    ltime = convert_to_ctime(dyear, mon, day, hh, mm, 0)

    return ltime

#--------------------------------------------------------------------
#--- convert_to_ctime: convert time in Chandra time                --
#--------------------------------------------------------------------

def convert_to_ctime(year, mon, day, hh, mm, ss):
    """
    convert time in Chandra time
    input:  year    --- year
            mon     --- month
            day     --- mday
            hh      --- houris
            mm      --- minutes
            ss      --- seconds
    output: ctime   --- chandra time; seconds from 1998.1.1
    """

    ctime = str(year) + ':' + mcf.add_leading_zero(mon) + ':' + mcf.add_leading_zero(day) 
    ctime = ctime     + ':' + mcf.add_leading_zero(hh)  + ':' + mcf.add_leading_zero(mm)
    ctime = ctime     + ':' + mcf.add_leading_zero(ss)

    ctime = time.strftime('%Y:%j:%H:%M:%S', time.strptime(ctime, '%Y:%m:%d:%H:%M:%S'))
    ctime = Chandra.Time.DateTime(ctime).secs

    return ctime

#--------------------------------------------------------------------

if __name__ == '__main__':

    sci_run_get_radiation_data()


