#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           update_grating_focus_data_lists.py: update grating zero order data files            #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Jul 18, 2018                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import random
import numpy
import time
import Chandra.Time

#--- reading directory list
#
path = '/data/mta/Script/Grating/Grating_DB/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import convertTimeFormat    as tcnv
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail   = int(time.time())
zspace  = '/tmp/zspace' + str(rtail)

obslist = gdata_dir + 'obslist'

name_list =  ['abs_start_time', 'detector', 'grating', 'zo_loc_x', 'zo_loc_y', 'zo_chip_x', 'zo_chip_y', 'heg_all_angle', 'meg_all_angle', 'leg_all_angle']

#----------------------------------------------------------------------------------------------
#-- update_grating_db: update gratdata.db                                                    --
#----------------------------------------------------------------------------------------------

def update_grating_db():
    """
    update gratdata.db
    input:  none, but read from <gdata_dir>/*/*/*summ*.txt
    output: <gdata_dir>/gratdata.db
    """

    cmd = 'ls ' + gdata_dir + '*/*/*summ*.txt > ' + zspace
    os.system(cmd)
    data = read_data_file(zspace, remove=1)

    outfile = gdata_dir + 'gratdata.db'

    cmd     = 'mv ' + outfile + ' ' +outfile + '~'
    try:
        os.system(cmd)
    except:
        pass

    d_dict = {}
    t_list = []
    for ifile in data:
        [stime, line] = extract_data(ifile)
        d_dict[stime] = line
        t_list.append(stime)

    t_list.sort()

    fo   = open(outfile, 'w')
    line = '#obsid'
    for ent in name_list:
        line = line + '|' + ent
    line = line + '\n'
    fo.write(line)
    for stime in t_list:
        fo.write(d_dict[stime])
        fo.write('\n')
    fo.close()

#---------------------------------------------------------------------------------------------
#-- extract_data: extract needed data from a given file                                     --
#---------------------------------------------------------------------------------------------

def extract_data(ifile):
    """
    extract needed data from a given file
    input:  ifile   --- a file name
    output: stime   --- time stamp
            line    --- a string of data (in order of name_list)
    """
#
#--- find obsid from the file name path
#
    atemp = re.split('\/', ifile)
    obsid = atemp[-2].strip()

    nlen = len(name_list)
#
#--- read the file
#
    data = read_data_file(ifile)
    save = []
#
#--- check each data name in name_list to find their value
#
    for k in range(0, nlen):
        save.append('')
    for ent in data:
        
        for k in range(0, nlen):
            name = name_list[k]
            mc = re.search(name, ent)
            if mc is not None:
#
#--- if it is not read already, find the value from the line
#
                if save[k] == '':
                    val = get_value(ent)
                    save[k] = val
                    break
#
#--- create data line
#
    line = obsid 
    for k in range(0, nlen):
        line = line + '|' + save[k]

    stime = float(save[0])

    return [stime, line]

#---------------------------------------------------------------------------------------------
#-- get_value: get the value part from the line                                              --
#---------------------------------------------------------------------------------------------

def get_value(line):
    """
    get the value part from the line
    input:  line    --- data line
    output: val     --- value
    Note: we assume that the line is like:
             S               grating : "LETG"
        or
             N        abs_start_time :  52965340. +/- 0.0000000 second
    """

    atemp = re.split(':', line)
#
#--- numeric case
#
    if line[0] == 'N':
        btemp = re.split('\+\/\-', atemp[1])
        val   = btemp[0].strip()
        if val == '':
            val = '-999'
#
#--- string case
#
    else:
        val  = atemp[1]
        val  = val.replace('"', '')
        val  = val.strip()

    return val

#---------------------------------------------------------------------------------------------
#-- read_data_file: read data file                                                          --
#---------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):
    """
    read data file
    input:  ifile   --- file name
            remove  --- indicator which tells whether you want to remove the file after reading
                        if remove: 0, no, otherwise yes
    output: data    --- a list of the data
    """

    f    = open(ifile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if remove > 0:
        mcf.rm_file(ifile)

    return data

#---------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_grating_db()
