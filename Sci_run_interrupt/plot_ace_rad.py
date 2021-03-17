#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       plot_ace_rad.py: plot ACE radiation data                                        #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 09, 2021                                               #
#                                                                                       #
#########################################################################################

import math
import re
import sys
import os
import string
import numpy as np
#
#--- pylab plotting routine related modules
#
from pylab import *
if __name__ == '__main__':
    mpl.use('Agg')

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a  path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- mta common functions
#
import mta_common_functions             as mcf
#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions        as itrf 

#-----------------------------------------------------------------------------------
#--- start_ace_plot: the main function to plot NOAA data                         ---
#-----------------------------------------------------------------------------------

def start_ace_plot(event, start, stop):
    """
    for a gien event, start and stop data, initiate ACE plottings.
    input:  event   --- name of the event <yyyymmdd>
            start   --- interruption starting time in <yyyy>:<ddd>:<hh>:<mm>
            stop    --- interruption stopping time in <yyyy>:<ddd>:<hh>:<mm>
    """
#
#--- change time format to year and ydate (float)
#
    [year1, ydate1] = itrf.dtime_to_ydate(start)
    [year2, ydate2] = itrf.dtime_to_ydate(stop)
#
#--- plot ACE Data
#
    ace_data_plot(event, year1, ydate1, year2, ydate2)


#-----------------------------------------------------------------------------------
#--- ace_data_plot: ACE data plotting manager                                    ---
#-----------------------------------------------------------------------------------

def ace_data_plot(name, start_year, start_yday, stop_year, stop_yday):
    """
    manage ACE data plot routines. 
    input:  name        --- envet name <yyyymmdd>
            start_year   --- interruption starting year
            start_yday   --- interruption starting ydate
            stop_year    --- interruption stopping year
            stop_yday    --- interruption stopping ydate
    """
#
#--- set the plotting range
#
    (pyear_start, period_start, pyear_stop, period_stop, \
     plot_year_start, plot_start, plot_year_stop, plot_stop, period) \
                = itrf.find_collection_period( start_year, start_yday, stop_year, stop_yday)
#
#--- read radation zone information
#
    radZone = itrf.read_rad_zone(name)
#
#---  read the data
#
    [dofy, e38, e175, p47, p112, p310, p761, p1060, ani] =  read_ace_data(name)
#
#--- if the ending data is in the following year
#
    if stop_year > start_year:
       if mcf.is_leapyear(start_year):
           base = 366
       else:
           base = 365
       stop_yday += base
#
#--- plot data; after 2014, anisotorpy data disappeard; so no plotting for anisotorpy
#
    if period == 1:
        if start_year < 2014:
            plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, ani,\
                    start_yday, stop_yday, plot_start, plot_stop, radZone)
        else:
            plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA',\
                    start_yday, stop_yday, plot_start, plot_stop, radZone)

        cmd = 'mv ./out.png ' + plot_dir + name + '.png'
        os.system(cmd)
#
#--- if the interruption period cannot be covered by one plotting panel, 
#--- create as many panels as we need to cover the period.
#
    else:
        pstart = plot_start 
        prange = period + 1
        if start_year < 2014:
            for i in range(1, prange):
                pend = pstart + 5
                if i == 1:
                    plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, \
                            ani, start_yday, 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_dir + name + '.png'
                    os.system(cmd)

                elif i == period:
                    plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, ani, \
                           'NA', stop_yday, pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_dir + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)

                else:
                    plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, ani, \
                            'NA', 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_dir + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)
    
                pstart  = pend

        else:
            for i in range(1, prange):
                pend = pstart + 5
                if i == 1:
                    plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', \
                            start_yday, 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_dir + name + '.png'
                    os.system(cmd)

                elif i == period:
                    plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', \
                            'NA', stop_yday, pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_dir + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)

                else:
                    plot_ace(dofy, e38, e175, p47, p112, p310, p761, p1060, 'NA', \
                            'NA', 'NA', pstart, pend, radZone)
                    cmd = 'mv ./out.png ' + plot_dir + name + '_pt'+ str(i) + '.png'
                    os.system(cmd)
    
                pstart  = pend


#-----------------------------------------------------------------------------------
#--- read_ace_data: reading ACE Data from ACE data table                           ---
#-----------------------------------------------------------------------------------

def read_ace_data(ifile):
    """
    reading an ACE data file located in a Interrupt Data_dir
    input:  ifile       --- data file name
    output: dofy        --- a list of date in ydate
            elec38      --- a list of elec 38 data
            elec175     --- a list of elec 175 data
            proton47    --- a list of proton 47 data
            proton112   --- a list of proton 112 data
            proton310   --- a list of porton 310 data
            proton761   --- a list of proton 761 data
            proton1060  --- a list of proton 1060 data
            aniso       --- a list of anisotropy data
    """
    ifile = wdata_dir + ifile + '_dat.txt'
    data  = mcf.read_data_file(ifile)

    dofy       = []
    elec38     = []
    elec175    = []
    proton47   = []
    proton112  = []
    proton310  = []
    proton761  = []
    proton1060 = []
    aniso      = []
    for ent in data:
        if ent:
            atemp = re.split('\s+|\t+', str(ent))
            btemp = re.split('\.', str(atemp[0]))

            if str.isdigit(str(btemp[0])):

                if atemp[1] and atemp[2] and atemp[3] and atemp[4] \
                     and atemp[5] and atemp[6] and atemp[7] and atemp[8]:
                    atemp[1] = float(atemp[1])
                    atemp[2] = float(atemp[2])
                    atemp[3] = float(atemp[3])
                    atemp[4] = float(atemp[4])
                    atemp[5] = float(atemp[5])
                    atemp[6] = float(atemp[6])
                    atemp[7] = float(atemp[7])
                    atemp[8] = float(atemp[8])

                    for m in range(1, 8):
                        if atemp[m] <= 0:
                            atemp[m] = 1e-5
    
                    dofy.append(float(atemp[0]))
    
                    elec38.append(math.log10(atemp[1]))
                    elec175.append(math.log10(atemp[2]))
                    proton47.append(math.log10(atemp[3]))
                    proton112.append(math.log10(atemp[4]))
                    proton310.append(math.log10(atemp[5]))
                    proton761.append(math.log10(atemp[6]))
                    proton1060.append(math.log10(atemp[7]))
                    aniso.append(atemp[8])

    return [dofy, elec38, elec175, proton47, proton112, proton310,proton761, proton1060, aniso]

#-----------------------------------------------------------------------------------
#--- plot_ace: plotting routine                                                  ---
#-----------------------------------------------------------------------------------

def plot_ace(xdata, ydata0, ydata1, ydata2, ydata3, ydata4, ydata5,\
            ydata6, ydata7, start, stop, xmin, xmax, radZone):
    """
    actual plotting of ACE data are done with this fuction. 
    input:  xdata   --- a list of time in ydate
            ydata0  --- elec38 
            ydata1  --- elec175 
            ydata2  --- proton47 
            ydata3  --- proton 112
            ydata4  --- prton310
            ydata5  --- prton 761
            ydata6  --- proton1060
            ydata7  --- anisotrophy index
            start   --- interruption starting time in ydate
            stop    --- interruption stopping time in ydate
            xmin    --- plotting range x min
            xmax    --- plotting range x max
            radZone --- a list of rad zone 
    """
#
#--- setting the plotting ranges for each plot
#
    electronMin = 1.0
    electronMax = 6.0
    protonMin   = 1.0
    protonMax   = 6.0
    anisoMin    = 0.
    anisoMax    = 2.


    plt.close('all')                    #--- clean up the previous plotting 
#
#--- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=6)
    plt.subplots_adjust(hspace=0.08)

#---------------------------------
#--- first panel : electron data
#---------------------------------

#
#--- check whether anisotorphy data exits and change the number of panels
#
    if ydata7 !='NA':           
        ax1  = plt.subplot(311)
    else:
        ax1  = plt.subplot(211)
#
#--- set plotting range
#
    ymin = electronMin 
    ymax = electronMax

    ax1.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
    ax1.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

    ax1.set_xlim(xmin, xmax, auto=False)
    ax1.set_ylim(ymin, ymax, auto=False)

    tix_row = itrf.make_tix_label(ymin, ymax)
    ax1.set_yticklabels(tix_row)
#
#-- plot lines
#
    [xval, yval] = itrf.remove_none_data(xdata, ydata0, -5)
    p0, =plt.plot(xval, yval, color='red', lw=1)

    [xval, yval] = itrf.remove_none_data(xdata, ydata1, -5)
    p1, =plt.plot(xval, yval, color='blue',lw=1)
#
#--- plot radiation zone markers
#
    itrf.plot_rad_zone(radZone, xmin, xmax, ymin)
#
#--- put lines to indicate the interrupted time period
#
    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        xdiff = xmax - xmin
        ydiff = ymax - ymin
        xtext = start + 0.01 * xdiff
        ytext = ymax - 0.1 * ydiff
    
        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
#
#--- add legend
#
    leg = legend([p0,p1], ['Electron30-53','Electron75-315'], prop=props)
    leg.get_frame().set_alpha(0.5)
#
#--- mark y axis
#
    ax1.set_ylabel('Electron/cm2-q-sr-Mev')

#---------------------------------
#---- second panel: proton data 
#---------------------------------

    if ydata7 != 'NA':
        ax2 = plt.subplot(312, sharex=ax1)
    else:
        ax2 = plt.subplot(212, sharex=ax1)
#
#--- set plotting range
#
    ymin = protonMin
    ymax = protonMax
    ax2.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
    ax2.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

    ax2.set_xlim(xmin, xmax, auto=False)
    ax2.set_ylim(ymin, ymax, auto=False)

    tix_row = itrf.make_tix_label(ymin, ymax)
    ax2.set_yticklabels(tix_row)
#
#--- plot lines
#
    [xval, yval] = itrf.remove_none_data(xdata, ydata2, -5)
    p0, = plt.plot(xval, yval, color='red',   lw=1)

    [xval, yval] = itrf.remove_none_data(xdata, ydata3, -5)
    p1, = plt.plot(xval, yval, color='blue',  lw=1)

    [xval, yval] = itrf.remove_none_data(xdata, ydata4, -5)
    p2, = plt.plot(xval, yval, color='green', lw=1)

    [xval, yval] = itrf.remove_none_data(xdata, ydata5, -5)
    p3, = plt.plot(xval, yval, color='aqua',  lw=1)

    [xval, yval] = itrf.remove_none_data(xdata, ydata6, -5)
    p4, = plt.plot(xval, yval, color='teal',  lw=1)
#
#--- plot radiation zone markers
#
    itrf.plot_rad_zone(radZone, xmin, xmax, ymin)
#
#--- put lines to indicate the interrupted time period
#
    if start != 'NA':
        plt.plot([start, start], [ymin, ymax], color='red', lw=2)

        xdiff = xmax - xmin
        ydiff = ymax - ymin
        xtext = start + 0.01 * xdiff
        ytext = ymax - 0.1 * ydiff
    
        plt.text(xtext, ytext, r'Interruption', color='red')

    if stop  != 'NA':
        plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
#
#--- draw trigger level
#
    plt.plot([xmin, xmax], [4.70, 4.70], color='red', linestyle='--', lw=1.0)
#
#--- add legend
#
    leg = legend([p0, p1, p2, p3, p4], \
            ['Proton47-65','Proton112-187', 'Proton310-580','Proton781-1220','Prton1080-1910'],\
          prop=props)
    leg.get_frame().set_alpha(0.5)
#
#--- label y axis

    ax2.set_ylabel('Proton/cm2-q-sr-Mev')

#-----------------------------------
#--- third panel: anisotropy index 
#-----------------------------------

    if ydata7 != 'NA':
        ax3 = plt.subplot(313, sharex=ax1)
#
#--- set plotting range
#
        ymin = anisoMin
        ymax = anisoMax

        ax3.set_autoscale_on(False)     #---- these three may not be needed for the new pylab, but 
        ax3.set_xbound(xmin,xmax)       #---- they are necessary for the older version to set
    
        ax3.set_xlim(xmin, xmax, auto=False)
        ax3.set_ylim(ymin, ymax, auto=False)
#
#--- check the case the data is not available (no data: -1.0 )
#
        if len(ydata7) == 0:
            xtpos = xmin + 0.1 * (xmax - xmin)
            ytpos = 1.5
            plt.text(xtpos, ytpos, r'No Data', color='red', size=12)
    
        else:
            avg = math.fsum(ydata7) / len(ydata7)
    
            if avg < -0.95 and avg  > -1.05:
                xtpos = xmin + 0.1 * (xmax - xmin)
                ytpos = 1.5
                plt.text(xtpos, ytpos, r'No Data', color='red', size=12)
    
            else:
#
#---- plot line
#
                [xval, yval] = itrf.remove_none_data(xdata, ydata7, 0, 2)
                p0, = plt.plot(xval, yval, color='red', lw=1)
#
#--- plot radiation zone markers
#
        itrf.plot_rad_zone(radZone, xmin, xmax, ymin)
#
#--- put lines to indicate the interrupted time period
#
        if start != 'NA':
            plt.plot([start, start], [ymin, ymax], color='red', lw=2)
    
            xdiff = xmax - xmin
            ydiff = ymax - ymin
            xtext = start + 0.01 * xdiff
            ytext = ymax  - 0.1  * ydiff
     
            plt.text(xtext, ytext, r'Interruption', color='red')
    
        if stop  != 'NA':
            plt.plot([stop,  stop ], [ymin, ymax], color='red', lw=2)
     
        ax3.set_ylabel('Anisotropy Index')
#
#--- plot x axis tick label only at the third panel
#

    xlabel('Day of Year')
    if ydata7 != 'NA':
        for ax in ax1, ax2, ax3:
            if ax != ax3:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                pass
    else:
        for ax in ax1, ax2:
            if ax != ax2:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                pass
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    if ydata7 != 'NA':
        fig.set_size_inches(10.0, 5.0)
    else:
        fig.set_size_inches(10.0, 3.33)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=300)

#------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 3:
        event = sys.argv[1]
        start = sys.argv[2]
        stop  = sys.argv[3]

        start_ace_plot(event, start, stop)
