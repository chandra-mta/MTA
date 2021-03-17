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

import math
import re
import sys
import os
import string
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
#--- mta common functions
#
import mta_common_functions             as mcf
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

def extract_data(ifile):
    """
    extract ephin and GOES data. this is a control and call a few related scripts 
    input: ifile    --- a file contain the data information
                        e.g., 20170911    2017:09:11:07:51    2017:09:13:22:56    171.6   auto
    output: all data files and stat data file for the event(s)
    """
    if ifile == '':
        ifile = input('Please put the intrrupt timing list: ')

    rzl.sci_run_add_to_rad_zone_list(ifile)
#
#--- correct science run interruption time excluding radiation zones
#
    itrf.sci_run_compute_gap(ifile)

    data = mcf.read_data_file(ifile)

    for ent in data:
        print( "EXTRACTING DATA FOR: " + ent)

        if not ent:
            break

        atemp = re.split('\s+|\t+', ent)
        event = atemp[0]
        start = atemp[1]
        stop  = atemp[2]
        gap   = atemp[3]
        itype = atemp[4]
#
#--- extract ephin/hrc data
#
        ephin.ephin_data_extract(event, start, stop)
#
#--- compute ephin/hrc statistics
#
        ephin.compute_ephin_stat(event, start)
#
#---- extract GOES data
#
        try:
            goes.extract_goes_data(event, start, stop)
        except:
            pass
#
#---- compute GOES statistics
#
        try:
            goes.compute_goes_stat(event, start)
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
