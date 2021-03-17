#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#           convert_to_fits.py: converting the trend data into a fits file                              #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               last update: Nov 20, 2014                                                               #
#                                                                                                       #
#########################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
from astropy.io import fits 
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')

#
#--- reading directory list
#
path = '/data/mta/Script/Trending/Recovery/dir_list_py'

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
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- the name of data set that we want to extract
#
name_list = ['gradablk', 'gradaincyl', 'gradfap', 'gradhcone', 'gradhpflex', 'gradocyl', \
             'gradperi', 'gradtfte', 'gradahet',  'gradcap',     'gradfblk',  'gradhhflex',\
             'gradhstrut',  'gradpcolb',  'gradsstrut']


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def run_script(name_list):
    """
    Input:  name_list   --- a list of the name of dataset that we want to extract/update
    Output: updated fits file (e.g. avg_compaciscent.fits)
    """

    for dir in name_list:

        nfile = house_keeping + dir
        f     = open(nfile, 'r')
        data  = [line.strip() for line in f.readlines()]
        f.close()

        col_list = []
        for ent in data:
            atemp = re.split('\s+', ent)
            col_list.append(atemp[0])

#
#---- now creating fits file
#
        convert_to_fits(dir, col_list)


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def convert_to_fits(dir, col_list):

        file = './Results/' + dir
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
#
#--- define column names
#
        col_names =[]
        for ent in col_list:
            aname = ent + '_AVG'
            col_names.append(aname)
            ename = ent + '_DEV'
            col_names.append(ename)


        dlen  = len(col_list)
        dlen2 = 2 * dlen
        time  = []
        data_set = [[] for x in range(0, dlen2)]
        for ent in data:
            atemp = re.split('\t', ent)
            time.append(atemp[0])

            for j in range(1, len(atemp)):
                data_set[j-1].append(atemp[j])

        time  = numpy.array(time)
        col = fits.Column(name='Time', format='D', array=time)
        col_list = [col]

        for j in range(0, dlen2):
            data_set[j] = numpy.array(data_set[j])
            col = fits.Column(name=col_names[j], format='D', array=data_set[j])
            col_list.append(col)

        cols = fits.ColDefs(col_list)
#        tbhdu = fits.BinTableHDU.from_columns(cols)            # --- version 0.42
        tbhdu = fits.new_table(cols)                            # --- versuib 0.30
#
#---- create a bare minimum header
#
        prihdr = fits.Header()
        prihdu = fits.PrimaryHDU(header=prihdr)

        out_name = './Results/avg_' + dir + '.fits'
#
#--- create the fits file
#
        cmd = 'rm ' + out_name
        os.system(cmd)

        thdulist = fits.HDUList([prihdu, tbhdu])
        thdulist.writeto(out_name)


#-----------------------------------------------------------------------

if __name__ == "__main__":

    run_script(name_list)


