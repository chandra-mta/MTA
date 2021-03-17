#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       sib_corr_functions.py: save sib correlation related functions           #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           Last Update: Mar 03, 2021                                           #
#                                                                               #
#################################################################################

import sys
import os
import string
import re
import math
import unittest
import time
import Chandra.Time
import random
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; \
                   source /home/mta/bin/reset_param ', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folders
#
sys.path.append(mta_dir)
sys.path.append(sybase_dir)
sys.path.append(bin_dir)

import mta_common_functions   as mcf
import set_sybase_env_and_run as sser
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
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
#
#--- set pipe process environment
#
    ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/'+ lev + '/Reportdir/'

    ldir    =  cor_dir + lev + '/'
    indir   =  ldir    + 'Input/'
    outdir  =  ldir    + 'Outdir/'
    repdir  =  ldir    + 'Reportdir/'

    cmd  = 'ls ' + indir + '/* > ' + zspace
    os.system(cmd)

    with open(zspace, 'r') as f:
        test = f.read()
    mcf.rm_files(zspace)
#
#--- check whether fits files around
#
    mc  = re.search('fits', test)
    if mc is not None:
        cmd = 'ls ' +indir + '*fits > ' +  indir + 'input_dat.lis'
    else:
        cmd = 'echo "" > ' + indir + 'input_dat.lis'
    os.system(cmd)
#
#--- run flt_run_pipe and process the data
#
    cmd = ' flt_run_pipe -i ' + indir + '  -r input -o ' 
    cmd = cmd + outdir + ' -t  mta_monitor_sib.ped -a "genrpt=no"'
    run_ascds(cmd)

    cmd = ' mta_merge_reports sourcedir=' + outdir + ' destdir=' + repdir
    cmd = cmd + ' limits_db=foo groupfile=foo stprocfile=foo grprocfile=foo '
    cmd = cmd + ' compprocfile=foo cp_switch=yes'
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
    data = run_arc5gl_browse(start, stop, lev)
#
#--- create obsid list
#
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

    if os.path.isfile('./acis_obs') and os.stat('./acis_obs').st_size > 0:
        cmd = 'mv -f ./acis_obs ./acis_obs~'
        os.system(cmd)

    if len(tlist) > 0:
        with open('./acis_obs', 'w') as fo:
            for ent in tlist:
                fo.write(save[ent])
    else:
        cmd = 'touch ./acis_obs'
        os.system(cmd)
    

#-----------------------------------------------------------------------------------------
#-- run_arc5gl_browse: run arc5gl to get a list of fits files in the given time period  --
#-----------------------------------------------------------------------------------------

def run_arc5gl_browse(start, stop, lev='Lev1'):
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

    f_list = mcf.run_arc5gl_process(line)

    return f_list

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
#
#-- sql command
#
    cmd = 'select targname,instrument,soe_st_sched_date,targid,'
    cmd = cmd + 'seq_nbr from target where obsid=' + str(obsid)

    try:
#
#--- call sql database
#
        out    = sser.set_sybase_env_and_run(cmd, fetch='fetchone')
#
#--- output is a list of the data
#
        target = clean_name(out[0])
        inst   = out[1]
        odate  = out[2]
        targid = out[3]
        seqno  = out[4]
#
#--- convert time into sec from 1998.1.1
#
        tsec   = mcf.convert_date_format(odate, ifmt='%Y-%m-%dT%H:%M:%S', ofmt='chandra')

        line   = str(obsid) + '\t' + target      + '\t' + str(odate) + '\t' + str(tsec) 
        line   = line       + '\t' + str(targid) + '\t' + str(seqno) + '\n'

        return [tsec, line]

    except:
        return NULL

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
#-- remove_old_reg_file: remove old reg files                                           --
#-----------------------------------------------------------------------------------------

def remove_old_reg_file(lev):
    """
    remove old reg files
    input:  lev --- level 1 or 2
    output: none
    """
#
#--- set the cut time to 90 days ago
#
    now = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    now = Chandra.Time.DateTime(now).secs
    cut = now - 86400 * 90.0

    cmd = 'ls ' + cor_dir + 'Lev' + str(lev) + '/Reg_files/* > ' + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    for ifile in data:
        out  = os.path.getmtime(ifile)
        out  = time.strftime('%Y:%j:%H:%M:%S', time.gmtime(out))
        comp = Chandra.Time.DateTime(out).secs
        if comp < cut:
            cmd = 'rm -rf ' + ifile
            os.system(cmd)

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    start = '2019-07-01T00:00:00'
    stop  = '2019-07-10T00:00:00'
    out   = find_observation(start, stop, 2)
    print(str(out))

#    out   = get_data_from_db(21494)
#    print('Sybase out: ' + str(out[1]))



#    remove_old_reg_file(1)
#    remove_old_reg_file(2)
