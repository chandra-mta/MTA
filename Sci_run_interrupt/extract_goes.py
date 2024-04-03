#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       extract_goes.py: extract GOES-R data and plot the results               #
#                                                                               #
#           Note: this script works only after: 2020:077                        #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#       P1   1.0 -   3.0 MeV protons (Counts/cm2 sec sr MeV) Uncorrected        #
#       P2   3.4 -  11.0 MeV protons (Counts/cm2 sec sr MeV) Uncorrected        #
#       P5  40.0 -  98.0 MeV protons (Counts/cm2 sec sr MeV) Uncorrected        #
#       HRC Proxy = 6000 * (11.64-38.1MeV) + 270000 * (40.3-73.4MeV)            #
#                                          + 100000 * (83.7-242.0MeV)           #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import calendar
import time
import Chandra.Time

WEB_DIR = '/data/mta_www/mta_interrupt'
OUT_WEB_DIR = '/data/mta_www/mta_interrupt'

WDATA_DIR = '/data/mta_www/mta_interrupt/Data_dir'
OUT_WDATA_DIR = '/data/mta_www/mta_interrupt/Data_dir'

STAT_DIR = '/data/mta_www/mta_interrupt/Stat_dir'
OUT_STAT_DIR = '/data/mta_www/mta_interrupt/Stat_dir'

#
#--- original data location
#
goes_r = '/data/mta4/Space_Weather/GOES/Data/goes_data_r.txt'
#
#--- a day in seconds
#
aday = 86400.0

#-------------------------------------------------------------------------------
#-- extract_goes_data: read goes r data and extract the potion for this period -
#-------------------------------------------------------------------------------

def extract_goes_data(event, start, stop):
    """
    read goes r data and extract the potion for this period
    input:  event   --- the name of the event
            start   --- starting time in <yyyy>:<mm>:<dd>:<hh>:<mm>
            stop    --- stopping time in <yyyy>:<mm>:<dd>:<hh>:<mm>
    output: <web_dir>/GOES_data/<event>_goes.txt
    """
#
#--- year of starting time
#
    atemp = re.split(':', start)
    syear = float(atemp[0])
#
#--- convert time in Chandra Time
#
    start = time.strftime('%Y:%j:%H:%M:00', time.strptime(start, '%Y:%m:%d:%H:%M'))
    stop  = time.strftime('%Y:%j:%H:%M:00', time.strptime(stop,  '%Y:%m:%d:%H:%M'))
    start = int(Chandra.Time.DateTime(start).secs)
    stop  = int(Chandra.Time.DateTime(stop).secs)
#
#--- this script works only after 2020:077
#
    if start < 700790394:
        print('Starting time is before the valid date (2020:077). Terminating the process.')
        exit(1)
#
#--- set to data collecting period
#
    pstart = start - 2 * aday
    period = int((stop - start) / (5 * aday)) + 1
    pstop  = start + 5 * period * aday
#
#--- original data has the following columns
#--- Time  P1  P2A  P2B  P3  P4  P5  P6   P7  P8A   P8B  P8C  P9  P10  HRC Proxy
#
    with open(goes_r) as f:
        data = [line.strip() for line in f.readlines()]
    hline  = 'Science Run Interruption: ' + event + '\n'
    hline  = hline + 'dofy        p1          p2          p5           hrc prox\n'
    hline  = hline + '-' * 65 + '\n'
    line   = ''
    for ent in data:
        if ent[0] == '#':
            continue

        atemp = re.split('\s+', ent)
        stime = int(Chandra.Time.DateTime(atemp[0]).secs)
        if stime < pstart:
            continue
        elif stime > pstop:
            break
#
#--- time in ydate
#
        ctime = chandra_time_to_yday(stime, syear)
#
#--- p1:  1020 - 1860 keV
#--- p2a: 1900 - 2300 keV
#--- p2b: 2310 - 3340 keV
#
        p1    = float(atemp[1])
        p2a   = float(atemp[2])
        p2b   = float(atemp[3])
        p1n   = (0.83 * p1 + 0.4 * p2a + 1.0 * p2b) / 2.3
#
#--- p3:  3400 - 6480 keV
#--- p4:  5840 - 1100 keV
#
        p3    = float(atemp[4])
        p4    = float(atemp[5])
        p2n   = (3.08 * p3 + 5.16 * p4) / 7.6
#
#--- p8b:  99900 - 118000 keV
#--- p8c: 115000 - 143000 keV
#
        p8b   = float(atemp[10])
        p8c   = float(atemp[11])
        p5n   = (18.1 * p8b + 28.0 * p8c) / 43.1

        hprox = atemp[14]

        line  = line + str(stime)  + '\t'
        line  = line + '%3.3e\t' % p1n
        line  = line + '%3.3e\t' % p2n
        line  = line + '%3.3e\t' % p5n
        line  = line + hprox       + '\n'

        hline = hline + '%3.4f\t' % ctime
        hline = hline + '%3.3e\t' % p1n
        hline = hline + '%3.3e\t' % p2n
        hline = hline + '%3.3e\t' % p5n
        hline = hline + hprox       + '\n'
#
#--- print out the data
#
    ofile = f"{OUT_WEB_DIR}/GOES_data/{event}_goes.txt"

    with open(ofile, 'w') as fo:
        fo.write(line)

    ofile = f"{OUT_WDATA_DIR}/{event}_goes.txt"

    with open(ofile, 'w') as fo:
        fo.write(hline)

#--------------------------------------------------------------------
#-- chandra_time_to_yday: convert chandra time to ydate            --
#--------------------------------------------------------------------

def chandra_time_to_yday(stime, syear):
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
        base = 365 + calendar.isleap(int(syear))

        ydate += base

    return ydate

#--------------------------------------------------------------------
#--- compute_goes_stat: computing GOES statitics                  ---
#--------------------------------------------------------------------

def compute_goes_stat(event, start):

    """
    read data from goes data, and compute statistics
    input:  event       --- event name
            start       --- interruption start time in <yyyy>:<mm>:<dd>:<hh>:<mm>
    output: <stat_dir>/<event>_goes_stat
    """
#
#--- check the interruption period so that we can choose which data format to use
#
    atemp  = re.split(':', start)
    syear  = float(atemp[0])
    nind   = 0
    if syear >= 2020:
        nind = 1
#
#--- convert to ydate
#
    start  = time.strftime('%Y:%j:%H:%M:00', time.strptime(start, '%Y:%m:%d:%H:%M'))
    atemp  = re.split(':', start)
    rstart = float(atemp[1]) + float(atemp[2]) / 24.0 + float(atemp[3]) / 1440.0
#
#--- read the data file
#
    ifile = f"{OUT_WDATA_DIR}/{event}_goes.txt"
    with open(ifile) as f:
        data = [line.strip() for line in f.readlines()]
#
#--- initialize
#
    p1_list    = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p2_list    = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p5_list    = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    hp_list    = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p1_int_val = 0.0
    p2_int_val = 0.0
    p5_int_val = 0.0
    hp_int_val = 0.0
    ind        = 0            #---- indicator whther the loop passed the interruption time

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])

        if ent and btemp[0].isdigit():

            atemp = re.split('\s+|\t+', ent)
            if len(atemp) < 4:
                continue

            val0  = float(atemp[0])         #--- time
            val1  = float(atemp[1])         #--- p1
            val2  = float(atemp[2])         #--- p2
            val3  = float(atemp[3])         #--- p5
            p1_list = update_data_set(val0, val1, p1_list) 
            p2_list = update_data_set(val0, val2, p2_list) 
            p5_list = update_data_set(val0, val3, p5_list) 
            if nind > 0:
                val4  = float(atemp[4])     #--- hrc prox
                hp_list = update_data_set(val4, val1, p1_list) 

#
#--- finding the value at the interruption
#
            if rstart <=  val0 and ind == 0:
                p1_int_val = val1
                p2_int_val = val2
                p5_int_val = val3
                if nind > 0:
                    hp_int_val = val4
                ind = 1
#
#--- compute avg/std and create output 
#
    line = '\t\t\tavg\t\t\tmax\t\tTime\t\tmin\t\tTime\t\tValue at Interruption Started\n'

    line = line + '-'*95 + '\n'

    line = line + create_stat_line(p1_list, 'p1\t', p1_int_val)
    line = line + create_stat_line(p2_list, 'p2\t', p2_int_val)
    line = line + create_stat_line(p5_list, 'p5\t', p5_int_val)
    if nind > 0:
        line = line + create_stat_line(hp_list, 'hrc prox', hp_int_val)

    ofile = f"{OUT_STAT_DIR}/{event}_goes_stat"
    with open(ofile, 'w') as fo:
        fo.write(line)

#----------------------------------------------------------------------------
#-- update_data_set: update min, max,sum and sum of square value in the data list
#----------------------------------------------------------------------------

def update_data_set(ytime, val, dlist):
    """
    update min, max,sum and sum of square value in the data list
    input:  ytime   --- time in ydate
            val     --- value 
            dlist   --- a list of data:
                            <sum of value>
                            <sum of value**2>
                            <max>
                            <min>
                            <time of max>
                            <time of min>
                            <# of data>
    output: dlist   --- updated data list
    """
    if val > 0:
        dlist[0] += val
        dlist[1] += val * val

        if val > dlist[2]:
            dlist[2] = val
            dlist[4] = ytime

        if val < dlist[3]:
            dlist[3] = val
            dlist[5] = ytime

        dlist[6] += 1

    return dlist

#----------------------------------------------------------------------------
#-- create_stat_line: create a stat result line for a given data list       -
#----------------------------------------------------------------------------

def create_stat_line(d_list, title, int_val):
    """
    create a stat result line for a given data list
    input:  d_list  --- a list of data
            title   --- a line head
            int_val --- the value at the interruption
    output: line    --- a resulted line to be printed
    """
    [davg, dstd] = compute_stat(d_list)

    line = title + '\t%2.3e +/- %2.3e\t\t%2.3e\t%4.3f\t\t%2.3e\t%4.3f\t\t%2.3e\n'\
                    % (davg, dstd, d_list[2], d_list[4], d_list[3], d_list[5], int_val)

    return line

#----------------------------------------------------------------------------
#-- compute_stat: compute avg and std                                      --
#----------------------------------------------------------------------------

def compute_stat(d_list):
    """
    compute avg and std 
    input:  d_list  --- a list of data
    output [avg, std]
    """

    if d_list[-1] > 0:
        davg = d_list[0] / d_list[-1]
        try:
            dstd = math.sqrt((d_list[1] / d_list[-1]) - (davg * davg))
        except: 
            dstd = -999
    else:
        davg = -999
        dstd = -999

    return [davg, dstd]


#----------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 2:
        event = sys.argv[1]
        start = sys.argv[2]
        stop  = sys.argv[3]
        extract_goes_data(event, start, stop)
        compute_goes_stat(event, start)

