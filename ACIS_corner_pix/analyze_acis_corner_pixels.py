#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       analyze_acis_corner_pixels.py: extract acis evt1 data and analyze corner pixels #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 03, 2021                                               #
#                                                                                       #
#########################################################################################

import os
import os.path
import sys
import re
import string
import math
import numpy
import astropy.io.fits as pyfits
import time
import Chandra.Time
import unittest
from scipy.stats import norm as snorm
from scipy.stats import skewnorm

import matplotlib as mpl

if __name__ == '__main__':
    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot   as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
import matplotlib.gridspec as gridspec
#
#--- reading directory list
#
path = '/data/mta/Script/Corner_pix/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

    for ent in data:
        atemp = re.split(':', ent)
        var   = atemp[1].strip()
        line  = atemp[0].strip()
        exec("%s = %s" %(var, line))

sys.path.append(mta_dir)

import mta_common_functions as mcf
import robust_linear        as robust

ccds    = [2, 3, 6, 7]
ccd_id  = ["I2", "I3", "S2", "S3"]
binsize = 75
#
#--- set temp space
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#------------------------------------------------------------------------------------
#-- analyze_acis_corner_pixels: extract acis evt1 data and analyze corner pixels   --
#------------------------------------------------------------------------------------

def analyze_acis_corner_pixels(start, stop):
    """
    extract acis evt1 data and analyze corner pixels
    input:  start   --- start time either Chandra time or <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stop time either Chandra time or <yyyy>:<ddd>:<hh>:<mm>:<ss>
    output: <plot_dir>/Ind_Plots/<acis_prefix>_<ccd_id>_<tail>.png (e.g. acisf20783_I2_hist.png)
            <plot_dir>/Ind_Plots/<acis_prefix>_<taiL>.png (e.g., acisf20783_cp.png)
            <data_dir>/<ccd)_id>.dat
    """
    if start == '':
        today = time.strftime('%Y:%j:00:00:00', time.gmtime())
        stop  = Chandra.Time.DateTime(today).secs
        start = find_the_last_entry_date()
    elif stop == '':
        try:
            chk = float(start)
            stop = start + 86400.0
        except:
            start = Chandra.Time.DateTime(start).secs
            stop  = start + 86400.0
#
#--- extract acis evt1 file during the period
#
    flist = extract_evt1_data(start, stop)
    if len(flist) < 1:
        print("No data extracted")
#
#--- now analyze the data
#
    else:
        for ent in flist:
            cmd  = 'gzip -d ' + ent
            os.system(cmd)
            fits = ent.replace('.gz', '')
    
            run_corner_pixel_info(fits)
    
            mcf.rm_files(fits)
#
#--- remove duplicated entries
#
    remove_duplicate()
#
#--- copy data to the web site
#
    cmd = 'cp -f ' + data_dir + '* ' + web_dir + 'Data/.'
    os.system(cmd)

#------------------------------------------------------------------------------------
#-- find_the_last_entry_date: find the last data entry date                        --
#------------------------------------------------------------------------------------

def find_the_last_entry_date():
    """
    find the last data entry date
    input: none but read from data
    output: last    --- time in seconds from 1998.1.1
    """
    cmd   = 'ls ' + data_dir + '*.dat > ' + zspace
    os.system(cmd)
    dlist = mcf.read_data_file(zspace, remove=1)
    last  = 0.0
    for dfile in dlist:
        data = mcf.read_data_file(dfile)
        atemp = re.split('\s+', data[-1])
        ltime = float(atemp[0])
        if ltime > last:
            last = ltime

    out   = Chandra.Time.DateTime(last + 86400.0).date
    atemp = re.split(':', out)
    date  = atemp[0] + ':' + atemp[1] + ':00:00:00'
    last  = Chandra.Time.DateTime(date).secs


    return last

#------------------------------------------------------------------------------------
#-- extract_evt1_data: extract all acis evt1 file during the period                --
#------------------------------------------------------------------------------------

def extract_evt1_data(start, stop):
    """
    extract all acis evt1 file during the period
    input:  start   --- start time
            stop    --- stop time
    output: ./acisf_evt1.fits
            out     --- a list of acis evt1 file extracted
    """
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=evt1\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'

    out  = mcf.run_arc5gl_process(line)

    return out

#------------------------------------------------------------------------------------
#-- run_corner_pixel_info: run analysis on acis corner pixels                      --
#------------------------------------------------------------------------------------

def run_corner_pixel_info(fits):
    """
    run analysis on acis corner pixels
    input:  fits    --- fits file
    output: <plot_dir>/Ind_Plots/<acis_prefix>_<ccd_id>_<tail>.png (e.g. acisf20783_I2_hist.png)
            <plot_dir>/Ind_Plots/<acis_prefix>_<taiL>.png (e.g., acisf20783_cp.png)
            <data_dir>/<ccd)_id>.dat
    """
#
#--- prepare for prefix of the files
#
    atemp = re.split('_', fits)
    acis_prefix = atemp[0] + '_'

    btemp = re.split('acisf', atemp[0])
    obsid = btemp[1]
#
#--- open fits file
#
    print("FILE: " + fits)
    tout = pyfits.open(fits)
#
#--- find the data mode
#
    head  = tout[1].header
    dmode = head['datamode']
#
#--- extract data part
#
    fdata = tout[1].data
    
    if dmode == 'VFAINT':
#
#--- we want to use these pixels but instead, use cremove to drop unwanted pixels
#
#        cpixels = [0,1,2,3,4,5,6,8,9,10,14,15,16,18,19,20,21,22,23,24]
#        apixels = [6,8,16,18]

        cremove = [7, 11, 12, 13, 17]
        omode   = 'vfaint'
        extract_corner_pixel_info(fdata, cremove, acis_prefix, obsid,  omode, fits)
#
#--- central 9 pixel area of vfaint case
#
        cremove = [0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 17, 19, 20, 21, 22, 23, 24]
        omode   = 'afaint'
        extract_corner_pixel_info(fdata, cremove, acis_prefix, obsid,  omode, fits)
    
    elif dmode == 'FAINT':
#        cpixels = [0,2,6,8]
#        apixels = [-1]

        cremove = [1, 3, 4, 5, 7]
        omode   = 'faint'
        extract_corner_pixel_info(fdata, cremove, acis_prefix, obsid,  omode, fits)

    else:
        #exit(1)
        pass

#------------------------------------------------------------------------------------
#-- extract_corner_pixel_info: extract and analyze acis corner pixel distribution  --
#------------------------------------------------------------------------------------

def extract_corner_pixel_info(data, cremove, acis_prefix, obsid,  omode, fits):
    """
    extract and analyze acis corner pixel distribution
    input:  data        --- event data
            cremove     --- a list of pixel position to remove
            aics_prefix --- prefix of the output files
            obsid       --- obsid
            omode       --- data mode
            fits        --- fits file name
    output: <plot_dir>/Ind_Plots/<acis_prefix>_<ccd_id>_<tail>.png (e.g. acisf20783_I2_hist.png)
            <plot_dir>/Ind_Plots/<acis_prefix>_<taiL>.png (e.g., acisf20783_cp.png)
            <data_dir>/<ccd)_id>.dat
    """
#
#--- select data with grade 0, 2, 3, 4, or 6
#
    mask  = data['grade']  != 1
    data2 = data[mask]
    mask  = data2['grade'] != 4
    data3 = data2[mask]
    mask  = data3['grade'] != 7
    data4 = data3[mask]
#
#--- create lists of lists to save fitted results
#
    nc_list = [[] for x in range(0, 4)]         #--- normal distribution center
    nw_list = [[] for x in range(0, 4)]         #--- normal distribution width
    sc_list = [[] for x in range(0, 4)]         #--- skewed normal distribution center
    sw_list = [[] for x in range(0, 4)]         #--- skewed normal distribution width
    sk_list = [[] for x in range(0, 4)]         #--- skewness
    m_list  = [[] for x in range(0, 4)]         #--- bin position
#
#--- go through each ccd
#
    for n in range(0, 4):
        ccd   = ccds[n]
        cname = ccd_id[n]
        mask  = data4['ccd_id'] == ccd
        data5 = data4[mask]

        if len(data5) < 1:
            continue
#
#--- devide the data into 16 sections
#
        minexpo = min(data5['expno'])
        maxexpo = max(data5['expno'])
        kstop   = int((maxexpo - minexpo) /16.0 / binsize) + 1

        k     = 0       #--- bin skip counter: reset after each hist plotted
        m     = 0       #--- bin counter
        j     = minexpo
#
#--- create holders for data for later use (creating a matrix of histogram plots)
#
        data_list = []
        mnp_list  = []
        wnp_list  = []
        msp_list  = []
        wsp_list  = []
        skp_list  = []
        bp_list   = []
        while j < maxexpo:
            k += 1
            m += 1

            mask  = data5['expno'] >= j
            data6 = data5[mask]
            mask  = data6['expno'] < (j + binsize)
            data7 = data6[mask]

            pdata = data7['phas']
            edata = data7['expno']

            hlist = flaten_the_data(pdata, cremove)
            if hlist != 'NA':

                mu    = numpy.mean(hlist)
                std   = numpy.std(hlist)
                [skew, smu, sstd] = skewnorm.fit(hlist)
#
#--- save data for the tending plots
#
                nc_list[n].append(mu)
                nw_list[n].append(std)
                sc_list[n].append(smu)
                sw_list[n].append(sstd)
                sk_list[n].append(skew)
                m_list[n].append(numpy.mean(edata))
#
#---  save histogram data for bin: m if k reachs kstop
#
                if k == kstop:
                    data_list.append(hlist)
                    mnp_list.append(mu)
                    wnp_list.append(std)
                    msp_list.append(smu)
                    wsp_list.append(sstd)
                    skp_list.append(skew)
                    bp_list.append(m)
#
#--- set k = 0for the next round
#
                    k = 0

            j += binsize
#
#--- create histogram plots in a multipanel plot
#
        create_histogram_plot(data_list, mnp_list, wnp_list, msp_list, wsp_list,\
                              skp_list, bp_list, acis_prefix, ccd_id[n], omode)
#
#--- save data
#
        stime = numpy.mean(data4['time'])
        save_data(stime, m_list[n], nc_list[n], nw_list[n],  sc_list[n], sw_list[n],\
                  sk_list[n], ccd_id[n], obsid, omode)
#
#--- now create trend plots: normal distribution and skewed normal distribution
#
    create_trend_plots(ccd_id, m_list, nc_list, fits, acis_prefix, omode)
    create_trend_plots(ccd_id, m_list, sc_list, fits, acis_prefix, omode, sk=1)

#------------------------------------------------------------------------------------
#-- save_data: save data in a data files                                           --
#------------------------------------------------------------------------------------

def save_data(stime, x, ny, nw, sy, sw, sk, ccd_id, obsid, omode):
    """
    save data in a data files
    input:  stime   --- the time of the data collected
            x       --- a list of bins
            ny      --- a list of center postion
            nw      --- a list of width
            sy      --- a list of skewed center postion
            sw      --- a list of skewed width
            sk      --- a list of skewness
            ccd_id  --- ccd ID
            obsid   --- obsid
            omode   --- data ode
    output: <data_dir>/<ccd_id>.dat
    """
#
#--- estimate a slope of the fitted line
#
    try:
        [intc, slope, err]  = robust.least_sq(x, ny)
    except:
        intc  = 0.0
        slope = 0.0
#
#--- remove the extreme cases and then computer mean and std
#
    ny    = remove_extreme(ny)          #--- normal center
    ym1   = numpy.mean(ny)
    ym2   = numpy.std(ny)

    nw    = remove_extreme(nw)          #--- normal width
    wm1   = numpy.mean(nw)
    wm2   = numpy.std(nw)

    sy    = remove_extreme(sy)          #--- skewed center
    ym3   = numpy.mean(sy)
    ym4   = numpy.std(sy)

    sw    = remove_extreme(sw)          #--- skewed width
    wm3   = numpy.mean(sw)
    wm4   = numpy.std(sw)

    skm   = numpy.mean(sk)              #--- skewness

    sline = '%2.7e\t' % stime
    sline = sline + str(obsid)    + '\t'
    try:
        val = float(slope)
        sline = sline + '%2.6e\t' % slope
    except:
        sline = sline + 'NA\t'

    sline = sline + '%2.6f\t' % ym1
    sline = sline + '%2.6f\t' % ym2
    sline = sline + '%2.6f\t' % wm1
    sline = sline + '%2.6f\t' % wm2
    sline = sline + '%2.6f\t' % ym3
    sline = sline + '%2.6f\t' % ym4
    sline = sline + '%2.6f\t' % wm3
    sline = sline + '%2.6f\t' % wm4
    sline = sline + '%2.6f\n' % skm
#
#--- save in a file
#
    outfile = data_dir + ccd_id + '_' + omode + '.dat'
#
#--- if this is the first time, add the header
#
    if not os.path.isfile(outfile):
        header = '#' + '-'*144 + '\n'
        header = header + '#time\t\t\tobsid\tslope\t\t\tcent mean\tcent std\t'
        header = header + 'width mean\twidth std\tskew cent\tskew c std\t'
        header = header + 'skew width\tskew w std\tskewness\n' + '#'
        header = header + '-'* 144 + '\n'
        with open(outfile, 'w') as fo:
            fo.write(header)
            fo.write(sline)
    else:
        with open(outfile, 'a') as fo:
            fo.write(sline)

#------------------------------------------------------------------------------------
#-- flaten_the_data: flaten the data to 1D list                                    --
#------------------------------------------------------------------------------------

def flaten_the_data(pdata, cremove):
    """
    flaten the data to 1D list
    input:  pdata   --- array of arrays of either 3x3 or 5x5
            cremove --- the pixel positions to be ignored
    output: hlist   --- a list of data
    """
    hlist = []
    for ent in pdata:
        tout = []
        for pn in range(0, len(ent)):
            tout = tout + list(ent[pn])

        tout  = list(numpy.delete(tout, cremove))
        hlist = hlist + tout

    hlist  = remove_extreme(hlist)
    if len(hlist) < 1:
        return 'NA'

    hmin   = min(hlist)
    ahlist = numpy.array(hlist)
    if hmin < 0:
        if hmin < -20:
            hmin   = -20
            mask   = ahlist > hmin
            ahlist = ahlist[mask]
        top = abs(hmin) + 1
    else:
        top = 20
    mask  = ahlist < top

    hlist = list(ahlist[mask])

    return hlist

#------------------------------------------------------------------------------------
#-- create_histogram_plot: create a histogram plot                                ---
#------------------------------------------------------------------------------------

def create_histogram_plot(data_list, nm_list, nw_list, sm_list, sw_list, sk_list,\
                          b_list, acis_prefix, ccd_id, omode):
    """
    create a histogram plot
    input:  data_list   --- a list of lists of histogram data
            nm_list     --- a list of center position esimates
            nw_list     --- a list of width estimates
            sm_list     --- a list of skewed center position esimates
            sw_list     --- a list of skewed width estimates
            sk_list     --- a list of skewness estimates
            b_list      --- a list of bin numbers
            acis_prefix --- a prefix for the output file
            ccd_id      --- ccd ID
            omod        --- data mode such faint, vfaint
    output: <plot_dir>/<acis_prefix>_<ccd_id>_<tail>.png
    """
    plt.close('all')
#
#--- create 4 x 4 plot surface and plot a histogram in one of the panels
#
    cols    = 4
    gs      = gridspec.GridSpec(len(nm_list) // cols + 1, cols)
    gs.update(hspace=0.4)

    figsize = (10, 10)
    fig1    = plt.figure(num=1, figsize=figsize)
    ax      = []

    for pc in range(0, len(nm_list)):
        row   = (pc // cols)
        col   = pc % cols 

        ax.append(fig1.add_subplot(gs[row, col]))

        hlist = data_list[pc]
        mu    = nm_list[pc]
        std   = nw_list[pc]
        smu   = sm_list[pc]
        sstd  = sw_list[pc]
        skew  = sk_list[pc]
        bno   = b_list[pc]
    
        title  = 'CCD: ' + ccd_id + "  BIN: " + str(bno)
        ax[-1].set_title(title) 
        plot_hist(hlist, mu,  std, smu, sstd, skew,  title)
#
#--- save histogram plots in a file
#
    if omode == 'afaint':
        tail = '_ahist.png'

    elif omode == 'vfaint':
        tail = '_vhist.png'

    else:
        tail = '_hist.png'

    odir = plot_dir +'Ind_Plots/'+ acis_prefix + 'plots'
    cmd = 'mkdir -p  ' +  odir
    os.system(cmd)

    outname = odir + '/'+ acis_prefix +  ccd_id + tail
    fig     = matplotlib.pyplot.gcf()
    plt.savefig(outname, format='png', dpi=200)

#------------------------------------------------------------------------------------
#-- plot_hist: create a histogram plot panel                                       --
#------------------------------------------------------------------------------------

def plot_hist(data, mu, std, smu, sstd, skew, title):
    """
    create a histogram plot panel
    input:  data    --- a list of data
            mu      --- estimated center location
            std     --- estimated width
            smu     --- estimated skewed center location
            sstd    --- estimated skewed width
            skew    --- estimated skewness
            title   --- the title of the plot
    output: a histogram plot panel (does not create a plot file)
    """
#
#--- plot histogram data
#
    try:
#
#--- older format... if the starndard one does not work
#
        plt.hist(data, bins=20, range=(-10, 10), normed=True, alpha=0.4, color='green')
    except:
        plt.hist(data, bins=20, range=(-10, 10), density=True, alpha=0.4, color='green')
#
#--- plot the normal/skewed normal fitting
#
    xmin, xmax = plt.xlim()
    xlist = numpy.linspace(xmin, xmax, 100)

    ylist = snorm.pdf(xlist, mu, std)
    plt. plot(xlist, ylist, color='blue', linewidth=2)

    ylist = skewnorm.pdf(xlist, skew, smu, sstd)
    plt. plot(xlist, ylist, color='red', linewidth=2)

    plt.title(title)
    ymin, ymax = plt.ylim()
    ydiff      = ymax - ymin
    ypos1      = ymax - 0.1 * ydiff
    ypos2      = ymax - 0.2 * ydiff
    plt.text(-11, ypos1, 'normal', color='blue')
    plt.text(-11, ypos2, 'skewed', color='red')

#------------------------------------------------------------------------------------
#-- create_trend_plots: create trend plot and save in a file                      ---
#------------------------------------------------------------------------------------

def create_trend_plots(ccd_id, m_list, c_list, fits, acis_prefix, omode, sk=0):
    """
    create trend plot and save in a file
    input:  ccd_id  --- a list of ccd id
            m_list  --- a list of bin positions
            c_list  --- a list of estimated center positions
            acis_prefix --- a prefix of the file
            fits    --- a fits file name
            omode   --- a  data ode
            sk      --- is this skewed plot? 0: no, 1: yes
    output: <plot_idr>/<acis_prefix>_<type>.png
    """
#
#--- now create trend plots
#
    plt.close('all')
    for k in range(0, 4):
#
#--- set the plot position (there are 4 trend plots)
#
        k1 = k + 1
        plt.subplot(4, 1, k1)
        x     = m_list[k]
        y     = c_list[k]

        try:
            [intc, slope, err]  = robust.least_sq(x, y)
        except:
            intc  = 0.0
            slope = 0.0

        title = fits + ' ' + ccd_id[k] + ' ' + omode 
        plot_trend(x, y, title, intc, slope, sk)

    if omode == 'afaint':
        tail = 'acp.png'
    else:
        tail = 'cp.png'
    if sk == 0:
        skt = 'norm_'
    else:
        skt = 'skew_'
#
#--- save the plot
#
    odir = plot_dir +'Ind_Plots/'+ acis_prefix + 'plots'
    cmd = 'mkdir -p  ' +  odir
    os.system(cmd)
    outname = odir  + '/' + acis_prefix + skt +  tail

    fig     = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 10.0)
    plt.savefig(outname, format='png', dpi=200)

#------------------------------------------------------------------------------------
#-- plot_trend: create a trend plot panel                                          --
#------------------------------------------------------------------------------------

def plot_trend(x, y, title, intc, slope, sk):
    """
    create a trend plot panel
    input:  x   --- a list of x values
            y   --- a list of y values
            title   --- a title of the plot
            intc    --- an intercept of the fitted line
            slope   --- a slope of the fitted line
            sk      --- is this skewed plot? 0: no, 1: yes
    output: a panel of plot; does not create an actual plot file
    """
    if len(x) > 0:
#
#--- set position etc
#
        xstart = min(x)
        xstop  = max(x)
        ystart = intc + slope * xstart
        ystop  = intc + slope * xstop
        xpos   = 0.7 * xstop
#
#--- plot data
#
        plt.plot(x, y, color='blue', marker='o', linewidth=0)
#
#--- plot a fitted line
#
        plt.plot([xstart,xstop], [ystart, ystop], color='red', marker='', linewidth=2)
#
#--- set text position in y direction (read from the plotting panel)
#
        ymin, ymax = plt.ylim()
        ydiff      = ymax - ymin
        ypos       = ymax - 0.1 * ydiff
#
#--- add labels etc
#
        plt.xlabel('Frame')
        if sk == 0:
            plt.ylabel('Pix Centroid')
        else:
            plt.ylabel('Pix Mu')

        plt.text(0.0, ypos, title)

        try:
            chk = float(slope)
            line = 'Slope: %2.3e' % slope
        except:
            line = 'na'

        plt.text(xpos, ypos, line)
#
#--- if there is no data to plot, create an empty box
#
    else:
        x = [0, 1]
        y = [0, 1]
        plt.plot(x, y, color='white', marker='.', markersize=0, linewidth=0)
        plt.xlabel('Frame')
        plt.ylabel('Pix Centroid')
        plt.text(0.5, 0.3, "No Data")
        plt.text(0.0, 0.9, title)

#------------------------------------------------------------------------------------
#-- remove_extreme: drop outlyers                                                  --
#------------------------------------------------------------------------------------

def remove_extreme(x):
    """
    drop outlyers
    input:  x   --- a list of data
    output: out --- a list of data dropped data outside of 3 sigma
    """
    avg  = numpy.mean(x)
    std  = numpy.std(x)
    top  = avg + 3.0 * std
    
    ax   = numpy.array(x)
    mask = ax <= top
    out  = list(ax[mask])

    return out

#------------------------------------------------------------------------------------
#-- remove_duplicate: remove duplicated data entries                               --
#------------------------------------------------------------------------------------

def remove_duplicate():
    """
    remove duplicated data entries
    input:  none
    output: cleaned data file
    """
    cmd   = 'ls ' + data_dir + '*.dat > ' + zspace
    os.system(cmd)
    dlist = mcf.read_data_file(zspace, remove=1)

    for ifile in dlist:
        data = mcf.read_data_file(ifile)
        aline = ''
        prev = 0
        for ent in data[1:]:
            atemp = re.split('\s+', ent)
            try:
                val = float(atemp[1])
            except:
                continue

            if prev == val:
                continue
            else:
                aline = aline + ent + '\n'
                prev = val

        with open(ifile, 'w') as fo:
            fo.write(aline)


#------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        start = sys.argv[1].strip()

    elif len(sys.argv) == 3:
        start = sys.argv[1].strip()
        stop  = sys.argv[2].strip()

    else:
        start = ''
        stop  = ''

    analyze_acis_corner_pixels(start, stop)


