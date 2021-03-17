#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_plot_exposure_stat.py:  plotting trendings of avg, min, 10th bright,  #
#                                       and max counts of each quadrant of I2, I3,      #
#                                       S2, and S3.                                     #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 09, 2021                                                       #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import copy
import numpy as np
import time
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
#
#--- reading directory list
#
path = '/data/mta/Script/Exposure/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)
import mta_common_functions as mcf
import exposureFunctions    as expf

#----------------------------------------------------------------------------------------
#--- acis_dose_plot_exposure_stat: read hrc database, and plot history of exposure    ---
#----------------------------------------------------------------------------------------

def acis_dose_plot_exposure_stat(indir='NA', outdir='NA', clean='NA'):
    """
    read acis database, and plot history of exposure. 
    input:  indir   --- input directory
            outdir  --- output directory
            clean   --- if not 'NA', clean up the data sets before plotting the data
    output: <outdir>/<inst>.png
    """
#
#--- setting indir and outdir if not given
#
    if indir   == 'NA':
        indir   = data_out

    if outdir  == 'NA':
        outdir  = plot_dir
#
#--- clean up the data sets before reading
#
    if clean != 'NA':
        expf.clean_data(indir)
#
#--- start plotting data
#
    for ccd in ('i_2', 'i_3', 's_2', 's_3'):
        for sec in range(0, 4):
            inst = ccd + '_n_' + str(sec)
            idata = expf.readExpData(indir, inst)
#
#--- plot data
#
            plot_acis_dose(idata)
#
#--- trim the edge and move to the plot directory
#
            cmd = 'convert acis.png -trim ' + outdir + inst + '.png' 
            os.system(cmd)
            mcf.rm_files('rm acis.png')

#----------------------------------------------------------------------------------------
#--- plot_acis_dose: plot 6 panels of hrc quantities.                                  --
#----------------------------------------------------------------------------------------

def plot_acis_dose(idata):
    """
    plot 6 panels of acis quantities. 
    input:  idata   --- a list of list of:
                date    --- a list of date
                amean   --- a list of cummurative mean
                amin    --- a list of cummurative min
                amax    --- a list of cummurative max
                accs1   --- a list of one sigma values
                accs2   --- a list of two sigma values
                accs3   --- a list of three sigma values
                deman   --- a list of diff mean
                dmin    --- a list of diff min
                dmax    --- a list of diff max
                diffs1  --- a list of one sigma values
                diffs2  --- a list of two sigma values
                diffs3  --- a list of three sigma values
    output: ./acis.png
    """
#
#--- open data
#
    (date, year, month, amean, astd, amin, amin_pos, \
     amax, amax_pos, accs1, accs2, accs3, dmean, dstd,\
     dmin, dmin_pos, dmax, dmax_pos, dffs1, dffs2, dffs3)  = idata

    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.05)
    plt.subplots_adjust(wspace=0.12)
#
#--- mean
#
    ax1 = plt.subplot(4,2,1)
    try:
        plot_panel(date, dmean, 'Average', ax1)
    except:
        pass
#
#--- mean cumulative
#
    ax2 = plt.subplot(4,2,2)
    try:
        plot_panel(date, amean, 'Average Cumulative', ax2)
    except:
        pass
#
#--- min
#
    ax3 = plt.subplot(4,2,3)
    try:
        plot_panel(date, dmin, 'Minimum', ax3)
    except:
        pass
#
#--- min cumulative
#
    ax4 = plt.subplot(4,2,4)
    try:
        plot_panel(date, amin, 'Minimum Cumulative', ax4)
    except:
        pass
#
#--- max
#
    ax5 = plt.subplot(4,2,5)
    try:
        plot_panel(date, dmax, 'Maximum', ax5)
    except:
        pass
#
#--- max cumulative
#
    ax6 = plt.subplot(4,2,6)
    try:
        plot_panel(date, amax, 'Maximum Cumulative', ax6)
    except:
        pass
#
#--- 68, 95, and 99.6% levels
#
    labels = ["68% Value ", "95% Value", "99.7% Value"]
    ax7 = plt.subplot(4,2,7)
    try:
        plot_three_values(date, dffs1, dffs2, dffs3,  labels, ax7)
    except:
        pass
#
#--- 68, 95, and 99.6% cumulative
#
    ax8 = plt.subplot(4,2,8)
    try:
        plot_three_values(date, accs1, accs2, accs3, labels, ax8)
    except:
        pass
#
#--- plot x axis tick label only at the bottom ones
#
    for ax in ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8:
        if ax != ax7 and ax != ax8:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            pass
#
#--- putting axis names
#
        ax3.set_ylabel('Counts per Pixel')
        ax7.set_xlabel('Year')
        ax8.set_xlabel('Year')
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#   
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 12.0)
#
#--- save the plot in png format
#   
    plt.savefig('acis.png', format='png', dpi=100)

    plt.close('all')

#----------------------------------------------------------------------------------------
#---   plot_panel: plotting each panel for a given "ax"                               ---
#----------------------------------------------------------------------------------------

def plot_panel(x, y, label, ax):
    """
    plotting each panel for a given "ax". 
    input:  x       --- a list of x values
            y       --- a list of y values
            label   --- label
            ax      --- designation of the plot
    output: return a part of plotting results
    """
#
#--- x axis setting: here we assume that x is already sorted
#
    xmin = x[0]
    xmax = x[len(x) -1]
    diff = xmax - xmin
    xmin = xmin - 0.05 * diff
    xmax = xmax + 0.05 * diff
    xmin = int(xmin)
    xmax = int(xmax) + 1
    xbot = xmin + 0.05 * diff
#
#--- y axis setting
#
    tymin = 1e8
    tymax = 1.0
    for i in range(0, len(y)):
        if y[i] > tymax: 
            tymax = y[i]
        if y[i] < tymin:
            tymin = y[i]

    ymin = min(y)
    ymax = max(y)
#
#--- for the case,  ymin == ymax, 
#
    if ymin == ymax:
        ymax += 1

    diff = ymax - ymin
    ymin = ymin - 0.01 * diff

    if ymin < 0:
        ymin = 0

    ymax = ymax + 0.1 * diff
    ytop = ymax - 0.12 * diff
#
#--- setting panel 
#

    ax.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

    ax.set_xlim(left=xmin,   right=xmax, auto=False)
    ax.set_ylim(bottom=ymin, top=ymax,   auto=False)
#
#--- plot line
#
    plt.plot(x, y, color='blue',   lw=1, marker='+', markersize=1.5)
    plt.text(xbot, ytop, label)

#----------------------------------------------------------------------------------------
#---  plot_three_values: plotting each panel for a given "ax": three different values on one pannel
#----------------------------------------------------------------------------------------

def plot_three_values(x, s1, s2, s3, labels, ax):
    """
    plotting each panel for a given "ax". : three different values on one pannel
    input:  x       --- a list of x values
            s1      --- a list of s1 values
            s2      --- a list of s2 values
            s3      --- a list of s3 values
            label   --- label
            ax      --- designation of the plot
    output: return a part of plotting results
    """
#
#--- x axis setting: here we assume that x is already sorted
#
    xmin = x[0]
    xmax = x[len(x) -1]
    diff = xmax - xmin
    xmin = xmin - 0.05 * diff
    xmax = xmax + 0.05 * diff
    xmin = int(xmin)
    xmax = int(xmax) + 1
    xbot = xmin + 0.05 * diff
#
#--- y axis setting
#
    ymin = 0
    ymax = max(s3)
    ymax = 1.1 * ymax
#
#--- for the case,  ymin == ymax, 
#
    if ymin == ymax:
        ymax += 1

    diff = ymax - ymin
    ymin = ymin - 0.01 * diff

    if ymin < 0:
        ymin = 0

    ymax = ymax + 0.1 * diff
    ytop = ymax - 0.12 * diff
#
#--- setting panel 
#
    ax.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

    ax.set_xlim(left=xmin,   right=xmax, auto=False)
    ax.set_ylim(bottom=ymin, top=ymax,   auto=False)
#
#--- plot line
#
    p1, = plt.plot(x, s1, color='blue',  lw=1, marker='', markersize=0.0)
    p2, = plt.plot(x, s2, color='green', lw=1, marker='', markersize=0.0)
    p3, = plt.plot(x, s3, color='orange',lw=1, marker='', markersize=0.0)

    legend([p1, p2, p3], [labels[0], labels[1], labels[2]], loc=2, fontsize=9)

#------------------------------------------------------------------------
#
#--- check whether this is a test case
#
if __name__ == '__main__':

    #acis_dose_plot_exposure_stat(clean ='Yes')
    acis_dose_plot_exposure_stat(clean ='No')
