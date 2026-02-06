#!/proj/sot/ska3/flight/bin/python
"""
**create_full_focal_plane_data.py**: Create/update full resolution focal plane data files.

:Author: W. Aaron (william.aaron@cfa.harvad.edu)
:Last Updated: Feb 05, 2026

# /// testing
# tested-ska-release = "2026.1"
# ///
"""

import sys
import os
import Chandra.Time
from cxotime import CxoTime
import Ska.engarchive.fetch as fetch
import getpass
import json
import glob
import math
#
#--- Define Directory Paths
#
DATA_DIR = '/data/mta/Script/ACIS/Focal/Data'
HOUSE_KEEPING = '/data/mta/Script/ACIS/Focal/Script/house_keeping'
SHORT_TERM = '/data/mta/Script/ACIS/Focal/Short_term'

def _fraction_day(frac):
    frac = float(frac)
    hh = math.floor(frac // 3600)
    mm = math.floor((frac % 3600) // 60)
    ss = math.floor(frac % 60)
    return hh,mm,ss

def _translate_custom_datetime(year, time):
    parts = time.split(":")
    hh, mm, ss = _fraction_day(parts[1])
    return CxoTime(f"{int(year):04}:{int(parts[0]):03}:{hh:02}:{mm:02}:{ss:02}")

def read_short_term(filename):
    parts = filename.split('_')
    _year = int(parts[1])
    year_change = parts[3] > parts[5] #: Change in year.
    _path = f"{SHORT_TERM}/{filename}"
    #: Column 1 is an undocumented representation of the OBC telemetry bytes indicating point in time
    #: Column 4 is an undocumented representation of some other temperature.
    table = ascii.read(_path, names= ('col1', 'custom_datetime', 'focal_plane_temp', 'col4'))
    cxocolumn = []
    if year_change:
        idx = 0
        while table['custom_datetime'][idx][:3] != "001":
            idx += 1

        for timepoint in table['custom_datetime'][:idx]:
            cxocolumn.append(_translate_custom_datetime(_year,timepoint))
        for timepoint in table['custom_datetime'][idx:]:
            cxocolumn.append(_translate_custom_datetime(_year+1,timepoint))
    else:
        for timepoint in table['custom_datetime']:
            cxocolumn.append(_translate_custom_datetime(_year,timepoint))
    table.add_column(cxocolumn, name = 'cxotime')
    return table['cxotime', 'focal_plane_temp']

def create_full_focal_plane_data():
    """
    create/update full resolution focal plane data
    input:   none, but read from <short_term>/data_*
    output: <data_dir>/full_focal_plane_data
    """

    record_file = f"{HOUSE_KEEPING}/processed_short_term_files.json"
    os.system(f"cp -f {record_file} {record_file}~")
    with open(record_file) as f:
        processed_short_term_files = json.load(f)
    
    current_short_term_files = [os.path.basename(_) for _ in glob.glob(f"{SHORT_TERM}/data_*")]
    
    new_file_list = list(set(current_short_term_files).difference(set(processed_short_term_files['data'])))

    #: TODO: Include checks to ensure we don't list a data file as processed
    #: If we're missing 1CRAT and 1CRBT data.
    tables = {}
    for file in new_file_list:

        table = read_short_term(file)

        #
        # --- Add 1CRAT and 1CRBT columns
        #
        tables[file] = table




    for ifile in flist:
        print("INPUT: " + ifile)
#
#---- checking whether the year change occurs in this file
#
        [year, chg] = find_year_change(ifile)
        with open(ifile,'r') as f:
            data = [line.strip() for line in f.readlines()]
#
#---- find the last entry time
#
        outfile = DATA_DIR + 'full_focal_plane_data_' + str(year)
        if schk == 0:
            try:
                with open(outfile,'r') as f:
                    ldata = [line.strip() for line in f.readlines()]
                ltemp = ldata[-1].split()
                start = int(float(ltemp[0]))
            except:
                start   = 0
            schk = 1
#
#--- select unique data
#
        tdict       = {}
        for ent in data:
            atemp = ent.split()
            if len(atemp) < 4:
                continue

            try:
                tdict[atemp[0]] = [atemp[1], atemp[2]]
            except:
                continue

        temp1 = []
        temp2 = []
        for key in tdict.keys():
            [val1, val2] = tdict[key]
#
#--- convert time into Chandra time (time is coming in, e.g.: 142:43394.950000 format)
#
            try:
                ctime = ptime_to_ctime(year, val1, chg)
            except:
                continue

            if ctime < start:
                continue

            temp1.append(ctime)
            temp2.append(float(val2))

        if len(temp1) == 0:
            continue
#
#--- sorting lists with time order
#
        temp1, temp2 = zip(*sorted(zip(temp1, temp2)))
        temp1 = list(temp1)
        temp2 = list(temp2)
#
#--- keep the last entry to mark the starting point to the next round
#
        start = temp1[-1]
#
#--- find cold plate temperatures
#
        [crat, crbt] = find_cold_plates(temp1)
#
#--- prep for data print out
#
        sline = ' ' 
        for k in range(0, len(temp1)):
#
#---- if the focal temp is warmer than -20C or colder than -273, something wrong with the data: drop it
#
            if temp2[k] > -20:
                continue
            elif temp2[k] < -273:
                continue
            elif crat[k] == 999.0:
                continue

            tline = "%d\t%4.3f\t%4.3f\t%4.3f" % (temp1[k], temp2[k], crat[k], crbt[k])
            tline = tline.replace('\s+', '')
            if tline == '':
                continue 
            else:        
                sline = sline + tline + '\n'

        if sline == '':
            continue

#
#--- write the data out
#
        if os.path.isfile(outfile):
            wind = 'a'
            os.system(f"cp {outfile} {outfile}~")
        else:
            wind = 'w'

        with open(outfile, wind) as fo:
            fo.write(sline)

        cmd = 'chmod 774 ' + outfile
        os.system(cmd)
        cmd = 'chgrp mtagroup ' + outfile
        os.system(cmd)

#-------------------------------------------------------------------------------
#-- find_cold_plates: create cold plate temperature data lists corresponding to the given time list
#-------------------------------------------------------------------------------

def find_cold_plates(t_list):
    """
    create cold plate temperature data lists corresponding to the given time list
    input:  t_list  --- a list of time
    output: crat    --- a list of temperature of plate A
            crbt    --- a list of temperature of plate B
    """
#
#--- set data time interval
#
    start = t_list[0]
    stop  = t_list[-1]
#
#--- cold plate A
#
    out   = fetch.MSID('1crat', start, stop)
    tlist = out.times
    alist = out.vals
#
#--- cold plate B
#
    out   = fetch.MSID('1crbt', start, stop)
    blist = out.vals
#
#--- make sure that data have the same numbers of entries
#
    alen  = len(alist)
    blen  = len(blist)
    if alen < blen:
        blist = blist[:alen]
    elif alen > blen:
        for k in range(blen, alen):
            blist.append(blist[-1])
#
#--- find the cold plate temperatures correpond to the given time
#
    crat = []
    crbt = []
    for tent in t_list:
#
#-- take +/- 10 seconds 
#
        begin = tent - 30
        end   = tent + 30

        m     = 0
        chk   = 0
        for k in range(m, alen):
            if (tlist[k] >= begin) and (tlist[k] <= end):
                crat.append(float(alist[k]) - 273.15)
                crbt.append(float(blist[k]) - 273.15)
                m = k - 10
                if m < 0:
                    m = 0
                chk = 1
                break
        if chk == 0:
            crat.append(999.0)
            crbt.append(999.0)

    return [crat, crbt]

#-------------------------------------------------------------------------------
#-- find_year_change: find year of the data and whether the year change occures in this file
#-------------------------------------------------------------------------------

def find_year_change(ifile):
    """
    find year of the data and whether the year change occures in this file
    input:  ifile   --- input file name
                        assume that the ifile has a form of : .../Short_term/data_2017_365_2059_001_0241"
    output: year    --- year of the data
            chk     --- whether the year change occures in this file; 1: yes/ 0: no
    """
    btemp = ifile.split('/')[-1].split('_')
    year  = int(float(btemp[1]))

    day1  = int(float(btemp[2]))
    day2  = int(float(btemp[4]))
    if day2 < day1:
        chk = 1
    else: 
        chk = 0

    return [year, chk]

#-------------------------------------------------------------------------------
#-- ptime_to_ctime: convert focal plate time to chandra time                  --
#-------------------------------------------------------------------------------

def ptime_to_ctime(year, atime, chg):
    """
    convert focal plate time to chandra time
    input:  year    --- year of the data
            atime   --- data time in focal data time format:.e.g., 115:1677.850000
            chg     --- indicator that telling that year is changed (if 1)
    output: ctime   --- time in seconds from 1998.1.1
    """
    btemp = atime.split(':')
    day   = int(float(btemp[0]))
#
#--- the year changed during this data; so change the year to the next year
#
    if chg > 0:
        if day == 1:
            year += 1

    fday  = float(btemp[1])
    
    fday /= 86400.0
    tmp   = fday * 24.0
    hh    = int(tmp)
    tmp   = (tmp - hh) * 60.0
    mm    = int(tmp)
    ss    = int((tmp - mm) * 60.0)
    
#
#--- add leading zeros
#

    day = str(day).zfill(3)
    hh = str(hh).zfill(2)
    mm = str(mm).zfill(2)
    ss = str(ss).zfill(2)

    yday = f'{year}:{day}:{hh}:{mm}:{ss}'
    try:
        ctime = Chandra.Time.DateTime(yday).secs
    except:
        ctime = 999.0
    
    return ctime


#-------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

    create_full_focal_plane_data()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")