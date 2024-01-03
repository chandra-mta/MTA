#!/proj/sot/ska3/flight/bin/python

#####################@###############################################################################
#                                                                                                   #
#       create_long_term_max_data.py: create data file contains daily max value of focal plane temp #
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
import re
#
#--- Directory list
#
DATA_DIR = '/data/mta/Script/ACIS/Focal/Data/'
OUT_DATA_DIR = DATA_DIR

step  = 86400   #---- one day step
hstep = 0.5 * step

#-------------------------------------------------------------------------------
#-- create_long_term_max_data: create data file contains daily max value of focal plane temp 
#-------------------------------------------------------------------------------

def create_long_term_max_data(year=''):
    """
    create data file contains daily max value of focal plane temp 
    input:  all --- default: 0 extract data only this year. otherwise start from year 2000 to current
    output: <data_dir>/long_term_max_data format: <ctime>    <max focal temp> <crat> <crbt>
    """
#
#--- find today's date
#
    stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    today = Chandra.Time.DateTime(stday).secs
#
#--- find the current year
#
    atemp = stday.split(':')
    tyear = int(atemp[0])

    ofile =  OUT_DATA_DIR + 'long_term_max_data'
#
#--- if year == '' then compute from the last time entry
#
    if year == '':
        ifile = f"{DATA_DIR}long_term_max_data"
        try:
            with open(ifile,'r') as f:
                data = [line.strip() for line in f.readlines()]
            cut = set_start(data, pos=-1, add=hstep)
        except:
            cut = 0
        syear = int(Chandra.Time.DateTime(cut).date.split(":")[0])
        y_list = [x for x in range(syear,tyear)]
        y_list = list(set(y_list)-set([1997,1998,1999]))
        wind = 'a'
    else:
        y_list = [int(year)]
        cut    = 0.0
        wind = 'w'

    sline = ''
    for year in y_list:
        print("Processing YEAR: " + str(year))
#
#--- read data of each year
#
        dfile = f"{DATA_DIR}full_focal_plane_data_{year}"
        with open(dfile,'r') as f:
            data = [line.strip() for line in f.readlines()]
#
#--- set starting interval; the day after the last entry date
#
        start  = set_start(data)
        if cut > 0:
            start = cut

        stop   = start + step

        f_list = []
        a_list = []
        b_list = []
        for ent in data:
            try:
                atemp = re.split('\s+', ent)
                atime = float(atemp[0])
            except:
                continue

            if atime < cut:
                continue

            focal = float(atemp[1])
            crat  = float(atemp[2])
            crbt  = float(atemp[3])

            if (atime >= start) and (atime < stop):
                f_list.append(focal)
                a_list.append(crat)
                b_list.append(crbt)

            elif atime > stop:
#
#--- if there are data, find the warmest focal temp spot, and print out the data
#
                if len(f_list) > 0:
                    f_array = numpy.array(f_list)
                    mpos    = f_array.argmax(axis=0)
                    mtime   = start + hstep
                    sline   = sline +  "%d\t%4.3f\t%4.3f\t%4.3f\n" \
                                        % (mtime, f_list[mpos], a_list[mpos], b_list[mpos])

                else:
                    pass

                f_list = [focal]
                a_list = [crat]
                b_list = [crbt]
                start  = stop
                stop  += step

    with open(ofile, wind) as fo:
        fo.write(sline)

#-------------------------------------------------------------------------------
#-- set_start: find the fist day of the data and set to start from hour 00:00:00
#-------------------------------------------------------------------------------

def set_start(data, pos=0, add=0.0):
    """
    find the fist day of the data and set to start from hour 00:00:00
    input:  data    --- a list of data; <ctime>:<data1>:<data2>:<data3>
            pos     --- a postion of the element, usually 0 (at beginning)
            add     --- a shifting facotr in seconds; default: 0
    output: start   --- a starting time in seconds from 1998.1.1
    """
    atemp  = re.split('\s+', data[pos])
    stday  = float(atemp[0]) + add
    day    = Chandra.Time.DateTime(stday).date
    btemp  = re.split(':', day)

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
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

    create_long_term_max_data()

#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")