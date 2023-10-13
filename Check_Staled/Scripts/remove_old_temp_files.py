#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#       remove_old_temp_files.py: remove old temp file from /tmp directory                  #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Mar 15, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import calendar
import time
import random
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- remove_old_temp_files: remove old temp file from /tmp directory                     --
#-----------------------------------------------------------------------------------------

def remove_old_temp_files():
    """
    remove old temp file from /tmp directory
    input:  none but find from /tmp/ directory
    output: none but cleaned   /tmp/ directory
    """

    now = calendar.timegm(time.gmtime())

    cmd = 'ls /tmp/sort*  /tmp/zspace* > ' + zspace
    os.system(cmd)
    
    with open(zspace, 'r') as f:
        data = [line.strip() for line in f.readlines()]

    cmd = 'rm -rf ' + zspace
    os.system(cmd)

    for ent in data:
        try:
            out  = os.path.getmtime(ent)
            diff = now - out
            if diff > 1800:                    #--- 30 mins
                cmd = 'chmod 777 ' + str(ent)
                os.system(cmd)

                cmd = 'rm -rf ' + str(ent)
                os.system(cmd)
        except:
            pass

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    remove_old_temp_files()

