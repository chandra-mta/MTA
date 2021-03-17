#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       update_solor_wind_data.py: copy kp data and create a file to match in the required format   #
#                                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                                   #
#               last updae: Aug 07, 2018                                                            #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import math
import numpy
import time
import pyfits
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time

path = '/data/mta/Script/Ephem/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()
for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)


#---------------------------------------------------------------------------------------
#-- get_kp: copy kp data and create a file to match in the required format            --
#---------------------------------------------------------------------------------------

def get_kp():
    """
    copy kp data and create a file to match in the required format
    input: none but read from: /data/mta4/proj/rac/ops/KP/k_index_data
    output: <data_dir>/solar_wind_data.txt
    """
#
#--- find out the last update time
#
    datafile = data_dir + '/solar_wind_data.txt'
    odata    = read_data_file(datafile)
    at       = re.split('\s+', odata[-1])
    otime    = at[0] + ':' + at[1] + ':' + at[2] + ':' + at[3][0]  + at[3][1] + ':' + at[3][2] + at[3][3] + ':00'
    otime    = datetime.strptime(otime, "%Y:%m:%d:%H:%M:%S").strftime("%Y:%j:%H:%M:%S")
    otime    =  Chandra.Time.DateTime(otime).secs
#
#--- read kp data file
#
    ifile = '/data/mta4/proj/rac/ops/KP/k_index_data'
    f     = open(ifile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()
#
#--- find the part which are not in the data
#
    line  = ''
    for ent in data:
        atemp = re.split('\s+', ent)
        ltime = float(atemp[0])
        if ltime < otime:
            continue

        kval  = atemp[1]
    
        ltime = Chandra.Time.DateTime(ltime).date
        mc    = re.search('\.', ltime)
        if mc is not None:
            btemp = re.split('\.', ltime)
            ltime = btemp[0]
    
        ldate = datetime.strptime(ltime, '%Y:%j:%H:%M:%S').strftime("%Y %m %d %H%M")
    
        line  = line  + ldate + '\t\t' + ldate + '\t\t' + kval + '\t\t\t' + ldate + '\t\t' + kval + '\t\t' + kval + '\n'
#
#--- if there is  new data, update
#
    if line != '':
        fo  = open(datafile, 'a')
        fo.write(line)
        fo.close()


#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def read_data_file(ifile):

    f    = open(ifile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()


    return data




#---------------------------------------------------------------------------------------

if __name__ == '__main__':

    get_kp()

