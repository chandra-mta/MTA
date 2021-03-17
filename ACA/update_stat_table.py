#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#        update_stat_table.py: update magnitude related stat table data files               #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 23, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import random
import Chandra.Time
import numpy

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
import robust_linear        as rlf
#
#--- temp writing file name
#
rfname  = int(time.time() * random.random())
zspace  = '/tmp/zspace' + str(rfname)
oneyear = 86400.0 * 365.0

#----------------------------------------------------------------------------------
#--  update_stat_table: update magnitude related stat table data files           --
#----------------------------------------------------------------------------------

def update_stat_table(this_year='', this_mon=''):
    """
    update magnitude related stat table data files
    input: none, but read from: 
                acis_<#>, hrc_i_<#>, hrc_s_<#>  for full range average
                mag_i_avg_<#>                   all others
    output: monthly_mag_stats   --- monthly stats
            yearly_mag_stats    --- yearly stats
            recent_mag_stats    --- most recent one year
            full_mag_stats      --- entire period
            stats are fitted linear slope and std of the data
    """
#
#--- find the current year and month
#
    if this_year == '':
        out       = time.strftime('%Y:%m:%d', time.gmtime())
        atemp     = re.split(':', out)
        this_year = int(float(atemp[0]))
        this_mon  = int(float(atemp[1]))
        this_day  = int(float(atemp[2]))
        if this_day < 5:
            this_mon -= 1
            if this_mon < 1:
                this_mon   = 12
                this_year -= 1
#
#--- initialize lists for monthly and yearly data saving
#
    mtime  = []
    mslope = []
    mstd   = []
    ytime  = []
    yslope = []
    ystd   = []
#
#--- there are 14 entries, named mag_i_avg_1... the first slot won't be used
#
    for k in range(0, 15):
        yslope.append([])
        ystd.append([])
        mslope.append([])
        mstd.append([])
#
#--- initialize for recent one year stats saving
#
    rslope = ''
    rstd   = ''
#
#--- go through each data set
#
    for k in range(1, 15):
        ifile    = data_dir + 'mag_i_avg_' + str(k)
        [t_array, d_array] = read_in_data(ifile)
#
#--- recent one year
#
        if len(t_array) > 2:
            r_cut        = t_array[-1] - oneyear
            [slope, std] = get_slope_and_str(t_array, d_array, r_cut, t_array[-1])
            rslope       = rslope +  slope + '\t'
            rstd         = rstd   +  std   + '\t'
        else:
            rslope       = rslope + 'na\t'
            rstd         = rstd   + 'na\t'
#
#--- yearly
#
        for year in range(1999, this_year + 1):
            if k == 1:
                ytime.append(str(year))
            start    = int(Chandra.Time.DateTime(str(year)   + ':001:00:00:00').secs)
            stop     = int(Chandra.Time.DateTime(str(year+1) + ':001:00:00:00').secs)

            if len(t_array) > 2:
                [slope, std] = get_slope_and_str(t_array, d_array, start, stop)
            else:
                [slope, std] = ['nan', 'nan']

            yslope[k].append(slope)
            ystd[k].append(std)
#
#--- monthly
#
        for year in range(1999, this_year + 1):
            for month in range(1, 13):
                if year == 1999 and month < 8:
                    continue
                if year == this_year and month > this_mon:
                    break
                if k == 1:
                    mtime.append(str(year) + ':' +  mcf.add_leading_zero(month))

                nyear    = year
                nmonth   = month + 1
                if nmonth > 12:
                    nmonth = 1
                    nyear += 1

                start    = convert_mday_to_stime(year,  month,  1)
                stop     = convert_mday_to_stime(nyear, nmonth, 1)

                if len(t_array) > 2:
                    [slope, std] = get_slope_and_str(t_array, d_array, start, stop)
                else:
                    [slope, std] = ['nan', 'nan']

                mslope[k].append(slope)
                mstd[k].append(std)
#
#--- now update the data files
#
#
#--- most recent one year 
#
    line = rslope +  rstd + '\n'
    rout = data_dir + 'recent_mag_stats'
    with open(rout, 'w') as fo:
        fo.write(line)
#
#--- yearly 
#
    line = ''
    for k in range(0, len(ytime)):
        line = line + ytime[k] + '\t'
        for m in range(1, 15):
            line = line + yslope[m][k] + '\t'
        for m in range(1, 15):
            line = line + ystd[m][k]   + '\t'
        line = line + '\n'
    
    yout = data_dir + 'yearly_mag_stats'
    with open(yout, 'w') as fo:
        fo.write(line)
#
#--- monthly
#
    line = ''
    for k in range(0, len(mtime)):
        line = line + mtime[k] + '\t'
        for m in range(1, 15):
            line = line + mslope[m][k] + '\t'
        for m in range(1, 15):
            line = line + mstd[m][k]   + '\t'
        line = line + '\n'
    
    mout = data_dir + 'monthly_mag_stats'
    with open(mout, 'w') as fo:
        fo.write(line)
#
#--- full range stats computation uses different data sets which are already averaged on each month
#--- first create data file list
#
    dfile_list = []
    for i in range(1, 7):
        ifile = data_dir + 'acis_' + str(i)
        dfile_list.append(ifile)

    for i in range(1, 5):
        ifile = data_dir + 'hrc_i_' + str(i)
        dfile_list.append(ifile)
    
    for i in range(1, 5):
        ifile = data_dir + 'hrc_s_' + str(i)
        dfile_list.append(ifile)
    
    slp_line = ''
    std_line = ''
    for ifile in dfile_list:
        [t_array, d_array] = read_in_data(ifile, col=2)
#
#--- convert time into fractional year, then convert year 1999 origin
#
        if len(t_array) > 3:
            t_array  = convert_stime_to_fyear_list(t_array)
            t_array  = t_array - 1999
    
            out      = rlf.least_sq(t_array, d_array)
            std      = numpy.std(d_array)
            slp_line = slp_line + '%2.3e\t' % out[1]
            std_line = std_line + '%2.3e\t' %std
        else:
            slp_line = slp_line + '-999\t'
            slp_line = std_line + '-999\t'

    line = slp_line + std_line + '\n'
    fout = data_dir + 'full_mag_stats'
    with open(fout, 'w') as fo:
        fo.write(line)


#----------------------------------------------------------------------------------
#-- read_in_data: read the data and return the cleaned up arrays of time and data -
#----------------------------------------------------------------------------------

def read_in_data(ifile, col=1):
    """
    read the data and return the cleaned up arrays of time and data
    input:  ifile   --- a file name
            col     --- a column position of the data set; default: 1
                        we assume that the first column (0) is time in seconds from 1998.1.1
    output: t_array --- an array of time
            d-array --- an array of data
    """
    data     = mcf.read_data_file(ifile)
    if len(data) < 1:
        return [[],[]]

    data_set = mcf.separate_data_to_arrays(data)
    t_array  = numpy.array(data_set[0])
    d_array  = numpy.array(data_set[col])
#
#--- get rid of nan data points
#
    idx      = ~numpy.isnan(d_array)
    t_array  = t_array[idx]
    d_array  = d_array[idx]
#
#--- get rind of bad data (usually -999.0)
#
    idx      = d_array > -10 
    t_array  = t_array[idx]
    d_array  = d_array[idx]

    return [t_array, d_array]

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def convert_stime_to_fyear_list(dlist):

    save = []
    for ent in dlist:
        fyear = mcf.chandratime_to_fraq_year(ent)
        save.append(fyear)

    save = numpy.array(save)

    return save

#----------------------------------------------------------------------------------
#-- convert_mday_to_stime: convert year, month, mday into Chandra time           --
#----------------------------------------------------------------------------------

def convert_mday_to_stime(year, month, mday):
    """
    convert year, month, mday into Chandra time
    input:  year    --- year
            month   --- month   
            mday    --- day of the monty
    output: ltime   --- time in seconds from 19981.1
    """
    ltime    = str(year) + ':' + mcf.add_leading_zero(month) +  ':' +  mcf.add_leading_zero(mday)
    ltime    = time.strftime('%Y:%j:00:00:00', time.strptime(ltime, '%Y:%m:%d'))
    ltime    = int(Chandra.Time.DateTime(ltime).secs)

    return ltime


#----------------------------------------------------------------------------------
#-- get_slope_and_str: compute fitted slope and std of the data                  --
#----------------------------------------------------------------------------------

def get_slope_and_str(t_array, d_array, start, stop, cind=0):
    """
    compute fitted slope and std of the data
    input:  t_array --- an array of time
            d_datay --- an array of data
            start   --- period starting time in seconds from 1998.1.1
            stop    --- period stopping time in seconds from 1998.1.1
    output: slope   --- slope
            std     --- standard deviation of d_array
    """
#
#--- select data for the given time period
#
    idx     = (t_array >= start) & (t_array < stop)
    t_array = t_array[idx]
    d_array = d_array[idx]
#
#--- compute the stats only when there are more than 3 data points
#
    if len(t_array) > 2:
#
#--- convert to ydate
#
        if cind == 0:
            t_array = convert_to_ydate_list(t_array)
#
#--- convert to fractional year
#
        else:
            t_array = convert_to_fyear_list(t_array)
#
#--- rlf.least_sq reaturn [<intersect>, <slope>, <err of slope>]
#
        out   = rlf.least_sq(t_array, d_array)
        std   = numpy.std(d_array)
        slope = '%2.3e' % out[1]
        std   = '%2.3e' % std
#
#--- otherwise return 'nan'
#
    else:
        slope  = 'nan'
        std    = 'nan'

    return [slope, std]

#----------------------------------------------------------------------------------
#-- convert_to_ydate_list: convert time data in a list from time in seconds to y date
#----------------------------------------------------------------------------------

def convert_to_ydate_list(t_list):
    """
    convert time data in a list from time in seconds to y date
    input:  t_list  --- a list/an array of time data in seconds from 1998.1.1
    output: t_list  --- an array of time data in y date
    """
    save = []

    [byear, ydate] = chandratime_to_yday(t_list[0])

    if mcf.is_leapyear(byear):
        base = 366
    else:
        base = 365

    for ent in t_list:
        [year, ydate] = chandratime_to_yday(ent)
#
#--- if year changes, make it to the extension of the base year
#
        if year > byear:
            ydate += base

        save.append(ydate)

    save = numpy.array(save)

    return save

#--------------------------------------------------------------------------
#-- chandratime_to_yday: convert chandra time into a day of year         --
#--------------------------------------------------------------------------

def chandratime_to_yday(ctime):
    """
    convert chandra time into a day of year
    input:  ctime   --- time in seconds from 1998.1.1
    output: ydate   --- a day of year (fractional)
    """
    
    atime = mcf.convert_date_format(ctime, ofmt='%Y:%j:%H:%M:%S')
    btemp = re.split(':', atime)
    year  = float(btemp[0])
    ydate = float(btemp[1])
    hour  = float(btemp[2])
    mins  = float(btemp[3])
    sec   = float(btemp[4])
    
    ydate  = ydate + (hour/24.0 + mins/1440.0 + sec/86400.0)
    
    
    return  [year, ydate]


#----------------------------------------------------------------------------------
#-- convert_to_fyear_list: convert time data in seconds in a list to fractional year in the list
#----------------------------------------------------------------------------------

def convert_to_fyear_list(t_list):
    """
    convert time data in seconds in a list to fractional year in the list
    input:  t_list  --- a list of time data in seconds from 1998.1.1
    output: t_list  --- an array of time data in fractional year
    """
    save = []
    for ent in t_list:
        save.append(chandratime_to_fraq_year(ent))

    save = numpy.array(save)
    return save

#----------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 3:
        year = int(float(sys.argv[1]))
        mon  = int(float(sys.artv[2]))
    else:
        year = ''
        mon  = ''
    update_stat_table(year, mon)
