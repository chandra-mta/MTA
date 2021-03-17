#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#   extract_ace_data.py: read ace data and extract the potion for this period   #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string
import time
import Chandra.Time
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
#--- append path
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions     as mcf
#
#--- a day in seconds
#
aday = 86400.0

#-------------------------------------------------------------------------------
#-- extract_ace_data: read ace data and extract the potion for this period     -
#-------------------------------------------------------------------------------

def extract_ace_data(event, start, stop):
    """
    read ace data and extract the potion for this period
    input:  event   --- the name of the event
            start   --- starting time in <yyyy>:<mm>:<dd>:<hh>:<mm>
            stop    --- stopping time in <yyyy>:<mm>:<dd>:<hh>:<mm>
    output: <wdata_dir>/<event>_data.txt
    """
#
#--- year of starting time
#
    atemp  = re.split(':', start)
    syear  = int(float(atemp[0]))
    atemp  = re.split(':', stop)
    eyear  = int(float(atemp[0]))
#
#--- convert time in Chandra Time
#
    lstart = start
    start  = time.strftime('%Y:%j:%H:%M:00', time.strptime(start, '%Y:%m:%d:%H:%M'))
    stop   = time.strftime('%Y:%j:%H:%M:00', time.strptime(stop,  '%Y:%m:%d:%H:%M'))
    start  = int(Chandra.Time.DateTime(start).secs)
    stop   = int(Chandra.Time.DateTime(stop).secs)
#
#--- set to data collecting period
#
    pstart = start - 2 * aday
    period = int((stop - start) / (5 * aday)) + 1
    pstop  = start + 5 * period * aday

    data = []
    for year in range(syear, eyear+1):
        ifile  = data_dir + 'rad_data' + str(syear)
        tdata  = mcf.read_data_file(ifile)
        data   = data + tdata

    hline = 'Science Run Interruption: ' + lstart + '\n'
    hline = hline + 'dofy    electron38  electron175 protont47   proton112   '
    hline = hline + 'proton310   proton761   proton1060  aniso\n'
    hline = hline + '-' * 100

    for ent in data:
        atemp = re.split('\s+', ent)
        if atemp[0].isdigit():
            ltime = atemp[0] + ':' + atemp[1] + ':' + atemp[2] + ':' + atemp[3]
            ltime = time.strftime('%Y:%j:%H:%M:00', time.strptime(ltime, '%Y:%m:%d:%H%M'))
            stime = int(Chandra.Time.DateTime(ltime).secs)
            if (stime >= pstart) and (stime < pstop):
                hline = hline + '%3.4f\t' % chandara_time_to_yday(stime, syear) 
                hline = hline + atemp[7]  + '\t' + atemp[8]  + '\t'
                hline = hline + atemp[10] + '\t' + atemp[11] + '\t'
                hline = hline + atemp[12] + '\t' + atemp[13] + '\t'
                hline = hline + atemp[14] + '\t' + atemp[15] + '\n'

#
#--- print out the data
#
    ofile = wdata_dir  + event + '_dat.txt'

    with open(ofile, 'w') as fo:
        fo.write(hline)

#--------------------------------------------------------------------
#-- chandara_time_to_yday: convert chandra time to ydate           --
#--------------------------------------------------------------------

def chandara_time_to_yday(stime, syear):
    """
    convert chandra time to ydate
    input:  stime   --- time in seconds from 1998.1.1
            syear   --- year at the beginning of the data period
    output: ydate   --- ydate
    """
    atime = Chandra.Time.DateTime(stime).date
    btemp = re.split(':', atime)
    year  = float(btemp[0])
    ydate = float(btemp[1])
    hour  = float(btemp[2])
    mins  = float(btemp[3])
    sec   = float(btemp[4])
    ydate = ydate + (hour/24.0 + mins/1440.0 + sec/86400.0)
#
#--- if the date is over two years, keep counting from the first year
#
    if year > syear:
        if mcf.is_leapyear(syear):
            base = 366
        else:
            base = 365

        ydate += base

    return ydate

#--------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 3:
        event = sys.argv[1]
        start = sys.argv[2]
        stop  = sys.argv[3]

        extract_ace_data(event, start, stop)
