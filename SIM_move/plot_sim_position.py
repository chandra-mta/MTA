#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#       plot_sim_position.py: create sim positional trend plots                             #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 17, 2021                                                       #
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

#--------------------------------------------------------------------------------
#-- plot_sim_position: create sim positional trend plots                       --
#--------------------------------------------------------------------------------

def plot_sim_position(t_array, tsc_array, fa_array, mpw_array, inst_array, xmin_range, today):
    """
    create sim positional trend plots
    input:  t_array     --- an array of time data
            tsc_array   --- an array of tsc data
            fa_array    --- an array of fa data
            mpw _array  --- an array of mrmmxmv data
            inst_array  --- an array of instrument indecies
            xmin_range  --- a list of starting time in week, month, year and full range plot
            today       --- today's time in seconds from 1998.1.1
    output: <web_dir>/Postion/<msid>_<inst>_<type>.png
    """
#
#--- acis i
#
    prep_and_plot(0, xmin_range, t_array, tsc_array, inst_array, drange,  'tscpos',  today, 'SIM Position')
    prep_and_plot(0, xmin_range, t_array, fa_array,  inst_array, drange2, 'fapos',   today, 'FA Position')
    prep_and_plot(0, xmin_range, t_array, mpw_array, inst_array, drange3, 'mrmmxmv', today, '3MRMMXMV')

    prep_and_lot2(0, tsc_array, mpw_array, t_array, inst_array, drange, drange3, xmin_range, "tsc_mxmv", 'TSCPOS', 'MRMMXMV')
#
#--- acis s
#
    prep_and_plot(1, xmin_range, t_array, tsc_array, inst_array, drange,  'tscpos',  today, 'SIM Position')
    prep_and_plot(1, xmin_range, t_array, fa_array,  inst_array, drange2, 'fapos',   today, 'FA Position')
    prep_and_plot(1, xmin_range, t_array, mpw_array, inst_array, drange3, 'mrmmxmv', today, '3MRMMXMV')

    prep_and_lot2(1, tsc_array, mpw_array, t_array, inst_array, drange, drange3, xmin_range, "tsc_mxmv", 'TSCPOS', 'MRMMXMV')
#
#--- hrc i
#
    prep_and_plot(2, xmin_range, t_array, tsc_array, inst_array, drange,  'tscpos',  today, 'SIM Position')
    prep_and_plot(2, xmin_range, t_array, fa_array,  inst_array, drange2, 'fapos',   today, 'FA Position')
    prep_and_plot(2, xmin_range, t_array, mpw_array, inst_array, drange3, 'mrmmxmv', today, '3MRMMXMV')

    prep_and_lot2(2, tsc_array, mpw_array, t_array, inst_array, drange, drange3, xmin_range, "tsc_mxmv", 'TSCPOS', 'MRMMXMV')
#
#--- hrc s
#
    prep_and_plot(3, xmin_range, t_array, tsc_array, inst_array, drange,  'tscpos',  today, 'SIM Position')
    prep_and_plot(3, xmin_range, t_array, fa_array,  inst_array, drange2, 'fapos',   today, 'FA Position')
    prep_and_plot(3, xmin_range, t_array, mpw_array, inst_array, drange3, 'mrmmxmv', today, '3MRMMXMV')

    prep_and_lot2(3, tsc_array, mpw_array, t_array, inst_array, drange, drange3, xmin_range, "tsc_mxmv", 'TSCPOS', 'MRMMXMV')
#
#--- full data
#
    prep_and_plot(4, xmin_range, t_array, tsc_array, inst_array, drange,  'tscpos',  today, 'SIM Position')
    prep_and_plot(4, xmin_range, t_array, fa_array,  inst_array, drange2, 'fapos',   today, 'FA Position')
    prep_and_plot(4, xmin_range, t_array, mpw_array, inst_array, drange3, 'mrmmxmv', today, '3MRMMXMV')

    prep_and_lot2(4, tsc_array, mpw_array, t_array, inst_array, drange, drange3, xmin_range, "tsc_mxmv", 'TSCPOS', 'MRMMXMV')


#--------------------------------------------------------------------------------
#-- prep_and_plot: prepare data for specific plot and plot it                 ---
#--------------------------------------------------------------------------------

def prep_and_plot(pos, xmin_range, x_list, y_list, inst, drange, prefix, today, yname):
    """
    prepare data for specific plot and plot it
    input:  pos         --- indicator of instrument
            xmin_range  --- a list of starting time
            x_list      --- an array of time data
            y_list      --- an array of selected msid data
            inst        --- an array of instrument (in values between 0 and 4)
            drange      --- a list of data range
            prefix      --- indicator of which data set
            today       --- today's time in seconds from 1998.1.1
            yname       --- y axis label
    output: <web_dir>/Position/<msid>_<inst>_<range>.png
    """

#
#--- select data for the instrument
#
    if pos == 4:                                #--- combine data set
        xr   = x_list
        yr   = y_list
    else:
        indx = inst == pos
        xr   = x_list[indx]
        yr   = y_list[indx]

    title   = detectors[pos].replace('-','_')
    y_range = drange[pos]
#
#--- week, month, year, and full range plots
#
    #for  k in range(0, 4):
    for  k in range(3, 4):
        tail    = tail_list[k]
        outname = web_dir + 'Position/' + prefix + '_' + title.lower() + '_' + tail + '.png' 
        x_range = [xmin_range[k], today + add_list[k]]
#
#--- converting to yday
#
        if k in [0, 1, 2]:
            indx    = xr > xmin_range[k]
            x       = xr[indx]
            y       = yr[indx]
            if len(x) < 1:
                cmd = 'cp ' + house_keeping + 'no_plot.png ' + outname
                os.system(cmd)
                continue 

            byear, x       = sms.convert_time_format(x, 0)
            [year1, start] = sms.chandratime_to_yday(x_range[0])
            [year2, stop]  = sms.chandratime_to_yday(x_range[1])
            if year1 == year2:
                x_range = [start, stop]
            else:
                if mcf.is_leapyear(byear):
                    base = 366
                else:
                    base = 365
                if byear == year1:
                    x_range = [start, stop + base]
                else:
                    x_range = [start - base, stop]

            xname    = 'Time (YDay in Year: ' + str(byear) + ')'
#
#--- converting to fractional year
#
        else:
            byear, x = sms.convert_time_format(xr, 1)
            y        = yr
            start    = mcf.chandratime_to_fraq_year(x_range[0])
            stop     = mcf.chandratime_to_fraq_year(x_range[1])
            x_range  = [start, stop]
            xname    = 'Time (in Year)'

        sms.plot_panel(x, y, x_range, y_range, xname, yname, title, outname)


#--------------------------------------------------------------------------------
#-- prep_and_lot2: prepare data for specific plot and plot it                  --
#--------------------------------------------------------------------------------

def prep_and_lot2(pos, x_list, y_list, t_list, inst, x_range, y_range, t_range, prefix, xname, yname):
    """
    prepare data for specific plot and plot it
    input:  pos         --- indicator of instrument
            xmin_range  --- a list of starting time
            x_list      --- an array of time data
            y_list      --- an array of selected msid data
            inst        --- an array of instrument (in values between 0 and 4)
            drange      --- a list of data range
            prefix      --- indicator of which data set
            today       --- today's time in seconds from 1998.1.1
            yname       --- y axis label
    output: <web_dir>/Position/tsc_mxmv_<inst>_<range>.png
    """
#
#--- select data for the instrument
#
    if pos == 4:                                #--- combine data set
        xr   = x_list
        yr   = y_list
        tr   = t_list
    else:
        indx = inst == pos
        xr   = x_list[indx]
        yr   = y_list[indx]
        tr   = t_list[indx]

    title    = detectors[pos].replace('-','_')

    for k in range(0, 4):
        tail    = tail_list[k]
        outname = web_dir + 'Position/' + prefix + '_' + title.lower() + '_' + tail + '.png' 
        indx    = tr > t_range[k]
        x       = xr[indx]
        y       = yr[indx]

        sms.plot_panel(x, y, x_range[pos], y_range[pos], xname, yname, title, outname)

#--------------------------------------------------------------------------------

if __name__ == "__main__":

    plot_sim_position()
