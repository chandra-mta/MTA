#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       acis_dose_control.py: monthly acis dose update control script           #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last updated: Mar 09, 2021                                              #
#                                                                               #
#################################################################################

import sys
import os
import string
import re
import fnmatch
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
sys.path.append(mta_dir)
sys.path.append(bin_dir)
sys.path.append(acis_bin_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions         as mcf
#
#--- Exposure related funcions shared
#
import acis_dose_get_data           as getd
import acis_create_cumulative       as cuml
import acis_compute_stat            as astat
import acis_dose_plot_exposure_stat as aplot
import acis_dose_make_data_html     as ahtml
import acis_dose_monthly_report     as arport
import acis_dose_create_image       as aimg

import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#-- acis_dose_control: monthly acis dose update contorl script                   ---
#-----------------------------------------------------------------------------------

def acis_dose_control(year = '', month = ''):
    """
    monthly acis dose update control script
    input: optional year and month
    """
    if year == '' or month == '':
        [year, month, day] = mcf.today_date()
        month = month -1
        if month < 1:
            month = 12
            year -= 1
    else:
        year  = int(year)
        month = int(month)

    syear = str(year)
    smon  = mcf.add_leading_zero(month)
#
#--- extract data
#
    try:
        getd.acis_dose_get_data(year, month, year, month)
    except:
        print("Data Extraction Failed!!")
        subject = 'ACIS data extraction problem'
        content = 'Extraction of ACIS data for exposure map trend failed.'
        expf.send_warning_email(subject, content)
        exit(1)
#
#--- create cumulative data
#
    file1 = 'ACIS_' + smon + '_' + syear + '.fits'
    file2 = 'ACIS_' + smon + '_' + syear + '.fits.gz'

    chk = 0
    for test in os.listdir('./'):
        if fnmatch.fnmatch(test, file2):
            chk = 1
            break

    if chk == 0:
        afile = file1
    else:
        afile = file2
    try:
        cuml.acis_create_cumulative(afile)
    except:
        print("Cumurative Data Creating Failed!!")
        subject = 'ACIS crumulativedata problem'
        content = 'Creation of Cumulative ACIS data for exposure map trend failed.'
        expf.send_warning_email(subject, content)
        exit(1)
#
#--- compute statistics
#
    astat.acis_dose_extract_stat_data_month(year, month)
#
#--- plot data
#
    aplot.acis_dose_plot_exposure_stat(clean='Yes')
#
#--- create images (you need to use ds9 to create a better image)
#
    aimg.create_acis_maps(year, month)
#
#--- update html pages
#
    ahtml.acis_dose_make_data_html()
#
#--- print monthly output
#
    arport.acis_dose_monthly_report()

#--------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 2:
        year = sys.argv[1]
        mon  = sys.argv[2]
    else:
        year = ''
        mon  = ''

    acis_dose_control(year, mon)
