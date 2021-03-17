#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       plot_grating_zero_orders.py: update grating zero_order plots                            #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Jul 13, 2018                                                           #
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
path = '/data/mta/Script/Grating/Zero/Scripts/house_keeping/dir_list'

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

col_name = ['sky_x', 'sky_y', 'chip_x', 'chip_y']

#----------------------------------------------------------------------------------------------
#-- update_zero_order_data_plot: update grating zero_order plots                                      ---
#----------------------------------------------------------------------------------------------

def update_zero_order_data_plot():
    """
    update grating zero_order plots
    input:  none, but <data_dir>/acis_hetg, acis_letg, hrc_letg
    output: <web_dir>/Plots/<d_file>_<col_name>_zero_order.phg
    """
    for d_file in ['acis_hetg', 'acis_letg', 'hrc_letg']:
        out  = read_data(d_file)
        time = out[0]
        for k in range(0, len(col_name)):
            outname = web_dir + 'Plots/'  + d_file +'_' + col_name[k] +  '_zero_order.png'
            data    = out[k + 1]
            y_label = col_name[k].replace('_', ' ')

            plot_data(time, data, y_label.upper(), outname)

#----------------------------------------------------------------------------------------------
#-- plot_data: plot data                                                                     --
#----------------------------------------------------------------------------------------------

def plot_data(xdata, ydata, y_label, outname):
    """
    plot data
    input:  xdata   --- x data
            ydata   --- y data
            grating --- tile of the data
            outname --- output plot file; assume it is png
    output: hetg_all_zero_order.png, metg_all_zero_order.png, letg_all_zero_order.png
    """
#    
#--- set sizes
#
    fsize  = 18
    color  = 'blue'
    color2 = 'red'
    marker = '.'
    psize  = 4
    lw = 3
    alpha  = 0.3
    width  = 10.0
    height = 5.0
    resolution = 200

    xmin = 1999
    xmax = max(xdata) 
    diff = xmax - int(xmax)
    if diff > 0.7:
        xmax = int(xmax) + 2
    else:
        xmax = int(xmax) + 1
#
#--- remove extreme values
#
    [x, y] = remove_extreme(xdata, ydata)
    ymin   = min(y)
    ymax   = max(y)
    diff   = ymax - ymin
    ymin  -= 0.1 * diff
    ymax  += 0.1 * diff

#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
#
#--- set plotting range
#
    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    plt.plot(xdata, ydata, color=color, marker=marker, markersize=psize, lw=0)

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
    plt.xlabel('Time (year)')
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

    index = [(y > bot) & (y < top)]
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
            c1_list --- a list of data (sky_x)
            c2_list --- a list of data (sky_y)
            c3_list --- a list of data (chip_x)
            c4_list --- a list of data (chip_y)
    """
    infile = data_dir + infile

    f    = open(infile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    t_list  = []
    c1_list = []
    c2_list = []
    c3_list = []
    c4_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        try:
            t  = convert_time_format(int(atemp[0]))
            v1 = float(atemp[1])
            v2 = float(atemp[2])
            v3 = float(atemp[3])
            v4 = float(atemp[4])
        except:
            continue

        t_list.append(t)
        c1_list.append(v1)
        c2_list.append(v2)
        c3_list.append(v3)
        c4_list.append(v4)

    return [t_list, c1_list, c2_list, c3_list, c4_list]

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

    update_zero_order_data_plot()
            
