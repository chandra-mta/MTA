#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_run.py: run all required scripts to create HRC data/images             #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Mar 09, 2021                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import time
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
path = '/data/mta/Script/Exposure/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
hbin_dir = bin_dir + 'HRC_scripts/'
sys.path.append(bin_dir)
sys.path.append(hrc_bin_dir)
sys.path.append(mta_dir)
#
#--- import HRC related scripts/functions
#
import mta_common_functions             as mcf                  #--- MTA common functions
import exposureFunctions                as expf                 #--- exposure related functions
import hrc_dose_get_data_full_rage      as hgdata               #--- getting data
import hrc_dose_extract_stat_data_month as hstat                #--- hrc statistics
import hrc_dose_make_data_html          as hhtml                #--- html related
import hrc_dose_plot_exposure_stat      as hplot                #--- plot related
import hrc_dose_create_image            as himg                 #--- image creation
import hrc_dose_plot_monthly_report     as monthly              #--- plotting monthly report plot

import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------
#--- hrc_dose_run: run all needed HRC scripts to extract data and create images     ---
#--------------------------------------------------------------------------------------

def hrc_dose_run(year='NA', month='NA'):
    """
    run all needed HRC scripts to extract data and create images  
    input:  year    --- year    
            month   --- month
    """
#
#--- if year and month are given, get that year and month for data extraction
#
    if year != 'NA' and str(year).isdigit() and str(month).isdigit():
        lyear  = int(year)
        lmonth = int(month)
#
#--- if year and month are not given, use a month before the current year/month
#
    else:
        [year, month, day] = mcf.today_date()
        lyear  = year
        lmonth = month - 1
        if lmonth < 1:
            lmonth = 12
            lyear -= 1

#
#--- extracting data
#
    try:
        hgdata.hrc_dose_get_data(lyear, lmonth, lyear, lmonth)
    except:
        print("Data Extraction Failed!!")
        subject = 'HRC data extraction problem'
        content = 'Extraction of HRC data for exposure map trend failed.'
        expf.send_warning_email(subject, content)
#        exit(1)
#
#--- computing statistics
#
    try:
        hstat.hrc_dose_extract_stat_data_month(lyear, lmonth)
    except:
        print("Stat computation failed")
        pass
#
#--- creating html pages
#
    try:
        hhtml.hrc_dose_make_data_html()
    except:
        print("HTML page construction failed")
        pass
#
#--- plotting histories
#
    try:
        hplot.hrc_dose_plot_exposure_stat()
    except:
        print("Trend plotting failed")
        pass
#
#--- creating map images
#
    try:
        himg.create_hrc_maps(lyear, lmonth)
    except:
        print("HRC map construction failed")
        pass
#
#--- plotting monthly report trend
#
    try:
        monthly.hrc_dose_plot_monthly_report()
    except:
        print("Plot for monthly report failed")
        pass

#--------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 3:
        year = sys.argv[1].strip()
        mon  = sys.argv[2].strip()
    else:
        year = 'NA'
        mon  = 'NA'

    hrc_dose_run(year, mon)
