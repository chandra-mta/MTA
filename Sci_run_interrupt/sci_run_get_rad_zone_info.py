#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       sci_run_get_rad_zone_info.py: find expected radiation zone timing               #
#                                                                                       #
#           this script must be run on rhodes to see the radiation zone information     #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 09, 2021                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import time
import Chandra.Time
import numpy
#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
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
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------------
#--- get_radzone_info: update rad_zone_info                                              ----
#--------------------------------------------------------------------------------------------

def get_radzone_info():
    """
    update rad_zone_info (a list of radiation zone entry/exit). 
    it will check this month and the next month. 
    """
#
#--- find out today's date
#
    today = time.strftime('%Y:%m', time.gmtime())
    atemp = re.split(':', today)
    year  = int(float(atemp[0]))
    month = int(float(atemp[1]))
#
#--- read the past radiation zone information
#
    ifile = data_dir + 'rad_zone_info'
    rdata = mcf.read_data_file(ifile)
#
#--- extract new radiation zone information of "ENTRY" and "EXIT"
#
    entry_list = extract_radzone_info(year, month, 'RADENTRY')
    exit_list  = extract_radzone_info(year, month, 'RADEXIT')
#
#--- combined all three lists
#
    clist      = rdata + entry_list + exit_list
#
#--- to sort the list, first separate each entry to three elements
#
    [cdat1, cdat2, cdat3] = mcf.separate_data_to_arrays(clist, '\t\t')
#
#--- the second elemet (cdat2) is chandra time; use that to sort the list in time order
#
    cdat1 = numpy.array(cdat1)
    cdat2 = numpy.array(cdat2)
    cdat3 = numpy.array(cdat3)
    idx   = numpy.argsort(cdat2)
    ent1  = cdat1[idx]
    ent2  = cdat2[idx]
    ent3  = cdat3[idx]
#
#--- recombine three element into one and make a time ordered list
#
    l_line = ''
    ind    = ''
    s_line = ''
    for i in range(0,len(ent1)):
#
#--- check ENTRY/EXIT is in order
#
        if ent1[i] != ind:
            line = str(ent1[i]) + '\t\t' + str(ent2[i]) + '\t\t' + str(ent3[i]) + '\n'
#
#--- remove duplicated lines
#
            if line != l_line:
                s_line = s_line + line
                l_line = line
                ind    = ent1[i]
#
#--- move the old file
#
    ofile   = data_dir + 'rad_zone_info'
    cmd     = 'mv -f ' +  ofile + ' ' + ofile + '~'
    os.system(cmd)
#
#--- print out the data
#
    with open(ofile, 'w') as fo:
        fo.write(s_line)


#--------------------------------------------------------------------------------------------
#--- extract_radzone_info: extract radiation zone information from MP data                ---
#--------------------------------------------------------------------------------------------

def extract_radzone_info(year, month, etype):
    """
    extract radiation zone information from MP data. 
    input:  year    --- year
            month   --- month
            etype   --- RADENTRY / RADEXIT
    output: olist   --- a list of data <otpye> <ctime> <dtime>

    """
#
#--- find the next month
#
    year2  = year
    month2 = month + 1

    if month2 == 13:
        year2 += 1
        month2 = 1
#
#--- extract this month and the next month radiation zone information
#
    lmon = mcf.change_month_format(month).upper()
    cmd  = 'cat ' +  '/data/mpcrit1/mplogs/'+ str(year)  + '/' +  lmon + '*/ofls/*dot'
    cmd  = cmd    + '|grep ' + etype + ' > ' + zspace
    os.system(cmd)

    lmon = mcf.change_month_format(month2).upper()
    cmd  = 'cat ' +  '/data/mpcrit1/mplogs/'+ str(year2) + '/' +  lmon + '*/ofls/*dot'
    cmd  = cmd    + '|grep ' + etype + ' >> ' + zspace
    os.system(cmd)
#
#--- read the tmp files and clean up the the radiation zone entry / exit information
#
    data = mcf.read_data_file(zspace, remove=1)

    olist = []
    for ent in data:
        line = clean_entry(ent)
        olist.append(line)

    return olist

#--------------------------------------------------------------------------------------------
#--- clean_entry: Clean up Radiation zone Entry/Exist information                          --
#--------------------------------------------------------------------------------------------

def clean_entry(line):
    """
    clean up Radiation zone Entry/Exist information suitable for use.  See extract_radzone_info
    input:  line    --- data line
    output: line    --- cleaned up data line
    """
    temp1 = re.split('\s+', str(line))
    temp2 = re.split('=',   temp1[0])
    ctime = int(Chandra.Time.DateTime(temp2[1]).secs)

    m = re.search('RADENTRY', line)
    if m is not None: 
        act = 'ENTRY'
    else:
        act = 'EXIT'

    line = act + '\t\t' + str(ctime) + '\t\t' + str(temp2[1]) 

    return line

#------------------------------------------------------------------------------------------

if __name__ == '__main__':

    get_radzone_info()





