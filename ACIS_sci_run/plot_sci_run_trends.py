#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       plot_sci_run_trends.py: pdate  science run trend plots                  #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Feb 26, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator
import time

import matplotlib as mpl
mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

path = '/data/mta/Script/ACIS/Acis_sci_run/house_keeping/dir_list_py_t'

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
import mta_common_functions     as mcf
import acis_sci_run_functions   as asrf

#-----------------------------------------------------------------------------------------------
#-- plot_sci_run_trends: pdate  science run trend plots                                       --
#-----------------------------------------------------------------------------------------------

def plot_sci_run_trends(tyear=''):
    """
    update  science run trend plots
    input:  tyear   --- the year of the data
    output: <web_dir>Year<year>/<type>_out.png
    """
    if tyear == '':
        tyear = int(float((time.strftime('%Y', time.gmtime()))))

    cout_dir = 'Year' + str(tyear)
#
#--- plot trends for the year
#
    plot_events(cout_dir)
#
#--- plot long term trends
#
    plot_events('Long_term')
#
#--- update html pages
#
    today   = time.strftime("%Y:%m:%d", time.gmtime())
    atemp   = re.split(':', today)
    year    = int(float(atemp[0]))
    month   = int(float(atemp[1]))
    mday    = int(float(atemp[2]))
    if year != tyear:
        month = 12
        mday  = 31

    asrf.acis_sci_run_print_html(web_dir, tyear, month, mday)

#-----------------------------------------------------------------------------------------------
#--- plot_events: control sub for plotting each data group                                   ---
#-----------------------------------------------------------------------------------------------

def plot_events(data_dir):
    """
    control function to create plots for each sub data set
    input: data_dir --- the directory name where the data located (e.g. Year2013/)
    output: png plot file such as te3_3_out.png
    """
    ifile   = web_dir + data_dir + '/cc3_3_out'
    outname = ifile + '.png'
    acis_sci_run_plot(ifile, outname)

    ifile   = web_dir + data_dir + '/te3_3_out'
    outname = ifile + '.png'
    acis_sci_run_plot(ifile, outname)

    ifile   = web_dir + data_dir + '/te5_5_out'
    outname = ifile + '.png'
    acis_sci_run_plot(ifile, outname)

    ifile   = web_dir + data_dir + '/te_raw_out'
    outname = ifile + '.png'
    acis_sci_run_plot(ifile, outname)

#-----------------------------------------------------------------------------------------------
#-- acis_sci_run_plot: sets up the parameters for the given file and create plots            ---
#-----------------------------------------------------------------------------------------------

def acis_sci_run_plot(ifile, outname):
    """
    this function sets up the parameters for the given file and create plots
    input:   ifile   --- data file name
             outname --- plot output file name

    output:  <outname>.png
    """
#
#--- read input data
#
    data = mcf.read_data_file(ifile)
#
#--- if there is no data a copy an "no data" plot
#
    if len(data) == 0:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + outname
        os.system(cmd)
        return False

    col        = []
    date_list  = []
    count_list = []
    err_list   = []
    drop_list  = []

    xmakerInd  = 0                  #--- used to mark whether this is a plot for a long term (if so, 1)

    for ent in data:
        col   = re.split('\t+|\s+', ent)
        try:
            val = float(col[6])
            if val > 0:
                m = re.search(':', col[1])
#
#--- for each year, change date format to ydate (date format  in the data file is: 112:00975.727)
#
                if m is not None:
                    atemp = re.split(':', col[1])
                    date  = float(atemp[0]) + float(atemp[1])/86400.0
#
#---- for the case of long term: the date format is already in a  fractional year date
#
                else:
                    date      = float(col[1])
                    xmakerInd =  1
#
#--- convert event rate and error rate in an appropreate units
#
                evt   = float(col[7])/float(val)/1000.0
                err   = float(col[8])/float(val)
#
#--- save needed data
#
                date_list.append(date)
                count_list.append(evt)
                err_list.append(err)
                drop_list.append(float(col[9]))
        except:
            pass

    if len(date_list) > 0:
#
#--- set plotting range
#
        (xmin, xmax)   = set_min_max(date_list)

        if xmakerInd == 1:                  #--- if it is a long term, x axis in year (in interger)
            xmin = int(xmin)
            xmax = int(xmax) + 1

        (ymin1, ymax1) = set_min_max(count_list)
#
#--- if the data set is te_raw_out, set the y plotting range to fixed size: 0  - 10
#
        m1 = re.search(ifile, 'te_raw_out')
        if m1 is not None:
            ymin1 = 0
            ymax1 = 10

        (ymin2, ymax2) = set_min_max(err_list)
        (ymin3, ymax3) = set_min_max(drop_list)

        yminSet  = [ymin1, ymin2, ymin3]
        ymaxSet  = [ymax1, ymax2, ymax3]
        xSets    = [date_list,  date_list, date_list]
        ySets    = [count_list, err_list,  drop_list]

        if xmakerInd == 0:
            xname    = 'Time (Day of Year)'
        else:
            xname    = 'Time (Year)'

        yLabel   = ['Events/sec', 'Events/sec', 'Percent']
        entLabels= ['Events per Second (Science Run)','Errors (Science Run)','Percentage of Exposures Dropped (Science Run)']
#
#--- calling actual plotting routine
#
        plotPanel(xmin, xmax, yminSet, ymaxSet, xSets, ySets, xname, yLabel, entLabels, outname)

#-----------------------------------------------------------------------------------------------
#--- set_min_max: set min and max of plotting range                                          ---
#-----------------------------------------------------------------------------------------------

def set_min_max(data):
    """
    set  min and max of the plotting range; 10% larger than actual min and max of the data set
    Input: data --- one dimentioinal data set

    Output (pmin, pmanx): min and max of plotting range
    """
    try:
        pmin = min(data)
        pmax = max(data)
        diff = pmax - pmin
        pmin = pmin - 0.1 * diff
        if pmin < 0:
            pmin = 0
        pmax = pmax + 0.1 * diff

        if pmin == pmax:
            pmax = pmin + 1
    except:
        pmin = 0
        pmax = 1

    return (pmin, pmax)

#-----------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                       ---
#-----------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yminSet, ymaxSet, xSets, ySets, xname, yLabel, entLabels, ofile):

    """
    This function plots multiple data in separate panels.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            xname: a name of x-axis
            yname: a name of y-axis
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """
#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
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
        exec("%s.set_autoscale_on(False)" % (axNam))      #---- these three may not be needed for the new pylab, but 
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))      #---- they are necessary for the older version to set

        exec("%s.set_xlim(left=xmin,         right=xmax,     auto=False)" % (axNam))
        exec("%s.set_ylim(bottom=yminSet[i], top=ymaxSet[i], auto=False)" % (axNam))

        xdata  = xSets[i]
        ydata  = ySets[i]
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], lw =0,  markersize=4.0, marker='o')
#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec("%s.set_ylabel(yLabel[i], size=8)" % (axNam))
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
    plt.subplots_adjust(hspace=0.08)
#
#--- save the plot in png format
#
    plt.savefig(ofile, format='png', dpi=200)

#--------------------------------------------------------------------

if __name__ == '__main__':

    
    if len(sys.argv) > 1:
        tyear = int(float(sys.argv[1]))
    else:
        tyear = ''

    plot_sci_run_trends(tyear)


