#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#############################################################################################
#                                                                                           #
#           ede_temperature_plots.py: plot OBA/HRMA temperature - EdE relations             #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Aug 29, 2019                                                       #
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

import Ska.engarchive.fetch as fetch

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
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#-- run_ede_temperature_plots: find data file names and run plotting routines                     --
#---------------------------------------------------------------------------------------------------

def run_ede_temperature_plots():
    """
    find data file names and run plotting routines
    input:  none but read from <data_dir>
    output: *_plot.png/*_low_res_plot.png --- two plots; one is in 200dpi and another in 40dpi
    """
    cmd  = 'ls ' + data_dir + '*_data > ' + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    for ifile in data:
        ede_temperature_plots(ifile)

#---------------------------------------------------------------------------------------------------
#-- ede_temperature_plots: plot OBA/HRMA temperature - EdE relations                             ---
#---------------------------------------------------------------------------------------------------

def ede_temperature_plots(ifile):
    """
    plot OBA/HRMA temperature - EdE relations
    input:  ifile   --- a file name of data
    output: *_plot.png/*_low_res_plot.png --- two plots; one is in 200dpi and another in 40dpi
    """
#
#--- read data
#
    [xdata, xdata2,  ydata, yerror] = read_ede_data(ifile)
#
#--- set y plotting range
#
    [ymin, ymax] = set_min_max(ydata)
    ymax = 2100
#
#--- plot OBA data
#
    for oob in range(1, 63):
        msid = 'oobthr' + mcf.add_leading_zero(oob)
#
#--- find a corresponding temperature
#
        temperature = get_temp_data(msid, xdata2)
#
#--- set label, output file name...
#
        label   = create_label(ifile)
        outdir  =  web_dir + 'OBA/Plots/'
        outname = set_out_name(outdir, msid,  ifile)
#
#--- plot data
#
        plot_data(temperature, ydata, yerror, ymin, ymax, msid, label, outname)
#
#--- plot HRMA data
#
    for rt in range(556, 581):
        msid = '4rt' + str(rt) + 't'

        try:
            temperature = get_temp_data(msid, xdata2)
        except:
            continue 

        label   = create_label(ifile)
        outdir  = web_dir + 'HRMA/Plots/'
        outname = set_out_name(outdir, msid,  ifile)
        plot_data(temperature, ydata, yerror, ymin, ymax, msid, label, outname)

#---------------------------------------------------------------------------------------------------
#-- get_temp_data: get temperature data of msid for the given time spots in the list              --
#---------------------------------------------------------------------------------------------------

def  get_temp_data(msid, xdata):
    """
    get temperature data of msid for the given time spots in the list
    input:  msid    --- msid
            xdata   --- a list of time data in seconds from 1998.1.1
    output: temperature --- a list of temperature corresponding to the time list
    """
    temperature = []
    for m in range(0, len(xdata)):
        start = xdata[m] - 60.0
        stop  = xdata[m] + 60.0
        out   = fetch.MSID(msid, start, stop)
        val   = numpy.mean(out.vals)
        temperature.append(val)

    return temperature

#---------------------------------------------------------------------------------------------------
#-- plot_data: preparing to plot data and call the routine                                        --
#---------------------------------------------------------------------------------------------------

def plot_data(temperature, ydata, yerror,  ymin, ymax, msid, label, outname):
    """
    preparing to plot data and call the routine
    input:  temperature --- a list of temperature data
            ydata       --- a list of ydata
            yerror      --- a list y error
            ymin        --- y min
            ymax        --- y max
            msid        --- msid
            label       --- label
            outname     --- output file name
    output: outname
    """
    [xmin, xmax] = set_min_max(temperature)
    xname = msid.upper() + ' (K)'
    yname = 'EdE'
#
    plot_single_panel(xmin, xmax, ymin, ymax, temperature, ydata, \
                      yerror, xname, yname, label, outname, resolution=200)

#---------------------------------------------------------------------------------------------------
#-- set_min_max: set plotting range                                                              ---
#---------------------------------------------------------------------------------------------------

def set_min_max(idata):
    """
    set plotting range
    Input:  idata   ---- data
    Output: [imin, imax]
    """
    imin  = min(idata)
    imax  = max(idata)
    idiff = imax - imin
    imin -= 0.1 * idiff
    imax += 0.2 * idiff
    if imin < 0:
        imin = 0

    if imin == imax:
        imin = imin - 0.1 * imax
        imax = imax + 0.1 * imax

    return [imin, imax]

#---------------------------------------------------------------------------------------------------
#-- create_label: create a label for the plot from the data file                                 ---
#---------------------------------------------------------------------------------------------------

def create_label(ifile):
    """
    create a label for the plot from the data file
    Input:  file    --- input file name
    Output: out     --- text 
    """
    atemp = re.split('\/', ifile)
    line  = atemp[-1]
    if line == '':
        line = ifile

    atemp  = re.split('_', line)
    inst   = atemp[0].upper()
    grat   = atemp[1].upper()
    energy = atemp[2]
    energy = energy[0] + '.' + energy[1] + energy[2] + energy[3]
    
    out   = 'Line: ' + str(energy) + 'keV : ' + inst + '/' +  grat

    return out

#---------------------------------------------------------------------------------------------------
#-- set_out_name: create output name                                                              --
#---------------------------------------------------------------------------------------------------

def set_out_name(outdir, msid,  ifile):
    """
    create output name
    input:  outdir  --- the output directory
            msid    --- msid
            ifile   --- data file name
    output: outname --- output file name with (full) path
    """
    atemp   = re.split('\/', ifile)
    name    = atemp[-1]

    name    = name.replace('_data', '')
    outname = outdir + name + '_' + msid + '_plot.png'

    return outname

#---------------------------------------------------------------------------------------------------
#-- read_ede_data: read data from a given file                                                       ---
#---------------------------------------------------------------------------------------------------

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
    date_list2 = []
    ede_list   = []
    error_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        if mcf.is_neumeric(atemp[0])== False:
            continue

        fwhm  = float(atemp[2])
        ferr  = float(atemp[3])
        ede   = float(atemp[4])
        date  = atemp[5]
        sdate = float(atemp[6])

        stime = Chandra.Time.DateTime(date).secs
        fyear = mcf.chandratime_to_fraq_year(stime)

        date_list.append(fyear)
        date_list2.append(sdate)
        ede_list.append(ede)
#
#--- the error of EdE is computed using FWHM and its error value
#
        error = math.sqrt(ede*ede* ((ferr*ferr) / (fwhm*fwhm)))

        error_list.append(error)


    return [date_list, date_list2, ede_list, error_list]

#---------------------------------------------------------------------------------------------------
#-- plot_single_panel: plot a single data set on a single panel                                  ---
#---------------------------------------------------------------------------------------------------

def plot_single_panel(xmin, xmax, ymin, ymax, xdata, ydata, yerror, \
                      xname, yname, label, outname, resolution=100):
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
    try:
        (sint, slope, serr) = robust.robust_fit(xdata, ydata)
    except:
        sint  = 0.0
        slope = 0.0

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

    run_ede_temperature_plots()

