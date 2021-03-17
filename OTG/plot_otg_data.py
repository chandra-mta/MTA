#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#########################################################################################
#                                                                                       #
#           plot_otg_data.py: create otg related plots                                  #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.eud)                                   #
#                                                                                       #
#           last update: Jan 11, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import numpy

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
path = '/data/mta4/Script/Dumps/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions as mcf

#---------------------------------------------------------------------------------------
#-- plot_otg_data: create otg realted plots                                           --
#---------------------------------------------------------------------------------------

def plot_otg_data():
    """
    create otg realted plots
    input:  none but read from <arc_dir>/OTG_sorted.rdb'
    output: <arc_dir>/OTG_Plots/*png
    """
#
#--- read the data
#
    infile  = arc_dir + 'OTG_sorted.rdb'
    data    = mcf.read_data_file(infile)
#
#--- get headers
#
    hdr1    = data[0]
    hdr2    = data[1]
    h1_list = re.split('\s+', hdr1)
    h2_list = re.split('\s+', hdr2)
#
#--- find out which ones are numeric entries
#
    cols    = []
    for k in range(6, len(h1_list)):
        if h2_list[k] == 'N':
            cols.append(h1_list[k])
#
#--- create separate data sets for hetg/letg, insr/reter
#
    hetg_i  = [hdr1, hdr2]
    hetg_r  = [hdr1, hdr2]
    letg_i  = [hdr1, hdr2]
    letg_r  = [hdr1, hdr2]
    hi_time = []
    hr_time = []
    li_time = []
    lr_time = []
    xmax    = 2000.0

    for ent in data[2:]:
        atemp = re.split('\s+', ent)
        dirn  = atemp[0]
        grat  = atemp[1]

        otime = atemp[2]
        ntime = convert_time_format(otime)
        if ntime > xmax: 
            xmax = ntime

        if grat == 'HETG':

            if dirn == 'INSR':
                hetg_i.append(ent)
                hi_time.append(ntime)
            elif dirn == 'RETR':
                hetg_r.append(ent)
                hr_time.append(ntime)

        elif grat == 'LETG':

            if dirn == 'INSR':
                letg_i.append(ent)
                li_time.append(ntime)
            elif dirn == 'RETR':
                letg_r.append(ent)
                lr_time.append(ntime)
#
#--- convert the data lists into a dictionary format
#
    hetg_i_dict = create_dict(hetg_i)
    hetg_r_dict = create_dict(hetg_r)
    letg_i_dict = create_dict(letg_i)
    letg_r_dict = create_dict(letg_r)

    xSets = [hi_time, hr_time, li_time, lr_time]
    labels = ['HETG INSR', 'HETG RETR', 'LETG INSR', 'LETG RETR']
#
#--- start plotting each numeric msids
#
    for cnam in cols:
#
#--- convert data into float
#
        yset1   = [float(d) for d in hetg_i_dict[cnam]]
        yset2   = [float(d) for d in hetg_r_dict[cnam]]
        yset3   = [float(d) for d in letg_i_dict[cnam]]
        yset4   = [float(d) for d in letg_r_dict[cnam]]
        ySets   = [yset1, yset2, yset3, yset4]

        outname = arc_dir + 'OTG_Plots/' + cnam + '_plot.png'
#
#--- calling plotting routine
#
        plot_multi_panel(2000, xmax, xSets, ySets, "Time (year)", cnam, labels, outname)

#---------------------------------------------------------------------------------------
#--- plot_multi_panel: plots multiple data in separate panels                        ---
#---------------------------------------------------------------------------------------

def plot_multi_panel(xmin, xmax, xSets, ySets, xname, yname, entLabels, outname,\
                     yerror=0, fsize = 9, psize = 2.0, marker = 'o', pcolor =1, \
                     lcolor=7,lsize=0, resolution=100, linefit=0, connect=0):

    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax  plotting range of x axis
            xSets:      a list of lists containing x-axis data
            ySets:      a list of lists containing y-axis data
            xname:      x axis label
            yname:      y axis label
            entLabels:  a list of the names of each data
            outname:    a name of plotting file
            yerror:     a list of lists of error on y, or if it is '0' no error bar on y, default = 0
            fsize:      font size, default = 9
            psize:      plotting point size, default = 2.0
            marker:     marker shape, defalut = 'o'
            pcolor:     color of the point, default= 7 ---> 'black'
            lcolor:     color of the fitted line, default = 7 ---> 'black'
                        colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime', 
                                     'maroon', 'black', 'olive', 'yellow')
            lsize:      fitted line width, defalut = 1
            resolution: plotting resolution in dpi, default = 100
            linefit:    if 1, linear line is fitted, default: 0
            connect:    connected line size. if it is '0', no connected line

    Output: a png plot: outname
    """
#
#--- set line color list
#
    colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime',\
                 'maroon', 'black', 'olive', 'yellow')
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = fsize 
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- start plotting each data
#
    for i in range(0, tot):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec("%s = plt.subplot(%s)"       % (axNam, line))
        exec("%s.set_autoscale_on(False)" % (axNam))
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))
        exec("%s.set_xlim(left=xmin, right=xmax, auto=False)" % (axNam))

        ymax = 1.3 * max(ySets[i])
        if ymax == 0:
            ymax = 1.0

        exec("%s.set_ylim(bottom=0, top=ymax, auto=False)" % (axNam))

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[pcolor], marker= marker,\
                      markersize=psize, lw =connect)
#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec("%s.set_ylabel(yname, size=fsize)" % (axNam))
#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            line = eval("%s.get_xticklabels()" % (ax))
            for label in  line:
                label.set_visible(False)
        else:
            pass

    xlabel(xname)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)

#-------------------------------------------------------------------------------------------
#-- create_dict: convert data list into a dictionary form                                 --
#-------------------------------------------------------------------------------------------

def create_dict(indata):
    """
    convert data list into a dictionary form
    input:  infile  --- assume that the first two lines are header
    output: d_dict  --- dictionary of header <---> data list
    """
    head   = re.split('\s+', indata[0].strip())
    hlen   = len(head)
    save   = []
    for k in range(0, hlen):
        save.append([])
#
#--- top two lines of the data are headers
#
    dpart  = indata[2:]
    d_dict = {}
    
    for ent in dpart:
    
        atemp = re.split('\s+', ent)
        if len(atemp) == hlen:
            for k in range(0, hlen):
                save[k].append(atemp[k])
    
    for k in range(0, hlen):
        d_dict[head[k]] = save[k]
    
    return d_dict

#-------------------------------------------------------------------------------------------
#-- convert_time_format: convert otg time format to fractional year                      ---
#-------------------------------------------------------------------------------------------

def convert_time_format(ft):
    """
    convert otg time format to fractional year
    input:  ft      --- otg time (e.g. 2019036.0239520)
    output: otime   --- fractional year
    """
    year = float(ft[0]  + ft[1] + ft[2] + ft[3])
    yday = float(ft[4]  + ft[5] + ft[6])
    hh   = float(ft[8]  + ft[9])
    mm   = float(ft[10] + ft[11])
    ss   = float(ft[12] + ft[13])

    if mcf.is_leapyear(year):
        base = 366.0
    else:
        base = 365.0

    otime = year + (yday + hh/24.0 + mm /3600.0 + ss/ 86400.0) / base

    return otime

#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_otg_data()
