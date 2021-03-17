#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       plot_function.py: plotting routine                                      #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Mar 04, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import numpy as np
import time
import Chandra.Time
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
path = '/data/mta/Script/Disk_check/house_keeping/dir_list_py'
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
#--- set y plotting range
#
ymin = 30
ymax = 100

#-----------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                       ---
#-----------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outfile):

    """
    This function plots multiple data in separate panels.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            xname: a name of x-axis
            yname: a name of y-axis
            entLabels: a list of the names of each data
            outfile: output file name
    Output: a png plot: outfile
    """
#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon',\
                 'black', 'yellow', 'olive')
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
    for i in range(0, tot):
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
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))

        exec("%s.set_xlim(left=xmin, right=xmax, auto=False)" % (axNam))
        exec("%s.set_ylim(bottom=ymin, top=ymax, auto=False)" % (axNam))

        xdata  = xSets[i]
        ydata  = ySets[i]
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], lw =1.5)
#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
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
    plt.savefig(outfile, format='png', dpi=200)

#--------------------------------------------------------------------
