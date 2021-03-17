#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#               create_five_min_avg.py: create 5 min averaged data for given msid lists             #
#                                                                                                   #
#                   author:  t. isobe (tisobe@cfa.harvard.edu)                                      #
#                                                                                                   #
#                   last update: Apr 07, 2017                                                       #
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

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#-----------------------------------------------------------------------------------
#-- create_five_min_avg: creates a table fits file with 5 min averaged values for msids 
#-----------------------------------------------------------------------------------

def create_five_min_avg(msid_list, start_year, start_yday, stop_year='', stop_yday=''):
    """
    creates a table fits file with 5 min averaged values for msids
    input:  msid_list   --- a list of msids
            start_year  --- a start year int value
            start_yday  --- a start yday int value
            stop_year   --- a stop year int value; default:"" if that is the case, it will use yesterday
            stop_yday   --- a stop yday int value; default:"" if that is the case, it will use yesterday
    output: "temp_5min_data.fits"   --- a table fits file
    """
#
#--- setting start and stop time for the data extraction
#
    lstart_yday = str(start_yday)
    if start_yday < 10:
        lstart_yday = '00' + str(int(start_yday))
    elif start_yday < 100:
        lstart_yday = '0' + str(int(start_yday))

    start_date = str(start_year) + ':' + lstart_yday + ':00:00:00'
    start      = Chandra.Time.DateTime(start_date).secs

    if stop_year == '' or stop_yday == '':
        stop_date  = time.strftime("%Y:%j:00:00:00", time.gmtime())
        stop_year  = int(float(time.strftime("%Y", time.gmtime())))
        stop_yday  = int(float(time.strftime("%j", time.gmtime()))) - 1 #---- trying to make sure that there are data
        stop       = Chandra.Time.DateTime(stop_date).secs
    else:
        lstop_yday = str(stop_yday)
        if stop_yday < 10:
            lstop_yday = '00' + str(int(stop_yday))
        elif stop_yday < 100:
            lstop_yday = '0' + str(int(stop_yday))

        stop_date = str(start_year) + ':' + lstop_yday + ':00:00:00'
        stop      = Chandra.Time.DateTime(stop_date).secs
#
#--- data extracton starts here
#
    cdata = []
    for ent in msid_list:

        ent  = ent.upper()

        #print "MSID: " + str(ent)

        msid = ent.replace('_AVG', '')
#
#--- removing the leading "_"
#
        if msid[0] == '_':
            msid = str(msid[1:])

        [atime, data] = fetch_eng_data(msid, start, stop)
        cdata.append(data)

    outfile = 'temp_5min_data.fits'
    write_fits(msid_list, atime, cdata, outfile)


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def fetch_eng_data(msid, start, stop):
    """
    get eng data from archieve
    input:  msid            --- msid
            start           --- start time in sec from 1998.1.1
            stop            --- stop time in  sec from 1988.1.1
    output: [time, data]    --- a list of time array and data array
    """
#
#--- read data from database
#
    out = fetch.MSID(msid, start, stop)
#
#--- collect data in 5 min intervals and take an average
#
    stime = []
    data  = []
    tsave = []
    pstart = start
    pstop  = pstart + 300.0
    for k in range(0, len(out.times)):

        if out.times[k] < pstart:
            continue
#
#--- collected data for the last 5 mins
#
        elif out.times[k] > pstop:
            stime.append(pstart+150.0)
#
#--- if no data, just put 0.0
#
            if len(tsave) == 0:
                data.append(0.0)
#
#--- take an avearge 
#
            else:
                data.append(numpy.mean(tsave))
                tsave = []
            pstart = pstop
            pstop  = pstart + 300.0

        else:
            tsave.append(out.vals[k])
#
#--- convert the list into an array form before returning
#
    atime = numpy.array(stime)
    adata = numpy.array(data)


    return [atime, adata]


#-----------------------------------------------------------------------------------
#-- write_fits: write table fits file out                                        ---
#-----------------------------------------------------------------------------------

def write_fits(col_list, time_list,  data_list, outfile="",  format_list=''):
    """
    write table fits file out
    input:  col_list    --- msid name list. don't include time
            time_list   --- a list of time vlaues
            data_list   --- a list of lists of msid data
            outfile     --- output file name. optional. if it is not given, 'temp_comp.fits is used
            format_list --- a list of format. optional. if it is not given "E" is used for all
    """

    if format_list == '':
        format_list = []
        for k in range(0, len(col_list)):
            format_list.append('E')
#
#--- add time
#
    acol = pyfits.Column(name='TIME', format='E', array=numpy.array(time_list))
    ent_list = [acol]
#
#--- rest of the data
#
    for k in range(0, len(col_list)):
        acol = pyfits.Column(name=col_list[k], format=format_list[k], array=numpy.array(data_list[k]))
        ent_list.append(acol)

    coldefs = pyfits.ColDefs(ent_list)
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)

    if outfile == "":
        outfile = "./temp_comp.fits"

    mcf.rm_file(outfile)

    tbhdu.writeto(outfile)


#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    clen = len(sys.argv)
    if clen != 4 or clen != 6:
        print "Input: <input file name> <start year> <start yday> <stop year(optional)> <stop yday (optional)>"

    else:
        infile = sys.argv[1]
        infile.strip()
        f = open(infile, 'r')
        dlist = [line.strip() for line in f.readlines()]
        f.close()
        start_year = int(float(sys.argv[2]))
        start_yday = int(float(sys.argv[3]))
        if clen > 4:
            stop_year = int(float(sys.argv[4]))
            stop_yday = int(float(sys.argv[5]))
        else:
            stop_year = ''
            stop_yday = ''

    create_five_min_avg(dlist, start_year, start_yday, stop_year, stop_yday)


