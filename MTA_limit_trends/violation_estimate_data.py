#!/proj/sot/ska3/flight/bin/python

#####################################################################################################
#                                                                                                   #
#       violation_estimate_data.py: save violation estimated times in sqlite database v_table       #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Feb 01, 2021                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
import unittest
import time
from time import gmtime, strftime, localtime
#
#--- reading directory list
#
#path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
path = '/data/mta4/testTrend/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append("/data/mta4/Script/Python3.10/MTA")
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
#
#--- set location of the database
#
v_table = house_keeping + '/v_table.sqlite3'
db      = sqlite3.connect(v_table)

#-----------------------------------------------------------------------------------
#-- read_v_estimate: read data for a given msid                                  ---
#-----------------------------------------------------------------------------------

def read_v_estimate(msid, dtype='long', mtype='mid', state='none'):
    """
    read data for a given msid
    input:  msid    --- msid
            dtype   --- data type week, short, year, five long
            mtype   --- mid, min, max
            state   --- state
    output: (yl_time, yt_time, rl_time, rt_time)
    """
    cursor  = db.cursor()

    cmd = 'SELECT * FROM v_table WHERE '
    cmd = cmd + " msid='"      + msid.lower()  + "'"
    cmd = cmd + " and dtype='" + dtype.lower() + "'"
    cmd = cmd + " and mtype='" + mtype.lower() + "'"
    cmd = cmd + " and state='" + state.lower() + "'"
    cursor.execute(cmd)
    vout = cursor.fetchall()

    if len(vout) == 0:
        return []
    else:
        out = list(vout[0])
        out = out[4:]

        return out 

#-----------------------------------------------------------------------------------
#-- read_v_estimate_full: read out all set of data for msid                       --
#-----------------------------------------------------------------------------------

def read_v_estimate_full(msid):
    """
    read out all set of data for msid
    input: msid --- msid
    output: full entry output -- [(<msid>, <dtye>, <mtype>, <state>, <yl>, <yu>, <rl>, <rp>),..]
    """
    cursor  = db.cursor()

    cmd = 'SELECT * FROM v_table WHERE '
    cmd = cmd + " msid='"      + msid.lower()  + "'"
    cursor.execute(cmd)
    vout = cursor.fetchall()

    return vout


#-----------------------------------------------------------------------------------
#-- create_table: create table                                                    --
#-----------------------------------------------------------------------------------

def create_table():
    """
    create table
    input:  none
    output: sql database: v_table
    """
    cursor  = db.cursor()
    cursor.execute('''CREATE TABLE v_table (msid, dtype, mtype, state, \
                                            yl_time, yt_time, rl_time, rt_time)''')    

#-----------------------------------------------------------------------------------
#-- incert_data: incert a new data set                                           ---
#-----------------------------------------------------------------------------------

def incert_data(msid, dtype, mtype, state, data):
    """
    incert a new data set
    input:  msid    --- msid
            dtype   --- data type week, short, year, five long
            mtype   --- mid, min, max
            state   --- state of the data
            data    --- a list of:
                yl_time --- yellow low violation time
                yt_time --- yellow top violation time
                rl_time --- red low violation time
                rt_time --- red top violation time
    ouput:  updated sql database
    """
    cmd = 'INSERT INTO v_table VALUES ("' 
    cmd = cmd + msid  + '", "' 
    cmd = cmd + dtype + '", "'
    cmd = cmd + mtype + '", "' 
    cmd = cmd + state + '",'
    cmd = cmd + str(data[0]) + ', '
    cmd = cmd + str(data[1]) + ', '
    cmd = cmd + str(data[2]) + ', '
    cmd = cmd + str(data[3]) + ') '
#
#--- check whether the entry is already in the database
#--- if so, just update. otherwise, create a new entry
#
    try:
        out = read_v_estimate(msid, dtype, mtype, state)
        if out ==  []:
            cursor  = db.cursor()
            cursor.execute(cmd)
            db.commit()
        else:
            update_data(msid, dtype, mtype, state, data)
    except:
        cursor  = db.cursor()
        cursor.execute(cmd)
        db.commit()

#-----------------------------------------------------------------------------------
#-- update_data: update an existing data set                                     ---
#-----------------------------------------------------------------------------------

def update_data(msid, dtype, mtype, state, data):
    """
    update an existing data set
    input:  msid    --- msid
            dtype   --- data type week, short, year, five long
            mtype   --- mid, min, max
            state   --- state
            data    --- a list of:
                yl_time --- yellow low violation time
                yt_time --- yellow top violation time
                rl_time --- red low violation time
                rt_time --- red top violation time
    output: updated sql database
    """
    cmd = 'UPDATE v_table SET  '
    cmd = cmd + ' yl_time='     + str(data[0]) + ', '
    cmd = cmd + ' yt_time='     + str(data[1]) + ', '
    cmd = cmd + ' rl_time='     + str(data[2]) + ', '
    cmd = cmd + ' rt_time='     + str(data[3])
    cmd = cmd + ' WHERE msid="' + msid  + '"'
    cmd = cmd + ' and  dtype="' + dtype + '"'
    cmd = cmd + ' and  mtype="' + mtype + '"'
    cmd = cmd + ' and  state="' + state + '"'

    cursor  = db.cursor()
    cursor.execute(cmd)
    db.commit()

#-----------------------------------------------------------------------------------
#-- delete_entry: delete entry with msid                                         ---
#-----------------------------------------------------------------------------------

def delete_entry(msid, state):
    """
    delete entry with msid
    input:  msid    --- msid
    output: updated database
    """
    cmd = 'DELETE FROM v_table  '
    cmd = cmd + 'WHERE  msid="' + msid  + '"'
    cmd = cmd + ' and  state="' + state + '"'

    cursor  = db.cursor()
    cursor.execute(cmd)
    db.commit()

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

#class TestFunctions(unittest.TestCase):
#    """
#    testing functions
#    """
#    msid  = '1cbat_test'
#    dtype = 'long'
#    msid = '1cbat'
#    mtype = 'mid'
#    state = 'none'
#    data  = [0, 0, 0, 0]
#
#    create_table()
#
#    incert_data(msid, dtype, mtype, state, data)
#
#    out = read_v_estimate(msid, dtype, mtype, state)
#    print("Data Inserted: "  + str(out))
#
#    data  = [1, 1, 1, 1]
#    update_data(msid, dtype, mtype, state, data)
#
#    out = read_v_estimate(msid, dtype, mtype, state)
#    print("Data Updated:  "  + str(out))
#
#    out = read_v_estimate_full(msid)
#    print("Full Data: " + str(out))
#
#    delete_entry(msid, state)
#    try:
#        out = read_v_estimate(msid, dtype, mtype, state)
#        print("Data Is Still Here:  "  + str(out))
#    except:
#        print("Data Deleted")

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        msid = sys.argv[1]
        msid.strip()
        out  = read_v_estimate_full(msid)
        print(str(out))
    else:
#        unittest.main()
        pass

