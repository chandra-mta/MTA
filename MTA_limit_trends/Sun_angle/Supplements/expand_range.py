#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: May 20, 2019                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
import unittest
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts3.83.6/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def fix_range():

    infile = house_keeping + 'msid_list_sun_angle'
    data   = mcf.read_data_file(infile)

    line = ''

    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        group = atemp[1]
        low   = atemp[2]
        top   = atemp[3]
        [low, top] = adjust(low, top)

        if len(msid)  < 8:
            msid  = msid + '\t'
        if len(group) < 8:
            group = group + '\t'

        line = line +  msid + '\t' + group + '\t' + low + '\t' + top + '\t0.011\n'

    fo     = open('./msid_list_sun_angle', 'w')
        fo.write(line)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def adjust(low, top):

    low = float(low)
    top = float(top)
    if low < 1.0:
        return [str(low), str(top)]

    else:
        diff = top - low
        if diff < 5:
            low -= 0.1
            top += 0.2
            return [str(low) , str(top)]
        else:
            low = str(int(low)) + '.0'
            top = str(int(top) + 2) + '.0'
            return [low, top]


#--------------------------------------------------------------------------------------

if __name__ == '__main__':

    fix_range()




