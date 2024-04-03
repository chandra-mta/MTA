#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       extract_data.py: extract data needed for sci. run interruption plots    #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#################################################################################

import re
import sys

#
#--- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/Interrupt/Scripts'

#
#--- append a path to a privte folder to python directory
#
sys.path.append(BIN_DIR)

#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions        as itrf
#
#---- EPHIN/HRC data extraction
#
import extract_ephin                    as ephin
#
#---- GOES data extraction
#
import extract_goes                     as goes
#
#---- ACE (NOAA) data extraction
#
import extract_ace_data                 as ace
#
#---- ACE (NOAA) statistics
#
import compute_ace_stat                 as astat
#
#---- XMM data/stat/plot
#
import compute_xmm_stat_plot_for_report as xmm
#
#--- adding radiation zone info
#
import sci_run_add_to_rad_zone_list     as rzl

#-------------------------------------------------------------------------------------
#--- extract_data: extract ephin and GOES data. this is a control and call a few related scripts
#-------------------------------------------------------------------------------------

def extract_data(event_data):
    """
    extract ephin and GOES data. this is a control and call a few related scripts 
    input: event_data --- dictionary containing event data
        e.g., name: 20170911    tstart: 2017:09:11:07:51    tstop: 2017:09:13:22:56    tlost: 171.6   mode: auto
    output: all data files and stat data file for the event(s)
    """

    rzl.sci_run_add_to_rad_zone_list(event_data)
#event = name
#
#--- extract ephin/hrc data
#
    ephin.ephin_data_extract(event_data['name'], event_data['tstart'][:-3], event_data['tstop'][:-3])
#
#--- compute ephin/hrc statistics
#
    ephin.compute_ephin_stat(event_data['name'], event_data['tstart'][:-3])
#
#---- extract GOES data
#
    try:
        goes.extract_goes_data(event_data['name'], event_data['tstart'][:-3], event_data['tstop'][:-3])
    except:
        pass
#
#---- compute GOES statistics
#
    try:
        goes.compute_goes_stat(event_data['name'], event_data['tstart'][:-3])
    except:
        pass
#
#---- extract ACE (NOAA) data
#
    try:
        ace.extract_ace_data(event, start, stop)
    except:
        pass
#
#---- compute ACE statistics
#
    try:
        astat.compute_ace_stat(event, start, stop)
    except:
        pass
#
#---- extract/compute/plot xmm data
#
    try:
        xmm.read_xmm_and_process(event)
    except:
        pass

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 2:
        ifile = sys.argv[1]
    else:
        ifile = ''
    extract_data(ifile)
