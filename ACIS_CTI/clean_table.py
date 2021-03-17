#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       clean_table.py: sort and cleaned data tables in <data_dir>/Results      #
#                                                                               #
#           author: t. isobe(tisobe@cfa.harvard.edu)                            #
#                                                                               #
#           Last Update:    Mar 02, 2021                                        #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator
import time
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf   #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------
#-- clean_table: sort and clean the table data in <data_dir>/Results      --
#---------------------------------------------------------------------------

def clean_table():
    """
    sort and clean the table data in <data_dir>/Results
    Input:  none but read from <data_dir>/Results/<elm>_ccd<ccd#>
    Output: cleaned up <data_dir>/Results/<elm>_ccd<ccd#>
    """
#
#--- make a backup
#
    out  = time.strftime('%m%d%y', time.gmtime())
    cout = data_dir + '/Results/Save_' + out

    cmd  = 'rm -rf ' + cout
    os.system(cmd)
    cmd  = 'mkdir -p '  + cout
    os.system(cmd)
    cmd  = 'cp -f  ' + data_dir + '/Results/*_ccd* ' + cout + '/.'
    os.system(cmd)
#
#--- now clean up the data
#
    cmd = 'ls ' + data_dir + '/Results/*_ccd* > ' + zspace
    os.system(cmd)

    flist = mcf.read_data_file(zspace, remove=1)

    for ifile in flist:
        data = mcf.read_data_file(ifile)
        data.sort()
        
        prev    = data[0]
        cleaned = [prev]

        for ent in data:
            if ent == prev:
                prev = ent
            else:
                cleaned.append(ent)
                prev = ent

        with  open(ifile, 'w') as fo:
            for ent in cleaned:
                line = ent + '\n'
                fo.write(line)

#--------------------------------------------------------------------

if __name__ == '__main__':

    clean_table()

