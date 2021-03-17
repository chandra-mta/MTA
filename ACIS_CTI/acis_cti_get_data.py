#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#       acis_cti_get_data.py: extract acis evt1 files which are not processed for CTI observations  #
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    Mar 02, 2021                                                            #
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
import time
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf    #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

working_dir = exc_dir + '/Working_dir/'

#---------------------------------------------------------------------------------------------------
#-- acis_cti_get_data: extract acis evt1 files which are not processed for CTI observations       --
#---------------------------------------------------------------------------------------------------

def acis_cti_get_data():
    """
    extract acis evt1 files which are not processed for CTI observations
    Input:  none, but read from directory: /data/mta/www/mp_reports/photons/acis/cti/*
    Output: <working_dir>/acisf<obsid>*evt1.fits
    """
#
#--- get a new data list
#
    obsid_list = find_new_entry()
#
#--- if there is no new data, just exit
#
    if len(obsid_list) > 0:
#
#--- create a temporary saving directory 
#
        cmd = 'rm -rf '   + working_dir
        os.system(cmd)
        cmd = 'mkdir -p ' + working_dir
        os.system(cmd)
#    
#--- extract acis evt1 file
#
        line = ''
        for obsid in obsid_list:
            line = line + obsid + '\n'
            cnt  = 0
            chk  = extract_acis_evt1(obsid)
            if chk != 'na':
                cnt += 1
                cmd = 'mv *'+ str(obsid) + '*.fits.gz ' + working_dir
                os.system(cmd)
    
        outdir = working_dir + '/new_entry'     #---- new_entry list will be used later
        with open(outdir, 'w') as fo:
            fo.write(line)

        if cnt > 0:
            cmd = 'gzip -d ' + working_dir + '*.gz'
            os.system(cmd)
    else:
        exit(1)

#---------------------------------------------------------------------------------------------------
#-- extract_acis_evt1: extract acis evt1 file                                                     --
#---------------------------------------------------------------------------------------------------

def extract_acis_evt1(obsid):
    """
    extract acis evt1 file 
    Input: obsid    --- obsid of the data
    Output: acisf<obsid>*evt1.fits.gz
            file name if the data is extracted. if not ''
    """
#
#--- write  required arc5gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'version=last\n'
    line = line + 'filetype=evt1\n'
    line = line + 'obsid=' + str(obsid) + '\n'
    line = line + 'go\n'
    with open(zspace, 'w') as f:
        f.write(line)
#
#--- run arc5gl
#
    try:
        cmd = ' /proj/sot/ska/bin/arc5gl -user isobe -script ' + zspace
        os.system(cmd)
    except:
        cmd  = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ' + zspace
        os.system(cmd)

    mcf.rm_files(zspace)
#
#--- check the data is actually extracted
#
    cmd  = 'ls * > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    data_out = []
    for ent in data:
        m = re.search(str(obsid), ent)
        if m is not None:
            data_out.append(ent)
#
#--- if multiple evt1 files are extracted, don't use it, but keep the record of them 
#
    if len(data_out) > 1:
        cmd  = 'rm -f *'+ str(obsid) + '*evt1.fits.gz '
        os.system(cmd)

        ifile = house_keeping + '/keep_entry'
        with open(ifile, 'a') as f:
            f.write(obsid)
            f.write('\n')
     
        return 'na'
    elif len(data_out) == 1:
#
#--- normal case, only one file extracted
#
        mcf.rm_files(zspace)
        line = data_out[0]
        return line
    else:
#
#--- no file is extracted
#
        return 'na'

#---------------------------------------------------------------------------------------------------
#-- find_new_entry: create a list of obsids which have not processed yet                         ---
#---------------------------------------------------------------------------------------------------

def find_new_entry():
    """
    create a list of obsids which have not processed yet
    Input: none, but read from /data/mta/www/mp_reports/photons/acis/cti/*
    Output: obsid_list  --- a list of obsids
    """
#
#--- find currently available data
#
    cmd  = "ls -td /data/mta/www/mp_reports/photons/acis/cti/*_* > " + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    current_obsids = []
    for ent in data:
        m = re.search("\d\d\d\d\d_\d", ent)
        if m is not None:
            atemp = re.split('\/', ent)
            btemp = re.split('_', atemp[-1])
            current_obsids.append(btemp[0])
#
#--- probably we need only the most recent 20 of them
#
            current_obsids = current_obsids[0:20]
#
#--- read the past entry list
#
    pobsid_list = []
    for ccd in range(0, 10):
        cfile = data_dir + 'Results/ti_ccd' + str(ccd)
        data  = mcf.read_data_file(cfile)

        for ent in data:
            atemp = re.split('\s+', ent)
            pobsid_list.append(int(atemp[5]))

    old_list = list(set(pobsid_list))
#
#--- create a list of data which have not been processed
#
    new_list   =  list(numpy.setdiff1d(current_obsids, old_list))

    if len(new_list) > 0:
#
#--- excluded obsids in an exclude list
#
        ifile  = house_keeping + 'exclude_obsid_list'
        exfile = mcf.read_data_file(ifile)
        
        obsid_list = list(numpy.setdiff1d(new_list, exfile))
    else:
        obsid_list = []

    return obsid_list

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_extract_acis_evt1(self):

        obsid = 52675
        extract_acis_evt1(obsid)
        cmd = 'ls *fits.gz > ' + zspace
        os.system(cmd)
        data = mcf.read_data_file(zspace, remove=1)

        chk = 0
        for ent in data:
            atemp = re.split('acisf', ent)
            btemp = re.split('_', atemp[1])
            if btemp[0] == str(obsid):
                chk = 1
                break

        self.assertEquals(chk, 1)

#------------------------------------------------------------

    def test_find_new_entry(self):    

        try:
            obsid_list = find_new_entry()
            chk = 1
        except:
            chk = 0

        self.assertEquals(chk, 1)

#--------------------------------------------------------------------

if __name__ == '__main__':

    acis_cti_get_data()

