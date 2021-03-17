#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#  check_prev_getnrt_process.py: kill getnrt process if the previous one is still running   #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Mar 04, 2021                                                       #
#                                                                                           #
#############################################################################################

import sys
import os
import string
import re
import time
import random

#
#--- reading directory list
#
path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folders
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------
#-- check_prev_getnrt_process: kill getnrt process if the previous one is still running
#----------------------------------------------------------------------------

def check_prev_getnrt_process():
    """
    kill getnrt process if the previous one is still running
    input:  none
    output: none
    """

    cmd = 'ps aux | grep mta | grep python | grep getnrt_control > ' + zspace
    os.system(cmd)

    pid_list = []
    out = mcf.read_data_file(zspace, remove=1)
    if len(out)> 1:
        for ent in out:
            mc = re.search('zspace', ent)
            if mc is not None:
                continue 

            atemp = re.split('\s+', ent)
            cmd   = 'kill -9 ' + atemp[1]
            os.system(cmd)


#----------------------------------------------------------------------------

if __name__ == "__main__":

    check_prev_getnrt_process()
