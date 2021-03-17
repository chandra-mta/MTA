#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#   add_new_data_to_compgradkodak.py: add new data after the last update on compgradkoda.fits       #
#                                                                                                   #
#                   author:  t. isobe (tisobe@cfa.harvard.edu)                                      #
#                                                                                                   #
#                   last update: Apr 10, 2017                                                       #
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
sys.path.append('./')

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import create_five_min_avg  as cfma
import create_compgradkodak as ccgk

data_dir = './Data/'

#-----------------------------------------------------------------------------------
#-- add_new_data_to_compgradkodak: add new data after the last update on compgradkoda.fits and compgradkodak_5m_data.fits
#-----------------------------------------------------------------------------------

def add_new_data_to_compgradkodak():
    """
    add new data after the last update on compgradkoda.fits and compgradkodak_5m_data.fits
    input: none but read from compgradkoda.fits and compgradkodak_5m_data.fits
    output: updated compgradkoda.fits and compgradkodak_5m_data.fits
    """
    mslist  = data_dir + 'compgradkodak_input_msid_list'
    infile1 = data_dir + 'compgradkodak_5m_data.fits'
    infile2 = data_dir + 'compgradkodak.fits'

    f       = open(mslist, 'r')
    dlist   = [line.strip() for line in f.readlines()]
    f.close()
#
#--- find the last date of the current dataset
#
    ff    = pyfits.open(infile1)
    atime = ff[1].data['time']
    ff.close()

    ldate      = atime[-1]
    out        = Chandra.Time.DateTime(float(ldate)).date
    atemp      = re.split(':', out)
    start_year = int(float(atemp[0]))
    start_yday = int(float(atemp[1])) + 1
#
#--- check whether the starting date is moved into the "next" year
#
    if tcnv.isLeapYear(start_year) == 1:
        test = 366
    else:
        test = 365

    if start_yday > test:
        start_yday -= test
        start_year += 1
#
#--- find today's date and set the stop day to be one day before
#
    today     = time.strftime("%Y:%j", time.gmtime())
    atemp     = re.split(':', today)
    stop_year = int(float(atemp[0]))
    stop_yday = int(float(atemp[1])) -1
#
#--- check whether the stopping date is in the "last" year
#
    if stop_yday < 1:
        stop_year -= 1
        if tcnv.isLeapYear(stop_year) == 1:
            stop_yday += 366
        else:
            stop_yday += 365
#
#--- create 5 min average data file for the new section
#
    cfma.create_five_min_avg(dlist, start_year, start_yday, stop_year, stop_yday)
#
#--- append the new section to the previous data fits file
#
    fits_append(infile1, 'temp_5min_data.fits', 'temp_out.fits')

    bfile = infile1 + '~'
    cmd = 'mf -f ' + infile1 + ' ' + bfile
    os.system(cmd)

    cmd = 'mv temp_out.fits ' + infile1
    os.system(cmd)
#
#--- compute the daily average and std for the new section
#
    ccgk.create_compgradkodak('temp_5min_data.fits', 'temp_out.fits')
#
#--- append the new section to the previous data fits file
#
    fits_append(infile2, 'temp_out.fits', 'temp_out2.fits')
    
    bfile = infile2 + '~'
    cmd   = 'mv -f ' + infile2 + ' ' + bfile
    os.system(cmd)

    cmd   = 'mv temp_out2.fits ' + infile2
    os.system(cmd)

    mcf.rm_file('temp_out.fits')
    mcf.rm_file('temp_5min_data.fits')


#------------------------------------------------------------------------------------------
#-- fits_append: append one fits file to another                                         --
#------------------------------------------------------------------------------------------

def fits_append(fits1, fits2, outfile=''):
    """
    append one fits file to another. they must have the same columns
    input:  fits1   --- the first fits file
            fits2   --- the fits to be appended to fits1
            outfile --- outputfits file name
    output: outfile
    """

    t1 = pyfits.open(fits1)
    t2 = pyfits.open(fits2)

    nrows1 = t1[1].data.shape[0]
    nrows2 = t2[1].data.shape[0]
    nrows  = nrows1 + nrows2
    hdu    = pyfits.BinTableHDU.from_columns(t1[1].columns, nrows=nrows)
    for colname in t1[1].columns.names:
        hdu.data[colname][nrows1:] = t2[1].data[colname]

    if outfile == '':
        outfile = fits1

    hdu.writeto(outfile)
    t1.close()
    t2.close()

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    add_new_data_to_compgradkodak()

