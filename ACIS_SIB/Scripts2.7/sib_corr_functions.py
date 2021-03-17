#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#       sib_corr_functions.py: save sib correlation related functions                                       #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Spe 04, 2018                                                                       #
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
#--- directory path
#
s_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/'
b_dir = s_dir + 'Sib_corr/'
#
#--- append path to a private folders
#
sys.path.append(mta_dir)
sys.path.append(b_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import OcatSQL              as sql
from OcatSQL        import OcatDB

#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

NULL   = 'na'

#-----------------------------------------------------------------------------------------
#-- sib_corr_comp_sib: extract acis evt1 files from archeive, and compute SIB           --
#-----------------------------------------------------------------------------------------

def sib_corr_comp_sib(lev):
    """
    extract acis evt1 files from archeive, and compute SIB
    input:  lev --- level of the data to be processed. either "Lev1" or "Lev2"
            the data is also read from ./Input/*fits
    output: proccessed fits files in out_dir/lres/*fits
    """

    ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/'+ lev + '/Reportdir/'

    bin_dir =  s_dir + 'Sib_corr/'
    ldir    =  s_dir + lev + '/'
    indir   =  ldir  + 'Input/'
    outdir  =  ldir  + 'Outdir/'
    repdir  =  ldir  + 'Reportdir/'

    cmd  = 'ls ' + indir + '/* > ' + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    test = f.read()
    f.close()
    mcf.rm_file(zspace)

    mc  = re.search('fits', test)
    if mc is not None:
        cmd = 'ls ' +indir + '*fits > ' +  indir + 'input_dat.lis'
    else:
        cmd = 'echo "" > ' + indir + 'input_dat.lis'
    os.system(cmd)


    cmd = ' flt_run_pipe -i ' + indir + '  -r input -o ' + outdir + ' -t  mta_monitor_sib.ped -a "genrpt=no"'
    run_ascds(cmd)

    cmd = ' mta_merge_reports sourcedir=' + outdir + ' destdir=' + repdir
    cmd = cmd + ' limits_db=foo groupfile=foo stprocfile=foo grprocfile=foo compprocfile=foo cp_switch=yes'
    run_ascds(cmd)


#-----------------------------------------------------------------------------------------
#-- find_observation: find information about observations in the time period            --
#-----------------------------------------------------------------------------------------

def find_observation(start, stop, lev):
    """
    find information about observations in the time period
    input:  start   --- starting time in the format of <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
            stop    --- stoping time in the format of <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
            lev     --- data level
    output: acis_obs    --- a list of the observation infromation 
    """
#
#--- run arc5gl to get observation list
#
    run_arc5gl_browse(start, stop,lev, zspace)
#
#--- create obsid list
#
    data = read_file(zspace, remove=1)
    obsid_list = []
    for ent in data:
        mc = re.search('acisf', ent)
        if mc is not None:
            atemp = re.split('acisf', ent)
            btemp = re.split('_', atemp[1])
            obsid = btemp[0]
            mc    = re.search('N', obsid)
            if mc is not None:
                ctemp = re.split('N', obsid)
                obsid = ctemp[0]
            obsid_list.append(obsid)
#
#--- remove duplicate
#
    o_set = set(obsid_list)
    obsid_list = list(o_set)
#
#--- open database and extract data for each obsid
#
    save  = {}
    tlist = []
    for obsid in obsid_list:
        out = get_data_from_db(obsid)
        if out != NULL:
            [tsec, line] = out
            tlist.append(tsec)
            save[tsec] = line

    tlist.sort()

    mcf.rm_file('./acis_obs')
    fo = open('./acis_obs', 'w')
    for ent in tlist:
        fo.write(save[ent])

    fo.close()

#-----------------------------------------------------------------------------------------
#-- run_arc5gl_browse: run arc5gl to get a list of fits files in the given time period  --
#-----------------------------------------------------------------------------------------

def run_arc5gl_browse(start, stop, lev='Lev1', outfile=zspace):
    """
    run arc5gl to get a list of fits files in the given time period
    input:  start   --- starting time in the format of <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
            stop    --- stoping time in the format of <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
            lev     --- data level
            outfile --- output file name, default: zspace
    output: a list of fits file names in <outfile>
    """

    line = 'operation=browse\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    if lev == 'Lev1':
        line = line + 'level=1\n'
        line = line + 'filetype=evt1\n'
    else:
        line = line + 'level=2\n'
        line = line + 'filetype=evt2\n'
    line = line + 'tstart=' + start + '\n'
    line = line + 'tstop='  + stop  + '\n'
    line = line + 'go\n'

    fo   = open('./input_line', 'w')
    fo.write(line)
    fo.close()

    #cmd  = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ./input_line > ' + outfile 
    cmd  = ' /proj/sot/ska/bin/arc5gl -user isobe -script ./input_line > ' + outfile 
    os.system(cmd)
    #run_ascds(cmd, clean=0)


#-----------------------------------------------------------------------------------------
#-- get_data_from_db: extract observation information from the database                 --
#-----------------------------------------------------------------------------------------

def get_data_from_db(obsid):
    """
    extract observation information from the database
    input:  obsid   --- obsid
    output: tsec    --- the data of the observation in seconds from 1998.1.1
            line    --- a string of the information extract
                        <obsid> <target name> <obs date> <obs date in sec>
                        <target id> < sequence number>
    """

    try:
        dbase  = OcatDB(obsid)
        tname  = dbase.origValue('targname')
        target = clean_name(tname)              #--- limit target name to 14 characters
        inst   = dbase.origValue('instrument')
        odate  = dbase.origValue('soe_st_sched_date')
        tsec   = convert_date_to_sectime(odate)
        targid = dbase.origValue('targid')
        seqno  = dbase.origValue('seq_nbr')

        line   = str(obsid) + '\t' + target      + '\t' + str(odate) + '\t' + str(tsec) 
        line   = line       + '\t' + str(targid) + '\t' + str(seqno) + '\n'

        return [tsec, line]
    except:
        return NULL

#-----------------------------------------------------------------------------------------
#-- convert_date_to_sectime: convert time in <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> to seconds from 1998.1.1
#-----------------------------------------------------------------------------------------

def convert_date_to_sectime(odate):
    """
    convert time in <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> to seconds from 1998.1.1
    input:  odate   --- date in the format of <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
    output: tsce    --- date in seconds from 1998.1.1
    """

    atemp  = re.split('\s+', str(odate))
    mon    = tcnv.changeMonthFormat(atemp[0])
    day    = int(float(atemp[1]))
    year   = int(float(atemp[2]))

    mc     = re.search('AM', atemp[3])
    if mc is not None:
        time  = atemp[3].replace('AM','')    
        btemp = re.split(':', time)
        hrs   = int(float(btemp[0]))
        mins  = int(float(btemp[1]))
    else:
        time  = atemp[3].replace('PM','')
        btemp = re.split(':', time)
        hrs   = int(float(btemp[0])) + 12
        mins  = int(float(btemp[1]))

    tsec  = tcnv.convertDateToTime2(year, mon, day, hours=hrs, minutes=mins)

    return tsec

#-----------------------------------------------------------------------------------------
#-- clean_name: convert the name into 14 character string                               --
#-----------------------------------------------------------------------------------------

def clean_name(name):
    """
    convert the name into 14 character string
    input:  name    --- the string of the name
    output: cname   --- the string of the name in 14 characters
    """

    name  = str(name)
    nlen  = len(name)
    cname = name[0]
    for i in range(1, 14):
        if i >= nlen:
            add_char = ' '

        elif name[i] == ' ':
            add_char = ' ' 

        else:
            add_char = name[i]

        cname = cname + add_char

    return cname

#-----------------------------------------------------------------------------------------
#-- run_ascds: run the command in ascds environment                                     --
#-----------------------------------------------------------------------------------------

def run_ascds(cmd, clean =0):
    """
    run the command in ascds environment
    input:  cmd --- command line
            clean   --- if 1, it also resets parameters default: 0
    output: command results
    """
    if clean == 1:
        acmd = '/usr/bin/env PERL5LIB=""  source /home/mta/bin/reset_param ;' + cmd
    else:
        acmd = '/usr/bin/env PERL5LIB=""  ' + cmd

    bash(acmd, env=ascdsenv)

#-----------------------------------------------------------------------------------------
#-- read_file: read a file                                                             ---
#-----------------------------------------------------------------------------------------

def read_file(file, remove=0):
    """
    read a file 
    input:  file    --- a file to be read
            remove  --- indicator whether to remove the file after it was read default=0 (no)
    output: data    --- a list of the data
    """

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if remove > 0:
        mcf.rm_file(file)

    return data

#-----------------------------------------------------------------------------------------
if __name__ == '__main__':

#    sib_corr_comp_sib()

    start = '2017-01-13T00:00:00'
    stop  = '2017-02-01T00:00:00'
    find_observation(start, stop, 2)
