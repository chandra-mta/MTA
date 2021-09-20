#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################    
#                                                                                   #
#       plot_otg_move.py: plot otg move during the transition                       #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Sep 17, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import Chandra.Time
import matplotlib.pyplot as plt
import matplotlib as mpl
if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines

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

import Ska.engarchive.fetch as fetch
#
#--- reading directory list
#
path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list'
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
sys.path.append(mta_dir)

import mta_common_functions     as mcf
import random

tail = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(tail)

#-------------------------------------------------------------------------------------------
#-- plot_otg_move: plot otg move during the transition                                    --
#-------------------------------------------------------------------------------------------

def plot_otg_move():
    """
    plot otg move during the transition
    input:  none but read from <arc_dir>/OTG_summary.rdb and ska database
    output: <arc_dir>/Plots/<name>.png
    """
    done_list = find_existing_plots()

    ifile     = arc_dir + 'OTG_summary.rdb'
    data      = mcf.read_data_file(ifile)

    for ent in data[2:]:
        atemp = re.split('\s+', ent)
        start = atemp[2]
        stop  = atemp[4]

        name  = start.replace('.','')
        if name in done_list:
            continue

        try:
            start = convert_time_format(start)
            stop  = convert_time_format(stop) 
        except:
            continue

        print("START: " + start)
#
#--- add extra 15 secs to the end
#
        stop  = Chandra.Time.DateTime(stop).secs + 15.0
        stop  = Chandra.Time.DateTime(stop).date

        try:
            create_plot(start, stop, name)
        except:
            continue

#-------------------------------------------------------------------------------------------
#-- find_existing_plots: find names of data which already plotted                         --
#-------------------------------------------------------------------------------------------

def find_existing_plots():
    """
    find names of data which already plotted
    input:  none, but read from <arc_dir>/Plots/*
    output: file_list   --- a list of plot file names
    """

    cmd = 'ls ' + arc_dir + 'Plots/*.png > ' + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)
    file_list = []
    for ent in data:
        atemp = re.split('\/', ent)
        btemp = re.split('\.png', atemp[-1])
        file_list.append(btemp[0])

    return file_list

#-------------------------------------------------------------------------------------------
#-- convert_time_format: convert time format from <yyyy><ddd>.<hh><mm><ss.ss> tp <yyyy>:<ddd>:<hh>:<mm>:<ss>
#-------------------------------------------------------------------------------------------

def convert_time_format(tline):
    """
    convert time format from <yyyy><ddd>.<hh><mm><ss.ss> tp <yyyy>:<ddd>:<hh>:<mm>:<ss>
    input:  time in <yyyy><ddd>.<hh><mm><ss.ss>
    output: time in yyyy>:<ddd>:<hh>:<mm>:<ss>
    """
    tl = tline.replace('.','')
    year = tl[0]  + tl[1] + tl[2] + tl[3]
    yday = tl[4]  + tl[5] + tl[6]
    hh   = tl[7]  + tl[8]
    mm   = tl[9]  + tl[10]
    ss   = tl[11] + tl[12]

    out  = year + ':' + yday + ':' + hh + ':' + mm + ':' + ss

    return out

#-------------------------------------------------------------------------------------------
#-- create_plot: plot data                                                                --
#-------------------------------------------------------------------------------------------

def create_plot(start, stop, name):
    """
    plot data
    input:  start   --- start time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stop time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            name    --- the name of the file 
    output: <arc_dir>/Plots/<name>.png
    """
#
#--- find the year of the data
#
    atemp = re.split(':', start)
    year  = atemp[0]
    yday  = atemp[1]
#
#--- extract data from ska
#
    data  = fetch.MSID('4MP28AV', start=start, stop=stop)
    clf()
#
#--- set font size
#
    mpl.rcParams['font.size'] = 6
    props = font_manager.FontProperties(size=6)
    plt.subplot(1,1,1)
#
#--- plot data
#
    data.plot()
#
#--- plot labels
#
    xline = 'Time (' + year + ':' + yday + ')'
    plt.xlabel(xline)
    plt.ylabel('4MP28AV')
#
#--- set the szie etc
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(6.0, 3.0)

    outfile = arc_dir +  'OTG_Plots/Ind_Plots/' + name + '.png'
    plt.savefig(outfile, format='png', dpi=300)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":


    plot_otg_move()
