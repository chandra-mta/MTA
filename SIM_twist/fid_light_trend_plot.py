#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#           fid_light_trend_plot.py: plots fid light trend plots                        #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 03, 2021                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- pylab plotting routine related modules
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
path = '/data/mta/Script/ALIGNMENT/Sim_twist/Scripts/house_keeping/dir_list_py'

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
#
#--- import several functions
#
import mta_common_functions as mcf        #---- contains other functions commonly used in MTA scripts
import robust_linear        as rfit       #---- robust fit rountine
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

mon_list = [0, 31, 59, 90, 120, 151, 181, 212, 234, 373, 304, 334]
#
#--- break points of the line fitting
#
b_period = [1999.0, 2003.42, 2006.94]

#------------------------------------------------------------------------------------------
#-- fid_light_trend_plot: plots fid light trend plots for ACIS I/S and HSC I/S           --
#------------------------------------------------------------------------------------------

def fid_light_trend_plot():
    """
    plots fid light trend plots for ACIS I/S and HSC I/S
    input:  none but read from <data_dir>/<I-*/S-*> and <data_dir>/<H-I-*/H-S-*>
    output: png plots e.g., I-2.png, H-S-1.png
    """
    for part in range(1, 7):
        name   = 'I-'   + str(part)
        infile = data_dir + name
        indata = read_fid_light_data(infile)
        plot_panel(indata, name)

        name   = 'S-'   + str(part)
        infile = data_dir + name
        indata = read_fid_light_data(infile)
        plot_panel(indata, name)

    for part in range(1, 5):
        name   = 'H-I-' + str(part)
        infile = data_dir + name
        indata = read_fid_light_data(infile)
        plot_panel(indata, name)

        name   = 'H-S-' + str(part)
        infile = data_dir + name
        indata = read_fid_light_data(infile)
        plot_panel(indata, name)

#------------------------------------------------------------------------------------------
#-- read_fid_light_data: read fid light data                                             --
#------------------------------------------------------------------------------------------

def read_fid_light_data(infile):
    """
    read fid light data
    input:  infile  --- input file name
    output: atime   --- time in fractional year
            acen_i  --- acent i
            acen_j  --- acent j
    """
    out    = mcf.read_data_file(infile)
    atime  = []
    acen_i = []
    acen_j = []
    for ent in out:
        try:
            atemp = re.split('\s+', ent)
            var1  = mcf.chandratime_to_fraq_year(float(atemp[0]))
            var2  = float(atemp[4])
            var3  = float(atemp[5])
        except:
            continue

        atime.append(var1)
        acen_i.append(var2)
        acen_j.append(var3)

    return [atime, acen_i, acen_j]

#------------------------------------------------------------------------------------------
#-- plot_panel: plot data                                                                --
#------------------------------------------------------------------------------------------

def plot_panel(data, outname):
    """
    plot data
    input:  data    --- data in [time, y data set1, y data set2]
            outname --- the name of the data to be plotted
    output: <web_dir>/Plots/<outname>.png
    """
    r_len    = len(b_period)
#
#--- data are separated into a few sections. here we set the end of the each
#--- section in fractional year. the last closing data is set to year 4000
#--- see b_period for the starting date (in fractional year)
#
    e_period = []
    for k in range(1, r_len):
        e_period.append(b_period[k])

    e_period.append(4000.0)

    plt.close('all')
    dlen = 2
    mlen = dlen - 1
    ylab = ['ACENT I', 'ACNET J']
#
#--- set panel parameters
#
    plt.subplots_adjust(hspace=0.08)
    props = font_manager.FontProperties(size=9)
#
#--- set x range
#
    [atime, xmin, xmax, xlabel, xtext] = set_x_range(data[0])
#
#--- plot each panel
#
    for k in range(0, dlen):
        j = k +  1
        line = str(dlen) + '1' + str(j)
        exec("ax%s = plt.subplot(%s)" % (str(k), line))
        exec("ax%s.set_xlim(left=xmin, right=xmax, auto=False)" % (str(k)))
#
#--- if ymin and ymax are given, use them
#
        ydata = data[k+1]
        [ymin, ymax, ytext] = set_y_range(data[0], ydata)
        exec("ax%s.set_ylim(bottom=ymin, top=ymax, auto=False)" % (str(k)))
        exec("ax%s.plot(atime, ydata, color='blue', marker='.', markersize=1, lw=0)" % (str(k)))
#
#--- fit lines
#
        if outname in ('I-3','S-3'):
            rtop = 1
        else:
            rtop =  r_len
        for m in range(0, rtop):
            if k % 2 == 0:
                bot = 0
            else:
                bot = 1
            [x_range, y_range, ytext, line] \
               = fit_line_period(data[0], ydata, b_period[m], e_period[m], m, ymin, ymax, bot)

            exec("ax%s.plot(x_range, y_range, color='red', lw=2)" % (str(k)))
            plt.text(xtext, ytext, line)
#
#--- y axis label
#
        exec("ax%s.set_ylabel('%s')" % (str(k), ylab[k]))
#
#--- x axis label
#
    exec('ax%s.set_xlabel("%s")' % (str(mlen), 'Time (Year)'))
#
#--- add x ticks label only on the last panel
#
    for k in range(0, dlen):
        ax = 'ax' + str(k)

        if k != mlen:
            line = eval("%s.get_xticklabels()" % (ax))
            for label in  line:
                label.set_visible(False)
        else:
            pass
#
#--- save the plot in a file
#
    fig    = matplotlib.pyplot.gcf()
    height = 4.0 * dlen + 0.5
    fig.set_size_inches(10.0, height)

    outname = web_dir + 'Plots/' + outname + '.png'

    plt.savefig(outname, format='png', dpi=100.0)

#------------------------------------------------------------------------------------------
#-- fit_line_period: fit a line on the given data section and return the results         --
#------------------------------------------------------------------------------------------

def fit_line_period(x, y, x_start, x_stop, m,  ymin, ymax, bot=0):
    """
    fit a line on the given data section and return the result
    input:  x       --- x data
            y       --- y data
            x_start --- a list of the starting points
            x_stop  --- a list of the stopping points
            m       --- section position of the lists above
            ymin    --- y min
            yax     --- y max
            bot     --- an indicator of where to print the text. bot =1 to bottom side
    output: x_range  --- a list of start and stop position of the line in x 
            y_range  --- a list of start and stop position of the line in y
            ytext   --- y position of the text
            line    --- a line to be printed
    """
    dlen = len(x)
    xn   = []
    yn   = []
#
#--- select data for the limited range
#
    for k in range(0, dlen):
        if x[k] >= x_start and x[k] < x_stop:
            if y[k] >= ymin and y[k] <= ymax:
                xn.append(x[k])
                yn.append(y[k])
#
#--- compute the fitted line with robust method
#
    try:
        [a, b, e] = rfit.robust_fit(xn, yn)
        y1        = a + b * x_start
        y2        = a + b * x_stop
        x_range    = [x_start, x_stop]
        y_range    = [y1, y2]
#
#--- set the text postion and create the text to be printed
#
        ydiff     = ymax - ymin
        if bot == 0:
            ytext     = ymax -0.1 * ydiff * (m + 1)
        else:  
            ytext     = ymax -0.1 * ydiff * (m + 1) -0.5 * ydiff

        if x_start < 2000:
            line      = "Slope (%4.1f < year):  %3.3f" % (x_stop, round(b, 3))
        elif x_stop > 3000:
            line      = "Slope (year > %4.1f):  %3.3f" % (x_start, round(b, 3))
        else:
            line      = "Slope (%4.1f <  year < %4.1f): %3.3f" % (x_start, x_stop, round(b, 3))
    
        return [x_range, y_range, ytext, line]
#
#--- for the case the fitting failed
#
    except:
        ydiff     = ymax - ymin
        if bot == 0:
            ytext     = ymax -0.1 * ydiff * (m + 1)
        else:  
            ytext     = ymax -0.1 * ydiff * (m + 1) - 0.5 * ydiff

        return[[0,0], [0,0], ytext, 'NA']

#------------------------------------------------------------------------------------------
#-- set_x_range: set several x axis related values                                       --
#------------------------------------------------------------------------------------------

def set_x_range(xdata):
    """
    set several x axis related values
    input:  xdata   --- x data
    output: ndata   --- x data set for the short time span (less than 2 yrs)
            xmin    --- x min
            xmax    --- x max
            xlabel  --- label of x axis
            xtext   --- x position of the text to be printed
    """
    xmin = min(xdata)
    year = int(xmin)
    xmax = max(xdata)

    xdiff = xmax - xmin
    if xdiff < 2.0:
        if mcf.is_leapyear(year):
            base = 366
        else:
            base = 365

        ndata = []
        for ent in xdata:
            val = base * (ent - year)
            ndata.append(val)
 
            xlabel = 'Time (year=' + str(year) + ' yday)'

            xmin   = 0
            xmax   = base

    else:
        ndata = xdata
        xmin  = int(xmin)
        xmax  = int(xmax) + 1
        xlabel = 'Time (year)'

    xdiff = xmax - xmin
    xtext = xmin + 0.02 * xdiff

    return [ndata, xmin, xmax, xlabel, xtext]

#------------------------------------------------------------------------------------------
#-- set_y_range: setting ymin and ymax                                                   --
#------------------------------------------------------------------------------------------

def set_y_range(xdata, ydata):
    """
    setting ymin and ymax
    input:  xdata   --- x data
            ydata   --- y data
    output: ymin    --- y min
            ymax    --- y max
            ytext   --- y position of the text to printed
    """
    xmax     = int(max(xdata))
    yavg     = numpy.median(ydata)
    interval = 4 + 0.5 * (xmax - 2005)

    ymin     = yavg - 0.55 * interval
    ymax     = yavg + 0.45 * interval
    
    ytext    = ymax - 0.1 * interval

    return [ymin, ymax, ytext]

#------------------------------------------------------------------------------------------

if __name__ == "__main__":

    fid_light_trend_plot()



