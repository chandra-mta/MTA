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
import string
import re
import numpy
import getopt
import time
import random
import Chandra.Time
import Ska.engarchive.fetch as fetch
import unittest
import getpass
#
#--- reading directory list
#
path = '/data/mta4/testACIS/Focal/Script/house_keeping/dir_list'
#path = '/data/mta/Script/ACIS/Focal/Script/house_keeping/dir_list'

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
sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
step  = 86400   #---- one day step
hstep = 0.5 * step

#-------------------------------------------------------------------------------
#-- create_long_term_max_data: create data file contains daily max value of focal plane temp 
#-------------------------------------------------------------------------------

def create_long_term_max_data(iall=0):
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
    atemp = re.split(':', stday)
    tyear = int(atemp[0])

    ofile =  data_dir + 'long_term_max_data'
#
#--- if all != 0 recompute from beginning
#
    if iall == 0:
        y_list = [tyear,]
        cut    = find_last_entry_date()
        if os.path.isfile(ofile):
            wind = 'a'
        else:
            wind = 'w'
    elif iall == 1:
        y_list = range(2000, tyear+1)
        cut    = 0.0
        wind   = 'w'
    elif iall == 2:
#
#--- unittest options
#
        y_list = range(2000,2001)
        cut = 0
    
    sline = ''
    for year in y_list:
        print("Processing YEAR: " + str(year))
#
#--- read data of each year
#
        dfile = data_dir + '/full_focal_plane_data_' + str(year)
        data  = mcf.read_data_file(dfile)
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
#
#--- if unittest case then return sline
#
    if iall == 2:
        return sline

    with open(ofile, wind) as fo:
        fo.write(sline)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def find_last_entry_date():

    ifile = data_dir + 'long_term_max_data'

    try:
        data  = mcf.read_data_file(ifile)
        start = set_start(data, pos=-1, add=hstep)

    except:
        start = 0

    return start

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
#-- TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST -
#-------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
    def test_set_start(self):
        data = ['800000000    foo', '700012868.184    bar']
        start = set_start(data)
        self.assertEqual(799977669.184,start)
        start = set_start(data,pos=1, add=1)
        self.assertEqual(700012869.184,start)

    def test_create_long_term_max_data(self):
        data = create_long_term_max_data(2)
        data = data.strip().split("\n")
        self.assertEqual('64929664',data[0].split()[0])
        self.assertEqual('-117.770',data[-1].split()[1])
    
    
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
        iall = 1
    else:
        iall = 0

    #unittest.main(exit=False)
    create_long_term_max_data(iall)

#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")