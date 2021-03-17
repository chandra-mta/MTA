#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           update_grating_zero_order_data_lists.py: update grating zero order data files       #
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
path = '/data/mta/Script/Grating/Zero/Scripts/house_keeping/dir_list'

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
obslist = gdata_dir + '/obslist'

#----------------------------------------------------------------------------------------------
#-- update_grating_zero_order_data_lists: extract grating zero order information and update data file 
#----------------------------------------------------------------------------------------------

def update_grating_zero_order_data_lists():
    """
    extract grating zero order information and update data file
    input:  none but read from <obslist>
    output: <data_dir>/letg, <data_dir>/metg, <data_dir>/hetg
    """
#
#--- read all grating data list
#
    a_list = read_data_file(obslist)
#
#--- read already processed data list
#
    ifile  = house_keeping + 'past_data'
    if os.path.isfile(ifile):
        o_list = read_data_file(ifile)
    else:
        o_list = []

    n_list = list(set(a_list) - set(o_list))

    if len(n_list) > 0:
        cmd = 'cp ' + obslist + ' ' + house_keeping + 'past_data'
        os.system(cmd)
#
#--- read each data file and extract needed information
#
        acis_h = []
        acis_l = []
        hrc_l  = []
        for path in n_list:
            out = extract_needed_data(path)
            if out == False:
                continue
            [inst, grating, tstart, l_x, l_y, c_x, c_y] =  out
            if inst == 'acis_s':
                if grating == 'LETG':
                    if tstart == '' or l_x == '' or l_y == '':
                        continue

                    line = tstart + '\t' + l_x + '\t' + l_y + '\t' + c_x + '\t' + c_y
                    acis_l.append(line)
    
                else:
                    if tstart == '' or l_x == '' or l_y == '':
                        continue

                    line = tstart + '\t' + l_x + '\t' + l_y + '\t' + c_x + '\t' + c_y
                    acis_h.append(line)

            else:
                if tstart == '' or l_x == '' or l_y == '':
                    continue

                line = tstart + '\t' + l_x + '\t' + l_y + '\t' + c_x + '\t' + c_y
                hrc_l.append(line)


#
#--- update the data file
#
        print_data('acis_hetg', acis_h)
        print_data('acis_letg', acis_l)
        print_data('hrc_letg',  hrc_l)

#---------------------------------------------------------------------------------------------
#-- extract_needed_data: extract needed information from the file                           --
#---------------------------------------------------------------------------------------------

def extract_needed_data(path):
    """
    extract needed information from the file
    input:  path    --- the path to the data file.
                        we assume that the file name is obsid_<obsid>_Sky_summary.txt
    output: gating  ---  grating
            tstart  --- starting time in seconds from 1998.1.1
            l_x     --- zero position in sky x
            l_y     --- zero position in sky y
            c_x     --- zero position in chip x
            c_y     --- zero position in chip y
    """

    atemp = re.split('\/', path)
    obsid = atemp[-1]
    ifile = path + '/obsid_' + obsid + '_Sky_summary.txt'

    if not os.path.isfile(ifile):
        return False

    data    = read_data_file(ifile)

    inst    = ''
    grating = ''
    tstart  = ''
    l_x     = ''
    l_y     = ''
    c_x     = ''
    x_y     = ''
    chk     = 0
    for ent in data:
#
#--- find which instrument is used
#
        if chk == 0:
            mc  = re.search('ACIS-S', ent)
            if mc  is not None:
                inst = 'acis_s'
                chk  = 1
            mc1 = re.search('HRC-S',  ent)
            if mc1 is not None:
                inst = 'hrc_s'
                chk  = 1

#
#--- find which grating system is used
#
        mc2 = re.search('grating',  ent)
        if mc2 is not None:
            grating = get_value(ent)
            continue
#
#---- find the observation time
#
        mc3 = re.search('abs_start_time', ent)
        if mc3 is not None:
            tstart  = str(int(float(get_value(ent))))
            continue
#
#--- find zero position
#
        mc4 = re.search('zo_loc_x', ent)
        if mc4 is not None:
            l_x = get_value(ent)
            continue

        mc5 = re.search('zo_loc_y', ent)
        if mc5 is not None:
            l_y = get_value(ent)
            continue

        mc6 = re.search('zo_chip_x', ent)
        if mc6 is not None:
            c_x = get_value(ent)


        mc7 = re.search('zo_chip_y', ent)
        if mc7 is not None:
            c_y = get_value(ent)

    if (grating == '') or (tstart == ''):
        return False
    else:
        return [inst, grating, tstart, l_x, l_y, c_x, c_y]

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
#
#--- string case
#
    else:
        val   = atemp[1]
        val   = val.replace('"', '')
        val   = val.strip()

    return val

#---------------------------------------------------------------------------------------------
#-- print_data: print out the data                                                          --
#---------------------------------------------------------------------------------------------

def print_data(oname, data):
    """
    print out the data
    input:  oname   --- output file name (going to web_dir)
            data    --- a list of data
    output: updated <web_dir>/oname
    """
    
    if len(data) > 0:
        ofile = data_dir + oname 
        fo    = open(ofile, 'a')
        for ent in data:
            fo.write(ent)
            fo.write('\n')
    
        fo.close()

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

    update_grating_zero_order_data_lists()
