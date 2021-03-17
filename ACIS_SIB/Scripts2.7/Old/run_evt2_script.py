#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           run_evt2_script.py: extract sib data from event 2 acis data                                     #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Sep 17, 2015                                                                       #
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

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/Lev1/Reportdir/'
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
#--- directory path
#
s_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/'

#-----------------------------------------------------------------------------------------
#-- run_evt2_script: extract sib data from acis event 2 data                            --
#-----------------------------------------------------------------------------------------

def run_evt2_script():
    """
    extract sib data from acis event 2 data
    input: None
    output: extracted data in Outdir/
    """
#
#--- find today's date information (in local time)
#
    tlist = time.localtime()

    eyear  = tlist[0]
    emon   = tlist[1]
    eday   = tlist[2]
#
#--- if today is before the 5th day of the month, complete the last month
#
    #if eday < 5:
    if eday < 15:
        eday = 1
        syear = eyear
        smon  = emon -1
        if smon < 1:
            syear -= 1
            smon   = 12
    else:
        syear = eyear
        smon  = emon
#
#--- find the last date of the previous data anlyzed
#
    sday   = find_prev_date(emon)
#
#--- now convert the date format 
#
    temp   = str(eyear)
    leyear = temp[2] + temp[3]
    lemon  = str(emon)
    if emon < 10:
        lemon = '0' + lemon
    leday  = str(eday)
    if eday < 10:
        leday = '0' + leday

    stop = lemon + '/' + leday + '/'  + leyear + ',00:00:00'


    temp   = str(syear)
    lsyear = temp[2] + temp[3]
    lsmon  = str(smon)
    if smon < 10:
        lsmon = '0' + lsmon
    lsday  = str(sday)
    if int(float(sday)) < 10:
        lsday = '0' + lsday

    start = lsmon + '/' + lsday + '/' + lsyear + ',00:00:00'
#
#--- extract obsid list for the period
#
    cmd1 = '/usr/bin/env PERL5LIB="" ' 
    cmd2 = ' source /home/mta/bin/reset_param; perl ' + s_dir + 'Sib_corr/sib_corr_find_observation.perl ' + start + ' ' + stop
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#---  run the main script
#
    cmd1 = '/usr/bin/env PERL5LIB="" '
    cmd2 = ' source /home/mta/bin/reset_param; perl  /data/mta/Script/ACIS/SIB/Correct_excess/Lev2/process_evt2.perl'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)


#-----------------------------------------------------------------------------------------
#-- find_prev_date: find the last extreacted obsid date                                 --
#-----------------------------------------------------------------------------------------

def find_prev_date(cmon):
    """
    find the last extreacted obsid date
    input:  cmon    --- current month
    output: date    --- the date which to be used to start extracting data
    """

    afile = s_dir + '/Lev2/acis_obs'
#
#--- check whether file exist
#
    if os.path.isfile(afile):
        afile = s_dir + '/Lev2/acis_obs'
        f     = open(afile, 'r')
        data  = [line.strip() for line in f.readlines()]
        f.close()
    
        atemp = re.split('\s+', data[-1])
        mon   = atemp[3]
#
#--- just in a case acis_obs is from the last month..
#
        dmon  = tcnv.changeMonthFormat(mon)
        if dmon == cmon:
            date  = atemp[4]
        else:
            date  = '1'
    else:
        date = "1"

    return date


#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

def clean_up_dir(ldir):

    if os.path.isdir(ldir):
        cmd = 'rm -rf ' + ldir + '*'
        os.system(cmd)
    else:
        cmd = 'mkdir ' + ldir
        os.system(cmd)
        
    
#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    run_evt2_script()

