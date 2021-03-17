#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       sim_move_supple.py: holding supplemental python function for sim move   #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Feb 17, 2021                                           #
#                                                                               #
#################################################################################
import os
import sys
import re
import string
import time
import Chandra.Time
import random
import numpy

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
path = '/data/mta/Script/SIM_move/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions       as mcf 
#
#--- temp writing file name
#
import random
rtail   = int(time.time() * random.random())
zspace  = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------
#-- convert_time_format: cnvert time format to either ydate or fractional year  -
#--------------------------------------------------------------------------------

def convert_time_format(t_list, ind=0):
    """
    cnvert time format to either ydate or fractional year
    input:  t_list  --- a list of time in seconds from 1998.1.1
            ind     --- if 0: ydate, else franctional year
    output: <year> <a list of time in the new format>
    """

    save = []
#
#--- convert to the ydate
#
    if ind == 0:
        t_list1 = []
        t_list2 = []
        for  ent in t_list:
            [year, ydate] = chandratime_to_yday(ent)
            t_list1.append(year)
            t_list2.append(ydate)
#
#---  everything happnes in the same year
#
        if t_list1[0] == t_list1[-1]:
            save  = t_list2
            byear = t_list1[0]
#
#--- when the data are over two years
#
        else:
            if mcf.is_leapyear(t_list1[0]):
                base = 366
            else:
                base = 365
#
#--- checking in which year the majority of the data is in
#
            t_array = numpy.array(t_list1)
            indx    = t_array == t_list1[0]
            y_len   = len(t_array[indx])
#
#--- the majority of the data is in the last year
#
            if y_len > 0.5 * len(t_list1):
                byear = t_list1[0]
                for j in range(0, len(t_list1)):
                    if t_list1[j] == byear:
                        save.append(t_list2[j])
                    else:
                        save.append(t_list2[j] + base)
#
#--- the majority of the data is in this year
#
            else:
                byear = t_list[-1]
                for j in range(0, len(t_list1)):
                    if t_list1[j] == byear:
                        save.append(t_list2[j])
                    else:
                        save.append(t_list2[j] - base)

        return byear, save
#
#--- convert to the fractional year
#
    else:
        for ent in t_list:
            fyear = mcf.chandratime_to_fraq_year(ent)
            save.append(fyear)

        return 1999, save

#--------------------------------------------------------------------------------
#-- chandratime_to_yday: convert chandra time into a day of year               --
#--------------------------------------------------------------------------------

def chandratime_to_yday(ctime):
    """
    convert chandra time into a day of year
    input:  ctime   --- time in seconds from 1998.1.1
    output: ydate   --- a day of year (fractional)
    """
    
    atime = Chandra.Time.DateTime(ctime).date
    btemp = re.split(':', atime)
    year  = float(btemp[0])
    ydate = float(btemp[1])
    hour  = float(btemp[2])
    mins  = float(btemp[3])
    sec   = float(btemp[4])
    
    ydate  = ydate + (hour/24.0 + mins/1440.0 + sec/86400.0)
    
    
    return [int(year), ydate]

#--------------------------------------------------------------------------------
#-- plot_panel: plotting data and save as a png data                          ---
#--------------------------------------------------------------------------------

def plot_panel(x, y, x_range, y_range, xname, yname, title, outname, tind=0):
    """
    plotting data and save as a png data
    input:  x           --- a list of x values
            y           --- a list of y values
            x_range     --- x plotting range
            y_range     --- y plotting range
            xname       --- x axis label
            yname       --- y axis label
            title       --- title
            outname     --- output file name
            tind        --- if >0, add fitting line
    output: <outname>   --- a png file
    """
#
#--- clean up the plotting device
#
    plt.close('all')
#
#--- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)

    plt.scatter(x, y, color='blue', marker='.')
    plt.xlabel(xname)
    plt.ylabel(yname)
    #plt.title(title)
    [xmin, xmax] = x_range
    [ymin, ymax] = y_range
    xpos = xmax - 0.20 * (xmax - xmin)
    ypos = ymax - 0.05 * (ymax - ymin)
    font ={'size' : 12, 'color' : 'red'}
    plt.text(xpos, ypos, title, **font)

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
#
#--- adding trand line
#
    if tind > 0:
        xa        = numpy.array(x) - 1999
        ya        = numpy.array(y)
        try:
            [a, b, e] = linear_fit(xa, ya)
        except:
            [a, b, e] = [-999, -999, 0]
        
        ystart = a + b * (xmin - 1999) 
        yend   = a + b * (xmax - 1999) 
        
        plt.plot([xmin, xmax], [ystart, yend], color='red', marker='', linewidth=2)
        
        xpos  = 0.6 *(xmax-xmin) + xmin
        ypos  = 0.1 *(ymax-ymin) + ymin
        ypos2 = 0.08 *(ymax-ymin) + ymin
        line  = 'Slope: %1.3e' % (b) + '(sec/step/year)'
        plt.text(xpos, ypos, line)
        line  = '(Fitting after year 2001)'
        plt.text(xpos, ypos2, line)
#
#--- set the size of the plotting area etc
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0,8.0)
#
#--- save the plot in png
#
    plt.savefig(outname, format='png', dpi=200)

    plt.close('all')

#--------------------------------------------------------------------------------
#-- linear_fit: compute a linear fit parameters using least sq method          --
#--------------------------------------------------------------------------------

def linear_fit(x, y):
    """
    compute a linear fit parameters using least sq method
    Input:  x   --- a list of independent variable
    y   --- a list of dependent variable
    Output: aa  --- intersect
    bb  --- slope
    delta   --- denominator
    """
    avg  = numpy.mean(y)
    std  = numpy.std(y)
#
#--- remove outlayers
#--- x > 2 means starting data from year 2001 
#
    cut  = avg + 3.0 * std
    idx  = (y < cut) & (y < 0.004) & (y > 0.0) & (x > 2)
    xval = x[idx]
    yval = y[idx]
    tot  = len(xval)
    sx   = 0.0
    sy   = 0.0
    sxy  = 0.0
    sxx  = 0.0
    
    for j in range(0, tot):
        sx  += xval[j]
        sy  += yval[j]
        sxy += xval[j] * yval[j]
        sxx += xval[j] * xval[j]
    
    delta = tot * sxx - sx * sx
    
    aa= (sxx * sy  - sx * sxy) / delta
    bb= (tot * sxy - sx * sy)  / delta
    
    return (aa, bb, delta)



#--------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_sim_movement()
