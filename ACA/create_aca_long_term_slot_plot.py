#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       create_aca_long_term_slot_plot.py: create long term plots for slot data             #
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
import numpy
import Chandra.Time

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
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

data_list = ['pos_err_mtatr', 'diff_mtatr', 'acacent_mtatr']
slot_name = ['pos_err', 'diff', 'ang']

oneyear   = 365 * 86400.0

#-----------------------------------------------------------------------------------
#-- create_aca_long_term_slot_plot:  create long term plots  for slot data        ---
#-----------------------------------------------------------------------------------

def create_aca_long_term_slot_plot(year=''):
    """
    create long term plots for slot data
    input:  year    --- year, if it is not given, use this year
            <data_dir>/<inst>
            <data_dir>/<inst>_month
    output: <web_dir>/Plots/<year>/<slot name>_<#>.png
            <web_dir>/Plots/<slot name>_<#>_recent_1yr.png
            <web_dir>/Plots/<yyyy>/<slot name>_<#>.png
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
            also read from <data_dir>/<slot name>_<#>
    output: <web_dir>/Plots/<year>/<slot name>_<#>.png
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

    for m in range(0, 3):
#
#--- read data, separate into column data, and select the data only between time period specified
#
        ifile     = data_dir + data_list[m]
        data_set  = mcf.read_data_file(ifile)
        data_set  = mcf.separate_data_to_arrays(data_set)
        data_set  = select_data_for_time_period(data_set, tstart, tstop)
#
#--- save time in day of year
#
        time_list = []
        for tval in data_set[0]:
            time_list.append(mcf.chandratime_to_yday(tval))
#
#--- start plotting each slot
#
        for k in range(1, len(data_set)):
#
#--- acacent_mtatr hold 2 sets of data
#
            if m == 2:
                if k < 9:
                    y_name = slot_name[m] + 'ynea_' + str(k-2)
                else:
                    y_name = slot_name[m] + 'znea_' + str(k-9)
            else:
                y_name = slot_name[m] + '_' + str(k-1)
            out_name = y_name + '.png'

            [t_list, d_list] = drop_nan(time_list, data_set[k])

            xlabel = 'Day of Year (Year: ' + str(year) + ')'
            odir   = web_dir + 'Plots/' + str(year) + '/'
            if not os.path.isdir(odir):
                cmd = 'mkdir -p ' + odir
                os.system(cmd)
    
            out_name = odir + out_name

            if len(t_list) < 1:
                cmd = 'cp ' + house_keeping + 'no_data.png' + ' ' + out_name
                os.system(cmd) 
                continue
            plot_data(t_list, d_list, xlabel, y_name,  out_name)
        

#-----------------------------------------------------------------------------------
#-- create_recent_one_year_plot: create most recent one year trending plots       --
#-----------------------------------------------------------------------------------

def create_recent_one_year_plot():
    """
    create most recent one year trending plots
    input:  none, but read from <data_dir>/<slot name>_<#>
    output: <web_dir>/Plots/<slot name>_<#>_recent_1yr.png
    """
    for m in range(0, 3):
        ifile     = data_dir + data_list[m]
#
#--- read data, separate into column data, and select the data only between time period specified
#
        data_set  = mcf.read_data_file(ifile)
        data_set  = mcf.separate_data_to_arrays(data_set)
#
#--- find the data starting time (one year before the last data point)
#
        tstop  = data_set[0][-1]
        tstart = tstop - oneyear
        data_set  = select_data_for_time_period(data_set, tstart, tstop)

#
#--- save time in fractional year
#
        time_list = []
        for tval in data_set[0]:
            time_list.append(mcf.chandratime_to_fraq_year(tval))

        for k in range(1, len(data_set)):
#
#--- acacent_mtatr hold 2 sets of data
#
            if m == 2:
                if k < 9:
                    y_name = slot_name[m] + 'ynea_' + str(k-2)
                else:
                    y_name = slot_name[m] + 'znea_' + str(k-9)
            else:
                y_name = slot_name[m] + '_' + str(k-2)
            out_name = web_dir + 'Plots/' + y_name + '_recent_1yr.png'

            [t_list, d_list] = drop_nan(time_list, data_set[k])
            if len(t_list) < 1:
                cmd = 'cp ' + house_keeping + 'no_data.png' + ' ' + out_name
                os.system(cmd) 
                continue

            xlabel = 'Time (year)'
    
            plot_data(t_list, d_list, xlabel, y_name, out_name, xs=1)
        
#-----------------------------------------------------------------------------------
#-- create_full_lange_plot: create full range trending plot                       --
#-----------------------------------------------------------------------------------

def create_full_lange_plot():
    """
    create full range trending plots
    input:  none, but read from <data_dir>/<inst>_month
    output: <web_dir>/Plots/<inst>_full.png
    """
    for m in range(0, 3):
        ifile     = data_dir + data_list[m] + '_month'
#
#--- read data, separate into column data
#
        data_set  = mcf.read_data_file(ifile)
        data_set  = mcf.separate_data_to_arrays(data_set)
#
#--- save time in fractional year format
#
        time_list = []
        for ent in data_set[1]:
            atemp = re.split(':', ent)
            tval = float(atemp[0]) + float(atemp[1]) / 12.0
            time_list.append(tval)

        for k in range(2, len(data_set)):
#
#--- acacent_mtatr hold 2 sets of data
#
            if m == 2:
                if k < 9:
                    y_name = slot_name[m] + 'ynea_' + str(k-2)
                else:
                    y_name = slot_name[m] + 'znea_' + str(k-9)
            else:
                y_name = slot_name[m] + '_' + str(k-2)

            out_name = web_dir + 'Plots/' + y_name + '_full.png'

            [t_list, d_list] = drop_nan(time_list, data_set[k])
            if len(t_list) < 1:
                cmd = 'cp ' + house_keeping + 'no_data.png' + ' ' + out_name
                os.system(cmd) 
                continue

            xlabel = 'Time (year)'

            plot_data(t_list, d_list, xlabel, y_name, out_name)


#-----------------------------------------------------------------------------------
#-- drop_nan: drop nan from lists, assuming the second list might have nan value   -
#-----------------------------------------------------------------------------------

def drop_nan(x, y):
    """
    drop nan from lists, assuming the second list might have nan
    input:  x   --- a list
            y   --- a list in which nan may exist
    output: xl  --- a cleaned up list
            yl  --- a cleaned up list
    """
    if len(x) == 0:
        return [x, y]

    ax  = numpy.array(x)
    ay  = numpy.array(y)
    idx = ~numpy.isnan(ay)

    xl  = list(ax[idx])
    yl  = list(ay[idx])

    return [xl, yl]

#-----------------------------------------------------------------------------------
#-- select_data_for_time_period: select data for the given time period            --
#-----------------------------------------------------------------------------------

def select_data_for_time_period(data_set, tstart, tstop):
    """
    select data for the given time period. assume that the time is in the first column
    input:  data_set    --- a list of lists of data
            tstart      --- starting time in seconds from 1998.1.1
            tstop       --- stopping time in seconds from 1998.1.1
    output: save        --- a list of lists of data in the time period
    """
    tarray = numpy.array(data_set[0])
    idx    = (tarray >=tstart) & (tarray <= tstop)
    save   = []
    for ent in data_set:
        varray = numpy.array(ent)
        out    = varray[idx]
        lout   = list(out)
        save.append(lout)

    return save

#-----------------------------------------------------------------------------------
#-- plot_data: create plot                                                        --
#-----------------------------------------------------------------------------------

def plot_data(t_list, d_list, xlabel, ylabel, outname, xs=0):
    """
    create plot
    input:  t_list  --- a list of x data
            d_list  --- a list of y data
            xlabel  --- the label for x axis
            ylabel  --- the label for y axis
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
    tarray = tarray[idx]
    darray = darray[idx]
    idx    = (darray < 100) & (darray > -100)
    t_list = list(tarray[idx])
    d_list = list(darray[idx])
#
#--- if there are  no data, copy no data plot
#
    if len(t_list) < 1:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + outname
        os.system(cmd)
        return False
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
#--- compute fitting line and plot the fitted line
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

def remove_na_from_lists(alist, blist):

    out1 = []
    out2 = []
    for k in range(0, len(alist)):
        if mcf.is_neumeric(alist[k]) and mcf.is_neumeric(blist[k]):
            out1.append(alist[k])
            out2.append(blist[k])
    
    return [out1, out2]


#-----------------------------------------------------------------------------------

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    create_aca_long_term_slot_plot(year)

