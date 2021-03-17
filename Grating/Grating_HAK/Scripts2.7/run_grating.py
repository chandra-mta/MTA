#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#       run_grating.py: process grating data                                    #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Jul 19, 2018                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import datetime
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv  = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Grating/Grating_HAK/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf

m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

admin  = 'tisobe@cfa.harvard.edu'           #--- get email notification about new grating obs

#--------------------------------------------------------------------------------------
#-- run_grating: controlling function to run the script                              --
#--------------------------------------------------------------------------------------

def run_grating(full=0):
    """
    controlling function to run the script
    input:  full --- indicator of whether we want to run for the entire last month: default = 0: no, otherwise yes
    output: <data_dir>/<dir> where dir is <Mon><yy>
    """
#
#--- set data collecting range
#
    (start, stop, dir) = find_time_interval(full)
#
#--- extract needed data fits files
#
    run_arc5gl(start, stop)
#
#--- process fits files
#
    run_idl(dir)
#
#--- update records
#
    get_obslist()
#
#--- move the data to an appropriate location
#
    cdir = data_dir + dir
    if os.path.isdir(cdir):
        cmd = 'cp -rf ' + exc_dir + 'Gratings/' + dir + '/* ' + cdir + '/.'
        os.system(cmd)
        cmd = 'rm -rf ' + exc_dir + 'Gratings/' + dir
        os.system(cmd)
    else:
        cmd = 'mv ' + exc_dir + 'Gratings/' + dir + ' ' + data_dir + '/.'
        os.system(cmd)
#
#--- clean up
#
    os.system('rm -rf *.fits.gz')
    os.system('rm -rf run_arc mk_idl_command.pl mkcommand.idl')

#--------------------------------------------------------------------------------------
#-- run_arc5gl: extract acis and hrc evt1a.fits files using arc4gl                   --
#--------------------------------------------------------------------------------------

def run_arc5gl(start, stop):
    """
    extract acis and hrc evt1a.fits files using arc4gl
    input:  start   --- start time in the format of 2018-01-01:00:00:00
            stop    --- stop time
    output: fits files (e.g., acisf17108_001N002_evt1a.fits.gz)
    """
#
#--- read a template and create the current command file
#
    file = house_keeping +'arc_template'

    line = open(file, 'r').read()
    line = line.replace('#START#', start)
    line = line.replace('#STOP#',  stop)

    fo   = open('./run_arc', 'w')
    fo.write(line)
    fo.close()
#
#--- run arc5gl
#
    try:
        cmd = ' /proj/sot/ska/bin/arc5gl  -user isobe -script run_arc > ztemp_out'
        os.system(cmd)
    except:
        cmd = ' /proj/axaf/simul/bin/arc5gl -user isobe -script run_arc > ztemp_out'
        os.system(cmd)
#
#--- remove unwanted fits files
#
    os.system('rm *src1a* ztemp_out run_arc')

#--------------------------------------------------------------------------------------
#-- run_idl: process fits files with an updated idl scripts                          --
#--------------------------------------------------------------------------------------

def run_idl(dir):
    """
    process fits files with an updated idl scripts
    input:  dir --- the name of output directory
    output: dir/<stemp> --- a directory which contains the processed data
    """
#
#--- read a template and create the current command file
#
    file = house_keeping + 'pl_template'

    line = open(file, 'r').read()
    line = line.replace('#DIR#', dir)

    fo   = open('./mk_idl_command.pl', 'w')
    fo.write(line)
    fo.close()
#
#--- make an output directory
#
    cmd = 'mkdir -p ' + exc_dir + 'Gratings/' + dir
    os.system(cmd)
#
#--- run a perl script to create an idl script
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 =  ' perl ./mk_idl_command.pl '
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- run the idl script to process fits files
#
    os.system('idl  ./mkcommand.idl')

    os.system('rm -f ./mkcommand.idl ./mk_idl_command.pl')

#--------------------------------------------------------------------------------------
#-- find_time_interval: create start and stop time and output directory name        ---
#--------------------------------------------------------------------------------------

def find_time_interval_old(test='NO', month=4, year=2015):
    """
    ******THIS VERSION IS RETIRED !!! *********
    create start and stop time and output directory name
    input:  test    --- if it is test, yes. default: 'NO'
            month   --- test month input. default: 4. it is ignored if not test.
            year    --- test year input.  default: 2015. it is ignored if not test.
    output: start   --- start time in the format of mm/01/yy (e.g. 03/01/15)
            stop    --- stop time
            dir     --- output directory name in the format of <Mon><yy> (e.g. Jan15)
    """

#
#--- for the case if you want to run the test, there is option...
#
    if test == 'NO':
#
#--- this function gives you the current time. year in the format of 2015, and month in 4
#
        [year, month, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()
#
#--- if the date is later 5th of the month, work on this month
#
    if day > 4:
        month += 1
        if month > 12:
            month = 1
            year += 1
#
#--- we need start and stop times in the formats of 03/01/15, 04/01/15
#
    year_start = year
    year_end   = year

    this_month = str(month)
    if month < 10:
        this_month = '0' + this_month

    temp_month = month -1
    if temp_month < 1:
        temp_month = 12
        year_start -= 1
    last_month = str(temp_month)
    if temp_month < 10:
        last_month = '0' + last_month

    #temp       = str(year_start)
    #year_start = temp[2] + temp[3]

    #temp       = str(year_end)
    #year_end   = temp[2] + temp[3]

#    start = last_month + '/01/' + year_start
#    stop  = this_month + '/01/' + year_end
    start = str(year_start) + '-' + last_month + '-01T00:00:00'
    stop  = str(year_end)   + '-' + this_month + '-01T00:00:00'
#
#--- create the output directory name (format example: Apr15)
#
    cmonth = tcnv.changeMonthFormat(temp_month)
    temp     = str(year_start)
    year_dir = temp[2] + temp[3]
    dir      = cmonth + year_dir

    return (start, stop, dir)


#--------------------------------------------------------------------------------------
#-- find_time_interval: create start and stop time and output directory name        ---
#--------------------------------------------------------------------------------------

def find_time_interval(full=0):
    """
    set the data extraction time period
    input:  full    --- indicator of whether we want to extract the data for the entier last month
                        option: 0   ---- no; just 10 day period (1-10, 10-20, 20-the end of month)
    output: start   --- starting time in <yyyy>-<mm>-<dd>T00:00:00
            stop    --- stopping time in <yyyy>-<mm>-<dd>T00:00:00
            odir    --- output dir name in <Mmm><yy>
    """
#
#--- find today's date
#
    sout  = time.strftime("%Y:%m:%d", time.gmtime())
    atemp = re.split(':', sout)
    syear = atemp[0]
    year  = int(syear)
    smon  = atemp[1]
    mon   = int(smon)
    sday  = atemp[2]
    day   = int(sday)
    day   = 23
    sday  = str(day)
#
#--- for the case in which we want to find the nearest last 10 day period
#
    if full == 0:
#
#--- if the mday is < 10th day, check the last month 20th day to this month 1st
#
        if day < 10:
            lyear = year
            lmon  = mon -1
            if lmon < 1:
                lmon   = 12
                lyear -= 1
    
            slmon = str(lmon)
            if lmon < 10:
                slmon = '0' + slmon
            slyear = str(lyear)
    
            start = slyear + '-' + slmon + '-20T00:00:00'
            stop  = syear  + '-' + smon  + '-01T00:00:00'
    
            dir  = m_list[lmon-1] + slyear[2] + slyear[3]
#
#--- this month 1st to 10th day
#
        elif day < 20:
            start = syear + '-' + smon + '-01T00:00:00'
            stop  = syear + '-' + smon + '-10T00:00:00'

            dir  = m_list[mon-1] + syear[2] + syear[3]
#
#--- this month 10th to 20th day
#
        else:
            start = syear + '-' + smon + '-10T00:00:00'
            stop  = syear + '-' + smon + '-20T00:00:00'

            dir  = m_list[mon-1] + syear[2] + syear[3]
#
#--- the entire last month
#
    else:
        lyear = year
        lmon  = mon -1
        if lmon < 1:
            lmon   = 12
            lyear -= 1

        slmon = str(lmon)
        if lmon < 10:
            slmon = '0' + slmon
        slyear = str(lyear)

        start = slyear + '-' + slmon + '-01T00:00:00'
        stop  = syear  + '-' + smon  + '-01T00:00:00'

        dir  = m_list[lmon-1] + slyear[2] + slyear[3]

    return [start, stop, dir]


#--------------------------------------------------------------------------------------
#-- update_record: update the recormed of the process data ***** RETIRED             --
#--------------------------------------------------------------------------------------

def update_record(dir):
    """
    update the recormed of the process data
    input:  none    but read from the current output directory
    outpu:  obslist in 'Angles', 'EdE', 'Focus', 'Zero' directories
    """
##
##--- find out which data are processed from the output directory
##
#    cmd = 'ls /data/mta4/Gratings/' + dir + '> ./ztemp'
#    os.system(cmd)
#    f   = open('./ztemp', 'r')
#    data = [line.strip() for line in f.readlines()]
#    f.close()
#    os.system('rm ./ztemp')
#
#    line = ''
#    for each in data:
#        line = line + '../' + dir + '/' + each + '\n'
##
##--- there are four directories with "obslist"
##
#    for odir in ('Angles', 'EdE', 'Focus', 'Zero'):
#        file =  '/data/mta/www/mta_grat/' + odir + '/obslist'
#        fo   = open(file, 'a')
#        fo.write(line)
#        fo.close()

    
    tdate = datetime.datetime.today().strftime("%Y:%m")
    atemp = re.split(':', tdate)
    tyear = int(atemp[0])
    tmon  = int(float(atemp[1]))
    
    obslist = []
    for year in range(1999, tyear+1):
        temp  = str(year)
        pyear = temp[2] + temp[3]
    
        for k in range(0, 12):
            if (year == 1999) and (k < 7):
                continue
            elif (year == tyear) and (k >= tmon):
                break
    
            month = m_list[k]
            tdir = month + pyear
            cmd = 'ls -d ' + data_dir + tdir +'/* >' +  zspace
            os.system(cmd)
            f    = open(zspace, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()
         
            for ent in data:
                atemp = re.split('\/', ent)
                try:
                    test = float(atemp[-1])
                except:
                    test = 0
                if test != 0:
                    line = '../' +  tdir + '/' + atemp[-1]
                    obslist.append(line)
    
    fo = open('./obsliist', 'w')
    for ent in obslist:
        fo.write(ent)
        fo.write('\n')
    
    fo.close()

#    for odir in ('Angles', 'EdE', 'Focus', 'Zero'):
#        file =  '/data/mta/www/mta_grat/' + odir + '/obslist'
#        cmd  = 'cp ./obslist ' + file
#        os.system(cmd)

#------------------------------------------------------------------------------------
#-- get_obslist: update obslist                                                    --
#------------------------------------------------------------------------------------

def get_obslist():
    """
    update obslist
    input: none but read from <data_dir>/<Mmm><yy>/*
    ouptput:    <data_dir>/obslist
    """

    cmd = 'mv ' + data_dir + 'obslist ' + data_dir +'obslist~'
    os.system(cmd)

    out   = time.strftime("%Y:%m", time.gmtime())
    atemp = re.split(':', out)
    lyear = int(float(atemp[0]))
    lmon  = int(float(atemp[1]))
#
#--- arrange the data in time order from 1999 Aug to current month
#
    for year in range(1999, lyear+1):
        syear = str(year)
        lyr   = syear[2] + syear[3]
        for k in range(0, 12):
            if (year == 1999) and (k < 7):
                continue
            if (year == lyear) and (k >= lmon):
                break

            cmd = 'ls -d ' + data_dir  + m_list[k] + lyr 
            cmd = cmd +  '/* >> ' + data_dir + 'obslist'
            os.system(cmd)

#--------------------------------------------------------------------------------------
#-- notify_new_gratings_obs: send email notification to admin when new gratings observations are found
#--------------------------------------------------------------------------------------

def notify_new_gratings_obs():
    """
    send email notification to admin when new gratings observations are found
    input:  none
    output: email to admin
    """

    ifile = data_dir  + 'obslist~'
    odata = read_data_file(ifile)

    ifile = data_dir  + 'obslist'
    ndata = read_data_file(ifile)

    diff  = set(ndata) - set(odata)
    if len(diff) > 0:
        line = 'New Gratings Observations\n\n'
        for ent in diff:
            line = line + ent + '\n'

        fo  = open(zspace, 'w')
        fo.write(line)
        fo.close()

        cmd = 'cat ' + zspace + '|mailx -s \"Subject: New Gratings Observations\n\" ' + admin 
        os.system(cmd)

        mcf.rm_file(zspace)


#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------

def read_data_file(ifile):

    f    = open(ifile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    return data

#--------------------------------------------------------------------------------------

if __name__ == '__main__':

#
#--- if you like to run test, uncomment the next, and commend 
#--- on the main script calling
#
    #unittest.main()
    if len(sys.argv) > 1:
        full = int(sys.argv[1])
    else:
        full = 0

    run_grating(full)

    notify_new_gratings_obs()

