#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#           extract_sim_data.py: extract sim data from PRIMARYCCDM_*.*.tl                   #
#                                                                                           #
#               author: t. isobe    (tisobe@cfa.harvard.edu)                                #
#                  based on scripts written by b. spitzbart (bspitzbart@cfa.harvard.edu)    #
#                                                                                           #
#               last update: Feb 165 2021                                                   #
#                                                                                           #
#############################################################################################

import sys
import os
import string
import re
import math
import random
import time
import Chandra.Time
 
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
import mta_common_functions     as mcf
#
#--- temp writing file name
#
rtail   = int(time.time() * random.random())
zspace  = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------------------
#-- extract_sim_data: extract sim data from PRIMARYCCDM_*.*.tl                                  ---
#--------------------------------------------------------------------------------------------------

def extract_sim_data():
    """
    extract sim data from PRIMARYCCDM_*.*.tl
    input: none but read from <dump_dir>/PRIMARYCCDM_*.*.tl
    output: <data_dir>sim_data.out
    """
#
#--- find the time of the last entry from the sim_data.out
#
    sfile = data_dir + 'sim_data.out'
    data  = mcf.read_data_file(sfile)
#
#--- cleaning up the data; drop the data which the date starts from ":" e.g. :2014
#
    pdata = []
    for ent in data:
        if re.search('^:', ent):
            continue
        else:
            pdata.append(ent)
#
#--- the last entiry values
#
    if len(pdata) > 0:
        atemp  = re.split('\s+', pdata[-1])
        ltime  = int(float(Chandra.Time.DateTime(atemp[0]).secs))
        time_2 = atemp[0]
        col1_2 = atemp[1]
        col2_2 = atemp[2]
        col3_2 = atemp[3]
    else:
        ltime  = 0
        time_2 = 0
        col1_2 = ''
        col2_2 = ''
        col3_2 = ''
#
#--- check whether input files exists 
#
    cmd = 'ls -rt ' + dump_dir + 'PRIMARYCCDM_*.*.tl >' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    dlen = len(data)
    if dlen < 1:
        exit(1)

#
#--- files exist. read the data from the last 40 files
#
    if dlen > 40:
        tlist = data[-40:]
    else:
        tlist = data

    for ent in tlist:
        cmd = 'cat ' + ent + ' >> ' + zspace
        os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)
#
#--- go though each data line
#
    prev  = ''
    sline = ''
    for ent in data:
#
#--- expect the first letter of the data line is numeric (e.g. 2014).
#
        try:
            val = float(ent[0])         
        except:
            continue
#
#--- only data with "FMT" format will be used
#
        mc    = re.search('FMT', ent)
        if mc is None:
            continue
#
#--- if there are less than 20 entries, something wrong; skip it
#
        atemp = re.split('\t+', ent)
        if len(atemp) < 20:             
            continue
#
#--- convert time format
#
        ttime  = atemp[0]
        ttime  = ttime.strip();
        ttime  = ttime.replace(' ',   ':')
        ttime  = ttime.replace(':::', ':00')
        ttime  = ttime.replace('::',  ':0')
#
#--- if the time is exactly same as one before, skip it
#
        if ttime == time_2:
            continue
#
#--- if the time is already in the database, skip it
#
        stime = int(float(Chandra.Time.DateTime(ttime).secs))
        if stime <= ltime:
            continue
#
#--- use only data which tscpos and fapos have numeric values
#
        tscpos = atemp[4].strip()
        fapos  = atemp[5].strip()

        if tscpos == "" or fapos == "":
            continue
        else:
            if (mcf.is_neumeric(tscpos)) and (mcf.is_neumeric(fapos)):
                tscpos = str(int(float(tscpos)))
                fapos  = str(int(float(fapos)))
            else:
                continue

        mpwm = atemp[12].strip()
        if mcf.is_neumeric(mpwm):
            mpwm = int(float(mpwm))
            mpwm = str(mpwm)
        else:
            mpwm = '0'
#
#--- we want to print only beginning and ending of the same data entries.
#--- skip the line if all three entiries are same as one before, except the last one
#
        if (col1_2 == tscpos) and (col2_2 == fapos) and (col3_2 == mpwm):
            time_2 = ttime
            continue

        line = ttime + '\t' + str(tscpos) + '\t' + str(fapos) + '\t' + str(mpwm) + '\n'
        if line == prev:
            continue
        else:
            pline  = time_2  + '\t' + str(col1_2) + '\t' + str(col2_2) + '\t' + str(col3_2) + '\n'
            sline  = sline + pline + line

            prev   = line
            time_2 = ttime
            col1_2 = tscpos
            col2_2 = fapos
            col3_2 = mpwm


    with open('./temp_save', 'w') as fo:
        fo.write(sline)

    sfile2 = sfile + '~'
    cmd    = 'cp  ' + sfile + ' ' + sfile2
    os.system(cmd)
    cmd    = 'cat ./temp_save >> ' + sfile
    os.system(cmd)

    mcf.rm_file('./temp_save')

#------------------------------------------------------------------------------------

if __name__ == "__main__":

    extract_sim_data()
