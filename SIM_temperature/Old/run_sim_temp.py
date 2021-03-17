#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#      run_sim_temp.py: update sim temperature data                                         # 
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Apr 27, 2016                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import time
import operator
import math
import numpy
import unittest

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param; ', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"
#
#--- reading directory list
#
path = '/data/mta/Script/SIM/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- a couple of things needed
#
dare   = mcf.get_val('.dare',   dir = bindata_dir, lst=1)
hakama = mcf.get_val('.hakama', dir = bindata_dir, lst=1)

#-----------------------------------------------------------------------------------------------------------
#-- run_sim_temp_script: run all scripts to update tsc_temps.txt data file                                --
#-----------------------------------------------------------------------------------------------------------

def run_sim_temp_script(year, sdate, edate):
    """
    run all scripts to update tsc_temps.txt data file
    input:  year    --- year of the data to be extracted
            sdate   --- stating ydate
            edate   --- ending ydate
        these three can be <blank>. if that is the case, the period starts from the
        day after the date of the last data entry to today
    output: updated <date_dir>/tsc_temps.txt
    """
#
#--- if the range is not given, start from the last date of the data entry
#
    tperiod = set_data_period(year, sdate, edate)
#
#--- process the data for each day
#
    for tent in tperiod:
        year  = tent[0]
        yday  = tent[1]
#
#--- covert date foramt to  mm/dd/yy, 00:00:00
#
        [start, stop] = start_stop_period(year, yday)
#
#--- extract trace log files. if chk == 0, no files are extracted
#
        chk = run_filter_script(start, stop)

        if chk == 0:
            continue
        else:
#
#--- run pre-proccessor 
#
            cmd = bin_dir + 'proc_sim.pl'
            os.system(cmd)
#
#--- extract data
            tdir = exc_dir + 'TL'
            if os.listdir(tdir) != []:
                #cmd = 'cat ' + exc_dir +  'TL/PRIMARYSIM_*.tl.tmp |' + bin_dir + 'monitor_sim.pl'
                cmd =  bin_dir + 'monitor_sim.pl'
                os.system(cmd)
                cmd = 'rm -rf ' + exc_dir + 'TL/*'
                os.system(cmd)
#
#--- clean up the main data file:  tsc_temps.txt
#
    clean_tsc_data()

#-----------------------------------------------------------------------------------------------------------
#-- start_stop_period: convert year and yday to the mm/dd/yy, 00:00:00 format                             --
#-----------------------------------------------------------------------------------------------------------

def start_stop_period(year, yday):
    """
    convert year and yday to the mm/dd/yy, 00:00:00 format
    input:  year    --- year
            yday    --- yday
    output: [start, stop]   --- in the format of mm/dd/yy, 00:00:00 
    """

    lyear = str(year)
    syear = lyear[2] + lyear[3]

    [mon, mday] = tcnv.changeYdateToMonDate(year, yday)

    smon = str(mon)
    if mon < 10:
        smon = '0' + smon
    sday = str(mday)
    if mday < 10:
        sday = '0' + sday

    start = smon + '/' + sday + '/' +  syear

    stop  = start
    start = start + ',00:00:00'
    stop  = stop  + ',23:59:59'

    return [start, stop]
            

#-----------------------------------------------------------------------------------------------------------
#-- run_filter_script: collect data and run sim script                                                   ---
#-----------------------------------------------------------------------------------------------------------

def run_filter_script(start, stop):
    """
    collect data and run sim script
    input:  none
    outout: various *.tl files
            return 1 if the data extracted; otherwise: 0
    """
#
#--- get Dump_EM files
#
    unprocessed_data = get_dump_em_files(start, stop)

    if len(unprocessed_data) < 1:
        return 0
    else:
#
#--- create .tl files from Dmup_EM files
#
        filters_sim(unprocessed_data)

        cmd = 'rm -f ' + exc_dir + 'EM_Data/*Dump_EM*'
        os.system(cmd)
        cmd = 'mv *.tl ' + exc_dir + 'TL/.'
        os.system(cmd)

        return 1

#-----------------------------------------------------------------------------------------------------------
#-- filters_sim: run acorn for sim filter                                                                 --
#-----------------------------------------------------------------------------------------------------------

def filters_sim(unprocessed_data):
    """
    run acorn for sim filter
    input: unprocessed_data    --- list of data
    output: various *.tl files
    """

    for ent in unprocessed_data:
        cmd1 = '/usr/bin/env PERL5LIB="" '
        cmd2 = ' /home/ascds/DS.release/bin/acorn -nOC msids_sim.list -f ' + ent
        cmd  = cmd1 + cmd2
        try:
            print 'Data: ' + ent
            bash(cmd, env=ascdsenv)
        except:
            pass


#-----------------------------------------------------------------------------------------------------------
#-- get_dump_em_files: extract Dump_EM files from archive                                                 --
#-----------------------------------------------------------------------------------------------------------

def get_dump_em_files(start, stop):
    """
    extract Dump_EM files from archive
    input:  start   --- start time in format of mm/dd/yy
            stop    --- stop time in format of mm/dd/yy
    output: *Dump_EM* data in ./EM_data directory
            data    --- return data lists
    """
#
#--- get data from archive
#
    run_arc4gl(start, stop)
#
#--- move the data to EM_Data directory and return the list of the data extracted
#
    cmd = 'mv *Dump_EM* ' + exc_dir + 'EM_Data/. 2>/dev/null'
    os.system(cmd)

    cmd = 'ls ' + exc_dir + 'EM_Data/ > ' + zspace
    os.system(cmd)
    f   = open(zspace, 'r')
    test = f.read()
    f.close()
    mcf.rm_file(zspace)

    mc   = re.search('sto', test)

    if mc is not None:
        cmd = 'gzip -d ' + exc_dir + 'EM_Data/*gz'
        os.system(cmd)

        cmd = 'ls ' + exc_dir + 'EM_Data/*Dump_EM*sto > ' + zspace
        os.system(cmd)

        f    = open(zspace, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        mcf.rm_file(zspace)
    else:
        data = []

    return  data

#-----------------------------------------------------------------------------------------------------------
#-- run_arc4gl: extract data from archive using arc4gl                                                    --
#-----------------------------------------------------------------------------------------------------------

def run_arc4gl(start, stop, operation='retrieve', dataset='flight', detector='telem', level='raw'):
    """
    extract data from archive using arc4gl
    input:  start   --- starting time in the format of mm/dd/yy,hh/mm/ss. hh/mm/ss is optional
            stop    --- stoping time
            operation   --- operation command.  default = retrieve
            dataset     --- dataset name.       default = flight
            detector    --- detector name       default = telem
            level       --- level               defalut = raw
    output: extracted data set
    """
#
#--- write arc4gl command
#
    line = 'operation = '       + operation  + '\n'
    line = line + 'dataset = '  + dataset    + '\n'
    line = line + 'detector = ' + detector   + '\n'
    line = line + 'level = '    + level      + '\n'
    line = line + 'tstart='     + str(start) + '\n'
    line = line + 'tstop='      + str(stop)  + '\n'
    line = line + 'go\n'

    fo = open(zspace, 'w')
    fo.write(line)
    fo.close()
#
#--- run arc4gl 
#
    cmd1 = '/usr/bin/env PERL5LIB=""'
    ####cmd2 = '  source /home/mta/bin/reset_param;'
    cmd2 =  ' echo ' + hakama + '|arc4gl -U' + dare + ' -Sarcocc -i' + zspace
    cmd  = cmd1 + cmd2
    bash(cmd, env=ascdsenv)
    mcf.rm_file(zspace)

#-----------------------------------------------------------------------------------------------------------
#-- clean_tsc_data: order and removed duplicated entries                                                  --
#-----------------------------------------------------------------------------------------------------------

def clean_tsc_data():
    """
    order and removed duplicated entries
    input:  none, but read from data file tsc_temps.txt
    output: cleaned tsc_temps.txt
    """

    file = data_dir + 'tsc_temps.txt'
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    header = data[0]
    body   = data[1:]

    body.sort()

    prev = ''
    cleaned = []
    for ent in body:
        if ent == prev:
            continue
        else:
            prev = ent
            cleaned.append(ent)

    fo   = open(file, 'w')
    fo.write(header)
    fo.write('\n')

    for ent in cleaned:
#
#--- only the lines with full 9 entries are put back
#
        atemp = re.split('\s+', ent)
        if len(atemp) == 9:
            fo.write(ent)
            fo.write('\n')
    fo.close()

#-----------------------------------------------------------------------------------------------------------
#-- set_data_period: create a list of dates to be examined                                               ---
#-----------------------------------------------------------------------------------------------------------

def set_data_period(year, sdate, edate):
    """
    create a list of dates to be examined
    input:  year    --- year of the date
            sdate   --- starting yday
            edate   --- ending ydate
        these three can be <blank>. if that is the case, it will fill from 
        the date of the last data entry to today's date
    output: dperiod --- a list of dates in the formant of [[2015, 199], [2015, 200], ...]
    """
    if year != '':
        dperiod = []
        for yday in range(sdate, edate+1):
            dperiod.append([year, yday])
    else:
#
#--- find today's date
#
        today = time.localtime()
        year  = today.tm_year
        yday  = today.tm_yday
#
#--- find the last date of the data entry
#--- entry format: 2015365.21252170    16.4531   27.0   33.0     10   174040    0    0   28.4
#
        file = data_dir + 'tsc_temps.txt'
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    
        lent  = data[-1]
        atemp = re.split('\s+', lent)
        btemp = re.split('\.',  atemp[0])
        ldate = btemp[0]
    
        dyear = ldate[0] + ldate[1] + ldate[2] + ldate[3]
        dyear = int(float(dyear))
        dyday = ldate[4] + ldate[5] + ldate[6]
        dyday = int(float(dyday))
#
#--- check whether it is a leap year
#
        lchk  = tcnv.isLeapYear(dyear)
        if lchk == 1:
            base = 366
        else:
            base = 365
#
#--- now start filling the data period (a pair of [year, ydate])
#
        dperiod = []
#
#--- for the case, year change occurred
#
        if dyear < year:
    
            for ent in range(dyday, base+1):
                dperiod.append([dyear, ent])
    
            for ent in range(1, yday+1):
                dperiod.append([year, ent])
#
#--- the period in the same year
#
        else:
            for ent in range(dyday, yday+1):
                dperiod.append([year, ent])
#
#--- return the result
#
    return dperiod

#-----------------------------------------------------------------------------------------------------------
 
if __name__ == "__main__":
#
#--- if you like to specify the date period, give
#---  a year and starting yday and ending yday
#
    if len(sys.argv) > 3:
        year  = int(float(sys.argv[1]))
        sdate = int(float(sys.argv[2]))
        edate = int(float(sys.argv[3]))
#
#--- if the date period is not specified,
#--- the period is set from the last entry date to
#--- today's date
#
    else:
        year  = ''
        sdate = ''
        edate = ''

    run_sim_temp_script(year, sdate, edate)
