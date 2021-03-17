#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#           ede_plot.py:    plotting evolution of EdE for ACIS S and HRC S grating obs      #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Mar 09, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import math
import time
import Chandra.Time
import numpy

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
path = '/data/mta/Script/Grating/EdE_trend/Scripts/house_keeping/dir_list_py'

with open(path, 'r') as f:
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
import robust_linear        as robust
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#-- run_ede_plot: find the data files and plots the data                          --
#-----------------------------------------------------------------------------------

def run_ede_plot():
    """
    find the data files and plots the data
    input: none but read from <data_dir>
    output: *_plot.png/*_low_res_plot.png --- two plots; one is in 200dpi and another in 40dpi
    """
    cmd = 'ls ' + data_dir + '*_data > ' + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    for ifile in data:
        ede_plots(ifile)

#-----------------------------------------------------------------------------------
#-- ede_plots: plotting time evolution of EdE                                    ---
#-----------------------------------------------------------------------------------

def ede_plots(ifile):
    """
    plotting time evolution of EdE
    input:  file    --- a file name of data
    output: *_plot.png/*_low_res_plot.png --- two plots; one is in 200dpi and another in 40dpi
    """
#
#--- read data
#
    [xdata, ydata, yerror] = read_ede_data(ifile)
#
#--- set plotting range
#
    [xmin, xmax, ymin, ymax] = set_min_max(ydata)
    ymax = 2100

    xname = 'Time (year)'
    yname = 'EdE'
    label = create_label(ifile)
    [out1, out2] = set_out_names(ifile)
#
#--- create two figures. One is 200dpi and another for 40dpi. 
#--- the low res plot is great for the intro page
#
    plot_single_panel(xmin, xmax, ymin, ymax, xdata, ydata, yerror,\
                      xname, yname, label, out1, resolution=200)

    plot_single_panel(xmin, xmax, ymin, ymax, xdata, ydata, yerror, \
                      xname, yname, label, out2, resolution=40)

#-----------------------------------------------------------------------------------
#-- set_min_max: set plotting range                                              ---
#-----------------------------------------------------------------------------------

def set_min_max(ydata):
    """
    set plotting range
    Input:  ydata   ---- ydata
    Output: [xmin, xmax, ymin, ymax]
    """
    xmin  = 1999
    xmax  = int(time.strftime('%Y', time.gmtime())) + 1

    ymin  = min(ydata)
    ymax  = max(ydata)
    ydiff = ymax - ymin
    ymin -= 0.1 * ydiff
    ymax += 0.2 * ydiff
    if ymin < 0:
        ymin = 0

    return [xmin, xmax, ymin, ymax]

#-----------------------------------------------------------------------------------
#-- create_label: create a label for the plot from the data file                 ---
#-----------------------------------------------------------------------------------

def create_label(ifile):
    """
    create a label for the plot from the data file
    Input:  ifile   --- input file name
    Output: out     --- text 
    """
    atemp = re.split('\/', ifile)
    line  = atemp[len(atemp)-1]
    if line == '':
        line = ifile

    atemp  = re.split('_', line)
    inst   = atemp[0].upper()
    grat   = atemp[1].upper()
    energy = atemp[2]
    energy = energy[0] + '.' + energy[1] + energy[2] + energy[3]
    
    out   = 'Line: ' + str(energy) + 'keV : ' + inst + '/' +  grat

    return out

#-----------------------------------------------------------------------------------
#-- set_out_names: set two plot file names                                        --
#-----------------------------------------------------------------------------------

def set_out_names(ifile):
    """
    set two plot file names
    input:  ifile   --- input data file name
    output: out1/out2   --- two plotting file names
    """
    atemp = re.split('\/', ifile)
    out   = atemp[-1]
    out1  = web_dir + 'EdE_Plots/' + out.replace('_data', '_plot.png')
    out2  = web_dir + 'EdE_Plots/' + out.replace('_data', '_low_res_plot.png')

    return [out1, out2]

#-----------------------------------------------------------------------------------
#-- read_ede_data: read data from a given file                                   ---
#-----------------------------------------------------------------------------------

def read_ede_data(ifile):
    """
    read data from a given file
    Input:  ifile       --- input file name
    Output: date_list   --- a list of date
            ede_list    --- a list of ede value
            error_list  --- a list of computed ede error
    """
    data = mcf.read_data_file(ifile)

    date_list  = []
    ede_list   = []
    error_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        if mcf.is_neumeric(atemp[0]) == False:
            continue

        fwhm  = float(atemp[2])
        ferr  = float(atemp[3])
        ede   = float(atemp[4])
        date  = atemp[5]

        stime = Chandra.Time.DateTime(date).secs
        fyear = mcf.chandratime_to_fraq_year(stime)

        date_list.append(fyear)
        ede_list.append(ede)
#
#--- the error of EdE is computed using FWHM and its error value
#
        error = math.sqrt(ede*ede* ((ferr*ferr) / (fwhm*fwhm)))

        error_list.append(error)

    return [date_list, ede_list, error_list]

#-----------------------------------------------------------------------------------
#-- remove_extreme: remove extreme data points                                    --
#-----------------------------------------------------------------------------------

def remove_extreme(x, y):
    """
    remove extreme data points
    input:  x   --- a list of x data
            y   --- a list of y data
    output: [x, y]
    """
    x   = numpy.array(x)
    y   = numpy.array(y)
    avg = numpy.mean(y)
    std = numpy.std(y)
    bot = avg -3.5 * std
    top = avg +3.5 * std
    ind = (y > bot) & (y < top)
    x   = list(x[ind])
    y   = list(y[ind])

    return [x, y]

#-----------------------------------------------------------------------------------
#-- plot_single_panel: plot a single data set on a single panel                  ---
#-----------------------------------------------------------------------------------

def plot_single_panel(xmin, xmax, ymin, ymax, xdata, ydata, yerror,\
                      xname, yname, label, outname, resolution=200):
    """
    plot a single data set on a single panel
    Input:  xmin    --- min x
            xmax    --- max x
            ymin    --- min y
            ymax    --- max y
            xdata   --- independent variable
            ydata   --- dependent variable
            yerror  --- error in y axis
            xname   --- x axis label
            ynane   --- y axis label
            label   --- a text to indecate what is plotted
            outname --- the name of output file
            resolution-- the resolution of the plot in dpi
    Output: png plot named <outname>
    """
#
#--- fit line --- use robust method
#
    xcln = []
    ycln = []
    for k in range(0, len(xdata)):
        try:
            val1 = float(xdata[k])
            val2 = float(ydata[k])
            xcln.append(val1)
            ycln.append(val2)
        except:
            continue

    xdata = xcln
    ydata = ycln
    [xt, yt] = remove_extreme(xdata, ydata)

    (sint, slope, serr) = robust.robust_fit(xt, yt)
    lslope = '%2.3f' % (round(slope, 3))
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = 12
    props = font_manager.FontProperties(size=9)
#
#--- set plotting range
#
    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(left=xmin,   right=xmax, auto=False)
    ax.set_ylim(bottom=ymin, top=ymax,   auto=False)
#
#--- plot data
#
    plt.plot(xdata, ydata, color='blue', marker='o', markersize=4.0, lw =0)
#
#--- plot error bar
#
    plt.errorbar(xdata, ydata, yerr=yerror, lw = 0, elinewidth=1)
#
#--- plot fitted line
#
    start = sint + slope * xmin
    stop  = sint + slope * xmax
    plt.plot([xmin, xmax], [start, stop], color='red', lw = 2)
#
#--- label axes
#
    plt.xlabel(xname)
    plt.ylabel(yname)
#
#--- add what is plotted on this plot
#
    xdiff = xmax - xmin
    xpos  = xmin + 0.5 * xdiff
    ydiff = ymax - ymin
    ypos  = ymax - 0.08 * ydiff

    label = label + ': Slope:  ' + str(lslope)

    plt.text(xpos, ypos, label)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)

#--------------------------------------------------------------------

if __name__ == '__main__':

    run_ede_plot()
