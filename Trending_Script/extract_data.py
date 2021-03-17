#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       extract_data.py:    extract data from mp reort and update saved data set        #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Mar 12, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import time
import numpy
from astropy.io import fits  as pyfits
#
#--- reading directory list
#
path = '/data/mta/Script/Trending/house_keeping/dir_list_py'

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
#--- import several functions
#
import mta_common_functions       as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- the name of data set that we want to extract
#--- (compephinkey removed Oct 9, 2018)
#
name_list = ['compaciscent', 'compacispwr', 'compgradkodak', \
             'compsimoffset', 'gradablk', 'gradahet', 'gradaincyl', 'gradcap',    \
             'gradfap', 'gradfblk', 'gradhcone', 'gradhhflex', 'gradhpflex',      \
             'gradhstrut', 'gradocyl', 'gradpcolb', 'gradperi', 'gradsstrut',     \
             'gradtfte']

#--------------------------------------------------------------------------------
#-- extract_data: extract the new data and update the data sets                --
#--------------------------------------------------------------------------------

def extract_data(name_list):
    """
    extract the new data and update the data sets.
    Input:  name_list   --- a list of the name of dataset that we want to extract/update
    Output: updated fits file (e.g. avg_compaciscent.fits)
    """

    for idir in name_list:

        fits_name = data_dir + 'avg_' + idir + '.fits'
#
#--- find the last logged dom date
#
        try:
            lent      = find_last_entry_time(fits_name)
        except:
            cmd = 'cp ' + fits_name + '~ ' + fits_name
            os.system(cmd)
            try:
                lent      = find_last_entry_time(fits_name)
            except:
                print(fits_name)
                continue
#
#--- find available fits data from <mp_dir>
#
        cmd  = 'ls ' + mp_dir + '/*/' + idir + '/data/*_summ.fits > ' +  zspace
        os.system(cmd)

        mp_data = mcf.read_data_file(zspace, remove=1)
    
        for ent in mp_data:
#
#--- find dom date
#
            dom = find_dom_from_mp_file(ent)
    
            if dom <= lent:
                continue
#
#--- now open fits file and get data
#
            else:
                cdict         = {}
                cdict['time'] = dom
    
                dout       = pyfits.getdata(ent, 1)
                cname_list = dout.field('name')
                avg_list   = dout.field('average')
                err_list   = dout.field('error')
     
                for k in range(0, len(cname_list)):
                    cname = cname_list[k].lower()
                    aname = cname + '_avg'
                    ename = cname + '_dev'
                    cdict[aname] = avg_list[k]
                    cdict[ename] = err_list[k]
     
                append_data(fits_name, cdict)


#--------------------------------------------------------------------------------
#-- find_dom_from_mp_file: find dom date from the direoctry path name         ---
#--------------------------------------------------------------------------------

def find_dom_from_mp_file(ent):
    """
    find dom date from the direoctry path name
    input:  ent --- full path to the file <mp_dir>/<date>/...
    output: dom --- day of mission
    """

    atemp = re.split(mp_dir, ent)
    btemp = atemp[1].replace('/', '')
    year  = btemp[0] + btemp[1] + btemp[2] + btemp[3]
    month = btemp[4] + btemp[5]
    day   = btemp[6] + btemp[7]
    year  = int(float(year))
    month = int(float(month))
    day   = int(float(day))
 
    line  = str(year) + ':' + mcf.add_leading_zero(month) + ':' +  mcf.add_leading_zero(day)
    ydate = int(time.strftime('%j', time.strptime(line, '%Y:%m:%d')))
    dom   = mcf.ydate_to_dom(year, ydate)

    return dom

#--------------------------------------------------------------------------------
#-- find_last_entry_time: find the last logged dom date                        --
#--------------------------------------------------------------------------------

def find_last_entry_time(fits):
    """
    find the last logged dom date
    """
    fdat = pyfits.open(fits)
    data = fdat[1].data
    lent = data[-1][0]

    return lent

#--------------------------------------------------------------------------------
#-- append_data: append new data row into the fits file                        --
#--------------------------------------------------------------------------------

def append_data(orig_fits, cdict):
    """
    append new data row into the fits file
    input:  orig_fits   --- fits file name
            cdict       --- dictionary of data: col name <---> value
    output: orig_fits   --- updated fits file
    """
#
#--- open the original fits file 
#
    fdat = pyfits.open(orig_fits)
    row  = fdat[1].data.shape[0]
#
#--- expand the data table to accomodate the new data. assume that only one new row of data
#
    nrow = row + 1
    hdu  = pyfits.BinTableHDU.from_columns(fdat[1].columns, nrows=nrow)
#
#--- add each data row
#
    for colname in fdat[1].columns.names:
        try:
            val = cdict[colname.lower()]
        except:
            val = -99.0

        hdu.data[colname][row:] = val
#
#--- write out the data
#
    mcf.rm_files('./ztemp,fits')
    hdu.writeto('./ztemp.fits')
#
#--- check whether data are added correctly, before move 
#--- the temp fits file to the original fits file
#
    chk  = pyfits.open('ztemp.fits')
    cnt  = chk[1].data.shape[0]
    if cnt >= nrow:
        cmd = 'mv -f ' +  orig_fits + ' ' + orig_fits +'~'
        os.system(cmd)
        cmd = 'mv -f ztemp.fits ' + orig_fits
        os.system(cmd)
    else:
        mcf.rm_file('./ztemp,fits')


#-----------------------------------------------------------------------

if __name__ == "__main__":

    extract_data(name_list)


