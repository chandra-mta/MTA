#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#   create_aggragate_data_sets.py: create aggragated data sets              #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           Last Update: Mar 02, 2021                                       #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import operator
import math
import numpy
import time
import random                   #--- random must be called after pylab

path = '/data/mta/Script/ACIS/Count_rate/house_keeping/dir_list_py'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import libraries
#
import mta_common_functions       as mcf 
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

m_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

#----------------------------------------------------------------------------------
#-- create_aggragate_data_sets: create aggragate data sets                       --
#----------------------------------------------------------------------------------

def create_aggragate_data_sets(chk = 1):
    """
    create aggragate data sets
    input: chk  --- whether start from beginning (=1) or just the last month (=0)
    output: <data_dir>/full_data_ccd<ccd#>.dat
            <data_dir>/month_avg_data_ccd<ccd#>.dat
    """
    out = time.strftime('%Y:%m', time.gmtime())
    atemp = re.split(':', out)
    year  = int(float(atemp[0]))
    mon   = int(float(atemp[1]))

    if chk == 0:
        lyear = year
        lmon  = mon -1
        if lmon < 1:
            lmon   = 12
            lyear -= 1
        get_data(lyear, lmon)

    else:
        cmd = 'rm -rf ' + data_dir + '*ccd*.dat'
        os.system(cmd)

        for ryear in range(1999, year+1):
            for rmon in range(1, 13):
                if (ryear == 1999) and (rmon < 8):
                    continue
                if (ryear == year) and (rmon > mon-1):
                    break
                get_data(ryear, rmon)

#----------------------------------------------------------------------------------
#-- get_data: create aggragate data sets for the given month/year                --
#----------------------------------------------------------------------------------

def get_data(year, mon):
    """
    create aggragate data sets for the given month/year
    input:  year    --- year of the data
            mon     --- month of the data
    output: <data_dir>/full_data_ccd<ccd#>.dat
            <data_dir>/month_avg_data_ccd<ccd#>.dat
    """
    for ccd in range(0, 10):
        ifile = data_dir + m_list[mon-1] + str(year) + '/ccd' + str(ccd)
        data  = mcf.read_data_file(ifile)
        xdata = []
        sum1  = 0
        sum2  = 0
        line  = ''
    
        for ent in data:
            atemp = re.split('\s+', ent)
            y     = float(atemp[1])
            if (y == 0) or (y > 500000):
                continue
            else:
                val = int(float(y) / 300.0)
                if val == 0:
                    continue
                line = line + atemp[0] + '\t' + str(val) + '\n'
                xdata.append(float(atemp[0]))
                sum1 += y
                sum2 += y * y

        tot = len(xdata)
        if tot == 0:
            continue

        tavg = numpy.mean(xdata)
        avg = sum1 / tot / 300.0
        try:
            sig = math.sqrt(sum2 / tot / 90000.0 - avg * avg)
        except:
            sig = 0.0

        mline = '%d\t%d\t%2.2f\n' % ( tavg, avg, sig)
        out   = data_dir + 'month_avg_data_ccd' + str(ccd) + '.dat'
        with open(out, 'a') as fo:
            fo.write(mline)

        out   = data_dir + 'full_data_ccd' + str(ccd) + '.dat'
        with open(out, 'a') as fo:
            fo.write(line)


#----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        chk = int(float(sys.argv[1]))
    else:
        chk = 1

    create_aggragate_data_sets(chk)

