#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################    
#                                                                                   #
#       create_msid_pitch_plots.py: plot msid value agaist pitch                    #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Sep 30, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import numpy
import Chandra.Time
#
#--- set python environment if it is not set yet
#
if 'PYTHONPATH' not in os.environ:
    os.environ['SAK']        = "/proj/sot/ska"
    os.environ['PYTHONPATH'] = "/data/mta/Script/Python3.8/envs/ska3-shiny/lib/python3.6/site-packages:/data/mta/Script/Python3.6/lib/python3.6/site-packages"
    try:
        os.execv(sys.argv[0], sys.argv)
    except Exception:
        print('Failed re-exec:', exc)
        sys.exit(1)

import re
import Ska.engarchive.fetch as fetch

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
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import mta_common_functions     as mcf

color_table =['navy', 'blue', 'teal', 'aqua', 'lime', 'green', 'olive', 'orange',\
              'purple', 'fuchsia', 'red', 'darkred', 'darkred']

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def  create_msid_pitch_plots(switch=0):

    ifile = house_keeping + 'msid_list_pitch'
    data  = mcf.read_data_file(ifile)
    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        group = atemp[1]
        ymin  = float(atemp[2])
        ymax  = float(atemp[3])
        if switch == 0:
            create_msid_pitch_current(msid, group, ymin, ymax)
        else:
            create_msid_pitch_all_years(msid, group, ymin, ymax)

#-------------------------------------------------------------------------------------------
#-- create_msid_pitch_current: create plots from the current year for a given msid        --
#-------------------------------------------------------------------------------------------

def create_msid_pitch_current(msid, group, ymin, ymax):
    """
    create plots from the current year for a given msid
    input:  msid    --- msid
    output: png files   <msid>_<year>_range.png
                        <msid>_<year>_binned.png
    """
    out   = Chandra.Time.DateTime().date
    atemp = re.split(':', out)
    eyear = int(atemp[0])
    eyday = int(atemp[1])
#
#--- if today is still in the first few days of the year, update the last year's plot fisrt
#
    if eyday < 3:
        lyear = eyear -1
        plot_msid_pitch(msid, group, lyear, ymin, ymax)
#
#--- update this year's plot
#
    plot_msid_pitch(msid, group, eyear, ymin, ymax)

#-------------------------------------------------------------------------------------------
#-- create_msid_pitch_all_years: create plots from 1999 to current year for a given msid   --
#-------------------------------------------------------------------------------------------

def create_msid_pitch_all_years(msid, group, ymin, ymax):
    """
    create plots from 1999 to current year for a given msid
    input:  msid    --- msid
    output: png files   <msid>_<year>_range.png
                        <msid>_<year>_binned.png
    """
    out   = Chandra.Time.DateTime().date
    atemp = re.split(':', out)
    eyear = int(atemp[0])
    for year in range(1999, eyear + 1):
        plot_msid_pitch(msid, group, year, ymin, ymax)

#-------------------------------------------------------------------------------------------
#-- plot_msid_pitch: create pitchvs msid value for one year period                        --
#-------------------------------------------------------------------------------------------

def plot_msid_pitch(msid, group, year, ymin, ymax):
    """
    create pitchvs msid value for one year period
    input:  msid    --- msid to be plotted
            year    --- year for the data selection
    output: png files   <msid>_<year>_range.png
                        <msid>_<year>_binned.png
    """
    start = str(year)   + ':001:00:00:00'
    stop  = str(year+1) + ':001:00:00:00'
#
#--- extract data
#
    [t_list, a_list, min_list, avg_list, max_list] = get_msid_values(msid, start, stop)
#
#--- convert time into ydate
#
    yt_list = convert_time_format(t_list)
#
#--- create color coded list based on month
#
    c_list  = create_color_list(yt_list, year)
#
#--- a plot with color coordindated time span
#
    plot_color_coordinated_data(msid, group, year, a_list, min_list, avg_list, max_list, c_list, ymin, ymax)
#
#--- a plot with pitch angle binned data
#
    x_set   = []
    y_set   = []
    r_list  = []
    for angle in range(20, 180, 20):
        x_list  = []
        y_list  = []
        for k in range(0, len(t_list)):
            if a_list[k] >= angle and a_list[k] < angle+20:
                x_list.append(yt_list[k])
                y_list.append(avg_list[k])
        x_set.append(x_list)
        y_set.append(y_list)
        line = str(angle) + '-' + str(angle+20)
        r_list.append(line)
    
    plot_pitch_binned_data(msid, group, year, r_list, x_set, y_set, ymin, ymax)

#-------------------------------------------------------------------------------------------
#-- plot_color_coordinated_data: create time base color coded msid-pitch angle plot       --
#-------------------------------------------------------------------------------------------

def plot_color_coordinated_data(msid, group, year, a_list, min_list, avg_list, max_list, c_list, ymin, ymax):
    """
    create time base color coded msid-pitch angle plot
    input:  msid        --- msid
            year        --- year
            a_list      --- a list of pitch angle data
            min_list    --- a list of min value data
            avg_list    --- a list of avg value data
            max_list    --- a list of max value data
            c_list      --- a list of a color code of each data point
            ymin        --- a plotting range min
            ymax        --- a plotting range max
    output: <msid>_<year>_range.png
    """
    xmin  = 40
    xmax  = 180
    diff  = ymax - ymin
    ymin -= 0.2 * diff
    ymax += 0.2 * diff

    plt.close('all')
    mpl.rcParams['font.size'] = 9
    mpl.rcParams['font.weight'] =  'bold'
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
    plt.scatter(a_list, avg_list, c=c_list, s=10, linewidth=0)
#
#--- add a min-max range bar for each data point
#
    for k in range(0, len(a_list)):
        xset   = [a_list[k],   a_list[k]]
        yset   = [min_list[k], max_list[k]]
        c_code = c_list[k]
        plt.plot(xset, yset, color=c_code, marker='.', markersize='0.5', lw='1')
#
#--- label axis
#
    font = {'weight': 'bold'}
    plt.xlabel('Pitch', fontdict=font)
    plt.ylabel(msid.upper(), fontdict=font)
    plt.title('Year: ' + str(year), fontdict=font)

    ypos  = ymax - 0.03 * (ymax - ymin)
    ypos2 = ymax - 0.04 * (ymax - ymin)
    xdiff = (xmax - xmin) / 12.0
    xadd  = xdiff/10.0
    for k in range(0, 12):
        xpos = xmin + xdiff * k  + 2.00
        plt.scatter(xpos,ypos, c=color_table[k])
        xpos = xpos + xadd
        line = ': ' + mcf.change_month_format(k+1)
        text(xpos, ypos2, line, color=color_table[k])
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5 in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    odir    = web_dir + 'Pitch/' + group + '/' + msid + '/Plots/' 
    cmd     = 'mkdir -p ' + odir
    os.system(cmd)

    outname = odir + msid + '_' + str(year) + '_range.png'
    plt.savefig(outname, format='png', dpi=300, bbox_inches='tight')

#-------------------------------------------------------------------------------------------
#-- plot_pitch_binned_data: create  a pitch angle binned plot                             --
#-------------------------------------------------------------------------------------------

def plot_pitch_binned_data(msid, group, year, angles, x_set,y_set, ymin, ymax):
    """
    create  a pitch angle binned plot
    input:  msid    --- msid
            year    --- year
            angles  --- a list of groupings such as 40-60, 60-80
            x_set   --- a list of lists of time data
            y_set   --- a list of lists of msid data
            ymin    --- a min of data (min of min data set)
            ymax    --- a max of data (max of max data set)
    output: png plot --- <msid>_<year>_binned.png
    """
    xmin  = 0
    xmax  = 367
    xpos  = 30
    diff  = ymax - ymin
    ymin -= 0.2 * diff
    ymax += 0.2 * diff
    ydiff = ymax - ymin
    ypos  = ymax -0.15 * ydiff
    
    plt.close('all')
    mpl.rcParams['font.size'] = 9
    mpl.rcParams['font.weight'] =  'bold'
    plt.subplots_adjust(hspace=0.02)
    plt.subplots_adjust(wspace=0.02)
    
    tot = len(angles)
    pcnt = int(tot/2) + 1
    ynshaare = 1
#
#--- there will be 8 pannels
#
    for i in range(0, tot):
        axNam = 'ax' + str(i)
     
        j = i + 1
        if i == 0:
            line = str(pcnt) + str(2) + str(j)
        else:
            k = i % 2
            line = str(pcnt) + str(2) + str(j) + ', sharex=ax0'
     
        exec("%s = plt.subplot(%s)"   % (axNam, line))
        exec("%s.set_autoscale_on(False)" % (axNam))
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))
        exec("%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam))
        exec("%s.set_ylim(ymin=ymin, ymax=ymax, auto=False)" % (axNam))
        xdata  = x_set[i]
        ydata  = y_set[i]
#
#--- panel names
#
        p, = plt.plot(xdata, ydata,marker='.', markersize='2', lw='0')
        line = 'Pitch: ' + str(angles[i])
        text(xpos, ypos,line)
#
#--- x labels will be shown only at the bottom
#
        if i == tot -2 or i == tot -1:
            line = 'Y Date (Year: ' + str(year) + ')'
            xlabel(line)
#
#--- y labels and ticks are shown only on the left panels
#
        if i % 2 == 0:
            exec("%s.set_ylabel(msid)" % (axNam))
        else:
            exec("%s.axes.yaxis.set_visible(False)" %(axNam))
#
#--- x ticks are shown only at the bottom
#
        if i < tot-2:
            exec("%s.axes.xaxis.set_visible(False)" %(axNam))
    
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 10.0)
#
#--- save the plot in png format
#
    odir    = web_dir + 'Pitch/' + group + '/' + msid + '/Plots/' 
    cmd     = 'mkdir -p ' + odir
    os.system(cmd)

    outname = odir + msid + '_' + str(year)  +  '_binned.png'
    plt.savefig(outname, format='png', dpi=300, bbox_inches='tight')

#-------------------------------------------------------------------------------------------
#-- get_msid_values: get mean, min, and max values for each stable pitchperiods     ---
#-------------------------------------------------------------------------------------------

def get_msid_values(msid, start, stop):
    """
    get mean, min, and max values for each stable pitchperiods
    input:  msid        --- msid
            start       --- start time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop        --- stop tie in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    output: t_list      --- a list of time (middle of the stable pointing period)
            ang_list    --- a list of pitch
            min_list    --- a list of min of the periods
            avg_list    --- a list of avg of the periods
            max_list    --- a list of max of the periods
    """
#
#--- find a stable pitchperiods
#
    t_begin, t_stop, a_list = get_pitch(start, stop)
#
#--- get msid data
#
    [m_time, data] = get_data(msid, start, stop)

    dlen = len(a_list)
    t_list   = []
    ang_list = []
    min_list = []
    avg_list = []
    max_list = []
    dstart   = 1
#
#--- find the msid value in each stable pitchperiod
#
    for k in range(0, dlen):
        tstart = t_begin[k]
        tstop  = t_stop[k]
        tmid   = 0.5 * (tstart + tstop)

        save   = []
        chk    = 0
        for m in range(dstart, len(m_time)):
            ctime0 = m_time[m-1]
            ctime1 = m_time[m]
            if chk == 0 and (tstart >= ctime0) and (tstart <= ctime1):
                chk = 1
            elif chk == 1 and  (tstop >= ctime0) and (tstop <= ctime1):
                chk = 2
#
#--- if msid values are during the period, collect them
#
            if  chk == 1:
                save.append(data[m])

#
#--- all data during the period were found. take min, mean and max of the data collected
#
            elif chk == 2:
                d_min = min(save)
                d_max = max(save)
                avg   = numpy.mean(save)
                t_list.append(tmid)
                ang_list.append(a_list[k])
                min_list.append(d_min)
                avg_list.append(avg)
                max_list.append(d_max)
                chk    = 0
                save   = []
                dstart = m-2
                break

    return [t_list, ang_list, min_list, avg_list, max_list]

#-------------------------------------------------------------------------------------------
#-- get_pitch: get pitchdata                                                     --
#-------------------------------------------------------------------------------------------

def get_pitch(start, stop):
    """
    get pitchdata
    input:  start   --- start time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stop tie in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    output: t_begin --- a list of a stable pitchstarting time
            t_stop  --- a list of a stable pitchending time
            a_list  --- a list of pitch
    Note: we assume that pointing stable more than one hour while observing
    """
#
#--- pointing_suncentang has less data than pitch; so it is quicker to get the data
#--- there could be a small difference between then but probably it won't matter for
#--- mta use
#---- pitch:  54.079u 3.630s 1:49.88 52.5%     0+0k 78976+1104io 0pf+0w
#---- sunang:  8.894u 2.824s 0:22.60 51.8%     0+0k 9368+1088io 0pf+0w
#
    #[t_list, d_list] = get_data('pitch', start, stop)
    [t_list, d_list] = get_data('point_suncentang', start, stop)
    d_list = roundup(d_list)
    t_begin = []
    t_stop  = []
    a_list  = []
    tstart  = t_list[0]
    angle   = d_list[0]
    for k in range(1, len(d_list)):
        if d_list[k] == angle:
            continue
        else:
#
#--- find periods which the pitch is stable for more than one hour
#
            diff = t_list[k-1] - tstart
            if diff > 3600:
                t_begin.append(tstart)
                t_stop.append(t_list[k-1])
                a_list.append(angle)

            tstart = t_list[k]
            angle  = d_list[k]

    if t_list[-1] - tstart > 3600:
        t_begin.append(tstart)
        t_stop.append(t_list[-1])
        a_list.append(angle)

    return t_begin, t_stop, a_list

#-------------------------------------------------------------------------------------------
#-- roundup: convert the values in the list to rounded up integer                         --
#-------------------------------------------------------------------------------------------

def roundup(d_list):
    """
    convert the values in the list to rounded up integer
    input:  d_list  --- a list of data
    output: save    --- a list of modified data
    """
    save = []
    for ent in d_list:
        val = int(round(ent, 0))
        save.append(val)

    return save

#-------------------------------------------------------------------------------------------
#-- convert_time_format: convert time into ydate                                          --
#-------------------------------------------------------------------------------------------

def convert_time_format(t_list):
    """
    convert time into ydate
    input:  t_list  --- a list of time in chandra time
    output: save    --- a list of time in ydate
    """
    save = []
    for ent in t_list:

        out = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', out)
        year  = int(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])
        yday += hh /24.0 + mm /1440.0 + ss / 86400.0
        save.append(yday)

    return save

#-------------------------------------------------------------------------------------------
#-- create_color_list: create color list depending of month                               --
#-------------------------------------------------------------------------------------------

def create_color_list(t_list, year):
    """
    create color list depending of months
    input:  t_list  --- a list of data
            year    --- year of the data
    output: c_list  --- a list of color codes
    """
    if mcf.is_leapyear(year):
        base = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366, 380]
    else:
        base = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365, 380]
    c_list = []
    for ent in t_list:
        for k in range(0, 12):
            if ent >= base[k] and ent <= base[k+1]+1:
                c_list.append(color_table[k])
                break

    return c_list

#-------------------------------------------------------------------------------------------
#-- create_color_list: create color list with the shade between c1 and c2                 --
#---    CURRENTLY THIS IS NOT USED IN THIS SCRIPT AS THE SHADE ARE NOT DIVERSE ENOUGH
#---    FOR OUT PURPSOE. HOWEVER, IT COULD BE USEFUL IN THE FUTURE AND WILL BE KEPT HERE
#
#-------------------------------------------------------------------------------------------

def create_color_list_xx(t_list, c1='red', c2='green'):
    """
    create color list with the shade between c1 and c2
    input:  t_list  --- a list of data
            c1      --- a color at the beginning
            c2      --- a color at the ending
    output: c_list  --- a list of colors between red and green color
    """
    c_list = []
    tmax   = max(t_list)
    for ent in t_list:
        color = color_fader(c1, c2, ent/tmax)
        c_list.append(color)

    return c_list

#-------------------------------------------------------------------------------------------
#-- color_fader: fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)         --
#-------------------------------------------------------------------------------------------

def color_fader(c1, c2, mix=0):
    """
    fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    input:  c1  --- bottom end of color
            c2  --- top end of color
            mx  --- a value between 0 and 1 to create the shade of color
    output: color code
    """
    c1=numpy.array(mpl.colors.to_rgb(c1))
    c2=numpy.array(mpl.colors.to_rgb(c2))

    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

#-------------------------------------------------------------------------------------------
#-- get_data: extract data for msid between given start and stop times                    --
#-------------------------------------------------------------------------------------------

def get_data(msid, start, stop):
    """
    extract data for msid between given start and stop times
    input:  msid    --- msid
            start   --- start time
            stop    --- stop time
    output: ttime   --- a list of time data
            tdata   --- a list of data
    """
#
#--- extract data from archive
#
    chk = 0
    try:
        out     = fetch.MSID(msid, start, stop)
        tdata   = out.vals
        ttime   = out.times
    except:
        tdata   = []
        ttime   = []


    return [ttime, tdata]

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        switch = 1
    else:
        switch = 0

    create_msid_pitch_plots(switch)

