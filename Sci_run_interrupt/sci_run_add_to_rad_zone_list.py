#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       sci_run_add_to_rad_zone_list.py: add radiation zone list around a given date            #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvarad.edu)                                      #
#                                                                                               #
#               last update: Mar 09, 2021                                                       #
#                                                                                               #
#################################################################################################

import sys
import os
import re
import string
import time
import Chandra.Time
import numpy
#
#--- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/Interrupt/Scripts'
DATA_DIR = '/data/mta/Script/Interrupt/Data'
OUT_DATA_DIR = '/data/mta/Script/Interrupt/Data'
#
#--- append a path to a privte folder to python directory
#
sys.path.append(BIN_DIR)

#----------------------------------------------------------------------------------------------
#--- sci_run_add_to_rad_zone_list: adding radiation zone list to rad_zone_list              ---
#----------------------------------------------------------------------------------------------

def sci_run_add_to_rad_zone_list(event_data):
    """
    adding radiation zone list to rad_zone_list. 
    input: file name containing: 
            e.g. 20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto'
    output: updated <data_dir>/rad_zone_list
    """
#
#--- read radiation zone infornation
#
    infile = DATA_DIR + '/rad_zone_info'
    with open(infile) as f:
        rdata = [line.strip() for line in f.readlines()]
    
    t_list = []
    r_dict = {}

#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add the rad zone list
#--- to each date
#


    atemp = re.split(':', event_data['tstart'])
    year  = atemp[0]
    month = atemp[1]
    date  = atemp[2]
#
#--- convert to dom/sec1998
#
    ltime = time.strftime('%Y:%j:%H:%M:%S', time.strptime(event_data['tstart'], '%Y:%m:%d:%H:%M:%S'))
    csec  = int(Chandra.Time.DateTime(ltime).secs)
#
#--- end date
#
    ltime = time.strftime('%Y:%j:%H:%M:%S', time.strptime(event_data['tstart'], '%Y:%m:%d:%H:%M:%S'))
    csec2 = int(Chandra.Time.DateTime(ltime).secs)
#
#--- date stamp for the list
#
    list_date = str(year) + str(month) + str(date)

#
#--- check radiation zones for 3 days before to 5 days after from the interruptiondate
#

    begin = csec  - 3 * 86400.0
    end   = csec2 + 5 * 86400.0

    status = []
    rdate  = []
    chk    = 0
    last_st= ''
    cnt    = 0

    for line in rdata:
        atemp = re.split('\s+', line)

        dtime = float(atemp[1]) 

        if chk  == 0 and atemp[0] == 'ENTRY' and dtime >= begin:
            status.append(atemp[0])
            rdate.append(dtime)
            chk += 1
            last_st = atemp[0]
            cnt += 1
        elif chk > 0 and dtime >= begin and dtime <= end:
            status.append(atemp[0])
            rdate.append(dtime)
            last_st = atemp[0]
            cnt += 1
        elif float(atemp[1]) > end and last_st == 'EXIT':
            break
        elif float(atemp[1]) > end and last_st == 'ENTRY':
            status.append(atemp[0])
            rdate.append(dtime)
            cnt += 1
            break
            

#
#--- a format of the output is, e.g.: '20120313    (4614.2141112963,4614.67081268519):...'
#

        sline =  list_date + '\t'
        dlen  = int(0.5 * len(rdate))
        for k in range(0, dlen):
            m = 2 * k 
            n = m + 1
            line =  '(' + str(rdate[m]) +',' + str(rdate[n]) + ')'
            if k == 0:
                kline = line
            else:
                kline = kline + ':' + line

        sline = sline + kline
        t_list.append(list_date)
        r_dict[list_date] = sline
#
#--- print out the result
#
    ifile  = DATA_DIR + '/rad_zone_list'
    with open(ifile) as f:
        data = [line.strip() for line in f.readlines()]
    c_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        c_list.append(atemp[0])

    out = numpy.setdiff1d(t_list, c_list)

    if len(out) > 0:
        line = ''
        for ent in out:
            line = line + r_dict[ent] + '\n'

        with  open(f"{OUT_DATA_DIR}/rad_zone_list", 'a') as fo:
            fo.write(line)

#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        ifile = sys.argv[1].strip()
    else: 
        ifile = 'NA'

    sci_run_add_to_rad_zone_list(ifile)
