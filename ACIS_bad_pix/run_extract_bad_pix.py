#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#       run_extract_bad_pix.py: running extract_bad_pix.py script to extrat bad pixel data          #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update Mar 02, 2021                                                                #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import time
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

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
import mta_common_functions    as mcf        #---- contains other functions commonly used in MTA scripts
import extract_bad_pix         as ebp
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------
#-- find_data_collection_interval: find data collection period in dom                ---
#---------------------------------------------------------------------------------------

def find_data_collection_interval():
    """
    find data collection period in dom
    input:  none but read from <data_dir>/Dis_dir/hist_ccd3
    output: ldom    --- starting dom
            tdom    --- stopping dom (today)
    """
#
#--- find today's  date
#
    tout  = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    tdate = int(float(Chandra.Time.DateTime(tdate).secs))
#
#--- find the date of the last entry
#
    ifile = data_dir + 'hist_ccd3'
    data  = mcf.read_data_file(ifile)
    data.reverse()

    for ent in data:
        atemp = re.split('<>', ent)
        try:
            ldate = int(float(atemp[0]))
            break
        except:
            continue
#
#--- the data colleciton starts from the next day of the last entry date
#
    ldate += 86400

    return [ldate, tdate]

#---------------------------------------------------------------------------------------
#-- mv_old_file: move supplemental data file older than 30 day to a reserve           --
#---------------------------------------------------------------------------------------

def mv_old_file(tdate):
    """
    move supplemental data file older than 30 day to a reserve
    input:  tdate   --- the current time in seconds from 1998.1.1
    output: none but older files are moved
    """
    tdate -= 30 * 86400

    cmd = 'ls ' + house_keeping + '/Defect/CCD*/* > ' + zspace
    os.system(cmd)
    ldata = mcf.read_data_file(zspace, remove=1)

    for ent in ldata:
        atemp = re.split('\/acis', ent)
        btemp = re.split('_', atemp[1])

        if int(btemp[0]) < tdate:
            out = ent
            out = out.replace('Defect', 'Defect/Save')
            cmd = 'mv ' + ent + ' ' + out 
            os.system(cmd)

#--------------------------------------------------------------------

if __name__ == '__main__':
#    
#--- run the control function; first find out data colleciton interval
#
    if len(sys.argv) == 3:
        start = sys.argv[1]
        start.strip()
        start = int(start)
        stop  = sys.argv[2]
        stop.strip()
        stop  = int(stop)
    else:
        (start, stop) = find_data_collection_interval()

    ebp.find_bad_pix_main(start, stop)
    mv_old_file(start)



