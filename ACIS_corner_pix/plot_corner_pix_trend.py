#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       # 
#   plot_corner_pix_trend.py: create trending plots related acis corner pixels          #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 03, 2021                                                       #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import numpy
import time 
import Chandra.Time

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
path = '/data/mta/Script/Corner_pix/Scripts/house_keeping/dir_list'

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
import robust_linear        as robust

col_snames = ['slope', 'norm_cent', 'norm_cent_s', 'norm_width', 'norm_width_s', \
             'skew_cent', 'skew_cent_s', 'skew_width', 'skew_width_s', 'skewness']

col_dnames = ['Slope', 'Norm Centroid', 'Norm Centrodi STD', 'Norm Width', 'Norm Width STD', \
             'Skew Mu', 'Skew Mu STD', 'Skew Width', 'SKew Width STD', 'Skewness']

#-------------------------------------------------------------------------------
#-- plot_corner_pix_trend: create trending plots related acis corner pixels   --
#-------------------------------------------------------------------------------

def plot_corner_pix_trend():
    """
    create trending plots related acis corner pixels 
    input: none but read from <data_dir>/<ccd>_<dtype>.dat
    ouptput:<plot_dir>/<ccd>_<dtype>_<col_name>.png
    """
    for ccd in ['I2', 'I3', 'S2', 'S3']:
        dsave = []
        for dtype in ['faint', 'vfaint', 'afaint']:

            ifile = data_dir + ccd + '_'+ dtype + '.dat'
            data  = mcf.read_data_file(ifile)
#
#--- top three lines are the header
#
            data  = data[3:]
#
#--- combine faint and vfaint data to create all data plots
#
            if dtype in ['faint', 'vfaint']:
                dsave = dsave + data

            plot_each_column_data(data, ccd, dtype)
#
#--- create "all data" plots
#
        plot_each_column_data(dsave, ccd, 'all')

#-------------------------------------------------------------------------------
#-- plot_each_column_data: create a trending plot for each column             --
#-------------------------------------------------------------------------------

def plot_each_column_data(data, ccd, dtype):
    """
    create a trending plot for each column 
    input:  data    --- a list of data
            ccd     --- ccd nmae
            dtype   --- data type
    output: <plot_dir>/<ccd>_<dtype>_<col_name>.png
    """
#
#--- separate the data by columns
#
    dlist = mcf.separate_data_into_col_data(data)
#
#--- convert time from Chandra time to fractional year
#
    t_list = []
    for ent in dlist[0]:
        ftime = mcf.chandratime_to_fraq_year(ent)
        t_list.append(ftime)
#
#--- there are 10 different quantities to trend
#
    for k in range(0, 10):
        cpos  = k + 2                   #--- seond entry is obsid; so start from third one
        pdata = dlist[cpos] 
#
#--- clean up the data by dropping none numerical data points
#
        [ctime, cdata] = clean_up_data(t_list, pdata)
#
#--- create trending plot for each data
#
        create_trend_data_plot(ctime, cdata, ccd, dtype,  col_snames[k], col_dnames[k])

#-------------------------------------------------------------------------------
#-- clean_up_data: clean up the data by dropping none numerical data points   --
#-------------------------------------------------------------------------------

def clean_up_data(x, y):
    """
    clean up the data by dropping none numerical data points
    input:  x   --- a list of x data
            y   --- a list of y data; this one will be checked
    output: c1  --- a list of x data cleaned
            c2  --- a list of y data cleaned
    """
    c1 = []
    c2 = []
    for m in range(0, len(y)):
        try:
            val = float(y[m])
            if str(val) == 'nan':
                continue
            c1.append(x[m])
            c2.append(val)
        except:
            continue

    return [c1, c2]

#-------------------------------------------------------------------------------
#-- create_trend_data_plot: create a trend plot                               --
#-------------------------------------------------------------------------------

def create_trend_data_plot(x, y, ccd, dtype, col_name, col_dname):
    """
    create a trend plot
    input:  x           --- a list of x data
            y           --- a list of y data
            ccd         --- ccd name
            dytpe       --- data type
            col_name   --- short-hand column name
            col_dname  --- full column name
    output: <plot_dir>/<ccd>_<dtype>_<col_name>.png
    """
#
#--- fit a trend line
#
    [intc, slope, err] = robust.robust_fit(x, y)
#
#--- set plotting range
#
    [xmin, xmax, ymin, ymax] = set_plotting_range(x, y)

    plt.close('all')
    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(left=xmin,   right=xmax, auto=False)
    ax.set_ylim(bottom=ymin, top=ymax,   auto=False)
#
#--- plot data
#
    plt.plot(x, y, color='blue', marker='.', markersize='1', lw=0)
#
#--- plot trending line
#
    yb = intc + slope * xmin
    ye = intc + slope * xmax
    plt.plot([xmin,xmax], [yb, ye], color='red', marker='.', markersize='1', lw=2)
#
#--- label axes
#
    plt.xlabel('Time (year)')
    plt.ylabel(col_dname)
#
#--- save the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10, 5)

    outname = plot_dir +  ccd + '_' + dtype + '_' + col_name + '.png'

    plt.savefig(outname, format='png', dpi=200)

#-------------------------------------------------------------------------------
#-- set_plotting_range: set plotting range                                    --
#-------------------------------------------------------------------------------

def set_plotting_range(x, y):
    """
    set plotting range
    input:  x   --- a list of x data
            y   --- a list of y data
    output: xmin, xmax, ymin, ymax
    """
    xmin  = 1999
    xmax  = max(x)
    ixmax = int(xmax)
    diff  = xmax - ixmax
    if diff > 0.5:
        xmax = ixmax + 2
    else:
        xmax = ixmax + 1

    yavg  = numpy.mean(y)
    ystd  = numpy.std(y)

    ymin = yavg - 3.2 * ystd 
    ymax = yavg + 3.2 * ystd

    return [xmin, xmax, ymin, ymax]

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_corner_pix_trend()
