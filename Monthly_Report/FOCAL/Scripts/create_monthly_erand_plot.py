#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           create_monthly_focal_temp.py: create weekly report                                              #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Mar 03, 2016                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import Cookie
import unittest
import time
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['IDL_PATH'] = '+/usr/local/rsi/user_contrib/astron_Oct09/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'
ascdsenv2 = getenv('source /proj/sot/ska/bin/ska_envs.csh', shell='tcsh')
ascdsenv2['IDL_PATH'] = '+/usr/local/rsi/user_contrib/astron_Oct09/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'
 
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
#sys.path.append(base_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#
#--- set directory paths
#
wdir = '/data/mta/Script/Month/FOCAL/'
tdir = wdir + 'Scripts/Templates/'
#
#--- admin email address
#
admin  = 'tisobe@cfa.harvard.edu'

#------------------------------------------------------------------------------------------
#-- create_monthly_focal_temp: main script to create a monthly focal temp trend plots     -
#------------------------------------------------------------------------------------------

def create_monthly_focal_temp(year, month, eyear, emonth):
    """
    main script to create a monthly focal temp trend plots
    input:  year    --- start year in the format of yyyy (e.g. 2015)
            month   --- start month in the format of mm (e.g. 1 or 12)
            eyear   --- stopping year
            emonth  --- stopping month
    output: a direcotry containing templete (e.g. Sep10)
    """

    oned  = 86400

    syear = str(year)                       #--- 4 digit year
    yrd2  = syear[2] + syear[3]             #--- 2 digit year
    year  = int(float(year))                #--- integer year
    
    smon  = str(month)
    mon   = int(float(smon))                #--- integer month
    lmon  = tcnv.changeMonthFormat(mon)     #--- month in letter (e.g.Mar)

    sday  = '01'                            #--- two digit mday
    day   = 1                               #--- integer mday

    start = tcnv.convertDateToCTime(year, mon, day, 0, 0, 0)


    seyear = str(eyear)                     #--- 4 digit year
    eyrd2  = seyear[2] + seyear[3]          #--- 2 digit year
    eyear  = int(float(eyear))              #--- integer year
    
    semon  = str(emonth)
    emon   = int(float(semon))              #--- integer month
    lemon  = tcnv.changeMonthFormat(emon)   #--- month in letter (e.g.Mar)

    seday  = '01'                           #--- two digit mday
    eday   = 1                              #--- integer mday

    stop   = tcnv.convertDateToCTime(eyear, emon, eday, 0, 0, 0)
#
#--- set plot tick interval
#
    if mon == 2:
        dlist = [10, 20, 28]
        if tcnv.isLeapYear(year) == 1:
            dlist = [ 10, 20, 29]
    else:
        dlist  = [10, 20, 30]
    sdlist = [start]
    for ent in dlist:
        stime = tcnv.convertDateToCTime(year, mon, ent, 0, 0, 0)
        sdlist.append(stime)
#
#--- focal temp file name
#
    fptemp        = 'erad_' + lmon.lower() + yrd2 + '.gif'
    fpext_range   = str(start)+' '+  str(stop)
    fpstart       = str(start)
    fplsub        = '"' + lmon.lower() + '01","' + lmon.lower() + '10","' + lmon.lower() + '20","' + lmon.lower() + str(dlist[2]) + '"'
    fpdsub        = str(sdlist[0]) + ', ' + str(sdlist[1]) + ', ' + str(sdlist[2]) + ', ' + str(sdlist[3])

#
#--- copy command scripts and a couple of others needed
#
    cmd = 'cp -f  ' + tdir + 'get_ftemp_data.perl ' + wdir + '.'
    os.system(cmd)
    cmd = 'cp -f  ' + tdir + 'test ' + wdir + '.'
    os.system(cmd)
    cmd = 'cp -f  ' + tdir + 'run_temp  ' + wdir + '.'
    os.system(cmd)

    cmd = 'rm -rf param'
    os.system(cmd)
    cmd = 'mkdir param'
    os.system(cmd)
#
#--- create idl script
#
    tfile = tdir +  'plot_erad_time_month.pro'
    f     = open(tfile, 'r')
    input = f.read()
    f.close()

    input = input.replace('#START#',       str(start))
    input = input.replace('#SDATELIST#',   fpdsub)
    input = input.replace('#LDATELIST#',   fplsub)
    input = input.replace('#GIFNAME#',     fptemp)
    ofile =  wdir + 'plot_erad_time_month.pro'
    fo    = open(ofile, 'w')
    fo.write(input)
    fo.close()
#
#--- run the scripts
#
    run_focal_temp_data(start, stop) 
    cmd = 'mv ' + fptemp + ' ./Plots/.'
    os.system(cmd)
#
#--- clean up
#
    cmd = 'rm -rf param  get_ftemp_data.perl test run_temp plot_erad_time_month.pro out'
    os.system(cmd)

#----------------------------------------------------------------------------------
#-- run_focal_temp_data: run focal temp script and create a plot, read a table   --
#----------------------------------------------------------------------------------

def run_focal_temp_data(start, stop):
    """
    run focal temp script and create a plot, read a table
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: fcnt    --- number of peaks observed
            fdata   --- table input
    """

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' /usr/local/bin/perl ' + wdir + 'get_ftemp_data.perl ' + str(start) + ' ' +  str(stop)
    cmd  = cmd1 + cmd2
#
#--- run the focal temp script to extract data
#
    bash(cmd,  env=ascdsenv)

    mcf.rm_file('./test')

    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' idl ./run_temp > out'
    cmd  = cmd1 + cmd2
#
#--- run the focal temp script to create a plot
#
    bash(cmd,  env=ascdsenv2)

    cmd = 'rm -rf ./*fits '
    os.system(cmd)

#----------------------------------------------------------------------------------
#-- find_date_and_year_for_report: find nearest Thursday date                    --
#----------------------------------------------------------------------------------

def find_date_and_year_for_report():
    """
    find nearest Thursday date 
    input:  none
    output: date    --- date of the nearest Thu in the format of mmdd (e.g. 0910)
            year    --- year of the nearest Thu
    """
#
#--- find today's date information (in local time)
#
    tlist = time.localtime()

    year  = tlist[0]
    mon   = tlist[1]
    day   = tlist[2]
    wday  = tlist[6]
    yday  = tlist[7]

    mon  -= 1
    if mon < 1:
        mon   = 12
        year -= 1

    return [year, mon]


#------------------------------------------------------------------------------------------

if __name__ == "__main__":
#
    if len(sys.argv) >= 2:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
    else:
        [year, month] = find_date_and_year_for_report()

    eyear  = year
    emonth = month + 1
    if emonth > 12:
        emonth = 1
        eyear += 1

    create_monthly_focal_temp(year, month, eyear, emonth)

