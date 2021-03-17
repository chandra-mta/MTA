#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       sci_run_compute_gap.py: compute science time lost                               #
#                               (interuption total - radiation zone)                    #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 09, 2021                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import re
import string
import time
import Chandra.Time
#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
import mta_common_functions as mcf
#
#--- temp writing file name
#
import random 
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------------------------
#--- sci_run_compute_gap: for given data, recompute the science run lost time excluding rad zones ---
#----------------------------------------------------------------------------------------------------

def sci_run_compute_gap(ifile):
    """
    for a given file name which contains a list, recompute the lost science time 
                (excluding radiation zone) 
    input:  file    --- the file containing information, e.g.:
        20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto" 
    output: file    --- updated file
    """
#
#--- if file is not given (if it is NA), ask the file input
#
    test = exc_dir + ifile
    if not os.path.isfile(test):
        ifile = raw_input('Please put the intrrupt timing list: ')

    data = mcf.read_data_file(ifile)
#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add the rad zone list
#--- to each date
#

    update = ''
    for ent in data:
        if not ent:                         #--- if it is a blank line end the operation
            break

        etemp = re.split('\s+', ent)
        atemp = re.split(':', etemp[1])
        year  = atemp[0]
        month = atemp[1]
        date  = atemp[2]
        hour  = atemp[3]
        mins  = atemp[4]
#
#--- convert time to chandra Time
#
        ltime = time.strftime("%Y:%j:%H:%M:00", time.strptime(etemp[1], '%Y:%m:%j:%H:%M'))
        csec  = Chandra.Time.DateTime(ltime).secs
#
#--- end date
#
        ltime = time.strftime("%Y:%j:%H:%M:00", time.strptime(etemp[2], '%Y:%m:%j:%H:%M'))
        csec2 =  Chandra.Time.DateTime(ltime).secs
#
#--- date stamp for the list
#
        list_date = str(year) + str(month) + str(date)
#
#--- read radiation zone information from "rad_zone_list" and add up the time overlap with 
#--- radiatio zones with the interruption time period
#
        rfile = data_dir + '/rad_zone_list'
        rlist = mcf.read_data_file(rfile)

        dsum = 0
        for record in rlist:
            atemp = re.split('\s+', record)
            if list_date == atemp[0]:
                btemp = re.split(':', atemp[1])
                for period in btemp:

                    t1 = re.split('\(', period)
                    t2 = re.split('\)', t1[1])
                    t3 = re.split('\,', t2[0])
                    pstart = float(t3[0])
                    pend   = float(t3[1])

                    if pstart >= csec and  pstart < csec2:
                        if pend <= csec2:
                            diff = pend - pstart
                            dsum += diff
                        else:
                            diff = csec2 - pstart
                            dsum += diff
                    elif pstart < csec2 and pend > csec:
                        if pend <= csec2:
                            diff = pend - csec
                            dsum += diff
                        else:
                            diff = csec2 - csec
                            dsum += diff

                break
#
#--- total science time lost excluding radiation zone passes
#
        dsum *= 86400                           #--- change unit from day to sec
        sciLost = (csec2 - csec - dsum) / 1000.

        line = etemp[0] + '\t' + etemp[1]    + '\t' + etemp[2] + '\t' 
        line = line     + "%.1f" %  sciLost  + '\t' + etemp[4]

        update = update + line + '\n'


    with open(ifile, 'w') as fo:
        fo.write(update)

    return update


#--------------------------------------------------------------------

if __name__ == '__main__':


    if len(sys.argv) == 2:
        input_file = sys.argv[1]
    else:
        input_file = 'interruption_time_list'

    out = sci_run_compute_gap(input_file)

    print(out)
