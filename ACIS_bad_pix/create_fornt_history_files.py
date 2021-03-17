#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#############################################################################################
#                                                                                           #
#       create_fornt_history_files.py: create combined front side ccds history files        #
#                                                                                           #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                           #
#                   last update: Mar 25, 2019                                               #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'
with  open(path, 'r') as f:
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
import mta_common_functions as mcf

#--------------------------------------------------------------------------------------------
#-- create_fornt_history_files: create combined front side ccds history files             ---
#--------------------------------------------------------------------------------------------

def create_fornt_history_files():
    """
    create combined front side ccds history files
    input:  none but read from indivisual ccd history files
    output: front_side_<part><ccd#>
    """
    adict = {}
    tdict = {}
    date  = []
    for part in ('ccd', 'col', 'hccd'):
        for ccd in (0, 1, 2, 3, 4, 6, 8, 9):
            ifile = data_dir + part + str(ccd) + '_cnt'
            data  = mcf.read_data_file(ifile)
#
#--- row: (time in sec)<>(yyyy):(ddd)<>(quad0)<>(quad1)<>(quad2)<>(quad3)
#
            for ent in data:
                atemp = re.split('<>', ent)
                atime = int(atemp[0])
#
#--- if there is already data in the dict, make the sum of each quad
#
                try:
                    alist = adict[atime]
                    for k in range(0, 4):
                        alist[k] += int(atemp[k+2])
                    adict[atime]  = alist
#
#--- if this is the first time, create a dict entry
#
                except:
                    date.append(atime)
                    tdict[atime] = atemp[1]
                    dlist        = [int(atemp[2]), int(atemp[3]), int(atemp[4]), int(atemp[5])]
                    adict[atime] = dlist
#
#--- make sure the date is unique in the list and sorted
#
        date = list(set(date))
        date = sorted(date)
#
#--- print out the data
#
        line = ''
        for ent in date:
            line = line + str(ent) + '<>'    + tdict[ent] + '<>' 
            line = line + str(adict[ent][0]) + '<>' + str(adict[ent][1]) + '<>' 
            line = line + str(adict[ent][2]) + '<>' + str(adict[ent][3]) + '\n'
    
        name = data_dir + 'front_side_' + part + '_cnt'
        with open(name, 'w') as fo:
            fo.write(line)

#----------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_fornt_history_files()


