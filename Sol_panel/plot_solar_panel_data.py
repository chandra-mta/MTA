#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       plot_solar_panel_data.py: plot soloar panel related data                                #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 12, 2021                                                       #
#                                                                                               #
#################################################################################################
import os
import sys
import re
import string
import math
import numpy
import time
import Chandra.Time
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
path = '/data/mta/Script/Sol_panel/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
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
import find_moving_average        as mavg       #---- contains moving average routine
import check_limit_val            as clv        #---- contains limit related routine
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few lists
#
msid_list  = ['tmysada', 'tpysada', 'tsamyt', 'tsapyt', 'tfssbkt1', 'tfssbkt2',\
              'tpc_fsse', 'elbi', 'elbv', 'obattpwr', 'ohrmapwr', 'oobapwr']   
tchk_list  = [2,2,2,2,2,2,2,0,0,0,0,0]          #--- indicator of whether msid is with a temperature in F
angle_list = [40, 60, 80, 100, 120, 140, 160]

#---------------------------------------------------------------------------------------
#-- plot_solar_panel_data: run plotting routine for all angle intervals              --
#---------------------------------------------------------------------------------------

def plot_solar_panel_data():
    """
    run plotting routine for all angle intervals
    input:  none but read data from <data_dir>
    output: <web_dir>/Plots/<Msid>/msid_angle<angle>.png
    """
#
#--- plot each angle interval data
#
    for angle in angle_list:
        print("Processing ANGLE:" + str(angle))
#
#--- read data
#
        dfile = data_dir + 'solar_panel_angle_' + str(angle)
        our   = mcf.read_data_file(dfile)
        data  = []
        for ent in data:
            if ent[0] == '#':
                continue
            else:
                data.append(ent)

        if len(data) < 2:
            exit(1)

#
#--- plot time trend of each msid
#
        plot_each_msid(data, angle=angle)
#
#--- plot ysada temp vs elbi
#
        plot_sada_elbi(data, angle)
#
#--- plot full data
#
#    print("Plotting All Data Points")
#    dfile  = data_dir + 'solar_panel_all_data'
#    fdata  = plot_each_msid(dfile, dreturn=1)

#---------------------------------------------------------------------------------------
#-- plot_each_msid: go through each msid and create plots                             --
#---------------------------------------------------------------------------------------

def plot_each_msid(data, angle='', dreturn=0):
    """
    go through each msid and create plots
    input:  data    --- a list of lists of data
            angle   --- angle of the data. default: '' --- use full data set
            dretun  --- if 1, return the list of lists of data
    output: <web_dir>/Plots/<Msid>/msid_angle<angle>.png
    """
#
#--- set the end of the x plot range
#
    lyear  = time.strftime("%Y", time.gmtime())
    lyear  = int(lyear) + 1
#
#--- convert time into fractional year
#
    tcol   = data[0]
    tcol   = convert_time_to_year(tcol)
#
#--- plot each msid
#
    for k in range(0, len(msid_list)):
        msid  =   msid_list[k]
        sdata = data[k+2]
#
#--- find y plot range
#
        try:
            [x, y, ymin, ymax] = find_range(tcol, sdata)
            plot_data(x, y, 1999, lyear, ymin, ymax, msid, angle)
        except:
            pass

    if dreturn > 0:
        return data

#---------------------------------------------------------------------------------------
#-- find_range: remove outliers and then set y axis plotting range                    --
#---------------------------------------------------------------------------------------

def find_range(x, y, dsize=10):
    """
    remove outliers and then set y axis plotting range
    input:  x       --- a list of independent variable
            y       --- a list of dependent variable
            dsize   --- how to set digit of the limit defalut: 10 --- range is set at value of 10
    output: x       --- a list of cleaned up x
            y       --- a list of cleaned up y
            dmin    --- ymin
            dmax    --- ymax
    """
    x     = numpy.array(x)
    y     = numpy.array(y)
    avg   = numpy.mean(y)
    sd    = numpy.std(y)

    bot   = avg - 3.5 * sd
    top   = avg + 3.5 * sd
    index = (y > bot) & (y < top)

    x     = list(x[index])
    y     = list(y[index])

    dmin  = dsize * int(min(y)/dsize)
    dmax  = dsize * int(max(y)/dsize) + 2 * dsize

    return [x, y, dmin, dmax]

#---------------------------------------------------------------------------------------
#-- plot_data: plot a single panel data                                              --
#---------------------------------------------------------------------------------------

def plot_data(x, y, xmin, xmax, ymin, ymax, msid, angle):
    """
    plot a single panel data
    input:  x       --- a list of independent variable
            y       --- a list of dependent variable
            xmin    --- xmin of the plotting range
            xmax    --- xmax of the plotting range
            ymin    --- ymin of the plotting range
            ymax    --- ynax of the plotting range
            misd    --- msid
            angle   --- angle 
    output: <web_dir>/Plots/<<Msid>/msid_angle<angle>.png; if it full, <msid>.png
    """
#
#--- set sizes
#
    fsize      = 18
    color      = 'blue'
    color2     = 'red'
    marker     = '.'
    psize      = 4
    lw         = 4
    width      = 10.0
    height     = 5.0
    resolution = 200
#
#--- output file name
#
    outdir  = web_dir + 'Plots/' + msid.capitalize() + '/' 
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)

    if angle == '':
        outname = outdir + msid + '.png'
    else:
        outname = outdir + msid + '_angle' + str(angle) + '.png'
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
#--- find envelopes
#
    [xv, movavg, sigma, min_sv, max_sv, ym, yb, yt, y_sig] \
                            = mavg.find_moving_average(x, y, 1, 4, nodrop=3)
#
#--- plot data
#
    plt.plot(x, y, color=color, marker=marker, markersize=psize, lw=0)
#
#--- plot envelopes
#
    plt.plot(xv, yb, color=color2, marker=marker, markersize=0, lw=lw)
    plt.plot(xv, ym, color=color2, marker=marker, markersize=0, lw=lw)
    plt.plot(xv, yt, color=color2, marker=marker, markersize=0, lw=lw)
#
#--- plot limit line
#
    [lstart, lstop, y_min, y_max] = find_limit(msid)
    for k in range(0, len(lstart)):
        if k > 0:
            plt.plot([lstop[k-1], lstart[k]], [y_min[k-1], y_min[k]], color='green', lw=1)
            plt.plot([lstop[k-1], lstart[k]], [y_max[k-1], y_max[k]], color='green', lw=1)

        plt.plot([lstart[k], lstop[k]], [y_min[k], y_min[k]], color='green', lw=1)
        plt.plot([lstart[k], lstop[k]], [y_max[k], y_max[k]], color='green', lw=1)

        ax.fill_between([lstart[k], lstop[k]], [y_min[k], y_min[k]],\
                         [y_max[k], y_max[k]], facecolor='green', alpha=0.05)
#
#--- add label
#
    plt.xlabel('Time (Year)')
    plt.ylabel(msid)
#
#--- save the plot in png format
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')

#---------------------------------------------------------------------------------------
#-- plot_sada_elbi: plot +y sada temp vs elbi value                                   --
#---------------------------------------------------------------------------------------

def plot_sada_elbi(data, angle):
    """
    plot +y sada temp vs elbi value
    input:  data    --- a list of lists of full data
            angle   --- angle of the data set
    output: <web_dir>/Plots/sada_elbi.png
    """

    sada = data[3]
    elbi = data[9]
#
#--- set sizes
#
    fsize      = 18
    color      = 'blue'
    color2     = 'red'
    marker     = '.'
    psize      = 4
    lw         = 4
    width      = 10.0
    height     = 10.0
    resolution = 200
    xmin       = 260
    xmax       = 300
    ymin       = 40
    ymax       = 80
    xpos       = 270
    ypos       = 78
#
#--- output file name
#
    outname = web_dir + 'Plots/SADA_ELBI/sada_elbi_angle' + str(angle) + '.png'
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
    plt.plot(sada, elbi, color=color, marker=marker, markersize=psize, lw=0)
#
#--- fitting line: 3rd deg polynomial
#
    [int, slp1, slp2]  = fit_poly(sada,elbi, 3)
    ps     = 265            #--- data seems to start around here and finish 298
    pe     = 298

    step   = float(pe - ps) / 100.0
    xf     = []
    yf     = []
    for k in range(0, 100):
        xv = ps + step * k
        xf.append(xv)
        yv = int + slp1 * xv + slp2 * xv * xv
        yf.append(yv)
    plt.plot(xf, yf, color=color2, marker=marker, markersize=0, lw=lw)
#
#--- add label
#
    plt.xlabel('+Y SADA Temperature')
    plt.ylabel("ELBI")
    line = 'Line Fit: %2.3f ' % int
    if slp1 < 0:
        line = line + ' - %2.3f*x'    % abs(slp1)
    else:
        line = line + ' + %2.3f*x'    % abs(slp1)

    if slp2 < 0:
        line = line + ' - %2.4f*x^2'  % abs(slp2)
    else:
        line = line + ' + %2.4f*x^2'  % abs(slp2)

    plt.text(xpos, ypos, line)
#
#--- save the plot in png format
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=resolution)

    plt.close('all')

#---------------------------------------------------------------------------------------
#-- convert_time_to_year: converting Chandra time to fractional year                  --
#---------------------------------------------------------------------------------------

def convert_time_to_year(tlist):
    """
    converting Chandra time to fractional year
    input:  tlist   --- a list of time in format of seconds from 1998.1.1
    output: save--- a list of time in format of fractional year
    """
    save = []
    for ent in tlist:
        ldate = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', ldate)
        year  = float(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])
     
        if mcf.is_leapyear(year):
            base = 366.0
        else:
            base = 365.0
     
        fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base
        save.append(fyear)
    
    return save

#---------------------------------------------------------------------------------------
#-- find_limit: find yellow limits for a given msid                                   --
#---------------------------------------------------------------------------------------

def find_limit(msid):
    """
    find yellow limits for a given msid
    input:  msid    --- msid
    output: tb_list --- a list of starting time in frational year format
            te_list --- a list of stopping time in frational year format
            y_min   --- a list of the lower limit values
            y_max   --- a list of the upper limit values
    """
#
#--- find whether msid is temperature
#
    for k in range(0, len(msid_list)):
        if msid_list[k] == msid:
            break
    tchk = tchk_list[k]
#
#--- get the limit from glimmon
#
    out     = clv.read_glimmon_main(msid, tchk)
#
#--- change the data arrangement
#
    tb_list = []
    te_list = []
    y_min   = []
    y_max   = []

    for ent in out:
        tb_list.append(ent[0])
        te_list.append(ent[1])
        y_min.append(ent[2])
        y_max.append(ent[3])
#
#--- convert time in fractional year
#
    tb_list = convert_time_to_year(tb_list)
    te_list = convert_time_to_year(te_list)

    return [tb_list, te_list, y_min, y_max]
    
#---------------------------------------------------------------------------------------
#-- fit_poly: estimate polynomial fitting coefficients                                --
#---------------------------------------------------------------------------------------

def fit_poly(x, y, nterms):

    """
    estimate polynomial fitting coefficients
    Input:  x       --- independent variable (array)
            y       --- dependent variable (array)
            nterms  --- degree of polynomial fit
    Output: out     --- array of polynomial fit coefficient
    
    """
    d = numpy.array(x)
    v = numpy.array(y)

    try:
        out = numpy.polyfit(d, v, nterms)
    except:
        out = numpy.zeros(nterms)
        print("Something wrong with polinomial fit")
        raise SystemExit
    
    return out

#---------------------------------------------------------------------------------------------------
#-- residuals: compute residuals  --- NOT USED                                                   ---
#---------------------------------------------------------------------------------------------------

def residuals(p, data):

    """
    compute residuals
    input:  p       --- parameter array
            data    ---  data (x, y)  x and y must be numpyed
    """
    x, y = data
    
    return y - model(p, x)

#---------------------------------------------------------------------------------------------------
#-- model: the model to be fit   --- NOT USED                                                    ---
#---------------------------------------------------------------------------------------------------

def model(p, x):

    """
    the model to be fit
    Input:  p   --- parameter array
            x   --- independent value (array --- numpyed)
    """
    
    plen = len(p)
    yest = [p[0] for i in range(0, len(x))]
    for i in range(1, plen):
        yest += p[i] * x**i
    
    return yest


#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_solar_panel_data()
