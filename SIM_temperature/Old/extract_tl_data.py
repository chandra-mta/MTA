#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#      extract_tl_data.py: extract TL data                                                  #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Jul 19, 2023                                                   #
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
#path = '/data/mta/Script/SIM/Scripts/house_keeping/dir_list'
path = '/data/mta4/testSIM/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append("/data/mta4/Script/Python3.10/MTA")
#
#--- import several functions
#
import mta_common_functions   as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------
#-- extract_tl_data: extract TL data                                                 ---
#---------------------------------------------------------------------------------------

def extract_tl_data(year, sdate, edate):
    """
    extract tl data
    input:  year    --- year of the data to be extracted
            sdate   --- stating ydate
            edate   --- ending ydate
        these three can be <blank>. if that is the case, the period starts from the
        day after the date of the last data entry to today
    output: <exc_dir>/TL/PRIMARYSIM_<#>.tl
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

#---------------------------------------------------------------------------------------
#-- start_stop_period: convert year and yday to the mm/dd/yy, 00:00:00 format         --
#---------------------------------------------------------------------------------------

def start_stop_period(year, yday):
    """
    convert year and yday to the mm/dd/yy, 00:00:00 format
    input:  year    --- year
            yday    --- yday
    output: [start, stop]   --- in the format of mm/dd/yy, 00:00:00 
    """
    today = str(year) + ':' + mcf.add_leading_zero(yday, 3)
    start = today + ':00:00:00'
    stop  = today + ':23:59:59'

    return [start, stop]
            

#---------------------------------------------------------------------------------------
#-- run_filter_script: collect data and run sim script                               ---
#---------------------------------------------------------------------------------------

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
        cmd = 'mv -f  *.tl* ' + exc_dir + 'TL/.'
        os.system(cmd)

        return 1

#---------------------------------------------------------------------------------------
#-- filters_sim: run acorn for sim filter                                             --
#---------------------------------------------------------------------------------------

def filters_sim(unprocessed_data):
    """
    run acorn for sim filter
    input: unprocessed_data    --- list of data
    output: various *.tl files
    """

    for ent in unprocessed_data:
        cmd1 = '/usr/bin/env PERL5LIB="" '
        cmd2 = ' /home/ascds/DS.release/bin/acorn -nOC '
        cmd2 = cmd2 + house_keeping + 'msids_sim.list -f ' + ent
        cmd  = cmd1 + cmd2
        try:
            print('Data: ' + ent)
            bash(cmd, env=ascdsenv)
        except:
            pass

#---------------------------------------------------------------------------------------
#-- get_dump_em_files: extract Dump_EM files from archive                             --
#---------------------------------------------------------------------------------------

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
    out = run_arc5gl(start, stop)
#
#--- if data are extracted..
#
    if len(out) > 0:
#
#--- move the data to EM_Data directory and return the list of the data extracted
#
        cmd = 'mv *Dump_EM* ' + exc_dir + 'EM_Data/. 2>/dev/null'
        os.system(cmd)
    
        cmd = 'ls ' + exc_dir + 'EM_Data/ > ' + zspace
        os.system(cmd)
        with open(zspace, 'r') as f:
            test = f.read()
     
        mcf.rm_file(zspace)
    
        mc   = re.search('sto', test)
    
        if mc is not None:
            cmd = 'gzip -d ' + exc_dir + 'EM_Data/*gz'
            os.system(cmd)
    
            cmd = 'ls ' + exc_dir + 'EM_Data/*Dump_EM*sto > ' + zspace
            os.system(cmd)
    
            data = mcf.read_data_file(zspace, remove=1)
        else:
            data = []
    else:
        data = []

    return  data

#---------------------------------------------------------------------------------------
#-- run_arc5gl: extract data from archive using arc5gl                                --
#---------------------------------------------------------------------------------------

def run_arc5gl(start, stop):
    """
    extract data from archive using arc5gl
    input:  start   --- starting time in the format of mm/dd/yy,hh/mm/ss. hh/mm/ss is optional
            stop    --- stoping time
    output: extracted data set
    """
#
#--- write arc5gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset =flight\n'
    line = line + 'detector=telem\n'
    line = line + 'level =raw\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'
#
#--- extract data
#
    out  = mcf.run_arc5gl_process(line)

    return out

#---------------------------------------------------------------------------------------
#-- set_data_period: create a list of dates to be examined                           ---
#---------------------------------------------------------------------------------------

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
        ifile = data_dir + 'tsc_temps.txt'
        data  = mcf.read_data_file(ifile)
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
        if mcf.is_leapyear(dyear):
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

#---------------------------------------------------------------------------------------
 
if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    if os.path.isfile(f"/tmp/mta/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/mta/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/mta/{name}.lock")

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

    extract_tl_data(year, sdate, edate)

#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/mta/{name}.lock")
