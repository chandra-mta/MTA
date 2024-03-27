#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       plot_goes.py: plot GOES data                                            #
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
import numpy as np
#
#--- pylab plotting routine related modules
#
from pylab import *
if __name__ == '__main__':
    mpl.use('Agg')

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
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
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- mta common functions
#
import mta_common_functions             as mcf
#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions        as itrf

#-------------------------------------------------------------------------------------
#--- plot_goes_main: read GOES data and plot them.                                   ---
#-------------------------------------------------------------------------------------

def plot_goes_main(event, start, stop):
    """
    read GOES data from data_dir and plot them. 
    input:  event   --- event name (e.g. 20170906)
            start   --- starting time in <yyyy:mm:dd:hh:mm>
            stop    --- stopping time in <yyyy:mm:dd:hh:mm>
    """
#
#--- find starting year
#
    atemp = re.split(':', start)
    syear = int(float(atemp[0]))
#
#--- read radiation zone information
#
    rad_zone = itrf.read_rad_zone(event)
#
#--- read GOES data
#
    ifile = wdata_dir + event + '_goes.txt'
    data  = mcf.read_data_file(ifile)

    dofy  = []
    p1    = []
    p2    = []
    p5    = []
    hrc   = []
    dcnt  = 0

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        btemp = re.split('\.', atemp[0])
        if ent and btemp[0].isdigit():

            val0 = float(atemp[0])
            dofy.append(val0)

            val1 = float(atemp[1])
            if val1 <= 0:
                val1 = 1e-5

            val2 = float(atemp[2])
            if val2 <= 0:
                val2 = 1e-5

            val3 = float(atemp[3])
            if val3 <= 0:
                val3 = 1e-5

            p1.append(math.log10(val1))
            p2.append(math.log10(val2))
            p5.append(math.log10(val3))
#
#--- hrc prox data only appears afte 2020
#
            if syear >= 2020:
                val4 = float(atemp[4])
                if val4 <= 0:
                    val4 = 1e-5
                hrc.append(math.log10(val4))
#
#--- modify date formats
#
    [year1, ydate1] = itrf.dtime_to_ydate(start)
    [year2, ydate2] = itrf.dtime_to_ydate(stop)
#
#--- find plotting range
#
    (pyear_start, period_start, pyear_stop, period_stop,\
     plot_year_start, plot_start, plot_year_stop, plot_stop, pannel_num) \
                 = itrf.find_collection_period(year1, ydate1, year2, ydate2)
#
#--- if the interuption go over two years, adjust the ending ydate to that of the previous year
#
    if year2 > year1:
        if mcf.is_leapyear(yeat1):
            base = 366
        else:
            base = 365

        ydate2 += base
#
#--- plot data
#
    if pannel_num == 1:
        plot_goes(dofy, p1, p2, p5, hrc, ydate1, ydate2, plot_start, plot_stop, rad_zone)
        cmd = 'mv ./out.png ' + goes_dir + event + '_goes.png'
        os.system(cmd)
#
#--- if the interruption period cannot be covered by one plotting panel, 
#--- create as many panels as we need to cover the period.
#
    else:
        pstart = plot_start
        prange = pannel_num + 1
        for i in range(1, prange):
            pend = pstart + 5
            if i == 1:
                plot_goes(dofy, p1, p2, p5, hrc, ydate1, 'NA', pstart, pend, rad_zone)
                cmd = 'mv ./out.png ' + goes_dir + event + '_goes.png'
                os.system(cmd)

            elif i == pannel_num:
                plot_goes(dofy, p1, p2, p5, hrc, 'NA', ydate2, pstart, pend, rad_zone)
                cmd = 'mv ./out.png ' + goes_dir + event + '_goes_pt'+ str(i) +  '.png'
                os.system(cmd)

            else:
                plot_goes(dofy, p1, p2, p5, hrc, 'NA', 'NA', pstart, pend, rad_zone)
                cmd = 'mv ./out.png ' + goes_dir + event + '_goes_pt'+ str(i) +  '.png'
                os.system(cmd)
            pstart = pend

#-------------------------------------------------------------------------------------
#--- plot_goes: create three panel plots of GOES data                             ---
#-------------------------------------------------------------------------------------

def plot_goes(dofy, p1, p2, p5, hrc,  start, stop, xmin, xmax,  rad_zone):
    """
    create three panel plots of GOES data 
    input:  dofy    --- a list of date in ydate
            p1      --- a list of goes p1 data
            p2      --- a list of goes p2 data
            p5      --- a list of goes p5 data
            hrc     --- a list of goes hrc prox data
            start   --- interruption starting time in ydate
            stop    --- interruption stopping time in ydate
            xmin    --- plotting range x min
            xmax    --- plotting range x max
            rad_zone --- a list of rad zone 
    """
#
#--- check hrc prox data
#
    hdlen = len(hrc)
    if hdlen == 0:
        hind = 0
    else:
        hind = 1
#
#--- setting the plotting ranges
#
    ymin  = -3
    ymax  =  5

    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.08)

#
#--------------------------------
#---- first panel: P1
#--------------------------------
#
    if hind == 0:
        ax1 = plt.subplot(311)
    else:
        ax1 = plt.subplot(411)

    plot_panel(ax1, dofy, p1, start, stop, xmin, xmax, ymin, ymax, rad_zone)
#
#--- mark y axis
#
    ax1.set_ylabel('Log(p1 Rate)')
#
#----------------------------
#--- second panel:  P2
#----------------------------
#
    if hind == 0:
        ax2 = plt.subplot(312, sharex=ax1)
    else:
        ax2 = plt.subplot(412, sharex=ax1)

    plot_panel(ax2, dofy, p2, start, stop, xmin, xmax, ymin, ymax, rad_zone)
#
#--- draw trigger level
#
    plt.plot([xmin,xmax],[2.0, 2.0], color='red', linestyle='--', lw=1.0)
#
#--- label y axis
#
    ax2.set_ylabel('Log(p2 Rate)')
#
#----------------------
#--- third Panel: P5
#----------------------
#
    if hind == 0:
        ax3 = plt.subplot(313, sharex=ax1)
    else:
        ax3 = plt.subplot(413, sharex=ax1)

    plot_panel(ax3, dofy, p5, start, stop, xmin, xmax, ymin, ymax, rad_zone)
#
#--- draw trigger level
#
    plt.plot([xmin,xmax],[-0.155, -0.155], color='red', linestyle='--', lw=1.0)
#
#--- label axis
#
    ax3.set_ylabel('Log(p5 Rate)')
#
#--------------------------
#--- fourth Panel: Hrc Prox
#--------------------------
#
    if hind > 0:
        ax4 = plt.subplot(414, sharex=ax1)
        ymin = 1
        ymax = 6

        plot_panel(ax4, dofy, hrc, start, stop, xmin, xmax, ymin, ymax, rad_zone)

        ax4.set_ylabel('Log(HRC Prox)')
#
#--- label  x axis
#
    xlabel('Day of Year')
#
#--- plot x axis tick label only at the last panel
#
    if hind == 0:
        alist = [ax1, ax2]
    else:
        alist = [ax1, ax2, ax3]

    for ax in alist:
        for label in ax.get_xticklabels():
            label.set_visible(False)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0/6.7in)
#
    fig = matplotlib.pyplot.gcf()
    if hind == 0:
        fig.set_size_inches(10.0, 5.0)
    else:
        fig.set_size_inches(10.0, 6.7)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=300)

#-------------------------------------------------------------------------------------
#-- plot_panel: create a part of each panel                                         --
#-------------------------------------------------------------------------------------

def plot_panel(ax, dofy, ydata,  start, stop, xmin, xmax, ymin, ymax,  rad_zone):
    """
    create a part of each panel
    input:  ax          --- panel id
            dofy        --- a list of time
            ydata       --- a list of data
            start       --- interruption starting time
            stop        --- interruption stopping time
            xmin        --- plotting starting time
            xmax        --- plotting stopping time
            rad_zone    --- a list of radiation zone
    output: out.png 
    """
#
#--- set text position
#

    xdiff = xmax - xmin
    ydiff = ymax - ymin
    if start == 'NA':
        xtext = 0.01 * xdiff
    else:
	    xtext = start + 0.01 * xdiff
    ytext = ymax - 0.2 * xdiff
#
#--- set plotting range
#
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)

    ax.set_xlim(xmin, xmax, auto=False)
    ax.set_ylim(ymin, ymax, auto=False)

    tix_row = itrf.make_tix_label(ymin, ymax)
    ax.set_yticklabels(tix_row)
#
#--- plot line
#
    plt.plot(dofy, ydata, color='black', lw=0, marker='.', markersize=0.8)
#
#--- plot radiation zone makers
#
    itrf.plot_rad_zone(rad_zone, xmin, xmax, ymin)
#
#--- put lines to indicate the interrupted time period
#
    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)

#--------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 3:
        event = sys.argv[1]
        start = sys.argv[2]
        stop  = sys.argv[3]

        plot_goes_main(event, start, stop)
