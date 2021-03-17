#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       run_interruption.py: run all sci run interrupt scripts                  #
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
import time
import Chandra.Time
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')
#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
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
sys.path.append(mta_dir)
#
#--- MTA common functions 
#
import mta_common_functions             as mcf
#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions        as itrf
#
#--- extracting data
#
import extract_data                     as edata
#
#--- Ephin ploting routines
#
import plot_ephin                       as ephin
#
#---- GOES ploting routiens
#
import plot_goes                        as goes
#
#---- ACE plotting routines
#
import plot_ace_rad                     as ace 
#
#---- extract xmm data and plot
#
import compute_xmm_stat_plot_for_report as xmm
#
#---- update html page
#
import sci_run_print_html               as srphtml

#-------------------------------------------------------------------------------------
#-- run_interrupt: run all sci run plot routines                                    --
#-------------------------------------------------------------------------------------

def run_interrupt(ifile):
    
    """
    run all sci run plot routines
    input:  ifile                --- input file name. if it is not given, the script will ask
    output: <plot_dir>/*.png    --- ace data plot
            <ephin_dir>/*.png   --- ephin data plot
            <goes_dir>/*.png    --- goes data plot
            <xmm_dir>/*.png     --- xmm data plot
            <html_dir>/*.html   --- html page for that interruption
            <web_dir>/rad_interrupt.html    --- main page
    """
#
#--- check input file exist, if not ask
#
    test = exc_dir + ifile
    if not os.path.isfile(test):
        ifile = input('Please put the intrrupt timing list: ')
#
#--- extract data
#
    print( "Extracting Data")
    edata.extract_data(ifile)

    data  = mcf.read_data_file(ifile)

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        event = atemp[0]
        start = atemp[1]
        stop  = atemp[2]
        gap   = atemp[3]
        itype = atemp[4]

        print("PLOTING: " + str(event))
#
#--- plot Ephin data
#
        print("EPHIN/HRC")
        ephin.plot_ephin_main(event, start, stop)
#
#---- plot GOES data
#
        print("GOES")
        goes.plot_goes_main(event, start, stop)
#
#---- plot other radiation data (from NOAA)
#
        print("NOAA")
        ace.start_ace_plot(event, start, stop)
#
#---- extract and plot XMM data
#
        print("XMM")
        xmm.read_xmm_and_process(event)

#
#---- create indivisual html page
#
    print("HTML UPDATE")
    srphtml.print_each_html_control(ifile)
#
#---- update main html page
#
    srphtml.print_each_html_control()

#-------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 2:
        ifile = sys.argv[1]
    else:
        ifile = 'interruption_time_list'

    run_interrupt(ifile)

