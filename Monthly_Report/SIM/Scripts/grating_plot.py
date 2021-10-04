#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       grating_plot.py: create grating movement plots for monthly report               #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.eud)                                   #
#                                                                                       #
#           last update: Oct 04, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import math
import unittest
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
path = '/data/mta/Script/Month/SIM/house_keeping/dir_list_py'

with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
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

datafile = "/data/mta/www/mta_otg/OTG_sorted.rdb"

#-----------------------------------------------------------------------------------------
#-- plot_grat_movement: create grating movement plots                                  ---
#-----------------------------------------------------------------------------------------

def plot_grat_movement(year, month):

    """
    create grating movement plots
    input:  none, but read from database
    outupu: monthly_grat.png and monthly_grat_ang.png
    """
#
#--- read data
#
    [ltime, h_in_ang, h_out_ang, l_in_ang, l_out_ang, h_in, h_out, l_in, l_out]\
                                    = get_grat_data(year, month)
#
#--- plot insertion/retraction angle plots
#
    plot_steps(year, month, ltime, h_in_ang, h_out_ang, l_in_ang, l_out_ang)
#
#--- plot hetg/letg cumulative count rate plots
#
    plot_cum_grating(ltime, h_in, l_in)

#-----------------------------------------------------------------------------------------
#-- get_grat_data: read database and extract needed information, then create data       --
#-----------------------------------------------------------------------------------------

def get_grat_data(year, mon):
    """
    read database and extract needed information, then create data
    input: none but read from the database: "/data/mta/www/mta_otg/OTG_sorted.rdb"
    output: [time, h_in_ang, h_out_ang, l_in_ang, l_out_ang, h_in, h_out, l_in, l_out]
            where: time         --- time in fractional year
                   h_in_ang     --- hetig insertion angle
                   h_out_ang    --- hetig retraction angle
                   l_in_ang     --- letig insertion angle
                   l_out_ang    --- letig retraction angle
                   h_in         --- hetig insertion cumm count
                   h_out        --- hetig retraction cumm count
                   l_in         --- letig insertion cumm count
                   l_out        --- hetig retraction cumm count
    """
#
#--- read data
#
    data = mcf.read_data_file(datafile)

    direct   = []
    grating  = []
    start    = []
    stop     = []
    hposa    = []
    hposb    = []
    fposa    = []
    fposb    = []

    for i in range(1, len(data)):
        ent   = data[i]
        atemp = re.split('\s+', ent)
        try:
            test  = float(atemp[2])
            test2 = float(atemp[4])
        except:
            continue
        direct.append(atemp[0].strip())
        grating.append(atemp[1].strip())
        val = convert_time(atemp[2])

        start.append(val)
        stop.append(convert_time(atemp[4]))
        hposa.append(float(atemp[18]))
        hposb.append(float(atemp[19]))
        fposa.append(float(atemp[20]))
        fposb.append(float(atemp[21]))
#
#--- create start and stop lists of data bin. the width is a month
#
    [blist, elist] = create_monthly_bins(2000, year, mon)

    blen          = len(blist)
    ltime          = [0 for x in range(0, blen)]
    h_in          = [0 for x in range(0, blen)]     #--- hetg insertion cumm count rate
    h_in_ang      = [0 for x in range(0, blen)]     #--- hetg insertion angle
    h_out         = [0 for x in range(0, blen)]     #--- hetg retraction cumm count rate
    h_out_ang     = [0 for x in range(0, blen)]     #--- hetg retraction angle

    l_in          = [0 for x in range(0, blen)]
    l_in_ang      = [0 for x in range(0, blen)]
    l_out         = [0 for x in range(0, blen)]
    l_out_ang     = [0 for x in range(0, blen)]

    for j in range(1, blen):

        ltime[j]       = 0.5 * (blist[j] + elist[j]) #--- take a mid point for the bin's time 
#
#-- creating cummulative count; the current bin should have, at least, as the same as the 
#-- previous bin
#
        h_in[j]       = h_in[j-1]
        h_out[j]      = h_out[j-1]
        l_in[j]       = l_in[j-1]
        l_out[j]      = l_out[j-1]

        h_in_ang_cnt  = 0
        h_out_ang_cnt = 0
        l_in_ang_cnt  = 0
        l_out_ang_cnt = 0
#
#--- since the data are not ordered by date, go through begining to the end 
#--- every bin cycle
#
        for i in range(0, len(start)):

            if start[i] >= blist[j] and start[i] < elist[j]: 
                if direct[i] == 'INSR':
                    if grating[i] == 'HETG':
                        h_in_ang[j]   += fposa[i]
                        h_in_ang_cnt  += 1
                        h_out_ang[j]  += hposa[i]
                        h_out_ang_cnt += 1
     
                    if grating[i] == 'LETG':
                        l_in_ang[j]   += fposa[i]
                        l_in_ang_cnt  += 1
                        l_out_ang[j]  += hposa[i]
                        l_out_ang_cnt += 1
#
#--- taking monthly average
#
        if h_in_ang_cnt> 0:
            h_in_ang[j] /=  h_in_ang_cnt

        if h_out_ang_cnt> 0:
            h_out_ang[j] /=  h_out_ang_cnt

        if l_in_ang_cnt> 0:
            l_in_ang[j] /=  l_in_ang_cnt

        if l_out_ang_cnt> 0:
            l_out_ang[j] /=  l_out_ang_cnt
#
#--- adding in/out count for the month to appropriate bins
#
        h_in[j]  += h_in_ang_cnt
        h_out[j] += h_out_ang_cnt
        l_in[j]  += l_in_ang_cnt
        l_out[j] += l_out_ang_cnt

    return [ltime, h_in_ang, h_out_ang, l_in_ang, l_out_ang, h_in, h_out, l_in, l_out]

#-----------------------------------------------------------------------------------------
#-- convert_time: convert time format from <year><ydate>.<hh><mm><ss> to frac year     ---
#-----------------------------------------------------------------------------------------

def convert_time(otime):

    """
    convert time format from <year><ydate>.<hh><mm><ss> to frac year
    input:  otime   --- time in e.g. 2014059.122333.1
    output: fyear   --- fractional year, e.g. 2014.1630585
    """

    year  = float(otime[0:4])
    ydate = float(otime[4:7])
    hours = float(otime[8:10])
    mins  = float(otime[10:12])
    secs  = float(otime[12:14])

    if mcf.is_leapyear(year):
        base = 366.0
    else:
        base = 365.0

    fday  = hours / 24.0 + mins / 1440.0 + secs / 86400.0
    fyear = year + (ydate + fday) / base

    return fyear

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
#-- : create insertion and retraction angle plots for hetig and letig                   --
#-----------------------------------------------------------------------------------------

def plot_steps(year, mon, ltime, set1, set2, set3, set4):
    """
    create insertion and retraction angle plots for hetig and letig
    input:  ltime    --- time in fractional year
            set1    --- mean hetig insertion angle
            set2    --- mean hetig retraction angle
            set3    --- mean letig insertion angle
            set4    --- mean letig retraction angle
            where "mean" means month average
    output: monthly_grat_ang.png
    """
    xmin  = 2000
    xmax  = year + 1
    if mon > 6:
        xmax += 1

    ymin1 = 5.0
    ymax1 = 10.0
    ymin2 = 76
    ymax2 = 81
#
#--- set a few parameters
#

    fsize  = 9       #--- font size
    lsize  = 0       #--- line width
    color  = 'red'
    marker = 'o'
    msize  = 2

    plt.close("all")
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
    plt.subplots_adjust(hspace=0.20, wspace=0.11)  #--- spacing of panels 
#
#--- 'Mean HETG Inserted Angle
#
    a1 = plt.subplot(221)
    plot_sub(a1, ltime, set1, xmin, xmax, ymin1, ymax1, color, lsize, marker, msize, tline='Mean HETG Inserted Angle')
    a1.set_ylabel('Insertion Angle (Degree)', size=fsize)
#
#--- 'Mean HETG Retracted Angle
#
    a2 = plt.subplot(223)
    plot_sub(a2, ltime, set2, xmin, xmax, ymin2, ymax2, color, lsize, marker,  msize, tline='Mean HETG Retracted Angle')
    a2.set_xlabel('Time (year)', size=fsize)
    a2.set_ylabel('Retraction Angle (Degree)', size=fsize)
#
#--- 'Mean LETG Inserted Angle
#
    a3 = plt.subplot(222)
    plot_sub(a3, ltime, set3, xmin, xmax, ymin1, ymax1, color, lsize, marker,  msize, tline='Mean LETG Inserted Angle')

#
#--- 'Mean LETG Retracted Angle
#
    a4 = plt.subplot(224)
    plot_sub(a4, ltime, set4, xmin, xmax, ymin2, ymax2, color, lsize, marker,  msize, tline='Mean LETG Rectracted Angle')
    a4.set_xlabel('Time (year)', size=fsize)
#
#--- save the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(7.5, 3.75)

    outname = 'monthly_grat_ang.png'
    plt.savefig(outname, format='png', dpi=200)

#-----------------------------------------------------------------------------------------
#-- plot_cum_grating: plot cummulative count rates of hetig and letig insertion         --
#-----------------------------------------------------------------------------------------

def plot_cum_grating(ltime, h_in, l_in):
    """
    plot cummulative count rates of hetig and letig insertion. 
    input:  ltime    --- fractional year
            h_in    --- hetig insertion cummulative count rate (month step)
            l_in    --- letig insertion cummulative count rate 
    output: monthly_grat.prn
    """
#
#--- set x axis plotting range
#
    out = time.strftime('%Y:%m', time.gmtime())
    atemp = re.split(':', out)
    year  = int(atemp[0])
    mon   = int(atemp[1])
    xmin  = 2000
    xmax  = int(year) + 1
    if mon > 6:
        xmax += 1
#
#--- set y axis plotting range
#
    ymin = 0.0
    ymax = max(h_in)
    ymax2 = max(l_in)
    if ymax2 > ymax:
        ymax = ymax2
    ymax = int(1.1 * ymax) + 10
#
#--- set a few parameters
#
    fsize  = 9
    lsize  = 0
    color  = 'red'
    marker = 'o'
    msize  = 3
    plt.close("all")
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
    plt.subplots_adjust(hspace=0.08, wspace=0.10)
#
#--- HETG Cumulative Count Plots
#
    a1 = plt.subplot(121)           #--- two panel plot: left
    plot_sub(a1, ltime, h_in, xmin, xmax, ymin, ymax, color, lsize, marker,  msize, tline='HETG')

    a1.set_xlabel('Time (year)', size=fsize)
    a1.set_ylabel('Cumulative Insertion Counts', size=fsize)
#
#--- LETG Cumulative Count Plots
#
    a1 = plt.subplot(122)           #--- two panel plot: right
    plot_sub(a1, ltime, l_in, xmin, xmax, ymin, ymax, color, lsize, marker,  msize, tline='LETG')

    a1.set_xlabel('Time (year)', size=fsize)
#
#--- save the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 7.5)
    outname = 'monthly_grat.png'
    plt.savefig(outname, format='png', dpi=100)

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
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_get_grat_data(self):

        [time, h_in_ang, h_out_ang, l_in_ang, l_out_ang, h_in, h_out, l_in, l_out] = get_grat_data()

        h_in_ang_test  = [5.96, 0, 5.96, 6.086666666666667, 5.96]
        h_out_ang_test = [79.09, 0, 79.09000000000002, 79.09, 79.09]
        l_in_ang_test  = [7.09, 7.09, 7.09, 6.71, 6.773333333333333]
        l_out_ang_test = [78.15, 78.15, 77.96, 77.96, 77.96]
        h_in_test      = [368, 368, 374, 377, 379]
        h_out_test     = [368, 368, 374, 377, 379]
        l_in_test      = [204, 206, 207, 208, 214]
        l_out_test     = [204, 206, 207, 208, 214]

        self.assertEquals(h_in_ang[100:105],  h_in_ang_test)
        self.assertEquals(h_out_ang[100:105], h_out_ang_test)
        self.assertEquals(l_in_ang[100:105],  l_in_ang_test)
        self.assertEquals(l_out_ang[100:105], l_out_ang_test)
        self.assertEquals(h_in[100:105],      h_in_test)
        self.assertEquals(h_out[100:105],     h_out_test)
        self.assertEquals(l_in[100:105],      l_in_test)
        self.assertEquals(l_out[100:105],     l_out_test)
    
#------------------------------------------------------------

    def test_convert_time(self):

        time = '2014059.122333.1'
        val  = convert_time(time)
        val  = round(val, 7)
        self.assertEquals(val, 2014.1630585)
        
#------------------------------------------------------------

    def test_create_monthly_bins(self):

        out1 = [2013.0, 2013.0849315068492, 2013.1616438356164, 2013.2465753424658, 2013.3287671232877, 2013.4136986301369, 2013.495890410959, 2013.5808219178082, 2013.6657534246576, 2013.7479452054795, 2013.8328767123287, 2013.9150684931508, 2014.0, 2014.0849315068492]
        out2 = [2013.0849315068492, 2013.1616438356164, 2013.2465753424658, 2013.3287671232877, 2013.4136986301369, 2013.495890410959, 2013.5808219178082, 2013.6657534246576, 2013.7479452054795, 2013.8328767123287, 2013.9150684931508, 2014, 2014.0849315068492, 2014.1616438356164]
        ystart = 2013
        ystop  = 2014
        mstop  = 2
        [blist, elist] = create_monthly_bins(ystart, ystop, mstop)

        self.assertEquals(blist, out1)
        self.assertEquals(elist, out2)

#-----------------------------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

chk = 0
if len(sys.argv) == 2:
    chk = 1

if __name__ == '__main__':

    if chk > 0:
        plot_grat_movement()
    else:
        unittest.main()


