#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################################
#                                                                                                       #
#   classify_sim_data_and_plot.py: classify the sim postion data and create sim movement related plots  #
#                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                       #
#           last update: Mar 08, 2021                                                                   #
#                                                                                                       #
#########################################################################################################

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
import plot_sim_position        as psp
import plot_sim_transition_time as pstt
import plot_sim_avg_step        as psas
#
#--- temp writing file name
#
import random
rtail   = int(time.time() * random.random())
zspace  = '/tmp/zspace' + str(rtail)
#
#--- some setting
#
tlimit    = 500.0           #--- set maximum allowable move time in seconds
staytime  = 1500.0          #--- set minimum time instrument must stay in position 
                            #---to be considered "settled"
detectors = ['ACIS-I','ACIS-S','HRC-I','HRC-S', 'All']
drange    = [[89000, 94103], [71420, 76820], [-51705, -49306], [-100800, -98400], [-110000, 101000]]
drange2   = [[-2000, 200],   [-2000,   200], [-2000,     200], [-2000,      200], [-2000,      200]]
drange3   = [[-2, 15],       [-2, 15],       [-2, 15],         [-2, 15],          [-2, 15]]
tail_list = ['week', 'month', 'year', 'full']
add_list  = [0, 86400, 3*86400, 365*86400]

#--------------------------------------------------------------------------------
#-- classify_sim_data_and_plot: classify the sim postion data and create sim movement related plots
#--------------------------------------------------------------------------------

def classify_sim_data_and_plot():
    """
    classify the sim postion data and create sim movement related plots
    input:  none, but read from <data_dir>/sim_data.out
    output: various plots in <web_dir>/<cateogry dir>
    """
#
#--- setting time in fractional year
#
    tout       = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    ctime      = Chandra.Time.DateTime(tout).secs
    today      = ctime
#
#--- set data starting time for different period plots
#
    wago       = ctime - 86400 * 7
    mago       = ctime - 86400 * 30
    yago       = ctime - 86400 * 365

    xmin_range = [wago, mago, yago, 31536000]

    this_year  = int(float(time.strftime('%Y', time.gmtime())))
    this_mon   = int(float(time.strftime('%m', time.gmtime())))
#
#--- setting x axis plotting range etc
#
    xmax      = this_year + 1
    if this_mon >6:
        xmax += 1
#
#--- read the sim data
#
    ifile = data_dir + 'sim_data.out'
    sdata = mcf.read_data_file(ifile)
#
#--- save week long data
#
    t_list_w   = []
    tsc_list_w = []
    fa_list_w  = []
    mpw_list_w = []
    inst_w     = []
#
#--- save entire range
#
    t_list     = []
    tsc_list   = []
    fa_list    = []
    mpw_list   = []
    inst       = []

    for ent in sdata:
        atemp = re.split('\s+', ent)
        stime = float(Chandra.Time.DateTime(atemp[0]).secs)
        tsc   = float(atemp[1])
        fa    = float(atemp[2])
        mp    = float(atemp[3])
#
#--- occasionally fa value is 9999; use one value before
#
        if fa == 9999:
            fa = fa_list[-1]

        t_list.append(stime)
        tsc_list.append(tsc)
        fa_list.append(fa)
        mpw_list.append(mp)
#
#--- acis i
#
        if (tsc   > drange[0][0]) and(tsc < drange[0][1]):
            inst.append(0)
#
#--- acis s
#
        elif (tsc > drange[1][0]) and(tsc < drange[1][1]):
            inst.append(1)
#
#--- hrc i
#
        elif (tsc > drange[2][0]) and(tsc < drange[2][1]):
            inst.append(2)
#
#--- hrc s
#
        elif (tsc > drange[3][0]) and(tsc < drange[3][1]):
            inst.append(3)
#
#--- something else: transition area
#
        else:
            inst.append(4)
#
#--- week long data
#
        if stime > wago:
            t_list_w.append(stime)
            tsc_list_w.append(tsc)
            fa_list_w.append(fa)
            mpw_list_w.append(mp)
            inst_w.append(inst[-1])
#
#--- convert to numpy array
#
    t_array    = numpy.array(t_list)
    tsc_array  = numpy.array(tsc_list)
    fa_array   = numpy.array(fa_list)
    mpw_array  = numpy.array(mpw_list)
    inst_array = numpy.array(inst)

#
#--- create sim transition data
#
    tdata = find_sim_movement_time(t_list, tsc_list, fa_list, inst)

    print("Done Classifying Data")
##
##--- plot sim position
##
#    psp.plot_sim_position(t_array, tsc_array, fa_array, mpw_array, inst_array, xmin_range, today)
#    print("SIM Position Plot Done")
##
##--- plot sim transition time
##
#    pstt.plot_sim_transition_time(tdata, xmin_range, today)
#    print("SIM Transition Plot Done")
##
##--- plot sim average step
##
#    psas.plot_sim_avg_step(tdata, this_year, this_mon)
#    print("SIM Step Size Plot Done")
#
#--- handle the week long data
#
    wdata = find_sim_movement_time(t_list_w, tsc_list_w, fa_list_w, inst_w)
#
#--- creating stat for the weekly report
#
    [fmcnt, fmavg] = find_move_stat(tdata)
    [wmcnt, wmavg] = find_move_stat(wdata)

    line = str(fmcnt) + '\t' + str(fmavg) + '\t' + str(wmcnt) + '\t' + str(wmavg) + '\n'
    ofile = data_dir + 'weekly_report_stat'
    with open(ofile, 'w') as fo:
        fo.write(line)

#--------------------------------------------------------------------------------
#-- find_move_stat: compute stats for weekly report                            --
#--------------------------------------------------------------------------------

def find_move_stat(data):
    """
    compute stats for weekly report
    input:  data
            [[<starting inst>, <starting time>, <starting tsc>, <starting fa>],
             [<stopping inst>, <stopping time>, <stopping tsc>, <stopping fa>]]
    output: mcnt    --- numbers of sim movement
            mavg    --- avg time per step
    """

    mcnt = len(data)
    tsum = 0.0
    msum = 0.0
    for k in range(0, mcnt):
        tsum += data[k][1][1] - data[k][0][1]
        msum += abs(data[k][1][2] - data[k][0][2])

    mavg = tsum / msum

    return [mcnt, mavg]


#--------------------------------------------------------------------------------
#-- find_sim_movement_time: find when sim is transitted to the next instrument --
#--------------------------------------------------------------------------------

def find_sim_movement_time(t_list, tsc_list, fa_list, inst_list):
    """
    find when sim is transitted to the next instrument
    input:  t_list      --- a list of time
            tsc_list    --- a list of tsc values
            fa_list     --- a list of fa values
            inst_list   --- a list of instrument
    output: transtab    --- a list of lists containing:
                            [[<starting inst>, <starting time>, <starting tsc>, <starting fa>],
                             [<stopping inst>, <stopping time>, <stopping tsc>, <stopping fa>]]
    """
    dlen     = len(t_list)
    transtab = []
    moving   = 0
    tstart   = 0

    for k in range(0, dlen):
#
#--- in transit
#
        if inst_list[k] == 4:                   #--- 4 means not in any instrument range
#
#--- when it moves into the transit area, record the time etc
#
            if moving == 0:
                tstart = t_list[k-1]
                pstart = tsc_list[k-1]
                p0     = tsc_list[k]
                qstart = fa_list[k-1]
                istart = inst_list[k-1]
                moving = 1
#
#--- in one of the instrument range
#
        else:
            if moving == 1:
                tmpend  = t_list[k]
                tmpinst = inst_list[k]
                moving  = 0
#
#--- find how long it stays in that instrument range
#
                for j in range(k, dlen):
                    if inst_list[j] == tmpinst:
                        continue
#
#--- it is settled in that range, write out the transit information
#
                tdiff = t_list[j-1] - tmpend
                if tdiff > staytime:
                    tstop  = t_list[k]
                    p1     = tsc_list[k-1]
                    pstop  = tsc_list[k]
                    qstop  = fa_list[k-1]
                    istop  = inst_list[k]

                    if (tstop - tstart) < tlimit:
                        out    = [[istart, int(tstart), int(pstart), int(qstart)],\
                              [istop,  int(tstop),  int(pstop),  int(qstop) ]]
                        transtab.append(out)
                    
                    moving = 0
    
                    k      = j - 1
                    continue
#
#--- it is still mvoing to another instrument
#
                else:
                    moving = 1


    return transtab


#--------------------------------------------------------------------------------

if __name__ == "__main__":

   classify_sim_data_and_plot()
