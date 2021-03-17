#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           update_grating_angle_data_lists.py: update grating angle data files                 #
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
path = '/data/mta/Script/Grating/Angles/Scripts/house_keeping/dir_list'

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

#----------------------------------------------------------------------------------------------
#-- update_grating_angle_data_lists: extract grating angle information and update data file  --
#----------------------------------------------------------------------------------------------

def update_grating_angle_data_lists():
    """
    extract grating angle information and update data file
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
        l_list = []
        m_list = []
        h_list = []
        for path in n_list:
            out = extract_needed_data(path)
            if out == False:
                continue
            [grating, tstart, leg, meg, heg] =  out

            if grating == 'LETG':
                if tstart == '' or leg == '':
                    continue

                line = tstart + '\t' + leg
                l_list.append(line)

            else:
                if tstart == '' or meg == '':
                    continue

                line = tstart + '\t' + meg
                m_list.append(line)

                if tstart == '' or heg == '':
                    continue

                line = tstart + '\t' + heg
                h_list.append(line)
#
#--- update the data file
#
        print_data('letg', l_list)
        print_data('metg', m_list)
        print_data('hetg', h_list)

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
            leg     --- letg angle
            meg     --- metg angle
            heg     --- hetg angle
            Note, leg has a value only when grating is LETG, and meg and heg have value when HETG
    """

    atemp = re.split('\/', path)
    obsid = atemp[-1]
    ifile = path + '/obsid_' + obsid + '_Sky_summary.txt'

    if not os.path.isfile(ifile):
        return False

    data    = read_data_file(ifile)

    grating = ''
    tstart  = ''
    leg     = ''
    meg     = ''
    heg     = ''
    chk     = 0
    for ent in data:
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
#--- find all_angle
#
            mc4 = re.search('leg_all_angle', ent)
            if mc4 is not None:
                leg = get_value(ent)
                continue

            mc5 = re.search('meg_all_angle', ent)
            if mc5 is not None:
                meg = get_value(ent)
                continue

            mc6 = re.search('heg_all_angle', ent)
            if mc6 is not None:
                heg = get_value(ent)

    if (grating == '') or (tstart == ''):
        return faluse
    else:
        return [grating, tstart, leg, meg, heg]

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

    update_grating_angle_data_lists()
