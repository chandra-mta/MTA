#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################
#                                                                               #
#   update_top_gratings_html_page.py:  update gratings page index page          #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Apr 03, 2018                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import datetime

bin_dir       = '/data/mta4/Gratings/Script/'
house_keeping = '/data/mta4/Gratings/Script/house_keeping/'
mta_dir       = '/data/mta/Script/Python_script2.7/'
dat_dir       = '/data/mta/MTA/data/'

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import get_obslist          as gobs


rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------
#-- update_top_gratings_html_page: update gratings page index page                   --
#--------------------------------------------------------------------------------------

def update_top_gratings_html_page():
    """
    update gratings page index page
    input:  none
    output: /data/mta_www/mta_grat/index.html
    """

    infile = '/data/mta_www/mta_grat/Focus/index.html'
    f      = open(infile, 'r')
    data   = [line.strip() for line in f.readlines()]
    f.close()

    vals   = []
    for ent in data:
        mc = re.search('00DDFF', ent)
        if mc is not None:
            atemp = re.split('00DDFF>', ent)
            btemp = re.split('<', atemp[1])
            vals.append(btemp[0].strip())


    infile = house_keeping + 'top_index_template'
    f      = open(infile, 'r')
    text   = f.read()
    f.close()

    text   = text.replace('#VAL1#', vals[0])
    text   = text.replace('#VAL2#', vals[1])
    text   = text.replace('#VAL3#', vals[2])
    text   = text.replace('#VAL4#', vals[3])
    text   = text.replace('#VAL5#', vals[4])
    text   = text.replace('#VAL6#', vals[5])

    fo     = open('/data/mta_www/mta_grat/index.html', 'w')
    fo.write(text)
    fo.close()

#--------------------------------------------------------------------------------------

if __name__ == "__main__":
    update_top_gratings_html_page()
