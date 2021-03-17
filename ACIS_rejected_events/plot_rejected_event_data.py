#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################
#                                                                               #
#           plot_rejected_event_data.py: plot rejected event data               #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Apr 29, 2019                                           #
#                                                                               #
#################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import os.path
import time
import Chandra.Time
#
#--- interactive plotting module
#
##import mpld3
#from mpld3 import plugins, utils
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
#--- read directory path
#
path = '/data/mta/Script/ACIS/Rej_events/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf      #---- contains other functions commonly used in MTA scripts
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#------------------------------------------------------------------------------------
#-- plot_rej_evt_data: create rejected event data plots                            --
#------------------------------------------------------------------------------------

def plot_rej_evt_data():
    """
    create rejected event data plots
    input:  none, but read from <data_dir>/CCD<ccd#>_rej.dat
    output: <web_dir>/Plots/ccd<ccd#>_<part>.png
    """
    for ccd in range(0, 10):
        #print("CCD: " + str(ccd))
        ifile = data_dir + 'CCD' + str(ccd) + '_rej.dat'
        data  = mcf.read_data_file(ifile)

        set1  = [[] for x in range(0, 5)]
        set2  = [[] for x in range(0, 5)]
        for dline in data[1:]:
            ent = re.split('\s+', dline)
            ytime = mcf.chandratime_to_fraq_year(float(ent[0]))
            if float(ent[-2]) > 50000:
                set1[0].append(ytime)
                set1[1].append(float(ent[1]))
                set1[2].append(float(ent[3]))
                set1[3].append(float(ent[7]))
                set1[4].append(float(ent[9]))
            else:
                set2[0].append(ytime)
                set2[1].append(float(ent[1]))
                set2[2].append(float(ent[3]))
                set2[3].append(float(ent[7]))
                set2[4].append(float(ent[9]))

        plot_data(set1, ccd, 'cti')
        plot_data(set2, ccd, 'sci')

#------------------------------------------------------------------------------------
#-- plot_data: create multi-panel plots                                            --
#------------------------------------------------------------------------------------

def plot_data(data_set, ccd, part):
    """
    create multi-panel plots
    input:  data_set    --- a list of lists of data
            ccd         --- ccd #
            part        --- either "cti" or "sci"
    output: <web_dir>/Plots/ccd<ccd#>_<part>.png
    """
    ylab_list = ['EVTSENT', 'DROP_AMP', 'DROP_GRD', 'THR_PIX']
    ymax_list = [300, 300, 700, 3e4]

    now = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    now = Chandra.Time.DateTime(now).secs
    now = mcf.chandratime_to_fraq_year(now)

    xmin = 2000.0
    now += 1.4
    xmax = int(round(now , 1))

    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size']   = 10 
    mpl.rcParams['font.weight'] = 'medium'
    props = font_manager.FontProperties(size=10)
    props = font_manager.FontProperties(weight='medium')
    plt.subplots_adjust(hspace=0.08)

    for ax in range(0, 4):
        axnam = 'ax' + str(ax)
        j     = ax + 1
        line  = '61' + str(j)

        exec("%s = plt.subplot(%s)"       % (axnam, line))
        exec("%s.set_autoscale_on(False)" % (axnam))
        exec("%s.set_xbound(xmin,xmax)"   % (axnam))
        exec("%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axnam))
        exec("%s.set_ylim(ymin=0, ymax=%s, auto=False)" % (axnam, str(ymax_list[ax])))

        plt.plot(data_set[0], data_set[j],marker='.', mec='blue', \
                 markerfacecolor='blue', markersize='2.0', lw=0)

        ylabel(ylab_list[ax], fontweight='medium')
#
#--- add x ticks label only on the last panel
#
    for i in range(0, 4):
       axnam = 'ax' + str(i)
       if i != 3:
           line = eval("%s.get_xticklabels()" % (axnam))
           for label in  line:
               label.set_visible(False)
       else:
           pass

    xlabel('Time (Year)', fontweight='medium')
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0,8.0)
#
#--- save the plot in png format
#
    outname = html_dir + 'Plots/ccd' + str(ccd) + '_' + part  + '.png'
    plt.savefig(outname, format='png', dpi=200, bbox_inches='tight')

    plt.close('all')

#---------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_rej_evt_data()
