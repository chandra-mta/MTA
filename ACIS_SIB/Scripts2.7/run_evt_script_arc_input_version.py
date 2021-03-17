#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           run_evt_script.py: extract sib data from event 1 or 2 acis data                                 #
#               this takes arc5gl output and extract data                                                   #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Jan 06, 2017                                                                       #
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

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param ', shell='tcsh')
#ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/Lev1/Reportdir/'
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
sys.path.append(mta_dir)
#
#--- directory path
#
s_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/'
b_dir = s_dir + 'Sib_corr/'
sys.path.append(b_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import exclude_srouces      as es
import sib_corr_functions   as scf

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- run_evt_script: extract sib data from acis event  data                            ---
#-----------------------------------------------------------------------------------------

def run_evt_script(lev="Lev1"):
    """
    extract sib data from acis event  data
    input: lev  --- lev of the data to be processed; either "Lev1" or "Lev2"
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
#    if eday < 3:
    if eday < 5:
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
    sday   = find_prev_date(smon, lev)
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

    #stop = lemon + '/' + leday + '/'  + leyear + ',00:00:00'
    stop = temp + '-' +  lemon + '-' + leday + 'T00:00:00'


    temp   = str(syear)
    lsyear = temp[2] + temp[3]
    lsmon  = str(smon)
    if smon < 10:
        lsmon = '0' + lsmon
    lsday  = str(sday)
    if int(float(sday)) < 10:
        lsday = '0' + lsday

    #start = lsmon + '/' + lsday + '/' + lsyear + ',00:00:00'
    start = temp + '-' + lsmon + '-' + lsday + 'T00:00:00'

#
#--- extract obsid list for the period
#
    try:
        scf.find_observation(start, stop, lev=lev)
#
#---  run the main script
#
        process_evt(lev)
    except:
        pass


#-----------------------------------------------------------------------------------------
#-- find_prev_date: find the last extreacted obsid date                                 --
#-----------------------------------------------------------------------------------------

def find_prev_date(cmon, lev):
    """
    find the last extreacted obsid date
    input:  cmon    --- current month
            lev     --- data level
    output: date    --- the date which to be used to start extracting data
    """

    afile = s_dir + lev + '/acis_obs'
#
#--- check whether file exist
#
    if os.path.isfile(afile):
        f     = open(afile, 'r')
        data  = [line.strip() for line in f.readlines()]
        f.close()
    
        if len(data) > 0:
            atemp = re.split('\s+', data[-1])
            try:
                mon   = atemp[-7]
#
#--- just in a case acis_obs is from the last month..
#
                dmon  = tcnv.changeMonthFormat(mon)
                if dmon == cmon:
                    date  = atemp[-6]
                else:
                    date  = '1'
#
#--- it seems that output format changed (1/4/17); so check the data in a different form
#
            except:
                btemp = re.split('\/', atemp[2])
                mon   = int(float(btemp[0]))
                if mon  == cmon:
                    date = btemp[1]
                else:
                    date = '1'
        else:
            date = '1'
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
        
#-----------------------------------------------------------------------------------------------
#-- convert_time_format: convert time format to be acceptable by arc5gl                      ---
#-----------------------------------------------------------------------------------------------

def convert_time_format(stime):
    """
    convert time format to be acceptable by arc5gl
    input:  stime   --- time
    output  simte   --- modified (if needed) time
    note: only time format does not accept is mm/dd/yy,hh:mm:ss which is aceptable in ar4cgl
    so convert that into an acceptable format: yyyy-mm-ddThh:mm:ss
    """
#
#--- if the time is seconds from 1998.1.1, just pass
#
    if isinstance(stime, float) or isinstance(stime, int):
        return stime
#
#--- time word cases; only mm/dd/yy,hh:mm:ss is modified
#
    mc = re.search('\,', stime)
    if mc is not None:
        atemp = re.split('\,', stime)
        btemp = re.split('\/', atemp[0])
        mon   = btemp[0]
        day   = btemp[1]
        yr= int(float(btemp[2]))
        if yr > 90:
            yr += 1900
        else:
            yr += 2000
            stime = str(yr) + '-' + mon + '-' + day + 'T' + atemp[1]
    
    return stime

#-----------------------------------------------------------------------------------------------
#-- process_evt: process ACIS SIB data                                                        --
#-----------------------------------------------------------------------------------------------

def process_evt(lev= 'Lev1'):
    """
    process lev1 or 2  ACIS SIB data
    input:  lev --  which level data to process; defalut: 'Lev1'
            it also reads acis_obs file to find fits file names
    output: processed fits files in <out_dir>/lres/
    """

    bin_dir =  s_dir + 'Sib_corr/'
    ldir    =  s_dir + lev + '/'
    indir   =  ldir  + 'Input/'
    outdir  =  ldir  + 'Outdir/'
    repdir  =  ldir  + 'Reportdir/'

    f    = open('./acis_obs', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    for obs in data:
        atemp = re.split('\s+', obs)
        btemp = re.split('_', atemp[0])
        ctemp = re.split('acisf', btemp[0])
        obsid = ctemp[1].strip()

        mc    = re.search('N', obsid)
        if mc is not None:
            dtemp = re.split('N', obsid)
            obsid = dtemp[0]
        print "OBSID: " + str(obsid)

        line = 'operation=retrieve\n'
        line = line + 'dataset=flight\n'
        line = line + 'detector=acis\n'
        if lev == 'Lev1':
            line = line + 'level=1\n'
            line = line + 'filetype=evt1\n'
        else:
            line = line + 'level=2\n'
            line = line + 'filetype=evt2\n'
        line = line + 'obsid=' + str(obsid) + '\n'
        line = line + 'go\n'

        fo   = open('./input_line', 'w')
        fo.write(line)
        fo.close()

        cmd1 = "/usr/bin/env PERL5LIB= "
        cmd2 = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ./input_line '
        cmd  = cmd1 + cmd2
        #scf.run_ascds(cmd, clean=0)
        bash(cmd,  env=ascdsenv)

        cmd   = 'ls acisf*fits* > ' + zspace
        os.system(cmd)
        f     = open(zspace, 'r')
        flist = [line.strip() for line in f.readlines()]
        f.close()
        mcf.rm_file(zspace)
        mcf.rm_file('./input_list')

        for fits in flist:
#
#--- exclude bright sources from the file
#
            try:
                es.exclude_sources(fits)
            except:
                cmd = 'rm -rf *fits*'
                os.system(cmd)
                continue 

            cmd  = 'mv *cleaned*fits ' + indir + '/. 2>/dev/null'
            os.system(cmd)
        
        cmd = 'rm -rf *fits*'
        os.system(cmd)
#
#--- extract acis evt1 files from archeive, and compute SIB
#
        try:
            scf.sib_corr_comp_sib(lev)
        except:
            try:
                scf.sib_corr_comp_sib(lev)
            except:
                pass
#
#--- clean up the files
#
        cmd  = 'rm -rf ' + indir + '/*fits ' + outdir + '/*fits ' + outdir + '/*ped* '
        os.system(cmd)

    
#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    lev = "Lev1"
    if len(sys.argv) == 2:
        lev = sys.argv[1]
        lev = lev.strip()

    ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/' + lev + '/Reportdir/'
    run_evt_script(lev)

