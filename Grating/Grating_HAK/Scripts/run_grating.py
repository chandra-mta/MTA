#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       run_grating.py: process grating data                                    #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Mar 09, 2021                                           #
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
import random
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv  = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Grating/Grating_HAK/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf

m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

admin  = 'tisobe@cfa.harvard.edu'           #--- get email notification about new grating obs

#--------------------------------------------------------------------------------------
#-- run_grating: controlling function to run the script                              --
#--------------------------------------------------------------------------------------

def run_grating(full=0):
    """
    controlling function to run the script
    input:  full --- indicator of whether we want to run for the entire last month: 
                     default = 0: no, otherwise yes
    output: <data_dir>/<dir> where dir is <Mon><yy>
    """
#
#--- set data collecting range
#
    (start, stop, idir) = find_time_interval(full)
#
#--- extract needed data fits files
#
    run_arc5gl(start, stop)
#
#--- process fits files
#
    run_idl(idir)
#
#--- update records
#
    get_obslist()
#
#--- move the data to an appropriate location
#
    cdir = data_dir + idir
    if os.path.isdir(cdir):
        cmd = 'cp -rf ' + exc_dir + 'Gratings/' + idir + '/* ' + cdir + '/.'
        os.system(cmd)
        cmd = 'rm -rf ' + exc_dir + 'Gratings/' + idir
        os.system(cmd)
    else:
        cmd = 'mv ' + exc_dir + 'Gratings/' + idir + ' ' + data_dir + '/.'
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
    ifile = house_keeping +'arc_template'
    with open(ifile, 'r') as f:
        line = f.read()

    line = line.replace('#START#', start)
    line = line.replace('#STOP#',  stop)

    flist = mcf.run_arc5gl_process(line)
#
#--- remove unwanted fits files
#
    os.system('rm *src1a*')

#--------------------------------------------------------------------------------------
#-- run_idl: process fits files with an updated idl scripts                          --
#--------------------------------------------------------------------------------------

def run_idl(idir):
    """
    process fits files with an updated idl scripts
    input:  idir --- the name of output directory
    output: dir/<stemp> --- a directory which contains the processed data
    """
#
#--- read a template and create the current command file
#
    ifile = house_keeping + 'pl_template'
    with open(ifile, 'r') as f:
        line = f.read()

    line = line.replace('#DIR#', idir)

    with open('./mk_idl_command.pl', 'w') as fo:
        fo.write(line)
#
#--- make an output directory
#
    cmd = 'mkdir -p ' + exc_dir + 'Gratings/' + idir
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
    
            idir  = m_list[lmon-1] + slyear[2] + slyear[3]
#
#--- this month 1st to 10th day
#
        elif day < 20:
            start = syear + '-' + smon + '-01T00:00:00'
            stop  = syear + '-' + smon + '-10T00:00:00'

            idir  = m_list[mon-1] + syear[2] + syear[3]
#
#--- this month 10th to 20th day
#
        else:
            start = syear + '-' + smon + '-10T00:00:00'
            stop  = syear + '-' + smon + '-20T00:00:00'

            idir  = m_list[mon-1] + syear[2] + syear[3]
#
#--- the entire last month
#
    else:
        lyear = year
        lmon  = mon -1
        if lmon < 1:
            lmon   = 12
            lyear -= 1

        slyear = str(lyear)
        slmon  = mcf.add_leading_zero(lmon)

        start = slyear + '-' + slmon + '-01T00:00:00'
        stop  = syear  + '-' + smon  + '-01T00:00:00'

        idir  = m_list[lmon-1] + slyear[2] + slyear[3]

    return [start, stop, idir]

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

            tdir = data_dir  + m_list[k] + lyr
            if os.path.isdir(tdir) and len(os.listdir(tdir)) > 0:
                cmd = 'ls -d ' + tdir + '/* >> ' + data_dir + 'obslist'
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
    odata = mcf.read_data_file(ifile)

    ifile = data_dir  + 'obslist'
    ndata = mcf.read_data_file(ifile)

    diff  = set(ndata) - set(odata)
    if len(diff) > 0:
        line = 'New Gratings Observations\n\n'
        for ent in diff:
            line = line + ent + '\n'

        with open(zspace, 'w') as fo:
            fo.write(line)

        cmd = 'cat ' + zspace + '|mailx -s \"Subject: New Gratings Observations\n\" ' + admin 
        os.system(cmd)

        mcf.rm_file(zspace)

#--------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        full = int(sys.argv[1])
    else:
        full = 0

    run_grating(full)
    notify_new_gratings_obs()

