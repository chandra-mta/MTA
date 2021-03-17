#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       create_aca_long_term_mag_plot.py: create long term plots                            #
#                                                                                           #
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
import Chandra.Time
import numpy

import matplotlib as mpl
if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
#
#--- reading directory list
#
path = '/data/mta/Script/ACA/Scripts/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

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
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

inst_list = ['ACIS_1', 'ACIS_2', 'ACIS_3', 'ACIS_4', 'ACIS_5', 'ACIS_6', \
             'HRC_I_1', 'HRC_I_2', 'HRC_I_3', 'HRC_I_4', \
             'HRC_S_1', 'HRC_S_2', 'HRC_S_3', 'HRC_S_4']

oneyear   = 365 * 86400.0

#-----------------------------------------------------------------------------------
#-- create_aca_long_term_mag_plot:  create long term plots                       ---
#-----------------------------------------------------------------------------------

def create_aca_long_term_mag_plot(year=''):
    """
    create long term plots
    input:  year    --- year, if it is not given, use this year
            <data_dir>/mag_i_avg_<#>
            <data_dir>/<inst>
    output: <web_dir>/Plots/<year>/mag_i_avg_<#>.png
            <web_dir>/Plots/mag_i_avg_<#>_recent_1yr.png
            <web_dir>/<MMM><yy>/Plots/MAG_I_AVG_<#>.png
    """
#
#--- create one year long plots for the given year
#
    create_year_long_plot(year)
#
#--- create most recent one year long plots
#
    create_recent_one_year_plot()
#
#--- create full range plots
#
    create_full_lange_plot()

#-----------------------------------------------------------------------------------
#-- create_year_long_plot: create one year long plots for the given year          --
#-----------------------------------------------------------------------------------

def create_year_long_plot(year):
    """
    create one year long plots for the given year. if the year is not given, use this year
    input:  year    --- year
            also read from <data_dir>/mag_i_avg_<#>
    output: <web_dir>/Plots/<year>/mag_i_avg_<#>.png
    """
#
#--- if the year is not given, use this year, except the first 10 days of year
#--- create the last year's plot
#
    if year == '':
        year = int(float(time.strftime('%Y', time.gmtime())))
        mday = int(float(time.strftime('%j', time.gmtime())))
        if mday < 5:
            year -= 1
#
#--- set starting and stopping time of the data interval
#
    tstart = str(year) + ':001:00:00:00'
    tstart = Chandra.Time.DateTime(tstart).secs
    tstop  = tstart + oneyear
    if mcf.is_leapyear(year):
        tstop += 86400.0

    for fid in range(1, 15):
        ifile  = data_dir + 'mag_i_avg_' + str(fid)
        data   = mcf.read_data_file(ifile)

        t_list = []
        d_list = []
        for ent in data:
            atemp = re.split('\s+', ent)
            tval  = float(atemp[0])
            dval  = float(atemp[1])
            if tval < tstart:
                continue
            elif tval > tstop:
                break

            if dval <= 0.0 or str(dval) == 'nan':
                continue

            t_list.append(tval)
            d_list.append(dval)

        if len(t_list) == 0:
            cmd = 'cp ' + house_keeping + 'no_data.png ' + oname
            os.system(cmd)
            return 

        t_list = convert_to_ydate_list(t_list)

        xlabel = 'Day of Year (Year: ' + str(year) + ')'
        odir   = web_dir + 'Plots/' + str(year) + '/'
        if not os.path.isdir(odir):
            cmd = 'mkdir -p ' + odir
            os.system(cmd)

        oname  = odir + 'mag_i_avg_' + str(fid) + '.png'

        plot_data(t_list, d_list, fid, xlabel, oname)
        
#-----------------------------------------------------------------------------------
#-- create_recent_one_year_plot: create most recent one year trending plots       --
#-----------------------------------------------------------------------------------

def create_recent_one_year_plot():
    """
    create most recent one year trending plots
    input:  none, but read from <data_dir>/mag_i_avg_<#>
    output: <web_dir>/Plots/mag_i_avg_<#>_recent_1yr.png
    """
    for fid in range(1, 15):
        ifile  = data_dir + 'mag_i_avg_' + str(fid)
        data   = mcf.read_data_file(ifile)
#
#--- find the data starting time (one year before the last data point)
#
        atemp  = re.split('\s+', data[-1])
        tlast  = float(atemp[0])
        tstart = tlast - oneyear

        t_list = []
        d_list = []
        for ent in data:
            atemp = re.split('\s+', ent)
            tval  = float(atemp[0])
            dval  = float(atemp[1])
            if tval < tstart:
                continue
            if dval <= 0.0 or str(dval) == 'nan':
                continue
            t_list.append(tval)
            d_list.append(dval)

        [byear, xxx] = chandratime_to_yday(t_list[0])

        if len(t_list) == 0:
            cmd = 'cp ' + house_keeping + 'no_data.png ' + oname
            os.system(cmd)
            return 

        t_list       = convert_to_ydate_list(t_list)

        xlabel = 'Day of Year (Year: ' + str(byear) + ')'
        oname  = web_dir + 'Plots/mag_i_avg_' + str(fid) + '_recent_1yr.png'

        plot_data(t_list, d_list, fid, xlabel, oname, xs=1)
        
#-----------------------------------------------------------------------------------
#-- create_full_lange_plot: create full range trending plot                       --
#-----------------------------------------------------------------------------------

def create_full_lange_plot():
    """
    create full range trending plots
    input:  none, but read from <data_dir>/<inst>
    output: <web_dir>/Plots/<inst>_full.png
    """
    for k in range(0, len(inst_list)):
        inst   = inst_list[k].lower()
        ifile  = data_dir + inst
        data   = mcf.read_data_file(ifile)
        t_list = []
        d_list = []
        for ent in data:
            atemp = re.split('\s+', ent)
            yval  = float(atemp[2])
#
#--- drop bad data (usually lower than or equal to 0.0 mag)
#
            if yval <= 0.0 or str(yval) == 'nan':
                continue

            btemp = re.split(':', atemp[1])
#
#--- time in the format of <yyyy>:<mm>
#
            tval  = float(btemp[0]) + float(btemp[1]) / 12.0
            t_list.append(tval)
            d_list.append(yval)
#
#--- set fid light # etc
#
        fid    = k + 1
        xlabel = 'Time (year)'
        oname  = web_dir + 'Plots/' + inst + '_full.png'

        plot_data(t_list, d_list, fid, xlabel, oname)


#-----------------------------------------------------------------------------------
#-- plot_data: create plot                                                        --
#-----------------------------------------------------------------------------------

def plot_data(t_list, d_list, fid, xlabel, outname, xs=0):
    """
    create plot
    input:  t_list  --- a list of x data
            d_list  --- a list of y data
            fid     --- fid light #
            xlabel  --- the label for x axis
            outname --- plot file name
            xs      --- indicator which way to set xaxis range
    output: outname --- png plot created
    """

    [t_list, d_list] = remove_na_from_lists(t_list, d_list)
    tarray = numpy.array(t_list)
    darray = numpy.array(d_list)
    idx    = ~numpy.isnan(darray)
    tarray = tarray[idx]
    darray = darray[idx]
    idx    = (darray < 100) & (darray > -100)
    t_list = list(tarray[idx])
    d_list = list(darray[idx])
#
#--- set plotting range
#
    if xs == 0:
        xmin   = int(min(t_list)) - 1
        xmax   = int(max(t_list)) + 1
    else:
        xmin   = (int(10 * min(t_list)) - 0.5) / 10.0
        xmax   = (int(10 * max(t_list)) + 1.5) / 10.0

    ymin   = (int(10 * min(d_list)) - 0.5) / 10.0
    ymax   = (int(10 * max(d_list)) + 1.5) / 10.0
#
#--- y label
#
    ylabel = 'MAG_I_AVG_' + str(fid)
#
#--- start plotting
#
    plt.close('all')
    props = font_manager.FontProperties(size=9)

    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
    ax.set_facecolor("lime")
#
#--- plot data
#
    plt.plot(t_list, d_list, marker='D', markersize=2, lw=0)
#
#--- compute fitting line and plot a fitted line
#
    try:
        if len(t_list) > 3:
            out    = rlf.robust_fit(t_list, d_list)
            pstart = out[0] + out[1] * xmin
            pstop  = out[0] + out[1] * xmax
            plt.plot([xmin, xmax],[pstart, pstop], markersize=0, lw=1, linestyle='dashed', color='blue')
    except:
        pass

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
#
#--- set the size of the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(7, 3.5)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dip=300)
    plt.close('all')

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def remove_na_from_lists(alist, blist):

    out1 = []
    out2 = []
    for k in range(0, len(alist)):
        if mcf.is_neumeric(alist[k]) and mcf.is_neumeric(blist[k]):
            out1.append(alist[k])
            out2.append(blist[k])

    return [out1, out2]


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

#-----------------------------------------------------------------------------------

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    create_aca_long_term_mag_plot(year)

