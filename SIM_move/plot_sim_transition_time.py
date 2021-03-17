#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#           plot_sim_transition_time.py: create sim transit time trend plots                #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Feb 17, 2021                                                   #
#                                                                                           #
#############################################################################################
import os
import sys
import re
import string
import time
import Chandra.Time
import random
import numpy
#
#--- reading directory list
#
path = '/data/mta/Script/SIM_move/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf 
import sim_move_supple          as sms
#
#--- temp writing file name
#
import random
rtail   = int(time.time() * random.random())
zspace  = '/tmp/zspace' + str(rtail)
#
#--- some setting
#
detectors = ['ACIS-I','ACIS-S','HRC-I','HRC-S', 'All']
drange    = [[89000, 94103], [71420, 76820], [-51705, -49306], [-100800, -98400], [-110000, 101000]]
drange2   = [[-2000, 200],   [-2000,   200], [-2000,     200], [-2000,      200], [-2000,      200]]
drange3   = [[-2, 15],       [-2, 15],       [-2, 15],         [-2, 15],          [-2, 15]]
tail_list = ['week', 'month', 'year', 'full']
add_list  = [0, 86400, 3*86400, 365*86400]


dthisyear = time.strftime('%Y', time.gmtime())

#--------------------------------------------------------------------------------
#-- plot_sim_transition_time: create sim transit time trend plots             ---
#--------------------------------------------------------------------------------

def plot_sim_transition_time(tdata, xmin_range, today):
    """
    create sim transit time trend plots
    input:  tdata       --- a list of lists containing:
                        [[<starting inst>, <starting time>, <starting tsc>, <starting fa>],
                         [<stopping inst>, <stopping time>, <stopping tsc>, <stopping fa>]]
            xmin_range  --- list of starting times of week, month, one year, and full range plot
            today       --- today's time in seconds from 1998.1.1
    output: <web_dir>/Transit/transit_<inst>_<inst>_<range>.png
    """
#
#--- tsc plots
#
    line = ''
    for inst1 in range(0, 4):
        for inst2 in range(0, 4):
            if inst1 == inst2:
                continue 

            [stime, trans_time] = extract_transition_data_for_inst(tdata, inst1, inst2, 1)
            prep_and_plot(stime, trans_time, inst1, inst2, xmin_range, today)
#
#--- compute basic stats
#
            vary = numpy.array(trans_time)
            ind  = vary < 350.0                 #--- removing extreme values
            vary = vary[ind]
            avg  = numpy.mean(vary)
            std  = numpy.std(vary)
            line = line + str(inst1) + '\t' + str(inst2) + '\t'
            line = line + '%3.1f\t%3.1f' % (avg, std) + '\n'
#
#--- print out the stats
#
    ofile = data_dir + 'avg_sim_move_time'
    with open(ofile, 'w') as fo:
        fo.write(line)


#--------------------------------------------------------------------------------
#-- extract_transition_data_for_inst: extrat transit data for a given instrument combination
#--------------------------------------------------------------------------------

def extract_transition_data_for_inst(tdata, inst1, inst2, pos):
    """
    extrat transit data for a given instrument combination
    input:  tdata   --- a list of lists of data (see plot_sim_transition_time)
            inst1   --- starting instrument
            inst2   --- ending instrument
            pos     --- which msid is used: 2 tsc
    """

    stime      = []
    trans_time = []
    for ent in tdata:
        dset1 = ent[0]
        dset2 = ent[1]

        if dset1[0] != inst1:
            continue

        if dset2[0] != inst2:
            continue

        tdiff = abs(dset2[pos] - dset1[pos])

        stime.append(dset1[1])
        trans_time.append(tdiff)


    return [stime, trans_time]


#--------------------------------------------------------------------------------
#-- prep_and_plot: prepare the data for plotting and plot                      --
#--------------------------------------------------------------------------------

def prep_and_plot(x, y, inst1, inst2, xmin_range, today):
    """
    prepare the data for plotting and plot
    input:  x           --- a list of x data
            y           --- a list of y data
            inst1       --- starting instrument
            inst2       --- ending instrument
            xmin_range  --- starting time for week, month, year, and full range plot
            today       --- today's time in seconds from 1998.1.1
    output: <web_dir>/Transit/transit_<inst>_<inst>_<range>.png
    """
    title   = detectors[inst1] + ' to ' + detectors[inst2]
    yname   = 'Transit Time (sec)'
    y_range = [0, 370]
#
#--- set output file header
#
    detct1  = (detectors[inst1].replace('-','')).lower()
    detct2  = (detectors[inst2].replace('-','')).lower()
    head    = web_dir + 'Transit/tsc_' + detct1 + '_' + detct2  + '_' 
#
#--- go thrugh each plotting range
#
#    for k in range(0, 4):
    for k in range(3, 4):
        outname = head + tail_list[k] + '.png'
        cut     = xmin_range[k]

        xa      = numpy.array(x)
        ya      = numpy.array(y)
        indx    = xa > cut
        xa      = xa[indx]
#
#--- for week, month, and year, user y date
#
        ya      = ya[indx]
        if k in [0, 1, 2]:
            if len(xa) > 0 :
                byear, xr = sms.convert_time_format(xa)     #--- ydate
            else:
                xr    = xa
                byear = dthisyear

            xname = 'Time (YDay in Year: ' + str(byear) + ')'

            [year1, start] = sms.chandratime_to_yday(cut)
            [year2, stop]  = sms.chandratime_to_yday(today)
            if year1 == year2:
                x_range= [start, stop]
            else:
                if mcf.is_leapyear(byear):
                    base = 366
                else:
                    base = 365
                if byear == year1:
                    x_range = [start, stop + base]
                else:
                    x_range = [start - base, stop]
#
#--- for the year, use fractional year
#
        else:
            byear, xr = sms.convert_time_format(xa, ind=1)  #--- fractional year
            x_range = (1999, int(dthisyear) + 1)
            xname = 'Time (Year)'

        sms.plot_panel(xr, ya, x_range, y_range, xname, yname, title, outname)


#--------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_sim_transition_time()
