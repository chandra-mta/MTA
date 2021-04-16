#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#       plot_aiming_point_data.py: plot aiming point trend data             #
#                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                   #
#                                                                           #
#               last update: Apr 16, 2021                                   #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import unittest
import time 
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
path = '/data/mta/Script/ALIGNMENT/Abs_pointing/Scripts/house_keeping/dir_list'

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
import mta_common_functions as mcf  #---- contains other functions commonly used in MTA scripts
import robust_linear        as robust
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------
#-- plot_aiming_trend_data: read data and plot data of aiming point       --
#---------------------------------------------------------------------------

def plot_aiming_trend_data():
    """
    read data and plot data of aiming point 
    input: none but read from <data_dir>/aics_i etc
    output: <web_dir>/Plots/<inst>_<ychoice>.png
    """
    year = int(float(time.strftime("%Y", time.gmtime())))
    xmax = year + 1

    for inst in ('acis_i', 'acis_s', 'hrc_i', 'hrc_s'):
        ifile = data_dir + inst + '_data'
        out   = mcf.read_data_file(ifile)
        if len(out) == 0:
            continue

        data  = mcf.separate_data_into_col_data(out[2:], spliter='\t+')
        if len(data[0]) == 0:
            continue

        dat1  = data[0]
        dat2  = data[7]
        dat3  = data[8]
        atime = []
        dy    = []
        dz    = []
        for k in range(0, len(dat1)):
            try:
                out = mcf.chandratime_to_fraq_year(dat1[k])
                atime.append(out)
                dy.append(dat2[k])
                dz.append(dat3[k])
            except:
                continue

        try:
            [atime, dy, dz] = remove_extreme(atime, dy, dz)
        except:
            pass

        plot_data(atime, dy, 1999, xmax, -2, 2, inst, 'y')
        plot_data(atime, dz, 1999, xmax, -2, 2, inst, 'z')

#---------------------------------------------------------------------------
#-- plot_data: plot data                                                  --
#---------------------------------------------------------------------------

def plot_data(x, y, xmin, xmax, ymin, ymax, inst, ychoice):
    """
    plot data
    input:  x   --- a list of independent variable
            y   --- a list of dependent variable
            xmin    --- x min
            xmax    --- x max
            ymin    --- y min
            ymax    --- y max
            inst    --- instrument name
            ychoice --- y or z
    output: <web_dir>/Plots/inst_<ychoice>.png
    """
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = 16
    props = font_manager.FontProperties(size=16)
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
    plt.plot(x, y, color='blue', marker='.', markersize=8, lw=0)
#
#--- put y = 0 line
#
    plt.plot([xmin, xmax], [0, 0], color='black', linestyle='-.', lw=1)
#
#--- fit a line
#
    (sint, slope, serr) = robust.robust_fit(x, y)
    ybeg = sint + slope * xmin
    yend = sint + slope * xmax
    plt.plot([xmin, xmax], [ybeg, yend], color='red', lw=2)
#
#--- add text
#
    line = 'Slope: %3.2f' % (slope)

    xpos = xmin + 0.05 * (xmax - xmin)
    ypos = 1.6
    plt.text(xpos, ypos, line, color='red')

    plt.xlabel('Time (Year)')
    ylabel = ychoice.upper() + ' Axis Error (arcsec)'
    plt.ylabel(ylabel)
#
#--- save the plot in png format
#
    width      = 10.0
    height     = 5.0
    resolution = 200
    outname    = web_dir + 'Plots/' + inst + '_' + ychoice + '.png'


    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)
    
    plt.close('all')

#---------------------------------------------------------------------------
#-- remove_extreme: remove data points larger than 3                      --
#---------------------------------------------------------------------------

def remove_extreme(atime, dy, dz):
    """
    remove data points larger than 3
    input: atime    --- time
            dy      --- dy
            dz      --- dz
    output: atime   --- cleaned atime
            dy      --- cleaned dy
            dz      --- cleaned dz
    """
    at = numpy.array(atime)
    ay = numpy.array(dy)
    az = numpy.array(dz)

    index = [(ay > -3) & (ay < 3)]
    at    = at[index]
    ay    = ay[index]
    az    = az[index]

    index = [(az > -3) & (az < 3)]
    at    = at[index]
    ay    = ay[index]
    az    = az[index]

    at    = list(at)
    ay    = list(ay)
    az    = list(az)

    return [at, ay, az]

#---------------------------------------------------------------------------

if __name__ == "__main__":

    plot_aiming_trend_data()

