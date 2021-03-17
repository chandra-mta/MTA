#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#   find_focal_temp_peaks.py: find acis focal temperature peack postion, temp, and width    #
#                           this is monthly version!!                                       #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Mar 03, 2016                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import time
import operator
import math
import numpy
import astropy.io.fits  as pyfits
from datetime import datetime
import unittest

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

BTFMT    = '%m/%d/%y,%H:%M:%S'
basetime = datetime.strptime('01/01/98,00:00:00', BTFMT)

dat_dir  = '/data/mta/Script/Month/FOCAL/Data/'
tdata = dat_dir + 'this_month_data'
fdata = dat_dir + 'focal_temp_data'

#-----------------------------------------------------------------------------------------------
#-- find_focal_temp_peaks: estimate focal temperature peak position, temperature, and the peak width
#-----------------------------------------------------------------------------------------------

def find_focal_temp_peaks(year='', month=''):
    """
    estimate focal temperature peak position, temperature, and the peak width.
    the data are collected Thu - Thu span close to the date given.
    input:  year    --- year of the period. default: '' (means the current year)
            month   --- month of the period, default: '' (mean the current month)
            mday    --- date of the month   defalut: '' (menas today's date)
    output: focal_temp_list:    a file contain, peak positioin, temperature, and the peak width
    """
#
#--- find time spans that the data will be collected (Thu - Thu period)
#
    [year, tstart, tstop]  = find_time_span(year, month)
#
#--- extract data for the period. the temperature values are smoothed
#
    [time_set, temp_set] = find_focal_temp_list(tstart, tstop)
#
#--- find peak position, temperature and width of the peak
#
    peak_list = select_peak(time_set, temp_set)
    peak_list = clean_up_peak_list(peak_list)
    peak_list = convert_to_readable(peak_list)
#
#--- print out the data
#
    fo    = open(tdata,'w')
    for ent in peak_list:
        vtime = float(ent[0])
        ltime = str(vtime)
        if vtime < 10:
            ltime = '00' + ltime
        elif vtime < 100:
            ltime = '0'  + ltime
#
        line = str(year) + '\t\t' + str(ltime) + '\t\t' + str(ent[1]) + '\t\t' + str(ent[2]) + '\n'
        fo.write(line)
    fo.close()
#
#-- make a backup before adding this month's data to full data set
#
    bdata = fdata + '~'
    cmd = 'cp ' + fdata + ' ' + bdata
    os.system(cmd)

    cmd = 'cat ' + tdata + '>> ' +  fdata 
    os.system(cmd)
    
#-----------------------------------------------------------------------------------------------
#-- find_time_span: find time span for Thu to Thu nearest to a given date                     --
#-----------------------------------------------------------------------------------------------

def find_time_span(year = '', month = ''):
    """
    find time span for Thu to Thu nearest to a given date
    input:  year    --- year.           default: current year
            month   --- month.          default: current month
            mday    --- month date.     default: today's date
    """
#
#--- if year and month is given, find ydate of the month and the next month
#
    if year != '':    
        eyear  = year
        emonth = month + 1
        if emonth > 12:
            emonth = 1
            eyear += 1

#
#--- if the year and month are not given, set this month as the ending month
#
    else:
        tlist = time.localtime()

        eyear   = tlist[0]
        emonth  = tlist[1]

        year   = eyear
        month  = emonth -1
        if month < 1:
            month = 12
            year  -= 1
#
#--- starting time
#
    input_time = str(year) +':' + str(month) + ':01'
    tlist  = time.strptime(input_time, "%Y:%m:%d") 
    syday  = tlist.tm_yday
#
#--- stopping time
#
    input_time = str(eyear) +':' + str(emonth) + ':01'
    tlist  = time.strptime(input_time, "%Y:%m:%d") 
    eyday  = tlist.tm_yday
#
#--- convert time into seconds from 1998.1.1
#
    start = convertto1998sec(year,  syday)
    stop  = convertto1998sec(eyear, eyday)

    return [year, start, stop] 

#-----------------------------------------------------------------------------------------------
#-- convertto1998sec: convert time format from mm/dd/yy,hh:mm:ss to seconds from 1998.1.1    ---
#-----------------------------------------------------------------------------------------------

def convertto1998sec(year, yday):
    """
    convert time format from mm/dd/yy,hh:mm:ss to seconds from 1998.1.1
    inputftime--- time in mm/dd/yy,hh:mm:ss or yyyy-mm-dd,hh:mm:ss
    output  stime--- time in seconds from 1998.1.1
    """
    FMT2     = '%Y:%j:%H:%M:%S'
    ftime = str(year) + ':' + str(yday) + ':00:00:00'
#
#--- base time 1998 Jan 1, 00:00:00 (see top setting section)
#
    ftime = datetime.strptime(ftime, FMT2)

    tdel  = ftime - basetime

    sec1998 = 86400 * tdel.days + tdel.seconds

    return sec1998


#-----------------------------------------------------------------------------------------------
#-- find_focal_temp_list: extract data for the data period given, and return smoothed focal temperature list
#-----------------------------------------------------------------------------------------------

def find_focal_temp_list(start, stop):
    """
    extract data for the data period given, and return smoothed focal temperature list
    input:  start       --- start time in seconds from 1998.1.1
            stop        --- stop time in seconds from 1998.1.1
    output: time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of smoothed focal temperature
            Note: focal temperature is smoothed so that when trying to find peak and the
                  bottoms, we won't get too many peaks and valleys. 
    """
#
#--- create the list of the data files
#
    cmd = 'ls /data/mta/Script/ACIS/Focal/Short_term/data_* > ' + zspace
    os.system(cmd)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)
#
#--- reverse the list so that we can start from the latest
#
    data.reverse()
    data_set = []
    for ent in data:
        atemp = re.split('data_', ent)
        btemp = re.split('_', atemp[1])
        year = btemp[0]
        yday = btemp[1]
        stime = convertto1998sec(year, yday)
#
#--- collect data line which date follows between start and stop
#
        if stime >= start and stime <= stop:
            f   = open(ent, 'r')
            dinput = [line.strip() for line in f.readlines()]
            f.close()
            for line in dinput:
                ctemp = re.split('\s+', line)
                dtemp = re.split(':', ctemp[1])

                try:
                    yday  = int(float(dtemp[0]))
                    htime = int(float(dtemp[1]))
                except:
                    continue

                ttime = convertto1998sec(year, yday) + htime
                focal = ctemp[2]
                line  = str(ttime) + '\t' + str(focal)
                data_set.append(line)
        else:
            continue
#
#--- sort and then remove duplicated lines
#
    data_set.sort()

    prev    = data_set[0]
    cleaned = [prev]
    for i in range(1, len(data_set)):
        if data_set[i] == prev:
            continue
        else:
            prev = data_set[i]
            cleaned.append(prev)
#
#--- select out time stamp and forcal temperature
#
    time_set = []
    temp_set = []
    for ent in cleaned:
        atemp = re.split('\s+', ent)
        time_set.append(int(float(atemp[0])))
        temp_set.append(float(atemp[1]))
#
#--- take average over 10 minutes
#
    [stime_set, stemp_set] = smooth_data(time_set, temp_set)
#
#--- take moving average to farther smoothing
#
    [stime_set, stemp_set] = mving_avg_data(stime_set, stemp_set)

    return [stime_set, stemp_set]


#-----------------------------------------------------------------------------------------------
#-- smooth_data: take averages of temperatures and return lists of time and temperature lists --
#-----------------------------------------------------------------------------------------------

def smooth_data(time_set, temp_set):
    """
    take averages of temperatures and return lists of time and temperature lists
    input:  time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of temperature 
    output: stime_set   --- a list of time in seconds from 1998.1.1
            stemp_list  --- a list of smoothed temperature 
    """
    
    tspan = 600                 #---- average is currently taken for 10 min span
    prev = time_set[0]
    sum  = temp_set[0]
    cnt  = 1
    stime_set = []
    stemp_set = []
    for i in range(1, len(time_set)):
        if time_set[i] < prev + tspan:
#
#--- drop extreme temperature cases; probably they are glitchs
#
            if temp_set[i] < -130:
                continue
            if temp_set[i] > -70:
                continue
            sum += temp_set[i]
            cnt += 1
        else:
            avg = sum / cnt
            stime_set.append(prev+ 300)
            stemp_set.append(avg)
            prev = time_set[i]
            sum  = temp_set[i]
            cnt  = 1

    avg = sum / cnt
    avg = '%.2f' % round(avg, 2)
    avg = float(avg)
    diff = 0.5 * (time_set[-1] + prev)
    stime_set.append(diff)
    stemp_set.append(avg)

    return[stime_set, stemp_set]

#-----------------------------------------------------------------------------------------------
#-- mving_avg_data: take a moving average                                                      -
#-----------------------------------------------------------------------------------------------

def mving_avg_data(time_set, temp_set):
    """
    take a moving average
    input:  time_set    ---- a list of time
            temp_set    ---- a set of temperature 
    output: stime_set   ---- a list of time
            stemp_set   ---- a list of smoothed temp list
    """
    
    tstep = 10                  #--- moving average is currently taken for 10 data points

    hstep = int(0.5 * tstep)
    stime_set = []
    stemp_set = []
    tlen      = len(time_set)

    for i in range(hstep+1 , tlen-hstep-1):
        sum = 0
        cnt = 0
        for m in range(0, tstep):
            step = i + m - hstep
            sum += temp_set[step]
            cnt += 1
        avg = sum / cnt
        avg = '%.2f' % round(avg, 2)
        avg = float(avg)
        stime_set.append(int(float(time_set[i])))
        stemp_set.append(avg)


    return [stime_set, stemp_set]

#-----------------------------------------------------------------------------------------------
#-- find_turning_point: find peaks and valleys of the focal temperature data                 ---
#-----------------------------------------------------------------------------------------------

def find_turning_point(time_set, temp_set):
    """
    find peaks and valleys of the focal temperature data
    input:  time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of forcal temperature
    """

    up_list   = []
    down_list = []
#
#--- find whether the temperature is going up or down at the begining
#
    diff = temp_set[1] - temp_set[0]
    if diff >= 0:
        slope = 1
    else:
        slope = 0

    for i in range(1, len(time_set)):
        diff = temp_set[i] - temp_set[i-1]
        if diff >= 0:
            cslope = 1
        else:
            cslope = 0
#
#--- if the slope direction changes, we assume that we reached a peak (or a valley)
#
        if slope != cslope:
#
#---  the valley must be lower then -115
#
            if cslope == 1:
                if temp_set[i] < -115:
                    up_list.append(i)
#
#--- the peak must be higher than -118.5
#
            else:
                if temp_set[i] > -118.5:
                    down_list.append(i)
            slope = cslope

    return [up_list, down_list]

#-----------------------------------------------------------------------------------------------
#-- select_peak: find a peak and valleys srrounding the peak                                 ---
#-----------------------------------------------------------------------------------------------

def select_peak(time_set,temp_set):
    """
    find a peak and valleys srrounding the peak
    input:  time_set    --- a list of time in seconds from 1998.1.1
            temp_set    --- a list of temperatures
    output: peak_list   --- a list  of lists of:
                [<peak position> <peak temp> <valley position1> <valley temp> <valley position2> <valley temp>]
    """

    [up_list, down_list] = find_turning_point(time_set, temp_set)

    peak_list = []
#
#--- find a peak and it temperature
#
    for k in down_list:
        htemp = temp_set[k]
        for m in range(0, len(up_list)):
            p1 = time_set[up_list[m]]
            try:
                p2 = time_set[up_list[m+1]]
                lchk = 0 
            except:
                p2 = time_set[-1]
                lchk = 1
            spoint = 0
#
#--- find two valleys around the peak
#
            if time_set[k] >= p1 and time_set[k] <= p2:
#
#--- if the temperature difference between the peak and the valley is less than 1 degree
#--- find the next closest valley point
#
                for l in range(m, 0, -1):
                    diff = htemp - temp_set[up_list[l]]
                    if diff > 1:
                        spoint = up_list[l]
                        break
                epoint = len(up_list) - 1
                for l in range(m+1, len(up_list)):
                    diff = htemp - temp_set[up_list[l]]
                    if diff > 1:
                        epoint = up_list[l]
                        break

                p1 = time_set[spoint]
                p2 = time_set[epoint]

                peak_list.append([time_set[k], temp_set[k], p1, temp_set[spoint], p2, temp_set[epoint]])
                break

    return peak_list

#-----------------------------------------------------------------------------------------------
#-- clean_up_peak_list: find overlapped data and combine them                                 --
#-----------------------------------------------------------------------------------------------

def clean_up_peak_list(peak_list):
    """
    find overlapped data and combine them
    input:  peak_list   --- a list of lists of:
            [<peak position> <peak temp> <valley position1> <valley temp> <valley position2> <valley temp>]
    output: mpeak_list  --- a cleaned up list of lists
    """
                
    [m_time, m_temp, s_time, s_temp, e_time, e_temp] = peak_list[0]
    cleaned_list = []
    for i in range(1, len(peak_list)):
        [m_time2, m_temp2, s_time2, s_temp2, e_time2, e_temp2] = peak_list[i]

        if s_time > s_time2:
            continue
#
#--- if two set of peaks have the same start and stop valley positions, combine them
#
        elif s_time == s_time2 and e_time == e_time2:
            if m_temp < m_temp2:
                m_time = m_time2
                m_temp = m_temp2
#
#--- if the start and stop time are in order (in two set), save the data
#
        elif s_time < s_time2:
            if e_time > s_time2:

                if m_temp2 > m_temp:
                    m_time = m_time2
                    m_temp = m_temp2
                    s_time = s_time2
                    s_temp = s_temp2
                    e_time = e_time2
                    e_temp = e_temp2

            alist = [m_time, m_temp, s_time, s_temp, e_time, e_temp]
            cleaned_list.append(alist)
            m_time = m_time2
            m_temp = m_temp2
            s_time = s_time2
            s_temp = s_temp2
            e_time = e_time2
            e_temp = e_temp2
#
#--- remove duplicate
#
    prev  = cleaned_list[0]
    mpeak_list = [prev]
    for i in range(1, len(cleaned_list)):
        if prev == cleaned_list[i]:
            continue
        else:
            prev = cleaned_list[i]
            mpeak_list.append(prev)

    return mpeak_list


#-----------------------------------------------------------------------------------------------
#-- convert_to_readable: convert the data to reable form                                     ---
#-----------------------------------------------------------------------------------------------

def convert_to_readable(peak_list):
    """
    convert the data to reable form
    input:  peak_list   ---  a list of lists of:
           [<peak position> <peak temp> <valley position1> <valley temp> <valley position2> <valley temp>]
    output: lday        --- ydate
            focal       --- focal temperature (in C)
            width       --- width of the peak in day)
    """

    slist = []
    for ent in peak_list:
        lday  = sec1998tofracday(ent[0])
        focal = float(ent[1])
        focal = "%.2f" % round(focal, 2)
        start = ent[2]
        stop  = ent[4]
        width = (stop -start)/86400.
        width = "%.2f" % round(width, 2)

        alist = [lday, focal, width]
        slist.append(alist)

    return slist

#-----------------------------------------------------------------------------------------------
#-- sec1998tofracday: convert time from seconds from 1998.1.1 to fractional yday              --
#-----------------------------------------------------------------------------------------------

def sec1998tofracday(stime):
    """
    convert time from seconds from 1998.1.1 to fractional yday 
    input:  stime   --- time in seconds from 1998.1.1
    output: lday    --- fractional year date. igore year
    """

    ptime = tcnv.axTimeMTA(stime)
    atemp = re.split(':', ptime)
    day   = float(atemp[1])
    hh    = float(atemp[2])
    mm    = float(atemp[3])
    dtime = day + hh/24.0 + mm/ 1440.0
    lday  = "%.2f" % round(dtime, 2)

    return lday


#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#-----------------------------------------------------------------------------------------

    def test_find_time_span(self):

        [start, stop] = find_time_span()

        print 'TIME START/STOP: ' + str(start) + '<--->' + str(stop)

#-----------------------------------------------------------------------------------------

    def test_find_focal_temp_list(self):

        comp = [['22.52', -115.19, '0.85'], ['23.77', -114.81, '1.21'], ['25.15', -112.8, '1.19'], \
                ['26.81', -114.69, '1.10'], ['27.82', -111.39, '0.73']]
        year = 2016
        month = 1
        mday  = 29
        [start, stop]        = find_time_span(year, month, mday)
        [time_set, temp_set] = find_focal_temp_list(start, stop)

        peak_list = select_peak(time_set, temp_set)
        peak_list = clean_up_peak_list(peak_list)
        peak_list = convert_to_readable(peak_list)

        self.assertEquals(peak_list, comp)

        for ent in peak_list:
            print str(ent)

#-----------------------------------------------------------------------------------------------
 
if __name__ == "__main__":
#
#--- if you like to specify the date, give year, month, and date
#
    test = 0
    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            test = 1
            del sys.argv[1:]
        else:
            exit(1)
    elif len(sys.argv) == 4:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
    else:
        year  = ''
        month = ''

    if test == 0:
        find_focal_temp_peaks(year, month)
    else:
        unittest.main()
