#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#       plot_focal_temperature.py: plot focal temperature peak and width trend          #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last updated: Feb 04, 2014                                                  #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import random
import operator
import numpy

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

#
#--- append a path to a private folder to python directory
#
mta_dir = '/data/mta/Script/Python_script2.7/'
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf

dat_dir = '/data/mta/Script/Month/FOCAL/Data/'
tdata   = dat_dir + 'this_month_data'
fdata   = dat_dir + 'focal_temp_data'

#-------------------------------------------------------------------------------
#-- plot_data  plotting moving aerage of peak temperature and peak width     ---
#-------------------------------------------------------------------------------

def plot_data():
    """
    plotting moving aerage of peak temperature and peak width for the entire period
    input:  none, but read from focal_temp in the same directory. this must be updated
            before compute.
    output: focal_temp_plot.png
    """

#
#--- read data
#
    f    = open(fdata, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    time  = []
    focal = []
    width = []

    for ent in data:

        atemp = re.split('\s+', ent)
        try:
            year  = float(atemp[0])
            ydate = float(atemp[1])

            if tcnv.isLeapYear(year) == 1:
                base = 366
            else:
                base = 365
     
            fyear = year + ydate/base
            time.append(fyear)
    
            focal.append(float(atemp[2]))
            width.append(float(atemp[3]))
        except:
            continue
#
#--- create 10 day moving average
#
    [mv_time, mv_temp, mv_width] = moving_avg(time, focal, width, period=10)
#
#--- set a few parameters for plotting
#
    plt.close('all')
    mpl.rcParams['font.size']   = 18
    mpl.rcParams['font.weight'] = 'bold'
    plt.subplots_adjust(hspace=0.08)
#
#--- set plotting ranges (x axis in year)
#
    xmin = 2000
    xmax = int(max(mv_time)) + 1
    if xmax - max(mv_time) < 0.3:
        xmax += 1
#
#--- focal temperature plot (top panel)
#
    a1 = plt.subplot(211)
    ymin = -120
    ymax = -95
    yname = 'Focal Temperature (C)'
    title = "Focal Temperature (10 Day Moving Average)"
    plot_panel(a1, mv_time, mv_temp,  xmin, xmax, ymin, ymax, yname, title) 
#
#--- peak width plot (bottom panel)
#
    a2 = plt.subplot(212)
    ymin = 0
    ymax = 2.0
    yname = 'Width (days)'
    title = "Peak Width (10 Day Moving Average)"
    plot_panel(a2, mv_time, mv_width, xmin, xmax, ymin, ymax, yname, title)

#
#--- label x axis only on the bottom one
#
    line = a1.get_xticklabels()
    for label in line:
        label.set_visible(False)

    a2.set_xlabel('Time (Year)', fontweight='bold')
#
#--- changing frame line width
#
    for axis in ['top','bottom','left','right']:
          a1.spines[axis].set_linewidth(3)
          a2.spines[axis].set_linewidth(3)
#
#---- set plotting area size
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(20.0,10.0)
#
#--- print out the plot
#
    outname = './Plots/focal_temp_plot.png'
    plt.savefig(outname, format='png', dpi=300)

    plt.close('all')


#-------------------------------------------------------------------------------
#-- moving_avg:  create <period>  day moving average                         ---
#-------------------------------------------------------------------------------

def moving_avg(time, temp, width, period=10):
    """
    create <period>  day moving average
    input:  time    a list of time
            temp    a list of temperature
            width   a list of peak width
    output: [mv_time, mv_temp, mv_width]
                mv_time --- a list of time (the first time of the 10 day period)
                mv_temp --- a list of moving average temperature
                mv_width--- a list of moving average width
    """
    mv_time  = []
    mv_temp  = []
    mv_width = []
    factor   = 1.0/float(period)

    for i in range(0, len(time)):
        avg_temp  = 0
        avg_width = 0
        for j in range(0, period):
            k = i - j
            avg_temp  += temp[k]
            avg_width += width[k]

        avg_temp  *= factor
        avg_width *= factor
        mv_time.append(time[i])
        mv_temp.append(avg_temp)
        mv_width.append(avg_width)

    return [mv_time, mv_temp, mv_width]

#-------------------------------------------------------------------------------
#-- plot_panel: plot each panel of the plots                                 ---
#-------------------------------------------------------------------------------

def plot_panel(ax, x, y,  xmin, xmax, ymin, ymax,  ylabel, title):

    """
    plot each panel of the plots
    input:  ax      --- axis name
            x       --- a list of x value
            y       --- a list of y value
            xmin    --- min of x plotting range
            xmax    --- max of x plotting range
            ymin    --- min of y plotting range
            ymax    --- max of y plotting range
            ylabel  --- a label of y axis
            title   --- a title of the panel
    output  none
    """
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin, xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    p, = plot(x, y, color='blue', marker='', markersize=0, lw=3)
    
    ax.set_ylabel(ylabel, fontweight='bold')

    xpos = 2001.5
    ypos = ymax - 0.15 *(ymax - ymin)

    plt.text(xpos, ypos, title,size=20, fontweight='bold')

#-------------------------------------------------------------------------------
#-- find_average: compute a mean and a standard deviation for peak values    ---
#-------------------------------------------------------------------------------

def find_average():
    """
    compute a mean and a standard deviation for peak heights and peak widths
    input:  none but read from this_month_data in the same directory. this must
            be updated before compute.
    output: mean and sd of peak height and width
    """

    f    = open(tdata, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    focal = []
    width = []

    for ent in data:
        atemp = re.split('\s+', ent)
        focal.append(float(atemp[2]))
        width.append(float(atemp[3]))

    favg = numpy.mean(focal)
    fsig = numpy.std(focal)

    wavg = numpy.mean(width)
    wsig = numpy.std(width)

    line =  "This month's average focal temp: " + str(round(favg,4)) + ' +/- ' + str(round(fsig,4)) + '\n'
    line = line +  "This month's average peak width: " + str(round(wavg,4)) + ' +/- ' + str(round(wsig,4)) + '\n'

    out  = '/data/mta/Script/Month/FOCAL/Plots/month_avg'
    fo   = open(out, 'w')
    fo.write(line)
    fo.close()


#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    plot_data()

    find_average()

