#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       create_iru_bias_plots.py: create iru bias data plot                             #
#                                                                                       #
#           author: t. isobe    (tisobe@cfa.harvard.edu)                                #
#                                                                                       #
#           last update: Mar 12, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import math
import numpy
import astropy.io.fits      as pyfits
import time
from datetime import datetime
import Chandra.Time
import unittest
#
#--- plotting routine
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
#
#--- reading directory list
#
path = '/data/mta/Script/IRU/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import functions
#
import mta_common_functions       as mcf
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
bias_list = ['aogbias1', 'aogbias2', 'aogbias3']
col_name  = ['time', 'roll_bias_avg', 'roll_bias_std', 'pitch_bias_avg',\
             'pitch_bias_std', 'yaw_bias_avg', 'yaw_bias_std']

rad2sec = 360.0 * 60. * 60. /(2.0 * math.pi)
m_list  = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

#----------------------------------------------------------------------------------
#-- create_iru_bias_plots: create iru bias data plots                           ---
#----------------------------------------------------------------------------------

def create_iru_bias_plots(run=['w', 'm', 'y', 't'], stime =''):
    """
    create iru bias data plots
    input:  run     --- a list of which one to plot
                        w   --- weekly
                        m   --- monthly
                        y   --- yearly
                        t   --- full range
                        these must be elements of a list
            stime   --- time of where the plot(s) will bie made around. 
                        the weekly plot always from Fri - Fri
                        the monthly plot alwyas  from 1st of the month to the end
                        the year plot alwyas from Jan 1 till the end of year, 
                        except the lateest year; from Jan1 to today

                        stime is time in seconds from 1998.1.1
                                 time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
                        if it is for year, you can give year
    output: <web_dir>/Plots_new/<year>/<head>_bias.png (for full plot, without<year>)
            <web_dir>/Plots_new/<year>/<head>_hist.png (for full plot, without<year>)
    """
    for ind in run:
#
#--- weekly plots for Weekly report
#
        if ind == 'w':
            [tstart, tstop, head] = set_weekly_range(stime)
            print("Weekly: " + str(tstart) + '<-->' + str(tstop))
            plot_selected_period(tstart, tstop, head)

#
#--- monthly plot
#
        elif ind == 'm':
            [tstart, tstop, head] = set_monthly_range(stime)
            print("Monthly: " + str(tstart) + '<-->' + str(tstop))
            plot_selected_period(tstart, tstop, head)
#
#--- if today is the less than 5th day of the month, create dummy monthly plots
#--- this is because the main function creates only the previous month's plots
#--- in that time period
#
            add_empty_plot_page('mon')
#
#--- yearly plot
#
        elif ind == 'y':
            [tstart, tstop, head] = set_yearly_range(stime)
            print("Yearly: " + str(tstart) + '<-->' + str(tstop))
            plot_selected_period(tstart, tstop, head)
#
#--- if today is the less than 5th day of the year, create dummy yearly plots
#
            add_empty_plot_page('year')
#
#--- full range plot
#
        elif ind == 't':
            print("Full period")
            [tstart, tstop, head] =set_full_range()
            plot_selected_period(tstart, tstop, head, tunit=1)

#----------------------------------------------------------------------------------
#-- plot_selected_period: create a plot for a specified peiod                    --
#----------------------------------------------------------------------------------

def plot_selected_period(tstart, tstop, head, tunit=0):
    """
    create a plot for a specified peiod
    input:  tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
            head    --- prefix of the plot file 
            tunit   --- indicator to tell whether this is full plot; default=0: no
    output: <web_dir>/Plots_new/<year>/<head>_bias.png (for full plot, without<year>)
            <web_dir>/Plots_new/<year>/<head>_hist.png (for full plot, without<year>)
    """

    year  = find_year(tstart + 3600.0)
    data  = read_data(tstart, tstop)
    dtime = data[0]
#
#--- bais plot
#
    if tunit == 0:
        outdir  = web_dir + 'Plots_new/' + str(year) 

        cmd     = 'mkdir -p ' + outdir
        os.system(cmd)

        outname = outdir + '/' + head + '_bias.png'
    else:
        outname = web_dir + 'Plots_new/' + head + '_bias.png'

    out = bias_plot(dtime, data[1]*rad2sec, data[3]*rad2sec, data[5]*rad2sec, outname, tunit)
    if out == False:
        return out
#
#--- hist plot
#
    if tunit == 0:
        outdir  = web_dir + 'Plots_new/' + str(year) 

        cmd     = 'mkdir -p ' + outdir
        os.system(cmd)

        outname = outdir + '/' + head + '_hist.png'
    else:
        outname = web_dir + 'Plots_new/' + head + '_hist.png'
#
#--- compute the shift from one data point to the data point
#
    shift = find_shift(data)

    hist_plot(shift[0], shift[1], shift[2], outname)

#----------------------------------------------------------------------------------
#-- read_data: for the give period, find data fits files and read it             --
#----------------------------------------------------------------------------------

def read_data(tstart, tstop):
    """
    for the give period, find data fits files and read it
    input:  tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output:  out    --- a list of arrays of data
                see: col_name for which data are extracted
    """
    byear = find_year(tstart)
    eyear = find_year(tstop)

    c_len = len(col_name)
    chk   = 0
    save  = []
    for year in range(byear, eyear+1):

        fits = data_dir + 'iru_gyro_bias_year' + str(year) + '.fits'
        try:
            fout = pyfits.open(fits)
            data = fout[1].data
            fout.close()
        except:
            continue
#
#--- for the case, first year or only one year data file to read:
#
        if chk == 0:
            for k in range(0, c_len):
                save.append(data[col_name[k]])
            chk = 1 
#
#--- reading the second year and append the data
#
        else:
            for k in range(0, c_len):
                temp    = numpy.append(save[k], data[col_name[k]])
                save[k] = temp

    out  = select_out_data(save, tstart, tstop)

    return out

#----------------------------------------------------------------------------------
#-- find_year: find year from the Chandra time                                   --
#----------------------------------------------------------------------------------

def find_year(stime):
    """
    find year from the Chandra time
    input:  stime   --- time in seconds from 1998.1.1
    output: year    --- year
    """
    date  = Chandra.Time.DateTime(stime).date
    atemp = re.split(':', date)
    year  = int(atemp[0])

    return year

#----------------------------------------------------------------------------------
#-- select_out_data: extract data for a specific period                         ---
#----------------------------------------------------------------------------------

def select_out_data(data, tstart, tstop):
    """
    extract data for a specific period
    input:  data    --- a list of arrays of data
            tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: save    --- a list of arrays of data of the specified time period
    """
#
#--- drop nan data
#
    dtime  = numpy.array(data[0])
    index  = ~numpy.isnan(dtime)
    dtime  = dtime[index]
#
#--- select data for the time period
#
    index2 = (dtime >= tstart) &(dtime < tstop)
    save  = []
    for  k in range(0, len(data)):
        atemp = numpy.array(data[k])
        btemp = atemp[index]
        ctemp = btemp[index2]

        save.append(ctemp)

    return save

#----------------------------------------------------------------------------------
#-- find_shift: compute the shift from the previous data points                  --
#----------------------------------------------------------------------------------

def find_shift(data):
    """
    compute the shift from the previous data points
    input:  data    --- a list of data
    output: save    --- a list of shift. len(save) = len(data) -1
    """
    save = []
    for k in [1, 3, 5]:
        adata = data[k]  * rad2sec
        shift = []
        for m in range(1, len(adata)):
            diff = adata[m] - adata[m-1]
            shift.append(diff)

        save.append(shift)

    return save

#----------------------------------------------------------------------------------
#-- bias_plot: create three panel plots of bias time trend                       --
#----------------------------------------------------------------------------------

def bias_plot(time, data1, data2, data3, outname, tunit=0):
    """
    create three panel plots of bias time trend
    input:  time    --- a list of time data in seconds from 1998.1.1
            data1   --- a list of data for the panel 1
            data2   --- a list of data for the panel 2
            data3   --- a list of data for the panel 3
            outname --- output file name
            tunit   --- indicator of full plot or not: default=0: no
    output: outname --- a png file
    """
#
#--- convert time format
#
    if len(time) == 0:
        return False

    [btime, byear] = convert_time_format(time, tunit)
#
#--- set ploting range
#
    try:
        [xmin, xmax] = set_x_range(btime)
    except:
        return False
#    
#--- set sizes
#
    fsize  = 8
    weight = 'bold'
    color  = 'blue'
    color2 = 'red'
    marker = '.'
    psize  = 0
    lw     = 1
    width  = 7.0
    height = 5.0
    resolution = 200
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size']   = fsize
    mpl.rcParams['font.weight'] = weight
    props = font_manager.FontProperties(size=fsize)
    props = font_manager.FontProperties(weight=weight)
    plt.subplots_adjust(hspace=0.05)
#
#--- first panel
    ax1 = plt.subplot(311)
    [ymin, ymax] = set_y_range(data1, tunit)
    ax1.set_autoscale_on(False)
    ax1.set_xbound(xmin,xmax)
    ax1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax1.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    p, = plt.plot(btime, data1, color=color, lw=lw, marker=marker, markersize=psize)

    ax1.set_ylabel("Roll Bias (arcsec/sec)", fontweight=weight)
#
#--- don't plot tick labels
#
    line = ax1.get_xticklabels()
    for label in line:
        label.set_visible(False)
#
#--- second panel
#
    ax2 = plt.subplot(312)
    [ymin, ymax] = set_y_range(data2, tunit)
    ax2.set_autoscale_on(False)
    ax2.set_xbound(xmin,xmax)
    ax2.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax2.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    p, = plt.plot(btime, data2, color=color, lw=lw, marker=marker, markersize=psize)

    ax2.set_ylabel("Pitch Bias (arcsec/sec)", fontweight=weight)
#
#--- don''t plot tick labels
#
    line = ax2.get_xticklabels()
    for label in line:
        label.set_visible(False)
#
#--- thrid panel
#
    ax3 = plt.subplot(313)
    [ymin, ymax] = set_y_range(data3, tunit)
    ax3.set_autoscale_on(False)
    ax3.set_xbound(xmin,xmax)
    ax3.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax3.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    p, = plt.plot(btime, data3, color=color, lw=lw, marker=marker, markersize=psize)

    ax3.set_ylabel("Yaw Bias (arcsec/sec)", fontweight=weight)
    
    if tunit == 0:
        line = 'Year Date (' + str(byear) + ')'
        xlabel(line, fontweight=weight)

    else:
        xlabel('Time (Year)', fontweight=weight)

#
#--- save the figure
#
    plt.subplots_adjust(bottom=0.05,hspace=0.01)
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout(h_pad=0.05)
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')

    return True

#----------------------------------------------------------------------------------
#-- hist_plot: create three panel histogram plot                                 --
#----------------------------------------------------------------------------------

def hist_plot(data1, data2, data3, outname):
    """
    create three panel histogram plot
    input:  data1   --- a list of data for the panel 1
            data2   --- a list of data for the panel 2
            data3   --- a list of data for the panel 3
            outname --- the output file name
    output: outname --- png file
    """
#
#--- set ploting range
#
    xmin = -0.02
    xmax =  0.02
#    
#--- set sizes
#
    fsize  = 8 
    weight = 'bold'
    color  = 'blue'
    color2 = 'red'
    marker = '.'
    psize  = 0
    lw     = 1
    width  = 7.0
    height = 5.0
    resolution = 300
    alpha  = 0.5
    bins   = 300
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size']   = fsize
    mpl.rcParams['font.weight'] = weight
    props = font_manager.FontProperties(size=fsize)
    props = font_manager.FontProperties(weight=weight)
#
#--- first panel
#
    ax1 = plt.subplot(311)
    n1, bins1, patches1 = plt.hist(data1, bins=bins, range=[xmin, xmax], facecolor=color,\
                                    alpha=alpha, histtype='stepfilled', log=True)
#
#--- fix the plotting range
#
    plt.xlim(xmin, xmax)

    ax1.text(0.05, 0.95, "Roll", transform=ax1.transAxes, fontsize=fsize, verticalalignment='top')
#
#--- remove the tix label for this plot
#
    line = ax1.get_xticklabels()
    for label in line:
        label.set_visible(False)
#
#--- second panel
#
    ax2 = plt.subplot(312)
    n2, bins2, patches2 = plt.hist(data2, bins=bins, range=[xmin, xmax], facecolor=color,\
                                    alpha=alpha, histtype='stepfilled', log=True)
    plt.xlim(xmin, xmax)

    ax2.text(0.05, 0.95, "Pitch", transform=ax2.transAxes, fontsize=fsize, verticalalignment='top')
    ax2.set_ylabel("Freq (arcsec/3600s shift)", fontweight=weight)
#
#--- remove the tix label for this plot
#
    line = ax2.get_xticklabels()
    for label in line:
        label.set_visible(False)
#
#--- thrid panel
#
    ax3 = plt.subplot(313)
    n3, bins3, patches3 = plt.hist(data3, bins=bins, range=[xmin, xmax], facecolor=color, \
                                    alpha=alpha, histtype='stepfilled', log=True)

    ax3.text(0.05, 0.95, "Yaw", transform=ax3.transAxes, fontsize=fsize, verticalalignment='top')
    plt.xlim(xmin, xmax)

    xlabel('Bias Drift Shift over 3600 sec', fontweight=weight)
#
#--- save the figure
#
    plt.subplots_adjust(bottom=0.05,hspace=0.01)
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout(h_pad=0.05)
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')

#----------------------------------------------------------------------------------
#-- convert_time_format: convert chandra time into either fractional year or day of year
#----------------------------------------------------------------------------------

def convert_time_format(t_list, dformat=0):
    """
    convert chandra time into either fractional year or day of year
    input:  t_list  --- a list of time in seconds from 1998.1.1
            dformat --- indicator of whether to convert fractional year or doy
                        default= 0: day of year
    output: save    --- a list of time in the specified format
            byear   --- the year of the data; useful to use with day of year 
                note: if the the data are over two years, byear is the year
                      of the starting year and day of year will increase 
                      beyond 365/366. 
    """
    save  = []
    byear = 0
    for ent in t_list:
        out   = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', out)
        year  = int(atemp[0])
        if byear == 0:
            byear = year
            if mcf.is_leapyear(byear):
                base = 366
            else:
                base = 365

        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])
        yday += hh / 24.0 + mm / 1440.0 + ss / 84600.0
#
#--- for the case that the time is in yday; assume that the range is always 
#--- smaller than two years
#
        if dformat == 0:
            if year > byear:
                yday += base

            save.append(yday)
#
#--- for the case that the time is in fractional year
#
        else:
            if year > byear:
                if mcf.is_leapyear(byear):
                    base = 366
                else:
                    base = 365

                byear = year

            fyear = year + yday / base
            save.append(fyear)

    return [save, byear]


#----------------------------------------------------------------------------------
#-- set_x_range: set x plotting range                                            --
#----------------------------------------------------------------------------------

def set_x_range(x, ichk=0):
    """
    set x plotting range
    input:  x       --- a list x values
            ichk    --- indicator if whether this is a year plot: default= 0: no
    output: xmin    --- x min
            xmax    --- x max
    """
    xmin = min(x)
    xmax = max(x)
    diff = xmax - xmin
    xmin -= 0.05 * diff
    xmax += 0.05 * diff
    if ichk == 0:
        xmin  = int(xmin)
        xmax  = int(xmax) + 1
    else:
        if abs(xmin) > xmax:
            xmax = -xmin
        else:
            xmin = -xmax

    return [xmin, xmax]

#----------------------------------------------------------------------------------
#-- set_y_range:  set y plotting range                                          ---
#----------------------------------------------------------------------------------

def set_y_range(y, chk=0):
    """
    set y plotting range
    input:  y       --- a list of y data
            ichk    --- indicator if whether this is a year plot: default= 0: no
    output: ymin    --- y min
            ymax    --- y max
    """
#
#--- range setting for full range plots
#
    if chk == 1:
        ymin  = -3.5
        ymax  =  1.0
    else:
        ymin  = numpy.percentile(y, 2.0)
#
#--- drop the exteme value
#
        ymax  = numpy.percentile(y, 98.0)
        diff  = ymax - ymin
        ymin -= 0.1 * diff
        ymax += 0.1 * diff
#
#--- don't make the plot larger than 0.6
#
#    if ymax > 0.6:
#        ymax = 0.6

    return [ymin, ymax]

#----------------------------------------------------------------------------------
#-- set_weekly_range: create a weekly plot range (Fri - Fri)                     --
#----------------------------------------------------------------------------------

def set_weekly_range(tday =''):
    """
    create a weekly plot range (Fri - Fri)
    input: tday     --- seconds from 1998.1.1; if it is given, create for that week interval dates
                        or date in yyyy:ddd:hh:mm:ss format
    output: tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
            pref    --- file header for the weekly plot
    """
#
#--- find today's date and week day
#
    if tday == '':
        tday   = time.strftime("%Y:%j:23:59:59", time.gmtime())
        tday   = Chandra.Time.DateTime(tday).secs
        tday2  = time.strftime("%Y:%m:%d", time.gmtime())
        tm     = re.split(':', tday2)
        wday   = int(datetime.date(int(tm[0]), int(tm[1]), int(tm[2])).strftime('%w'))
    else:
#
#--- if the date is given in Chandra time format
#
        try:
            tday  = float(tday)
            out   = Chandra.Time.DateTime(tday).date
            atemp = re.split('\.', out)
            out   = atemp[0].replace(':60', ':59')
            #wday = int(datetime.datetime.strptime(atemp[0], "%Y:%j:%H:%M:%S").strftime('%w'))
            wday = int(datetime.datetime.strptime(out, "%Y:%j:%H:%M:%S").strftime('%w'))
#
#--- if the date is given in yyyy:ddd:hh:mm:ss
#
        except:
            wday = int(datetime.datetime.strptime(tday, "%Y:%j:%H:%M:%S").strftime('%w'))
            tday = Chandra.Time.DateTime(tday).secs
#
#--- find time interval from Friday the last week to Friday this week
#
    tdiff  = 4 - wday
    tstop  = tday + tdiff * 86400.0
    tstart = tstop - 7.0  * 86400.0
#
#--- create a file header; 1 hr is added/subtructed to make sure that the dates are in the interval
#
    lstop  = Chandra.Time.DateTime(tstop  - 3600.0).date
    atemp  = re.split(':', lstop)
    ydate1 = atemp[1]

    lstart = Chandra.Time.DateTime(tstart + 3600.0).date
    atemp  = re.split(':', lstart)
    year   = atemp[0]
    ydate2 = atemp[1]

    pref   = year + '_' + ydate2 + '_' + ydate1

    return [int(tstart), int(tstop), pref]

#----------------------------------------------------------------------------------
#-- set_monthly_range: create a mnonthly plot range                             ---
#----------------------------------------------------------------------------------

def set_monthly_range(tday = ''):
    """
    create a mnonthly plot range
    input: tday     --- seconds from 1998.1.1; if it is given, create for that week interval dates
                        or date in yyyy:ddd:hh:mm:ss format
    output: tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
            pref    --- file header for the weekly plot
    """
#
#--- find today's date and week day
#
    if tday == '':
        tday = time.strftime("%Y:%m:%d", time.gmtime())
        atemp = re.split(':', tday)
        year  = int(atemp[0])
        mon   = int(atemp[1])
        mday  = int(atemp[2])
    else:
#
#--- if the time is given in Chandra time
#
        try:
            tday  = float(tday)
            out   = Chandra.Time.DateTime(tday).date
            atemp = re.split('\.', out)
            out   = atemp[0].replace(':60', ':59')
            #out   = datetime.datetime.strptime(atemp[0], "%Y:%j:%H:%M:%S").strftime('%Y:%m:%d')
            out   = datetime.datetime.strptime(out, "%Y:%j:%H:%M:%S").strftime('%Y:%m:%d')
#
#--- if the time is given in yyyy:ddd:hh:mm:ss
#
        except:
            out   = datetime.datetime.strptime(tday, "%Y:%j:%H:%M:%S").strftime('%Y:%m:%d')

        atemp = re.split(':', out)
        year  = int(atemp[0])
        mon   = int(atemp[1])
        mday  = int(atemp[2])
#
#--- if "today" is less than first 5 day of the month, give back the last month's date interval
#
    if mday < 5:
        mon -= 1
        if mon < 1:
            mon   = 12
            year -= 1

    emon  = mon + 1
    eyear = year
    if emon > 12:
        emon   = 1
        eyear += 1

    start = str(year)  + '-' + str(mon)  + '-01'
    start = (datetime.datetime.strptime(start, "%Y-%m-%d").strftime('%Y:%j:00:00:00'))
    start = Chandra.Time.DateTime(start).secs

    stop  = str(eyear) + '-' + str(emon) + '-01'
    stop  = (datetime.datetime.strptime(stop,  "%Y-%m-%d").strftime('%Y:%j:00:00:00'))
    stop  = Chandra.Time.DateTime(stop).secs

    lmon  = m_list[mon -1]
    lyear = str(year)
    pref  = lmon + lyear[2] + lyear[3]

    return [int(start), int(stop), pref]

#----------------------------------------------------------------------------------
#-- set_yearly_range: set time interval for the yearly data extraction           --
#----------------------------------------------------------------------------------

def set_yearly_range(year=''):
    """
    set time interval for the yearly data extraction
    input:  year    --- year of the data interval
    output: start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
            pref    --- header of the file
    """
#
#--- find  year of today
#
    if year == '':
        out   = time.strftime("%Y:%j", time.gmtime())
        atemp = re.split(':', out)
        year  = int(float(atemp[0]))
        yday  = int(float(atemp[1]))
#
#--- today is less than the 5th day of the year, use the previous year
#
        if yday < 5:
            year -= 1
    else:
        try:
            check = float(year)
#
#--- if the year is accidentaly given by chandra date, just find year
#
            if year > 3000:
                out   = Chandra.Time.DateTime(year).date
                atemp = re.split(':', out)
                year  = int(atemp[0])
        except:
            atemp = re.split(':', year)
            year  = int(atemp[0])

    year  = int(year)
    nyear = year + 1
    start = str(year)  + ':001:00:00:00'
    start = Chandra.Time.DateTime(start).secs
    stop  = str(nyear) + ':001:00:00:00'
    stop  = Chandra.Time.DateTime(stop).secs

    return [int(start), int(stop), str(year)]

#----------------------------------------------------------------------------------
#-- set_full_range: set time inteval for the full range plots                    --
#----------------------------------------------------------------------------------

def set_full_range():
    """
    set time inteval for the full range plots
    input:  none
    output: start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
            pref    --- header of the file
    """
#
#--- find today's date and week day
#
    start = 52531199                #--- 1999:244:00:00:00
    tday  = time.strftime("%Y:%j:00:00:00", time.gmtime())
    stop  = Chandra.Time.DateTime(tday).secs

    return [int(start), int(stop), 'total']

#----------------------------------------------------------------------------------
#--find_w_date: make a list of dates of a specific week yda in Chandara time    ---
#----------------------------------------------------------------------------------

def find_w_date(year, w=3):
    """
    make a list of dates of a specific week yda in Chandara time 
    input:  year    --- year
            w       --- weekday mon = 0; default 3: thu
    """
    save = []
    for d in findallwdays(year, w):
        tday  = (datetime.datetime.strptime(str(d), "%Y-%m-%d").strftime('%Y:%j:00:00:00'))
        stime = Chandra.Time.DateTime(tday).secs
        save.append(int(stime))

    return save

#----------------------------------------------------------------------------------
#-- findallwdays: return a list of date in yyyy-mm-dd for a given year and weekday 
#----------------------------------------------------------------------------------

def findallwdays(year, w):
    """
    return a list of date in yyyy-mm-dd for a given year and weekday
    input:  year    --- year
            w       --- weekday mon = 0; default 3: thu
    """
    d = datetime.date(year, 1, 1)
    d += datetime.timedelta(days = w - d.weekday())
    while d.year <= year:
        yield d
        d += datetime.timedelta(days = 7)

#----------------------------------------------------------------------------------
#-- add_empty_plot_page: create empty plots if the regular plots are created for the previous period 
#----------------------------------------------------------------------------------

def add_empty_plot_page(period):
    """
    create empty plots if the regular plots are created for the previous period
    input:  period  --- 'mon' or 'year'; which period to caeate the empnty plots
    output: <wb_dir>/Plot_new/<head>_<hist/bias>.png
    """
#
#--- today's date
#
    out   = time.strftime('%y:%m:%d:%Y:%j', time.gmtime())
    atemp = re.split(':', out)
    year  = atemp[0]
    mon   = int(float(atemp[1]))
    mday  = int(float(atemp[2]))
    fyear = atemp[3]
    yday  = int(float(atemp[4]))
    chk   = 0
#
#--- if this is for month plot, check whether today is less than 5th day of the month
#
    if period == 'mon':
        if mday < 5:
            lmon = m_list[mon-1]
            head = lmon + year
            chk  = 1
#
#--- if this is for year plot, check whether today is less than 5th day of the year
#
    else:
        if yday < 5:
            head = fyear
            chk  = 1
#
#--- if so, create the empty plots
#
    if chk > 0:
        odir  =  web_dir + 'Plots_new/' + str(fyear) + '/'
        for tail in ['bias', 'hist']:
            out = odir + head + '_' + tail + '.png'
            cmd = 'cp ' + house_keeping + 'no_plot.png ' + out 
            os.system(cmd)


#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------
    def test_set_weekly_range(self):

        test  = 647740794
        thead = '2018_187_193'
        [start, stop, pref] = set_weekly_range(test)

        print("Weekly setting:  "  + str(start) +'<-->' +  str(stop) + '<--->' +  pref)
        print("Expected:        "  + str(647222394) + '<-->' + str(647827194) + '<--->' + thead)

        test  = '2018:001:00:00:00'
        [start, stop, pref] = set_weekly_range(test)
        print("\nWeekly setting2: "  + str(start) +'<-->' +  str(stop) + '<--->' +  pref)
        print("\n\n")

#------------------------------------------------------------

    def test_set_monthly_range(self):

        test  = 647740794
        [start, stop, pref] = set_monthly_range(test)
        print("Monthly setting:  "  + str(start) +'<-->' +  str(stop) + '<--->' +  pref)
        print("Expected:         646790469<-->649468869<--->jul18")

        test  = '2018:001:00:00:00'
        [start, stop, pref] = set_monthly_range(test)
        print("\nMonthly setting2: "  + str(start) +'<-->' +  str(stop) + '<--->' +  pref)
        print("\n\n")

#------------------------------------------------------------

    def test_set_yearly_range(self):

        year = 2017
        [start, stop, pref] = set_yearly_range(year)
        print("Yearly setting: "  + str(start) +'<-->' +  str(stop) + '<--->' +  pref)

#----------------------------------------------------------------------------------

if __name__ == "__main__":


    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            sys.argv = [sys.argv[0]]
            unittest.main()
        
            exit(1)
        elif sys.argv[1] == 't':
            run = ['w', 'm', 'y', 't']
            stime = ''

        elif sys.argv[1].lower() in ['h', '-h','-help']:
            print("Usage: create_iru_bias_plots.py <ind>")
            print("<ind>:   test    --- run unit test")
            print("         t       --- create all plots")
            print("         time    --- time where you want to create plots (week, month, year)")
            print("         \"\"      --- create plots for the most recent period for all\n\n")
            print("create_iru_bias_plots.py <ind> <time>")
            print("         ind     --- string of combination of: 'w', 'm', 'y', 't' e.g, wmy")
            print("         time    --- time in Chandra time or format of <yyyy>:<ddd>:<hh>:<mm>:<ss>")
            exit(1)

        else:
            try:
                stime = float(sys.argv[1])
            except:
                stime = ''

            run = ['w', 'm', 'y']

    elif len(sys.argv) == 3:
        ind = sys.argv[1]
        try:
            stime = float(sys.argv[2])
        except:
            stime = sys.argv[2]

        run = []
        for ent in sys.argv[1]:
            run.append(ent)

    else:
        run = ['w', 'm', 'y', 't']
        stime = ''

    create_iru_bias_plots(run=run, stime= stime)


##
##---- recovering the plots
##
#
#    for year in range(1999, 2019):
#        print "YEAR: " + str(year)
#            run   = ['y',]
#            create_iru_bias_plots(run=run, stime=year)
#
#    for year in range(1999, 2019):
#        out = find_w_date(year)
#        for stime in out:
#            print "TIME: " + Chandra.Time.DateTime(stime).date
#         
#            if stime < 52531199:
#                continue
#            if stime > 648691194:
#                break
#         
#            run = ['w', 'm']
#            create_iru_bias_plots(run=run, stime= stime)
#
