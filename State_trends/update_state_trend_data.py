#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#   update_state_trend_data.py: extract data from dumpdata and update mj and sim state trend data   #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Mar 10, 2021                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import time
import numpy
import random
import Chandra.Time
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/OBT/Scripts/house_keeping/dir_list'
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions     as mcf
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------
#-- update_state_trend_data: extract data from dumpdata and update mj and sim state trend data 
#----------------------------------------------------------------------------

def update_state_trend_data(year):
    """
    extract data from dumpdata and update mj and sim state trend data
    """
    extract_data('mj',  year)
    extract_data('sim', year)

#----------------------------------------------------------------------------
#-- extract_data: extract data and update the data file                    --
#----------------------------------------------------------------------------

def extract_data(itype, year):
    """
    extract data and update the data file
    input:  itype   --- mj or sim data cotegory
    output: data file
    """
#
#--- find today's date
#
    if year == '':
        out   = time.strftime("%Y:%j", time.gmtime())
        atemp = re.split(':', out)
        year  = int(atemp[0])
        yday  = int(atemp[1])
        ychk  = 0
#
#--- if a year is given, fill up the gap till the end of the year
#
    else:
        if mcf.is_leapyear(year):
            yday  = 366
        else:
            yday  = 365
        ychk  = 1
#
#--- find the unproccessed data
#
    out   = find_new_data_file(year, yday, itype, ychk)
    ltime = out[2]
#
#--- the data go over year boundary (when the second list of "out" has values)
#
    if len(out[1]) > 0:
        tyear = year -1
#
#--- run last year part of the data
#
        run_extract(out[0], tyear, itype, ltime)
        cmd = 'mv ' + data_dir + 'todays_data ' + data_dir +'todays_data2'
        os.system(cmd)
#
#--- run this year part of the data
#
        run_extract(out[1], year, itype, ltime)
        cmd = 'cat ' + data_dir + 'todays_data2 ' 
        cmd  = cmd   + data_dir + 'todays_data > ' + data_dir + 'todays_data'
        os.system(cmd)
#
#--- handle data just this year
#
    else:
        run_extract(out[0], year, itype, ltime)
#
#--- create symbolic link at the beginning of the year
#
    if (yday >1) and (yday < 4):
        if itype == 'mj':
            head = 'comprehensive_data_summary'
        else:
            head = 'sim_data_summary'

        cmd = 'rm -f ' + html_dir + head
        os.system(cmd)
        cmd = 'ln -s ' + itype.upper() + '/' + head + str(year) + ' ' + html_dir + 'mta_' +  head
        os.system(cmd)

#----------------------------------------------------------------------------
#-- run_extract: process dump data and update data table                   --
#----------------------------------------------------------------------------

def run_extract(dlist, dyear, itype, ltime):
    """
    process dump data and update data table
    input:  dlist   --- a list of data
            dyear   --- year of the data cover
            itype   --- mj or sim data cotegory
            ltime   --- the last entry of the data in seconds from 1998.1.1
    output: data_summary table file
    """
    if itype == 'mj':
        s_file = 'simpos_acis.scr'
        n_file = 'mj_nawkscript'
        o_file = 'comprehensive_data_summary'
        d_dir  = mj_data_dir
    else:
        s_file = 'simpos_acis2.scr'
        n_file = 'sim_nawkscript'
        o_file = 'sim_data_summary'
        d_dir  = sim_data_dir
#
#--- convert the data into ascii format
#
    for dfile in dlist:
        cmd = 'gzip -dc ' + dfile + '> ' + zspace
        os.system(cmd)
        cmd = '/home/ascds/DS.release/bin/acorn -f ' + zspace + ' -nCO ' 
        cmd = cmd + house_keeping +  s_file + ' -T -o'
        run_ascds(cmd)
        mcf.rm_files(zspace)
        mcf.rm_files('./systemlog')
#
#--- combine all output
#
    cmd = 'cat outsimpos* >' + zspace
    os.system(cmd)
    mcf.rm_files('./outsimpos*')

    data = mcf.read_data_file(zspace, remove=1)
    clen = 0
    save = []
#
#--- check each line
#
    for ent in data:
#
#--- if it is the header line, count how many columns 
#
        mc = re.search('TIME', ent)
        if mc is not None:
            atemp = re.split('\s+', ent)
            if clen == 0:
                clen  = len(atemp)
#
#--- keep only the line which contains the numbers of data same as the header
#
        else:
            atemp = re.split('\s+', ent)
            if len(atemp) == clen:
                out = ent.replace('\s+', '\t')
                save.append(out)
#
#--- sort the data and write it out
#
    save.sort()

    eline = ''
    for ent in save:
        eline = eline + str(ent) + '\n'
    with open('./temp_out', 'w') as fo:
        fo.write(eline)
#
#--- convert the data format to <yyyy>:<ddd>:<hh>:<mm>:<ss> and clean up the format
#
    mcf.rm_files(zspace)
    cmd   = 'gawk -F"\\t" -f ' + house_keeping +  n_file + ' ./temp_out >'  + zspace
    run_ascds(cmd)
    mcf.rm_files('./temp_out')
#
#--- read the file and remove the data lines which were proccessed in past
#
    data  = mcf.read_data_file(zspace, remove=1)
    save  = []
    for ent in data:
        atemp = re.split('\s+', ent)
        ctime = Chandra.Time.DateTime(atemp[0]).secs
        if ctime > ltime:
            save.append(ent)

    if len(save) > 0:
        eline = ''
        for ent in save:
            eline = eline + str(ent) + '\n'
        with  open(zspace, 'w') as fo:
            fo.write(eline)

    else:
        cfile = data_dir + 'todays_data'
        if os.path.isfile(cfile):
            cmd = 'rm -f ' + cfile
            os.system(cmd)

        cmd = 'touch ' + cfile
        os.system(cmd)
        return
#
#--- combine the data into existing data file. if it does not exsit, create
#
    ofile = d_dir  + o_file + str(dyear)
    if os.path.isfile(ofile):
        cmd = 'cat ' + ofile + ' ' + zspace + ' > ztemp'
        os.system(cmd)
        cmd = 'mv ztemp ' + ofile
        os.system(cmd)
    else:
        cmd = 'cp  ' + zspace + ' '  + ofile
        os.system(cmd)
#
#--- save the data for focal plane temp reading
#
    if itype == 'mj':
        cmd = 'mv -f ' + zspace + ' ' + data_dir + 'todays_data'
        os.system(cmd)
    else:
        mcf.rm_files(zspace)

#----------------------------------------------------------------------------
#-- find_new_data_file: find which dump data files need to be processed    --
#----------------------------------------------------------------------------

def find_new_data_file(year, yday, itype, ychk):
    """
    find which dump data files need to be processed
    input:  year    --- year
            yday    --- yday
            itype   --- mj or sim data cotegory
            ychk    --- 1: if a year is specified; 0: multiple year possible.
    output: out     --- a list of lists of file names; second one is filled only
                        when the data go over year boundary
    """
    if itype == 'mj':
        o_file = 'comprehensive_data_summary'
        d_dir  = mj_data_dir
        header = 'mj_header'
    else:
        o_file = 'sim_data_summary'
        d_dir  = sim_data_dir
        header = 'sim_header'
#
#--- find currently available data file
#
    ofile = d_dir +  o_file + str(year)
#
#--- if there is not a data file for this year, create one and put the header
#--- then process the last year's data
#
    if not os.path.isfile(ofile):
        cmd   = 'cp ' + house_keeping + header + ' ' + ofile
        os.system(cmd)

        ofile = d_dir  + o_file + str(year-1)
#
#--- find the last entry date
#
    data  = mcf.read_data_file(ofile)
    if len(data) < 2:
        lyear = year
        lyday = 1
        lhm   = 0
        ltime = str(year) + ':001:00:00:00'
        ltime = Chandra.Time.DateTime(ltime).secs
    else:
        atemp = re.split('\s+', data[-1])
        btemp = re.split(':',   atemp[0])
        lyear = int(btemp[0])
        lyday = int(btemp[1])
        lhm   = int(btemp[2] + btemp[3])
        ltime = Chandra.Time.DateTime(atemp[0]).secs
#
#--- find currently available input data
#
    cmd   = 'ls -rt /dsops/GOT/input/*Dump_EM*gz >' + zspace
    os.system(cmd)
    data  = mcf.read_data_file(zspace, remove=1)
    save  = []
    nsave = []
    for ent in data:
        atemp = re.split('input\/', ent)
        btemp = re.split('_', atemp[1])
        cyear = int(btemp[0])
        cyday = int(btemp[3])
        chm   = int(btemp[4])

        if cyear > lyear and ychk == 0:
            nsave.append(ent)
        elif cyear == lyear:
            if cyday > lyday:
                save.append(ent)
            elif cyday < lyday:
                continue
            else:
                if chm > lhm:
                    save.append(ent)

    out = [save, nsave, ltime]
    return out 
            
#----------------------------------------------------------------------------
#-- run_ascds: running ascds related command                               --
#----------------------------------------------------------------------------

def run_ascds(cmd2):
    """
    running ascds related command
    input:  cmd2    --- command to be run
    output: result of cmd2
    """

    cmd1 = '/usr/bin/env PERL5LIB= ' 
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)


#----------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        year = int(sys.argv[1])
    else:
        year = ''
    update_state_trend_data(year)

