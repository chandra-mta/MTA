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

def find_range(msid_list):

    mfile = house_keeping  + msid_list
    data  = mcf.read_data_file(mfile)

    sline = ''
    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        mc    = re.search('#', msid)
        if mc is not None:
            continue

        group = atemp[1]

        fits  = data_dir + group + '/' + msid + '_data.fits'

        try:
            f     = pyfits.open(fits)
            fdata = f[1].data
            f.close()
        except:
            continue

        vals  = fdata[msid]

        blim  = numpy.percentile(vals, 1)
        tlim  = numpy.percentile(vals, 99)

        if blim == tlim:
            vmin = blim
            vmax = tlim

            blim = min(vals)
            tlim = max(vals)
            if blim == tlim:
                vmin = blim
                vmax = tlim
        else:
            selc  = [(vals > blim) & (vals < tlim)]
    
            svals = vals[selc]
            if len(svals) > 0:
                vmin  = min(svals)
                vmax  = max(svals)
            else:
                vmin  = min(vals)
                vmax  = max(vals)
    
        if vmin == vmax:
            vmin -= 1
            vmax += 1

        if len(msid) < 8:
            msid = msid + '\t'

        if len(group)< 8:
            tgroup = group + '\t'
        else:
            tgroup = group

        if abs(vmin) > 10:
            line  = msid + '\t' + tgroup + '\t' + '%3.1f' % (round(vmin, 1)) + '\t'
            line  = line + '%3.1f' % (round(vmax, 1)) + '\t0.011\n'
        elif abs(vmin) > 1:
            line  = msid + '\t' + tgroup + '\t' + '%3.2f' % (round(vmin, 2)) + '\t'
            line  = line + '%3.2f' % (round(vmax, 2)) + '\t0.011\n'
        else:
            line  = msid + '\t' + tgroup + '\t' + '%2.4f' % (round(vmin, 4)) + '\t'
            line  = line + '%2.4f' % (round(vmax, 4)) + '\t0.011\n'

        sline = sline + line
    
    with open('out', 'w') as fo:
        fo.write(line)
    fo.close()

#--------------------------------------------------------------------------------------

if __name__ == '__main__':

    msid_list = sys.argv[1]

    find_range(msid_list)




