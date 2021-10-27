#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#           remove_old_backups.py: remove old backups                                               #
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    Oct 27, 2021                                                            #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf    #---- contains other functions commonly used in MTA scripts

#------------------------------------------------------------------------------------------
#-- remove_old_backups: remove old backups                                               --
#------------------------------------------------------------------------------------------

def remove_old_backups():
    """
    remove old backups
    input:  none
    output: none
    """
    out = time.strftime('%m:%d', time.gmtime())
    atemp = re.split(':', out)
    month = int(atemp[0])
    day   = int(atemp[1])

    if day < 4:
        month2 = month -2
        if month2 < 1:
            if month2 == 0:
                month2 = 12
            else:
                month2 = 11

        month2 = mcf.add_leading_zero(month2, 2)

        cmd    = 'rm -rf /data/mta/Script/ACIS/CTI/Data/Results/Save_' + month2 + '*'
        os.system(cmd)

#------------------------------------------------------------------------------------------

if __name__ == "__main__":

    remove_old_backups()



