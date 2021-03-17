#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       sim_cumulative_plots.py:    plot tsc and fa movement                                #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 17, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import math
import numpy
import time

import matplotlib as mpl
if __name__ == '__main__':
    mpl.use('Agg')
from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
#
#--- reading directory list
#
path = '/data/mta/Script/SIM_move/Scripts/house_keeping/dir_list'

with  open(path, 'r') as f:
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
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf

#-----------------------------------------------------------------------------------------
#-- plot_sim_movement: read tsc and fa data and plot their cummulatinve movement        --
#-----------------------------------------------------------------------------------------

def plot_sim_movement():

    """
    read tsc and fa data and plot their cummulatinve movement
    input: none
    output: monthly_sim.png
    """
#
#--- read data
#
    [time, month_tsc_mm, month_fa_mm] = get_sim_data()
#
#--- plot data
#
    plot_steps(time, month_tsc_mm, month_fa_mm)


#-----------------------------------------------------------------------------------------
#-- get_sim_data: read data and compute tsc and fa values                              ---
#-----------------------------------------------------------------------------------------

def get_sim_data():

    """
    read data and compute tsc and fa values
    input: none, but read from /data/mta_www/mta_sim/Scripts/sim_data.out
    output: [avg_time, month_tsc_mm, month_fa_mm]
                avg_time     --- fractional year
                month_tsc_mm --- TSC value in 1.0e-4 mm size
                month_fa_mm  --- FA value in mm size
    """

#
#--- get data
#
    datafile = data_dir + 'sim_data.out'
    data     = mcf.read_data_file(datafile)

    stime  = []
    tsc_mm = []
    fa_mm  = []
    prev   = ''
    for ent in data:
#
#--- skip the data line which is same as one before
#
##        if ent == prev:
##            continue
##        else:
##            prev = ent

        atemp = re.split('\s+', ent)
        try:
            if float(atemp[1]) == 0 and float(atemp[2]) == 0:
                continue
        except:
            continue
#
#--- converting time to fractional year
#
        try:
            stime.append(convert_time(atemp[0]))
        except:
            continue
#
#--- computing TSC value
#
        try:
            tval = float(atemp[1])
            tsc_mm.append(-0.0025143153 * tval)
        except:
            tsc_mm.append(0.0)
#
#--- computing FA value
#
        try:
            fval = float(atemp[2])
            fa_mm.append(compute_fa_val(fval))
        except:
            fa_mm.append(0.0)
#
#--- sort the list according to time
#
    sorted_index   = numpy.argsort(stime)
    stime          = [stime[i]  for i in sorted_index]
    tsc_mm         = [tsc_mm[i] for i in sorted_index]
    fa_mm          = [fa_mm[i]  for i in sorted_index]
#
#--- create start and end time list of monthly bins
#
    out            = time.strftime('%Y:%m', time.gmtime())
    atemp          = re.split(':', out)
    year           = int(float(atemp[0]))
    mon            = int(float(atemp[1]))
    [blist, elist] = create_monthly_bins(2000, year, mon)
    blen           = len(blist)

    month_tsc_mm   = [0 for x in range(0, blen)]
    month_fa_mm    = [0 for x in range(0, blen)]
    avg_time       = [0 for x in range(0, blen)]
    test       = [0 for x in range(0, blen)]
#
#--- fill the monthly bin values
#
    k = 1
    for j in range(1, blen):
#
#--- cummulative value of bin i is at least the value of the i-i bin
#
        month_tsc_mm[j]   = month_tsc_mm[j-1]
        month_fa_mm[j]    = month_fa_mm[j-1]
        avg_time[j]       = 0.5 *  (blist[j] + elist[j])

        for i in range(k, len(stime)):

            if stime[i] < blist[j]:
                continue
            elif stime[i] >=  elist[j]:
                k = i - 5
                if k < 1:
                    k = 1
                break
            else:
#
#---for tsc, the plot take 1.0e-4 size on y axis
#
                month_tsc_mm[j] += abs(tsc_mm[i] - tsc_mm[i-1]) /1.0e4
                month_fa_mm[j]  += abs(fa_mm[i]  - fa_mm[i-1])

    return [avg_time, month_tsc_mm, month_fa_mm]


#-----------------------------------------------------------------------------------------
#-- convert_time:  convert timer format from <year>:<ydate>:<hours>:<mins>:<sec> to fractional year
#-----------------------------------------------------------------------------------------

def convert_time(otime):

    """
    convert timer format from <year>:<ydate>:<hours>:<mins>:<sec> to fractional year
    input:  otime   --- time in <year>:<ydate>:<hours>:<mins>:<sec>
    output  fyear   --- time in fractional year
    """
#
#--- input data sometime comes with an extra ":" at the front; check whether it is the case
#
    k = 0
    if otime[0] == ':':
        k = 1

    atemp = re.split(':', otime)
    year  = float(atemp[k])
    ydate = float(atemp[k+1])
    hours = float(atemp[k+2])
    mins  = float(atemp[k+3])
    secs  = float(atemp[k+4])

    if mcf.is_leapyear(year):
        base = 366.0
    else:
        base = 365.0

    fday  = hours / 24.0 + mins / 1440.0 + secs / 86400.0
    fyear = year + (ydate + fday) / base

    return fyear

#-----------------------------------------------------------------------------------------
#-- compute_fa_val: compute FA value                                                   ---
#-----------------------------------------------------------------------------------------

def compute_fa_val(val):

    """
    compute FA value
    input:  val     --- value from the database
    output: fa_val  --- computed fa value
    """

    val /= 1e5
    fa_val =  0.1020064  * math.pow(val,6) \
            + 0.529336   * math.pow(val,5) \
            + 0.39803832 * math.pow(val,4) \
            - 1.08492544 * math.pow(val,3) \
            + 3.5723322  * math.pow(val,2) \
            + 14.7906994 * math.pow(val,1)

    return fa_val

#-----------------------------------------------------------------------------------------
#-- plot_steps: plot tsc and fa movement                                                --
#-----------------------------------------------------------------------------------------

def plot_steps(otime, set1, set2):

    """
    plot tsc and fa movement
    input:  otime   --- a list of time in fractional year
            set1    --- a list of tsc value
            set2    --- a list of fa value
    output: monthly_sim.png
    """

#
#--- set plottting range
#
    out   = time.strftime('%Y:%m', time.gmtime())
    atemp = re.split(':', out)
    year  = int(float(atemp[0]))
    mon   = int(float(atemp[1]))
    xmin  = 2000
    xmax  = year + 1
    if mon > 6:
        xmax += 1

    ymin  = 0
    ymax  = max(set1)
    ymax1 = int(1.1 * ymax) + 10

    ymax  = max(set2)
    ymax2 = int(1.1 * ymax) + 10
#
#-- set a few parameters
#
    fsize  = 9
    lsize  = 0
    color  = 'red'
    marker = 'o'
    msize  = 3
    plt.close("all")
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
#
#--- specify x tick spacing for every 5 years
#
    tixspace = []
    for k in range(0, 100):
        t = 2000 + 5 *k
        if t < xmax:
            tixspace.append(t)
#
#--- TSC plot
#
    a1 = plt.subplot(121)
    plot_sub(a1, otime, set1, xmin, xmax, ymin, ymax1, color, lsize, marker, msize, tline='TSC')

    a1.set_xlabel('Time (year)', size=fsize)
    a1.set_ylabel('TSC Cummulative Moter Dist (x10^4 mm)', size=fsize)
    plt.xticks(tixspace)
#
#-- FA plot
#
    a2 = plt.subplot(122)
    plot_sub(a2, otime, set2, xmin, xmax, ymin, ymax2, color, lsize, marker, msize, tline='FA')

    a2.set_xlabel('Time (year)', size=fsize)
    a2.set_ylabel('FA Cummulative Moter Dist (mm)', size=fsize)
    plt.xticks(tixspace)
#
#--- save the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)

    outname = web_dir + 'Cumulative/monthly_sim.png'
    plt.savefig(outname, format='png', dpi=200)

#-----------------------------------------------------------------------------------------
#-- create_monthly_bins: create a month wide bin for given periods                     ---
#-----------------------------------------------------------------------------------------

def create_monthly_bins(ystart, ystop, mstop):
    """
    create a month wide bin for given periods
    input:  ystart  --- starting year
            ystop   --- stopping year
            mstop   --- stopping month of the stopping month
    output: [blist, elist] a list of lists of starting and stoping period in fractional year
    """

    interval1 = [0.0, 31.0, 59.0, 90.0, 120.0, 151.0, 181.0, 212.0, 243.0, 273.0, 304.0, 334.0, 365.0]
    interval2 = [0.0, 31.0, 60.0, 91.0, 121.0, 152.0, 182.0, 213.0, 244.0, 274.0, 305.0, 335.0, 366.0]

    blist = []
    elist = []
    
    for year in range(ystart, ystop+1):
#
#--- check leap year
#
        if mcf.is_leapyear(year):
            interval = interval2
            base = 366.0
        else:
            interval = interval1
            base = 365.0
#
#--- go around 12 months
#
        for i in range(0, 12):
            if year == ystop and i >= mstop:
                break
            begin = year + interval[i]   / base
            end   = year + interval[i+1] / base
            if int(end) > year:
                end = year + 1

            blist.append(begin)
            elist.append(end)
    
    return [blist, elist]


#-----------------------------------------------------------------------------------------
#-- plot_sub: plotting each panel                                                       --
#-----------------------------------------------------------------------------------------

def plot_sub(ap, x, y, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline=''):
    """
    plotting each panel
    input   ap      --- panel name
            x       --- x data list
            y       --- y data list
            xmin    --- xmin
            xmax    --- xmax
            ymin    --- ymin
            ymax    --- ymax
            color   --- color of data point
            lsize   --- line size
            marker  --- marker shape
            msize   --- size of the marker
            tlime   --- extra text line
    """

    ap.set_autoscale_on(False)
    ap.set_xbound(xmin,xmax)
    ap.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ap.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    plt.plot(x, y , color=color, lw=lsize, marker=marker, markersize=msize)

    if tline != '':
        xpos = 0.05 * (xmax - xmin) + xmin
        ypos = ymax -0.10 * (ymax - ymin)
        text(xpos, ypos, tline, fontsize=11,style='italic', weight='bold')


#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    plot_sim_movement()



