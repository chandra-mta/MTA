#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################
#                                                                       #
#       acis_gain_plot_trend.py: plotting gain and offset trends        #
#                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)               #
#                                                                       #
#               Last update: Sep 23, 2021                               #
#                                                                       #
#########################################################################

import os
import sys
import re
import string
import math
import operator
import numpy
import time
import Chandra.Time
import scipy
from scipy.optimize import curve_fit

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
path = '/data/mta/Script/ACIS/Gain/house_keeping/dir_list_py'

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
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set line color list
#
colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')

#-----------------------------------------------------------------------------------
#--- acis_gain_plot_trend: plotting trends of gain and offset                     --
#-----------------------------------------------------------------------------------

def acis_gain_plot_trend():

    """
    plotting trends of gain and offset
    Input:  none, but read from <data_dir>
    Output: <web_dir>/Plots/gain_plot_ccd<ccd>.png
            <web_dir>/Plots/offset_plot_ccd<ccd>.png
    """
    for ccd in range(0, 10):
#
#--- plotting 4 nodes on one panel, but gain and offset separately
#
        Xset_gain   = []
        Yset_gain   = []
        Eset_gain   = []
        yMin_gain   = []
        yMax_gain   = []
        Label_gain  = []

        Xset_offset = []
        Yset_offset = []
        Eset_offset = []
        yMin_offset = []
        yMax_offset = []
        Label_offset= []

        for node in range(0, 4):
#
#--- read data for given CCD and Node #
#
            ifile = data_dir + 'ccd' + str(ccd) + '_' + str(node)
            data = mcf.read_data_file(ifile)

            time   = []
            gain   = []
            gerr   = []                 #--- error for gain
            offset = []
            oerr   = []                 #--- error for offset
#
#--- setting lower and upper limits to remove outlyers
#
            sum1   = 0.0
            sum2   = 0.0
            for ent in data:
                atemp = re.split('\s+', ent)
                gval  = float(atemp[4])
                sum1 += gval
                sum2 += gval * gval
            avg = sum1 / len(data)
            sig = math.sqrt(sum2/len(data) - avg * avg)
            blim = avg - 3.0 * sig;
            tlim = avg + 3.0 * sig;

            for ent in data:
                atemp = re.split('\s+', ent)
#
#--- convert time into year date (e.g.2012.14)
#
                gval = float(atemp[4])
                if (gval <= blim) or (gval >= tlim):
                    continue

                ytime = mcf.chandratime_to_fraq_year(float(atemp[0]))
                time.append(ytime)
    
                gain.append(float(atemp[4]))
                gerr.append(float(atemp[5]))
                offset.append(float(atemp[6]))
                oerr.append(float(atemp[7]))

            xmax = max(time)

            Xset_gain.append(time)
            Yset_gain.append(gain)
            Eset_gain.append(gerr)
#
#--- set plotting range
#
            avg  = mean(gain)
            ymin = avg - 0.005
            ymin = round(ymin, 3) -0.001
            ymax = avg + 0.005
            ymax = round(ymax, 3) +0.001
            yMin_gain.append(ymin)
            yMax_gain.append(ymax)
            name = 'Gain (ADU/eV) Node' + str(node)
            Label_gain.append(name)

            Xset_offset.append(time)
            Yset_offset.append(offset)
            Eset_offset.append(oerr)
            
            avg = mean(offset)
            ymin = avg - 30.0
            ymin = int(ymin)
            ymax = avg + 30.0
            ymax = int(ymax)
            yMin_offset.append(ymin)
            yMax_offset.append(ymax)
            name = 'Offset (ADU) Node' + str(node)
            Label_offset.append(name)

        xmin = int(2000)
        xtmp = xmax
        xmax = int(xmax) + 1
#
#--- if the year is already passed a mid point, add another year
#
        if (xtmp - xmax) > 0.5:
            xmax += 1
        xname = 'Time (year)'
#
#--- actual plotting starts here
#
        yname   = 'Gain'
        outname = web_dir + "/Plots/gain_plot_ccd" + str(ccd) + '.png'
        plotPanel(xmin, xmax, yMin_gain, yMax_gain, Xset_gain, Yset_gain, \
                  Eset_gain, xname, yname, Label_gain, outname)

        yname   = 'Offset'
        outname = web_dir + "/Plots/offset_plot_ccd" + str(ccd) + '.png'
        plotPanel(xmin, xmax, yMin_offset, yMax_offset, Xset_offset, Yset_offset,\
                  Eset_offset, xname, yname, Label_offset, outname)


#-----------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                           ---
#-----------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets, xname, yname, entLabels, outname):

    """
    This function plots multiple data in separate panels
    Input:  xmin        --- x min
            xmax        --- x max
            ymin        --- y min
            ynax        --- ymax
            xSets       --- a list of lists containing x-axis data
            ySets       --- a list of lists containing y-axis data
            yMinSets    --- a list of ymin 
            yMaxSets    --- a list of ymax
            xname       --- x label
            yname       --- y label
            entLabels   --- a list of the names of each data
            outname     --- the output file name
    Output: outname     --- a png plot
    """
#
#--- clean up the plotting device
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
        exec("%s.set_autoscale_on(False)" % (axNam))      #---- these three may not be needed for the new pylab, but 
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))      #---- they are necessary for the older version to set

        exec("%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam))
        exec("%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam))

        xdata  = numpy.array(xSets[i])
        ydata  = numpy.array(ySets[i])
        edata  = numpy.array(eSets[i])

        elen   = len(edata)
        pdata = numpy.ones(elen)
#
#--- fitting weighted least sq. line
#
        popt, pcov = curve_fit(model, xdata, ydata, p0=(0, 1))
        [intc, slope] = list(popt)
        [ierr, serr]  = list(numpy.sqrt(numpy.diag(pcov)))
  
        ystart = intc + slope * xmin
        ystop  = intc + slope * xmax
        lxdata = [xmin, xmax]
        lydata = [ystart, ystop]
#
#---- actual data plotting
#
        p, = plt.plot(xdata,  ydata,  color=colorList[i], marker='.', markersize=4.0, lw =0)
        p, = plt.plot(lxdata, lydata, color=colorList[i], marker='',  markersize=1.0, lw =1)
        plt.errorbar(xdata, ydata, yerr=edata, ecolor=colorList[i],   markersize=0.0, fmt='ro')
#
#--- add legend
#
        if slope < 0.01:
            pslope = slope * 1.0e4
            pslope = round(pslope, 3)
            pserr  = serr  * 1.0e4
            pserr  = round(pserr, 3)
            eline  = '(' + str(pslope) + '+/-' + str(pserr) + ')e-04'

            legend_line = entLabels[i] + ' Slope: ' + eline
        else:
            legend_line = entLabels[i] + ' Slope: ' + str(round(slope, 3)) + '+/-' + str(round(serr, 3))
        leg = legend([p],  [legend_line], prop=props, loc=2)
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
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=200)

#--------------------------------------------------------------------------------------------------
#--  model: model for least sq. fitting                                                         ---
#--------------------------------------------------------------------------------------------------

def model(x, a, b):

    """
    model for least sq. fitting
    Input:  p   (a, b) --- intercept and slope of the line
            x          --- independent variable value
    Output: estimated y value
    """
    return a + b*x

#--------------------------------------------------------------------------------------------------
#-- residuals: compute residuals                                                                ---
#--------------------------------------------------------------------------------------------------

def residuals(p, my_arrays):

    """
    compute residuals
    my_arrays   --- (x, y, err): they are numpy array
    p           --- (a, b): intercept and slope
    Output:     numpy array of residuals
    """
    x, y, err = my_arrays
    a, b = p
    return (y-model(p,x))/err

#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

if __name__ == '__main__':

    acis_gain_plot_trend()
