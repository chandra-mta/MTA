#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       update_html_page.py: update disk space html page                        #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Mar 04, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time
import random
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
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------------
#-- update_html_page: update html page                                                        --
#-----------------------------------------------------------------------------------------------

def update_html_page():
    """
    update html page
    input none, but read <house_keeping>/disk_space_backup_py.html as a template
    output: <web_dir>/disk_space.html
    """
#
#--- today's date
#
    update  = 'Last Update: ' + mcf.today_date_display()
#
#--- read the current disk capacities
#
    cap1    = get_disk_capacity('/data/mta/')
    cap2    = get_disk_capacity('/data/mta_www/')
    cap3    = get_disk_capacity('/data/mta4/')
    cap4    = get_disk_capacity('/data/mays/')
    cap5    = get_disk_capacity('/data/swolk/')
    cap6    = get_disk_capacity('/data/mta1/')
    cap7    = get_disk_capacity('/data/mta2/')
    cap8    = get_disk_capacity('/proj/rac/ops/')
#
#--- read template
#
    line = house_keeping + 'disk_space_backup_py.html'
    with open(line, 'r') as f:
        data = f.read()
#
#---  update the blank lines
#
    data   = data.replace("#UPDATE#", update)
    data   = data.replace('#CAP1#',   cap1)
    data   = data.replace('#CAP2#',   cap2)
    data   = data.replace('#CAP3#',   cap3)
    data   = data.replace('#CAP4#',   cap4)
    data   = data.replace('#CAP5#',   cap5)
    data   = data.replace('#CAP6#',   cap6)
    data   = data.replace('#CAP7#',   cap7)
    data   = data.replace('#CAP8#',   cap8)
#
#--- print out the data
#
    out = web_dir + 'disk_space.html'
    with open(out, 'w') as fo:
        fo.write(data)

#-----------------------------------------------------------------------------------------------
#-- get_disk_capacity: read a disk capacity                                                   --
#-----------------------------------------------------------------------------------------------

def get_disk_capacity(dname):
    """
    read a disk capacity
    input:  dname       --- disk name
    output: capacity    --- capacity
    """
    cmd = 'df -k ' + dname + '>' + zspace
    os.system(cmd)

    data     = mcf.read_data_file(zspace, remove=1)
    atemp    = re.split('\s+',  data[1])
    capacity = atemp[1]

    return capacity

#--------------------------------------------------------------------

if __name__ == '__main__':

    update_html_page()

