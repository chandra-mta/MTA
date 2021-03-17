#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       aorwspd_plot.py:    plot AORWSPD movement for monthly report                        #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Mar 10, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import math
import numpy
import pyfits
import time
import Chandra.Time
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')


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
path = '/data/mta/Script/Month/SIM/house_keeping/dir_list_py'

with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())   
zspace = '/tmp/zspace' + str(rtail)

loginfile = '/data/mta/Script/Month/SIM/house_keeping/loginfile'
datafile  = '/data/mta/Script/Month/SIM/house_keeping/monthly_avg'


#-----------------------------------------------------------------------------------------
#-- plot_sim_movement: read tsc and fa data and plot their cummulatinve movement        --
#-----------------------------------------------------------------------------------------

def plot_aorwspd(year, month):

    """
    read tsc and fa data and plot their cummulatinve movement
    input: none
    output: monthly_sim.png
    """
#
#--- read data and add to the database
#
    [time, aw1, aw2, aw3, aw4, aw5, aw6] = read_data(year, month)
#
#--- plot data
#
    plot_data(time, aw1, aw2, aw3, aw4, aw5, aw6)


#-----------------------------------------------------------------------------------------
#-- read_data: read data and compute  monthly averages of aw values                     --
#-----------------------------------------------------------------------------------------

def read_data(year, month):

    """
    read data and compute  monthly averages of aw values
    input: year / month
    output: [time, aw1, aw2, aw3, aw4, aw5, aw6]
    """
#
#--- change data format
#
    lyear = str(year)
    lmon  = str(month)
    if month < 10:
        lmon = '0' + lmon
    ltime = lyear + '.' + lmon
    ctime = float(year) + float(month) / 12

#
#--- get data
#
    data = mcf.read_data_file(datafile)

    time = []
    aw1  = []
    aw2  = []
    aw3  = []
    aw4  = []
    aw5  = []
    aw6  = []
    for ent in data:
        atemp = re.split('\s+', ent)
        try:
            btemp = re.split('\.', atemp[0])
            val   = float(btemp[0]) + float(btemp[1]) / 12.0
            time.append(val)

            for i in range(1, 7):
                val = 1.375056e-3 * float(atemp[i])     #---- 1.375066e-3 = 1440 * 9.549 /1e7
                if val > 12:
                    val = 12

                exec("aw%s.append(float(%s))" % (i, val))
        except:
            pass
#
#--- check whether this time period is already extracted or not
#
    chk = 0
    for ent in time:
        if ctime == ent:
            chk = 1
            break
#
#--- if it is not extract data and append
#
    if chk == 0:
        [av1, av2, av3, av4, av5, av6] = get_new_value(year, month)
        time.append(ctime)
        aw1.append(av1 *  1.375056e-3)
        aw2.append(av2 *  1.375056e-3)
        aw3.append(av3 *  1.375056e-3)
        aw4.append(av4 *  1.375056e-3)
        aw5.append(av5 *  1.375056e-3)
        aw6.append(av6 *  1.375056e-3)
#
#--- add the new data into the database
#
        line = ltime + '\t' 
        line = line  + str(av1) + '\t' 
        line = line  + str(av2) + '\t'
        line = line  + str(av3) + '\t'
        line = line  + str(av4) + '\t'
        line = line  + str(av5) + '\t'
        line = line  + str(av6) + '\n'

        ofile = '/data/mta/Script/Month/SIM/house_keeping/monthly_avg'
        with open(ofile, 'a') as fo:
            fo.write(line)

    return [time, aw1, aw2, aw3, aw4, aw5, aw6]


#-----------------------------------------------------------------------------------------
#-- get_new_value: extract aorwspd values from dataseeker                              ---
#-----------------------------------------------------------------------------------------

def get_new_value(year, month):

    """
    extract aorwspd values from dataseeker
    input: year/month
    output: [av1, av2, av3, av4, av5, av6] --- six values of aorwspd(1-6)
    """
#
#--- set month long time interval in sec from 1998.1.1
#
    year2 = year
    month2 = month -1
    if month2 < 1:
        mont2  = 12
        year2 -= 1

    ltime = str(year) + ':' + mcf.add_leading_zero(month) + ':15'
    ltime = time.strftime('%Y:%j:00:00:00', time.strptime(ltime, '%Y:%m:%d'))
    time1 = Chandra.Time.DateTime(ltime)


    ltime = str(year2) + ':' + mcf.add_leading_zero(month2) + ':15'
    ltime = time.strftime('%Y:%j:00:00:00', time.strptime(ltime, '%Y:%m:%d'))
    time2 = Chandra.Time.DateTime(ltime)
#
#--- set command to call dataseeker
#
    cmd = 'touch ./test'
    os.system(cmd)                  #-- we need an empty "test" file to run dataseeker

    mcf.mk_empty_dir('param')       #-- make empty param directory

    line = 'columns=_aorwspd1_avg,'
    line = line + '_aorwspd2_avg,'
    line = line + '_aorwspd3_avg,'
    line = line + '_aorwspd4_avg,'
    line = line + '_aorwspd5_avg,'
    line = line + '_aorwspd6_avg'
    line = line + ' timestart=' + str(time2)
    line = line + ' timestop='  + str(time1)

    cmd = 'punlearn dataseeker;  dataseeker.pl infile=test outfile=ztemp.fits search_crit=\''
    cmd = 'dataseeker.pl infile=test outfile=ztemp.fits search_crit="'
    cmd = cmd + line + '"  loginFile="' + loginfile + '"'

#
#--- run dataseeker
#
    bash("/usr/bin/env PERL5LIB='' " + cmd, env=ascdsenv)

    mcf.rm_file(zspace)
    mcf.rm_file('./test')
    os.system('rm -rf ./param')
#
#--- read fits file
#
    try:
        dout = pyfits.getdata('./ztemp.fits')
        aw1  = dout.field('AORWSPD1_AVG')
        aw2  = dout.field('AORWSPD2_AVG')
        aw3  = dout.field('AORWSPD3_AVG')
        aw4  = dout.field('AORWSPD4_AVG')
        aw5  = dout.field('AORWSPD5_AVG')
        aw6  = dout.field('AORWSPD6_AVG')
    except:
        aw1 = aw2 = aw3 = aw4 = aw5 = aw6 = []

    mcf.rm_file("./ztemp.fits")
#
#--- create monthly "sum" of the reaction wheel rotations
#--- dataseeker gives 5 min avg of the value; one day is 24 hr x 60 min / 5min =  288.
#
    sum1 = sum2 = sum3 = sum4 = sum5 = sum6 = 0.0
    for i in range(0, len(aw1)):
        sum1 += abs(aw1[i])
        sum2 += abs(aw2[i])
        sum3 += abs(aw3[i])
        sum4 += abs(aw4[i])
        sum5 += abs(aw5[i])
        sum6 += abs(aw6[i])

    av1 = sum1 / 288
    av2 = sum2 / 288
    av3 = sum3 / 288
    av4 = sum4 / 288
    av5 = sum5 / 288
    av6 = sum6 / 288

    return [av1, av2, av3, av4, av5, av6]

#-----------------------------------------------------------------------------------------
#-- plot_data: create six aw value history plots                                       ---
#-----------------------------------------------------------------------------------------

def plot_data(time, aw1, aw2, aw3, aw4, aw5, aw6):

    """
    create six aw value history plots
    input:  time    --- a list of time in fractional year
            set1    --- a list of tsc value
            set2    --- a list of fa value
    output: monthly_sim.png
    """
#
#--- set plottting range
#
    dlen = len(time)
    xmin = 2000
    ltim = time[dlen-1]
    xmax = int(ltim) + 1
    diff = ltim - int(ltim)
    if diff > 0.6 :
        xmax += 1

    ymin = 4
    ymax = 12
#
#-- set a few parameters
#
    fsize  = 9
    lsize  = 1
    color  = 'red'
    marker = 'o'
    msize  = 3
    plt.close("all")
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=fsize)
    plt.subplots_adjust(hspace=0.06, wspace=0.06)
#
    a1 = plt.subplot(321)
    plot_sub(a1, time, aw1, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline='AORWDAY1')

    a2 = plt.subplot(323)
    plot_sub(a2, time, aw3, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline='AORWDAY3')
    a2.set_ylabel('Counts (x10**7)', size=fsize)

    a3 = plt.subplot(325)
    plot_sub(a3, time, aw5, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline='AORWDAY5')
    a3.set_xlabel('Time (year)', size=fsize)
#
    a4 = plt.subplot(322)
    plot_sub(a4, time, aw1, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline='AORWDAY2')

    a5 = plt.subplot(324)
    plot_sub(a5, time, aw3, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline='AORWDAY4')

    a6 = plt.subplot(326)
    plot_sub(a6, time, aw5, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline='AORWDAY6')
    a6.set_xlabel('Time (year)', size=fsize)
#
#--- x ticks label only on the bottom panels
#--- y ticks label only on the left panels
#
    for i in range(0, 6):
        ax = 'a' + str(i+1)
        if i != 2 and i != 5:
            line =eval(" %s.get_xticklabels()" % (ax))

            for label in  line:
                label.set_visible(False)
        if i != 0 and i != 1 and i != 2:
            line = evel("%s.get_yticklabels()" % (ax))
            for label in  line:
                label.set_visible(False)
        else:
            pass
#
#--- save the plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)

    outname = 'rotation.png'
    plt.savefig(outname, format='png', dpi=100)

#-----------------------------------------------------------------------------------------
#-- plot_sub: plotting each panel                                                       --
#-----------------------------------------------------------------------------------------

def plot_sub(ap, x, y, xmin, xmax, ymin, ymax, color, lsize, marker, msize, tline=''):
    """
    plotting each panel
    input   ap      --- panel name
            x       --- x data list
            y       --- y data list
            xmin    --- xmin
            xmax    --- xmax
            ymin    --- ymin
            ymax    --- ymax
            color   --- color of data point
            lsize   --- line size
            marker  --- marker shape
            msize   --- size of the marker
            tlime   --- extra text line
    """

    ap.set_autoscale_on(False)
    ap.set_xbound(xmin,xmax)
    ap.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ap.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    plt.plot(x, y , color=color, lw=lsize, marker=marker, markersize=msize)

    if tline != '':
        xpos = 0.05 * (xmax - xmin) + xmin
        ypos = ymin +0.15 * (ymax - ymin)
        text(xpos, ypos, tline, fontsize=11,style='italic', weight='bold')


#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_read_data(self):

        year  = 2014
        month = 3
        [time, aw1, aw2, aw3, aw4, aw5, aw6] = read_data(year, month)

        at1 = [8.88757569388, 9.26060912568, 9.16673790126, 8.4134481965]
        at2 = [8.52632301696, 8.74607270278, 8.58685974873, 8.32711315412]
        at3 = [8.67624830427, 9.06458892166, 9.52579669502, 9.49361433224]
        at4 = [9.349014082, 9.57600077008, 9.06517336787, 8.4891914387]
        at5 = [8.06821379165, 8.42655310529, 8.69090888914, 8.23181720344]
        at6 = [9.12260341534, 9.36751429219, 9.4069413189, 9.56819585662]

        self.assertEquals(aw1[10:14], at1)
        self.assertEquals(aw2[10:14], at2)
        self.assertEquals(aw3[10:14], at3)
        self.assertEquals(aw4[10:14], at4)
        self.assertEquals(aw5[10:14], at5)
        self.assertEquals(aw6[10:14], at6)
    
#------------------------------------------------------------

    def test_convert_time(self):

        tlist = [5146.0085192338256, 6649.7235161736608, 5646.532719382395, 5662.6181798718044, 6145.2843457273102, 6131.2501007893843]

        self.assertEquals(get_new_value(2014, 3), tlist)
        
#------------------------------------------------------------


#-----------------------------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

chk = 0
if len(sys.argv) == 3:
    year  = sys.argv[1]
    month = sys.argv[2]
    year  = int(float(year))
    month = int(float(month))
    chk = 1

if __name__ == '__main__':

    if chk == 1:
        plot_aorwspd(year, month)
    else:
        unittest.main()



