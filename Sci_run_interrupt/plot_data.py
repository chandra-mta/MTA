#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       plot_data.py: plot all science run interruption related data            #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string
import numpy as np
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
path = '/data/mta/Script/Interrupt/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]


for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions    as itrf
#
#--- Ephin/HRC ploting routines
#
import plot_ephin                   as ephin
#
#---- GOES ploting routiens
#
import plot_goes                    as goes
#
#---- ACE plotting routines
#
import plot_ace_rad                 as ace

#---------------------------------------------------------------------------------------------
#--- plot_data: plot all data related to the science run interruption (EPHIN/HRC/GOES/ACE)----
#---------------------------------------------------------------------------------------------

def plot_data(ifile):
    
    """
    plot all data related to the science run interruption (NOAA/EPHIN/GOES)
    input:  file                --- input file name. if it is not given, the script will ask
    output: <plot_dir>/*.png    --- ace data plot
            <goes_dir>/*.png    --- goes data plot
    """
    if ifile == '':
        ifile = raw_input('Please put the intrrupt timing list: ')
    }

    data = mcf.read_data_file(ifile)

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        event = atemp[0]
        start = atemp[1]
        stop  = atemp[2]
#
#--- plot Ephin/HRC data (after 2014, only hrc is plotted)
#
        ephin.plot_ephin_main(event, start, stop)
#
#---- plot GOES data
#
        goes.plot_goes_main(event, start, stop)
#
#---- plot ACE data
#
        ace.start_ace_plot(event, start, stop)

#---------------------------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) == 2:
        ifile = sys.argv[1]
    else:
        ifile = ''

    plot_data(ifile)

