#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#               plot_gyro_drift_trends.py: plot gryo drift trends                               #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 09, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
#
#--- plotting routine
#
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
path = '/data/mta/Script/Gyro/Scripts/house_keeping/dir_list'

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
#--- import several functions
#
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
import find_moving_average        as mavg       #---- contains moving average routine
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
catg_list    = ['roll', 'pitch', 'yaw']

#---------------------------------------------------------------------------------------
#-- plot_gyro_drift_trends: plot gyro drinf trends                                    --
#---------------------------------------------------------------------------------------

def plot_gyro_drift_trends():
    """
    plot gyro drinf trends
    input:  none, but read from <data_dir>/gyro_drift_<catg>_<grating>_<action>
    output: <web_dir>/Trending_plots/<catg>_<grating>_<action>_<position>.png
                <postion> can be: before, during, after, db_ratio, ad_ratio, or ba_ratio
    """
#
#--- set the end of the x plot range
#
    lyear  = time.strftime("%Y", time.gmtime())
    lyear  = int(lyear) + 1
#
#--- go through all data set to create several sub html pages related to indivisual fitting resluts
#
    for catg in catg_list:
        for grating in ['hetg', 'letg']:
            for action in ['insr', 'retr']:
                ifile  = data_dir + 'gyro_drift_' + catg + '_' + grating + '_' + action
                data   = mcf.read_data_file(ifile)
                data   = mcf.separate_data_to_arrays(data, com_out='#')
                data   = select_data(data)
#
#--- convert time into fractional year
#
                x = convert_time_to_year(data[0])
#
#--- std of before the movement
#
                y = get_std_part(data[1])
                out    = web_dir + 'Trending_plots/' + catg + '_' + grating + '_' + action + '_before.png'
                plot_data(x, y, 1999, lyear, 0.0, 2.0,  'Time (year)', catg, out)
#
#--- std of during the movement
#
                y = get_std_part(data[2])
                out    = web_dir + 'Trending_plots/' + catg + '_' + grating + '_' + action + '_during.png'
                plot_data(x, y, 1999, lyear, 0.0, 2.0, 'Time (year)', catg, out)
#
#--- std of after the movement
#
                y = get_std_part(data[3])
                out    = web_dir + 'Trending_plots/' + catg + '_' + grating + '_' + action + '_after.png'
                plot_data(x, y, 1999, lyear, 0.0, 2.0, 'Time (year)', catg, out)
#
#--- ratio of stds of before and during the movement
#
                y  = data[4]                
                out    = web_dir + 'Trending_plots/' + catg + '_' + grating + '_' + action + '_bd_ratio.png'
                plot_data(x, y, 1999, lyear, 0.0, 4.0, 'Time (year)', catg, out)
#
#--- ratio of stds of after and during the movment
                y  = data[5]                
                out    = web_dir + 'Trending_plots/' + catg + '_' + grating + '_' + action + '_ad_ratio.png'
                plot_data(x, y, 1999, lyear, 0.0, 4.0, 'Time (year)', catg, out)
#
#--- ratio of stds of before and after the movement
#
                y  = data[6]                
                out    = web_dir + 'Trending_plots/' + catg + '_' + grating + '_' + action + '_ba_ratio.png'
                plot_data(x, y, 1999, lyear, 0.0, 4.0, 'Time (year)', catg, out)

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def select_data(data):

    save = []
    for m in range(0, 8):
        save.append([])

    for k in range(0, len(data[0])):
        if data[7][k] > 100:
            continue
        for m in range(0, 8):
            save[m].append(data[m][k])

    return save

#---------------------------------------------------------------------------------------
#-- convert_time_to_year: converting Chandra time to fractional year                  --
#---------------------------------------------------------------------------------------

def convert_time_to_year(tlist):
    """
    converting Chandra time to fractional year
    input:  tlist   --- a list of time in format of seconds from 1998.1.1
    output: save    --- a list of time in format of fractional year
    """
    save = []
    for ent in tlist:
        ldate = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', ldate)
        year  = float(atemp[0])
        yday  = float(atemp[1])
        hh= float(atemp[2])
        mm= float(atemp[3])
        ss= float(atemp[4])
    
        if mcf.is_leapyear(year):
            base = 366.0
        else:
            base = 365.0
     
        fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base
        save.append(fyear)

    return save


#---------------------------------------------------------------------------------------
#-- get_std_part: extract std part of the data (assuming <avg>+/-<std>                --
#---------------------------------------------------------------------------------------

def get_std_part(data):
    """
    extract std part of the data (assuming <avg>+/-<std>
    input:  data    --- data list
    output: save    --- a list of std data
    """
    save = []
    for ent in data:
        atemp = re.split('\+\/\-', ent)
        save.append(float(atemp[1]))

    return save

#---------------------------------------------------------------------------------------
#-- plot_data: plotting data                                                          --
#---------------------------------------------------------------------------------------

def plot_data(x, y, xmin, xmax, ymin, ymax, xlabel, ylabel, outname):
    """
    plotting data
    input:  x       --- a list of x data
            y       --- a list of y dta
            xmin    --- xmin
            xmax    --- xmax
            ymin    --- ymin
            ymax    --- ymax
            xlabel  --- label for x axis
            ylabel  --- label for y axis
            outname --- output file name
    output: outname --- png plot file
    """
#
#--- remove extreme data points
#
    [x, y] = remove_extreme(x, y)

#    [ymin, ymax] = find_y_range(y)
#--- set sizes
#
    fsize      = 18
    color      = 'blue'
    color2     = 'red'
    marker     = '.'
    psize      = 4
    lw         = 4
    width      = 10.0
    height     = 4.0
    resolution = 200
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
#
#--- find moving average
#
    [xv, movavg, sigma, min_sv, max_sv, ym, yb, yt, y_sig] = mavg.find_moving_average(x, y, 1, 4, nodrop=3)
#
#--- plot data
#
    plt.plot(x, y, color=color, marker=marker, markersize=psize, lw=0)
#
#--- plot envelopes
#
    plt.plot(xv, yb, color=color2, marker=marker, markersize=0, lw=lw)
    plt.plot(xv, ym, color=color2, marker=marker, markersize=0, lw=lw)
    plt.plot(xv, yt, color=color2, marker=marker, markersize=0, lw=lw)
#
#--- add label
#
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
#
#--- save the plot in png format
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')


#---------------------------------------------------------------------------------------
#-- remove_extreme: remove extreme values                                            ---
#---------------------------------------------------------------------------------------

def remove_extreme(x, y):
    """
    remove extreme values
    input:  x   --- a list of x
            y   --- a list of y
    output: x   --- a list of x extreme removed
            y   --- a list of y extreme removed
    """
    x   = numpy.array(x)
    y   = numpy.array(y)

    avg = numpy.mean(y)
    std = numpy.std(y)
    #top = avg + 3.5 * std
    top = avg + 3.0 * std

    ind = y < top
    x   = list(x[ind])
    y   = list(y[ind])

    return [x, y]


#---------------------------------------------------------------------------------------
#-- find_y_range: set y plotting range                                                --
#---------------------------------------------------------------------------------------

def find_y_range(data):
    """
    set y plotting range
    input:  data    --- a list of data
    output: ymin / ymax
    """

    ymin  = min(data)
    ymax  = max(data)
    diff  = ymax - ymin 

    ymin -= 0.1 * diff
    if ymin < 0:
        ymin = 0.0
    ymax += 0.1 * diff

    return [ymin, ymax]


#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_gyro_drift_trends()
