#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#               extract_gyro_data.py: find gyro drift during the grating movements              #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 09, 2021                                                       #
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
import unittest
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
import Ska.engarchive.fetch as fetch
import scipy
from scipy.optimize import curve_fit
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
path = '/data/mta/Script/Gyro/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
catg_list    = ['roll', 'pitch', 'yaw']
grating_data =  "/data/mta_www/mta_otg/OTG_filtered.rdb"

#---------------------------------------------------------------------------------------
#-- extract_gyro_data: find gyro drift during the grating movements                   --
#---------------------------------------------------------------------------------------

def extract_gyro_data():
    """
    find gyro drift during the grating movements
    input: none
    output: plots, table, and html 
    """
#
#--- find the last entry date
#
    l_time = find_last_entry()
#
#--- find unprocessed data
#
    gout   = find_grating_insr_retr(l_time)
#
#--- go through each data
#
    for k in range(0, len(gout[0])):
    #for k in range(0, 5):
        action  = gout[0][k]
        grating = gout[1][k]
        start   = gout[2][k]
        stop    = gout[3][k]
        print(action + ' : ' + grating + ' : ' + str(start) + ' : ' + str(stop))
#
#--- extract data; fout contains data of roll, pitch, and yaw (time and value)
#
        fout    = extract_each_drift_data(start, stop)
        if len(fout[0][0]) == 0:
            continue

        for k in range(0, 3) :
#
#--- fit polinomial to the drift data
#
            dout  = fit_polinom_to_center(fout[k], start, stop, action, grating, catg_list[k])
            if dout == False:
                break

            [estimates, diff_data, f_time, sec1, sec2, sec3] = dout
#
#--- update data table
#
            update_table(sec1, sec2, sec3, action, grating, catg_list[k], start, stop) 
#
#--- create drift data plot
#
            plot_drift(fout[k], f_time, estimates, start, stop, action, grating, catg_list[k])
#
#--- create deviation data plot
#
            plot_dev(f_time, diff_data, action, grating, catg_list[k], start, stop)

#---------------------------------------------------------------------------------------
#-- find_grating_insr_retr: find time when the grating motion happened                --
#---------------------------------------------------------------------------------------

def find_grating_insr_retr(l_time):
    """
    find time when the grating motion happened
    input:  none, but read from /data/mta_www/mta_otg/OTG_filtered.rdb
    output: action  --- a list of movement
            grating --- a lit of grating
            tstart  --- a list of starting time in seconds from 1998.1.1
            tstop   --- a list of stopping time in seconds from 1998.1.1
    """
#
#--- read grating motion
#
    gdata   = read_data_file(grating_data)
    gdata   = gdata[2:]
    
    action  = []
    grating = []
    tstart  = []
    tstop   = []
    for ent in gdata:
        atemp = re.split('\s+', ent)
#
#--- only new observations are kept
#
        start = convert_to_stime(atemp[2])
        if start < l_time:
            continue
#
#--- only the data show the movement are used
#
        if atemp[0] in ('INSR', 'RETR'):

            action.append(atemp[0])
            grating.append(atemp[1])
            tstart.append(start)
            tstop.append(convert_to_stime(atemp[4]))

    return [action, grating, tstart, tstop]

#---------------------------------------------------------------------------------------
#-- extract_each_drift_data: extract roll, pitch, yaw data around movement            --
#---------------------------------------------------------------------------------------

def extract_each_drift_data(start, stop):
    """
    extract roll, pitch, yaw data around movement
    input:  start   --- starting time in seconds from 1998.1.1
            stop    --- ending time in seconds from 1998.1.1
    output: roll    --- a list of arrays of time and data; roll
            pitch   --- a list of arrays of time and data; pitch
            yaw     --- a list of arrays of time and data; yaw
    """
#
#--- find a mid point and the range
#
    mid    = 0.5 * (stop + start)
    diff   = stop  - start
    dstart = start - diff
    dstop  = stop  + diff
#
#--- extract data from ska database
#
    roll  = get_data_from_ska('AOGBIAS1', dstart, dstop)
    pitch = get_data_from_ska('AOGBIAS2', dstart, dstop)
    yaw   = get_data_from_ska('AOGBIAS3', dstart, dstop)

    roll  = [roll[0]  - mid, roll[1]  * 1.0e8]
    pitch = [pitch[0] - mid, pitch[1] * 1.0e8]
    yaw   = [yaw[0]   - mid, yaw[1]   * 1.0e8]

    return [roll, pitch, yaw]

#---------------------------------------------------------------------------------------
#-- fit_polinom_to_center: fitting a 5th degree polinomial to the data and find differences 
#---------------------------------------------------------------------------------------

def fit_polinom_to_center(fdata, start, stop, action, grating, catg):
    """
    fitting a 5th degree polinomial to the data and find differences
    input:  fdata   --- a list of arrays of time and data
            start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
            action  --- movement
            grating --- grating
            cag     --- catogry (roll/pitch/yaw)
    output: estimates   --- a list of model fitted data
            diff_data   --- a list of difference between themodel and the data
            f_time      --- a list of time for the selected data period
            sec1,sec2,sec3  --- list of [avg, std]  of three sections
    """
#
#--- set fitting range
#
    tdiff  = stop  - start
    dstart =  -1.5 * tdiff
    dstop  =   1.5 * tdiff
#
#--- limit data to the fitting range
#
    t_array  = fdata[0]
    v_array  = fdata[1]
    index    = (t_array > dstart) & (t_array < dstop)
    f_time   = t_array[index]
    f_data   = v_array[index]
#
#--- fit the data
#
    paraminitial = [0.0 for i in range(0, 5)]


    try:
        popt, pcov = curve_fit(p_model, f_time, f_data, p0=paraminitial)
    except:
        print("Something wrong with curve fitting")
        return False
#
#--- create lists of data of estimated fitting and deviations
#
    [estimates, diff_data] = compute_difference(f_time, f_data, popt)
#
#--- find avg and std of three sections
#
    [sec1, sec2, sec3]     = compute_avg_of_three_sections(f_time, diff_data, start, stop)
#
#--- write out the polinomial fitting result
#
    write_poli_fitting_result(popt, start, stop, action, grating, catg)

    return [estimates, diff_data, f_time,  sec1, sec2, sec3]

#---------------------------------------------------------------------------------------
#-- compute_difference: create model fitting results and a list of difference from the data 
#---------------------------------------------------------------------------------------

def compute_difference(f_time, f_data, popt):
    """
    create model fitting results and a list of difference from the data
    input:  f_time  --- an array of time data
            f_data  --- an array of data
            popt    --- a list of parameters
    output: estimates   --- a list of model fitted data
            diff_data   --- a list of difference between themodel and the data
    """
    [a0, a1, a2, a3, a4] = popt

    estimates = []
    diff_data = []
    for k in range(0, len(f_time)):
        est  = p_model(f_time[k], a0, a1, a2, a3, a4)
        diff = f_data[k] - est
        estimates.append(est)
        diff_data.append(diff * 1.0e2)

    return [estimates, diff_data]

#---------------------------------------------------------------------------------------
#-- compute_avg_of_three_sections: compute avg and std of three sctions               --
#---------------------------------------------------------------------------------------

def compute_avg_of_three_sections(f_time, diff_data, start, stop):
    """
    compute avg and std of three sctions
    input:  f_time  --- an array of time data
            diff_data   ---     an array of data
            start       --- starting time in seconds from 1998.1.1
            stop        --- stopping time in seconds from 1998.1.1
    output: [[<avg>, <std>], ...] --- three section avg and std
    """
    hdiff = 0.5 * (stop - start)
    dstart = -hdiff
    dstop  =  hdiff

    index = f_time < dstart
    out1  = select_and_avg(index, diff_data)

    index = (f_time >= dstart) & (f_time < dstop)
    out2  = select_and_avg(index, diff_data)

    index = f_time >= dstop
    out3  = select_and_avg(index, diff_data)

    return [out1, out2, out3]

#---------------------------------------------------------------------------------------
#-- select_and_avg: compute avg and std                                               --
#---------------------------------------------------------------------------------------

def select_and_avg(index, idata):
    """
    compute avg and std 
    input:  index   --- a list of indices to select data
            idata   --- a array of data
    output: avg     --- avg
            std     --- std
    """
    idata    = numpy.array(idata)
    selected = idata[index]
    avg      = numpy.mean(selected)
    std      = numpy.std(selected)

    return [avg, std]

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def p_model(x, a0, a1, a2, a3, a4):

    out = a0  + a1 * x + a2 * x**2 + a3 * x**3 + a4 * x**4

    return out

#---------------------------------------------------------------------------------------
#-- write_poli_fitting_result: printing out polinomial parameters                     --
#---------------------------------------------------------------------------------------

def write_poli_fitting_result(params, start, stop, action, grating, catg):
    """
    printing out polinomial parameters
    input:  params  --- polinomial fitting results (with params to get fitting parameters)
            start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
            action  --- movement
            grating --- grating
            catg    --- category
    output: <data_dir>/Polinomial_results/<GRATING>_<ACTION>/<time>_pol_fit_result
    """
    line   = str(int(0.5 * (start+ stop)))
    for ent in params:
        line = line + "\t%2.4e" % ent
    line   = line + '\n'
#
#--- create output directory if it does not exist
#
    out = data_dir + 'Polinomial_results/' 
    cmd = 'mkdir -p ' + out
    os.system(cmd)
#
#--- print the result
#
    out = out + 'poli_fit_' +  catg.lower() + '_' +  grating.lower() + '_' +  action.lower()
    with open(out, 'a') as fo:
        fo.write(line)

#---------------------------------------------------------------------------------------
#-- convert_to_stime: convert frational year to Chandra time                          --
#---------------------------------------------------------------------------------------

def convert_to_stime(tent):
    """
    convert frational year to Chandra time
    input:  tent    --- time in frational year
    output: out     --- time in seconds from 1998.1.1
    """
    atemp = re.split('\.', str(tent))
    tv    = atemp[0]
    year  = tv[0] + tv[1] + tv[2] + tv[3]
    fday  = tv[4] + tv[5] + tv[6]

    stime = str(year) + ':' + str(fday) + ':00:00:00'

    sv    = float('0.' + atemp[1]) * 86400.0

    stime = Chandra.Time.DateTime(stime).secs + sv

    return stime

#---------------------------------------------------------------------------------------
#-- update_table: update data table                                                   --
#---------------------------------------------------------------------------------------

def update_table(sec1, sec2, sec3, action, grating, catg, start, stop):
    """
    update data table 
    input:  sec1    --- [avg, std] of before the movement
            sec2    --- [avg, std] of during the movement
            sec3    --- [avg, std] of after  the movement
            action  --- movement
            grating --- grating
            catg    --- category
            start   --- start time in seconds from 1998.1.1
            stop    --- stop  time in seconds from 1998.1.1
    output: updated <data_dir>/gyro_drift_<catg>
    """
    line    = str(int(0.5 * (start + stop))) + '\t'
    line    = line + '%2.3f+/-%2.3f\t' % (sec1[0], sec1[1])
    line    = line + '%2.3f+/-%2.3f\t' % (sec2[0], sec2[1])
    line    = line + '%2.3f+/-%2.3f\t' % (sec3[0], sec3[1])
    line    = line + '%2.3f\t'         % comp_ratio(sec1[1], sec2[1])
    line    = line + '%2.3f\t'         % comp_ratio(sec3[1], sec2[1])
    line    = line + '%2.3f\t'         % comp_ratio(sec1[1], sec3[1])

    #line    = line + grating + '\t' + action + '\t'
    line    = line + '%3.1f' % (stop - start) 
    line    = line + '\n'

    outfile = data_dir + 'gyro_drift_' + catg + '_' +grating.lower() + '_' + action.lower()
    if os.path.isfile(outfile):
        with open(outfile, 'a') as fo:
            fo.write(line)

    else:
        with open(outfile, 'w') as fo:
            fo.write("#time       before          during          after           ")
            fo.write("b/d     a/d     b/a     duration\n")
            fo.write(line)


#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def comp_ratio(a, b):
    if b == 0:
        return 0.0
    else:
        return a / b

#---------------------------------------------------------------------------------------
#-- plot_drift: plotting gyro drift data                                              --
#---------------------------------------------------------------------------------------

def plot_drift(data_set, f_time, estimates, start, stop, action, grating, catg):
    """
    plotting gyro drift data
    input:  ftime   --- a list of time
            vdata   --- y data
            action  --- movement
            grating --- grating
            catg    --- category
            start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<time>/gyro_drift_<catg>.png
    """
#
#--- center the time to midlle
#
    ctime  = 0.5 * (start + stop)
    diff   = stop - start
    dstart = start - ctime
    dstop  = stop  - ctime
    tarray = data_set[0] 
    darray = data_set[1]
#
#--- set sizes
#
    fsize      = 18
    color      = 'blue'
    color2     = 'green'
    color3     = 'red'
    marker     = '.'
    psize      = 8
    lw         = 3
    width      = 10.0
    height     = 7.0
    resolution = 200
    [xmin, xmax, ymin, ymax] = set_range(dstart, dstop, data_set[1])

#
#--- output file name
#
    outdir  = web_dir + 'Individual_plots/' + grating.upper() 
    outdir  = outdir  + '_' + action.upper() + '/' + str(int(ctime)) + '/'

    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)

    outname = outdir  + 'gyro_drift_'  + catg + '.png'
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
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
    plt.plot(tarray, darray, color=color, marker=marker, markersize=psize, lw=0)
#
#--- plot fitted data
#
    plt.plot(f_time, estimates, color=color2, marker=marker, markersize=0, lw=5, alpha=0.6)
#
#--- add start and stop lines
#
    plt.plot([0, 0],[ymin, ymax], color='black', marker=marker, markersize=0, linestyle='--', lw=2)
    plt.plot([xmin, xmax],[0, 0], color='black', marker=marker, markersize=0, linestyle='--', lw=2)

    plt.plot([dstart, dstart],[ymin, ymax], color=color3, marker=marker, markersize=0, lw=4, alpha=0.3)
    plt.plot([dstop,  dstop], [ymin, ymax], color=color3, marker=marker, markersize=0, lw=4, alpha=0.3)
#
#--- add label
#
    plt.xlabel('Time (sec)')
    plt.ylabel(catg.capitalize())
#
#--- save the plot in png format
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)
    
    plt.close('all')

#---------------------------------------------------------------------------------------
#-- plot_dev: plotting deviation data                                                 --
#---------------------------------------------------------------------------------------

def plot_dev(ftime, vdata, action, grating, catg, start, stop):
    """
    plotting deviation data
    input:  ftime   --- a list of time
            vdata   --- y data
            action  --- movement
            grating --- grating
            catg    --- category
            start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<time>/deviation_<catg>.png
    """
#
#--- center the time to midlle
#
    ctime  = 0.5 * (start + stop)
    dstart = start - ctime
    dstop  = stop  - ctime
#
#--- set sizes
#
    fsize      = 18
    color      = 'blue'
    color2     = 'green'
    color3     = 'red'
    marker     = '.'
    psize      = 8
    lw         = 3
    width      = 10.0
    height     = 7.0
    resolution = 200
    [xmin, xmax, ymin, ymax] = set_range(dstart, dstop, vdata, chk =1)
    if ymax > abs(ymin):
        ymin = -1.0 * ymax
    else:
        ymax = abs(ymin)
        ymin = - ymax
#
#--- output file name
#
    outdir  = web_dir + 'Individual_plots/' + grating.upper() + '_' 
    outdir  = outdir  + action.upper() + '/' + str(int(ctime)) + '/'

    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)

    outname = outdir  + 'deviation_'  + catg + '.png'
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
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
    plt.plot(ftime, vdata, color=color, marker=marker, markersize=psize, lw=0)
#
#--- add start and stop lines
#
    plt.plot([0,0 ],[ymin, ymax], color='black', marker=marker, markersize=0, linestyle='--', lw=2)
    plt.plot([xmin, xmax],[0, 0], color='black', marker=marker, markersize=0, linestyle='--', lw=2)
    plt.plot([dstart, dstart],[ymin, ymax], color=color3, marker=marker, markersize=0, lw=4, alpha=0.3)
    plt.plot([dstop,  dstop], [ymin, ymax], color=color3, marker=marker, markersize=0, lw=4, alpha=0.3)
#
#--- add label
#
    plt.xlabel('Time (sec)')
    plt.ylabel(catg.capitalize())
#
#--- save the plot in png format
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')

#---------------------------------------------------------------------------------------
#-- set_range: set plotting range                                                    ---
#---------------------------------------------------------------------------------------

def set_range(start, stop, ydata, chk=0):
    """
    set plotting range
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            ydata   --- ydata
            chk     --- if chk > 0; take the range to 3 times of the 
                        stop - start range
    output: [xmin, xmax, ymin, ymax]
    """

    tdiff = stop - start
    cent  = 0.5 * (start + stop)
    xmin = start - 1.2 * tdiff
    xmax = stop  + 1.2 * tdiff

    ymin = min(ydata)
    ymax = max(ydata)
    diff = ymax - ymin
    if diff == 0:
        yavg = numpy.mean(ydata)
        ymin = yavg - 0.1
        ymax = yavg + 0.1
    else:
        ymin -= 0.1 * diff
        ymax += 0.1 * diff

    return [xmin, xmax, ymin, ymax]

#---------------------------------------------------------------------------------------
#-- create_drift_html_page: create a web page for a given plot group                  --
#---------------------------------------------------------------------------------------

def create_drift_html_page(start, stop, grating, action, savef):
    """
    create a web page for a given plot group
    input:  start   --- movement starting time in seconds from 1998.1.1
            stop    --- movement stopping time in seconds from 1998.1.1
            grating --- grating
            action  --- movement direction (inser or reter)
            savef   --- a list of lists of fitting results of three sections of three categories
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<time in seconds>/<gating>_<action>_<catg>_<time>.html
    """
#
#--- find mid time 
#
    stime  = int(0.5 * (start+ stop))
    ltime  = Chandra.Time.DateTime(stime).date
#
#--- set the directory which keeps plots
#
    outdir = web_dir + 'Individual_plots/' + grating.upper() + '_' + action.upper() + '/' 
#
#--- create table of plots
#
    line   = '<table border=0>\n'
    for k in range(0, 3):
#
#--- create stat results table for the html page
#
        results = create_result_table(savef[k])
#
#--- category of this data
#
        catg = catg_list[k]
#
#--- names of two plots for this category
#
        outname1 = outdir  + str(stime) + '/' + 'gyro_drift_' +  grating + '_' + action + '_' + catg +' _'\
                           + str(int(0.5 * (start + stop))) +  '.png'

        outname2 = outdir  + str(stime) + '/' + 'deviation_'  +  grating + '_' + action + '_' + catg + '_'\
                           + str(int(0.5 * (start + stop))) +  '.png'

        line     = line + '<tr>\n'
        line     = line + '<th><img src="' + outname1 + '" width=40%"></th>\n'
        line     = line + '<th><img src="' + outname2 + '" width=40%"></th>\n'
        line     = line + '<td>' + results + '</td>\n'
        line     = line + '</tr>\n'

    line = line + '</table>'
#
#--- read the template
#
    tname    = house_keeping + 'drift_plot_template'
    f        = opne(tnane , 'r')
    template = f.read()
    f.close()
#
#--- insert the data
#
    template = template.replace('#GRAT#', grating)
    template = template.replace('#ACT#',  action)
    template = template.replace('#STIME#', mtime)
    template = template.replace('#LTIME#', ltime)
    template = template.replace('#TABLE#', line)
#
#--- output file name
#
    outdir  = web_dir + 'Individual_plots/' + grating.upper() + '_' + action.upper() + '/'
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)

    outname = outdir  +  grating + '_' + action + '_' + catg + '_' + str(int(0.5 * (start + stop))) +  '.html'
#
#--- print out the result
#
    fo      = open(outname, 'w')
    fo.wirte(template)
    fo.close()

#---------------------------------------------------------------------------------------
#-- create_result_table: create the result table                                      --
#---------------------------------------------------------------------------------------

def create_result_table(data):
    """
    create the result table
    input: data     --- a list of list of fitting results
                    [[<before avg>, <before std>], [<during avg>, <during std>], [..., ...]]
    output: line    --- a html element
    """
#
#--- before the movement
#
    bavg  = data[0][0]
    bstd  = data[0][1]
#
#--- during the movement
#
    mavg  = data[1][0]
    mstd  = data[1][1]
#
#--- after the movement
#
    aavg  = data[2][0]
    astd  = data[2][1]
#
#--- create data table
#
    line = '<ul>\n'
    line = line + '<li>Before: %2.3f+/-%2.3f' % (bavg, bstd) + '</li>\n'
    line = line + '<li>During: %2.3f+/-%2.3f' % (mavg, mstd) + '</li>\n'
    line = line + '<li>After:  %2.3f+/-%2.3f' % (aavg, astd) + '</li>\n'

    line = line + '<li>Before/During: %2.3f' % comp_ratio(bstd, mstd) + '</li>\n'
    line = line + '<li>After/During:  %2.3f' % comp_ratio(astd, mstd) + '</li>\n'
    line = line + '<li>Before/After:  %2.3f' % comp_ratio(astd, bstd) + '</li>\n'
    line = line + '</ul>\n'

    return line

#---------------------------------------------------------------------------------------
#-- find_last_entry: find the last entry date                                         --
#---------------------------------------------------------------------------------------

def find_last_entry():
    """
    find the last entry date
    input:  none but read from <data_dir>/gyro_drift_yaw
    output: ltime   --- time in seconds from 1998.1.
    """
    save = []
    for tail in ['hetg_insr', 'hetg_retr', 'letg_insr', 'letg_retr']:
        try:
            ifile = data_dir + 'gyro_drift_yaw_' + tail
            data  = read_data_file(ifile)
            atemp = re.split('\s+', data[-1])
            ltime = float(atemp[0])
        except:
            ltime = 0

        save.append(ltime)

    ltime = max(save)

    return ltime

#---------------------------------------------------------------------------------------
#-- get_data_from_ska: extract data from ska database                                 --
#---------------------------------------------------------------------------------------

def get_data_from_ska(msid, tstart, tstop):
    """
    extract data from ska database
    input:  msid    --- msid
            tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: time    --- a list of time
            data    --- a list of data
    """

    out  = fetch.MSID(msid, tstart, tstop)
    time = out.times
    data = out.vals

    return [time, data]


#---------------------------------------------------------------------------------------
#-- read_data_file: read a data file                                                  --
#---------------------------------------------------------------------------------------

def read_data_file(ifile, spliter = '', remove=0, skip=''):
    """
    read a data file
    input:  infile  --- input file name
            spliter --- if you want to a list of lists of data, provide spliter, e.g.'\t+'
            remove  --- the indicator of whether you want to remove the data after read it. default=0: no
            skip    --- whether skip the line if marked. default:'' --- don't skip
    output: data    --- either a list of data lines or a list of lists
    """


    try:
        f    = open(ifile, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    except:
        return []

    if remove > 0:
        mcf.rm_files(ifile)

    if spliter != '':
        atemp = re.split(spliter, data[0])
        alen  = len(atemp)
        save  = []
        for k in range(0, alen):
            save.append([])

        for ent in data:
            if skip != '':
                if ent[0] == skip:
                    continue
            atemp = re.split(spliter, ent)
            for k in range(0, alen):
                try:
                    val = float(atemp[k])
                except:
                    val = atemp[k].strip()

                save[k].append(val)
        return save
    else:
        return data

#---------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST   --
#---------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#---------------------------------------------------------------------------------------

    def test_find_grating_insr_retr(self):

        [action, grating, tstart, tstop]  = find_grating_insr_retr(0)
        k = 100
        print(str(action[k]) + '<-->' + str(grating[k]) + '<-->' + str(tstart[k]) + '<-->' + str(tstop[k]))

#---------------------------------------------------------------------------------------

    def test_extract_each_drift_data(self):

        begin = 646978280
        end   = 646978300
        out   = extract_each_drift_data(begin, end)

        print(str(out[0][0][:10]))

#---------------------------------------------------------------------------------------

    def test_fit_polinom_to_center(self):

        begin = 646978280
        end   = 646978300
        out   = extract_each_drift_data(begin, end)

        start = 646978291
        stop  = 646978314

        [estimates, diff_data, f_time, sec1, sec2, sec3] = fit_polinom_to_center(out[0], start, stop)
        print(str(estimates[:10]))
        print(str(diff_data[:10]))
        print(str(sec1))
        print(str(sec2))
        print(str(sec3))

#---------------------------------------------------------------------------------------

    def test_convert_to_stime(self):

        ttime = "2000160.04125300"
        stime = convert_to_stime(ttime)

        print("TIME FORMAT CONVERSION: " +  str(ttime) + '<--->' + str(stime))

#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1].lower() == 'test':
#
#--TEST TEST TEST TEST TEST TEST ----------------------------
#

            sys.argv = [sys.argv[0]]
            unittest.main()

#
#-- REGULAR RUN                  ----------------------------
#
        else:
            extract_gyro_data()
    else:
        extract_gyro_data()
