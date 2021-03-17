#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################
#                                                                       #
#       extract_line_stat.py: extract line statistics                   #
#                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                   #
#                                                                       #
#           last update: Aug 28, 2019                                   #
#                                                                       #
#########################################################################

import os
import sys
import re
import string
import math
import numpy
import time
import Chandra.Time
import unittest
import random
#
#--- reading directory list
#
path = '/data/mta/Script/Grating/EdE_trend/Scripts/house_keeping/dir_list_py'

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
sys.path.append(sybase_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions   as mcf
import set_sybase_env_and_run as sser
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
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
#--- read data file header
#
    infile = house_keeping + 'data_header'
    with open(infile, 'r') as f:
        header = f.read()
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
    d_list = mcf.read_data_file(zspace, remove=1)

    sdate_list = [[], [], [], [], [], [], []]
    line_list  = [{}, {}, {}, {}, {}, {}, {}]
    lcnt       = len(l_list)
#
#---- go though each files
#
    for dfile in d_list:

        out = find_obs_date(dfile)
        if out == 'na':
            continue
        else:
            [obsid, ltime, stime] = out
#
#--- extract line information. if energy or fwhm are either "*" or "NaN", skip
#
        data = mcf.read_data_file(dfile)
        for ent in data:
            atemp = re.split('\s+', ent.strip())
            if mcf.is_neumeric(atemp[0]):
                energy = atemp[2]
                fwhm   = atemp[3]

                if energy == 'NaN':
                    continue

                if (fwhm == '*') or (fwhm == 'NaN'):
                    continue
                energy = mcf.add_tailing_zero(energy, 6)
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
#
#--- print out the data
#
        slist = sdate_list[k]
        slist.sort()

        line  = header + '\n'
        for sdate in slist:
            line = line +  line_list[k][sdate]

        val   = str(l_list[k])
        if len(val) < 4:
            val = '0' + val

        odata =  data_dir + ofile + val + '_data'
        with open(odata, 'w') as fo:
            fo.write(line)
        
#---------------------------------------------------------------------------------------------------
#-- find_obs_date: find obsid and a observation time                                                  --
#---------------------------------------------------------------------------------------------------

def find_obs_date(dfile):
    """
    find obsid and a observation time
    input:  dfile   --- original data file name
    output: obisd   --- obsid
            ltime   --- time in the format of <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stime   --- tine in second from 1998.1.1
    """
#
#--- find obsid
#
    atemp = re.split('obsid_', dfile)
    btemp = re.split('_', atemp[1])
    obsid = btemp[0]
#
#--- get observation data from sybase
#
    try:
        cmd   = 'select soe_st_sched_date,lts_lt_plan from target where obsid=' + obsid
        out   = sser.set_sybase_env_and_run(cmd)
        sdate = out[0][0]
        ldate = out[0][1]
#
#--- get lts time first
#
        ltime = time.strftime('%Y:%j:%H:%M:%S', time.strptime(ldate, '%Y-%m-%dT%H:%M:%S'))
#
#--- check soe scheduled date is available
#
        try:
            sdate = sdate.strip()
            ltime = convert_date_format(sdate)
        except:
            pass
    except:
        return 'na'
#
#--- convert time into seconds from 1998.1.1
#
    stime = Chandra.Time.DateTime(ltime).secs

    return [obsid, ltime, stime]

#---------------------------------------------------------------------------------------------------
#-- convert_date_format: from <Mmm> <dd> <yyy> <hh>:<mm><AM/PM> to <yyyy>:<ddd>:<hh>:<mm>:<ss>    --
#---------------------------------------------------------------------------------------------------

def convert_date_format(sdate):
    """
    convert time format from <Mmm> <dd> <yyyy> <hh>:<mm><AM/PM> to <yyyy>:<ddd>:<hh>:<mm>:<ss>
    input   sdate   --- date in <Mmm> <dd> <yyy> <hh>:<mm><AM/PM>
    output  ltime   --- date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    """
    atemp   = re.split('\s+', sdate)
    mon     = mcf.change_month_format(atemp[0])
    mon     = mcf.add_leading_zero(mon)
    day     = atemp[1]
    day     = mcf.add_leading_zero(day)
    year    = atemp[2]

    tpart   = atemp[3]
    mc    = re.search('AM', tpart)
    if mc is not None:
        add = 0
        spl = 'AM'
    else:
        add = 12
        spl = 'PM'
    btemp   = re.split(spl, tpart)
    ctemp   = re.split(':', btemp[0])
    hr      = str(int(ctemp[0]) + add)
    mm      = ctemp[1]

    ltime = year + ':' + mon + ':' + day + ':' + hr + ':' + mm + ':00'
    ltime = time.strftime("%Y:%j:%H:%M:%S", time.strptime(ltime, '%Y:%m:%d:%H:%M:%S'))

    return ltime

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_find_obs_date(self):
        dfile = 'obsid_21746_L1.5_S1HEGp1_linelist.txt'
        out   = find_obs_date(dfile)

    def test_mcfadd_tailing_zero(self):
        val  = 1.233
        digit= 6
        aval = mcf.add_tailing_zero(val, digit)
        self.assertEqual(aval, '1.233000')

    def test_convert_date_format(self):
        itime = 'Dec  1 2014  3:52AM'
        out   = convert_date_format(itime)
        self.assertEqual(out, '2014:335:03:52:00')

        itime = 'Sep  4 2002  3:07PM'
        out   = convert_date_format(itime)
        self.assertEqual(out, '2002:247:15:07:00')

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
