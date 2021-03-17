#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       hrma_plot_trends.py: create hrma src data trend plots                                   #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 15, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits  as pyfits
import time
import Chandra.Time

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
path = '/data/mta/Script/Hrma_src/Scripts/house_keeping/dir_list'

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
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp space
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
x_dist  = 500
x_dist2 = 1300

#-----------------------------------------------------------------------------------------
#-- hrma_plot_trends: creates hrma src2 related data                                   ---
#-----------------------------------------------------------------------------------------

def hrma_plot_trends(year):
    """
    creates hrma src2 related data
    input:  year    --- the year of which you want to created the plots. if <blank>, plot this year
    output: <web_dir>/Plots/<category>/<instrument>/*.png
    """

    if year == '':
        yday   = float(time.strftime("%j", time.gmtime()))
        year   = time.strftime("%Y", time.gmtime())
        iyear  = int(float(year))
#
#--- if it is a beginning of the year, just update the last year
#
        if yday < 15:
            stday  = str(iyear -1) + ':001:00:00:00'
            ystart = Chandra.Time.DateTime(stday).secs

            stday  = year + ':001:00:00:00'
            ystop  = Chandra.Time.DateTime(stday).secs

        else:
            stday  = year + ':001:00:00:00'
            ystart = Chandra.Time.DateTime(stday).secs

            stday  = time.strftime("%Y:%j:00:00:00", time.gmtime())
            ystop  = Chandra.Time.DateTime(stday).secs
    else:
        stday  = str(year) + ":001:00:00:00"
        ystart = Chandra.Time.DateTime(stday).secs
        stday  = str(year + 1) + ":001:00:00:00"
        ystop  = Chandra.Time.DateTime(stday).secs

    hdata = read_data()

    plot_sky_position(hdata[1], hdata[2], hdata[6], hdata[7], ystart, ystop, year)

    plot_psf(hdata[1], hdata[2], hdata[12], hdata[13], ystart, ystop, year)

    plot_roundness(hdata[1], hdata[2], hdata[10], hdata[13], ystart, ystop, year)

    plot_energy_radius(hdata[1], hdata[2], hdata[9], hdata[13], ystart, ystop, year)

    plot_dist_snr(hdata[1], hdata[2], hdata[8], hdata[13], ystart, ystop, year)

    plot_rotation(hdata[1], hdata[2], hdata[11], hdata[14], hdata[13], hdata[9], ystart, ystop, year)

#-----------------------------------------------------------------------------------------
#-- read_data: read data from hrma_src_data                                             --
#-----------------------------------------------------------------------------------------

def read_data():
    """
    read data from hrma_src_data
    input:  read from <data_dir>/hrma_src_data
    output: a list of arrays of:
                        0   obsid
                        1   inst
                        2   start
                        3   stop 
                        4   sim_x
                        5   sim_z
                        6   x
                        7   y
                        8   snr
                        9   ravg
                        10  rnd
                        11  rotang
                        12  psf
                        13  dist
                        14  angd
    """

    ifile = data_dir + 'hrma_src_data'
    data  = mcf.read_data_file(ifile)

    obsid = []
    inst  = []
    start = []
    stop  = []
    sim_x = []
    sim_z = []
    x     = []
    y     = []
    snr   = []
    ravg  = []
    rnd   = []
    rotang= []
    psf   = []
    dist  = []
    angd  = []
    for ent in data:
        atemp = re.split('\s+', ent)

        obsid.append(int(float(atemp[0])))
        inst.append(atemp[1])
        start.append(int(float(atemp[2])))
        stop.append(int(float(atemp[3])))
        sim_x.append(float(atemp[3]))
        sim_z.append(float(atemp[5]))
        x.append(float(atemp[6]))
        y.append(float(atemp[7]))
        snr.append(float(atemp[8]))
        ravg.append(float(atemp[9]))
        rnd.append(float(atemp[10]))
        rotang.append(float(atemp[11]))
        psf.append(float(atemp[12]))
        dist.append(float(atemp[13]))
        angd.append(float(atemp[14]))
#
#--- sort by time
#
    start.sort()
    start = numpy.array(start)
    sind  = start.argsort()

    obsid = numpy.array(obsid)[sind]
    inst  = numpy.array(inst)[sind]
    stop  = numpy.array(stop)[sind]
    sim_x = numpy.array(sim_x)[sind]
    sim_z = numpy.array(sim_z)[sind]
    x     = numpy.array(x)[sind]
    y     = numpy.array(y)[sind]
    snr   = numpy.array(snr)[sind]
    ravg  = numpy.array(ravg)[sind]
    rnd   = numpy.array(rnd)[sind]
    rotang= numpy.array(rotang)[sind]
    psf   = numpy.array(psf)[sind]
    dist  = numpy.array(dist)[sind]
    angd  = numpy.array(angd)[sind]


    return [obsid, inst, start, stop, sim_x, sim_z, x, y, snr, ravg, rnd, rotang, psf, dist, angd]

#-----------------------------------------------------------------------------------------
#-- plot_sky_position: plotting sky positino related plots                              --
#-----------------------------------------------------------------------------------------

def plot_sky_position(inst, stime, x, y, ystart, ystop, year):
    """
    plotting sky positino related plots
    input:  inst    --- instrument
            stime   --- starting time in sec from 1998.1.1
            x       --- x position
            y       --- y position
            ystart  --- starting time in sec from 1998.1.1 for yearlyt plot
            ystop   --- stopping time in sec from 1998.1.1 for yearlyt plot
            year    --- year of the yearly plot
    output: <web_dir>/Plots/Position/<inst>_sky_position.png
    """

    for det in ['acis_i', 'acis_s', 'hrc_i', 'hrc_s']:
        if det in ['acis_i', 'acis_s']:
            xmin = 2800
            xmax = 5200
            ymin = 2800
            ymax = 5200
#        elif det == 'acis_s':
#            xmin = 0
#            xmax = 7000
#            ymin = 1000
#            ymax = 8000
        elif det == 'hrc_i':
            xmin = 6000
            xmax = 26000
            ymin = 7000
            ymax = 27000
        else:
            xmin = 22000
            xmax = 42000
            ymin = 22000
            ymax = 42000

        xlabel = 'X Position'
        ylabel = 'Y Position'

        outdir = web_dir + 'Plots/Positions/' + det.capitalize() + '/' 
        cmd    = 'mkdir -p ' + outdir
        os.system(cmd)

        sind = inst == det
        xp   = x[sind]
        yp   = y[sind]
        st   = stime[sind]

        out  = outdir + det + '_sky_position.png'
        plot_panel(xp, yp, xmin, xmax, ymin, ymax, xlabel, ylabel, out)

#        tind = (st >= ystart) &(st < ystop)
#        xt   = xp[tind]
#        yt   = yp[tind]
#
#        out  = outdir + det + '_sky_position_' + str(year) + '.png'
#        plot_panel(xt, yt, xmin, xmax, ymin, ymax, xlabel, ylabel, out)


#-----------------------------------------------------------------------------------------
#-- plot_psf: plotting psf related plots                                                --
#-----------------------------------------------------------------------------------------

def plot_psf(inst, stime, psf, dist, ystart, ystop, year):
    """
    plotting psf related plots
    input:  inst    --- instrument
            stime   --- starting time in sec from 1998.1.1
            psf     --- psf
            dist    --- ditance from the center
            ystart  --- starting time in sec from 1998.1.1 for yearlyt plot
            ystop   --- stopping time in sec from 1998.1.1 for yearlyt plot
            year    --- year of the yearly plot
    output: <web_dir>/Plots/Psf/<inst>_dist_psf.png
            <web_dir>/Plots/Psf/<inst>_dist_psf_<year>.png
    """

    for det in ['acis_i', 'acis_s', 'hrc_i', 'hrc_s']:
        if det in  ['acis_i', 'acis_s']:
            xmin = 0
            xmax = x_dist 
            ymin = 0
            ymax = 20
        else:
            xmin = 0
            xmax = x_dist2
            ymin = 0
            ymax = 120

        xlabel = 'Off Axis Dist (arcsec)'
        ylabel = 'PSF (arcsec)'

        outdir =  web_dir + 'Plots/Psf/' + det.capitalize() + '/'
        cmd    = 'mkdir -p ' + outdir
        os.system(cmd)

        sind = inst == det
        xp   = dist[sind]
        yp   = psf[sind]
        st   = stime[sind]

        out  = outdir + det + '_dist_psf.png'
        plot_panel(xp, yp, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)
#
#--- yearly plot
#
        tind = (st >= ystart) &(st < ystop)
        xt   = xp[tind]
        yt   = yp[tind]

        out  = outdir + det +  '_dist_psf_' + str(year) + '.png'
        plot_panel(xt, yt, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

#-----------------------------------------------------------------------------------------
#-- plot_roundness: plotting roundness related plots                                    --
#-----------------------------------------------------------------------------------------

def plot_roundness(inst, stime, round, dist, ystart, ystop, year):
    """
    plotting roundness related plots
    input:  inst    --- instrument
            stime   --- starting time in sec from 1998.1.1
            round   --- roundness
            dist    --- ditance from the center
            ystart  --- starting time in sec from 1998.1.1 for yearlyt plot
            ystop   --- stopping time in sec from 1998.1.1 for yearlyt plot
            year    --- year of the yearly plot
    output: <web_dir>/Plots/Roundness/<inst>_dist_roundness.png
            <web_dir>/Plots/Roundness/<inst>_dist_roundness_<year>.png
    """

    for det in ['acis_i', 'acis_s', 'hrc_i', 'hrc_s']:
        if det in  ['acis_i', 'acis_s']:
            xmin = 0
            #xmax = 1100 
            xmax = x_dist 
            ymin = 1
            ymax = 4.5
        else:
            xmin = 0
            #xmax = 10000
            xmax = x_dist2 
            ymin = 0
            ymax = 4.5

        xlabel = 'Off Axis Distance (arcsec)'
        ylabel = 'Roundness'

        outdir = web_dir + 'Plots/Roundness/' + det.capitalize() + '/' 
        cmd    = 'mkdir -p ' + outdir
        os.system(cmd)


        sind = inst == det
        xp   = dist[sind]
        yp   = round[sind]
        st   = stime[sind]

        out  = outdir + det + '_dist_roundness.png'
        plot_panel(xp, yp, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

        tind = (st >= ystart) &(st < ystop)
        xt   = xp[tind]
        yt   = yp[tind]
#
#--- yearly plot
#
        out  = outdir + det + '_dist_roundness_' + str(year) + '.png'
        plot_panel(xt, yt, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

#        xlabel = 'Time (year)'

#        out  = outdir + det + '_time_roundness.png'
#        st   = convert_time_in_fyear(st)
#        xmax = int(max(st)) + 1
#        plot_panel(st, yp, 1999, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

#-----------------------------------------------------------------------------------------
#-- plot_energy_radius: plotting radius related plots                                   --
#-----------------------------------------------------------------------------------------

def plot_energy_radius(inst, stime, radius, dist, ystart, ystop, year):
    """
    plotting radius related plots
    input:  inst    --- instrument
            stime   --- starting time in sec from 1998.1.1
            radius  --- radius 
            dist    --- ditance from the center
            ystart  --- starting time in sec from 1998.1.1 for yearlyt plot
            ystop   --- stopping time in sec from 1998.1.1 for yearlyt plot
            year    --- year of the yearly plot
    output: <web_dir>/Plots/Radius/<inst>_dist_radius.png
            <web_dir>/Plots/Radius/<inst>_dist_radius_<year>.png
    """

    for det in ['acis_i', 'acis_s', 'hrc_i', 'hrc_s']:
        if det in  ['acis_i', 'acis_s']:
            xmin = 0
            #xmax = 1100
            xmax = x_dist 
            ymin = 0
            #ymax = 20
            ymax = 10
        else:
            xmin = 0
            #xmax = 10000
            xmax = x_dist2 
            ymin = 0
            #ymax = 600
            ymax = 80


        xlabel = 'Off Axis Distance (arcsec)'
        ylabel = 'Encircled Energy Radius'

        outdir = web_dir + 'Plots/Radius/' + det.capitalize() + '/' 
        cmd    = 'mkdir -p ' + outdir
        os.system(cmd)

        sind = inst == det
        xp   = dist[sind]
        yp   = radius[sind]
        st   = stime[sind]

        out  = outdir + det + '_dist_radius.png'
        plot_panel(xp, yp, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

        tind = (st >= ystart) &(st < ystop)
        xt   = xp[tind]
        yt   = yp[tind]
#
#--- yearly plot
#
        out  = outdir + det + '_dist_radius_' + str(year) + '.png'
        plot_panel(xt, yt, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)



#-----------------------------------------------------------------------------------------
#-- plot_dist_snr: plotting snr related plots                                          ---
#-----------------------------------------------------------------------------------------

def plot_dist_snr(inst, stime, snr, dist, ystart, ystop, year):
    """
    plotting snr related plots
    input:  inst    --- instrument
            stime   --- starting time in sec from 1998.1.1
            snr     --- snr
            dist    --- ditance from the center
            ystart  --- starting time in sec from 1998.1.1 for yearlyt plot
            ystop   --- stopping time in sec from 1998.1.1 for yearlyt plot
            year    --- year of the yearly plot
    output: <web_dir>/Plots/Snr/<inst>_dist_snr.png
            <web_dir>/Plots/Snr/<inst>_dist_snr_<year>.png
    """

    for det in ['acis_i', 'acis_s', 'hrc_i', 'hrc_s']:
        if det == 'acis_i':
            xmin = 0
            #xmax = 1100
            xmax = x_dist 
            ymin = 6
            ymax = 80
        elif det == 'acis_s':
            xmin = 0
            Exmax = 1100
            xmax = x_dist 
            ymin = 6
            #ymax = 300
            ymax = 150
        elif det in ['hrc_i', 'hrc_s']:
            xmin = 0
            #xmax = 10000
            xmax = x_dist2
            ymin = 6
            #ymax = 400
            ymax = 100


        xlabel = 'Off Axis Distance (arcsec)'
        ylabel = 'SNR'

        outdir = web_dir + 'Plots/Snr/' + det.capitalize() + '/' 
        cmd    = 'mkdir -p ' + outdir
        os.system(cmd)

        sind = inst == det
        xp   = dist[sind]
        yp   = snr[sind]
        st   = stime[sind]

        out  = outdir + det + '_dist_snr.png'
        plot_panel(xp, yp, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)
#
#--- yearly plot
#
        tind = (st >= ystart) &(st < ystop)
        xt   = xp[tind]
        yt   = yp[tind]

        out  = outdir + det + '_dist_snr_' + str(year) + '.png'
        plot_panel(xt, yt, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

#        out  = outdir + det + '_time_snr.png'
#        st   = convert_time_in_fyear(st)
#        xmax = int(max(st)) + 1
#        xlabel = 'Time (year)'
#        plot_panel(st, yp, 1999, xmax, ymin, ymax, xlabel, ylabel, out, width=15)


#-----------------------------------------------------------------------------------------
#-- plot_rotation: plotting rotation angle related plots                                --
#-----------------------------------------------------------------------------------------

def plot_rotation(inst, stime, rotang, angd, dist, rad,  ystart, ystop, year):
    """
    plotting rotation angle related plots
    input:  inst    --- instrument
            stime   --- starting time in sec from 1998.1.1
            rotang  --- rotation angle
            angd    --- rotation angle estimated from x and y
            dist    --- ditance from the center
            rad     --- roundness
            ystart  --- starting time in sec from 1998.1.1 for yearlyt plot
            ystop   --- stopping time in sec from 1998.1.1 for yearlyt plot
            year    --- year of the yearly plot
    output: <web_dir>/Plots/Rotation/<inst>_angd_rotang.png
            <web_dir>/Plots/Rotation/<inst>_dist_rotation.png
            <web_dir>/Plots/Rotation/<inst>_dist_rotation_<year>.png
    """
#
    for det in ['acis_i', 'acis_s', 'hrc_i', 'hrc_s']:

        xmin = 0
        xmax = 3.1
        ymin = 0
        ymax = 3.1
        xlabel = 'ANGD'
        ylabel = 'ROTANG'

        outdir = web_dir + 'Plots/Rotation/' + det.capitalize() + '/' 
        cmd    = 'mkdir -p ' + outdir
        os.system(cmd)

        sind = inst == det
        xp   = angd[sind]
        yp   = rotang[sind]
        st   = stime[sind]
        ds   = dist[sind]
        rd   = rad[sind]
#
#--- remove xp = 0 cases
#
        idx   = xp != 0
        xp    = xp[idx] 
        yp    = yp[idx] 
        st    = st[idx] 
        ds    = ds[idx] 
        rd    = rd[idx] 

        out  = outdir + det + '_angd_rotang.png'
        plot_panel(xp, yp, xmin, xmax, ymin, ymax, xlabel, ylabel, out)

#
#--- dist - rotang/angd
#
        xmin = 0
        if det in ['acis_i', 'acis_s']:
            #xmax = 1100
            xmax = x_dist
        else:
            #xmax = 10000
            xmax = x_dist2 
        ymin = 0
        ymax = 10 
        xlabel = 'Off Axis Distance (arcsec)'
        ylabel = 'ROTANG/ANGD'

        ratio = yp / xp
        out  = outdir + det + '_dist_rotation.png'
        plot_panel(ds, ratio, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)
#
#--- yearly plot
#
        tind = (st >= ystart) &(st < ystop)
        xt   = ds[tind]
        yt   = ratio[tind]

        out  = outdir + det + '_dist_rotation_' + str(year) + '.png'
        plot_panel(xt, yt, xmin, xmax, ymin, ymax, xlabel, ylabel, out, width=15)

#
#--- time - rotang/angd
#
#        out  = outdir + det + '_time_rot.png'
#        st   = convert_time_in_fyear(st)
#        xmax = int(max(st)) + 1
#        xlabel = 'Time (year)'
#        plot_panel(st, ratio, 1999, xmax, ymin, ymax, xlabel, ylabel, out, width=15)


#-----------------------------------------------------------------------------------------
#-- convert_time_in_fyear: convert Chandra time in a fractional year time               --
#-----------------------------------------------------------------------------------------

def convert_time_in_fyear(t_list):
    """
    convert Chandra time in a fractional year time 
    input:  t_list  --- a list of time in sec from 1998.1.1
    output: tsave   --- a list of time in fractional year
    """

    tsave = []
    for ent in t_list:
        etime  = Chandra.Time.DateTime(ent).date
        atemp  = re.split(':', etime)
        year   = float(atemp[0])
        yday   = float(atemp[1])
        hh     = float(atemp[2])
        mm     = float(atemp[3])
        ss     = float(atemp[4])

        if mcf.is_leapeyear(year):
            base = 366.0
        else:
            base = 365.0

        out = year + (yday + hh /24.0 + mm / 1440.0 + ss / 86400.0) / base
        tsave.append(out)

    tsave = numpy.array(tsave)

    return tsave


#-----------------------------------------------------------------------------------------
#-- plot_panel: plot data                                                              ---
#-----------------------------------------------------------------------------------------

def plot_panel(x, y, xmin, xmax, ymin, ymax, xlabel, ylabel, outname, width=10.0, height=10.0, fit=0):
    """
    plot data
    input:  x       --- a list of independent data
            y       --- a list of dependent data
            xmin    --- min of x plotting range
            xmax    --- max of x plotting range
            ymin    --- min of y plotting range
            ymax    --- max of y plotting range
            xlabel  --- a label of x axis
            ylabel  --- a label of y axis
            outname --- the output file name
            width   --- width of the plot in inch; default: 10 in
            height  --- height of the plot in inch: default: 10 in 
            fit     --- whether fit a line. if 0 no, otherwise, it also indicates the degree of polynomlal fit
    output: outname        
    """
#
#--- set params
#
    fsize  = 20
    pcolor = 'blue'
    lcolor = 'red'
    marker = '.'
    msize  = 8
    lw     = 4
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
#--- fit line
#
    if fit > 0:
        coeffs          = fit_line(x, y, fit)
        [x_est, y_est]  = estimate_fit_val(xmin, xmax, coeffs)
        
        plt.plot(x_est, y_est, color=lcolor, marker=marker, markersize=0, lw=lw)
    else:
        coeffs = []
#
#--- create plot and save
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(width, height)
    plt.tight_layout()
    plt.savefig(outname, format='png', dpi=200)
                
    plt.close('all')

    return coeffs

#-----------------------------------------------------------------------------------------
#-- fit_line: fit polynomial line on the given data                                     --
#-----------------------------------------------------------------------------------------

def fit_line(x, y, deg):
    """
    fit polynomial line on the given data
    input:  x       --- independent data
            y       --- dependent data
            deg     --- degree of polynomial
    output: coeffes --- a list of coefficients
    """
    ax     = numpy.array(x)
    ay     = numpy.array(y)
    coeffs = numpy.polyfit(ax, ay, deg)

    return coeffes

#-----------------------------------------------------------------------------------------
#-- estimate_fit_val: create a list of data points of theestimated line                 --
#-----------------------------------------------------------------------------------------

def estimate_fit_val(xmin, xmax, coeffs):
    """
    create a list of data points of theestimated line
    input:  xmin    --- x starting point
            xmax    --- x stopping point
            coeffs  --- coefficients of polynomial fitting
    output: x       --- x data 
            y_est   --- y data
    """

    deg = len(coeffs)

    step = (xmax - xmin) / 100.0
    x    = []
    for k in range(0, 100):
        x.append(xmin + step * k)

    y_est = []
    for val in x:
        sum =  coeffs[0]
        for k in range(1, deg):
            sum += coeffs[k] * val**k
        y_est.append(sum)

    return [x, y_est]

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    hrma_plot_trends(year)

#    for year in range(1999, 2021):
#        print("Year: " + str(year))
#        hrma_plot_trends(year)

