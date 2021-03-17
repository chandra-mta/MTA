#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       compute_ace_stat.py: find hradness and other statistics of the radiation curves         #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 09, 2021                                                       #
#                                                                                               #
#################################################################################################

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
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- mta common functions
#
import mta_common_functions         as mcf
#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions    as itrf

#-----------------------------------------------------------------------------------------------
#--- compute_ace_stat: compute ACE radiation data statistics                                 ---
#-----------------------------------------------------------------------------------------------

def compute_ace_stat(event, start, stop):
    """
    for a gien event, start and stop data, compute ACE statistics. 
    input:  event   --- event name                  example: 20110804
            start   --- interruption starting time  example: 2011:08:04:07:03
            stop    --- interruption stopping time  example: 2011:08:07:10:25
    output: <stat_dir>/<event>_ace_stat
    """
#
#--- change time format to year and ydate (float)
#
    [year1, ydate1] = itrf.dtime_to_ydate(start)
    [year2, ydate2] = itrf.dtime_to_ydate(stop)
#
#--- set interruption starting check time interval
#
    out    = time.strftime('%Y:%j:%H:%M:00', time.strptime(start, '%Y:%m:%d:%H:%M'))
    stime  = int(Chandra.Time.DateTime(out).secs)
    cstart = stime - 200
    [year, cstart] = itrf.ctime_to_ydate(cstart)
    cstop  = stime + 200
    [year, cstop]  = itrf.ctime_to_ydate(cstop)
#
#--- find plotting range (need only plot_start and plot_stop time)
#
    (xx, xx, xx, xx, xx,plot_start, xx, plot_stop, xx) \
                 = itrf.find_collection_period(year1, ydate1, year2, ydate2)
#
#--- read ACE data
#
    ifile = wdata_dir + event + '_dat.txt'
    data  = mcf.read_data_file(ifile)
#
#--- initialization
#
    e38_int        = 0
    e175_int       = 0
    p47_int        = 0
    p112_int       = 0
    p310_int       = 0
    p761_int       = 0
    p1060_int      = 0
    aniso_int      = 0
    r38_175_int    = 0
    r47_1060_int   = 0
    r112_1060_int  = 0
    r310_1060_int  = 0
    r761_1060_int  = 0
    
    time_save      = []
    e38_save       = []
    e175_save      = []
    p47_save       = []
    p112_save      = []
    p310_save      = []
    p761_save      = []
    p1060_save     = []

    e38_list       = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    e175_list      = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p47_list       = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p112_list      = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p310_list      = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p761_list      = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    p1060_list     = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    aniso_list     = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    r38_175_list   = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    r47_1060_list  = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    r112_1060_list = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    r310_1060_list = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
    r761_1060_list = [0.0, 0.0, 0.0, 1.0e10, 0.0, 0.0, 0.0]
#
#--- start accumulating the values
#
    for ent in data:    
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])

        if (len(atemp) >= 9)  and btemp[0].isdigit():
#
#--- if the value is negative, set it to very small value
#
            for j in range(1, 9):
                if float(atemp[j]) <= 0:
                    atemp[j] = 1.0e-5

            stime      = float(atemp[0])
            e38        = float(atemp[1])
            e175       = float(atemp[2])
            p47        = float(atemp[3])
            p112       = float(atemp[4])
            p310       = float(atemp[5])
            p761       = float(atemp[6])
            p1060      = float(atemp[7])
            aniso      = float(atemp[8])

            time_save.append(stime)
            e38_save.append(e38)
            e175_save.append(e175)
            p47_save .append(p47)
            p112_save.append(p112)
            p310_save.append(p310)
            p761_save.append(p761)
            p1060_save.append(p1060)
#
#--- check whether the value is min/max. also update sum and square of sum 
#--- to compute avg and std at the end 
#
            e38_list   = get_stat_data(e38,   stime, e38_list)
            e175_list  = get_stat_data(e175,  stime, e175_list)
            p47_list   = get_stat_data(p47,   stime, p47_list)
            p112_list  = get_stat_data(p112,  stime, p112_list)
            p310_list  = get_stat_data(p310,  stime, p310_list)
            p761_list  = get_stat_data(p761,  stime, p761_list)
            p1060_list = get_stat_data(p1060, stime, p1060_list)
            aniso_list = get_stat_data(aniso, stime, aniso_list)
#
#--- start checking the ratio of the values
#
            r38_175   = -999
            r47_1060  = -999
            r112_1060 = -999
            r310_1060 = -999
            r761_1060 = -999
            if  e175 > 0:
                r38_175 = e38/e175
                if e38 > 0:
                    r38_175_list = get_stat_data(r38_175, stime, r38_175_list)

            if p1060 > 0:
                r47_1060 =  p47/p1060
                if p47 > 0:
                    r47_1060_list = get_stat_data(r47_1060, stime, r47_1060_list)
                 
                r112_1060  = p112/p1060
                if p112 > 0:
                    r112_1060_list = get_stat_data(r112_1060, stime, r112_1060_list)

                r310_1060  = p310/p1060
                if p310 > 0:
                    r310_1060_list = get_stat_data(r310_1060, stime, r310_1060_list)

                r761_1060 = p761/p1060
                if p761 > 0:
                    r761_1060_list = get_stat_data(r761_1060, stime, r761_1060_list)
#
#--- recording interruption starting time values
#
            if (stime > cstart) and (stime < cstop):
                e38_int       = e38
                e175_int      = e175
                p47_int       = p47
                p112_int      = p112
                p310_int      = p310
                p761_int      = p761
                p1060_int     = p1060
                aniso_int     = aniso
                r38_175_int   = r38_175
                r47_1060_int  = r47_1060
                r112_1060_int = r112_1060
                r310_1060_int = r310_1060
                r761_1060_int = r761_1060
#
#--- create stat table
#
    line = 'Data Period  (doy): %6.4f - %6.4f\n' % (plot_start, plot_stop)
    line = line + 'Interruption (doy): %6.4f - %6.4f\n\n' % (ydate1,    ydate2)

    line = line + '\t\t\tAvg\t\t\t Max\t\tTime\t\tMin\t\tTime\t\tValue at Interruption Started\n'
    line = line + '-' * 95 + '\n'

    line = line +  create_stat_line(e38_list,       'e38\t',        e38_int)
    line = line +  create_stat_line(e175_list,      'e175\t',       e175_int)
    line = line +  create_stat_line(p47_list,       'p47\t',        p47_int)
    line = line +  create_stat_line(p112_list,      'p112\t',       p112_int)
    line = line +  create_stat_line(p310_list,      'p310\t',       p310_int)
    line = line +  create_stat_line(p761_list,      'p761\t',       p761_int)
    line = line +  create_stat_line(p1060_list,     'p1060\t',      p1060_int)
    if year1 < 2014:
        line = line +  create_stat_line(aniso_list,     'aniso',      aniso_int)
    line = line +  create_stat_line(r38_175_list,   'e38/e175',   r38_175_int)
    line = line +  create_stat_line(r47_1060_list,  'p47/p1060',  r47_1060_int)
    line = line +  create_stat_line(r112_1060_list, 'p112/p1060', r112_1060_int)
    line = line +  create_stat_line(r310_1060_list, 'p310/p1060', r310_1060_int)
    line = line +  create_stat_line(r761_1060_list, 'p761/p1060', r761_1060_int)
#
#---- find gradient and chooes the steepest rising point
#
    line = line + '\nSteepest Rise\n'
    line = line + '------------\n'
    line = line + '\tTime\t\tSlope(in log per hr)\n'
    line = line + '----------------------------------------\n'
    line = line + steepness_line(e38_save,   time_save, 'e38')
    line = line + steepness_line(e175_save,  time_save, 'e175')
    line = line + steepness_line(p47_save,   time_save, 'p47')
    line = line + steepness_line(p112_save,  time_save, 'p112')
    line = line + steepness_line(p310_save,  time_save, 'p310')
    line = line + steepness_line(p761_save,  time_save, 'p761')
    line = line + steepness_line(p1060_save, time_save, 'p1060')

    out = stat_dir + event + '_ace_stat'
    with  open(out, 'w') as fo:
        fo.write(line)

#---------------------------------------------------------------------------------------------
#-- get_stat_data: update min, max,sum and sum of square value in the data list             --
#---------------------------------------------------------------------------------------------

def get_stat_data(data, stime, dlist):
    """
    update min, max,sum and sum of square value in the data list
    input:  data    --- data value
            stime    --- time in seconds from 1998.1.1
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
    if val > 1.0e-5:            #---- 1.0e-5 is a mark of invalid data point
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
    line = line + '%4.3e\n'         % (vint)

    return line 

#---------------------------------------------------------------------------------------------
#--- steepness_line: create steepness stat line                                             --
#---------------------------------------------------------------------------------------------

def steepness_line(val, stime, head):
    """
    create steepness stat line
    input:  val     --- a list of the data
            stime   --- a list of the time
            head    --- line head
    output: line    --- a resulted line to be printed
    """
    [m_pos, m_slp] = find_jump(val, stime)
    line = head + ' \t'
    if m_pos == -999:
        line = line + 'na\t\tna\n'
    else:
        line = line + '%5.4f\t\t%3.4f\n' % (stime[m_pos], m_slp)

    return line

#---------------------------------------------------------------------------------------------
#--- fin_jump: find a steepest jump from a given list                                      ---
#---------------------------------------------------------------------------------------------

def find_jump(alist, stime):
    """
    find the steepest jump from a given line 
    input:  alist           --- a list of the data
            stime           --- a list of the time
    output: max position    --- a position where the jump occurs
            max slope       --- the slope of the jump 
    """
    if len(alist) < 10:
        temp = [0 for x in range(100)]
        return (-999, temp[0])
    else:
        last      = len(alist) - 10
        diff      = 24.0 * (stime[last] - stime[10])/(last -10)
        max_slope = 0;
        max_pos   = 0;
    
        if diff > 0:
            for k in range(10, last):
                start = k
                end   = k + 1
                sum   = 0
    
                for m in range(0, 10):
                    sum += alist[end] - alist[start]
                    start += 1
                    end   += 1
    
                slope = 0.1 * sum / diff
                if slope > max_slope:
                    max_slope = slope
                    max_pos   = k + 5
    
        return (max_pos, max_slope)


#--------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 3:
        event = sys.argv[1]
        start = sys.argv[2]
        stop  = sys.argv[3]

        compute_ace_stat(event, start, stop)
