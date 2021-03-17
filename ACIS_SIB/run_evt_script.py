#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#           run_evt_script.py: extract sib data from event 1 or 2 acis data             #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           Last Update: Mar 03, 2021                                                   #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import math
import unittest
import time
import random
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folders
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions as mcf
import exclude_srouces      as es
import sib_corr_functions   as scf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
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
    if eday <= 4:
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
#--- find the last date of the previous data analyzed
#
    sday   = find_prev_date(smon, lev)
#
#--- now convert the date format 
#
    lemon = mcf.add_leading_zero(emon)
    leday = mcf.add_leading_zero(eday)
    stop  = str(eyear) + '-' + lemon + '-' + leday + 'T00:00:00'

    lsmon = mcf.add_leading_zero(smon)
    lsday = mcf.add_leading_zero(sday)
    start = str(syear) + '-' + lsmon + '-' + lsday + 'T00:00:00'
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
    afile = cor_dir + lev + '/acis_obs'
#
#--- check whether file exist
#
    if os.path.isfile(afile):
        data = mcf.read_data_file(afile)
    
        if len(data) > 0:
            atemp = re.split('\s+', data[-1])
            try:
                btemp = re.split('T', atemp[-4])
                ctemp = re.split('-', btemp[0])
                dmon  = int(float(ctemp[1]))
                day   = str(int(float(ctemp[2])))
            except:
                mon   = atemp[-7]
                dmon  = mcf.change_month_format(mon)
                day   = atemp[-6]
#
#--- just in a case acis_obs is from the last month..
#
            if dmon == cmon:
                date  = day
            else:
                date  = '1'
        else:
            date = '1'
    else:
        date = '1'

    return date

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
    ldir    =  cor_dir + lev + '/'
    indir   =  ldir  + 'Input/'
    outdir  =  ldir  + 'Outdir/'
    repdir  =  ldir  + 'Reportdir/'

    data    = mcf.read_data_file('./acis_obs')

    for obs in data:
        atemp = re.split('\s+', obs)
        obsid = atemp[0].strip()
        print("OBSID: " + str(obsid))
#
#--- extract evt 1/2 file
#
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

        flist = mcf.run_arc5gl_process(line)

        for fits in flist:
#
#--- exclude bright sources from the file
#
            es.exclude_sources(fits)

            cmd  = 'mv *cleaned*fits ' + indir + '/. 2>/dev/null'
            os.system(cmd)
        
        cmd = 'rm -rf *fits*'
        os.system(cmd)
#
#--- extract acis evt1 files from archeive, and compute SIB
#--- at some occasion, the process dies with unknown reason; so repeat twice
#--- to cover the failed case
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

    run_evt_script(lev)

