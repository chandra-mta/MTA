#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       plot_grating_focus.py: update grating focus plots                                       #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Jul 17, 2018                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import random
import numpy
import time
import Chandra.Time

import matplotlib as mpl

if __name__ == '__main__':
    mpl.use('Agg')

#
#--- reading directory list
#
path = '/data/mta/Script/Grating/Focus/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import convertTimeFormat        as tcnv
import mta_common_functions     as mcf
import find_moving_average      as mavg       #---- contains moving average routine
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------------------
#-- update_focus_data_plot: update grating focus plots                                      ---
#----------------------------------------------------------------------------------------------

def update_focus_data_plot():
    """
    update grating focus plots
    input:  none, but <data_dir>/acis_hetg, acis_letg, hrc_letg
    output: <web_dir>/Plots/<d_file>_<ax_lrf/streak_lrf>_focus.phg
    """
    for d_file in ['acis_hetg', 'acis_letg', 'hrc_letg']:
        out   = read_data(d_file)
        time  = out[0]
        try:
            a_set = [out[1], out[2], out[5], out[7]]
        except:
            continue

        [ctime, c_set] = remove_non_data(time, a_set)
        titles         = ['AX LRF at 10% Peak', 'AX LRF at 50% Peak', 'Gaussian FWHM']
        outname        = web_dir + 'Plots/' + d_file + '_ax_lrf_focus.png'
        y_label        = 'Width (microns)'
        y_limits       = [[50,110], [20, 60], [20,60]]
        plot_data(ctime, c_set, titles, outname, y_label, y_limits)


        try:
            s_set = [out[3], out[4], out[6], out[8]]
        except:
            continue

        [ctime, c_set] = remove_non_data(time, a_set)
        titles         = ['Streak LRF at 10% Peak', 'Streak LRF at 50% Peak', 'Gaussian FWHM']
        outname        = web_dir + 'Plots/' + d_file + '_streak_lrf_focus.png'
        y_label        = 'Width (microns)'
        y_limits       = [[50, 110], [20, 60], [20, 60]]
        plot_data(ctime, c_set, titles, outname, y_label, y_limits)

#----------------------------------------------------------------------------------------------
#-- remove_non_data: removing non (-999) data and data outside of the useable valeus         --
#----------------------------------------------------------------------------------------------

def remove_non_data(x, t_set):
    """
    removing non (-999) data and data outside of the useable valeus
    input:  x       --- time
            t_set   --- a list of 4 lists; first three are value list and last one error list 
    output: x       --- cleaned time entry
            o_set   --- a list of cleaned three value lists. no error list are retured
    """
    x     = numpy.array(x)
    yarray = []
    for k in range(0, 4):
        yarray.append(numpy.array(t_set[k]))


    for k in range(0, 2):
        index = [(yarray[k] > 0) & (yarray[k] < 100)]
        x = x[index]
        for m in range(0, 4):
            yarray[m] = yarray[m][index]
        
    index = [yarray[3] < 10]
    x = x[index]
    for m in range(0, 4):
        yarray[m] = yarray[m][index]

    return [x, [list(yarray[0]),  list(yarray[1]), list(yarray[2])]]
        
#----------------------------------------------------------------------------------------------
#-- plot_data: plot data                                                                     --
#----------------------------------------------------------------------------------------------

def plot_data(xdata, y_set, titles, outname, y_label, y_limits):
    """
    plot data
    input:  xdata   --- x data
            ydata   --- y data
            grating --- tile of the data
            outname --- output plot file; assume it is png
    output: hetg_all_focus.png, metg_all_focus.png, letg_all_focus.png
    """
#    
#--- set sizes
#
    fsize  = 18
    color  = 'blue'
    color2 = 'red'
    marker = '.'
    psize  = 8
    lw = 3
    alpha  = 0.3
    width  = 10.0
    height = 10.0
    resolution = 200

    xmin = 1999
    xmax = max(xdata) 
    diff = xmax - int(xmax)
    if diff > 0.7:
        xmax = int(xmax) + 2
    else:
        xmax = int(xmax) + 1
    diff = xmax - xmin
    xpos = xmin + 0.02 * diff

#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
    plt.subplots_adjust(hspace=0.08)
#
#--- set plotting range
#
    for k in range(0, 3):
        plt.subplots_adjust(hspace=0.08)
        ymin   = y_limits[k][0]
        ymax   = y_limits[k][1]
        diff   = ymax - ymin
        ypos   = ymax - 0.1 * diff

        panel = '31' + str(k+1)
        ax  = plt.subplot(panel)
        ax.set_autoscale_on(False)
        ax.set_xbound(xmin,xmax)
        ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
        ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
    
        plt.plot(xdata, y_set[k], color=color, marker=marker, markersize=psize, lw=0)
        plt.tight_layout()

        [x, y] = remove_extreme(xdata, y_set[k])
        [xv, movavg, sigma, min_sv, max_sv, ym, yb, yt, y_sig] = mavg.find_moving_average(x, y, 1.0, 3, nodrop=0)
#
#--- plot envelopes
#
        plt.plot(xv, yb, color=color2, marker=marker, markersize=0, lw=lw, alpha=alpha)
        plt.plot(xv, ym, color=color2, marker=marker, markersize=0, lw=lw, alpha=alpha)
        plt.plot(xv, yt, color=color2, marker=marker, markersize=0, lw=lw, alpha=alpha)
#
#--- add label
#
        plt.text(xpos, ypos, titles[k], color=color)
        if k == 2:
            plt.xlabel('Time (year)')
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
            if k == 1:
                plt.ylabel(y_label)


    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------

def remove_extreme(x, y):

    x = numpy.array(x)
    y = numpy.array(y)
    avg = numpy.mean(y)
    sig = numpy.std(y)
    bot = avg - 3.0 * sig
    top = avg + 3.0 * sig

    index = [(y >0) & (y < 300)]
    x = x[index]
    y = y[index]

    return [x, y]

#----------------------------------------------------------------------------------------------
#-- read_data: read data file and extract data needed                                        --
#----------------------------------------------------------------------------------------------

def read_data(infile):
    """
    read data file and return lists of times and values
    input:  infile  --- data file name
    output: t_list  --- a list of time data
            c1_list --- a list of data (ax slf 10%)
            c2_list --- a list of data (ax slf 50%)
            c3_list --- a list of data (streak slf 10%)
            c4_list --- a list of data (streak slf 50%)
            c5_list --- a list of data (ax slf fwhm)
            c6_list --- a list of data (streak slf fwhm)
            c7_list --- a list of data (ax slf fwhm error)
            c8_list --- a list of data (streak slf fwhm error)
    """
    infile = data_dir + infile
    print "Data: " + str(infile)

    f    = open(infile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    t_list  = []
    c1_list = []
    c2_list = []
    c3_list = []
    c4_list = []
    c5_list = []
    c6_list = []
    c7_list = []
    c8_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        try:
            t  = convert_time_format(float(atemp[0]))
            v1 = float(atemp[1])
            v2 = float(atemp[2])
            v3 = float(atemp[3])
            v4 = float(atemp[4])
            v5 = float(atemp[5])
            v6 = float(atemp[6])
            v7 = float(atemp[6])
            v8 = float(atemp[6])
        except:
            continue

        t_list.append(t)
        c1_list.append(v1)
        c2_list.append(v2)
        c3_list.append(v3)
        c4_list.append(v4)
        c5_list.append(v5)
        c6_list.append(v6)
        c7_list.append(v7)
        c8_list.append(v8)

    return [t_list, c1_list, c2_list, c3_list, c4_list, c5_list, c6_list, c7_list, c8_list]

#----------------------------------------------------------------------------------------------
#-- convert_time_format: convert time in seconds from 1998.1.1 to a fractional year          --
#----------------------------------------------------------------------------------------------

def convert_time_format(atime):
    """
    convert time in seconds from 1998.1.1 to a fractional year
    input:  atime   --- time in seconds from 1998.1.1
    output: otime   --- time in a fractional year
    """

    date = Chandra.Time.DateTime(atime).date

    atemp = re.split(':', date)
    year  = float(atemp[0])
    yday  = float(atemp[1])
    hh    = float(atemp[2])
    mm    = float(atemp[3])
    ss    = float(atemp[4])

    if tcnv.isLeapYear(year) == 1:
        base = 366.0
    else:
        base = 365.0


    otime = year + yday / base + hh / 24.0 + mm / 1440.0 + ss / 86400.0

    return otime

#---------------------------------------------------------------------------------------------

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines


if __name__ == "__main__":

    update_focus_data_plot()
            
