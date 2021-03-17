#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       check_disk_space.py:   check /data/mta* space and send out email        #
#                              if it is beyond a limit                          #
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
import random
import numpy as np
import time
import Chandra.Time
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
import plot_function        as pf
import mta_common_functions as mcf
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set y plotting range
#
ymin = 30
ymax = 100

#-----------------------------------------------------------------------------------------------
#--- check_disk_space: extract disk usegae data-------------------------------------------------
#-----------------------------------------------------------------------------------------------

def check_disk_space():
    """
    this function extracts disk usage data
    Input: none
    Output udated usage table
    """
    line = ''
    chk  = 0;
#
#--- /data/mta/
#
    dName = '/data/mta'
    per0 = find_disk_size(dName)
    if per0 > 91:
        chk += 1
        line = dName + ' is at ' + str(per0) + '% capacity\n'
#
#--- /data/mta1/
#
    dName = '/data/mta1'
    per1 = find_disk_size(dName)
    if per1 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per1) + '% capacity\n'
#
#--- /data/mta2/
#
    dName = '/data/mta2'
    per2 = find_disk_size(dName)
    if per2 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per2) + '% capacity\n'
#
#--- /data/mta4/
#
    dName = '/data/mta4'
    per4 = find_disk_size(dName)
    if per4 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per4) + '% capacity\n'
#
#--- /data/swolk/
#
    dName = '/data/swolk'
    per5 = find_disk_size(dName)
    if per5 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per5) + '% capacity\n'
#
#--- /data/mays/
#
    dName = '/data/mays'
    per6 = find_disk_size(dName)
    if per6 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per6) + '% capacity\n'
#
#--- /data/mta_www/
#
    dName = '/data/mta_www'
    per7 = find_disk_size(dName)
    if per7 > 95:
        chk += 1
        line = line + dName + ' is at ' + str(per7) + '% capacity\n'
#
#--- /proj/rac/             --- we don't check this anymore
#
    per8 = 0
#
#--- if any of the disk capacities are over 95%, send out a warning email
#
    if chk > 0:
        send_mail(line)
#
#--- update data table
#
    per3 = 0;
    per8 = 0;
    update_datatable(per0, per1, per2, per3, per4, per5, per6, per7, per8)
#
#--- plot data
#
    historyPlots()

#-----------------------------------------------------------------------------------------------
#--- find_disk_size: finds a usage of the given disk                                         ---
#-----------------------------------------------------------------------------------------------

def find_disk_size(dName):
    """
    this function finds a usage of the given disk
    Input:   dName --- the name of the disk
    Output:  percent -- the percentage of the disk usage
    """
    cmd  = 'df -k ' + dName + ' > '  + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=-1)

    percent = 0
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        try:
            float(atemp[1])
            for test in atemp:
                m = re.search('%', test)
                if m is not None:
                    btemp = re.split('\%', test)
                    percent = btemp[0]                      #---- disk capacity in percent (%)
        except:
            pass

    return int(round(float(percent)))

#-----------------------------------------------------------------------------------------------
#--- send_mail: sending a warning emil----------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def send_mail(line):
    """
    this function sends out a warning email
    Input: line (containing a waring)
    Output: email 
    """
    with open(zspace, 'w') as f:
        f.write('-----------------------\n')
        f.write('  Disk Space Warning:  \n')
        f.write('-----------------------\n\n')
        f.write(line)

    cmd = 'cat ' + zspace + ' |mailx -s\"Subject: Disk Space Warning\n\" '
    cmd = cmd    + 'isobe\@head.cfa.harvard.edu'
    os.system(cmd)

    cmd = 'rm -rf ' + zspace
    os.system(cmd)

#-----------------------------------------------------------------------------------------------
#--- update_datatable: appends newest data to disk space data table                          ---
#-----------------------------------------------------------------------------------------------

def update_datatable(per0, per1, per2, per3, per4, per5, per6, per7, per8):
    """
    this function appends the newest data to the disk space data table
    Input: per0 ... per5: new measures for each disk. currently per3 is empty
    Output: <data_out>/disk_space_data (updated)
    """
#
#--- find out today's date in Local time frame
#
    out   = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    stime = Chandra.Time.DateTime(out).secs
    ftime = mcf.chandratime_to_fraq_year(stime)
    ftime = '%3.3f' % ftime
#
#--- today's data
#
    line  = str(ftime) + '\t' + str(per0) + '\t' + str(per1) + '\t' + str(per2)  + '\t'
    line  = line       +  str(per4) + '\t' + str(per5) + '\t' + str(per6) + '\t' 
    line  = line       + str(per7)  + '\t' + str(per8) + '\n'
#
#--- append to the data table
#
    ifile = data_out + 'disk_space_data'
    with open(ifile, 'a') as f:
        f.write(line)

#-----------------------------------------------------------------------------------------------
#---historyPlots: plots historical trend of disk usages                                      ---
#-----------------------------------------------------------------------------------------------

def historyPlots():
    """
    this function plots histrical trends of disk usages
    Input: no, but read from <data_out>/disk_space_data
    Output: disk_space1.png / disk_space2.png
    """
#
#--- read data
#
    ifile = data_out + 'disk_space_data'
    data  = mcf.read_data_file(ifile)

    time   = []
    space0 = []         #--- /data/mta/
    space1 = []         #--- /data/mta1/
    space2 = []         #--- /data/mta2/
    space4 = []         #--- /data/mta4/
    space5 = []         #--- /data/swolk/
    space6 = []         #--- /data/mays/
    space7 = []         #--- /data/mta_www/
    space8 = []         #--- /proj/rac/ops/

    ochk   = 0
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        val = float(atemp[0])
        if val > ochk:
            ochk = val
            time.append(val)
            space0.append(float(atemp[1]))
            space1.append(float(atemp[2]))
            space2.append(float(atemp[3]))
            space4.append(float(atemp[4]))
            space5.append(float(atemp[5]))
            space6.append(float(atemp[6]))
            space7.append(float(atemp[7]))
            space8.append(float(atemp[8]))
        else:
            continue
#
#---  x axis plotting range
# 
    xmin  = min(time)
    xmax  = max(time)

    xdiff = xmax - xmin
    xmin  = int(xmin - 0.1 * xdiff)
    xmin  = 2004                        #---- the earliest data starts year 2004
    xmax  = int(xmax + 0.1 * xdiff)
#
#--- plot first three
#
    xSets = []
    ySets = []
    for i in range(0, 3):
        xSets.append(time)

    ySets.append(space0)
    ySets.append(space7)
    ySets.append(space4)
    xname = 'Time (Year)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/data/mta/', '/data/mta_www/', '/data/mta4/']

    outfile = fig_out + 'disk_space1.png'
    pf.plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outfile)
#
#--- plot the rest
#
    xSets = []
    ySets = []
    for i in range(0, 2):
        xSets.append(time)

    ySets.append(space6)
    ySets.append(space5)
    xname = 'Time (Year)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/data/mays/', '/data/swolk/']

    outfile = fig_out + 'disk_space2.png'
    pf.plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outfile)

    xSets = []
    ySets = []
    for i in range(0, 2):
        xSets.append(time)

    ySets.append(space1)
    ySets.append(space2)
    xname = 'Time (Year)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/data/mta1/', '/data/mta2/']

    outfile = fig_out + 'disk_space3.png'
    pf.plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outfile)

    xSets = []
    ySets = []
    for i in range(0, 2):
        xSets.append(time)

    ySets.append(space8)
    xname = 'Time (Year)'
    yname = 'Capacity Filled (%)'
    entLabels = ['/proj/rac/ops/']

    outfile = fig_out + 'disk_space4.png'
    pf.plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outfile)

#--------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#
if __name__ == '__main__':

    check_disk_space()
