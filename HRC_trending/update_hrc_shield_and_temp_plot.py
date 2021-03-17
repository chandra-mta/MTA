#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       update_hrc_shield_and_temp_plot.py: update HRC shield rate and temperature plots        #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Jun 26, 2018                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import pyfits
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; punlearn dataseeker  ', shell='tcsh')
#
#--- plotting routine
#
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
path = '/data/mta/Script/HRC/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- mission start
#
pstart = 52531199.0     #--- 1999:244:00:00:00; orbital data starts around this date
#
#--- HRC temperature column names
#
hrc_t_ds = ['2ceahvpt_avg','2chtrpzt_avg','2condmxt_avg','2dcentrt_avg','2dtstatt_avg','2fhtrmzt_avg','2fradpyt_avg','2pmt1t_avg','2pmt2t_avg','2uvlspxt_avg']

hrc_t_cols = ['ceahvpt','chtrpzt','condmxt','dcentrt','dtstatt','fhtrmzt','fradpyt','pmt1t','pmt2t','uvlspxt']

#-----------------------------------------------------------------------------------------
#-- update_hrc_shield_and_temp_plot: update HRC shield rate and temperature plots       --
#-----------------------------------------------------------------------------------------

def update_hrc_shield_and_temp_plot(start=''):
    """
    update HRC shield rate and temperature plots 
    input: start    --- stating time in seconds from 1998.1.1. default: "" 
                        find the last entry time and start from there
    output: updated databases in <data_dir>
            update plots in <web_dir>/Plots/
    """
#
#--- if the starting time is not given, find the last entry time and start from there
#
    data = []
    if start == '':
        ifile = data_dir + 'shield_rate'
        try:
            data  = read_file(ifile)

            atemp = re.split('\s+', data[-1])
            atime = float(atemp[0]) + 86400.0
            ldate = Chandra.Time.DateTime(atime).date
            atemp = re.split(':', ldate)
            atime = atemp[0] + ':' + atemp[1] + ':00:00:00'
            start = float(Chandra.Time.DateTime(atime).secs)
        except:
#
#--- if this is the first time, start from the first of the mission
#
            start = pstart
#
#--- stop time is set to the begining of today
#
    stop = time.strftime("%Y:%j:00:00:00", time.gmtime())
    stop = Chandra.Time.DateTime(stop).secs

    if (stop - start) < 86400:
        exit(1)

    lstart = Chandra.Time.DateTime(start).date
    lstop  = Chandra.Time.DateTime(stop).date
    print "Date Period: " + str(lstart) + '<-->' + str(lstop)
#
#--- hrc shield rate plot
#
    plot_shield_rate(data, start, stop)
#
#--- hrc temperature plots
#
    plot_hrc_temperature(start, stop)
#
#--- update the web page
#
    update_html_page()

#-----------------------------------------------------------------------------------------
#-- plot_shield_rate: plot shield rate vs time                                          --
#-----------------------------------------------------------------------------------------

def plot_shield_rate(indata, start, stop):
    """
    plot shield rate vs time
    input:  start   --- start time
            stop    --- stop time
    output: updated database:   <data_dir>/shield_rate
            updated plots:      <web_dir>/Plots/shield_rate.png            
    """
#
#--- read past pdata
#
    stime  = []
    shield = []
    if len(indata) > 0:
        for ent in indata:
            atemp = re.split('\s+', ent)
            stime.append(float(atemp[0]))
            shield.append(float(atemp[1]))
#
#--- extract orbital data; the orbital data may not updated close to current date. if that is the case, stop
#
    [otime, dist] = get_chandra_dist(start, stop)
    if len(otime) < 1:
        return False
#
#--- call dataseeker
#
    catname  = 'mtahrc..hrcveto_avg'
    colnames = ['shevart_avg',]
    [vtime, sdata] = call_dataseeker(catname, colnames, start, stop)

    index = [sdata > 0]
    sdata = sdata[index]
    vtime = vtime[index]
#
#--- find shield rate for the time
#
    m      = 0
    chk    = 0
    tsave  = []
    dsave  = []
    olast  = len(otime)
    for k in range(0, len(vtime)):
        p1 = vtime[k] - 300
        p2 = vtime[k] + 300
        chk = 0
        for n in range(m, olast):
            if otime[n] < p1:
                continue
            elif otime[n] > p2:
                break
            else:
                tsave.append(vtime[k])
                dsave.append(sdata[k])
                m = n - 10
                if m <= 0:
                    m = 0
#
#--- now take a daily average
#
    sum     = 0.0
    cnt     = 0.0
    pstart  = start
    pstop   = pstart + 86400.0
    for k in range(0, len(tsave)):
        if tsave[k] < pstart:
            continue

        elif (tsave[k] >= pstart) and (tsave[k] < pstop):
            sum += dsave[k]
            cnt += 1.0

        else:
            atime = pstart + 43200.0
            if cnt > 0:
                avg   = sum / cnt

                stime.append(atime)
                shield.append(avg)

                line  = "%d\t%3.2f" % (atime, avg)
                indata.append(line)

            pstart = pstop
            pstop  = pstart +  86400.0
            sum    = 0.0
            cnt    = 0.0
#
#--- update database
#
    out = data_dir + 'shield_rate'

    if os.path.isfile(out):
        cmd = 'mv ' + out + ' ' + out +'~'
        os.system(cmd)

    fo  = open(out, 'w')
    for ent in indata:
        fo.write(ent)
        fo.write('\n')
    fo.close()
#
#--- convert time into fractional year
#
    stime = change_to_fyear(stime)
#
#--- plot data
#
    outname = web_dir + 'Plots/shiled_rate.png'
    plot_data(stime, shield, 0, 2.5e4,  'Time (Year)', 'Sheild Rate (per Sec)', outname)


#-----------------------------------------------------------------------------------------
#-- plot_hrc_temperature: plotting hrc temperature vs time                             ---
#-----------------------------------------------------------------------------------------

def plot_hrc_temperature(start, stop):
    """
    plotting hrc temperature vs time
    input:  start   --- start time
            stop    --- stop time
    output: updated database:   <data_dir>/hrc_temp_data
            updated plots:      <web_dir>/Plots/<name_temp_plot.png            
    """
    
    tsave = []
    ssave = []
    for k in range(0, 10):
        ssave.append([])
#
#--- read past data
#
    indata = []
    ifile = data_dir + 'hrc_temp_data'
    if os.path.isfile(ifile):
        indata = read_file(ifile)
        for ent in indata:
            atemp = re.split('\s+', ent)
            tsave.append(float(atemp[0]))
            for k in range(0, 10):
                ssave[k].append(float(atemp[k+1]))
#
#
#--- call dataseeker
#
    start    = tsave[-1]
    catname  = 'mtahrc..hrctemp_avg'
    [stime, tdata] = call_dataseeker(catname, hrc_t_ds, start, stop)
    if len(stime) < 1:
        return False
#
#--- now take a daily average
#
    sum = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    cnt = 0.0
    pstart  = start
    pstop   = pstart + 86400.0
    for k in range(0, len(stime)):
        if stime[k] < pstart:
            continue

        elif (stime[k] >= pstart) and (stime[k] < pstop):
            for m in range(0, 10):
                sum[m]  += tdata[m][k]
            cnt += 1.0

        else:
            atime = pstart + 43200.0
            line  = str(int(atime))

            chk = 0
            for m in range(0, 10):
                if cnt == 0:
                    chk = 1
                    break

                avg  = sum[m] / cnt
                ssave[m].append(avg)

                line = line +'\t%3.2f'% avg

            if chk == 0:
                indata.append(line)
                tsave.append(atime)

            pstart = pstop
            pstop  = pstart + 86400.0
            sum    = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            cnt    = 0.0
#
#--- update database
#
    out = data_dir + 'hrc_temp_data'

    if os.path.isfile(out):
        cmd = 'mv ' + out + ' ' + out +'~'
        os.system(cmd)

    fo  = open(out, 'w')
    for ent in indata:
        fo.write(ent)
        fo.write('\n')
    fo.close()
#
#--- convert time into fractional year
#
    tsave = change_to_fyear(tsave)
#
#--- plot data
#
    ymin = 280
    ymax = 310
    xlabel = 'Time (Year)'
    ylabel = 'Temperature (K)'
    
    for k in range(0, len(hrc_t_cols)):
        name = hrc_t_cols[k]
        out  = web_dir + 'Plots/' + name + '_temp_plot.png'

        plot_data(tsave, ssave[k], ymin, ymax, xlabel, ylabel, out, title=name,  width=10.0, height=3.0)

#-----------------------------------------------------------------------------------------
#-- get_chandra_dist: find the distance of Chandra                                      --
#-----------------------------------------------------------------------------------------

def get_chandra_dist(start, stop):
    """
    find the distance of Chandra 
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: otime   --- a list of time in seconds from 1998.1.1
            dist    --- a list of distance in km

    note:  the distance below 80,000 km is not included
    """
#
#--- extract orbital data 
#
    ifile = '/data/mta/DataSeeker/data/repository/aorbital.rdb'
    data  = read_file(ifile)

    otime = []
    dist  = []
    for k in range(2,len(data),2):
        ent = data[k]
        atemp = re.split('\s+', ent);
        try:
            stime = float(atemp[0])

            if stime < start:
                continue
            if stime > stop:
                break

            x     = float(atemp[1])
            y     = float(atemp[2])
            z     = float(atemp[3])
            var   = math.sqrt(x * x + y * y + z * z)
#
#--- select data; chandra is farther than 80000km
#
            if var < 80000:
                continue

            otime.append(stime)
            dist.append(var)
        except:
            pass

    return [otime, dist]

#-----------------------------------------------------------------------------------------
#-- call_dataseeker: extract data using dataseeker                                      --
#-----------------------------------------------------------------------------------------

def call_dataseeker(catname, colnames, start, stop):
    """
    extract data using dataseeker
    input:  catname     --- category name
            colnames    --- a list of column names
            start       --- start time
            stop        --- stop time
    output: vtime       --- a list of times in seconds from 1998.1.1
            sdata       --- either a list of lists of a list of data for the column(s)
    """
#
#--- set dataseeker input
#
    line = 'columns=' + catname + '\n'
    line = line + 'timestart=' + str(start) + '\n'
    line = line + 'timestop='  + str(stop)  + '\n'
    fo   = open('inline', 'w')
    fo.write(line)
    fo.close()
#
#--- run dataseeker
#
    mcf.rm_file('out.fits')

    cmd1 = "/usr/bin/env PERL5LIB= "
    cmd2 = " dataseeker.pl infile=inline print=yes "
    cmd2 = cmd2 + "outfile=out.fits loginFile=" + house_keeping + "loginfile"
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
    mcf.rm_file('./inline')
#
#--- read data
#
    fin   = pyfits.open("out.fits")
    data  = fin[1].data
    vtime = data['time']

    sdata = []
    for col in colnames:
        odata = data[col]
        sdata.append(odata)
    fin.close()

    mcf.rm_file('out.fits')
#
#--- if only one data set is extracted, return just the list not a list of lists
#
    if len(sdata) <= 1:
        sdata = sdata[0]

    return [vtime, sdata]

#-----------------------------------------------------------------------------------------
#-- change_to_fyear: change time format from chadra time to fractional year             --
#-----------------------------------------------------------------------------------------

def change_to_fyear(stime):
    """
    change time format from chadra time to fractional year
    input:  stime   --- a list of time in seconds from 1998.1.1
    output: ctime   --- a list of time in fractional year
    """
    ctime = []
    for ent in stime:
        ldate = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', ldate)
        year  = float(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])

        if tcnv.isLeapYear(year) == 1:
            base = 366.0
        else:
            base = 365.0

        fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base

        ctime.append(fyear)

    return ctime

#-----------------------------------------------------------------------------------------
#-- plot_data:  plot data on a single panel png                                         ---
#-----------------------------------------------------------------------------------------

def plot_data(x, y, ymin, ymax, xlabel, ylabel, outname, title="",  width=10.0, height=5.0):
    """
    plot data
    input:  x       --- a list of independent data
            y       --- a list of dependent data
            ymin    --- min of y plotting range
            ymax    --- max of y plotting range
            xlabel  --- a label of x axis
            ylabel  --- a label of y axis
            outname --- the output file name
            title   --- tile; default: none
            width   --- width of the plot in inch; default: 10 in
            height  --- height of the plot in inch: default: 5 in
    output: outname
    """
#
#--- set params
#   
    fsize  = 10
    pcolor = 'blue'
    marker = '.'
    msize  = 4
    lw     = 0
#
#--- set x range
#
    xmin = 1999
    xmax = int(max(x)) + 1
#
#--- close everything open
#
    plt.close('all')
#
#--- set fot size
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
#
#--- set plotting range
#
    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- plot data
#
    plt.plot(x, y, color=pcolor, marker=marker, markersize=msize, lw=0)
    plt.xlabel(xlabel, size=fsize)
    plt.ylabel(ylabel, size=fsize)
#
#--- if a title is given, add
#
    if title != "":
        xdiff = xmax - xmin
        xpos  = xmin + 0.05 * xdiff
        ydiff = ymax - ymin
        ypos  = ymax - 0.10 * ydiff
        plt.text(xpos, ypos, title, size=fsize)
#
#--- create plot and save
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=200)
    plt.close('all')

#-----------------------------------------------------------------------------------------
#-- update_html_page: update html page                                                  --
#-----------------------------------------------------------------------------------------

def update_html_page():
    """
    update html page
    input:  none, but read from HRC site
    output: <web_dir>/htc_trend.html
    """
    ihtml = '/proj/web-cxc-dmz/htdocs/contrib/cxchrc/HRC_trendings/ArLac/arlac_energy_trend.html'
    data  = read_file(ihtml)
    html  = data[:-10]

    bhtml = house_keeping + 'bottom_part.html'
    data  = read_file(bhtml)

    html  = html + data

    out   = web_dir + 'hrc_trend.html'
    fo    = open(out, 'w')
    for ent in html:
        fo.write(ent)
        fo.write('\n')

    fo.close()

#-----------------------------------------------------------------------------------------
#-- read_file: read data file                                                           --
#-----------------------------------------------------------------------------------------

def read_file(file):
    """
    read data file
    input:  file    --- input file name
    output: data    --- data list
    """

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    return data

#-----------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        start = float(sys.argv[1])
    else:
        start = ''

    update_hrc_shield_and_temp_plot(start)
    #update_html_page()


