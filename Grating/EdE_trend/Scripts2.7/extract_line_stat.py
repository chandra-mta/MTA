#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       extract_line_stat.py: extract line statistics                                       #
#                                                                                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Jul 18, 2018                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import math
import numpy
import time
import Chandra.Time
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/Grating/EdE_trend/Scripts/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import readSQL              as tdsql
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

m_list   = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
m_start1 = [0, 31, 59, 90, 120, 151, 181, 212, 243, 373, 304, 334]
m_start2 = [0, 31, 60, 91, 121, 152, 182, 213, 244, 374, 305, 335]
#
#--- lines to extract
#
h_lines = [824, 1022, 1472]             #---- hetg
m_lines = [654, 824, 1022, 1472]        #---- metg
l_lines = [654, 824, 1022]              #---- letg

#---------------------------------------------------------------------------------------------------
#-- get_lines: extract line statistics for a given grating                                        --
#---------------------------------------------------------------------------------------------------

def get_lines(grating):
    """
    extract line statistics for a given grating
    input:  grating --- hetg, metg, or letg
    output: acis_<grating>_<line>_data
    """
#
#--- read data file ehader
#
    infile = house_keeping + 'data_header'
    f      = open(infile, 'r')
    header = f.read()
    f.close()
#
#--- set which grating data to extract
#
    if grating == 'hetg':
        cmd    = 'ls ' + gdata_dir + '/*/*/obsid_*_L1.5_S1HEGp1_linelist.txt >' + zspace
        ofile  = 'acis_hetg_'
        l_list = h_lines
    elif grating == 'metg':
        cmd    = 'ls ' + gdata_dir + '/*/*/obsid_*_L1.5_S1MEGp1_linelist.txt >' + zspace
        ofile  = 'acis_metg_'
        l_list = m_lines
    else:
        cmd    = 'ls ' + gdata_dir + '/*/*/obsid_*_L1.5_S1LEGp1_linelist.txt >' + zspace
        ofile  = 'hrc_letg_'
        l_list = l_lines

    os.system(cmd)
    d_list = read_data_file(zspace, remove=1)

    sdate_list = [[], [], [], [], [], [], []]
    line_list  = [{}, {}, {}, {}, {}, {}, {}]
    lcnt       = len(l_list)

#
#---- go though each files
#
    for dfile in d_list:

        out = find_info(dfile)
        if out == 'na':
            continue
        else:
            [obsid, ltime, stime] = out
#
#--- extract line information. if energy or fwhm are either "*" or "NaN", skip
#
        data = read_data_file(dfile)
        for ent in data:
            atemp = re.split('\s+', ent.strip())
            if mcf.chkNumeric(atemp[0]):
                energy = atemp[2]
                fwhm   = atemp[3]

                if energy == 'NaN':
                    continue

                if (fwhm == '*') or (fwhm == 'NaN'):
                    continue
                energy = adjust_digit(energy, 6)
                peak   = float(energy)
                err    = atemp[4]
                ede    = atemp[5]
                line = str(obsid) + '\t' + energy + '\t' + fwhm + '\t' + err + '\t' + ede + '\t'
                line = line + str(ltime) + '\t' + str(int(stime)) + '\n'
#
#--- find the line value within +/-5 of the expected line center position
#
                for k in range(0, lcnt):
                    center = l_list[k]
                    low    = (center - 5) / 1000.0
                    top    = (center + 5) / 1000.0
                    if (peak >= low) and (peak <= top):

                        sdate_list[k].append(stime)
                        line_list[k][stime] = line
#
#--- output file name
#
    for k in range(0, lcnt):
        val   = str(l_list[k])
        if len(val) < 4:
            val = '0' + val

        odata =  data_dir + ofile + val + '_data'
        fo = open(odata, 'w')
        fo.write(header)
        fo.write('\n')
#
#--- print out the data
#
        slist  = sdate_list[k]
        slist.sort()
        for sdate in slist:
            ent = line_list[k][sdate]
            fo.write(ent)
        fo.close()
        
#---------------------------------------------------------------------------------------------------
#-- read_data_file: read data file                                                                --
#---------------------------------------------------------------------------------------------------

def read_data_file(infile, remove=0):
    """
    read data file
    input:  infile  --- input file name
            remove  --- if not 0, remove the infile after reading it
    output: data    --- data list
    """

    f     = open(infile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if remove == 1:
        mcf.rm_file(infile)

    return data

#---------------------------------------------------------------------------------------------------
#-- adjust_digit: add '0' to the end to fill the length after a dicimal point                     --
#---------------------------------------------------------------------------------------------------

def adjust_digit(val, digit):
    """
    add '0' to the end to fill the length after a dicimal point
    input:  val     --- value
            digit   --- the number of decimal position
    output: val     --- adjust value (str)
    """
    val   = str(val)
    atemp = re.split('\.', val)

    vlen  = len(atemp[1])
    diff  = digit - vlen
    if diff > 0:
        for k in range(0, diff):
            atemp[1] = atemp[1] + '0'

    val   = atemp[0] + '.' + atemp[1]

    return val

#---------------------------------------------------------------------------------------------------
#-- find_info: find obsid and a observation time                                                  --
#---------------------------------------------------------------------------------------------------

def find_info(dfile):
    """
    find obsid and a observation time
    input:  dfile   --- original data file name
    output: obisd   --- obsid
            ltime   --- time in the format of <yyyy>:<ddd>:<hh>:<mm>:<ss
            stime   --- tine in second from 1998.1.1
    """
#
#--- find obsid
#
    atemp = re.split('obsid_', dfile)
    btemp = re.split('_', atemp[1])
    obsid = btemp[0]

    monitor = []
    groupid = []
#
#--- get information about obsid
#
    try:
        sqlinfo = tdsql.get_target_info(obsid, monitor, groupid)
    except:
        return 'na'
#
#--- 11th data is the date of the observation
#
    sdate   = sqlinfo[11]
#
#--- convert the time into <yyyy>:<ddd>:<hh>:<mm>:<ss>
#
    ltime = convert_date_format(sdate)
#
#--- convert time into seconds from 1998.1.1
#
    stime = date = Chandra.Time.DateTime(ltime).secs


    return [obsid, ltime, stime]


#---------------------------------------------------------------------------------------------------
#-- convert_date_format: from <Mmm> <dd> <yyy> <hh>:<mm><AM/PM> to <yyyy>:<ddd>:<hh>:<mm>:<ss>    --
#---------------------------------------------------------------------------------------------------

def convert_date_format(sdate):
    """
    convert time format from <Mmm> <dd> <yyy> <hh>:<mm><AM/PM> to <yyyy>:<ddd>:<hh>:<mm>:<ss>
    input   sdate   --- date in <Mmm> <dd> <yyy> <hh>:<mm><AM/PM>
    output  ltime   --- date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    """
    atemp   = re.split('\s+', str(sdate))
    mon     = atemp[0]
    for k in range(0, 12):
        if mon.upper() == m_list[k]:
            mpos = k
            break

    date    = int(float(atemp[1]))
    year    = int(float(atemp[2]))
    if tcnv.isLeapYear(year) == 1:

        m_start = m_start2
    else:
        m_start = m_start1

    yday = m_start[mpos] + date
    syday = str(yday)
    if yday < 10:
        syday = '00' + syday
    elif yday < 100:
        syday = '0'  + syday

    tpart = atemp[3]
    mc    = re.search('AM', tpart)
    if mc is not None:
        add = 0
    else:
        add = 12

    tpart = tpart[:-2]
    btemp = re.split(':', tpart)
    hh    = int(float(btemp[0])) + add
    shh   = str(hh)
    if hh < 10:
        shh = '0' + shh


    ltime = str(year) + ':' + str(syday) + ':' + str(shh) + ':' + str(btemp[1]) + ':00'

    return ltime


#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------


    def test_find_info(self):
        dfile = 'obsid_21053_L1.5_S1HEGp1_linelist.txt'
        out   = find_info(dfile)
        self.assertEquals(out[0], '21053')
        self.assertEquals(out[1], '2018:092:03:37:00')
        self.assertEquals(out[2], 639027489.184)

    def test_adjust_digit(self):
        val  = 1.233
        digit= 6
        aval = adjust_digit(val, digit)
        self.assertEquals(aval, '1.233000')

    def test_convert_date_format(self):
        itime = 'Dec  1 2014  3:52AM'
        out   = convert_date_format(itime)
        self.assertEquals(out, '2014:335:03:52:00')

        itime = 'Sep  4 2002  3:07PM'
        out   = convert_date_format(itime)
        self.assertEquals(out, '2002:247:15:07:00')

#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        grating = sys.argv[1].strip()
        if grating == 'all':
            for grating in ('hetg', 'metg', 'letg'):
                get_lines(grating)
        else:
            get_lines(grating)

    else:
        unittest.main()


