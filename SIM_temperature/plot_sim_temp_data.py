#!/proj/sot/ska3/flight/bin/python

#####################################################################################
#                                                                                   #
#   plot_sim_temp_data.py: plot sim temperature related plots                       #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Jul 19, 2023                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import numpy
import time
import matplotlib as mpl
if __name__ == '__main__':
    mpl.use('Agg')
from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
import matplotlib.gridspec     as gridspec
import getpass
#
#--- reading directory list
#
path = '/data/mta/Script/SIM/Scripts/house_keeping/dir_list'

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
sys.path.append(bin_dir)
sys.path.append("/data/mta4/Script/Python3.10/MTA/")
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
import robust_linear        as robust
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

colorList  = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')

#---------------------------------------------------------------------------------------------------
#-- create_sim_temp_plots: control function to run sim temperature trending plots etc            ---
#---------------------------------------------------------------------------------------------------

def create_sim_temp_plots(start, stop):
    """
    control function to run sim temperature trending plots etc
    input:  start   --- starting year
            stop    --- stopping year
                if they are the same, it will cerate the plot for the year
                else, it will create the entire range (from 1999 to current)
    output: plots in <web_dir>/Plots/
                sim_temp_<year>.png
                sim)translation_<year>.png
    """
#
#--- check whether to create  full range or indivisual year plots
#
    if stop - start > 1:
        fname = web_dir + 'Plots/sim_temp_fullrange.png'
        oname = web_dir + 'Plots/sim_translation_fullrange.png'
        title = str(start) + ' - ' + str(stop-1)
        yind  = 0
    else:
        fname = web_dir + 'Plots/sim_temp_' + str(start) + '.png'
        oname = web_dir + 'Plots/sim_translation_' + str(start) + '.png'
        title = 'Year: ' + str(start)
        yind  = 1
        if mcf.is_leapyear(start):
            base = 366
        else:
            base = 365
#
#--- read sim temperature data file
#
    ifile = data_dir + 'tsc_temps.txt'
    data  = mcf.read_data_file(ifile)

    x     = []
    ts    = []
    te    = []
    delta = []
    steps = []

    for ent in data[1:]:
        atemp = re.split('\s+', ent)

        try:
            time  = convert_to_fyear(atemp[0])
            if time < start:
                continue
            if time > stop:
                break
            if yind == 1:
                time = (time - start) * base

            t1    = float(atemp[2])
            t2    = float(atemp[3])
            t3    = t2 - t1
            t4    = float(atemp[5])

            if t1 > 60 or t1 < -40:
                continue
            if t2 > 60 or t2 < -40:
                continue
            x.append(time)          #--- time in year or yday
            ts.append(t1)           #--- sim temperature at the beginning
            te.append(t2)           #--- sim temperature at the ending
            delta.append(t3)        #--- the sim temperature difference 
            steps.append(t4)        #--- the number of steps
        except:
            continue

#
#--- run moving average
#
    mvstep = 30 
    [mxs, mys] = smooth_data(x, ts, mvstep)
    if len(mxs) == 0:
        skip = 1
    else:
        skip = 0

    [mxe, mye] = smooth_data(x, te, mvstep)
    if len(mxe) == 0:
        skip = 1
    else:
        skip = 0

#
#--- read pitch angle data
#
    ifile = '/data/mta/DataSeeker/data/repository/orb_angle.rdb'
    data  = mcf.read_data_file(ifile)

    stime = []
    angle = []

    m      = 0
    for ent in data[2:]:
        atemp = re.split('\s+', ent)
        try:
            time  = mcf.chandratime_to_fraq_year(float(atemp[0]))
            if time < start:
                continue
            if time > stop:
                break

            if yind == 1:
                time = (time - start) * base
#
#--- just take the data every 20 mins or so (data is taken every 300 sec)
#
            if m % 4 == 0:
                stime.append(time)
                angle.append(float(atemp[1]))
            m += 1
        except:
            continue
#
#--- if yind == 0, full range, otherwise, year plot
#
    if yind == 0:
        xmin = start
        xmax = stop 
        tdff = 1.0e-5
    else:
        xmin = 1
        xmax = base
        tdff = 3.5e-3
#
#--- plot time tred of sim temperature
#
    plot_sim_temp_data(xmin, xmax, x, ts, te, mxs, mys, mxe, mye,\
                       delta, stime, angle, fname, yind, title, skip)
#
#--- plot translation step - delta sim temperature
#
    plot_step_delta(steps, delta, oname, title)

#---------------------------------------------------------------------------------------------------
#-- convert_to_fyear: convert sim temp database time format to fractional year                   ---
#---------------------------------------------------------------------------------------------------

def convert_to_fyear(val):
    """
    convert sim temp database time format to fractional year
    input:  val     --- sim temp time  
    output: fyear   --- fractional year e.g. 2014.11345
    """

    v    = str(val)
    year = v[0]  + v[1] + v[2] + v[3]
    year = float(year)
    yday = v[4]  + v[5] + v[6]
    yday = float(yday)
    hh   = v[7]  + v[8]
    hh   = float(hh)
    mm   = v[9]  + v[10]
    mm   = float(mm)
    ss   = v[11] + v[12]
    ss   = float(ss)

    if mcf.is_leapyear(year):
        base = 366
    else:
        base = 365

    fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base

    return fyear

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def smooth_data(x, y, period):

    xs = []
    ys = []
    k  = 0
    hp = int(0.5 * period)
    last = len(x) - hp
    for i in range(0, len(x)):
        if i < hp:
            continue
        if i >= last:
            break

        sum = 0
        for j in range(i-hp, i + hp):
            sum += y[j]
        val = sum / period
        if val > 50 or val < -20:
            val = ys[-1]
        xs.append(x[i])
        ys.append(val)

    return [xs, ys]

#---------------------------------------------------------------------------------------------------
#-- plot_sim_temp_data: plot  sim trend, temp delta, and pitch angle trends                      ---
#---------------------------------------------------------------------------------------------------

def plot_sim_temp_data(xmin, xmax, simtx, simtl, simth, mxs, mys, mxe, mye,\
                       delta, stime, angle, outname, yind, title,skip):
    """
    plot  sim trend, temp delta, and pitch angle trends
    Input:  xmin    --- starting date, either in year or yday
            xmax    --- ending date, either in year or yday
            simtx   --- time in either year or yday
            simtl   --- starting sim temperature
            simth   --- ending sim temperature
            mxs     --- moving average time
            mys     --- moving average of simtl
            mye     --- moving average of simth
            delta   --- <sim ending temp> - <sim starting temp>
            stime   --- time in either year or yday of picthc angle data
            angle   --- pitch angle
            outname --- output file name
            yind    --- whether this is a full range plot or yearly plot
            title   --- title of the plot
            skip    --- if 1, skip moving averge plots
    Output: png plot named <outname>
    """
#
#--- several setting for plotting
#
    fsize      = 14         #--- font size
    fweight    = 'bold'     #--- font weight
    psize      = 3.0        #--- plotting point size
    marker     = '.'        #--- marker shape
    pcolor     = 7          #--- color of the point
    lcolor     = 4          #--- color of the fitted lin
    lsize      = 3.0        #--- fitted line width
    resolution = 300        #--- the resolution of the plot
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size']  = fsize
    mpl.rcParams['font.weight'] = fweight
    mpl.rcParams['axes.linewidth'] = 2
    #set(0,'defaultlinelinewidth',8)
    props = font_manager.FontProperties(size=12)
    plt.subplots_adjust(hspace=0.05)

#
#--- set grid to 3 rows or height rtio 3:1:1
#
    gs = gridspec.GridSpec(3,1,height_ratios=[3,1,1])
#
#
#--- first panel: moter temperature trend  ------------------------------
#
#
#---- set ymin and ymax
#
    ymin = -40
    ymax =  60
#
#--- set plotting range
#
    #plt.subplot(311)
    ax0 = plt.subplot(gs[0])
    line = ax0.get_xticklabels()
    for label in line:
        label.set_visible(False)

    xlim((xmin,xmax))
    ylim((ymin,ymax))
#
#--- plot data
#
    plt.plot(simtx, simtl, color=colorList[0], marker=marker, markersize=psize, lw = 0)
    plt.plot(simtx, simth, color=colorList[2], marker=marker, markersize=psize, lw = 0)


    for i in range (0, len(simtx)):
        xset = [simtx[i], simtx[i]]
        yset = [simtl[i], simth[i]]
        plt.plot(xset, yset, color=colorList[3], marker='', markersize=0, lw = 1)

#
#--- plot moving average
#
    if skip == 0:
        plt.plot(mxs, mys, color=colorList[0],  marker='', markersize=0, lw=2)
        plt.plot(mxe, mye, color=colorList[2],  marker='', markersize=0, lw=2)
#
#--- add what is plotted on this plot
#
    xdiff = xmax - xmin
    xpos  = xmin + 0.05 * xdiff
    ydiff = ymax - ymin
    ypos1 = ymax - 0.08 * ydiff
    ypos2 = ymax - 0.12 * ydiff
    xpos3 = xmax - 0.20 * xdiff
    ypos3 = ymax + 0.005 * ydiff
    xpos4 = xmin + 0.05 * xdiff

    val1  = numpy.mean(simtl)
    val1  = '%2.2f' %round(val1, 2)
    val2  = numpy.mean(simth)
    val2  = '%2.2f' %round(val2, 2)

    label = 'T Stop Average:  ' + str(val2) + ' $^o$C'
    plt.text(xpos, ypos1, label, size=fsize, color=colorList[2])

    label = 'T Start Average: ' + str(val1) + ' $^o$C'
    plt.text(xpos, ypos2, label, size=fsize, color=colorList[0])

    plt.text(xpos3, ypos3, title, size=fsize)
    plt.text(xpos4, ypos3, 'SIM TSC Motor Temperatures', size=fsize)
#
#--- label axes
#
    yname = 'TSC Motor Temp ($^o$C)'
    plt.ylabel(yname, size=fsize, weight=fweight)
#
#
#--- second panel: temperature delta trend   -----------------------------
#
#
#--- set plotting range
#
    ymin = -20
    ymax =  20
    #plt.subplot(312)
    ax1 = plt.subplot(gs[1])
    line = ax1.get_xticklabels()
    for label in line:
        label.set_visible(False)

    xlim((xmin,xmax))
    ylim((ymin,ymax))
#
#--- plot data
#
    plt.plot(simtx, delta, color=colorList[0], marker=marker, markersize=3, lw = 0)
#
#--- fit line --- use robust method
#
    (sint, slope, serr) = robust.robust_fit(simtx, delta)
    lslope = '%2.3f' % (round(slope, 3))
#
#--- plot fitted line
#
    start = sint + slope * xmin
    stop  = sint + slope * xmax
    plt.plot([xmin, xmax], [start, stop], color=colorList[lcolor], lw = lsize)
#
#--- add what is plotted on this plot
#
    xdiff = xmax - xmin
    xpos  = xmin + 0.1 * xdiff
    ydiff = ymax - ymin
    ypos  = ymin + 0.10 * ydiff

    label = 'Slope:  ' + str(lslope)

    plt.text(xpos, ypos, label, size=fsize)
#
#--- label axes
#
    yname = '$\Delta$ T ($^o$C)'
    plt.ylabel(yname, size=fsize, weight=fweight)

#
#--- third panel: pitch angle trend       -------------------------------
#
#--- set plotting range
#
    ymin =  0
    ymax =  180
    #plt.subplot(313)
    plt.subplot(gs[2])
    xlim((xmin,xmax))
    ylim((ymin,ymax))
#
#--- plot data
#
    plt.plot(stime, angle, color=colorList[4], marker='', markersize=0, lw = 0.5)
#
#--- label axes
#
    yname = 'Pitch Angle'
    plt.ylabel(yname, size=fsize, weight=fweight)


#
#--- label  x axis
#
    if yind == 0:
        xname = 'Time (year)'
    else:
        xname = 'Time (yday)'

    plt.xlabel(xname, size=fsize, weight=fweight)
#
#
#--- set the size of the plotting area in inch (width: 10.0in, height 15 in)
#
    fig = matplotlib.pyplot.gcf()

    fig.set_size_inches(10.0, 15.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)



#---------------------------------------------------------------------------------------------------
#-- plot_step_delta: plot a single data set on a single panel                                    ---
#---------------------------------------------------------------------------------------------------

def plot_step_delta(steps, delta, outname, title):

    """
    plot a single data set on a single panel
    Input:  steps   --- translation steps
            delta   --- sim temperature difference before and after translation
            outname --- the name of output file
            title   --- title of the plot
    Output: png plot named <outname>
    """
    fsize      = 14         #--- font size
    fweight    = 'bold'     #--- font weight
    psize      = 3.0        #--- plotting point size
    marker     = '.'        #--- marker shape
    pcolor     = 7          #--- color of the point
    lcolor     = 4          #--- color of the fitted lin
    lsize      = 3.0        #--- fitted line width
    resolution = 300        #--- the resolution of the plot
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size']  = fsize
    mpl.rcParams['font.weight'] = fweight
    mpl.rcParams['axes.linewidth'] = 2
    #set(0,'defaultlinelinewidth',8)
    props = font_manager.FontProperties(size=12)
    plt.subplots_adjust(hspace=0.05)

    [xmin, xmax, ymin, ymax ] =  set_min_max(steps, delta)
    ymin = -5
    ymax = 20
#
#--- set plotting range
#
    plt.subplot(111)
    xlim((xmin,xmax))
    ylim((ymin,ymax))
#
#--- plot data
#
    plt.plot(steps, delta, color='fuchsia', marker='*', markersize=psize, lw = 0)
#
#--- fit line --- use robust method
#
    (sint, slope, serr) = robust.robust_fit(steps, delta)
    lslope = '%2.3f' % (round(slope * 10000, 3))
#
#--- plot fitted line
#
    start = sint + slope * xmin
    stop  = sint + slope * xmax
    plt.plot([xmin, xmax], [start, stop], color=colorList[lcolor], lw = lsize)

    label = 'Slope:  ' + str(lslope)  + ' ($^o$C / 10$^4$ steps)'
#
#--- add what is plotted on this plot
#
    xdiff = xmax - xmin
    xpos  = xmin + 0.05 * xdiff
    ydiff = ymax - ymin
    ypos  = ymax - 0.10 * ydiff
    xpos3 = xmax - 0.20 * xdiff
    ypos3 = ymax + 0.005 * ydiff
    xpos4 = xmin + 0.05 * xdiff

    plt.text(xpos, ypos, label, size=fsize)
#
#--- label axes
#
    yname = '$\Delta$ T ($^o$C)'
    plt.ylabel(yname, size=fsize, weight=fweight)
#
#--- label  x axis
#
    xname = 'Translation Steps'

    plt.xlabel(xname, size=fsize, weight=fweight)
#
#--- title
#
    plt.text(xpos3, ypos3, title, size=fsize)
    plt.text(xpos4, ypos3, 'TSC Motor Temp vs. Move Distance', size=fsize)
#
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5 in)
#
    fig = matplotlib.pyplot.gcf()

    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)

#---------------------------------------------------------------------------------------------------
#-- set_min_max: set plotting range                                                              ---
#---------------------------------------------------------------------------------------------------

def set_min_max(xdata, ydata, xtime = 0, ybot = -999):

    """
    set plotting range
    Input:  xdata   ---- xdata
            ydata   ---- ydata
            xtime   ---- if it is >0, it set the plotting range from 1999 to the current in year
            ybot    ---- if it is == 0, the ymin will be 0, if the ymin computed is smaller than 0
    Output: [xmin, xmax, ymin, ymax]
    """

    xmin  = min(xdata)
    xmax  = max(xdata)
    xdiff = xmax - xmin
    xmin -= 0.1 * xdiff
    xmax += 0.2 * xdiff

    if xtime > 0:
        xmin  = 1999
        tlist = int(foloat(time.strftime('%Y', time.gmtime())))
        xmax  = tlist[0] + 1

    ymin  = min(ydata)
    ymax  = max(ydata)
    ydiff = ymax - ymin
    ymin -= 0.1 * ydiff
    ymax += 0.2 * ydiff

    if ybot == 0:
        if ymin < 0:
            ymin = 0

    return [xmin, xmax, ymin, ymax]

#-------------------------------------------------------------------------------------------------

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
#
#--- if you give start = stop = <year>
#--- it will create the plot for the <year>
#

    if len(sys.argv) > 1:
        year  = int(float(sys.argv[1]))
        start = year
        stop  = year + 1

    else:
#
#--- find today's date
#
        today = time.localtime()
        year  = int(float(today.tm_year))
        start = 1999
        stop  = year + 1

    create_sim_temp_plots(start, stop)
#
#--- if the entire range update is asked, the plot
#--- for the latest year also needs to be updated
#
    if stop > start+1:
        create_sim_temp_plots(stop-1, stop)
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")
    sys.exit()
