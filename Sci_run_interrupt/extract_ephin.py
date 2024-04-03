#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       extract_ephin.py: extract Ephin data and plot the results               #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#################################################################################

import math
import re
import os
import calendar
import time
import Chandra.Time

WDATA_DIR = '/data/mta_www/mta_interrupt/Data_dir'
OUT_WDATA_DIR = '/data/mta_www/mta_interrupt/Data_dir'

STAT_DIR = '/data/mta_www/mta_interrupt/Stat_dir'
OUT_STAT_DIR = '/data/mta_www/mta_interrupt/Stat_dir'

#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions    as itrf

#---------------------------------------------------------------------------------
#--- ephin_data_extract: extract EPHIN data and create a data table            ---
#---------------------------------------------------------------------------------

def ephin_data_extract(event, start, stop):

    """
    extract EPIN related quantities and creates a data table 
    input:  event   --- event name (e.g.20170911)
            start   --- starting time in <yyyy>:<mm>:<dd>:<hh>:<mm> 
            stop    --- stopping time in <yyyy>:<mm>:<dd>:<hh>:<mm>
    output: <wdata_dir>/<event>_eph.txt
    """
#
#--- change time format and find data collection periods
#
    lstart = start
    start  = time.strftime("%Y:%j:%H:%M:00", time.strptime(start, '%Y:%m:%d:%H:%M'))
    start  = Chandra.Time.DateTime(start).secs - 2 * 86400
    start  = Chandra.Time.DateTime(start).date
    atemp  = re.split(':', start)
    syear  = int(float(atemp[0]))

    stop   = time.strftime("%Y:%j:%H:%M:00", time.strptime(stop,  '%Y:%m:%d:%H:%M'))
    stop   = Chandra.Time.DateTime(stop).secs  + 5 * 86400
    stop   = Chandra.Time.DateTime(stop).date
#
#--- ephin data were terminated before 2015
#
    if syear < 2020:
        [xdate, p4, p41, e150, e1300, ecnt] = get_ephin_data(start, stop, syear)
#
#--- hrc data is included after 2011
#
    if syear >= 2011:
        [stime, veto, hcnt] = get_hrc_data(start, stop, syear)

        if syear < 2020:
            hrc =  match_hrc_to_ephin(stime, veto, hcnt, xdate, syear)
#
#--- print out data
#
    line = 'Science Run Interruption: ' + lstart + '\n\n'

    if syear < 2011:
        line = line + 'dofy\t\tp4\t\t\tp41\t\t\te1300\n'
        line = line + '-------------------------------------------------------------------\n'
    
        for m in range(0, ecnt):
            line = line + '%4.3f\t\t%4.3e\t%4.3e\t%4.3e\n'\
                        % (float(xdate[m]), float(p4[m]), float(p41[m]),  float(e1300[m]))
    elif syear < 2020:
        line = line + 'dofy\t\thrc\t\te150\t\te1300\n'
        line = line + '-------------------------------------------------------------------\n'
    
        for m in range(0, ecnt):
            line = line +  '%4.3f\t\t%4.3e\t%4.3e\t%4.3e\n'\
                    % (float(xdate[m]), float(hrc[m]), float(e150[m]),  float(e1300[m]))
    else:
        line = line + 'dofy\t\thrc\n'
        line = line + '-------------------------------------------------------------------\n'
        
        for m in range(0, hcnt):
            line = line + '%4.3f\t\t%4.3e\n' % (float(stime[m]), float(veto[m]))


    ofile = f"{OUT_WDATA_DIR}/{event}_eph.txt"

    with open(ofile, 'w') as fo:
        fo.write(line)

#--------------------------------------------------------------------
#-- get_ephin_data: extract ephin data                            ---
#--------------------------------------------------------------------

def get_ephin_data(start, stop, syear):
    """
    extract ephin data
    input:  start   --- starting time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stopping time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            syear   --- starting year
    output: xdate   --- time
            p4, p41, e150, e1300 --- ephin data in each energy range
            ecnt    --- the number of data
    """
#
#--- read ephin data using arc5gl
#
    ephinList = itrf.use_arc5gl('retrieve', 'flight', 'ephin', 1, 'ephrates', start, stop) 
#
#--- extract needed data
#
    xdate = []
    p4    = []
    p41   = []
    e150  = []
    e1300 = []
    ecnt  = 0

    for fits in ephinList:
        mc = re.search('fits.gz', fits)
        if mc is None:
            continue

        [tcols, tbdata] = itrf.read_fits_file(fits)
        etime           = list(tbdata.field('time'))

        xdate           =  xdate + convert_to_ydate(etime, syear)

        if syear < 2011:
            p4   = p4  +  list(tbdata.field('scp4'))
            p41  = p41 +  list(tbdata.field('scp41'))
        else:    
            e150 = e150 + list(tbdata.field('sce150'))

        e1300 = e1300 + list(tbdata.field('sce1300'))

        os.remove(fits)

    ecnt = len(e1300)

    return [xdate, p4, p41, e150, e1300, ecnt]

#--------------------------------------------------------------------
#-- get_hrc_data: extract hrc veto rate                            --
#--------------------------------------------------------------------

def get_hrc_data(start, stop, syear):
    """
    extract hrc veto rate
    input:  start   --- starting time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stopping time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            syear   --- staring year
    output: time    --- a list of time
            veto    --- a list of veto rate
            hcnt    --- the number of data
    """
    [stime, veto]  = itrf.use_dataseeker(start, stop, 'shevart')
#
#--- converrt time format into day of year
#
    ltime = []
    for ent in stime:
        dofy = convert_to_ydate(ent, syear)
        ltime.append(dofy)

    hcnt = len(ltime)

    return [ltime, veto, hcnt]

#--------------------------------------------------------------------
#-- match_hrc_to_ephin: match hrc data to ephin time interval      --
#--------------------------------------------------------------------

def match_hrc_to_ephin(ltime, veto, hcnt, xdate, syear):
    """
    match hrc data to ephin time interval
    input:  ltime   --- a list of hrc time
            veto    --- a list of veto rate
            hcnt    --- the number of hrc data
            xdate   --- a list of ephin time
            syear   --- starting year
    output: hrc     --- a list of veto reate adjucted to ephin tine span
    """
#
#--- matching timing between electron data and hrc data
#
    ecnt = len(xdate)
    hrc  = ecnt * [0]
    j    = 0
    k    = 0

    base = 365 + calendar.isleap(syear)
#
#--- find the begining
#
    if ltime[0] < xdate[0]:
        while ltime[j] < xdate[0]:
            j += 1
            if j >= hcnt:
                print("Time span does not overlap. Abort the process.")
                exit(1)

    elif  ltime[0] > xdate[0]:
        while ltime[0] > xdate[k]:
            k += 1
            if k >= ecnt:
                print("Time span does not overlap. Abort the process.")
                exit(1)

    hrc[k] = veto[j]
    
    tspace = 1.38888888888e-3 / base    #--- setting timing bin size: base is given in hrc loop

    for i in range(k+1, ecnt):
        tbeg = xdate[i] - tspace
        tend = xdate[i] + tspace

        if j > hcnt - 2:
#
#--- if the hrc data runs out, just repeat the last data point value
#
            hrc[i] = veto[hcnt -1]

        elif ltime[j] >= tbeg and ltime[j] <= tend:
            hrc[i] = veto[j]

        elif ltime[j] < tbeg:
            while ltime[j] < tbeg:
                j += 1
            hrc[i] = veto[j]

        elif ltime[j] > tend:
            while ltime[j] > tend:
                j -= 1
            hrc[i] = veto[j]

    return hrc

#--------------------------------------------------------------------
#-- convert_to_ydate:  convert the time in second to ydate         --
#--------------------------------------------------------------------

def convert_to_ydate(ltime, syear):
    """
    convert the time in second to ydate
    input:  ltime   --- a value or a list of time in seconds from 1998.1.1
            syear   --- the year of the first data point
    output: xdate   --- a value or a list of day of year
    """
    base = 365 + calendar.isleap(syear)


    if isinstance(ltime, list):
        xdate = []
        for ent in ltime:
            [year, ydate] = itrf.ctime_to_ydate(ent)
            if year > syear:
                ydate += base
            xdate.append(ydate)
    
        return xdate

    else:
        [year, ydate] = itrf.ctime_to_ydate(ltime)
        if year > syear:
            ydate += base

        return ydate

#--------------------------------------------------------------------
#--- compute_ephin_stat: computing Ephin statitics                ---
#--------------------------------------------------------------------

def compute_ephin_stat(event, start):

    """
    read  data from ephin data, and compute statistics
    input:  event       --- name of the event
            startTime   --- start time
    output: <stat_dir>/<event>_ephin_stat
    Note: there are three types of output depending on when the event happened
        before 2010: p4, p41, and e1300
        before 2020: hrc, e150, e1300
        after  2020: hrc
    """

    start = time.strftime("%Y:%j:%M:%H:00", time.strptime(start, "%Y:%m:%d:%H:%M"))
    atemp = re.split(':', start)
    syear = int(float(atemp[0]))
    start = Chandra.Time.DateTime(syear).secs
    start = convert_to_ydate(start, syear)


    ifile = f"{OUT_WDATA_DIR}/{event}_eph.txt"

    with open(ifile) as f:
        data = [line.strip() for line in f.readlines()]

    d0_list = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    d1_list = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    d2_list = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    d0_int  = 0.0
    d1_int  = 0.0
    d2_int  = 0.0

    ind        = 0            #---- indicator whther the loop passed the interruption time
#
#--- dataset = 0 : p4 , p41, e1300
#---           1 : hrc, e150, e1300
#---           2 : hrc
#
    dataset    = 0
    t_line     = data[2]
    m1         = re.search('hrc', t_line)
    m2         = re.search('e150', t_line)

    if m1 is not None:
        dataset = 1
        if m2 is None:
            dataset = 2


    for ent in data:
        atemp = re.split('\s+', ent)
        try:
            stime = float(atemp[0])
        except: 
            continue

        val0    = float(atemp[1])
        d0_list = get_stat_data(val0, stime, d0_list)
        if dataset < 2:
            val1    = float(atemp[2])
            val2    = float(atemp[3])
            d1_list = get_stat_data(val1, stime, d1_list)
            d2_list = get_stat_data(val2, stime, d2_list)
#
#--- finding the value at the interruption
#
        if start <= stime and ind == 0:
            d0_int  = val0
            if dataset < 2:
                d1_int  = val1
                d2_int  = val2
            ind = 1

    line = '\t\tAvg\t\t\tMax\t\tTime\t\tMin\t\tTime\t\tValue at Interruption Started\n'
    line = line + '-'*95 + '\n'

    if dataset == 0:
        line = line + create_stat_line(d0_list, 'p4',    d0_int)
        line = line + create_stat_line(d1_list, 'p41',   d1_int)
        line = line + create_stat_line(d2_list, 'e1300', d2_int)
    elif dataset == 1:
        line = line + create_stat_line(d0_list, 'hrc',   d0_int)
        line = line + create_stat_line(d1_list, 'e150',  d1_int)
        line = line + create_stat_line(d2_list, 'e1300', d2_int)
    else:
        line = line + create_stat_line(d0_list, 'hrc',   d0_int)

    ofile = f"{OUT_STAT_DIR}/{event}_ephin_stat"

    with open(ofile, 'w') as fo:
        fo.write(line)

#---------------------------------------------------------------------------------------------
#-- get_stat_data: update min, max,sum and sum of square value in the data list             --
#---------------------------------------------------------------------------------------------

def get_stat_data(data, stime, dlist):
    """
    update min, max,sum and sum of square value in the data list
    input:  data    --- data value
            stime   --- time in seconds from 1998.1.1
            dlist   --- a list of data:
                        <# of data>
                        <max value>
                        <time of max> 
                        <min value>
                        <time of min>
                        <sum of value>
                        <sum of value**2>
    output: dlist   --- updated data list
    """
    val = float(data)
    if val > 1.0e-5:    #---- 1.0e-5 is a mark of invalid data point
#
#--- find max
#
        dlist[0] += 1
        if val > dlist[1]:
            dlist[1] = val
            dlist[2] = stime
#
#--- find min
#
        if val < dlist[3]:
            dlist[3] = val
            dlist[4] = stime
#
#--- create sum and sum of square
#
        dlist[5] += val
        dlist[6] += val * val
    
    return dlist

#---------------------------------------------------------------------------------------------
#-- create_stat_line: create a stat result line for a given data list                       --
#---------------------------------------------------------------------------------------------

def create_stat_line(dlist, head, vint):
    """
    create a stat result line for a given data list
    input:  dlist   --- a list of data
            head    --- a line head
            vint    --- the value at the interruption started time
    output: line    --- a resulted line to be printed out
    """
    if dlist[0] == 0:
        avg = 0.0
        std = 0.0
    else:
        avg = dlist[5] / dlist[0]
        std = math.sqrt(dlist[6] - avg * avg)
    
    line = head + ' \t\t'
    line = line + '%4.3e+/-%4.3e\t' % (avg, std)
    line = line + '%4.3e\t%4.3f \t' % (dlist[1], dlist[2])
    line = line + '%4.3e\t%4.3f \t' % (dlist[3], dlist[4])
    line = line + '%4.3e\n' % (vint)
    
    return line

