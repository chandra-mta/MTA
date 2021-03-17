#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#           update_base_data.py: update .../Short_term/<data_file>                      #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 03, 2021                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import numpy
import getopt
import time
import Chandra.Time
import Ska.engarchive.fetch as fetch
import random
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; setenv ACISTOOLSDIR /home/pgf', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Focal/Script/house_keeping/dir_list'

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

import mta_common_functions     as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------
#-- update_base_data: update acis focal temperature data files                --
#-------------------------------------------------------------------------------

def update_base_data():
    """
    update acis focal temperature data files 
    input: none but read from /dsops/GOT/input/*_Dump_EM_*.gz
    output: <short_term>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
#
#--- read already processed data list
#
    ifile = house_keeping + 'old_list_short'
    olist = mcf.read_data_file(ifile)

    cmd   = 'mv -f ' + ifile + ' ' + ifile + '~'
    os.system(cmd)
#
#--- find the currently available data
#
    cmd   = 'ls /dsops/GOT/input/*_Dump_EM_*.gz > ' + ifile
    os.system(cmd)
    clist = mcf.read_data_file(ifile)
#
#--- find which ones are not processed yet
#
    nlist = numpy.setdiff1d(clist, olist)
#
#--- create new short term data files (usually 3 per day)
#
    plist = extract_data_from_dump(nlist)

#-------------------------------------------------------------------------------
#-- extract_data_from_dump: extract focal data from dump data                 --
#-------------------------------------------------------------------------------

def extract_data_from_dump(nlist, test=0):
    """
    extract focal data from dump data
    input:  nlist   --- a list of new dump data file names
            test    --- for unittest
    output: extracted data: <short_term>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
    plist = []
    for ent in nlist:
        if test == 0:
            nfile = create_out_name(ent)
            plist.append(nfile)
        else:
            nfile = './short_term_test'

        cmd = '/usr/bin/env PERL5LIB= '
        cmd = cmd + 'gzip -dc ' + ent + ' |' + bin_dir + 'getnrt -O $* | '
        cmd = cmd + bin_dir + '/acis_ft_fptemp.pl >> ' +  nfile
        bash(cmd,  env=ascdsenv)

    return plist

#-------------------------------------------------------------------------------
#-- create_out_name: create an output data file name                          --
#-------------------------------------------------------------------------------

def create_out_name(ifile):
    """
    create an output data file name
    input:  ifile   --- dump_em file name
    output: ofile   --- output file name in <short_term>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
    atemp = re.split('\/', ifile)
    btemp = re.split('_Dump', atemp[-1])

    ofile = short_term + 'data_' + btemp[0]

    return ofile

#-------------------------------------------------------------------------------
#-- TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST   TEST -
#-------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#-------------------------------------------------------------------------------
    def test_create_out_name(self):

        ifile = '/dsops/GOT/input/2018_119_2325_120_1206_Dump_EM_76390.gz'
        out   = create_out_name(ifile)
        atemp = re.split('\/', out)
        self.assertEquals(atemp[-1], 'data_2018_119_2325_120_1206')


#-------------------------------------------------------------------------------
    def test_extract_data_from_dump(self):

        cmd = 'ls  /dsops/GOT/input/*Dump_EM*gz > ' + zspace
        os.system(cmd)
        data = mcf.read_data_file(zspace, remove=1)
        nlist = [data[-1],]

        plist = extract_data_from_dump(nlist, test=1)
        
        data  = mcf.read_data_file('./short_term_test', remove=1)

        if len(data) > 0:
            self.assertEquals(1, 1)
        else:
            self.assertEquals(0, 1)
    
#-------------------------------------------------------------------------------
#
#--- if there is any aurgument, it will run normal mode
#

if __name__ == "__main__":

    #unittest.main()
    update_base_data()
