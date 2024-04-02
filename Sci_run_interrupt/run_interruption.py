#!/proj/sot/ska3/flight/bin/python

#################################################################################
#                                                                               #
#       run_interruption.py: run all sci run interrupt scripts                  #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Apr 02, 2024                                       #
#                                                                               #
#################################################################################

import re
import sys
import os
import numpy as np
import Chandra.Time
from Chandra.Time import DateTime
from kadi import events
from datetime import datetime

#
#--- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/Interrupt/Scripts'
EXC_DIR = '/data/mta/Script/Interrupt/Exc'

#Time formats for stat / stop arguments
TIME_FORMATS = ["%Y:%j:%H:%M:%S", "%Y:%j:%H:%M", "%Y:%m:%d:%H:%M:%S", "%Y:%m:%d:%H:%M"]

#
#--- append a path to a privte folder to python directory
#
sys.path.append(BIN_DIR)

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

#Collect imported modules for ease of pathing changes.
MOD_GROUP = [edata, ephin, goes, ace, xmm, srphtml]

#-------------------------------------------------------------------------------------
#-- compute_gap: process stat / stop time arguments                                 --
#-------------------------------------------------------------------------------------
def compute_gap(start, stop, name = ''):
    """
    Intake string-formatted time and output interruption data
    """
    for form in TIME_FORMATS:
        try:
            tstart = datetime.strptime(start, form)
        except:
            pass
    for form in TIME_FORMATS:
        try:
            tstop = datetime.strptime(stop, form)
        except:
            pass
    if name == '':
        name = tstart.strftime("%Y%m%d")
    
    chandra_start = DateTime(tstart.strftime("%Y:%j:%M:%H:%S"))
    chandra_stop = DateTime(tstop.strftime("%Y:%j:%M:%H:%S"))
    
    rad_zones = events.rad_zones.filter(start = chandra_start, stop = chandra_stop).table
    rad_zones_duration_secs = np.sum(rad_zones['dur'])
    science_time_lost_secs = chandra_stop.secs - chandra_start.secs - rad_zones_duration_secs
    
    out = {'name': name,
           'tstart': tstart,
           'tstop': tstart,
           'tlost': f'{(science_time_lost_secs / 1000.):.2f}'} # ksec
    return out

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
    test = EXC_DIR + ifile
    if not os.path.isfile(test):
        ifile = input('Please put the intrrupt timing list: ')
#
#--- extract data
#
    print( "Extracting Data")
    edata.extract_data(ifile)

    with open(ifile,'r') as f:
        data = [line.strip() for line in f.readlines()]

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
#---- create individual html page
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

