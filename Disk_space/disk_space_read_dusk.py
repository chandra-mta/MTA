#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       disk_space_read_dusk.py: check /data/mta space and subdirectories       #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: May 13, 2019                                               #
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

#-----------------------------------------------------------------------------------
#-- disk_space_read_dusk: read dusk result, update data file, and plot the data  ---
#-----------------------------------------------------------------------------------

def disk_space_read_dusk():
    """
    control scripts to: read dusk result, update data file, and plot the data
    input: none but read files named dusk_<disk name>
    output: udated <data_out>/disk_data_<disk name>
                   <plot_dir>/<disk_name>_disk.png
    """
    diskName = '/data/mta/'
    nameList = ['Script','DataSeeker','Test','GIT']
    duskName = 'dusk_mta'
    pastData = data_out + 'disk_data_mta'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/data/mta4/'
    nameList = ['CUS','www','Deriv']
    duskName = 'dusk_mta4'
    pastData = data_out + 'disk_data_mta4'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/data/mays/'
    nameList = ['MTA']
    duskName = 'dusk_mays'
    pastData = data_out + 'disk_data_mays'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/data/mta_www/'
    nameList = ['ap_report', 'mp_reports','mta_max_exp']
    duskName = 'dusk_www'
    pastData = data_out + 'disk_data_www'
    plot_dusk_result(diskName, duskName, nameList, pastData)

    diskName = '/proj/rac/ops/'
    nameList = ['CRM2', 'CRM', 'ephem', 'CRM3']
    duskName = 'proj_ops'
    pastData = data_out + 'disk_proj_ops'
    plot_dusk_result(diskName, duskName, nameList, pastData)

#-----------------------------------------------------------------------------------
#-- plot_dusk_result: read dusk result, update data file, and plot the data       --
#-----------------------------------------------------------------------------------

def plot_dusk_result(diskName, duskName, nameList, pastData):
    """
    read dusk result, update data file, and plot the data
    input:  diskName    --- name of the disk
            duskName    --- a file name in which dusk result is written
            nameList    --- subdirectory names
            pastData    --- data file name
    output: udated <data_out>/disk_data_<disk name>
                   <plot_dir>/<disk_name>_disk.png
    """
#
#--- find the disk capacity of the given disk
#
    disk_capacity = diskCapacity(diskName)
#
#--- read the output from dusk
#
    line = run_dir + duskName
    data = mcf.read_data_file(line)

    capacity = {}               #---- make a dictionary
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        try:
            val = 100.0 * float(atemp[0]) /disk_capacity
            val =  round(val, 2)
            atemp[1] = atemp[1].replace('./', '')
            capacity[atemp[1]] = val 
        except:
            pass
#
#--- today's date
#
    out   = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    stime = Chandra.Time.DateTime(out).secs
    ftime = mcf.chandratime_to_fraq_year(stime)
#
#--- append the new data to the data table
#
    sline = '%3.3f' % ftime
    for dName in nameList:
        sline = sline + ':' + str(capacity[dName]) 
    sline = sline + '\n'

    with open(pastData, 'a') as fo:
        fo.write(sline)
#
#---- start plotting history data
#
    xxx = 999
    if xxx == 999:
    #try:
        plot_history_trend(diskName, duskName, nameList, pastData)
    #except:
    #    pass

#-----------------------------------------------------------------------------------
#-- plot_history_trend: plot history trend                                        --
#-----------------------------------------------------------------------------------

def plot_history_trend(diskName, duskName, nameList, pastData):
    """
    plot history trend
    input:  diskName    --- name of the disk
            duskName    --- a file name in which dusk result is written
            nameList    --- subdirectory names
            pastData    --- data file name
    output: <plot_dir>/<disk_name>_disk.png
    """
#
#--- read past data
#
    data = mcf.read_data_file(pastData)

    colNum = len(nameList)

    stime = []
    yval  = [[] for x in range(0, colNum)]
    
    prev = 0
    for ent in data:
        atemp = re.split(':', ent)
        stime.append(float(atemp[0]))

        for i in range(0, colNum):
            try:
               val  = float(atemp[i+1]) 
               prev = val
            except:
                val = prev

            if val > 100:
                if prev < 100:
                    val = prev
                else:
                    val = 0.0

            yval[i].append(val)

    xSets = [stime]
    xmin  = int(min(stime))
    xmax  = max(stime)
    ixmax = int(xmax)
    xmax = ixmax + 1

    xname = 'Time (Year)'
    yname = 'Disk Capacity Used (%)'

    for k in range(0, colNum):
        ent   = nameList[k]

        ymin  = min(yval[k])
        ymax  = max(yval[k])
        ydiff = ymax - ymin
        if ydiff == 0:
            ymin = 0
            if ymax < 1:
                ymax == 5

        ymin  = 0
        ymaxt = int(ymax + 0.1 * ydiff) 
        if ymax > 100:
            ymax = 100

        if ymaxt < ymax:
            ymax += 2
            ymax = int(ymax)
        else:
            ymax = ymaxt

        ySets     = [yval[k]]
        entLabels = [ent]

        outname = fig_out +  ent.lower() + '_disk.png'
        pf.plotPanel(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outname)

#-----------------------------------------------------------------------------------
#-- diskCapacity: find a disk capacity                                           ---
#-----------------------------------------------------------------------------------

def diskCapacity(diskName):
    """
    find a disk capacity
    input:  diskName        --- name of the disk
    output: disk_capacity   --- disk capacity
    """
    cmd = 'df -k ' + diskName + '> ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    disk_capacity = 'na'

    for ent in data:
        try:
            atemp  = re.split('\s+', ent)
            val = float(atemp[1])
            for test in atemp:
                m = re.search('%', test)
                if m is not None:
                    disk_capacity = val
                    break
        except:
            pass

    return disk_capacity

#--------------------------------------------------------------------

disk_space_read_dusk()
