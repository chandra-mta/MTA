#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_plot_monthly_report.py: plot history of exposure  for monthly report   #
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
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a privte folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import exposureFunctions    as expf

#------------------------------------------------------------------------------------------------
#--- hrc_dose_plot_monthly_report: read hrc database, and plot history of exposure  for monthly report
#------------------------------------------------------------------------------------------------

def hrc_dose_plot_monthly_report(indir = 'NA', outdir = 'NA'):
    """
    read hrc database, and plot history of exposure. 
    input:  indir   --- data directory path
            outdir  --- output directory path 
    output: <outdir>/hrc_max_exp.gif
    """
#
#--- setting indir and outdir if not given
#
    if indir   == 'NA':
        indir   = data_out

    if outdir  == 'NA':
        outdir  = img_dir
#
#--- read HRC I data
#
    out = expf.readExpData(indir,'hrci') 
    idate    = out[0]
    imax_acc = out[7]
#
#--- read HRC S data
#
    out = expf.readExpData(indir,'hrcs')
    smax_acc = out[7]
#
#--- plot data
#
    plot_max_dose(idate, imax_acc, smax_acc)
#
#--- move the plot  to img directory
#
    cmd = 'mv hrc_max_exp.gif ' + outdir
    os.system(cmd)

#--------------------------------------------------------------------------------------------
#--- plot_max_dose: plot hrc i and hrc s max exposure plots                                --
#--------------------------------------------------------------------------------------------

def plot_max_dose(date, hrci_max, hrcs_max):
    """
    plot hrc i and hrc s max exposure plots
    input:  date        --- a list of time, 
            hrci_max    --- a list of hrc i max cumurative exposure data 
            hrcs_max    --- a list of hrc s max cumurative exposure data
    output: hrc_max_exp.gif
    """
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 16
    mpl.rcParams['axes.linewidth'] = 2.0
    props = font_manager.FontProperties(size=14)
    plt.subplots_adjust(hspace=0.05)
    plt.subplots_adjust(wspace=0.12)
#
#--- HRC I
#
    ax1 = plt.subplot(2,1,1)
    plot_panel(date, hrci_max, 'HRC-I', ax1, ymin = 250)
#
#--- HRC S
#
    ax2 = plt.subplot(2,1,2)
    plot_panel(date, hrcs_max, 'HRC-S', ax2, ymin = 1400)
#
#--- plot x axis tick label only at the bottom ones
#
    for ax in ax1, ax2:
        if ax != ax2:
            for label in ax.get_xticklabels():
                label.set_visible(False)
        else:
            pass
#
#--- putting axis names
#
        ax1.set_ylabel('Counts')
        ax2.set_ylabel('Counts')
        ax2.set_xlabel('Year')
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#   
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 8.0)
#
#--- save the plot in png format and then convert to gif
#   
    plt.savefig('hrc_max_exp.png', format='png', dpi=100)
#
#--- convert is unix command to change img format
#
    cmd = 'convert hrc_max_exp.png hrc_max_exp.gif'
    os.system(cmd)
    os.system('rm hrc_max_exp.png')

    plt.close('all')

#--------------------------------------------------------------------------------------------
#---   plot_panel: plotting each panel for a given "ax"                                   ---
#--------------------------------------------------------------------------------------------

def plot_panel(x, y, label, ax, ymin):
    """
    plotting each panel for a given "ax". 
    input:  x       --- a list of x values
            y       --- a list of y values
            label   --- ax label
            ax      --- designation of the plot
            ymin    --- y min
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
    xbot = xmin + 0.05 * diff
#
#--- y axis setting
#
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
    plt.plot(x, y, color='blue', lw=3, marker='+', markersize=2.0)

    plt.text(xbot, ytop, label)

#----------------------------------------------------------------------------

if __name__ == '__main__':

    hrc_dose_plot_monthly_report()
