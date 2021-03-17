#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#       plot_count_rate.py: plot ACIS count rate related plots              #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           Last Update: Mar 03, 2021                                       #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import operator
import math
import numpy
import time
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

import random                   #--- random must be called after pylab

path = '/data/mta/Script/ACIS/Count_rate/house_keeping/dir_list_py'
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
#--- import libraries
#
import mta_common_functions       as mcf 
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

m_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

#----------------------------------------------------------------------------------
#--- create_plots: a control function to crate all acis dose plots              ---
#----------------------------------------------------------------------------------

def create_plots(year):
    """
    a control function to crate all acis dose plots
    input: year --- the year of the plot to be created
    output: all plots in png form
    """
#
#--- if the date is not given, create plots for the last month
#
    chk = 0
    if year == '':
        out   = time.strftime('%Y', time.gmtime())
        year  = int(float(out))
        chk = 1
#
#--- create ccd monthly plots
#
    generate_count_rate_plot(year)
#
#--- ephin data are available only before Nov 2018
#
    if (year <= 2018):
        generate_ephin_rate_plot(year)
#
#--- full range plots (create only when the most recent data are plotted)
#
    if chk > 0:
        full_range_plot()

#----------------------------------------------------------------------------------
#--- generate_count_rate_plot: create count rate plots                          ---
#----------------------------------------------------------------------------------

def generate_count_rate_plot(year):
    """
    create count rate plots
    input:  year    --- the year of the data
            mon     --- the month of the data
    output: <directory>/acis_dose_ccd<ccd>.png
            <directory>/acis_dose_ccd_5_7.png
    """

    odir    = web_dir + 'Plots/' + str(year)
    if not os.path.isdir(odir):
        cmd = 'mkdir -p ' + odir
        os.system(cmd)

    xname   = 'Time (Day of Year: Year ' + str(year) + ')'
    yname   = 'Count/Sec'
#
#--- save data sets for each ccd
#
    data_x  = []
    data_y  = []
#
#--- plot count rates for each ccd
#
    for ccd in range(0, 10):
        xdata = []
        ydata = []
        for mon in m_list:
            directory = mon + str(year)
            ifile = data_dir + directory + '/ccd' + str(ccd)
            if not os.path.isfile(ifile):
                continue
#
#--- get the data
#
            data  = mcf.read_data_file(ifile)
            for ent in data:
                atemp = re.split('\s+', ent)
#
#--- convert time to a year date  and normalized y data to cnts/sec --- 300 sec cumurative
#
                try:
                    xval = float(atemp[0])
                    xval = mcf.chandratime_to_yday(xval)
                    yval = float(atemp[1]) / 300.0
                except:
                    continue
#
#--- don't care to plot 'zero' values; so skip them
#
                if yval == 0:
                    continue
                if yval > 500:
                    continue
    
                xdata.append(xval)
                ydata.append(yval)

        title   = 'ACIS Count Rate: CCD' + str(ccd)
        outname = web_dir + 'Plots/' +  str(year) + '/acis_dose_ccd' + str(ccd) + '.png'

        if len(xdata) < 1:
            cmd = 'cp ' + house_keeping + 'no_plot.png ' + outname
            os.system(cmd)
        else:
            plot_panel(xdata, ydata, xname, yname, title, outname)

#----------------------------------------------------------------------------------
#--- full_range_plot: create long term trending plots                           ---
#----------------------------------------------------------------------------------

def full_range_plot():
    """
    create long term trending plots
    input: none but all data are read from web_dir/<MON><YEAR> directories
    output: <web_dir>/long_term_plot.png
            <web_dir>/month_avg_img.png
            <web_dir>/month_avg_spc.png
            <web_dir>/month_avg_bi.png
    """
    xname = 'Time (Year)'
    yname = 'Counts/Sec'
#
#--- imaging ccds full history (monthly average)
#
    [x0, y0]   = get_data_set('month_avg_data', 0)
    [x1, y1]   = get_data_set('month_avg_data', 1)
    [x2, y2]   = get_data_set('month_avg_data', 2)
    [x3, y3]   = get_data_set('month_avg_data', 3)
    x_set_list = [x0, x1, x2, x3]
    y_set_list = [y0, y1, y2, y3]
    yname_list = [yname,  yname,  yname,  yname]
    title_list = ['CCD0', 'CCD1', 'CCD2', 'CCD3']
    outname    = web_dir + 'Plots/month_avg_img.png'

    plot_multi_panel(x_set_list, y_set_list, xname, yname_list, title_list,\
                     outname, linew=0, mrk='+', ylim=1, autox='yes')
#
#--- spectral ccds full history (monthly average)
#
    [x4, y4]   = get_data_set('month_avg_data', 4)
    [x6, y6]   = get_data_set('month_avg_data', 6)
    [x8, y8]   = get_data_set('month_avg_data', 8)
    [x9, y9]   = get_data_set('month_avg_data', 9)
    x_set_list = [x4, x6, x8, x9]
    y_set_list = [y4, y6, y8, y9]
    yname_list = [yname,  yname,  yname,  yname]
    title_list = ['CCD4', 'CCD6', 'CCD8', 'CCD9']
    outname    = web_dir + 'Plots/month_avg_spc.png'

    plot_multi_panel(x_set_list, y_set_list, xname, yname_list, title_list, \
                     outname, linew=0, mrk='+', ylim=1, autox='yes')
#
#--- backside ccds full history (monthly average)
#
    [x5, y5]   = get_data_set('month_avg_data', 5)
    [x7, y7]   = get_data_set('month_avg_data', 7)
    x_set_list = [x5, x7]
    y_set_list = [y5, y7]
    yname_list = [yname,  yname]
    title_list = ['CCD5', 'CCD7']
    outname    = web_dir + 'Plots/month_avg_bi.png'
    y_limit    = [50, 50]

    plot_multi_panel(x_set_list, y_set_list, xname, yname_list, title_list,\
                     outname, linew=0, mrk='+', ylim=2,y_limit=y_limit, autox='yes')
#
#--- long term plot of ccds 5, 6, and 7
#
    [x5, y5]   = get_data_set('full_data', 5, skip=5)
    [x6, y6]   = get_data_set('full_data', 6, skip=5)
    [x7, y7]   = get_data_set('full_data', 7, skip=5)
    x_set_list = [x5, x6, x7]
    y_set_list = [y5, y6, y7]
    yname_list = [yname,  yname,  yname]
    title_list = ['CCD5', 'CCD6', 'CCD7']
    outname    = web_dir + 'Plots/long_term_plot.png'
    y_limit    = [750, 750, 750]

    plot_multi_panel(x_set_list, y_set_list, xname, yname_list, title_list,\
                     outname, ylim =2, y_limit=y_limit, autox='yes')

#----------------------------------------------------------------------------------
#-- get_data_set: read data a data file and create lists of x and y              --
#----------------------------------------------------------------------------------

def get_data_set(head, ccd, skip=1):
    """
    read data a data file and create lists of x and y
    input:  head    --- header of the data file
            ccd     --- ccd #
            skip    --- step; default: 1 -- read every data point
    output: [x, y]  --- a list of lists of x and y
    """

    ifile = data_dir + head + '_ccd' + str(ccd) + '.dat'
    data  = mcf.read_data_file(ifile)
    x     = []
    y     = []
    for ent in data[::skip]:
        atemp = re.split('\s+', ent)
        val = int(float(atemp[0]))
        val = mcf.chandratime_to_fraq_year(val)
        x.append(val)
        y.append(int(float(atemp[1])))

    return [x, y]

#----------------------------------------------------------------------------------
#--- generate_ephin_rate_plot: create ephin rate plots                          ---
#----------------------------------------------------------------------------------

def generate_ephin_rate_plot(year):
    """
    create ephin rate plots
    input: year --- year of the data
           mon  --- month of the data
           <directory>/ephin_rate --- ephin data file
    ouput: <directory>/ephin_rate.png
    """
    odir      = web_dir + 'Plots/' + str(year)
    if not os.path.isdir(odir):
        cmd = 'mkdir -p ' + odir
        os.system(cmd)

    xname  = 'Time (Day of Year: Year ' + str(year) + ')'
    yname  = 'Count/Sec'

    stime = []
    p4    = []
    e150  = []
    e300  = []
    e1300 = []
    for mon in m_list:
        directory = mon + str(year)
        ifile  = data_dir + directory + '/ephin_rate'
        if not os.path.isfile(ifile):
            continue

        data   = mcf.read_data_file(ifile)

        for ent in data:
            atemp = re.split('\s+', ent)
            try:
                val0 = int(float(atemp[0]))
                val0 = mcf.chandratime_to_yday(val0)
                val1 = float(atemp[1]) /300.0
                if val1 > 100000:
                    continue
                val2 = float(atemp[2]) /300.0
                if val2 > 100000:
                    continue
                val3 = float(atemp[3]) /300.0
                if val3 > 100000:
                    continue
                val4 = float(atemp[4]) /300.0
                if val4 > 100000:
                    continue
            except:
                continue
    
            stime.append(val0)
            p4.append(val1)
            e150.append(val2)
            e300.append(val3)
            e1300.append(val4)
    
    x_set_list = [stime, stime,  stime,  stime]
    y_set_list = [p4,  e150, e300, e1300]
    yname_list = [yname, yname, yname, yname]
    title_list = ['P4', 'E150', 'E300', 'E1300']

    outname    = web_dir + 'Plots/' +  str(year) + '/ephin_rate.png'

    plot_multi_panel(x_set_list, y_set_list, xname, yname_list, title_list, outname)

#----------------------------------------------------------------------------------
#--- plot_panel: createa single pamel plot                                      ---
#----------------------------------------------------------------------------------

def plot_panel(xdata, ydata, xname, yname, title, outname, autox='no'):
    """
    createa single pamel plot
    Input:  xdata  --- x data
            ydata  --- y data
            xname  --- x axis legend
            yname  --- y axis legend
            title  --- title of the plot
            outname -- output file name
    Output: outname -- a png plot file
    """
#
#--- set plotting range
#
    xmin = int(min(xdata) - 1)
    if autox == 'no':
        xmin = 0
        xmax = 370
    else:
        xmax = max(xdata)
        diff = xmax - xmin
    
        if diff == 0 and xmin > 0:
            xmax = xmin + 1
        else:
            xmin -= 0.05 * diff
            xmax += 0.05 * diff
            if xmin < 0.0:
                xmin = 0

    ymin = 0
#
#--- drop extreme case for ymax 
#
    avg  = numpy.mean(ydata)
    sig  = numpy.std(ydata)
    ymax = avg + 3.0 *sig
    diff = ymax - ymin
    if diff == 0 and ymin >= 0:
        ymax = ymin + 1
    else:
        ymax += 0.05 * diff
#
#--- clean up all plotting param
#
    plt.close('all')
#
#---- set a few parameters
#
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)
#
#---- set a panel
#
    ax = plt.subplot(111)
    ax.set_autoscale_on(False)      #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)        #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- plot data
#
    p, = plt.plot(xdata, ydata, color='black', lw =0 , marker='.', markersize=1.5)
#
#--- add legend
#    
    plt.title(title)
    ax.set_xlabel(xname, size=8)
    ax.set_ylabel(yname, size=8)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=200)
#
#--- clean up all plotting param
#
    plt.close('all')

#----------------------------------------------------------------------------------------------
#--- plot_multi_panel: create multiple panel plots                                          ---
#----------------------------------------------------------------------------------------------

def plot_multi_panel(x_set_list, y_set_list, xname, yname_list, title_list, outname,\
                     linew=0, mrk='.', ylim=0, y_limit=[], autox='no'):

    """
    create multiple panel plots
    Input:  x_set_list --- a list of x data sets
            y_set_list --- a list of y data set
            xname      --- x axis legend
            yname_list --- a list of y axix legends
            title_list --- a list of title of each panel
            outname    --- output file name
            linew      --- line width of the plot. if 0 is given, no line is drawn
            mrk        --- a marker used for plot such as '.', '*', 'o'  '+'
            ylim       --- if it is 0, each panel uses different y plotting range, 
                           otherwise set to the same 
                           if it is 2, read y_list
            y_limit    --- a list of limit in y axis
    iutput: outname    --- a png plot file
    """
#
#--- how many panels?
#
    pnum = len(x_set_list)
#
#--- set x plotting_range
#
    (xmin, xmax) = find_plot_range(x_set_list)
    xmin = int(xmin) -1
    if autox == 'no':
        xmin = 0
        xmax = 370
#
#--- if it is requested set limit
#
    if ylim == 1:
        (ymin, ymax) = find_plot_range(y_set_list)
        ymin = int(ymin)
        ynax = int(ymax) + 1

#--- clean up all plotting param
#
    plt.close('all')
#
#---- set a few parameters
#
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    for i in range(0, pnum):
        axNam = 'ax' + str(i)
#
#---- set a panel #i
#
        if ylim == 0:
            ymin = 0
            if len(y_set_list[i]) > 0:
                ymax = max(y_set_list[i])
            else:
                ymax = ymin + 1

            diff = ymax - ymin
            if diff == 0:
                ymax = ymin + 1
            else:
                ymax += 0.1 * diff
        elif ylim == 2:
            ymin = 0 
            ymax = y_limit[i]

        j = i + 1
        if i == 0:
            pline = str(pnum) + '1' + str(j)
        else: 
            pline = str(pnum) + '1' + str(j) + ', sharex=ax0'

        exec("%s= plt.subplot(%s)" % (axNam, pline))
        exec("%s.set_autoscale_on(False)" % (axNam))
#
#--- these are necessary for the older version
#
        exec("%s.set_xbound(xmin,xmax)" % (axNam)) 
        exec("%s.set_xlim(xmin=%s, xmax=%s, auto=False)" % (axNam, xmin, xmax))
        exec("%s.set_ylim(ymin=%s, ymax=%s, auto=False)" % (axNam, ymin, ymax))
#
#--- plot data
#
        p, = plt.plot(x_set_list[i], y_set_list[i], color='black', lw =linew,\
                      marker= mrk, markersize=1.5)
#
#--- add legend
        leg = legend([p],  [title_list[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)
    
        exec("%s.set_ylabel('%s', size=8)" % (axNam, yname_list[i]))
#
#-- add x ticks label only on the last panel
#
        pval = pnum-1
        if i != pval:
            line = eval("%s.get_xticklabels()" % (axNam))
            for label in line:
                label.set_visible(False)
        else:
#            pass
#
#--- x label is only put at the last panel
#
            xlabel(xname)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=200)
#
#--- clean up all plotting param
#
    plt.close('all')

#----------------------------------------------------------------------------------
#--- find_plot_range: find a unifiedplotting range for multiple data sets       ---
#----------------------------------------------------------------------------------

def find_plot_range(p_set_list):
    """
    find a unifiedplotting range for multiple data sets
    input: p_set_list --- a list of data sets 
    output: pmin / pmax --- min and max of the data
    """
    if len(p_set_list[0]) > 0:
        ptmin = min(p_set_list[0])
        ptmax = max(p_set_list[0])
    else: 
        ptmin = 0
        ptmax = 0

    for i in range(1, len(p_set_list)):
        if len(p_set_list[i]) > 0:
            pmin = min(p_set_list[i])
            pmax = max(p_set_list[i])
            if pmin < ptmin:
                ptmin = pmin
            if pmax > ptmax:
                ptmax = pmax

    diff = ptmax - ptmin
    if diff == 0:
        ptmax = ptmin + 1
    else:
        ptmax += 0.01 * diff
        ptmin -= 0.01 * diff
        if ptmin < 0:
            ptmin = 0

    return(ptmin, ptmax)

#--------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    create_plots(year)
