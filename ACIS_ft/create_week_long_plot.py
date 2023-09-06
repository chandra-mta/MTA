#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#       create_week_long_plot.py: create focal plane temperature plot for a week period #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Sep 23, 2021                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import re
import time
import Chandra.Time
import unittest
import getpass
import datetime

import matplotlib as mpl
mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt

from matplotlib import gridspec
#
#--- reading directory list
#
path = '/data/mta4/testACIS/Focal/Script/house_keeping/dir_list'
#path = '/data/mta/Script/ACIS/Focal/Script/house_keeping/dir_list'

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
sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions     as mcf

d_in_sec = 86400.0

#-------------------------------------------------------------------------------
#-- create_week_long_plot: create focal plane temperature plots      --
#-------------------------------------------------------------------------------

def create_week_long_plot(year):
    """
    create focal plane temperature plots
    input:  year   --- the year in which you want to create plot
                        if "", it will create the most recent week only
    output: <plot_dir>*.png
    """
#
#--- week long plot
#
    [ylist, wlist, blist, elist] = find_week(year)
#
#--- crate plots
#
    for k in range(0, len(wlist)):
        year   = ylist[k]
        week   = wlist[k]
        start  = blist[k]
        stop   = elist[k]

        create_plot(year, week, start, stop)

#-------------------------------------------------------------------------------
#-- create_plot: create focal plane temperature plots for a given week        --
#-------------------------------------------------------------------------------

def create_plot(year, week, start, stop):
    """
    create focal plane temperature plots for a given week
    input:  year    --- year
            week    --- week #
            start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: <plot_dir>*.png
    """
    ifile  = data_dir + 'full_focal_plane_data_' + str(year)
    [x, y, rta, rtb] = select_data(ifile, start, stop)

    xlab1  = "Time (Day of Year)"
    ylab1  = "Focal Temp (C)"
    ymin   = -120
    ymax   = -90

    wstart = week * 7 + 1           #--- the first week start day 1
    wstop  =  wstart + 7

    outdir = plot_dir + 'Year' + str(year) 

    if not os.path.isdir(outdir):
        cmd = 'mkdir ' + outdir
        os.system(cmd)

    outdir  = plot_dir + 'Year' + str(year)
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)
    outfile = 'Year' + str(year) + '/focal_week_long_' + str(week) + '.png'

    plot_data(x, y, rta, rtb, wstart, wstop, ymin, ymax, xlab1, ylab1,  outfile)

#-------------------------------------------------------------------------------
#-- find_week: create lists of week starting and ending times                 --
#-------------------------------------------------------------------------------

def find_week(year):
    """
    create lists of week starting and ending times
    input:  year        --- the year of which we want to get the lists; if "", it makes for this year
    output: year_list   --- a list of the year(s)
            wlist       --- a list of week #
            blist       --- a list of week starting time in seconds from 1998.1.1
            elist       --- a list of week ending time in seconds from 1998.1.1
    """
    chk = 0
    if year == '':
        stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
        today = Chandra.Time.DateTime(stday).secs
        atemp = re.split(':', stday)
        year  = int(atemp[0])
        yday  = int(atemp[1])
#
#--- always update this week and the last 
#
        bweek = int(yday/7)-1
        eweek = bweek + 2
#
#--- the last week is in the last year; indicate that
#
        if bweek < 0:
            bweek = 0
            chk   = 1
    else:
        bweek = 0
        eweek = 54
#
#--- if the year changed in the last couple of weeks, make sure to (re)plot the last 2 weeks
#--- of the last year; the update of the data may not happen till the new year
#
    if chk > 0:
        [lyear, lwlist, lblist, lelist] = create_week_list(year-1, 53, 54)
        [year, wlist, blist, elist] = create_week_list(year, bweek, eweek)
        year_list = [lyear, year]

        for k in range(bweek, eweek):
            year_list.append(year)

        wlist     = lwlist + wlist
        blist     = lblist + blist
        elist     = lelist + elist
#
#--- normal time (week > 2)
#
    else:
        [year, wlist, blist, elist] = create_week_list(year, bweek, eweek)
        year_list = []

        for k in range(bweek, eweek):
            year_list.append(year)

    return [year_list, wlist, blist, elist]

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def create_week_list(year, bweek, eweek):

    sdate = str(year) + ':001:00:00:00'
    start = Chandra.Time.DateTime(sdate).secs
    stop  = start + 7 * 86400.0
    wlist = []
    blist = []
    elist = []
    for k in range(0, 54):
        if (k >= bweek) and (k < eweek):
            wlist.append(k)
            blist.append(start)
            elist.append(stop)
        start  =  stop
        stop  += 7 * 86400.0

    return [year, wlist, blist, elist]
        
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
            if mcf.is_leapyear(byear):
                base = 366
            else:
                base = 365
        if cdata[0] > byear:
            nx.append(cdata[1] + base)
        else:
            nx.append(cdata[1])

    return nx

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def adjust_year_date(byear, x):

    if mcf.is_leapyear(byear):
        base = 366
    else:
        base = 365

    nx = []
    for ent in x:
        if ent[0] != byear:
            val = float(ent[1]) + base
            nx.append(val)
        else:
            nx.append(float(ent[1]))

    return nx

#-------------------------------------------------------------------------------
#-- check_time_format: return time in Chandra time                            --
#-------------------------------------------------------------------------------

def check_time_format(intime):
    """
    return time in Chandra time
    input:  intime  --- time in <yyyy>:<ddd>:<hh>:<mm>:<ss> 
                        or <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> or chandra time
    output: yeaer   --- the year
            time in chandra time (seconds from 1998.1.1)
    """
    mc1 = re.search('-', intime)
    mc2 = re.search(':', intime)
#
#--- it is already chandra format
#
    if mcf.is_neumeric(intime):
        out   = Chandra.Time.DateTime(intime).date
        atemp = re.split(':', out)
        year  = int(atemp[0])
        return [year, int(float(intime))]
#
#--- time in <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
#
    elif mc1 is not None:
        mc2 = re.search('T', intime)
        if mc2 is not None:
            atemp = re.split('T', intime)
            btemp = re.split('-', atemp[0])
            year  = int(float(btemp[0]))
            mon   = int(float(btemp[1]))
            day   = int(float(btemp[2]))
            ctemp = re.split(':', atemp[1])
            hrs   = ctemp[0]
            mins  = ctemp[1]
            secs  = ctemp[2]
     
        else:
            btemp = re.split('-', intime)
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

        atemp = re.split(':', intime)
        year  = int(atemp[0])
        return [year, Chandra.Time.DateTime(intime).secs]

#-------------------------------------------------------------------------------
#-- select_data: select data in the range and change the time format           -
#-------------------------------------------------------------------------------

def select_data(ifile, start, stop, yd=1):
    """
    select data in the range and change the time format
    input:  ifile   --- data file name
            cut     --- the data cut time in seconds from 1998.1.1
            yd      --- indicator to create fractional year (0) or ydate (1)
    output  xdata   --- a list of time data
            ydata   --- a list of temperature data
            radata  --- a list of 1crat data
            rbdata  --- a list of 1crbt data
    """
    data   = mcf.read_data_file(ifile)
    xdata  = []
    ydata  = []
    radata = []
    rbdata = []
    for ent in data:
        try:
            atemp = re.split('\s+', ent)
            atime = float(atemp[0])
        except:
            continue 

        if atime < start:
            continue
        if atime > stop:
            break

        xdata.append(atime)
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

    xdata = convert_date_list(xdata, yd=yd)

    radata = create_moving_average(radata, 20)
    rbdata = create_moving_average(rbdata, 20)

    return [xdata, ydata, radata, rbdata]

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
    bavg  = mean(partb)

    for k in range(0, step):
        out.append(bavg)

    for k in range(0, dlen-step):
        part = data[k:k+step]
        pavg = mean(part)
        out.append(pavg)

    return out

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
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
#
#--- save the plot in png format
#
    plt.savefig('ztemp.png', format='png', dpi=200)
#
#--- close the plot
#
    plt.close('all')

    print("Data: " + str(outname))
    cmd = 'convert ./ztemp.png -trim ' + plot_dir +  outname
    os.system(cmd)
    mcf.rm_files('ztemp.png')

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
    [xmin, xmax] = range_expand(xmin, xmax)
    
    ymin = int(min(y))
    ymax = int(max(y))
    [ymin, ymax] = range_expand(ymin, ymax)

    return [xmin, xmax, ymin, ymax]

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def range_expand(amin, amax):

    diff  = amax - amin
    amax += 0.1 * diff
    amax  = int(amax)

    amin -= 0.1 * diff
    amin  = int(amin)

    return [amin, amax]

#-------------------------------------------------------------------------------
#-- convert_date_list: convert date format in the list to either fractional year or ydate
#-------------------------------------------------------------------------------

def convert_date_list(alist, yd=1):
    """
    convert date format in the list to either fractional year or ydate
    input:  list    --- a list of date
            yd      --- indicator to create fractional year (0) or ydate (1)
    output: save    --- a list of date in the new format
    """
    save = []
    for ent in alist:
        date = change_ctime_to_ydate(ent, yd=yd)
        save.append(date[1])

    return save

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
    atemp = re.split(':', date)
    year  = float(atemp[0])
    date  = float(atemp[1])
    hh    = float(atemp[2])
    mm    = float(atemp[3])
    ss    = float(atemp[4])
    date += (hh + mm / 60.0 + ss / 3600.0) /24.0

    if yd == 1:
        return [year, date]
    else:
        if mcf.is_leapyear(year):
            base = 366
        else:
            base = 365

        date = year + date /base

        return [year, date]

#-------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")

    if len(sys.argv) > 1:
        year = int(sys.argv[1])
    else:
        year = ''
        
    create_week_long_plot(year)

#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")