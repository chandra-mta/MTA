#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#           create_5min_avg_data.py: create five min average data file                              #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Mar 03, 2021                                                               #
#                                                                                                   #
#####################################################################################################

import sys
import os
import string
import re
import numpy
import getopt
import random
import time
import Chandra.Time
#import Ska.engarchive.fetch as fetch
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Focal/Script/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#
step  = 600.0   #---- 5 min step
hstep = 0.5 * step

#-------------------------------------------------------------------------------
#-- create_5min_avg_data: create data file contains daily max value of focal plane temp 
#-------------------------------------------------------------------------------

def create_5min_avg_data(year):
    """
    create data file contains daily max value of focal plane temp 
    input:  all --- default: 0 extract data only this year. otherwise start from year 2000 to current
    output: <data_dir>/long_term_max_data format: <ctime>    <max focal temp> <crat> <crbt>
    """
#
#--- find today's date
#
    if year == '':
        stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
        today = Chandra.Time.DateTime(stday).secs
#
#--- find the current year
#
        atemp = re.split(':', stday)
        year  = int(atemp[0])
#
#--- read data of each year
#
    dfile = data_dir + '/full_focal_plane_data_' + str(year)
    data  = mcf.read_data_file(dfile)

    f_list = []
    a_list = []
    b_list = []
#
#--- set starting interval; the day after the last entry date
#
    start  = set_start(data)
    stop   = start + step
    sline  = ''

    for ent in data:
        if ent == '':
            continue
        atemp = re.split('\s+', ent)
        atime = float(atemp[0])

        focal = float(atemp[1])
        crat  = float(atemp[2])
        crbt  = float(atemp[3])

        if (atime >= start) and (atime < stop):
            f_list.append(focal)
            a_list.append(crat)
            b_list.append(crbt)

        elif atime > stop:
#
#--- if there are data, take averages of data
#
            if len(f_list) > 0:
                afocal = numpy.average(f_list)
                acrat  = numpy.average(a_list)
                acrbt  = numpy.average(b_list)
                mtime  = start + hstep

                sline = sline + "%d\t%4.3f\t%4.3f\t%4.3f\n" % (mtime, afocal, acrat, acrbt)
            else:
                pass

            f_list = [focal]
            a_list = [crat]
            b_list = [crbt]
            start  = stop
            stop  += step

    ofile = data_dir + '/focal_plane_data_5min_avg_' + str(year)
    with  open(ofile, 'w') as fo:
        fo.write(sline)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def find_last_entry_date():

    ifile = data_dir + 'long_term_max_data'

    try:
        data  = mcf.read_data_file(ifile)
        start = set_start(data, pos=-1, add=hstep)

    except:
        start = 0

    return start

#-------------------------------------------------------------------------------
#-- set_start: find the fist day of the data and set to start from hour 00:00:00
#-------------------------------------------------------------------------------

def set_start(data, pos=0, add=0.0):
    """
    find the fist day of the data and set to start from hour 00:00:00
    input:  data    --- a list of data; <ctime>:<data1>:<data2>:<data3>
            pos     --- a postion of the element, usually 0 (at beginning)
            add     --- a shifting facotr in seconds; default: 0
    output: start   --- a starting time in seconds from 1998.1.1
    """
    atemp  = re.split('\s+', data[pos])
    stday  = float(atemp[0]) + add
    day    = Chandra.Time.DateTime(stday).date
    btemp  = re.split(':', day)

    start  = btemp[0] + ':' + btemp[1] + ':00:00:00'
    start  = Chandra.Time.DateTime(start).secs

    return start

#-------------------------------------------------------------------------------
#-- TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST -
#-------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """


#-------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    create_5min_avg_data(year)

    #unittest.main()
