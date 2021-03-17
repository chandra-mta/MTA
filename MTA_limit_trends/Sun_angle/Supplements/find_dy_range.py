#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: May 20, 2019                                       #
#                                                                           #
#############################################################################

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

def find_dy_range():

    msid_list = house_keeping + 'msid_list_sun_angle'
    data      = mcf.read_data_file(msid_list)
    
    line = ''
    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        group = atemp[1]

        fits  = data_dir + group.capitalize() + '/' + msid + '_data.fits'
        fout  = pyfits.open(fits)
        fdata = fout[1].data
        dout  = fdata[msid]
        bot   = numpy.percentile(dout, 2)
        top   = numpy.percentile(dout, 98)
        diff  = top - bot
        ratio = diff / 120.0
        if ratio < 1:
            ratio  = round(ratio, 2)
            ratio *= 2
        else:
            ratio  = round(ratio, 0)
            ratio *= 3

        if ratio < 0.2:
            ratio = 0.2

        btemp = re.split('0.011', ent)

        line = line  + btemp[0] + '\t0.011\t' + str(ratio) + '\n'

    fo        = open('msid_list_sun_angle', 'w')
        fo.write(line)

#-------------------------------------------------------------------------------------

if __name__ == '__main__':

    find_dy_range()



