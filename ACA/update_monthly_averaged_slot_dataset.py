#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       update_monthly_averaged_slot_dataset.py: update monthly averaged slot data set      #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 23, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import numpy
import time
import Chandra.Time

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


data_list = ['pos_err_mtatr', 'diff_mtatr', 'acacent_mtatr']

#-----------------------------------------------------------------------------------------
#-- update_monthly_averaged_slot_dataset: update monthly averaged slot data set         --
#-----------------------------------------------------------------------------------------

def update_monthly_averaged_slot_dataset(tyear='', tmonth=''):
    """
    update monthly averaged slot data set
    input:  none, but use full slot dataset
    output: monthly averaged slot datasets
    """
#
#--- find today's date
#
    if tyear == '':
        today  = time.strftime('%Y:%m:%d', time.gmtime())
        atemp  = re.split(':', today)
        tyear  = int(float(atemp[0]))
        tmonth = int(float(atemp[1]))
        mday   = int(float(atemp[2]))
        if mday < 5:
            tmonth -= 1
            if tmonth < 1:
                tmonth = 12
                tyear -= 1

    for k in range(0, 3):
        fdname = data_dir + data_list[k]
        mdname = data_dir + data_list[k] + '_month'

        create_monthly_average(fdname, mdname, tyear, tmonth)

#-----------------------------------------------------------------------------------------
#-- create_monthly_average: create monthly averaged dataset from the full data set      --
#-----------------------------------------------------------------------------------------

def create_monthly_average(fdname, mdname, tyear, tmonth): 
    """
    create monthly averaged dataset from the full data set
    input:  fdname  --- a name of full data set
            mdname  --- a name of monthly average data set
            tyear   --- the stopping year of the data collection
            tmonth  --- the stopping month of the data collection
    output: mdname  --- updated monthly averaged data set
    """
#
#--- read full dataset
#
    data     = mcf.read_data_file(fdname)
    data_set = mcf.separate_data_to_arrays(data)

    dlen     = len(data_set)                #--- # of columns in the full data set
    mlen     = dlen + 1                     #--- # of columns in the averaged data set
#
#--- read the monthly averaged data
#
    data = mcf.read_data_file(mdname)

    if len(data) > 0:
        mon_data   = mcf.separate_data_to_arrays(data)
#
#--- find the last entry date and set starting time to the beginning of the month of that time period
#--- this is because the data of that last entties could be incomplete
#
        atemp  = re.split('\s+', data[-1])
        ltime  = float(atemp[0])
        ltime  = Chandra.Time.DateTime(ltime).date
        atemp  = re.split('\.', ltime)
        ltime  = time.strftime('%Y:%m', time.strptime(atemp[0], '%Y:%j:%H:%M:%S'))
        atemp  = re.split(':', ltime)
        syear  = int(float(atemp[0]))
        smonth = int(float(atemp[1])) 
#
#--- if this is the first time running this script, start from the empty data set
#
    else:
        mon_data   = []
        for k in range(0,mlen):
            mon_data.append([])

        syear  = 1999
        smonth = 8
#
#--- some initializations
#
    tlen  = len(data_set[0])                #--- length of the each data set
    save  = []                              #--- a list of lists to save mean of each month
    slp_t = []                              #--- a list of time related to slope list
    slp_y = []                              #--- a list of time related to slope list in <yyyy>:<mm>
    slp_s = []                              #--- a list of lists to save the slope of each month
    std_s = []                              #--- a list of lists to save std of each month
    tsave = []                              #--- a list of lists to save time for each value
    sums  = []                              #--- a list of lists to save the value for one month
#
#--- save which save monthly average, will hold the data from beginning (1999:08)
#--- but slope and the std hold only the newly computed part only
#
    for k in range(0, mlen):
        save.append([])
        slp_s.append([])
        std_s.append([])
    for k in range(0, dlen):
        sums.append([])
        tsave.append([])

    dpos  = 0                               #--- index on the full data set
    ipos  = 0                               #--- index on the monthly data set
    test  = 0
#
#--- before the data collection period starts, use the data from the monthly data set
#
    for  year in range(1999, tyear+1):
        for month in range(1, 13):
            if year < syear:
                for k in range(0, mlen):
                    try:
                        save[k].append(mon_data[k][ipos])
                    except:
                        pass
                ipos += 1
                continue

            elif (year == syear) and (month < smonth):
                for k in range(0, mlen):
                    try:
                        save[k].append(mon_data[k][ipos])
                    except:
                        pass
                ipos += 1
                continue

            elif (year == tyear) and (month > tmonth):
                break
#
#--- data gathering of each month from syear:smonth to tyear:tmonth starts here
#
            #if (year == syear) and (month == smonth):
            #    ldate = str(year) + ':' + mcf.add_leading_zero(month)
            #    slp_y.append(ldate)
            #    continue

            nyear  = year
            nmonth = month + 1
            if nmonth > 12:
                nmonth = 1
                nyear += 1
#
#--- set start, mid point, and stop time in seconds from 1998.1.1
#
            pstart = get_ctime(year,  month,  1)
            pmid   = get_ctime(year,  month, 15)
            pstop  = get_ctime(nyear, nmonth, 1)
#
#--- go through the main data
#
            for m in range(dpos, tlen):
                if data_set[0][m] < pstart:
                    continue
#
#--- data gethering of the period finished, compute averages
#
                elif data_set[0][m] > pstop:
#
#--- for the time use 15th of the month in seconds from 1998.1.1 format
#
                    save[0].append(pmid)
#
#--- second column is <yyyy>:<mm>
#
                    ldate = str(year) + ':' + mcf.add_leading_zero(month)
                    save[1].append(ldate)
                    
                    slp_t.append(pmid)
                    slp_y.append(ldate)
#
#--- now the slot data parts
#
                    for n in range(1, dlen):
#
#--- if there are data, make sure that they are not 'nan' before taking a mean
#
                        if len(sums[n]) > 0:
                            [t_list, v_list] = clean_up_list(tsave[n], sums[n])
                            if len(t_list) > 0:
                                save[n+1].append(numpy.mean(v_list))
#
#--- compute linear fitting on the data for the month and also compute the std of the data
#
                                if len(t_list) > 3:
                                    t_list = convert_to_ydate_list(t_list)
                                    [aa,bb,delta] = rlf.least_sq(t_list, v_list)
                                else:
                                    bb = -999
                                slp_s[n+1].append(bb)
                                std_s[n+1].append(numpy.std(v_list))
#
#--- if there is no valid data, use -999
#
                            else:
                                save[n+1].append(-999)
                                slp_s[n+1].append(-999)
                                std_s[n+1].append(-999)
#
#--- initialize the sums/tsave lists for the next round
#
                            try:
                                val = float(data_set[n][m])
                                sums[n]  = [val]
                                tsave[n] = [data_set[0][m]]
                            except:
                                sums[n]  = []
                                tsave[n] = []
                                continue
#
#--- no data during the period; just put -999
#
                        else:
                            save[n+1].append(-999)
                            slp_s[n+1].append(-999)
                            std_s[n+1].append(-999)
                            sums[n]  = []
                            tsave[n] = []
                            try:
                                val = float(data_set[n][m])
                                sums[n]  = [val]
                                tsave[n] = [data_set[0][m]]
                            except:
                                sums[n]  = []
                                tsave[n] = []
                                continue
#
#--- a few other initialization for the next round
#
                    sums[0]  = [data_set[0][m]]
                    tsave[0] = [data_set[0][m]]
                    dpos     = m + 1                #--- where to start reading the big data
                    lyear    = year                 #--- keep year and month for the later use
                    lmonth   = month
                    test     = 1
                    break
#
#--- the time is between the period. accumulate the data
#
                else:
                    for n in range(1, dlen):
                        try:
                            val = data_set[n][m]
                            if str(val).lower() in ['nan', 'na']:
                                continue

                            val = float(val)
#
#--- make sure that the value is reasonable
#
                            if val < 100 and val > -100:
                                sums[n].append(val)
                                tsave[n].append(data_set[0][m])
                        except:
                            continue
                    lyear  = year
                    lmonth = month
                    test   = 0
#
#--- the last part may not be a complete month data
#
    if test == 0:
        for n in range(1, dlen):
            test += len(sums[n])
        if test > 0:
            save[0].append(pmid)
            ldate = str(lyear) + ':' + mcf.add_leading_zero(lmonth)
            save[1].append(ldate)
    
            slp_t.append(pmid)
            slp_y.append(ldate)
    
            for n in range(1, dlen):
                if len(sums[n]) > 0:
                    [t_list, v_list] = clean_up_list(tsave[n], sums[n])
                    if len(t_list) > 0:
                        save[n+1].append(numpy.mean(v_list))
                        if len(t_list) > 3:
                            t_list = convert_to_ydate_list(t_list)
                            [aa,bb,delta] = rlf.least_sq(t_list, v_list)
                        else:
                            bb = -999.0
                        slp_s[n+1].append(bb)
                        std_s[n+1].append(numpy.std(v_list))
                    else:
                        save[n+1].append(-999)
                        slp_s[n+1].append(-999)
                        std_s[n+1].append(-999)
                else:
                    save[n+1].append(-999)
                    slp_s[n+1].append(-999)
                    std_s[n+1].append(-999)

#
#--- update the  mean monthly data set
#
    line  = ''
    for k in range(0, len(save[0])):
#
#--- prevent a dupulicated line
#
        if k != 0:
            if save[0][k] == save[0][k-1]:
                continue

        line  = line  + '%d\t' % save[0][k]
        line  = line  + save[1][k] + '\t'
        for n in range(2, mlen):
            line = line + format_line(save[n][k])

        line = line + '\n'

    with open(mdname, 'w') as fo:
        fo.write(line)
#
#---  update the slope/std monthly data set
#
    line = ''
    for k in range(0, len(slp_t)):
        line = line +  '%d\t' % slp_t[k]
        line = line + slp_y[k] + '\t'
        for n in range(2, mlen):
            line = line + format_line(slp_s[n][k])

        for n in range(2, mlen):
            line = line + format_line(std_s[n][k])
        line = line + '\n'
#
#--- since the slope data are saved only the new part, read the old data
#--- and find the spot whether the data are updated.
#
    sdname = mdname + '_slope'
    data   = mcf.read_data_file(sdname)
    try:
        btemp  = re.split(':', slp_y[0])
        syear  = int(float(btemp[0]))
        smon   = int(float(btemp[1]))
        aline  = ''
        for ent in data:
            atemp = re.split('\s+', ent)
            btemp = re.split(':' , atemp[1])
            cyear = int(float(btemp[0]))
            cmon  = int(float(btemp[1]))
            if cyear == syear and cmon == smon:
                break
            else:
                aline = aline + ent + '\n'
    except:
        aline = ''

    aline = aline + line

    with open(sdname, 'w') as fo:
        fo.write(aline)

#------------------------------------------------------------------------------------
#-- get_ctime: convert year month day into Chandra time                            --
#------------------------------------------------------------------------------------

def get_ctime(year, month, day):
    """
    convert year month day into Chandra time
    input:  year    --- year
            month   --- month
            day     --- day of month
    output: limt    --- time in seconds from 19981.1.
    """
    ltime  = str(year) + ':' + mcf.add_leading_zero(month) +  ':' + mcf.add_leading_zero(day)
    ltime  = time.strftime('%Y:%j:00:00:00', time.strptime(ltime, '%Y:%m:%d'))
    ltime  = int(Chandra.Time.DateTime(ltime).secs)

    return ltime

#------------------------------------------------------------------------------------
#-- clean_up_list: remove nan from lists assuming the second list has nan          --
#------------------------------------------------------------------------------------

def clean_up_list(x, y):
    """
    remove nan from lists assuming the second list has nan
    input:  x   --- a list
            y   --- a list which potentially has nan elements
    output: x   --- a cleaned up list
            y   --- a lceaned up list
    """
    sx = numpy.array(x)
    sy = numpy.array(y)

    idx = ~numpy.isnan(sy)
    sx  = sx[idx]
    sy  = sy[idx]

    return [sx, sy]

#------------------------------------------------------------------------------------
#-- format_line: format line for the data which is potentially nan                 --
#------------------------------------------------------------------------------------

def format_line(val):
    """
    format line for the data which is potentially nan
    input:  val     --- a numeric value which potentially nan
    outpu:  line    --- formated line
    """

    if val < -100 or str(val) == 'nan':
        line = '-999.0\t\t'
    else:
        line = '%2.3e\t' % val

    return line


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

#------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 2:
        year = int(float(sys.argv[1]))
        mon  = int(float(sys.argv[2]))
    else:
        year = ''
        mon  = ''

    update_monthly_averaged_slot_dataset(year, mon)
