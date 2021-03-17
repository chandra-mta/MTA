#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       acis_cti_run_script.py: a master script to run all cti data extraction/manupulation scripts #
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    Sep 11, 2014                                                            #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts

import acis_cti_get_data          as gdata
import create_cti_data_table      as cdt
import clean_table                as clean
import cti_detrend_factor         as det
import create_adjusted_cti_tables as adj
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- a couple of things needed
#
dare   = mcf.get_val('.dare',   dir = bin_data, lst=1)
hakama = mcf.get_val('.hakama', dir = bin_data, lst=1)

working_dir = exc_dir + '/Working_dir/'

#---------------------------------------------------------------------------------------------------
#-- acis_cti_run_script: a master script to run all cti data extraction/manupulation scripts     ---
#---------------------------------------------------------------------------------------------------

def acis_cti_run_script():
    """
    this is a master script to run all cti data extraction/manupulation scripts
    input:  none
    output: resulting cti tables save in /data/mta/Scripts/ACIS/CTI/Data/
    """
#
#--- extract acis evt1 files which are not processed for CTI observations
#
    gdata.acis_cti_get_data()
#
#--- extract cti values from data and create cti data tables 
#
    cdt.create_cti_table()
#
#--- sort and cleaned data tables in <data_dir>/Results
#
    clean.clean_table()
#
#--- create detrended cti tables
#
    det.cti_detrend_factor()
#
#--- create adjusted cti data and print out the results
#
    adj.update_cti_tables()

#--------------------------------------------------------------------

if __name__ == '__main__':

    acis_cti_run_script()

