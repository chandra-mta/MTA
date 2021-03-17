#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       disk_space_run_dusk.py:   run dusk in each directory to get disk size   #
#                                 information.                                  #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Mar 04, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re

#
#--- reading directory list
#
path = '/data/mta/Script/Disk_check/house_keeping/dir_list_py'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def disk_space_run_dusk():
#
#--- /data/mta/
#
    cmd = 'cd /data/mta;  /usr/local/bin/dusk > ' + run_dir + '/dusk_mta'
    os.system(cmd)
#
#--- /data/mta4/
#
    cmd = 'cd /data/mta4;  /usr/local/bin/dusk > ' + run_dir + '/dusk_mta4'
    os.system(cmd)
#
#--- /data/mays/
#
    cmd = 'cd /data/mays; nice -n15  /usr/local/bin/dusk > ' + run_dir + '/dusk_mays'
    os.system(cmd)
#
#--- /data/mta_www/
#
    cmd = 'cd /data/mta_www; nice -n15  /usr/local/bin/dusk > ' + run_dir + '/dusk_www'
    os.system(cmd)
#
#--- /proj/rac/ops/
#
    cmd = 'cd /proj/rac/ops/; nice -n15  /usr/local/bin/dusk > ' + run_dir + '/proj_ops'
    os.system(cmd)
#
#--- /data/swolk/MAYS/      --- retired
#
#    cmd = 'cd /data/swolk/MAYS/; dusk > ' + run_dir + '/dusk_check3'
#    os.system(cmd)
#
#--- /data/swolk/AARON/    --- retired
#
#    cmd = 'cd /data/swolk/AARON/; dusk > ' + run_dir + '/dusk_check4'
#    os.system(cmd)

#--------------------------------------------------------------------

if __name__ == '__main__':

    disk_space_run_dusk()
