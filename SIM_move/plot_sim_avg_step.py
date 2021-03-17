#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       plot_sim_avg_step.py: create time per step time trend plots                     #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Feb 17, 2021                                                   #
#                                                                                       #
#########################################################################################

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
detectors = ['ACIS-I','ACIS-S','HRC-I','HRC-S', 'All']
drange    = [[89000, 94103], [71420, 76820], [-51705, -49306], [-100800, -98400], [-110000, 101000]]
drange2   = [[-2000, 200],   [-2000,   200], [-2000,     200], [-2000,      200], [-2000,      200]]
drange3   = [[-2, 15],       [-2, 15],       [-2, 15],         [-2, 15],          [-2, 15]]
tail_list = ['week', 'month', 'year', 'full']
add_list  = [0, 86400, 3*86400, 365*86400]

dthisyear = time.strftime('%Y', time.gmtime())

#--------------------------------------------------------------------------------
#-- plot_sim_avg_step: create time per step time trend plots                  ---
#--------------------------------------------------------------------------------

def plot_sim_avg_step(tdata, this_year, this_mon):
    """
    create time per step time trend plots
    input:  tdata   --- a list of lists of: 
                            [[<starting inst>, <starting time>, <starting tsc>, <starting fa>],
                             [<stopping inst>, <stopping time>, <stopping tsc>, <stopping fa>]]
            this_year   --- this year (in yyyy form)
            this_mon    ---- this month (in mm form)
    output: <web_dir>/Step/tsc_steps_<inst>_<inst>png
    """
#
#---- set month interval table
#
    month_list = set_month_interval(this_year, this_mon)
#
#--- select combination of instruments
#
    line = ''
    for inst1 in range(0, 4):
        for inst2 in range(0, 4):
            if inst1 == inst2:
                continue
#
#--- tsc plots
#
            [stime, rate] = extract_transition_data_for_inst(tdata, inst1, inst2, 2)
            prep_and_plot(stime, rate, inst1, inst2, 'tsc')
#
#--- compute some stat
#
            line = line + str(inst1) + '\t' + str(inst2) + '\t'
            vary = numpy.array(rate)
            ind  = vary < 0.1
            vary = vary[ind]
            avg  = numpy.mean(vary)
            line = line + str(len(vary)) + '\t' +  '%1.5f' % (avg) + '\n'
#
#--- monthly average
#
    [stime, rate] = extract_transition_data_monthly_avg(tdata, month_list, 2)
    prep_and_plot(stime, rate, 'all', 'all', 'tsc')
#
#--- print out the stat
#
    ofile = data_dir + 'avg_sim_step_size'
    with open(ofile, 'w') as fo:
        fo.write(line)

#--------------------------------------------------------------------------------
#-- extract_transition_data_for_inst: extract transit data for the combination of two instruments
#--------------------------------------------------------------------------------

def extract_transition_data_for_inst(tdata, inst1, inst2, pos):
    """
    extract transit data for the combination of two instruments
    input:  tdata       --- a list of lists of data (see: plot_sim_avg_step)
            inst1       --- starting instrument
            inst2       --- ending instrument
            pos         --- msid pos, usually tsc
    output: <web_dir>/Step/tsc_steps_<inst>_<inst>.png

    """
    tsave = []
    msave = []

    for ent in tdata:
        dset1 = ent[0]
        dset2 = ent[1]

        if dset1[0] != inst1:
            continue

        if dset2[0] != inst2:
            continue

        fstep = float(abs(dset2[pos] - dset1[pos]))

        if fstep == 0.0:
            continue

        tstep = (dset2[1] - dset1[1]) / fstep

        if tstep == 0:
            continue

        atime = 0.5 * (dset1[1] + dset2[1])

        tsave.append(atime)
        msave.append(tstep)

    return [tsave, msave]

#
#--------------------------------------------------------------------------------
#-- extract_transition_data_monthly_avg: create monthly averaged transit data   -
#--------------------------------------------------------------------------------

def extract_transition_data_monthly_avg(tdata, month_list, pos):
    """
    create monthly averaged transit data
    input:  tdata       --- a list of lists of data (see: plot_sim_avg_step)
            month_list  --- a list of month intervals in seconds from 1998.1.1
            pos         --- msid postion
    output: mc_list     --- a list of time centered at each momth
            rate        --- ia list of ates of the month
    """

    [mb_list, me_list, mc_list] = month_list
    mlen  = len(mb_list)
    msave = []
    csave = []
    for k in range(0, mlen):
        msave.append(0)
        csave.append(0)

    for ent in tdata:
        dset1 = ent[0]
        dset2 = ent[1]

        for k in range(0, mlen):
            atime = 0.5 * (dset1[1] + dset2[1])
            fstep = float(abs(dset2[pos] - dset1[pos]))

            if fstep == 0.0:
                continue

            tstep = (dset2[1] - dset1[1]) / fstep

            if tstep == 0:
                continue

            if (atime >= mb_list[k]) and (atime <= me_list[k]):
                msave[k] = msave[k] + tstep
                csave[k] = csave[k] + 1
                break
            else:
                continue

    rate = []
    for k in range(0, mlen):
        if msave[k] > 0:
            avg = msave[k] / csave[k]
        else:
            avg = 0
        rate.append(avg)

    return [mc_list, rate]


#--------------------------------------------------------------------------------
#-- prep_and_plot: prepare the data and create a plot                         ---
#--------------------------------------------------------------------------------

def prep_and_plot(x, y, inst1, inst2, head):
    """
    prepare the data and create a plot
    input:  x       --- a list of x data
            y       --- a list of y data
            inst1   --- starting instrument
            inst2   --- ending instrument
            head    --- a header of the output file
    output: <web_dir>/Step/tsc_steps_<inst>_<inst>.png
    """
    yname   = 'Seconds / Step'
    y_range = [0.0, 0.004]
#
#--- monthly averaged transit case
#
    if inst1 == 'all':
        outname = web_dir + 'Step/' + head + '_monthly_steps.png' 
        title   = 'SIM Monthly Move Rate'
#
#--- indivisual instrument combination case
#
    else:
        detct1  = (detectors[inst1].replace('-','')).lower()
        detct2  = (detectors[inst2].replace('-','')).lower()
        outname = web_dir + 'Step/' + head + '_steps_' + detct1 + '_' + detct2  + '.png' 
        title   = detectors[inst1] + ' to ' + detectors[inst2]

    byear, xr = sms.convert_time_format(x, ind=1)  #--- fractional year
    x_range = (1999, int(dthisyear) + 1)
    xname = 'Time (Year)'

    sms.plot_panel(xr, y, x_range, y_range, xname, yname, title, outname, tind=1)

#--------------------------------------------------------------------------------
#-- set_month_interval: create month interval list                             --
#--------------------------------------------------------------------------------

def set_month_interval(this_year, this_mon):
    """
    create month interval list
    input:  this_year   --- this year in yyyy format
            this_mon    --- this month in mm format
    otput:  a list of lists of: [starting time], [ending time], [mid time of the month in second from 1998.1.1]]
    """

    start     = []
    stop      = []
    mid       = []
    for year in range(1999, this_year + 1):
        for mon in range(1, 13):
            if (year == 19999) and (mon < 8):
                continue
            elif (year == this_year) and (mon >= this_mon):
                break

            btime = str(year)  + ':' + mcf.add_leading_zero(mon)  + ':01:00:00:00'
            btime = time.strftime('%Y:%j:%H:%M:%S', time.strptime(btime, '%Y:%m:%d:%H:%M:%S'))
            nmon  = mon + 1
            nyear = year
            if nmon > 12:
                nmon   = 1
                nyear += 1
            etime = str(nyear) + ':' + mcf.add_leading_zero(nmon) + ':01:00:00:00'
            etime = time.strftime('%Y:%j:%H:%M:%S', time.strptime(etime, '%Y:%m:%d:%H:%M:%S'))

            begin = int(Chandra.Time.DateTime(btime).secs)
            end   = int(Chandra.Time.DateTime(etime).secs)
            avg   = int(0.5 * (begin + end))

            start.append(begin)
            stop.append(end)
            mid.append(avg)

    return [start, stop, mid]

#--------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_sim_avg_step()
