#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       separate_data_from_begining.py: create angle separated data file from begining          #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 12, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import numpy
import time
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/Sol_panel/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions   as mcf    #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
import random
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a couple of lists
#
angle_list = [40, 60, 80, 100, 120, 140, 160]
header     = 'time\tsuncent\ttmysada\ttpysada\ttsamyt\ttsapyt\ttfssbkt1\ttfssbkt2'
header     = header + '\ttpc_fsse\telbi\telbv\tobattpwr\tohrmapwr\toobapwr'

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def run_data_sepration():

    cmd = 'rm -rf ' + data_dir + 'solar_panne_angle_*'
    os.system(cmd)
#
#--- read the data
#
    ifile = data_dir + "solar_panel_all_data"
    out   = mcf.read_data_file(ifile)
    data  = []
    for ent in data:
        if ent[0] == '#'
            continue
        else:
            data.append(ent)

    separate_data_into_angle_step(data, 0)

#---------------------------------------------------------------------------------------
#-- separate_data_into_angle_step: separate a full data set into several angle interval data sets 
#---------------------------------------------------------------------------------------

def separate_data_into_angle_step(data, tstart=0):
    """
    separate a full data set into several angle interval data sets
    input:  data    --- data matrix of <col numbers> x <data length>
            tstart  --- starting time in seconds from 1998.1.1
    output: <data_dir>/solar_panel_angle_<angle>
    """
#
#--- set a few things
#
    alen  = len(angle_list)             #--- the numbers of angle intervals
    clen  = len(data)                   #--- the numbers of data columns
    save  = []                          #--- a list of lists to sve the data
    for k in range(0, alen):
        save.append([])
#
#--- go through all time entries, but ignore time before tstart
#
    for k in range(0, len(data[0])):
        if data[0][k] < tstart:
            continue

        for m in range(0, alen):
#
#--- set angle interval; data[1] is the column to keep sun center angle
#
            abeg = angle_list[m]
            aend = abeg + 20
            if (data[1][k] >= abeg) and (data[1][k] < aend):
                line = create_data_line(data, clen, k)
                save[m].append(line)
                break
#
#--- create/update the data file for each angle interval
#
    for k in range(0, alen):
        outname = data_dir + 'solar_panel_angle_' + str(angle_list[k])
#
#--- print the data
#
        if len(save[k]) == 0:
            continue

        line = ''
        for ent in save[k]:
            line = line + ent + '\n'


        if os.path.isfile(outname):
            with open(outname, 'a') as fo:
                fo.write(line)
#
#--- if this is the first time, add the header
#
        else:
            aline = "#" + header + '\n'
            aline = aline + '#' + '-'*120 + '\n'
            aline = aline + line

            with open(outname, 'w') as fo:
                fo.write(line)

#---------------------------------------------------------------------------------------
#-- create_data_line: create output data line                                         --
#---------------------------------------------------------------------------------------

def create_data_line(data, clen, k):
    """
    create output data line
    input:  data    --- data matrix of clen x len(data[0])
    output: line    --- a line of data of clen elements
    """

    line = str(data[0][k])
    for m in range(1, clen):
        line = line + '\t' + str(data[m][k])

    return line

#---------------------------------------------------------------------------------------

if __name__ == '__main__':

    run_data_sepration()
