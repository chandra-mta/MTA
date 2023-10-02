#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#       create_focal_temperature_plots.py: create focal plane temperature plot          #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Sep 23, 2021                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import re
import numpy
import time
import datetime
import Chandra.Time
import getpass

import matplotlib as mpl
mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
from matplotlib import gridspec
#
#--- Directory list
#
DATA_DIR = '/data/mta/Script/ACIS/Focal/Data/'
OUT_DATA_DIR = DATA_DIR
PLOT_DIR = '/data/mta/www/mta_fp/Plots/'

d_in_sec = 86400.0

#-------------------------------------------------------------------------------
#-- create_focal_temperature_plots: create focal plane temperature plots      --
#-------------------------------------------------------------------------------

def create_focal_temperature_plots():
    """
    create focal plane temperature plots
    input:  none but read from <data_dir>
    output: <plot_dir>*.png
    """
    xlab1 = "Time (Day of Year)"
    xlab2 = "Time (Year)"
    ylab1 = "Focal Temp (C)"
    ylab2 = "Temp (C)"
#
#--- find current time
#
    stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    today = Chandra.Time.DateTime(stday).secs
    atemp = stday.split(":")
    year  = int(atemp[0])
    nyear = year + 1
    yday  = float(time.strftime("%j", time.gmtime()))
#
#--- week long plot
#
    cut    = today   - 8 * d_in_sec
    start  = int(change_ctime_to_ydate(cut)[1])
    stop   = int(change_ctime_to_ydate(today)[1])

    ifile  = DATA_DIR + 'full_focal_plane_data_' + str(year)
    if yday < 7:
        ycut = 0
    else:
        ycut = cut
    [x, y, rta, rtb] = select_data(ifile, ycut, today)

    if yday < 7:
        if is_leapyear(year-1):
            dadd = 366.0
        else:
            dadd = 365.0
        ifile  = DATA_DIR + 'full_focal_plane_data_' + str(year-1)
        [xp, yp, rtap, rtbp] = select_data(ifile, cut, today)
        x   = xp + list(numpy.array(x) + dadd)
        y   = yp + y
        rta = rtap + rta
        rtb = rtbp + rtb
        stop  += dadd

    ymin   = -120
    ymax   = -90
    xlab3  = "Time (Day of Year" + str(year) + ")"
#
#--- take moving average so that jumps between two state will be smoothed out
#
    rta = create_moving_average(rta, 20)
    rtb = create_moving_average(rtb, 20)
    plot_data(x, y, rta, rtb, start, stop, ymin, ymax, xlab3, ylab1,  "focal_week_long.png")
#
#--- one year long plot
#
    ystart = str(year) + ':001:00:00:00'
    begin  = Chandra.Time.DateTime(ystart).secs
    ifile  = DATA_DIR + 'focal_plane_data_5min_avg_' +  str(year)
    [x, y, rta, rtb] = select_data(ifile, begin, today)
    ymin   = -120
    ymax   = -90
    outplt = 'focal_1year_long_' + str(year) +'.png'
    plot_data(x, y, rta, rtb, 0, 366, ymin, ymax, xlab1, ylab1, outplt, width=25, height=2.5)
#
#--- if it is the first couple of days of the year, update the last year's plot, too
#
    if yday < 3:
        syear = year -1
        ifile  = DATA_DIR + 'focal_plane_data_5min_avg_' +  str(syear)
        ystart = str(syear) + ':001:00:00:00'
        lbegin = Chandra.Time.DateTime(ystart).secs
        [x, y, rta, rtb] = select_data(ifile, lbegin, begin)
        outplt = 'focal_1year_long_' + str(syear) +'.png'
        plot_data(x, y, rta, rtb, 0, 366, ymin, ymax, xlab1, ylab1, outplt, width=25, height=2.5)
#
#--- full range plot
#
    ifile  = DATA_DIR + 'long_term_max_data'
    cut    = 0.0
    [x, y, rta, rtb] = select_data(ifile, cut, today, yd=0)
    ymin   = -120
    ymax   = -90
    plot_data(x, y, rta, rtb, 2000, nyear, ymin, ymax, xlab2, ylab1, "focal_full_range.png")

#-------------------------------------------------------------------------------
#-- create_moving_average: taking a moving average                            --
#-------------------------------------------------------------------------------

def create_moving_average(data, step):
    """
    taking a moving average
    input:  data    --- a list of data
            step    --- a step size (numbers of data point)
    output: out     --- a list of data smoothed by moving average
    """
    dlen  = len(data)

    if dlen == 0:
        return data

    if dlen <= step:
        step = dlen

    out = []
    sum = 0
    partb = data[0:step]
    bavg  = numpy.mean(partb)
    
    for k in range(0, step):
        out.append(bavg)
    
    for k in range(0, dlen-step):
        part = data[k:k+step]
        pavg = numpy.mean(part)
        out.append(pavg)
    
    return out

#-------------------------------------------------------------------------------
#-- select_data_over_data_files: select data with possibility of over several data files
#-------------------------------------------------------------------------------

def select_data_over_data_files(start, stop, binsize):
    """
    select data with possibility of over several data files
    input:  start   --- start time
            stop    --- stop time
            format is either chandra time, <yyyy>:<ddd>:<hh>:<mm>, or <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
            binsize --- bin size in seconds
    output: x       --- a list of time
            y       --- a list of focal temp
            rta     --- a list of 1crat
            rtb     --- a list of 1crbt
    """
    [year1, start] = check_time_format(start)
    [year2, stop]  = check_time_format(stop)

    x   = []
    y   = []
    rta = []
    rtb = []
    chk = 0
    for year in range(year1, year2+1):
        ifile = DATA_DIR + 'full_focal_plane_data_' + str(year)
        with open(ifile,'r') as f:
            data = [line.strip() for line in f.readlines()]

        for ent in data:
            atemp = ent.split()
            atime = float(atemp[0])
            if atime < start:
                continue
            if atime > stop:
                break

            x.append(float(atemp[0]))
            y.append(float(atemp[1]))
            rta.append(float(atemp[2]))
            rtb.append(float(atemp[3]))
    
    if binsize == 0:

        x = convert_to_ydate_list(x)

        return [x, y, rta, rtb]

    else:
#
#--- binning of the data
#
        hbin  = int(0.5 * binsize)

        xa    = []
        ya    = []
        raa   = []
        rab   = []
    
        yt    = []
        rxa   = []
        rxb   = []
        begin = x[0]
        end   = begin + binsize
        for k in range(0, len(x)):
            if (x[k] >= begin) and (x[k] < end):
                yt.append(y[k])
                rxa.append(rta[k])
                rxb.append(rtb[k])
            else:
                xa.append(begin + hbin)
                ya.append(numpy.average(yt))
                raa.append(numpy.average(rxa))
                rab.append(numpy.average(rxb))

                yt    = [y[k]]
                rxa   = [rta[k]]
                rxb   = [rtb[k]]
                begin = end
                end   = begin + binsize
    
        if len(yt) > 0:
            xa.append(int(0.5 * (begin + x[-1])))
            ya.append(numpy.average(yt))
            raa.append(numpy.average(rxa))
            rab.append(numpy.average(rxb))
    
        xa = convert_to_ydate_list(xa)

        return [xa, ya, raa, rab]

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def convert_to_ydate_list(x):

    nx = []
    byear = ''
    for val in x:
        cdata = change_ctime_to_ydate(val)
        if byear == '':
            byear = cdata[0]
            if is_leapyear(byear):
                base = 366
            else:
                base = 365
        if cdata[0] > byear:
            nx.append(cdata[1] + base)
        else:
            nx.append(cdata[1])

    return nx


#-------------------------------------------------------------------------------
#-- check_time_format: return time in Chandra time                            --
#-------------------------------------------------------------------------------

def check_time_format(intime):
    """
    return time in Chandra time
    input:  intime  --- time in <yyyy>:<ddd>:<hh>:<mm>:<ss> 
                        or <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> or chandra time
    output: year    --- the year
            time in chandra time (seconds from 1998.1.1)
    """
    mc1 = re.search('-', intime)
    mc2 = re.search(':', intime)
#
#--- it is already chandra format
#
    if isinstance(intime,'float') or isinstance(intime,'int'):
        out   = Chandra.Time.DateTime(intime).date
        atemp = out.split(":")
        year  = int(atemp[0])
        return [year, int(float(intime))]
#
#--- time in <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
#
    elif mc1 is not None:
        mc2 = re.search('T', intime)
        if mc2 is not None:
            atemp = intime.split("T")
            btemp = atemp[0].split("-")
            year  = int(float(btemp[0]))
            mon   = int(float(btemp[1]))
            day   = int(float(btemp[2]))
            ctemp = atemp[1].split(':')
            hrs   = ctemp[0]
            mins  = ctemp[1]
            secs  = ctemp[2]
     
        else:
            btemp = intime.split('-')
            year  = int(float(btemp[0]))
            mon   = int(float(btemp[1]))
            day   = int(float(btemp[2]))
            hrs   = '00'
            mins  = '00'
            secs  = '00'
    
        yday = datetime.date(year, mon, day).timetuple().tm_yday
     
        cyday = str(yday)
        if yday < 10:
            cyday = '00' + cyday
        elif yday < 100:
            cyday = '0' + cyday
    
        ytime = btemp[0] + ':' + cyday + ':' + hrs + ':' + mins + ':' + secs

        return [year, Chandra.Time.DateTime(ytime).secs]
#
#--- time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
#
    elif mc2 is not None:
        btemp = intime.split(":")
        year  = int(atemp[0])
        return [year, Chandra.Time.DateTime(intime).secs]

#-------------------------------------------------------------------------------
#-- select_data: select data in the range and change the time format           -
#-------------------------------------------------------------------------------

def select_data(ifile, start, stop, yd=1):
    """
    select data in the range and change the time format
    input:  ifile   --- data file name
            start   --- the data start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            yd      --- indicator to create fractional year (0) or ydate (1)
    output  xdata   --- a list of time data
            ydata   --- a list of temperature data
            radata  --- a list of 1crat data
            rbdata  --- a list of 1crbt data
    """
    with open(ifile,'r') as f:
        data = [line.strip() for line in f.readlines()]
    xdata_pre  = []
    ydata  = []
    radata = []
    rbdata = []
    for ent in data:
        try:
            atemp = ent.split()
            atime = float(atemp[0])
        except:
            continue 

        if atime < start:
            continue
        if atime > stop:
            break

        xdata_pre.append(atime)
        fval  = float(atemp[1])
        ydata.append(fval)

        test  = float(atemp[2])
        if test > -110:
            test = -125
        diff = fval - test
        radata.append(diff)

        test  = float(atemp[3])
        if test > -110:
            test = -125
        diff = fval - test
        rbdata.append(diff)

    xdata = []
    for ent in xdata_pre:
        date = change_ctime_to_ydate(ent, yd=yd)
        xdata.append(date[1])

    return [xdata, ydata, radata, rbdata]

#-------------------------------------------------------------------------------
#-- plot_data: plot the data                                                  --
#-------------------------------------------------------------------------------

def plot_data(x, y0, y1, y2, xmin, xmax, ymin, ymax,  xname, yname, outname, width=4, height=3):
    """
    plot the data
    input:  x       --- a list of x data
            y       --- a list of y data
            xmin    --- a min of the x plotting range
            xmax    --- a max of the x plotting range
            ymin    --- a min of the y plotting range
            ymax    --- a max of the y plotting range
            xname   --- x axis label
            yname   --- y axis label
            outname --- output file name
            width   --- width of the plot in inches
            height  --- height of the plot in inches
    output: outname --- a png file
    """
#
#--- close everything opened before starting a new one
#
    plt.close('all')
#
#---- set parameters
#
    mpl.rcParams['font.size'] = 5
    xpos = xmin + 0.05 * (xmax - xmin)
    mks  = 0.5
    mkt  = '.'
#
#--- set plotting range
#
    fig = plt.figure()
    gs  = gridspec.GridSpec(3, 1, height_ratios=[3,1,1])
#
#--- plot data
#
    ax0 = plt.subplot(gs[0])
    ax0.set_xbound(xmin, xmax)
    ax0.set_ybound(-120, -90)
    ax0.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax0.set_ylim(ymin=-120, ymax=-90, auto=False)
    ax0.text(xpos, -103, "Focal", fontsize=6)

    line0 = ax0.plot(x, y0, color='r', marker=mkt, markersize=mks, lw=0, label='Focal')
    plt.ylabel("Temp (C)", position=(0.1, 0.1))

    ax1 = plt.subplot(gs[1])
    ax1.set_xbound(xmin, xmax)
    ax1.set_ybound(3, 13)
    ax1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax1.set_ylim(ymin=3, ymax=13, auto=False)
    ax1.text(xpos, 11, "(Focal - 1CRAT)", fontsize=6)

    line1 = ax1.plot(x, y1, color='b', marker=mkt, markersize=mks, lw=0, label='Focal - 1CRAT')

    ax2 = plt.subplot(gs[2])
    ax2.set_xbound(xmin, xmax)
    ax2.set_ybound(3, 13)
    ax2.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax2.set_ylim(ymin=3, ymax=13, auto=False)
    ax2.text(xpos, 11, "(Focal - 1CRBT)", fontsize=6)

    line2 = ax2.plot(x, y2, color='g', marker=mkt, markersize=mks, lw=0, label='Focal - 1CRBT')

    plt.subplots_adjust(hspace=0.08)

    plt.xlabel(xname)

    line = ax0.get_xticklabels()
    for label in line:
        label.set_visible(False)

    line = ax1.get_xticklabels()
    for label in line:
        label.set_visible(False)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5 in)
#
    fig = plt.gcf()
    fig.set_size_inches(width, height)
#
#--- save the plot in png format
#
    plt.savefig('ztemp.png', format='png', dpi=200)
#
#--- close the plot
#
    plt.close('all')
    cmd = f"convert ./ztemp.png -trim {PLOT_DIR}{outname}; rm -f ztemp.png"
    os.system(cmd)

#-------------------------------------------------------------------------------
#-- set_plotting_range: find min/max of x and y axes and set plotting ranges  --
#-------------------------------------------------------------------------------

def set_plotting_range(x, y):
    """
    find min/max of x and y axes and set plotting ranges
    input:  x   --- a list of x data
            y   --- a list of y data
    output: [xmin, xmax, ymin, ymax]
    """
    xmin = int(min(x))
    xmax = int(max(x))
    diffx = xmax - xmin

    xmax += 0.1 * diffx
    xmax = int(xmax)

    xmin -= 0.1 * diffx
    xmin = int(xmin)
    
    ymin = int(min(y))
    ymax = int(max(y))
    diffy = ymax - ymin

    ymax += 0.1 * diffy
    ymax = int(ymax)
    
    ymin -= 0.1 * diffy
    ymin = int(ymin)

    return [xmin, xmax, ymin, ymax]

#-------------------------------------------------------------------------------
#-- change_ctime_to_ydate: convert chandra time into fractional year or ydate --
#-------------------------------------------------------------------------------

def change_ctime_to_ydate(cdate, yd=1):
    """
    convert chandra time into fractional year or ydate
    input:  cdate   --- chandra time
            yd      --- indicator to create fractional year (0) or ydate (1)
    output: year    --- the year of the date
            date    --- if yd==0, date in fractional year, otherwise, in ydate
    """

    date  = Chandra.Time.DateTime(cdate).date
    atemp = date.split(":")
    year  = float(atemp[0])
    date  = float(atemp[1])
    hh    = float(atemp[2])
    mm    = float(atemp[3])
    ss    = float(atemp[4])
    date += (hh + mm / 60.0 + ss / 3600.0) /24.0

    if yd == 1:
        return [year, date]
    else:
        if is_leapyear(year):
            base = 366
        else:
            base = 365

        date = year + date /base

        return [year, date]

#--------------------------------------------------------------------------
#-- is_leapyear: check whether the year is a leap year                   --
#--------------------------------------------------------------------------

def is_leapyear(year):
    """
    check whether the year is a leap year
    input:  year    --- year
    output: True/False
    """
    year = int(float(year))
    chk  = year % 4             #--- every 4 years:   leap year
    chk2 = year % 100           #--- but every 100 years: not leap year
    chk3 = year % 400           #--- except every 400 year: leap year

    val  = False
    if chk == 0:
        val = True
        if chk2 == 0:
            val = False
    if chk3 == 0:
        val = True

    return val

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")
        
    create_focal_temperature_plots()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")