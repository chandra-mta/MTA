#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#           run_iru_gyro_bias.py: update iru gyro bias database                     #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last updae: Mar 12, 2021                                            #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import math
import numpy
import time
import astropy.io.fits  as pyfits
import Chandra.Time
import Ska.engarchive.fetch as fetch
import random
#
#--- reading directory list
#
path = '/data/mta/Script/IRU/Scripts/house_keeping/dir_list'

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
#--- import functions
#
import mta_common_functions       as mcf        
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
bias_list = ['aogbias1', 'aogbias2', 'aogbias3']

#----------------------------------------------------------------------------------
#-- run_iru_gyro_bias: update iru gyro bias database                             --
#----------------------------------------------------------------------------------

def run_iru_gyro_bias(tstart, tstop):
    """
    update iru gyro bias database
    input:  tstart  --- starting time
            tstop   --- stopping time
    output: <data_dir>/iru_gyro_bias_year<year>.fits
    """
    if tstart == '':
        [y_list, b_list, e_list] = find_start_and_stop_time()
        for k in range(0, len(y_list)):
            year   = y_list[k]
            tstart = b_list[k]
            tstop  = e_list[k]
            append_new_data(year, tstart, tstop)
            
    else:
        date  = Chandra.Time.DateTime(0.5*(tstart + tstop)).date
        atemp = re.split(':', date)
        year  = int(atemp[0])

        append_new_data(year, tstart, tstop)

#----------------------------------------------------------------------------------
#-- append_new_data: append the new data potion to the existing database         --
#----------------------------------------------------------------------------------

def append_new_data(year, tstart, tstop):
    """
    append the new data potion to the existing database
    input:  year    --- this year
            tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: <data_dir>/iru_gyro_bias_year<year>.fits
    """
#
#--- read the input data fits file
#
    out = read_data(tstart, tstop)
#
#--- compute avg and std of roll, pitch, and yaw biases; default is one hour avg/std
#
    results =  compute_avg(out)
#
#--- convert the table into fits file
#
    create_new_data_fits(results)

    mfile = data_dir + 'iru_gyro_bias_year' + str(year) + '.fits'
#
#--- if the fits data file exists, append. otherwise, create it
#
    if os.path.isfile(mfile):
        append_fits_table(mfile, 'bias.fits', 'temp.fits')

        cmd = 'mv temp.fits ' + mfile
        os.system(cmd)

        mcf.rm_file('bias.fits')
    else:
        cmd = 'mv bias.fits ' + mfile
        os.system(cmd)

#----------------------------------------------------------------------------------
#-- find_start_and_stop_time: find starting and stopping time from the existing data 
#----------------------------------------------------------------------------------

def find_start_and_stop_time():
    """
    find starting and stopping time from the existing data
    input:   none but read from <data_dir>/iru_gyro_bias_year<year>.fits
    output: a list of year
            a list of starting time in seconds from 1998.1.1
            a list of stopping time in seconds from 1998.1.1

            Note, most of the time the lists contain only one value. However
            in some occasion, the data span goes over the end/beginning of years
            and get two entries.
    """
#
#--- check today's date
#
    date  = time.strftime("%Y:%j:00:00:00", time.gmtime())
    atemp = re.split(':', date)
    year  = int(atemp[0])
#
#--- check the file exists
#
    dfile = data_dir + 'iru_gyro_bias_year' + str(year) + '.fits'

    if os.path.isfile(dfile):
        fout  = pyfits.open(dfile)
        data  = fout[1].data
        dtime = data['time']
        dlast = dtime[-1]
        fout.close()

        tend  = Chandra.Time.DateTime(date).secs

        return [[year], [dlast], [tend]]
#
#--- if not check the last year
#
    else:
        dfile2 = data_dir + 'iru_gyro_bias_year' + str(year-1) + '.fits'
        if os.path.isfile(dfile2):
            fout   = pyfits.open(dfile2)
            data   = fout[1].data
            dlast  = data['time'][-1]
            fout.close()

            ybound = str(year) + ':001:00:00:00'
            stime  = Chandra.Time.DateTime(ybound).secs
            etime  = Chandra.Time.DateTime(date).secs

            return [[year-1, year], [dlast, stime], [stime, etime]]

        else:
#
#--- start from begining
#
            return [[1999], [48902399.0], [63071999.0]]

#----------------------------------------------------------------------------------
#-- read_data: extract needed data from sot database                             --
#----------------------------------------------------------------------------------

def read_data(tstart, tstop):
    """
    extract needed data from sot database
    input:  tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: data    --- a list of arrays of data
    """
    save = []
    for msid in bias_list:

        out = fetch.MSID(msid, tstart, tstop)
        val = out.vals
        save.append(val)
    
    data = [out.times] + save

    return data

#----------------------------------------------------------------------------------
#-- compute_avg: compute avg and std of given data                               --
#----------------------------------------------------------------------------------

def compute_avg(data, span=3600.0):
    """
    compute avg and std of given data
    input:  data    --- a list of data arrays
            span    --- time span of which you want to compute avg/std; default: 3600
    output: out     --- a list of arrays of the data
    """
    c_len = len(data)
#
#--- assume that the first array is time in seconds
#
    dtime = data[0]
    start = dtime[0]
    tend  = dtime[-1]
    stop  = start + span

    aout  = []
    for k in range(0, c_len*2):
        aout.append([])
#
#--- take avg and std of span interval of data
#
    while start < tend:
        index = (dtime >= start) & (dtime < stop)
        m = 0
        for k in range(0, c_len):
            select = data[k][index]
            avg    = numpy.mean(select)
            std    = numpy.std(select)
            aout[m].append(avg)
            m += 1
            aout[m].append(std)
            m += 1

        start = stop
        stop  = start + span
#
#--- convert the lists into arrays
#
    out = []
    for ent in aout:
        out.append(numpy.array(ent))

    return out

#----------------------------------------------------------------------------------
#-- create_new_data_fits: create a new fits file                                ---
#----------------------------------------------------------------------------------

def create_new_data_fits(data, out='bias.fits'):
    """
    create a new fits file
    input:  data    --- a list of arrays of data
                        [time (avg/std), roll (avg/std), pitch (avg/std), yaw (avg/std)
            out     --- output fits file name; defalut: bias.fits
    output: out     --- fits file
    """
#
#--- skip time 'std'
#
    col1  = pyfits.Column(name='time',           format='E', array=data[0])
    col2  = pyfits.Column(name='roll_bias_avg',  format='E', array=data[2])
    col3  = pyfits.Column(name='roll_bias_std',  format='E', array=data[3])
    col4  = pyfits.Column(name='pitch_bias_avg', format='E', array=data[4])
    col5  = pyfits.Column(name='pitch_bias_std', format='E', array=data[5])
    col6  = pyfits.Column(name='yaw_bias_avg',   format='E', array=data[6])
    col7  = pyfits.Column(name='yaw_bias_std',   format='E', array=data[7])

    cols  = pyfits.ColDefs([col1, col2, col3, col4, col5, col6, col7])
    
    tbhdu = pyfits.BinTableHDU.from_columns(cols)

    tbhdu.writeto(out)

#----------------------------------------------------------------------------------
#-- append_fits_table: Appending one table fits file to the another              --
#----------------------------------------------------------------------------------

def append_fits_table(file1, file2, outname, extension = 1):

    """
    Appending one table fits file to the another
    the output table will inherit column attributes of the first fits table
    Input:  file1   --- fits table
    file2   --- fits table (will be appended to file1)
    outname --- the name of the new fits file
    Output: a new fits file "outname"
    """
    t1 = pyfits.open(file1)
    t2 = pyfits.open(file2)
#
#-- find numbers of rows (two different ways as examples here)
#
    nrow1 = t1[extension].data.shape[0]
    nrow2 = t2[extension].header['naxis2']
#
#--- total numbers of rows to be created
#
    nrows = nrow1 + nrow2
    hdu   = pyfits.BinTableHDU.from_columns(t1[extension].columns, nrows=nrows)
#
#--- append by the field names
#
    for name in t1[extension].columns.names:
        hdu.data.field(name)[nrow1:] = t2[extension].data.field(name)
#
#--- write new fits data file
#
    hdu.writeto(outname)
    
    t1.close()
    t2.close()

#----------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- tstart an tstop are in seconds from 1998.1.1
#
    if len(sys.argv) == 3:
        tstart = float(sys.argv[1])
        tstop  = float(sys.argv[2])
    else:
        tstart = ''
        tstop  = ''

    run_iru_gyro_bias(tstart, tstop)

#    for year in range(1999, 2018):
#        if year == 1999:
#            date1 = "1999:244:00:00:00"
#        else:
#            date1 = str(year) + ':001:00:00:00'
#
#        date2 = str(year+1) + ':001:00:00:00'
#        
#        tstart = Chandra.Time.DateTime(date1).secs
#        tstop  = Chandra.Time.DateTime(date2).secs
#
#        print("Running: " + str(date1) + '<-->' + str(date2))
#
#        run_iru_gyro_bias(tstart, tstop)
