#!/proj/sot/ska3/flight/bin/python
#####################################################################################
#                                                                                   #
#       create_trend_plot.py: create trend plot                                     #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 15, 2021                                               #
#                                                                                   #
#####################################################################################

import sys
import os
import string
import re
import numpy
import os.path
import time
import math
import astropy.io.fits  as pyfits
import Chandra.Time
from copy import deepcopy
import argparse
import getpass
from datetime import date
DAYS = ['mon', 'tus','wed', 'thu', 'fri', 'sat', 'sun']
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

#path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
path = '/data/mta4/testTrend/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

bin_dir = './'

sys.path.append("/data/mta4/Script/Python3.10/MTA")
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
import read_limit_table         as rlt  #---- read limit table and craete msid<--->limit dict
import create_html_suppl        as chs
#
#--- set several values used in the plots
#
color_table  = ['blue', 'red', '#FFA500']
marker_table = ['s',   '*',    '^',     'o']
marker_size  = [50,    80,     70,      50]
#
#---  get dictionaries of msid<-->unit and msid<-->description
#
[udict, ddict] = ecf.read_unit_list()

#-----------------------------------------------------------------------------------
#-- create_msid_plots: create trend and derivative plots                          --
#-----------------------------------------------------------------------------------

def create_msid_plots(msid_file='', dtype=''):
    """
    create trend plots
    input:  msid_file   --- a file name of a msid list
            dtype       --- data type : week, short, long
    output: <web_dir>/<Group>/<Msid>/Plots/<msid>_<dtype>_<mtype>_<state>.png
    """
#
#--- today's time in Chandra Format (at 0 hr)
#
    global today
    today     = today_date_chandra()
    global this_year
    this_year = float(time.strftime('%Y', time.gmtime()))
#
#--- get msid list
#
    if msid_file == '':
        ifile = house_keeping + 'msid_list_all'
    else:
        ifile = house_keeping + msid_file
        if not os.path.isfile(ifile):
            ifile = house_keeping + 'msid_list_all'

    data      = mcf.read_data_file(ifile)
    msid_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        msid_list.append(atemp[0].strip())
#
#--- set which data type and which data group to run
#
    if dtype == '':
        r_list = ['week', 'short', 'long']
    else:
        if isinstance(dtype, list):
            r_list = dtype
        else:
            r_list = [dtype]
#
#--- create msid <---> group dict
#
    group_dict = create_group_dict()
#
    [limit_dict, cnd_dict] = rlt.get_limit_table()
#
#--- run for each msid
#
    chk = 0
    for msid in msid_list:
#
#--- find which group msid belongs
#--- get the limit data table for the msid
#
        try:
            group    = group_dict[msid]
            lim_data = limit_dict[msid]
        except:
            print("No limit data for: " + msid)
            continue
#
#--- extract data for the given period
#--- pdata = [<time list>, <mid list>, <min list>, <max list>, <color list>, <limt pos list>]
#
        for dtype in r_list:
            print("Running: " + msid + ' : ' + dtype)
            try:
                pdata = read_trend_data(msid, group, dtype)
                if pdata == False:
                    continue

            except:
                print("MSID: " + msid + ' : ' + dtype + ' plots was not created')
                continue
            print("I AM HERE:" + str(len(pdata[0])))
#
#--- if there are not enough data, don't make a plot
#
            if len(pdata[0]) < 1:
                continue

            if dtype != 'week':
                if len(pdata[0]) < 10:
                    continue
#
#--- some 'dtype' has more than one plot to make
#
            if dtype == 'week':
                d_list = ['week',]

            elif dtype == 'short':
                d_list = ['short', 'year']

            else:
                d_list = ['five', 'long']

            for dtype in d_list:
#
#--- cut the data for an appropriated period
#
                [mpdata, byear] = select_data_for_time_period(pdata, dtype)
                print("I AM HERE2: " + str(len(mpdata[0])) + '<-->' + str(byear))
#
#--- creating trending plot
#
                xxx = 999
                if xxx == 999:
                #try:
                    trend_dict = prep_plot_and_plot(mpdata, byear, msid, group, dtype, lim_data, udict)
                else:
                #except:
                    print("Plot failed: " + str(msid) )
                    continue
                print("I AM HERE PLOTTED")
#
#--- creating derivative plot
#
                dev_dict   = create_derivative_plots(mpdata, byear,  msid, group, dtype, udict)
                print("I AM HERE DEV")
#
#--- print out the fitted results
#
#
#--- first read the past data
#
                ofile = web_dir + group.capitalize() + '/' + msid.capitalize() 
                ofile = ofile   + '/Plots/' + msid + '_fit_results'
                data  = mcf.read_data_file(ofile)
                dlen  = len(data)
                print("I AM HERE 1")

                save  = []
                for mtype in ['mid', 'min', 'max']:
                    tout = trend_dict[mtype]
                    dout = dev_dict[mtype]
                    states = tout[0]
                    for state in states:
#
#--- combine stat results from trend fitting and deviation fitting
#
                        tline = tout[1][state]
                        try:
                            dline = dout[1][state]
                        except:
                            dline = '0.0:0.0:0.0'
                        rline = dtype + ':' + mtype + ':' + state 
                        dline = rline + '#'+ tline + ':' + dline 
                        chk   = 0
#
#--- compare the data type etc and replace the past data with the new one
#
                        for k in range(0, dlen):
                            atemp = re.split('#', data[k])
                            if atemp[0] == rline:
                                data[k] = dline
                                chk = 1
                                break
#
#--- if there is no past data keep it 
#
                        if chk == 0:
                            save.append(dline)

#
#--- there is a new type of data, append to the updated data set
#
                if len(save) > 0:
                    data = data + save
#
#--- print out the updated data set
#
                with open(ofile, 'w') as fo:
                    for ent in data:
                        fo.write(ent + '\n')

#--------------------------------------------------------------------------------
#-- read_trend_data: read the data of msid                                     --
#--------------------------------------------------------------------------------

def read_trend_data(msid, group,  dtype):
    """
    read the data of msid
    input:  msid--- msid
        group   --- group name
        dtype   --- data type: week, short, year, five, long
    output: pdata   --- a two dimensional array  of data
            xtime  = pdata[0]
            dnum   = pdata[1]
            avg    = pdata[4]
            med    = pdata[5]
            std    = pdata[6]
            dmin   = pdata[7]
            dmax   = pdata[8]
            state  = pdata[9]
    """
#
#--- with week data, only one week plot
#
    if dtype == 'week':
        dfile = data_dir + group.capitalize() + '/' + msid + '_week_data.fits'
#
#--- for short, we create 3 months and one year plots
#
    elif dtype  == 'short':
        dfile = data_dir + group.capitalize() + '/' + msid + '_short_data.fits'
#
#--- long data is for 5 yrs and full range
#
    else:
        dfile = data_dir + group.capitalize() + '/' + msid + '_data.fits'

    try:
        pdata  = read_msid_data(dfile, msid, dtype)
        return pdata
    except:
        return False

#-----------------------------------------------------------------------------------
#-- read_msid_data: extract data from fits file                                    ---
#-----------------------------------------------------------------------------------

def read_msid_data(dfile, msid, dtype):
    """
    extract data from fits file
    input;  dfile   --- data file name
            msid    --- column name: msid
            dtype   --- data type: week, short, long
    output: a list of lists of <time>, <col values>, <min values>, <max values>, 
                               <color list>, <color ind>,<state>
    """
#
#--- open fits file and select data 
#
    hdout = pyfits.open(dfile)
    data  = hdout[1].data
#
#--- get the data needed
#
    dtime     = data['time']
    col_vals  = data[msid]
    min_vals  = data['min']
    max_vals  = data['max']
    states    = data['state']
#
#--- rate of the data was in yellow/red warning/violation range
#
    ylow  = data['ylower']
    ytop  = data['yupper']
    rlow  = data['rlower']
    rtop  = data['rupper']
#
#--- if the data was more than 30% of time in the warning/violation area, 
#--- set the color of the data to yellow/red. otherwise, set the color to blue
#
    c_list = []
    c_ind  = []
    for k in range(0, len(dtime)):
        if rlow[k] > 0.3:
            c_list.append('red')
            c_ind.append('rl')

        elif rtop[k] > 0.3:
            c_list.append('red')
            c_ind.append('rt')

        elif ylow[k] > 0.3:
            c_list.append('orange')
            c_ind.append('yl')

        elif ytop[k] > 0.3:
            c_list.append('orange')
            c_ind.append('yt')

        else:
            c_list.append('blue')
            c_ind.append('c')
#
#--- make sure that the value is in float
#
    dtime    = (numpy.array(dtime)).astype(float)
    col_vals = (numpy.array(col_vals)).astype(float)
    min_vals = (numpy.array(min_vals)).astype(float)
    max_vals = (numpy.array(max_vals)).astype(float)

    return [dtime, col_vals, min_vals, max_vals, c_list, c_ind, states]

#-----------------------------------------------------------------------------------
#-- create_group_dict: create msid <---> category dictionary                   --
#-----------------------------------------------------------------------------------

def create_group_dict():
    """
    create msid <---> category dictionary
    input:  none, but read from <house_keeping>/msid_list
    output: catg_dict
    """
    ifile = house_keeping + 'msid_list_all'
    data  = mcf.read_data_file(ifile)

    catg_dict = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        catg_dict[atemp[0].strip()] = atemp[1].strip()

    return catg_dict

#--------------------------------------------------------------------------------
#-- today_date_chandra: get today's time (0 hr) in seconds from 1998.1.1      ---
#--------------------------------------------------------------------------------

def today_date_chandra():
    """
    get today's time (0 hr) in seconds from 1998.1.1
    input:  none
    output: stime   --- today's date (0 hr) in seconds from 1998.1.1
    """
    t_day = time.strftime('%Y:%j:00:00:00', time.gmtime())
    stime = Chandra.Time.DateTime(t_day).secs
    
    return stime

#-----------------------------------------------------------------------------------
#-- set_limit_ranges: create lower/upper warning/red violation area boxes for plotting
#-----------------------------------------------------------------------------------

def set_limit_ranges(ltable, xmax, dtype):
    """
    create lower/upper warning/red violation area boxes for plotting
    input:  ltable: limit table (see blow)
            dtype   --- data type: week, short, year, five, or long
    output: boxes   --- a list of warning/violation areas (see blow)
            byear   --- the base year

     ltable = [
      [<period start time>, <period end time>, y_low, y_top, r_low, r_top], ...
     ]

     boxs = [[ [<period start time>, <period end time>],
               [<lower red area bottom boundary>,    <lower red area top boundary>],
               [<lower yellow area bottom boundary>, <lower yellow area top boundary>],
               [<upper yellow area bottom boundary>, <upper yellow area top boundary>],
               [<upper red area bottom boundary>,    <upper red area top boundary>]
             ],...
            ]
    """
    if dtype == 'week':
        cut = today - 10 * 86400
    elif dtype == 'short':
        cut = today - 100 * 86400
    elif dtype == 'year':
        cut = today - 365 * 86400
    elif dtype == 'five':
        cut = today - 365 * 6 * 86400
    else:
        cut = 0
    
    box_save = []
    for k in range(0, len(ltable)):
#
#--- find limit ranges in the given time period
#
        stime = ltable[k][0]
        etime = ltable[k][1]
        if etime > cut:
#
#--- set the time periods in an appropriate format (either ydate or fractional year)
#
            if stime < cut:
                atime = cut
            else:
                atime = stime

            [syear, syday, base]  = get_year_yday_from_chandra(atime)
            [eyear, eyday, ebase] = get_year_yday_from_chandra(etime)
            if dtype in ['week', 'short', 'year']:
                stime = syday
                etime = eyday + base * (eyear - syear)
            else:
                stime = syear + syday / base
                etime = eyear + eyday / ebase
             
            trange = [stime, etime]
            y_lims = [ltable[k][2][0], ltable[k][2][1]]       #--- yellow lower/upper
            r_lims = [ltable[k][2][2], ltable[k][2][3]]       #--- red lower/upper
#
#--- create boxed area for lower/upper yellow/red violations
#
            out = set_violation_range(y_lims, r_lims)

            sout = [trange]
            for ent in out:
                sout.append(ent)
    
            box_save.append(sout)

    sout = box_save[-1]
    sout[0][1]   = xmax
    box_save[-1] = sout

    return [box_save, syear]

#-----------------------------------------------------------------------------------
#-- set_violation_range: set violation ranage list                                --
#-----------------------------------------------------------------------------------

def set_violation_range(y_lims, r_lims):
    """
    set violation ranage list
    input:  y_lim   --- a list of yellow limits
            r_lim   --- a list of red limits
    ouput:  [r_low_box, y_low_box, y_top_box, r_top_box]
            each list contains: [[<lower boundary>, <upper boundary>]...]
    """
#
#--- set red violation areas
#
    r_low_box = [-9999999.0, r_lims[0]]
    r_top_box = [r_lims[1], 9999999.0]
#
#--- set yellow violation areas
#
    y_low_box = [r_lims[0], y_lims[0]]
    y_top_box = [y_lims[1], r_lims[1]]

    return [r_low_box, y_low_box, y_top_box, r_top_box]
            
#-----------------------------------------------------------------------------------
#-- prep_plot_and_plot: prepare and plot for three plots for each state of the given msid
#-----------------------------------------------------------------------------------

def prep_plot_and_plot(pdata, byear, msid, group, dtype, lim_data, udict):
    """
    prepare and plot for three plots for each state of the given msid
    input:  pdata   --- a list of lists of data:
                [<time list>, <mid list>, <min list>, <max list>, <color list>, <limt pos list>]
            byear   --- a base year; used for week, short, and one year plots
            msid    --- msid
            group   --- group of misd
            dtype   --- week, short, one, five or long
            lim_data--- a list of lists of limts
                [
                    <period start time>, <period end time>, cnd_msid, 
                    <possibe key lists>, <limit dictonary: key <--> [y_low, y_top, r_low, r_top]
                ]
            udict   --- a dictionary of unit
    output:<plot_dir>/<msid>_<data typep>_<mtype>_<state>.png
    """
    m_list = ['mid', 'min', 'max']
    plen   = len(pdata)
#
#--- state list: short and five has smaller time period; so make sure to select
#--- state in that period
#
    if dtype in ['short', 'five']:
        if dtype == 'short':
            scut = 90.0             #--- 90 day
        else:
            scut = 5.0              #--- 5 years

        [xt, yt, st] =  cut_the_data(pdata[0], pdata[1], pdata[-1], scut)

        states = list(set(st))
    else:
        states = list(set(pdata[-1]))
#
#--- select data for each data state
#
    trend_dict = {}
    s_dict     = {}
    for mtype in m_list:
        trend_dict[mtype] = [states, {}]
    for state in states:
        odata = []
        ind = pdata[-1] == state
        for k in range(0, plen):
            sdata  = numpy.array(pdata[k])[ind]
            odata.append(sdata)

        if len(odata[0]) < 1:
            continue
#
#--- create plots of mid, min, and max data
#
        x = odata[0]                        #--- time

        if dtype == 'short':
            if x[-1] >= 450:
                if mcf.is_leapyear(byear):
                    base = 366
                else:
                    base = 365
                xa = numpy.array(x)
                x  = list(xa - base)

        c_list = odata[-3]                  #--- color assigned for the data
        c_ind  = odata[-2]                  #--- the data location in the warning area
        for k in range(0, 3):
            mtype  = m_list[k]
            y      = odata[k+1].astype(float)
        
            stat_results = plot_data(x, y, c_list, c_ind, byear, msid, dtype, \
                                     mtype, group, state, lim_data, udict)
            [stemp, s_dict]   = trend_dict[mtype]
            s_dict[state]     = stat_results
            trend_dict[mtype] = [states, s_dict]

    return trend_dict

#-----------------------------------------------------------------------------------
#-- select_data_for_time_period: select data for an appropriate time period and convert time format
#-----------------------------------------------------------------------------------

def select_data_for_time_period(ipdata, dtype):
    """
    select data for an appropriate time period and convert time format
    input:  pdata   --- a list of lists of data. the first entry is time
            dtyep   --- data type, week, short, year, five, long
    output: odata   --- converted list of lists
            byear   --- base year
    """
    pdata = deepcopy(ipdata)
#
#--- for the week data, convert time into yday
#
    if dtype == 'week':
        cut            = today - 8 * 86400
        odata          = pdata_cut(pdata, cut)
        [ctime, byear] = convert_time_format(odata[0], dtype)
        odata[0] = ctime
#
#--- for the five and long, convert time into year
#
    elif dtype in ['five','long']:
        odata  = deepcopy (pdata)
        [ctime, byear] = convert_time_format(odata[0], dtype)
        odata[0] = ctime
#
#--- for five, trim the data to the last 6 years
#
        if dtype == 'five':
            cut = this_year - 6.0
            odata = pdata_cut(odata, cut)
        else:
            cut = this_year - 100.0
            odata = pdata_cut(odata, cut)

#
#--- for short and year, convert time in yday and trim them appropriate length
#
    else:
        if dtype == 'short':
                cut = today - 140 * 86400
        elif dtype == 'year':
                cut = today - 365 * 86400
        odata          = pdata_cut(pdata, cut) 
        [ctime, byear] = convert_time_format(odata[0], dtype)
        odata[0]       = ctime
    
    return [odata, byear]

#-----------------------------------------------------------------------------------
#-- pdata_cut: trim data for given cut time to present                            --
#-----------------------------------------------------------------------------------

def pdata_cut(pdata, cut):
    """
    trim data for given cut time to present
    input:  pdata   --- a list of lists of data. the first entry is time set
    output: pdata   --- an updated list of lists
    """
    ind = 0
    x   = numpy.array(pdata[0]).astype(float)
    for k in range(0, len(pdata[0])):
        if x[k] <= cut:
            continue
        else:
            ind = k
            break

    for k in range(0, len(pdata)):
        pdata[k] = pdata[k][ind:]

    return pdata

#-----------------------------------------------------------------------------------
#--- plot_data: plot data                                                        ---
#-----------------------------------------------------------------------------------

def plot_data(dtime, vals, c_list, c_ind, byear, msid, dtype, mtype, group, state, lim_data, udict):
    """
    plot data
    input:  dtime       --- a list of x data
            vals        --- a list of y data
            c_list      --- a list of color data
            c_ind       --- a list of position of data regrad of warning area
            byear       --- a base year (used for week, short, and year)
            msid        --- msid
            dtype       --- data type week, short, year, five and year
            mtype       --- min, max, avg set indicaor
            group       --- group of msid belogs
            state       --- data state
            lim_data    --- a list of warning ranges (see: prep_plot_and_plot)
            udict       --- a dictionary of units
    output:<plot_dir>/<msid>_<data typep>_<mtype>_<state>.png
    """
#
#--- get limit data for the state
#---     ltable = [
#---       [<period start time>, <period end time>, y_low, y_top, r_low, r_top], ...
#---              ]
#
    ltable = make_limit_table(lim_data, state)
#
#--- drop extreme values from both sides
#
    [cdtime, cvals] = drop_extreme(dtime, vals)
#
#--- set plotting range
#
    [xmin, xmax, ymin, ymax] = set_plot_range(cdtime, cvals, dtype)
#
#--- some occasion, the data is totally flat; if that is the case, modify the limits
#
    if ymin == ymax:
        lim_out = ltable[-1][2]
        if lim_out[1] >= 9999997.0:
            if ymin == 0:
                ymin = -1
                ymax =  1
            else:
                add = abs(ymin)
                ymin -= add
                ymax += add
        else:
            ymin = lim_out[0]
            ymax = lim_out[1]
#
#--- reduce the data so that there are about 600 data points to plot
#
    [mdtime, mvals, mc_list, mc_ind] = shorten_data(dtime, vals, c_list, c_ind, dtype)
#
#--- first a few days of the year...
#
    if dtype == 'week':
        if xmax < 14:
            if mdtime[-1] > 300:
                if mcf.is_leapyear(byear-1):
                    base = 366
                else:
                    base = 365
                asave = []
                for ent in mdtime:
                    asave.append(ent - base)
                mdtime = asave
#
#--- find moving average and envelope
#
    [xmc, ymc, xme, ymb, ymt] = create_envelope(mdtime, mvals, dtype)
    try:
        ymc[0] = ymc[3]
        ymc[1] = ymc[3]
        ymc[2] = ymc[3]
    
        ymb[0] = ymb[3]
        ymb[1] = ymb[3]
        ymb[2] = ymb[3]
    
        ymt[0] = ymt[3]
        ymt[1] = ymt[3]
        ymt[2] = ymt[3]
    except:
        pass
#
#--- find a future trend
#
    [[tlim, tmax], [pbeg_bot, pend_bot],\
     [pbeg_cnt, pend_cnt], [pbeg_top, pend_top], \
     [min_a, min_b, max_a, max_b, slope, serr]] \
                            = get_predictive_lines(xmc, ymc, xme, ymb, ymt, mdtime[-1], xmax)

#
#--- re-evaluate the range of the y axis 
#
    yb_test = min_a + min_b * xmax
    if yb_test < ymin:
        ymin = yb_test
    try:
        if min(ymb) < ymin:
            ymin = min(ymb)
    except:
        pass
    
    yt_test = max_a + max_b * xmax
    if yt_test > ymax:
        ymax = yt_test
    try:
        if max(ymt) > ymax:
            ymax = max(ymt)
    except:
        pass
#
#--- use the second digit to adjust the plotting range
#
    try:
        mag  = find_magnitude(ymax)
        mag1 = mag -2
    except:
        mag1 = 0

    ymin = int(ymin /10**mag1 - 1) * 10**mag1
    ymax = int(ymax /10**mag1 + 1) * 10**mag1
#
#--- set yellow/red warning/violation area
#
    [boxes, byear]  = set_limit_ranges(ltable, xmax, dtype)
#
#--- set x and y axis labels
#
    [xlabel, ylabel] = set_axes_label(msid, udict[msid], dtype, byear)
#
#--- start plotting
#
    plt.close('all')
    props = font_manager.FontProperties(size=14)
    mpl.rcParams['font.size']   = 14
    mpl.rcParams['font.weight'] = 'bold'

    fig, ax = plt.subplots(1, figsize=(8,6))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
#
#--- compute stat and write out
#
    stat_results = compute_stat(cdtime, cvals)
#
#--- plot data points
#
    ax.scatter(mdtime, mvals, color=mc_list, alpha=0.5, marker='o', s=20 ,lw=0)
#
#--- plots warning and violation areas
#
    for olist in boxes:
        [trange, rlbox, ylbox, ytbox, rtbox] = olist
        ax.fill_between(trange, rtbox[0], rtbox[1], facecolor='red',\
                            alpha=0.2, interpolate=True)

        ax.fill_between(trange, ytbox[0], ytbox[1], facecolor='yellow',\
                            alpha=0.2, interpolate=True)

        ax.fill_between(trange, ylbox[0], ylbox[1], facecolor='yellow',\
                            alpha=0.2, interpolate=True)

        ax.fill_between(trange, rlbox[0], rlbox[1], facecolor='red',\
                            alpha=0.2, interpolate=True)
#
#--- plot center moving average
#
    ax.plot(xmc, ymc, color='#E9967A', lw=4)
#
#--- plot data envelope
#
    try:
        ax.fill_between(xme, ymb, ymt, facecolor='#00FFFF', alpha=0.3, interpolate=True)
    except:
        pass
#
#--- plot future trends
#
    if ((xmax - xmin) > 3) and (dtype in ['five', 'long']):
        tend = tlim + 2
        if xmax < tend:
            tend = xmax
#
#--- if the slope is too steep, probably the data is in transition; don't plot predictive line
#
        if abs(max_b) < 10 or abs(min_b) < 10:
            ax.plot([tlim, tend], [pbeg_bot, pend_bot], color='green', lw=4, linestyle='dashed')
            ax.plot([tlim, tend], [pbeg_cnt, pend_cnt], color='green', lw=4, linestyle='dashed')
            ax.plot([tlim, tend], [pbeg_top, pend_top], color='green', lw=4, linestyle='dashed')
#
#--- label state
#
    if not (state in ['single', 'nsingle', 'mta']):
        lxpos = xmin + 0.01 * (xmax - xmin)
        lypos = ymax - 0.05 * (ymax - ymin)
        if state == 'none':
            tline = "State: open" 
        else:
            tline = "State: " + state
        plt.text(lxpos, lypos, tline, color='blue')
#
#--- trend slope
#
    if slope != 0:
        sxpos = xmin + 0.22 * (xmax - xmin)
        sypos = ymax - 0.05 * (ymax - ymin)
        sline = 'Slope: ' + '%2.3f' % round(slope, 3) + '+/-' + '%2.3f' % round(serr, 3)
        plt.text(sxpos, sypos, sline)

#
#--- violation warning; only when it is the full data range.
#
    if dtype == 'long':
        warning = create_violation_notification(msid, dtype, mtype, state, cdtime, cvals, c_list, \
                                                c_ind, min_a, min_b, max_a, max_b, tmax , ltable)
        if warning != '':
            wxpos = xmin + 0.01 * (xmax - xmin)
            wypos = ymax - 0.10 * (ymax - ymin)
            plt.text(wxpos, wypos, warning, color='red')

    outdir  = web_dir + group + '/' + msid.capitalize() + '/Plots/'
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)
    if state in ['none','single', 'nsingle', 'mta']:
        outname = outdir + msid +  '_' + dtype + '_' + mtype + '.png'
    else:
        outname = outdir + msid + '_' + dtype+ '_' + mtype + '_' + state + '.png'

    fig.set_size_inches(10.0, 5.0)
    plt.savefig(outname, format='png', dpi=100)
    plt.close('all')

    return stat_results

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def drop_extreme(x, y):

    sy   = sorted(y)
    ylen = len(sy)
    bcut = int(0.01 * ylen)
    bval = sy[bcut]
    tcut = -1 * int(0.01 * ylen)
    tval = sy[tcut]

    if bval == tval:
        return [x, y]

    ax   = numpy.array(x)
    ay   = numpy.array(y)

    avg  = numpy.mean(y)
    std  = numpy.std(y)
    ul   = avg + 3.5 * std
    ll   = avg - 3.5 * std

    ind  = ay > bval
    ax   = ax[ind]
    ay   = ay[ind]

    ind  = ay > ul
    ax   = ax[ind]
    ay   = ay[ind]


    ind  = ay < tval
    ax   = ax[ind]
    ay   = ay[ind]

    ind  = ay < ll
    ax   = ax[ind]
    ay   = ay[ind]


    lx   = list(ax)
    ly   = list(ay)

    if len(ly) < 0.8 * ylen:
        return [x, y]

    return [lx, ly]

#--------------------------------------------------------------------------------
#-- shorten_data: reduce the numbers of data to plot                          ---
#--------------------------------------------------------------------------------

def shorten_data(dtime, vals, c_list, c_ind, dtype):
    """
    reduce the numbers of data to plot
    input:  dtime   --- a list of time data
            vals    --- a list of values
            c_list  --- a list of color of the data points
            c_ind   --- a list of indicator where the data points in the warning range
            dtype   --- a data type: week, short, year, five, or long
    output: dtime   --- a list of shorten time data
            vals    --- a list of shorten value data
            c_list  --- a list of shorten color values
            c_ind   --- a list of shorten location ind
    """
#
#--- for plotting, just skip the data: make them less than 600 data points
#
    dlen   = len(dtime)
    if dtype == 'week':
        skip = 3

    elif dtype in ['week', 'year']:
        skip = 10

    elif dtype == 'five':
        skip = 5

    else:
        skip = 5

    if dlen > 600:
        dtime  = numpy.array(dtime)[::skip]
        vals   = numpy.array(vals)[::skip]
        c_list = numpy.array(c_list)[::skip]
        c_ind  = numpy.array(c_ind)[::skip]

    return [dtime, vals, c_list, c_ind]

#--------------------------------------------------------------------------------
#-- average_data_for_envelope: reducing the numbers of data by taking averages of data
#--------------------------------------------------------------------------------

def average_data_for_envelope(x, y, ctop = 200):
    """
    reducing the numbers of data by taking averages of data for given numbers
    input:  x       --- a list of x data
            y       --- a list of y data
            ctop    --- the numbers of data point to average
    output: xsave   --- a list of averaged x data
            ysave   --- a list of averaged y data
    """
    xt   = numpy.array(x)
    yt   = numpy.array(y)
    aind = xt.argsort()
    x   = xt[aind[::]]
    y   = yt[aind[::]]

    dlen = len(x)
    if dlen <= ctop:
        return [x, y]

    step  = int(dlen/ctop) + 1
    xsave = []
    ysave = []
    for k in range(0, ctop):
        start = k * step
        stop  = start + step
        if stop > dlen:
            stop = dlen
        xout = x[start:stop]
        yout = y[start:stop]
        if len(xout) < 1:
            continue
        #xavg = numpy.mean(xout)
        yavg = numpy.mean(yout)
        #xsave.append(xavg)
        xsave.append(xout[-1])
        ysave.append(yavg)

    return [xsave, ysave]

#--------------------------------------------------------------------------------
#-- make_limit_table: extract a set of limit table for a given msid             --
#--------------------------------------------------------------------------------

def make_limit_table(ldata, state):
    """
    extract a set of limit table for a given msid
    input:  
            ldata   --- a list of lists of limits
                        [
                            <period start time>, <period end time>, cnd_msid, 
                            <possibe key lists>, <limit dictonary: key <--> [y_low, y_top, r_low, r_top]
                        ]
            state   --- the state of the data are in (e.g., on or off)
    output: asave   --- a list of lists of limit data. Each inner list contains:
                    [
                     <period start time>, <period end time>, [y_low, y_top, r_low, r_top]
                    ]
    """
    asave  = []
    for ent in ldata:
        try:
            lim_list = ent[3][state]
        except:
            try:
                lim_list = ent[3]['none']
            except:
                continue

        line = [ent[0], ent[1], lim_list]
        asave.append(line)

    return  asave

#-----------------------------------------------------------------------------------
#-- convert_time_format: convert time into either yday or fractional year depending on data type
#-----------------------------------------------------------------------------------

def convert_time_format(stime, dtype):
    """
    convert time into either yday or fractional year depending on data type
    input:  stime   --- time in seconds from 1998.1.1
            dtype   --- data type: week, short, year (y date)  or five or long (frac year)
    output: ctim    --- converted time
    """
#
#--- today's ydate and year
#
    cdate = int(float(time.strftime('%j', time.gmtime())))
    tyear = int(float(time.strftime('%Y', time.gmtime())))

    ctime = []
    byear = 0
    schk  = 0
    for ent in stime:
#
#--- set date in ydate
#
        if dtype in ['week', 'short', 'year']:
            out   = Chandra.Time.DateTime(ent).date
            atemp = re.split(':',  out)
            syear = int(atemp[0])
            syday = float(atemp[1])
            hh    = float(atemp[2])
            mm    = float(atemp[3])
            ss    = float(atemp[4])

            if schk < 1:
                byear = syear
                if mcf.is_leapyear(byear):
                    base = 366
                else:
                    base = 365
                schk = 1
#
#--- if this is a year long plot, for the first three months, the base year is the previous year
#--- after three months, the base year is this year
#
            if dtype == 'year':
                if cdate < 90:
                    syday += (syear - byear) * base + hh / 24.0 + mm / 1440.0 + ss / 86400.0
                else:
                    if syear == byear:
                        syday -= base
                    syday += hh / 24.0 + mm / 1440.0 + ss / 86400.0
                    schk   = 2
            else:
                syday += (syear - byear) * base + hh / 24.0 + mm / 1440.0 + ss / 86400.0

            ctime.append(syday)
#
#--- set date in fractional year
#
        else:
            byear = 1999
            ctime.append(float(mcf.chandratime_to_fraq_year(ent)))
#
#--- the base year changes, if it is year plot and after third months of the year
#
        if schk == 2:
            byear = tyear

    return [ctime, byear]

#-----------------------------------------------------------------------------------
#-- set_plot_range: set plotting range                                            --
#-----------------------------------------------------------------------------------

def set_plot_range(x, y, dtype):
    """
    set plotting range
    input:  x   --- a list of x values
            y   --- a list of y vales
            dtype   --- data type: week, short, year, five or long
    output: [xmin, xmax, ymin, ymax]
    """
#
#--- if the data type is week, short or year, use ydate for the range
#--- today is a global var
#
    [eyear, eyday, base]  = get_year_yday_from_chandra(today)
    if dtype in ['week', 'short', 'year']:
        if dtype == 'week':
            xmax = eyday
            xmin = xmax - 8
        elif dtype == 'short':
            xmax = eyday + 10 
            xmin = xmax - 100

        else:
            xmax = eyday + 30
            xmin = xmax  - 396
        if xmin < 1:
            xmax += base
            xmin += base
        
#
#--- if the data type is five or long, your year for the range
#
    elif dtype == 'five':
        xmax = eyear + 1
        xmin = xmax - 6
    else:
        xmax = eyear + 3
        xmin = 2000

    if len(y) > 100:
        ys = sorted(y)
        ycut = int(0.01 * len(y))
        nycut = -1 * ycut
        if abs(ycut) > 0 and abs(nycut) > 0:
            ys     = ys[ycut:nycut]
            ycut_b = chs.percentile(ys, 10)
            ycut_t = chs.percentile(ys, 90)
            ys = ys[ycut_b: ycut_t]
    else:
        ys = y

    yavg = numpy.mean(ys)
    ystd = numpy.std(ys)
    ymin = yavg - 3.5 * ystd
    ymax = yavg + 3.5 * ystd
    if ymin == ymax:
       band  = 0.1 * ymin
       if band == 0:
           band = 1
       ymin -= band
       ymax += band
       return [xmin, xmax, ymin, ymax]
#
#--- use the second digit to adjust the plotting range
#
    try:
        mag  = find_magnitude(ymax)
        mag1 = mag -2
    except:
        mag1 = 0

    ymin = int(ymin /10**mag1 - 1) * 10**mag1
    ymax = int(ymax /10**mag1 + 1) * 10**mag1
    if ymax == 0:
        ydiff = ymax - ymin
        ymax += 0.1 * ydiff

    return [xmin, xmax, ymin, ymax]

#-----------------------------------------------------------------------------------
#-- get_year_yday_from_chandra: convert Chandra time to year and ydate            --
#-----------------------------------------------------------------------------------

def get_year_yday_from_chandra(stime):
    """
    convert Chandra time to year and ydate
    input:  stime   --- time in seconds from 1998.1.1
    output: syear   --- year
            syday   --- y date
            base    --- either 366 (leap year) or 365 (regulare year)
    """

    out   = Chandra.Time.DateTime(stime).date
    atemp = re.split(':',  out)
    syear = int(atemp[0])
    syday = int(atemp[1])
    if mcf.is_leapyear(syear):
        base = 366
    else:
        base = 365

    return [syear, syday, base]

#-----------------------------------------------------------------------------------
#-- find_magnitude: find a magnitude of the value                                 --
#-----------------------------------------------------------------------------------

def find_magnitude(val):
    """
    find a magnitude of the value
    input:  val --- numeric value
    output: magnitude
    """

    return math.floor(math.log10(val))

#----------------------------------------------------------------------------------
#-- set_axes_label: set axes labels                                              --
#----------------------------------------------------------------------------------

def set_axes_label(msid, unit, dtype, byear):
    """
    set axes labels
    input:  msid    --- msid
            unit    --- unit
            dtype   --- short or long type plot indicator
            byear   --- base year (used for week, short, one)
    output: xlabel  --- x axis label
            ylabel  --- y axis label
    """
    if dtype in ['five', 'long']:
        xlabel = 'Time (year)'
    else:
        xlabel = 'Time (yday of ' + str(int(byear)) + ')'
    
    if unit != '':
        if unit in ('DEGF', 'DEGC'):
            unit = 'K'
        ylabel = msid + ' (' + unit + ')'
    else:
        ylabel = msid
    
    return [xlabel, ylabel]

#----------------------------------------------------------------------------------
#-- create_envelope: create envelope around data point                           --
#----------------------------------------------------------------------------------

def create_envelope(xdata, ydata, dtype):
    """
    create envelope around data points
    input:  xdata   --- a list of x data
            ydata   --- a list of y data
            dtype   --- data type: week, short, year, five, lonog
    output: xmc     --- a list of x values for the envelope
            ymc     --- a center moving average value
            ymb     --- a lower envelope
            ymt     --- a upper envelope
    """
    period = set_period(dtype)
#
#--- center trend
#
    [x, y]     = select_y_data_range(xdata, ydata, period, 2, 98)
    [x, y]     = average_data_for_envelope(x, y, 300)
    [xmc, ymc] = get_moving_average_fit(x, y, period)
#
#--- bottom envelope
#
    [x, y]     = select_y_data_range(xdata, ydata, period, 2, 10)
    [x, y]     = average_data_for_envelope(x, y)
    [xmb, ymb] = get_moving_average_fit(x, y, period)
#
#--- top envelope
#
    [x, y]     = select_y_data_range(xdata, ydata, period, 90, 98)
    [x, y]     = average_data_for_envelope(x, y)
    [xmt, ymt] = get_moving_average_fit(x, y, period)
#
#---- adjust length of lists so that top and bottom line have
#---- the same numbers of data
#
    yblen = len(ymb)
    ytlen = len(ymt)
    
    xme = xmt
    if yblen < ytlen:
        ymt = ymt[:yblen]
        xme = xmt[:yblen]
    elif yblen > ytlen:
        ymb = ymb[:ytlen]
        xme = xmb[:ytlen]

    return [xmc, ymc, xme, ymb, ymt]

#----------------------------------------------------------------------------------
#-- get_predictive_lines: estimate future trend envelopes from the current envelopes
#----------------------------------------------------------------------------------

def get_predictive_lines(xmc, ymc, xme, ymb, ymt, tlast, tmax):
    """
    estimate future trend envelopes from the current envelopes
    input:  xmc     --- a list of x values for the envelope
            ymc     --- a center moving average value
            ymb     --- a lower envelope
            ymt     --- a upper envelope
            tlast   --- the time of the last entry
            tmax    --- the max plotting range
    output: two point extensiion of the envelopes:
                tlim, tmax  --- start and stop time
                pbeg_bot, pend_bot  --- start and stop bottom envelop extension
                pbeg_cnt, pend_cnt  --- start and stop center estimate
                pbeg_top, pend_top  --- start and stop top envelope extension
                min_a, min_b, max_a, max_b --- bottom and top envelope intercect and slope 
    """
    tend = tlast + 0.8 * (tmax - tlast)
#
#--- bottom prediction
#
    if len(xme[-10:]) > 2:
        try:
            [min_a, min_b, sd] = chs.least_sq(xme[-10:], ymb[-10:], ecomp=1)
        except:
            [min_a, min_b] = [0, 0]
#
#--- top prediciton
#
        try:
            [max_a, max_b, sd] = chs.least_sq(xme[-10:], ymt[-10:], ecomp=1)
        except:
            [max_a, max_b] = [0, 0]
#
#--- sometime there are not enough data in top and bottom strips; use the center one
#
    else:
        try:
            [max_a, max_b, sd] = chs.least_sq(xmc[-10:], ymc[-10:], ecomp=1)
            min_a = cnt_a
            min_b = cnt_b
            max_a = cnt_a
            max_b = cnt_b
        except:
            [max_a, max_b] = [0, 0]
            [min_a, min_b] = [0, 0]
            [max_a, max_b] = [0, 0]

    pbeg_bot = min_a + min_b * tlast
    pend_bot = min_a + min_b * tend

    pbeg_top = max_a + max_b * tlast
    pend_top = max_a + max_b * tend
#
#--- center prediction --- take an average of top and bottom lines
#
    ac = 0.5 * (min_a + max_a)
    bc = 0.5 * (min_b + max_b)
    pbeg_cnt = ac + bc * tlast
    pend_cnt = ac + bc * tend 

    return [[tlast, tend], [pbeg_bot, pend_bot], [pbeg_cnt, pend_cnt],\
            [pbeg_top, pend_top], [min_a, min_b, max_a, max_b, bc, sd]]


#----------------------------------------------------------------------------------
#-- select_y_data_range: select data based on range of percentiles
#----------------------------------------------------------------------------------

def select_y_data_range(xtime, yval, period, p1, p2):
    """
    select data based on range of percentiles
    input:  xtime   --- a list of x values
            yval    --- a list of y values
            period  --- a compartment size
            p1      --- bottom cut in percentile
            p2      --- top cut in percentile
    output: xadjust --- a list of x data in the selected range
            yadjust --- a list of y data in the selected range
    """
    xt   = numpy.array(xtime)
    yt   = numpy.array(yval)
    aind = xt.argsort()
    xt   = xt[aind[::]]
    yt   = yt[aind[::]]
    xadjust = []
    yadjust = []
#
#--- set step size and numbers of periods: select the data span to 20% of the period given 
#--- so that the bottom and top spans do not change much during the data selection period
#
    step  = 0.2 * period
    start = xt[0]
    stop  = xt[-1]
    snum  = int((stop - start) / step) + 1
    
    begin = 0
    for k in range(0, snum):
#
#--- select the data in that period
#
        xs = []
        ys = []
        sn = 0
        lstop = (k+1) * step + start
        for m in range(begin, len(xt)):
            if xt[m] > lstop:
                break
            else:
                xs.append(xt[m])
                ys.append(yt[m])
                sn += 1
 
        if len(xs) < 1:
            continue
#
#--- reset the starting spot for the next round
#
        begin += sn
#
#--- find given percentaile range
#
        limb = numpy.percentile(ys, p1)
        limt = numpy.percentile(ys, p2)
        lavg = 0.5 * (limb + limt)

        for n in range(0, len(xs)):
#
#--- if the data is in the range, use the value
#
            if (ys[n] >= limb) and (ys[n] <= limt):
                xadjust.append(xs[n])
                yadjust.append(ys[n])
#
#--- if not, use the average
#
            else:
                xadjust.append(xs[n])
                yadjust.append(lavg)
 
    return [xadjust, yadjust]

#----------------------------------------------------------------------------------
#-- get_moving_average_fit: get moving average                                   --
#----------------------------------------------------------------------------------

def get_moving_average_fit(x, y, period):
    """
    get moving average 
    input:  x       --- a list of x values
            y       --- a list of y values
            period  --- a period of the step
    output: [tx1, tx2]  --- a list of lists of x and y values of moving average
    """
#
#--- first find moving average forward, then find moving average backward from the end
#
    try:
        out1 = fma.find_moving_average(x,  y, period , 0)
    except:
        out1 = [[],[]]
    try:
        out2 = fmab.find_moving_average(x, y, period , 0)
    except:
        out2 = [[],[]]
#
#--- combined two of them so that fill all the way
#
    tx1 = out1[0]
    ty1 = out1[1]
    
    tx2 = out2[0]
    ty2 = out2[1]
    
    tx3 = []
    ty3 = []
    for k in range(0, len(tx2)):
        if tx2[k] > tx1[-1]:
            tx3.append(tx2[k])
            ty3.append(ty2[k])
    
    tx1 = tx1 + tx3
    ty1 = ty1 + ty3
    
    return [tx1, ty1]

#----------------------------------------------------------------------------------
#-- set_period: assign numeric step interval for the given time interval indicator 
#----------------------------------------------------------------------------------

def set_period(dtype):
    """
    assign numeric step interval for the given time interval indicator
    input:  dtype   --- week, short, one, finve, long
    output: period  --- numeric step value for the dtype
    """
    if dtype ==  'long':
        period = 0.32           #--- four month interval
    elif dtype == 'five':
        period = 0.16           #--- two month interval
    elif dtype == 'week':
        period = 1.0            #--- one day interval
    elif dtype == 'year':
        period = 15.0           #--- 15 day interval
    else:
        period = 5.0            #--- 5 day interval (for 3 month plot)
    
    return period

#-----------------------------------------------------------------------------------
#-- create_violation_notification: create warning if the data will be in warning/violation area in future
#-----------------------------------------------------------------------------------

def create_violation_notification(msid, dtype, mtype, state, dtime, vals, c_list, c_ind,\
                                  min_a, min_b, max_a, max_b, tmax, ltable):
    """
    create warning if the data will be in warning/violation area in future
    this is only used when a long term data is used.
    input:  msid        --- msid
            dtype       --- data type week, short, year, five long
            mtype       --- mid, min, max
            state       --- state
            dtime       --- a list of x data
            vals        --- a list of y data
            c_list      --- a list of color data
            c_ind       --- a list of position of data regrad of warning area
            min_a       --- intercept of the lower envelope extension
            min_b       --- slope of the lower envelope extension
            max_a       --- intercept of the upper envelope extension
            max_b       --- slope of the upper envelope extension
            tmax        --- last x value
            ltable = [
                        [<period start time>, <period end time>, y_low, y_top, r_low, r_top]...]
                     ]
    output: warning     --- a sentence warning the possible future violation (or '')
    """
#
#--- set x max boundary
#
    t_out = time.strftime('%Y:%j:00:00:00', time.gmtime())
    atemp = re.split(':', t_out)
    tmax  = float(atemp[0]) + float(atemp[1]) / 365.0
#
#--- if there is no data for the last one year, don't bother checking the violation
#
    if dtime[-1] < tmax -1.0:
        return ''
#
#--- collect data for the last half year
#
    dlen  = len(dtime)
    tlast = dtime[-1]
    tchk  = tlast - 0.5     #---- a half year period
    for k in range(0, dlen):
        if dtime[k] > tchk:
            kstart = k
            break
#
#--- first check whether the data are already in warning/violation area
#
    yb_cnt = 0
    yt_cnt = 0
    rb_cnt = 0
    rt_cnt = 0
    for k in range(kstart, dlen):
        if c_list[k] == 'orange':
            if c_ind[k] == 'yl':
                yb_cnt += 1
            else:
                yt_cnt += 1
        elif c_list[k] == 'red':
            if c_ind[k] == 'rl':
                rb_cnt += 1
            else:
                rt_cnt += 1

    if (dtype == 'long') and (mtype == 'mid'):
        try:
            ved.delete_entry(msid, state)
        except:
            pass
    warning = ''
    dev = dlen - kstart
    if rt_cnt/dev > 0.3:
        warning = 'The data are already in Red Upper Violation'
        if (dtype == 'long') and (mtype == 'mid'):
            vtdata  = [0, 0, 0, tmax]
            ved.incert_data(msid, dtype, mtype, state, vtdata)

    elif rb_cnt/dev > 0.3:
        warning = 'The data are already in Red Lower Violation'
        vtdata  = [0, 0, tmax, 0]
        ved.incert_data(msid, dtype, mtype, state, vtdata)

    elif yt_cnt/dev > 0.3:
        warning = 'The data are already in Yellow Upper Violation'
        if (dtype == 'long') and (mtype == 'mid'):
            vtdata  = [0, tmax, 0, 0]
            ved.incert_data(msid, dtype, mtype, state, vtdata)

    elif yb_cnt/dev > 0.3:
        warning = 'The data are already in Yellow Lower Violation'
        if (dtype == 'long') and (mtype == 'mid'):
            vtdata  = [tmax, 0, 0, 0]
            ved.incert_data(msid, dtype, mtype, state, vtdata)
#
#--- check the future violation
#
    else:
        y_low   = ltable[-1][2][0]
        y_top   = ltable[-1][2][1]
        r_low   = ltable[-1][2][2]
        r_top   = ltable[-1][2][3]
        yltime  = predict_violation(min_a, min_b, dtime[-1], y_low, side = 0)
        syltime = '%4.2f' % yltime
        yttime  = predict_violation(max_a, max_b, dtime[-1], y_top, side = 1)
        syttime = '%4.2f' % yttime
        rltime  = predict_violation(min_a, min_b, dtime[-1], r_low, side = 0)
        srltime = '%4.2f' % rltime
        rttime  = predict_violation(max_a, max_b, dtime[-1], r_top, side = 1)
        srttime = '%4.2f' % rttime

        utime = tmax + 3.0

        if rttime < utime:
            warning = 'The data may violate the upper red limit at Year: '    + srttime
        elif rltime < utime:
            warning = 'The data may violate the lower red limit at Year: '    + srltime
        elif yttime < utime:
            warning = 'The data may violate the upper yellow limit at Year: ' + syttime
        elif yltime < utime:
            warning = 'The data may violate the lower yellow limit at Year: ' + syltime
#
#-- update violation time estimate database
#
        if (dtype == 'long') and (mtype == 'mid'):
            vtdata = [yltime, yttime, rltime, rttime]
            try:
                ved.incert_data(msid, dtype, mtype, state, vtdata)
            except:
                ved.update_data(msid, dtype, mtype, state, vtdata)

    return warning

#----------------------------------------------------------------------------------
#-- predict_violation: predict possible limti violations                         --
#----------------------------------------------------------------------------------

def predict_violation(a, b, current, vlimit, side = 1):
    """
    predict possible limti violations
    input:  a       --- intercept of the predicted line
            b       --- slope of the predicted line
            current --- the current time 
            vlimit  --- limit value
            side    --- lower (0) or upper (1) limit
    output: rtime   --- estimated violation time. if no violation return 0
    """
    if abs(b) == 999:
        return 2200.0
    elif abs(b) > 10:
        return 2200.0
    
    vlimit = float(vlimit)
    
    rtime  = 0
    now  = a + b * current
    if side > 0:
        if now > vlimit:
            rtime = current
    else:
        if now < vlimit:
            rtime = current
    
    if rtime == 0:
#
#--- if the slope is too steep, something is not right; so ignore the future estimation
#
        if  (b == 0) or (abs(b) > 10):
            rtime = 2200.0
        else:
            estimate = (vlimit - a) / b
            if estimate > current:
                rtime = estimate
            else:
                rtime = 2200.0
    
    return rtime



#-----------------------------------------------------------------------------------
#-- DERIVATIVE RELATED FUNCTIONS START HERE                                       --
#-----------------------------------------------------------------------------------






#--------------------------------------------------------------------------------------------
#-- create_derivative_plots: create derivative plots for all msid listed in msid_list      --
#--------------------------------------------------------------------------------------------

def create_derivative_plots(pdata, byear, msid, group, dtype, udict):
    """
    """
    dev_dict = {}
    for mtype in ['mid', 'min', 'max']:
        sline = ''
        o_list = plot_deviatives(pdata, byear, msid, group, dtype, mtype)
        s_list = []
        s_dict = {}
        for out in o_list:
            s_list.append(out[3])
            vline = out[0] + ':' + out[1] + ':' + out[2]
            s_dict[out[3]] = vline
        dev_dict[mtype] = [s_list, s_dict]

    return dev_dict

#--------------------------------------------------------------------------------------------
#-- plot_deviatives: create derivative plots for given msid                                --
#--------------------------------------------------------------------------------------------

def plot_deviatives(pdata, byear, msid, group, ltype, mtype):
    """
    create derivative plots for given msid
    input:  pdata   --- a two dimensional array of data set; see read_data for details
            byear   --- a base year for the short/weekly plots
            msid    --- msid
            group   --- group name
            ltype   --- data type, such as week, short, year, five, long
            mtype   --- data type, such as mid, min, max
    output: [a,b,d, outname]    --- fitted line  intercept, slope, error, and a png file name
            <web_dir>/<group>/<msid>/Plots/msid_*_dev.png
    """
#
#--- state list
#
    s_list  = pdata[-1]
#
#--- three different data position by mid, min, and max
#
    plen    = len(pdata)
    pos     = find_pos(mtype)
#
#--- step size indicates how many data collected before computing the dy/dx
#
    if ltype in ('five', 'long'):
        step = 20
        xt   = pdata[0]
        yt   = pdata[pos]
        st   = s_list

        if ltype == 'five':
            [xt, yt, st] =  cut_the_data(xt, yt, s_list, 5.0)       #---- five year interval

    elif ltype  in('short', 'year'):
        step = 50
        xt   = pdata[0]
        yt   = pdata[pos]
        st   = s_list
        if ltype == 'short':
            [xt, yt, st] =  cut_the_data(xt, yt, s_list, 90.0)     #---- three month interval

    else:                                               #--- week long data
        try:
            step = 20 
            xt   = pdata[0]
            yt   = pdata[pos]
            st   = s_list
        except:
            cmd = 'cp  ' + house_keeping + 'no_data.png ' + outname
            os.system(cmd)
            return ['0', '0', '0', outname]
#
#--- check whether there are multiple states
#
    st_out = set_state(xt, yt, st)

    r_save = []
    for out in st_out:
        xt   = out[0]
        yt   = out[1]
        scnd = out[2]
#
#--- find dy/dx along the time line
#
        [xd, yd, ad] = find_deriv(xt, yt, ltype,  step=step)
#
#--- set output png file name
#
        outname  = web_dir + group.capitalize() + '/' + msid.capitalize() 
        if scnd == 'none':
            outname = outname + '/Plots/' + msid + '_' + ltype + '_' + mtype + '_dev.png'
        else:
            outname = outname + '/Plots/' + msid + '_' + ltype + '_' 
            outname = outname + mtype + '_' + scnd + '_dev.png'
#
#--- if there are less than 10 data point display "no_data"
#
        if len(xd) < 10:
            cmd = 'cp  ' + house_keeping + 'no_data.png ' + outname
            os.system(cmd)
            continue
#
#--- fit a line to find dy/dx/dx
#
        [nx, ny]     = remove_out_layers(xd, yd)
        [a,  b,  d]  = chs.least_sq(nx, ny, ecomp=1)
#
#--- create a plot
#
        create_scatter_plot(msid, xt, xd,  yd,  ltype, mtype, byear, a,  b,  d, scnd,  outname)

        if abs(b) < 0.001:
            a = '%3.3e' % (a)
            b = '%3.3e' % (b)
            d = '%3.3e' % (d)
        else:
            a = '%3.3f' % round(a, 3)
            b = '%3.3f' % round(b, 3)
            d = '%3.3f' % round(d, 3)

        r_save.append([a, b, d, scnd, outname])

    return r_save

#--------------------------------------------------------------------------------------------
#-- set_state: separate the data into different states                                     --
#--------------------------------------------------------------------------------------------

def set_state(x, y, st):
    """
    separate the data into different states
    input:  x   --- a list of x data
            y   --- a list of y data
            st  --- a list of states
    output: save    --- a list of lists of [<x data>, <y data>, state]
    """
#
#--- find out how many states exist
#
    states = list(set(st))
    slen   = len(states)
#
#--- if only one state, just return the data
#
    if slen == 1:
        return [[x, y, states[0]]]
#
#--- if there are more than one state, separate the data
#
    else:
        save = []
#
#--- "none" state is not a really a state; so include in all data set
#
        st = numpy.array(st)
        x  = numpy.array(x)
        y  = numpy.array(y)
        if 'none' in states:
            ind = st == 'none'
            xn  = list(x[ind])
            yn  = list(y[ind])
        else:
            xn = []
            yn = []

        for state in states:
            if state == 'none':
                continue
            else:
                ind = st == state

                xt  = list(x[ind])
                yt  = list(y[ind])

                xt  = xt + xn
                yt  = yt + yn
                save.append([xt, yt, state])

        return save

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

def remove_out_layers(x, y):
    """
    remove extreme values from the data
    input:  x   --- a list of x data
            y   --- a list of y data
    output: nx  --- cleaned x data list
            ny  --- cleaned y data list
    """
    if len(y) < 1:
        return [x, y]

    ax = numpy.array(x)
    ay = numpy.array(y)

    ytemp = sort(y)
    xlen  = len(x)
#
#--- if the data set is large enough, drop the top and bottom 2%
#
    if xlen > 200:
        pos   = int(0.02 * xlen)
        bot   = ytemp[pos]
        top   = ytemp[-pos]
#
#--- otherwise, just top and botto data
#
    else:
        bot   = ytemp[0]
        top   = ytemp[-1]
#
#--- now compute avg and std
#
    try:
        avg  = numpy.mean(ay)
        std  = numpy.std(ay)
    except:
        avg  = 0.0
        std  = 0.0
#
#--- drop data outside of 3.5 sigma
#
    test = avg - 3.5 * std
    if test > bot:
        bot = test
    test = avg + 3.5 * std
    if  test < top:
        top = test
#
#--- if y value is extremely large, something wrong; so drop it
#
    idx = ay < 1e10
    ax  = ax[idx]
    ay  = ay[idx]

    idx = ay < top
    ax  = ax[idx]
    ay  = ay[idx]

    idx = ay > -1e10
    ax  = ax[idx]
    ay  = ay[idx]

    idx = ay > bot
    ax  = ax[idx]
    ay  = ay[idx]

    return [ax, ay]

#--------------------------------------------------------------------------------------------
#-- find_pos: set data position depending of the data type                                 --
#--------------------------------------------------------------------------------------------

def find_pos(mtype):
    """
    set data position depending of the data type
    input:  mtype   --- mid, min, or max
    output: pos     --- the data position in pdata
    """
    if mtype == 'mid':
        pos = 1
    elif mtype == 'min':
        pos = 2
    elif mtype == 'max':
        pos = 3
    else:
        pos = 1

    return pos
 
#--------------------------------------------------------------------------------------------
#-- cut_the_data: cut the data at period time before the current time                      --
#--------------------------------------------------------------------------------------------

def cut_the_data(x, y, st, period):
    """
    cut the data at period time before the current time
    input:  x   --- a list of x data (time data)
            y   --- a list of y data
            st  --- a list of state data
            period  --- the interval that we want the data from the current time
    output: xd  --- a list of x data after period time
            yd  --- a list of y data after period time
            sd  --- a list of state data after period time
    """
    cut   = float(x[-1]) - period
    x     = numpy.array(x)
    y     = numpy.array(y)
    st    = numpy.array(st)
    indx  = x > cut
    xd    = list(x[indx])
    yd    = list(y[indx])
    sd    = list(st[indx])

    return [xd, yd, sd]

#--------------------------------------------------------------------------------------------
#-- find_deriv: compute the derivative per year                                            --
#--------------------------------------------------------------------------------------------

def find_deriv(x, y, ltype, step=200):
    """
    compute the derivative per year
            the dy/dx is computed similar to that of moving average, but compute slope in that range
    input;  x       --- a list of x values
            y       --- a list of y values
            ltype   --- type of data such as short, long
            step    --- step size; how may data points should be include in the moving average
    output: xd      --- a list of x position
            yd      --- a list of dx/dy; of slope of the fitting
            ad      --- a list of intercept of the fitting
    """
    hstep = int(0.5 * step)
    dlen  = len(x)
#
#--- if the time is in days, convert it into years
#
    if ltype in ('week',  'short', 'year'):
        xt = list(numpy.array(x) / 365.0)
    else:
        xt = x
#
#--- sort the data with time
#
    xt  = numpy.array(xt)
    y   = numpy.array(y)
    ind = numpy.argsort(xt)
    xt  = list(xt[ind])
    y   = list(y[ind])
#
#--- moving average but compute slope instead of average
#
    xd    = []
    yd    = []
    ad    = []

    for k in range(hstep, dlen - hstep):
        ks = k - hstep
        ke = k + hstep
        xs = xt[ks:ke]
        ys = y[ks:ke]

        xp = 0.5*(xt[ke] + xt[ks])
        [a, b, d] = chs.least_sq(xs, ys)
#
#--- rare occasion, fits fail, skip the ponit
#
        if b == 999:
            continue
        else:
            xd.append(x[k])
            yd.append(b)
            ad.append(a)

    xd = numpy.array(xd)
    xd = xd.astype(float)
    xd = xd[0::2]

    yd = numpy.array(yd)
    yd = yd.astype(float)
    yd = yd[0::2]

    ad = numpy.array(ad)
    ad = ad.astype(float)
    ad = ad[0::2]

    return [xd, yd, ad]

#--------------------------------------------------------------------------------------------
#-- create_scatter_plot: create interactive trend plot                                     ---
#--------------------------------------------------------------------------------------------

def create_scatter_plot(msid, xo, xb, yb,  ltype, mtype,  byear, a, b, d, scnd, outname = ''):
    """
    create a plot
    input:  msid    --- msid
            xo      --- the original list of x data; used to computer the plotting range
            x       --- the list of x
            y       --- the list of y
            ltype   --- data type, such as short and long
            mtype   --- min, max, mid
             cut_the_data: cut the data at period time before the current time                      
            a       --- the intercept of the fitted line
            b       --- the slope of the fitted line
            d       --- the error of the fitted line
            scnd    --- state of the data
            outname --- the name of png file to be created
    output: outname --- <web_dir>/<group>/<msid>/Plots/msid_*.png
    """
#
#--- cut out 2 out of 3 data points from one year plot and full range plot
#
    if ltype in ('year', 'long'):
        x = xb[0::3]
        y = yb[0::3]
    else:
        x = xb
        y = yb
#
#
#--- open and set plotting surface
#
#
    plt.close('all')

    fig, ax = plt.subplots(1, figsize=(8,6))

    props = font_manager.FontProperties(size=14)
    mpl.rcParams['font.size']   = 14
    mpl.rcParams['font.weight'] = 'bold'
#
#--- set plotting axes
#
    [xmin, xmax, ymin, ymax] = set_plot_range(x, y, ltype)
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    [xlabel, ylabel] = set_axes_label(msid, udict[msid],  ltype, byear)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if ltype == 'five':
        labels = []
        for lval in range(xmin, xmax):
            labels.append(lval)
        ax.set_xticklabels(labels)

#
#--- set the size of plot
#
    fig.set_size_inches(10.0, 5.0)
    fig.tight_layout()
#
#---- trending plots
#
    points = ax.scatter(x, y, marker='o', s=20 ,lw=0)
#
#---- slope note
#
    ys   = a + b * xmin
    ye   = a + b * xmax
    plt.plot([xmin, xmax], [ys, ye], color='green', lw=3)

    if abs(b) < 0.001 or abs(b) > 100:
        line = 'Slope: ' +  ecf.modify_slope_dicimal(b, d)
    else:
        slp  = "%2.3f" % round(b, 3)
        err  = "%2.3f" % round(d, 3)
        line = 'Slope: ' + slp +'+/-' + err

    xpos = xmin + 0.01 * (xmax - xmin)
    ypos = ymax - 0.10 * (ymax - ymin)
    plt.text(xpos, ypos, line)
#
#--- state designation
#
    if scnd != 'none':
        lxpos = xmin + 0.01 * (xmax - xmin)
        lypos = ymax - 0.05 * (ymax - ymin)
        tline = "State: " + scnd
        plt.text(lxpos, lypos, tline, color='blue')
#
#--- set the size of plot
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
    fig.tight_layout()
    plt.savefig(outname, format='png', dpi=100)

    plt.close('all')

#-----------------------------------------------------------------------------------
#-- compute_stat: compute stats for the given data set                            --
#-----------------------------------------------------------------------------------

def compute_stat(x, y):
    """
    compute stats for the given data set
    input:  x   --- a list of x data
            y   --- a list of y data
    output: line    --- <avg>:<std>:<slope>:<slope std>
    """
    [a, b, d] = chs.least_sq(x, y)
    avg       = numpy.mean(y)
    std       = numpy.std(y)

    if abs(avg) > 10000 or abs(avg) < 0.001:
        line = '%3.3e' % avg + ':'
    else:
        line = '%3.3f' % avg + ':'

    if std > 10000 or std < 0.001:
        line = line + '%3.3e' % std + ':'
    else:
        line = line + '%3.3f' % std + ':'

    line = line + str(b) + ':' + str(d)

    return line

#-----------------------------------------------------------------------------
#-- day_string: return string for current day of week                       --
#-----------------------------------------------------------------------------
def day_string():
    today = date.today()
    return DAYS[today.weekday()]

#-----------------------------------------------------------------------------------

if __name__ == '__main__':
    """
    ifile = sys.argv[1]
    dtype = sys.argv[2]
    ifile.strip()
    dtype.strip()

    create_msid_plots(ifile, dtype)
    """
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")

    """
    parser.add_argument("-w","--week", help="Process last two weeks in a [msid]_week_data.fits file", dest='period', action="append_const",const="week")
    parser.add_argument("-s","--short", help="Process last 1.5 years in a [msid]_short_data.fits file", dest='period', action="append_const",const="short")
    parser.add_argument("-l","--long", help="Process till 1999:201 in a [msid]_data.fits file", dest='period', action="append_const",const="long")
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-p','--period',help='Process specific time length. Choices are last two weeks, 1.5 years, or since 1999:201 respectively', \
                        action="extend",nargs='*',type=str, choices=["week","short","long"])
    parser.add_argument("-m","--msid_list",help="File name of msid list to use from housekeeping",type=str)

    args = parser.parse_args()

    if args.msid_list is None:
        msid_list = f"msid_list_{day_string()}"
    else:
        msid_list = args.msid_list.strip()
    
    for dtype in args.period:
        create_msid_plots(msid_list,dtype)
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")