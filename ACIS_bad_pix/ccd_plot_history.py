#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#       ccd_plot_history.py: create  various history plots for warm pixels and warm columns #
#                                                                                           #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                           #
#                   Last update: Mar 02, 2021                                               #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':
    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'
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
import mta_common_functions    as mcf
#
#--- set color list
#
colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')

#-------------------------------------------------------------------------------------------
#--- plot_ccd_history: plotting warm pixel history                                       ---
#-------------------------------------------------------------------------------------------

def plot_ccd_histories():
    """
    plotting ccd histories 
    input: None but read from:
            <data_dir>ccd<ccd>_cnt
            <data_dir>bad_ccd<ccd>_cnt
            <data_dir>cum_ccd<ccd>_cnt
            --- 'ccd' could be hccd, col, etc
    output: <plot_dir>hist_plot<ccd>.png
    """
#
#--- set input parameters
#
    ctype = ['ccd', 'hccd', 'col']
    part1 = ['Warm Pixels', 'Hot Pixels', 'Warm Columns']
    part2 = ['Real Warm',   'Real Hot',   'Real Warm']
#
#--- there are three different types of data: ccd, hccd, and col
#
    for k in range(0, 3):
#
#--- plot each ccd
#
        for ccd in range(0, 10):
            ifile = data_dir + ctype[k] + str(ccd) + '_cnt'
            ofile = web_dir  + 'Plots/hist_plot_'  + ctype[k] + str(ccd) + '.png'
            part3 = 'CCD' + str(ccd)
            plot_each_data(ifile, ofile, part1[k], part2[k], part3)
#
#--- plot front side combined ccd 
#
        ifile = data_dir + 'front_side_' + ctype[k] + '_cnt'
        ofile = web_dir  + 'Plots/hist_' + ctype[k] + '_plot_front_side.png'
        part3 = 'Front Side CCDs'
        plot_each_data(ifile, ofile, part1[k], part2[k], part3)

#-------------------------------------------------------------------------------------------
#-- plot_each_data: create a plot for each data                                          ---
#-------------------------------------------------------------------------------------------

def plot_each_data(ifile, ofile, part1, part2, part3):
    """
    create a plot for each data
    input:  ifile   --- input data file name
            ofile   --- output plot file name in png
            part1   --- description of title part
            part2   --- description of title part
            part3   --- description of title part
    output: ofile   --- png plot 
    """
#
#--- read data and put in one basket
#
    [xMinSets, xMaxSets, yMinSets, yMaxSets, xSets, ySets] = readData(ifile)
    xmin = min(xMinSets)
    xmax = max(xMaxSets)
#
#--- set titles
#
    tlabels = []
    pname = 'Cumulative Numbers of '   + part1 + ': ' + part3
    tlabels.append(pname)

    pname = 'Numbers of Daily '        + part1 + ': ' + part3
    tlabels.append(pname)

    pname = 'Numbers of Persisting '   + part1 + ': ' + part3
    tlabels.append(pname)

    pname = 'Numbers of Potential '    + part1 + ' (' + part2 
    pname = pname + ' + Flickering): ' + part3
    tlabels.append(pname)
#
#--- plotting: create three panel plots
#
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, 'Time (Year)', 'Counts',
              tlabels, ofile, mksize=0.0, lwidth=1.5)

#---------------------------------------------------------------------------------------------------
#---  readData: read data and set plotting range                                                 ---
#---------------------------------------------------------------------------------------------------

def readData(dataname):
    """
    read data and set plotting range
    input: dataname  --- data file name (need a full path to the file)
    output: xval     --- an array of independent values (time in seconds from 1998.1.1)
            cval     --- cumulative counts
            dval     --- daily counts
            bval     --- actual bad point counts
            pval     --- potential bad point counts
    """
#
#--- read data
#
    data = mcf.read_data_file(dataname)
    xval = []
    cval = []
    dval = []
    bval = []
    pval = []
    prev = 0
    for ent in data:
        atemp = re.split('<>', ent)
        try:
            val = float(atemp[0])
            if val < 0:
                continue
            if val == prev:
                continue

            stime = int(float(val))
            ytime = mcf.chandratime_to_fraq_year(stime)
            xval.append(ytime)
            prev  = ytime
        
            val1  = float(atemp[2])
            val2  = float(atemp[3])
            val3  = float(atemp[4])
            val4  = float(atemp[5])
            cval.append(val1)
            dval.append(val2)
            bval.append(val3)
            pval.append(val3 + val4)
        except:
            pass
#
#-- find plotting ranges and make a list of data lists
#
    xmin_list = []
    xmax_list = []
    ymin_list = []
    ymax_list = []
    x_list    = []
    y_list    = []
    for dlist in (cval, dval, bval, pval):
        (xmin, xmax, ymin, ymax) = findPlottingRange(xval, dlist)
        xmin_list.append(xmin)
        xmax_list.append(xmax)
        ymin_list.append(ymin)
        ymax_list.append(ymax)
        x_list.append(xval)
        y_list.append(dlist)

    return [xmin_list, xmax_list, ymin_list, ymax_list, x_list, y_list]

#---------------------------------------------------------------------------------------------------
#--- findPlottingRange: setting plotting range                                                   ---
#---------------------------------------------------------------------------------------------------

def findPlottingRange(xval, yval):
    """
    setting plotting range
    input:  xval --- an array of x-axis
            yval --- an array of y-axis
    output: xmin --- the lower boundary of x axis plotting range
            xmax --- the upper boundary of x axis plotting range
            ymin --- the lower boundary of y axis plotting range
            ymax --- the upper boundary of y axis plotting range
    """
#
#--- set ploting range.
#
    xmin = min(xval)
    xmax = max(xval)
    xdff = xmax - xmin
    xmin -= 0.1 * xdff
    if xmin < 0.0:
        xmin = 0
    xmax += 0.1 * xdff
#
#--- since there is a huge peak during the first year, avoid that to set  y plotting range
#
    ytemp = []

    for i in range(0, len(yval)):
        if xval[i] < 2001.4986301:         #--- 2001:182:00:00:00
            continue
        ytemp.append(yval[i])

    ymin = min(ytemp)
    ymax = max(ytemp)

    ydff = ymax - ymin
    if ydff == 0:
        ymin = 0
        if ymax == 0:
            ymax = 2
    else:
        ymin -= 0.1 * ydff
        if ymin < 0.0:
            ymin = 0
        ymax += 0.1 * ydff

    ymin = int(ymin)
    ymax = int(ymax) + 2

    return(xmin, xmax, ymin, ymax)

#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, ofile, mksize=1.0, lwidth=1.5):
    """
    This function plots multiple data in separate panels
    input:  xmin, xmax, ymin, ymax: plotting area
            xSets       --- a list of lists containing x-axis data
            ySets       --- a list of lists containing y-axis data
            yMinSets    --- a list of ymin 
            yMaxSets    --- a list of ymax
            entLabels   --- a list of the names of each data
            ofile       --- output file name
            mksize      --- a size of maker
            lwidth      --- a line width
    output: ofile       --- a png plot 
    """
#
#--- close all opened plot
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- start plotting each data
#
    for i in range(0, len(entLabels)):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec("%s = plt.subplot(%s)"       % (axNam, line))
        exec("%s.set_autoscale_on(False)" % (axNam))
        exec("%s.set_xbound(xmin ,xmax)"  % (axNam))

        exec("%s.set_xlim(left=%s,   right=%s, auto=False)" % (axNam, str(xmin),        str(xmax)))
        exec("%s.set_ylim(bottom=%s, top=%s,   auto=False)" % (axNam, str(yMinSets[i]), str(yMaxSets[i])))

        xdata  = xSets[i]
        ydata  = ySets[i]
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=mksize, lw = lwidth)
#
#--- add legend
#
        leg = legend([p], [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec("%s.set_ylabel(yname, size=8)" % (axNam))
#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            line = eval("%s.get_xticklabels()" % (ax))
            for label in  line:
                label.set_visible(False)
        else:
            pass
    xlabel(xname)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig    = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(ofile, format='png', dpi=200)

#--------------------------------------------------------------------

if __name__ == '__main__':

    plot_ccd_histories()
