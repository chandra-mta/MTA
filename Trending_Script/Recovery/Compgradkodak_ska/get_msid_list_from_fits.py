#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#           get_msid_list_from_fits.py: extract msids from a given fits file                        #
#                                                                                                   #
#                   author:  t. isobe (tisobe@cfa.harvard.edu)                                      #
#                                                                                                   #
#                   last update: Apr 07, 2017                                                       #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits

import Chandra.Time
import Ska.engarchive.fetch as fetch

#
#--- add the path to mta python code directory
#
sys.path.append('/data/mta/Script/Python_script2.7/')

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#-----------------------------------------------------------------------------------
#-- get_msid_list: extract msid lists from a fits file                            --
#-----------------------------------------------------------------------------------

def get_msid_list_from_fits(fits):
    """
    extract msid lists from a fits file
    input:  fits    --- fits file name
    output: <fits head>_msid_list   --- a list of msids
    """

    ff = pyfits.open(fits)
    col_list = ff[1].columns.names
    ff.close()

    mc       = re.search('gz', fits)
    if mc is not None:
        fits = fits.replace('.gz', '')

    outfile = fits.replace('.fits', '_msid_list')
    mc      = re.search('\/', outfile)
    if mc is not None:
        atemp = re.split('\/', outfile)
        outfile = atemp[-1]

    fo = open(outfile, 'w')
    for ent in col_list:
#
#--- skip TIME column. keep only msids
#
        if ent.upper() == 'TIME':
            continue

        fo.write(ent)
        fo.write('\n')

    fo.close()

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        fits = sys.argv[1]
        fits.strip()
        get_msid_list_from_fits(fits)
    else:
        print "Please provide, fits file name (with full path)"

