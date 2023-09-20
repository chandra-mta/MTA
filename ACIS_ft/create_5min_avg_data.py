#!/proj/sot/ska3/flight/bin/python

#####################################################################################################
#                                                                                                   #
#           create_5min_avg_data.py: create five min average data file                              #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Mar 03, 2021                                                               #
#                                                                                                   #
#####################################################################################################

import sys
import os
import numpy
import time
import Chandra.Time
import Ska.engarchive.fetch as fetch
import getpass
#
#--- Directory list
#
DATA_DIR = '/data/mta/Script/ACIS/Focal/Data/'
OUT_DATA_DIR = DATA_DIR

#
#
step  = 600.0   #---- 5 min step
hstep = 0.5 * step

#-------------------------------------------------------------------------------
#-- create_5min_avg_data: create data file contains daily max value of focal plane temp 
#-------------------------------------------------------------------------------

def create_5min_avg_data(year=''):
    """
    create data file contains daily max value of focal plane temp 
    input:  year --- default: '' extract data only this year. otherwise start from year 2000 to current
    output: <data_dir>/long_term_max_data format: <ctime>    <max focal temp> <crat> <crbt>
    """
#
#--- find today's date
#
    if year == '':
        stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
        today = Chandra.Time.DateTime(stday).secs
#
#--- find the current year
#
        atemp = stday.split(':')
        year  = int(atemp[0])
#
#--- read data of each year
#
    dfile = f"{DATA_DIR}full_focal_plane_data_{year}"

    with open(dfile,'r') as f:
        data = [line.strip() for line in f.readlines()]

    f_list = []
    a_list = []
    b_list = []
#
#--- set starting interval; the day after the last entry date
#
    start  = set_start(data)
    stop   = start + step
    sline  = ''

    for ent in data:
        if ent == '':
            continue
        atemp = ent.split()
        atime = float(atemp[0])

        focal = float(atemp[1])
        crat  = float(atemp[2])
        crbt  = float(atemp[3])

        if (atime >= start) and (atime < stop):
            f_list.append(focal)
            a_list.append(crat)
            b_list.append(crbt)

        elif atime > stop:
#
#--- if there are data, take averages of data
#
            if len(f_list) > 0:
                afocal = sum(f_list)/len(f_list)
                acrat  = sum(a_list)/len(a_list)
                acrbt  = sum(b_list)/len(b_list)
                mtime  = start + hstep

                sline  = sline + "%d\t%4.3f\t%4.3f\t%4.3f\n" % (mtime, afocal, acrat, acrbt)
            else:
                pass

            f_list = [focal]
            a_list = [crat]
            b_list = [crbt]
            start  = stop
            stop  += step
    
    ofile = OUT_DATA_DIR + '/focal_plane_data_5min_avg_' + str(year)
    with  open(ofile, 'w') as fo:
        fo.write(sline)

#-------------------------------------------------------------------------------
#-- set_start: find the fist day of the data and set to start from hour 00:00:00
#-------------------------------------------------------------------------------

def set_start(data, pos=0, add=0.0):
    """
    find the first day of the data and set to start from hour 00:00:00
    input:  data    --- a list of data; <ctime>:<data1>:<data2>:<data3>
            pos     --- a postion of the element, usually 0 (at beginning)
            add     --- a shifting factor in seconds; default: 0
    output: start   --- a starting time in seconds from 1998.1.1
    """
    atemp  = data[pos].split()
    stday  = float(atemp[0]) + add
    day    = Chandra.Time.DateTime(stday).date
    btemp  = day.split(':')

    start  = btemp[0] + ':' + btemp[1] + ':00:00:00'
    start  = Chandra.Time.DateTime(start).secs

    return start

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
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''
    create_5min_avg_data(year)
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")