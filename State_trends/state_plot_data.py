#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#           state_plot_data.py: plot time trends of MJ and SIM state data               #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Mar 10, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
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
path = '/data/mta/Script/OBT/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions     as mcf
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- state_plot_data: plot time trends of MJ and SIM state data                         ---
#-----------------------------------------------------------------------------------------

def state_plot_data():
    """
    plot time trends of MJ and SIM state data 
    input: none but read from <mj_data_dir>/<sim_data_dir>
    output:<html_dir>/Plots/*png
    """
#
#--- find today's date
#
    out   = time.strftime("%Y:%j", time.gmtime())
    atemp = re.split(':', out)
    year  = int(atemp[0])
    yday  = int(atemp[1])
#
#--- plot data
#
    plot_data(mj_data_dir,  'comprehensive_data_summary', 'MJ',  year, yday)
    plot_data(sim_data_dir, 'sim_data_summary',           'SIM', year, yday)

#-----------------------------------------------------------------------------------------
#-- plot_data: read data and plot the data                                              --
#-----------------------------------------------------------------------------------------

def plot_data(ddir, head, catg, lyear, lyday):
    """
    read data and plot the data
    input:  ddir    --- data directory name
            head    --- header of the output file
            catg    --- MJ or SIM
            lyear   --- current year
            lyday   --- today's yday
    output:<html_dir>/Plots/*png
    """
#
#--- read data from 1999 to today
#
    for year in range(1999,  lyear+1):
        ifile = ddir + head + str(year)
        data  = mcf.read_data_file(ifile)

        if year == 1999:
            cols = re.split('\s+', data[0])     #--- column name list
            clen = len(cols)
#
#--- make a daily average of the data
#
            save = make_daily_avg(data[1:], clen, year)
        else:
            short = make_daily_avg(data[1:], clen, year)
            for k in range(0, len(save)):
                save[k] = save[k] + short[k]
#
#--- plotting each data
#
    plot_each_panel(save, cols, catg, lyear, lyday)

#-----------------------------------------------------------------------------------------
#-- make_daily_avg: make a daily average of data                                        --
#-----------------------------------------------------------------------------------------

def make_daily_avg(data, clen, iyear):
    """
    make a daily average of data
    input:  data    --- a list of lists of data
            clen    --- the numbers of data lists
            iyear   --- a year of which you want to extract the data
    output: save    --- a list of lists of daily averaged data
    """
#
#--- initialized a lists
#
    save = []       #--- a list of list of daily averaged data
    dadd = []       #--- a list to accumulate sum of the data for the day
    dcnt = 0
    for k in range(0, clen):
        save.append([])
        dadd.append(0)

    pdate = 0
    base  = 0
    for ent in data:
#
#--- the first list is time data (<yyyy>:<ddd>:<hh>:<mm>:<ss>)
#
        atemp = re.split('\s+', ent)
        btemp = re.split(':', atemp[0])
        try:
            year  = int(btemp[0])
        except:
            continue
        if year != iyear:
            continue
#
#--- find the year length in day (first time only)
#
        if base == 0:
            if mcf.is_leapyear(year):
                base = 366.0
            else:
                base = 365.0
#
#--- if ydate is same, accumulate the data
#
        ydate = int(btemp[1])
        if ydate == pdate:
            for k in range(1, clen):
                try:
                    val = float(atemp[k])
                except:
#
#--- none numeric cases
#
                    mc1 = re.search('ENAB', atemp[k])
                    mc2 = re.search('DISA', atemp[k])
                    mc3 = re.search('NMAN', atemp[k])
                    mc4 = re.search('NPNT', atemp[k])
                    mc5 = re.search('FMT',  atemp[k])
                    if mc1 is not None:
                        val = 1
                    elif mc2 is not None:
                        val = 0
                    elif mc3 is not None:
                        val = 0
                    elif mc4 is not None:
                        val = 1
                    elif mc5 is not None:
                        val = int(atemp[k].replace('FMT',''))
                    else:
                        val = 0
#
#--- add to the "sum"
#
                dadd[k] += val
            dcnt += 1
        else:
#
#--- yday changed; compute the daily average of the day before
#
            if dcnt > 0:
                ttime = float(year) + ydate / base
                save[0].append(ttime)
                for k in range(1, clen):
                    save[k].append(dadd[k]/dcnt)
                    try:
                        val = float(atemp[k])
                    except:
                        mc1 = re.search('ENAB', atemp[k])
                        mc2 = re.search('DISA', atemp[k])
                        mc3 = re.search('NMAN', atemp[k])
                        mc4 = re.search('NPNT', atemp[k])
                        mc5 = re.search('FMT',  atemp[k])
                        if mc1 is not None:
                            val = 1
                        elif mc2 is not None:
                            val = 0
                        elif mc3 is not None:
                            val = 0
                        elif mc4 is not None:
                            val = 1
                        elif mc5 is not None:
                            val = int(atemp[k].replace('FMT',''))
                        else:
                            val = 0

                    dadd[k] = val
                dcnt  = 1
            pdate = ydate 
#
#--- if there are leftovers, compute average and save
#
    if dcnt > 0:
        ttime = float(year) + ydate / base
        save[0].append(ttime)
        for k in range(1, clen):
            save[k].append(dadd[k]/dcnt)

    return save

#-----------------------------------------------------------------------------------------
#-- plot_each_panel: plot time trend data for each data                                 --
#-----------------------------------------------------------------------------------------

def plot_each_panel(indata, cols, catg, lyear, lyday):
    """
    plot time trend data for each data
    input:  indata  --- a list of lists of data
            cols    --- a list of column names
            ctag    --- MJ or SIM
            lyear   --- this year
            lyday   --- the latest ydate
    output: <html_dir>/Plots/*png
    """
#
#--- go through each data; the first column is time in year
#
    for k in range(1, len(cols)):
        col   = cols[k]
        out   = html_dir + 'Plots/' + catg + '/' + col + '.png'
        ddata = indata[k]
#
#--- set x axis range
#
        xmin  = 1999
        if lyday > 183:
            xmax = lyear + 1
        else:
            xmax  = lyear + 0.5
#
#--- set y axis range
#
        ymin  = min(ddata)
        ymax  = max(ddata)
        ydiff = ymax - ymin
        ymin -= 0.1 * ydiff
        ymax += 0.1 * ydiff
        if ymin == ymax:
            ymin -= 1
            ymax += 1
#
#--- plot start from here
#
        plt.close('all')
        ax  = plt.subplot(111)
        ax.set_autoscale_on(False)
        ax.set_xbound(xmin,xmax)
        ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
        ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
        plt.plot(indata[0], ddata, color='red', marker='.', markersize=5, lw =0)
        plt.xlabel('Time (year)')
        plt.ylabel(col)

        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(10, 5)
        plt.savefig(out, format='png', dpi=200)

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    state_plot_data()

