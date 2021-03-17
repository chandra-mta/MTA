#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#          recover_suppl_functions.py: supplmental collections of functions             # 
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Apr 04, 2017                                               #
#                                                                                       #
#########################################################################################

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

mon_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------

def change_colnames(fits, colnames,  outfile=''):

    t = pyfits.open(fits)
    for k in range(0, len(colnames)):
        t[1].columns[k].name = colnames[k]

    if outfile== '':
        outfile = fits

    t.writeto(outfile)

    t.close()

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------

def change_data_format(fits, dformat, col_format, outfile=''):
    """
    change a table data fits file data format
    input:  fits    --- fits file name
            dformat --- data format you want to use, e.g. float, int, double
                        don't use "" around it.
            col_format  --- indicator of the fits file data foramt see: create_fits_file()
            outfile     --- output fits file name: default: "" and write over on fits
    output: outfile
    """

    ff = pyfits.open(fits)
    data = ff[1].data
    cname = ff[1].columns.names

    save  = []
    for k in range(0, len(cnames)):
        out = numpy.array(ff[1].data[cname[k]].astype(dformat))
        cc  = pyfits.Column(name=cname[k], format=col_format, array=out)
        save.append(cc)

    coldefs = pyfits.ColDefs(save)
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)

    if outfile == '':
        outfile == fits

    mcf.rm_file(outfile)
    tbhdu.writeto(outfile)



#------------------------------------------------------------------------------------------
#-- create_fits_file: create a new table fits file                                      ---
#------------------------------------------------------------------------------------------

def create_fits_file(col_list, format_list, data_list, outfile):
    """
    create a new table fits file
    input:  col_list    ---  a list of column names
            format_list ---  a list of format specifications
            data_list   ---  a list of data
            outfile     ---  output fits file name
    output: outfile     --- output fits file

            FITS format code         Description                     8-bit bytes
            
            L                        logical (Boolean)               1
            X                        bit                             *
            B                        Unsigned byte                   1
            I                        16-bit integer                  2
            J                        32-bit integer                  4
            K                        64-bit integer                  4
            A                        character                       1
            E                        single precision floating point 4
            D                        double precision floating point 8
            C                        single precision complex        8
            M                        double precision complex        16
            P                        array descriptor                8
            Q                        array descriptor                16
    """

    ent_list = []
    for k in range(0, len(col_list)):
        acol = pyfits.Column(name=col_list[k], format=format_list[k], array=numpy.array(data_list[k]))
        ent_list.append(acol)

    coldefs = pyfits.ColDefs(ent_list)
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)

    tbhdu.writeto(outfile)

#------------------------------------------------------------------------------------------
#-- update_fits_date_span: update header date according to a data part of fits file      --
#------------------------------------------------------------------------------------------

def update_fits_date_span(fits):
    """
    update header date according to a data part of fits file
            it is assumed that the time is in seconds from 1998.1.1
    input:  fits    --- table fits file
    output: fits    --- updated fits file
    """

    tt    = pyfits.open(fits)
    atime = tt.data[1].time
    amin  = min(atime)
    amax  = max(atime)
    btime = sectime_to_caldate(amin)
    etime = sectime_to_caldate(amax)

    ctime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gtime())

    head  = tt[0].header
    head['TSTART']   = amin
    head['TSTOP']    = amax
    head['DATE']     = ctime
    head['DATE-OBS'] = btime
    head['DATE-END'] = etime

    tt[0].header = head

    tt.writeto(fits)

    tt.close()


#------------------------------------------------------------------------------------------
#-- sectime_to_caldate: convert seconds from 1998.1.1 to <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> format 
#------------------------------------------------------------------------------------------

def sectime_to_caldate(time):
    """
    convert seconds from 1998.1.1 to <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> format
    input:  time    --- time in seconds from 1998.1.1
    output: ndate   --- date in <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
    """

    date  = Chandra.Time.DateTime(time)
    out   = date.cladate
    year  = str(out[0:4])
    mon   = str(out[4:7])
    for k in range(0, mon_list):
        if mon == mon_list[k]:
            mon = k + 1
            break
    lmon = str(mon)
    if mon < 10:
        lmon + '0' + lmon

    day   = str(out[7:9])
    atemp = re.split('\s+', date)
    time  = atemp[2]

    ndate = year + '-' + lmon + '-' + day + 'T' + time

    return ndate


#------------------------------------------------------------------------------------------
#-- quickChandra_time: axTime3 replacement                                             ----
#------------------------------------------------------------------------------------------

def quickChandra_time(ent):
    """
    axTime3 replacement
    input:  ent --- either seconds from 1998.1.1 or date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    output: out --- either seconds from 1998.1.1 or date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    """

    if mcf.chkNumeric(ent):
        out = Chandra.Time.DateTime(float(ent)).date
    else:
        out = Chandra.Time.DateTime(str(ent)).secs

    return out

#------------------------------------------------------------------------------------------
#-- fetch_eng_data: get eng data from archieve                                           --
#------------------------------------------------------------------------------------------

def fetch_eng_data(msid_list, start, stop):
    """
    get eng data from archieve
    input:  msid_list   --- a list of msids
            start       --- start time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop        --- stop time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    output: results     --- a list of lists of data extracted including time at beginning
    """

    results = []
    chk = 0
    for msid in msid_list:
        out = fetch.MSID(msid, start, stop)

        if chk == 0:
            time = list(out.times)
            results.append(time)
            chk = 1

        data = list(out.vals)
        results.append(data)

    return results


#------------------------------------------------------------------------------------------

if __name__ == "__main__":

    #fits1 = 'compgradkodak_upto2016.fits'
    #fits2 = 'compgradkodak.fits'
    #outfile = 'test_out.fits'
    #fits_append(fits1, fits2, outfile=outfile)

    msid_list = ['OHRTHR02', 'OHRTHR03']
    start     = '2017:001:00:00:00'
    stop      = '2017:002:00:00:00'
    data = fetch_eng_data(msid_list, start, stop)





