#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#           monthly_focal_temp_plot.py: plot acis focal temperature trend for monthly       #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Aug 06, 2018                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import time
import math
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
from datetime import datetime
import Chandra.Time
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; punlearn dataseeker', shell='tcsh')
#
#--- plotting routine
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(mta_dir)
sys.path.append(bin_dir)
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
#--- set column names and header
#
orb_col_list  = ['time', 'x', 'y', 'z']
ang_col_list  = ['time','point_suncentang']
lfile         = '/data/mta/Script/Weekly/Focal/house_keeping/loginfile'

#-----------------------------------------------------------------------------------------------
#-- monthly_focal_temp_plot: plot acis focal temperature  for monthly                        ---
#-----------------------------------------------------------------------------------------------

def monthly_focal_temp_plot(tyear='', mon=''):
    """
    plot acis focal temperature; the plotting range is the last one month
    input:  none, but read from several database
    output: ./acis_focal_temp.png
    """
#
#--- if the time period is not givne, set for the last month
#
    if tyear =='':
        tyear = int(time.strftime("%Y", time.gmtime()))
        mon   = int(time.strftime("%m", time.gmtime()))
        mon  -= 1
        if mon < 1:
            mon = 12
            tyear -= 1

    nyear  = tyear
    aline  = str(tyear) + ':' + str(mon) + ':01'
    line   = datetime.datetime.strptime(aline, '%Y:%m:%d').strftime('%Y:%j:00:00:00')
    syday  = int(datetime.datetime.strptime(aline, '%Y:%m:%d').strftime('%j'))
    cstart = Chandra.Time.DateTime(line).secs
    nmon   = mon +  1
    if nmon > 12:
        nmon = 1
        nyear += 1

    line   = str(nyear) + ':' + str(nmon) + ':01'
    line   = datetime.datetime.strptime(line, '%Y:%m:%d').strftime('%Y:%j:00:00:00')
    cstop  = Chandra.Time.DateTime(line).secs
#
#--- extract focal temp data
#
    [ftime, focal]     = read_focal_temp(tyear, syday, cstart, cstop)
#
#--- convert time format to yday
#
    [ftime, byear]     = convert_time_format(ftime)
#
#--- extract altitude data and sun angle data
#
    [atime, alt, sang] = read_orbit_data(cstart, cstop)
    [atime, byear]     = convert_time_format(atime)
#
#--- convert alttude to normalized to sun angle (range between 0 and 180)
#
    alt                = compute_norm_alt(alt)
#
#--- plot data
#
    xlabel             = 'Day of Year (' + str(byear) + ')'
    [ltime, byear]     = convert_time_format([cstart, cstop])

    plot_data(ftime, focal, atime, alt, sang, ltime[0], ltime[1], xlabel)

#-----------------------------------------------------------------------------------------------
#-- read_focal_temp: read focal plane temperature data                                        --
#-----------------------------------------------------------------------------------------------

def read_focal_temp(tyear, yday, tstart, tstop):
    """
    read focal plane temperature data
    input:  tyear   --- this year
            yday    --- today's y date
            tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: ftime   --- a list of time 
            focal   --- a list of focal temp
    """
#
#--- if y daay is less than 8, read the data from the last year
#
    if yday < 8:
        ifile  = '/data/mta/Script/ACIS/Focal/Data/focal_plane_data_5min_avg_' + str(tyear-1)
        data   = read_data_file(ifile, sep='\s+', c_len=2)
        ftime  = data[0]
        focal  = data[1]
    else:
        ftime  = []
        focal  = []
#
#--- otherwise, just read this year
#
    ifile  = '/data/mta/Script/ACIS/Focal/Data/focal_plane_data_5min_avg_' + str(tyear)
    data   = read_data_file(ifile, sep='\s+', c_len=2)
    ftime  = ftime + data[0]
    focal  = focal + data[1]
#
#--- select out the data for the last 7 days
#
    [ftime, focal] = select_data_by_date(ftime, focal, tstart, tstop)

    return [ftime, focal]

#-----------------------------------------------------------------------------------------------
#-- read_orbit_data: read altitude and sun angle data                                        ---
#-----------------------------------------------------------------------------------------------

def read_orbit_data(tstart, tstop):
    """
    read altitude and sun angle data
    input:  tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: data    --- a list of lists of [time alt, sun_angle]
    """
#
#--- set up the input for dataseeker and extract the data
#
    fits = 'dataseek_avg.fits'
    cmd  = 'touch test'
    os.system(cmd)

    cmd1 = '/usr/bin/env PERL5LIB=  '
    cmd2 = " dataseeker.pl infile=test outfile=" + fits + " "
    cmd2 = cmd2 + "search_crit='columns=pt_suncent_ang,sc_altitude timestart=" + str(tstart)
    cmd2 = cmd2 + " timestop=" + str(tstop) + "' loginFile=" + lfile

    cmd  = cmd1 + cmd2
    bash(cmd, env=ascdsenv)
#
#--- read fits file and extract the data
#
    cols = ['time', 'sc_altitude', 'pt_suncent_ang']
    data = read_fits_data(fits, cols)
#
#--- clean up
#
    mcf.rm_file(fits)
    mcf.rm_file('test')

    return data

#-----------------------------------------------------------------------------------------------
#-- select_data_by_date: selet out the potion of the data by time                             --
#-----------------------------------------------------------------------------------------------

def select_data_by_date(x, y, tstart, tstop):
    """
    selet out the potion of the data by time
    input:  x       --- a list of time data
            y       --- a list of data
            tstart  --- a starting time in seconds from 1998.1.1
            tstop   --- a stopping time in seconds from 1998.1.1
    output: x       --- a list of time data selected
            y       --- a list of data selected
    """

    x   = numpy.array(x)
    y   = numpy.array(y)
    ind = [(x > tstart) & (x < tstop)]
    x   = list(x[ind])
    y   = list(y[ind])

    return [x, y]

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def compute_norm_alt(v, nval=180.):
    """
    normalize the data to a given max size
    input:  v       --- a list of the data
            nval    --- the max value; default = 180
    output: v       --- a list of the data normlaized
    """
    vmin = min(v)
    vmax = max(v)
    v    = v - vmin
    v    = v / (vmax - vmin)
    v    = v * nval

    return list(v)

#-----------------------------------------------------------------------------------------------
#-- convert_time_format: convert a list of the time data into ydate                           --
#-----------------------------------------------------------------------------------------------

def convert_time_format(otime):
    """
    convert a list of the time data into ydate
    input:  otime   --- a list of time in seconds from 1998.1.1
    output: save    --- a list of time in y date
            prev    --- the year of the data
    """

    save = []
    prev = 0
    for ent in otime:
        out = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', out)

        year  = int(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])

        yday +=  hh /24.0 + mm / 1440.0 + ss / 86400.0

        if prev == 0:
            prev = year
            save.append(yday)
            if tcnv.isLeapYear(year) == 1:
                base = 366
            else:
                base = 365
        else:
            if year != prev:
                save.append(yday + base)
            else:
                save.append(yday)

    return [save, prev]

#-----------------------------------------------------------------------------------------------
#-- read_data_file: read ascii data file                                                      --
#-----------------------------------------------------------------------------------------------

def read_data_file(ifile, sep='', remove=0, c_len=0):
    """
    read ascii data file
    input:  ifile   --- file name
            sep     --- split indicator: default: '' --- not splitting
            remove  --- indicator whether to remove the file after reading: default: 0 --- no
            c_len   --- numbers of columns to be read. col=0 to col= c_len. default: 0 --- read all
    output: data    --- a list of lines or a list of lists
    """

    f    = open(ifile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if remove > 0:
        mcf.rm_file(ifile)

    if sep != '':
        atemp = re.split(sep, data[0])
        if c_len == 0:
            c_len = len(atemp)
        save = []
        for k in range(0, c_len):
            save.append([])

        for ent in data:
            atemp = re.split(sep, ent)
            for k in range(0, c_len):
                try:
                    save[k].append(float(atemp[k]))
                except:
                    save[k].append(atemp[k])

        return save
    
    else:
        return data

#-----------------------------------------------------------------------------------------------
#-- plot_data: plot data                                                                      --
#-----------------------------------------------------------------------------------------------

def plot_data(ftime, ftemp, stime, alt, sang, xmin, xmax, xlabel):
    """
    plot data
    input:  ftime   --- a list of time for focal temp 
            ftemp   --- a list of focal temp data
            stime   --- a list of time for altitude and sun angle
            alt     --- a list of altitude data
            sang    --- a list of sun agnle
            xmin    --- min of x plotting range
            xmax    --- max of x plotting range
            xlabel  --- the label for x axis
    output: acis_focal_temp.png
    """
#    
#--- set sizes
#
    fsize  = 16
    color  = 'blue'
    color2 = 'red'
    color3 = 'green'
    marker = '.'
    psize  = 8
    lw     = 3
    alpha  = 0.3
    width  = 10.0
    height = 5.0
    resolution = 200
#
#-- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
    plt.subplots_adjust(hspace=0.08)
#
#--- set plotting range  focal temp
#
    [ymin, ymax] = set_focal_temp_range(ftemp)

    fig, ax1 = plt.subplots()

    ax1.set_autoscale_on(False)
    ax1.set_xbound(xmin,xmax)
    ax1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax1.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    temp, = ax1.plot(ftime, ftemp, color=color, label="Focal Temp", lw=lw)

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel('Focal Plane Temp (degC)')
    ax1.tick_params(axis='y', labelcolor=color)
#
#--- set plotting range sun angle
#
    ax2 = ax1.twinx()                   #--- setting the second axis 

    ax2.set_autoscale_on(False)
    ax2.set_xbound(xmin,xmax)
    ax2.set_xlim(xmin=xmin,  xmax=xmax, auto=False)
    ax2.set_ylim(ymin=0, ymax=180, auto=False)

    sun, = ax2.plot(stime, sang, color=color2, label="Sun Angle", alpha=0.8)

    ax2.set_ylabel('Sun Angle (degree)')
    ax2.tick_params(axis='y', labelcolor=color2)
#
#--- plot altitude
#
    alt, = ax2.plot(stime, alt, color=color3, label="Altitude", alpha=0.8)
#
#--- adding legend
#
    fontP = font_manager.FontProperties()
    fontP.set_size(8)
    plt.legend(loc='upper right', bbox_to_anchor=(1.0, -0.06), handles=[temp, sun, alt], fancybox=False, ncol=1, prop=fontP)
#
#--- save the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig('acis_focal_temp.png', format='png', dpi=resolution)

    plt.close('all')

#-----------------------------------------------------------------------------------------------
#-- set_focal_temp_range: setting the focal temp plotting range                               --
#-----------------------------------------------------------------------------------------------

def set_focal_temp_range(v):
    """
    setting the focal temp plotting range
    input:  v       --- focal temp
    output: vmin    --- min of the plotting range
            vmax    --- max of the plotting range
    """

    vmin = min(v)
    vmax = max(v)
    diff = vmax - vmin

    if vmin  > 122:
        vmin = 122
    else:
        vmin = int(vmin) -1
    
    vmax = int(vmax + 0.02 * diff)

    return [vmin, vmax]


#-------------------------------------------------------------------------------------------------
#-- read_fits_data: read fits data                                                              --
#-------------------------------------------------------------------------------------------------

def read_fits_data(fits, cols):
    """
    read fits data
    input:  fits    --- fits file name
            cols    --- a list of col names to be extracted
    output: save    --- a list of lists of data extracted
    """

    hout = pyfits.open(fits)
    data = hout[1].data
    hout.close()

    save = []
    for col in cols:
        out = data[col]
        save.append(out)

    return save

    

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_read_focal_temp(self):

        year   = 2018
        yday   = 5
        cdate  = Chandra.Time.DateTime('2018:005:00:00:00').secs
        cstart = cdate - 86400.0 * 7.0

        [x, y] = read_focal_temp(year, yday, cstart, cdate)

        print 'Focal: ' + str(len(x)) + '<-->' + str(x[:10]) + '<-->' +  str(y[:10])


#------------------------------------------------------------

    def test_read_orbit_data(self):

        year   = 2018
        yday   = 5
        cdate  = Chandra.Time.DateTime('2018:005:00:00:00').secs
        cstart = cdate - 86400.0 * 7.0

        [x, y, y2] = read_orbit_data(cstart, cdate)

        print 'Alt: ' + str(len(x)) + '<-->' + str(x[:10]) + '<-->' +  str(y[:10])


#------------------------------------------------------------

    def test_read_sunangle(self):

        year   = 2018
        yday   = 5
        cdate  = Chandra.Time.DateTime('2018:005:00:00:00').secs
        cstart = cdate - 86400.0 * 7.0

        [x, y] = read_sunangle(cstart, cdate)

        print 'Sun Angle: ' + str(len(x)) + '<-->' + str(x[:10]) + '<-->' +  str(y[:10])





#-----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    #unittest.main()
    if len(sys.argv) == 3:
        year = int(float(sys.argv[1]))
        yday = int(float(sys.argv[2]))
    else:
        year = ''
        yday = ''

    monthly_focal_temp_plot(year, yday)








