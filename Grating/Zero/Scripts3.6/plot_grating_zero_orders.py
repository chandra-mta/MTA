#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################################
#                                                                                               #
#       plot_grating_zero_orders.py: update grating zero_order plots                            #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Aug 29, 2019                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import random
import numpy
import time

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
path = '/data/mta/Script/Grating/Zero/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions     as mcf
import find_moving_average      as mavg       #---- contains moving average routine

col_name = ['sky_x', 'sky_y', 'chip_x', 'chip_y']

#----------------------------------------------------------------------------------------------
#-- update_zero_order_data_plot: update grating zero_order plots                            ---
#----------------------------------------------------------------------------------------------

def update_zero_order_data_plot():
    """
    update grating zero_order plots
    input:  none, but <data_dir>/acis_hetg, acis_letg, hrc_letg
    output: <web_dir>/Plots/<d_file>_<col_name>_zero_order.phg
    """
    for d_file in ['acis_hetg', 'acis_letg', 'hrc_letg']:
        out  = read_zero_data(d_file)
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
    ax.set_xlim(left=xmin,   right=xmax, auto=False)
    ax.set_ylim(bottom=ymin, top=ymax,   auto=False)

    plt.plot(xdata, ydata, color=color, marker=marker, markersize=psize, lw=0)

    [xv, movavg, sigma, min_sv, max_sv, ym, yb, yt, y_sig] \
                            = mavg.find_moving_average(x, y, 1.0, 3, nodrop=0)
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
#-- remove_extreme: remove extreme data points                                               --
#----------------------------------------------------------------------------------------------

def remove_extreme(x, y):
    """
    remove extreme data points
    input:  x   --- a list of x values
            y   --- a list of y values
    output: [x, y]
    """
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
#-- read_zero_data: read data file and extract data needed                                   --
#----------------------------------------------------------------------------------------------

def read_zero_data(infile):
    """
    read data file and return lists of times and values
    input:  infile  --- data file name
    output: t_list  --- a list of time data
            c1_list --- a list of data (sky_x)
            c2_list --- a list of data (sky_y)
            c3_list --- a list of data (chip_x)
            c4_list --- a list of data (chip_y)
    """
    infile  = data_dir + infile
    data    = mcf.read_data_file(infile)
    dout    = mcf.separate_data_to_arrays(data)

    t_list  = [mcf.chandratime_to_fraq_year(x) for x in dout[0]]
    c1_list = dout[1]
    c2_list = dout[2]
    c3_list = dout[3]
    c4_list = dout[4]

    return [t_list, c1_list, c2_list, c3_list, c4_list]

#---------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_zero_order_data_plot()
            
