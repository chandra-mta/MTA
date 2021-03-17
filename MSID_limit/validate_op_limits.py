#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#   validate_op_limits.py: compare the current op_limits.db to the standard     #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 10, 2021                                       #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time
import random
import math
import numpy

#
#--- reading directory list
#
path = '/data/mta/Script/MSID_limit/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)

import mta_common_functions as mcf 

rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------
#-- validate_op_limits: compare the current op_limits.db to the standard and report problems
#-------------------------------------------------------------------------------

def validate_op_limits():
    """
    compare the current op_limits.db to the standard and report problems
    input:  none, but read from <past_dir>/op_limits.db_080119 and ./op_limits.db
    output: op_limit_problems if there are any potential problems
    """
#
#--- remove the past checking result
#
    mcf.rm_files('op_limit_problems')
#
#--- this is the most recent clean data set; use as a starndard
#
    ifile  = main_dir + 'Past_data/op_limits.db_080119'
    p_dict =  read_op_limit(ifile)
#
#--- the current op_limits.db file
#
    ifile  = main_dir + 'op_limits.db'
    c_dict =  read_op_limit(ifile)
#
#--- start checking 
#
    wline  = ''
    for msid in p_dict.keys():
#
#--- check whether msid is missing in the new op_limits.db
#
        pdata = p_dict[msid]
        try:
            cdata = c_dict[msid]
        except:
            wline = wline + msid + ': Entry is missing in the new op_limit.db\n'
            continue
#
#--- check all past time entries are still in the current op_limts.db
#
        ptime = pdata[0]
        ctime = cdata[0]
        dtime = numpy.setdiff1d(ptime, ctime)
        if len(dtime) > 0:
            tline = ''
            for ent in dtime:
                tline =  tline + '\t' + str(ent)
            wline = wline + msid + ': Missing entry at time ' + tline + '\n'
            continue 
#
#--- check whether the current op_limits.db entry is in time order
#
        chk = 0
        for k in range(1, len(ctime)):
            if ctime[k] > ctime[k-1]:
                continue
            else:
                wline = wline + msid + ': Time is out of order at ' + str(ctime[k]) + '\n'
                chk = 1
                break
        if chk > 0:
            continue
#
#--- check whether the values are same between the standard and the new op_limits.db (in the standard potion)
#
        chk = 0
        for k in range(0, len(ptime)): 
            if (ptime[k] != ctime[k]) \
                or (p_dict[msid][1][k] != c_dict[msid][1][k]) \
                or (p_dict[msid][2][k] != c_dict[msid][2][k]) \
                or (p_dict[msid][3][k] != c_dict[msid][3][k]) \
                or (p_dict[msid][4][k] != c_dict[msid][4][k]): 

                wline = wline + msid + ': Time and/or Entry values are different at time ' + str(ctime[k]) + '\n'
                chk = 1
                break
        if chk > 0:
            continue

    if wline != '':
        with open('op_limit_problems', 'w') as fo:
            fo.write(wline)

#-------------------------------------------------------------------------------
#-- read_op_limit: create a data dictionary for msid <--> data                --
#-------------------------------------------------------------------------------

def read_op_limit(ifile):
    """
    create a data dictionary for msid <--> data
    input:  ifile   --- input file name
    output: m_dict  --- dictionary: 
            msid <--> [time_list, y_low_list, y_upper_list, r_low_list, r_upper_list]
    """
    data  = mcf.read_data_file(ifile)
    m_dict = {}
    prev   = ''
    for ent in data:
#
#--- skip none data part
#
        if ent == '':
            continue
        if ent[0] == '#':
            continue
#
#--- first 6 entries are used
#
        atemp = re.split('\s+', ent)
        msid  = atemp[0].strip()
        a1 = float(atemp[1])
        a2 = float(atemp[2])
        a3 = float(atemp[3])
        a4 = float(atemp[4])
        t  = float(atemp[5])
#
#--- first time we are getting data
#
        if prev == '':
            alist       = [[t], [a1], [a2], [a3], [a4]]
            m_dict[msid] = alist 
            prev        = msid
        else:
#
#--- the previous msid is same as this one, append the data to the lists of the list
#
            if msid == prev:
                alist = m_dict[msid]
                alist[0].append(t)
                alist[1].append(a1)
                alist[2].append(a2)
                alist[3].append(a3)
                alist[4].append(a4)
                m_dict[msid]  = alist
#
#--- for the case thatthis is the first time entry for the msid
#
            else:
                alist       = [[t], [a1], [a2], [a3], [a4]]
                m_dict[msid] = alist 
                prev        = msid

    return m_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    validate_op_limits()
