#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       update_monitor_data.py: update aca monitor related data files                       #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 22, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import random
import Chandra.Time
import numpy
import astropy.io.fits  as pyfits

#
#--- reading directory list
#
path = '/data/mta/Script/ACA/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

#
#--- append a path to a private folder to python directory
#
sys.path.append(mta_dir)

import mta_common_functions as mcf
#
#--- temp writing file name
#
rfname = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rfname)


gss_cols  = ['good', 'marginal', 'bad', 'type', 'name', 'rms_ra_err', 'rms_dec_err', 'rms_delta_mag',\
             'number', 'avg_angynea', 'avg_angznea', 'number_nea',  'mta_status']
perr_cols = ['time', 'pos_err_0', 'pos_err_1', 'pos_err_2', 'pos_err_3', 'pos_err_4', \
             'pos_err_5', 'pos_err_6', 'pos_err_7']
mag_cols  = ['time', 'diff_0', 'diff_1', 'diff_2', 'diff_3', 'diff_4', 'diff_5', 'diff_6', 'diff_7']
ang_cols  = ['time', 'angynea_0', 'angynea_1', 'angynea_2', 'angynea_3', 'angynea_4', 
             'angynea_5', 'angynea_6', 'angynea_7', 'angznea_0', 'angznea_1', 'angznea_2', 
             'angznea_3', 'angznea_4', 'angznea_5', 'angznea_6', 'angznea_7']

outfile_list = ['guide_gsst', 'fid_gsst', 'monitor_gsst', 'pos_err_mtatr', 'diff_mtatr', 'acacent_mtatr']
col_list     = [gss_cols, gss_cols, gss_cols, perr_cols, mag_cols, ang_cols]


#-----------------------------------------------------------------------------------
#-- update_monitor_data: update aca monitor related data files                    --
#-----------------------------------------------------------------------------------

def update_monitor_data(year, month):
    """
    update aca monitor related data files
    input:  year    --- year
            month   --- month
    output: <data_dir>/<data file> (see outfile_list)
    """
#
#--- if the data is not given, use this month, except the first 4days; use the last month
#
    if year == '':
        out = time.strftime('%Y:%m:%d', time.gmtime())
        atemp = re.split(':', out)
        year  = int(float(atemp[0]))
        month = int(float(atemp[1]))
        mday  = int(float(atemp[2]))
        if mday < 5:
            month -= 1
            if month < 1:
                year -= 1
                month = 12
#
#--- update files
#
    for k in range(3, len(outfile_list)):
        fname = outfile_list[k]
        cols  = col_list[k]
        ofile = data_dir + fname
        extract_monitor_data(year, month, fname, cols, ofile)
#
#--- clean up the file
#
        clean_up_file(ofile)

#-----------------------------------------------------------------------------------
#-- extract_monitor_data: extract monitor data from fits files                    --
#-----------------------------------------------------------------------------------

def extract_monitor_data(year, month, fname, cols, ofile):
    """
    extract monitor data from fits files
    input:  year    --- year
            month   --- month
            fname   --- none-variable part of fits file name
            cols    --- a list of column names
            ofile   --- output file name
    """
#
#--- find the last entry time (seconds from 1998.1.1)
#
    if os.path.isfile(ofile):
        odata = mcf.read_data_file(ofile)
        if len(odata) > 0:
            atemp = re.split('\s+', odata[-1])
            cut   = float(atemp[0])
        else:
            cut   = 0.0
    else:
        cut   = 0.0

    lyear = str(year)
    ddir  = data_dir + 'Fits_data/' + mcf.change_month_format(month).upper() 
    ddir  = ddir     + lyear[2] + lyear[3] + '/'
#
#--- data is a list of lists of column data
#
    data  = read_fits_data(ddir, fname, cols)

    if data:
        line = ''
#
#--- make sure that the data extracted will be after "cut" date
#
        dlen   = len(data[0])
        kstart = dlen
        for k in range(0, dlen):
            if data[0][k] > cut:
                kstart = k
                break
        if kstart == dlen:
            dlen = 0

        if dlen > 0:
            for k in range(kstart, dlen):
                for m in range(0, len(cols)):
                    if cols[m] == 'time':
                        line = line + '%d\t' % data[m][k]
                    else:
                        line = line + '%2.3e\t' % data[m][k]
                line = line + '\n'

            with open(ofile, 'a') as fo:
                fo.write(line)
                 
#-----------------------------------------------------------------------------------
#-- read_fits_data: read fits data                                                --
#-----------------------------------------------------------------------------------

def read_fits_data(ddir, fname, cols):
    """
    read fits data
    input:  ddir    --- the directory name where the fits file located
            fname   --- none_variable fits name part
            cols    --- a list of column names
    output: save    --- a list of arrays of data
    """
#
#--- find the fits file name
#
    cmd  = 'ls ' + ddir + '*_' + fname + '.fits* > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    if len(data) > 0:
        fits = data[0].strip()
    else:
        return False
#
#--- if the file exists, read the data
#
    try:
        fout  = pyfits.open(fits)
        fdata = fout[1].data
        fout.close()
    except:
        return False

    save  = []
    for col in cols:
        odata = fdata[col]
        save.append(odata)

    return save

#-----------------------------------------------------------------------------------
#-- clean_up_file: sort, the data and remove duplicate                            --
#-----------------------------------------------------------------------------------

def clean_up_file(ifile, col=0):
    """
    sort, the data and remove duplicate. if duplcated, a newer data is used
    input:  ifile   --- input file name with full path
            col     --- col # to be used for sorting
    output: ifile   --- cleaned up data file
    """
    t_list = []
    s_dict = {}
    data   = mcf.read_data_file(ifile)
    for ent in data:
        atemp = re.split('\s+', ent)
        tval  = float(atemp[col])
        t_list.append(tval)
        s_dict[tval] = ent

    tset   = set(t_list)
    t_list = sorted(list(tset))

    line   = ""
    for tval in t_list:
        line = line + s_dict[tval] + '\n'

    with open(ifile, 'w') as fo:
        fo.write(line)


#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv)  > 1:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
    else:
        year  = ''
        month = ''

    update_monitor_data(year, month)

#    for year in range(1999, 2021):
#        for month in range(1, 13):
#            if year == 1999 and month < 8:
#                continue
#            if year == 2020 and month > 3:
#                break
#
#            update_monitor_data(year, month)
#
