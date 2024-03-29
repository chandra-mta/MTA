#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#   get_value_from_sybase.py: run sybase command for python3.6                      #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Jun 21, 2019                                               #
#                                                                                   #
#   Note: this function must be run after setting:                                  #
#           source /soft/SYBASE16.0/SYBASE.csh                                      #
#           setenv PYTHONPATH /soft/SYBASE16.0/OCS-16_0/python/python34_64r/lib     #
#         to set sybpydb module correctely.                                         #
#         see also: set_sybase_env_and_run.py                                       #
#                                                                                   #
#####################################################################################

import sys
import os
import string
import re
import json
import time
import datetime
#
import sybpydb
#
#--- read directory paths
#
path   = '/data/mta/Script/Python3.6/MTA/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]
for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" % (var, line))
#
#--- set parameters
#
serv   = 'ocatsqlsrv'
usr    = 'mtaops_internal_web'
line   = pass_dir + '.targpass_internal'
with  open(line, 'r') as f:
    passwd = f.readline().strip()

#------------------------------------------------------------------------------------
#-- get_value_from_sybase: run sybase command for python3.6                        --
#------------------------------------------------------------------------------------

def get_value_from_sybase(cmd, db='axafocat'):
    """
    run sybase command for python3.6
    input:  cmd --- sybase command, fetchin only
            db  --- database name; default: axafocat
    output: row --- a json string (of a list of lists)
    """
#
#--- connect to sybase
#
    conn = sybpydb.connect(servername=serv, user=usr, password=passwd)
    cur  = conn.cursor()
#
#--- set db name
#
    dcmd = 'use ' + db
    cur.execute(dcmd)
#
#--- fetch data
#
    try:
        cur.execute(cmd)
        row = cur.fetchall()

        cur.close()
        conn.close()

    except:
        cur.close()
        conn.close()
        return [[]]
#
#--- convert none string data into string
#
    save = []
    for dset in row:
        tsave = []
        for k in range(0, len(dset)):
            ent = dset[k]
#
#--- convert sybpydb.LOB objects are converted back to a string
#
            mc = re.search('LOB', str(ent))
            if mc is not None:
                out = convert_lob_to_string(cmd, k)
#
#--- convert datetime object into date
#
            elif isinstance(ent, datetime.date):
                out = ent.strftime('%Y-%m-%dT%H:%M:%S')

#            elif isinstance(ent, varchar):
#                out = str(ent)

            else:
                out = ent

            tsave.append(out)

        tsave = tuple(tsave)
        save.append(tsave)
#
#--- convert a list to a json string so that we can pass back to the main script
#
    row = json.dumps(save)

    return row

#-------------------------------------------------------------------------------------
#-- convert_lob_to_string: rerun pybase command for a lob object and convert into a string
#-------------------------------------------------------------------------------------

def convert_lob_to_string(cmd, pos):
    """
    rerun pybase command for a lob object and convert into a string
    input:  cmd --- original pybase command
            pos --- the position of lob object in the command column names
    output: out --- a content of lob
    """
#
#--- reconstruct the command for the lob object
#
    atemp = re.split('select', cmd)
    btemp = re.split('from',   atemp[1])
    ctemp = re.split(',',      btemp[0])
    col   = ctemp[pos]
    
    cmd   = 'select ' + col + ' from ' + btemp[1]
#
#--- return the sybase command
#
    conn = sybpydb.connect(servername=serv, user=usr, password=passwd)
    cur  = conn.cursor()
    cur.execute(cmd)
    row  = cur.fetchone()
#
#--- convert lob object to a string
#
    out  = getlobdata(row[0])

    cur.close()
    conn.close()

    return out

#-------------------------------------------------------------------------------------
#-- getlobdata: convert LOB object to a string                                      --
#-------------------------------------------------------------------------------------

def getlobdata(lob):
    """
    convert LOB object to a string. 
    input:  lob --- LOB object
    output: out --- a string

    this functioin works only when LOB object is extracted specificlly for that column
    with fetchone. See "convert_lob_to_string" how to set to use this function.

    ref: http://infocenter.sybase.com/help/index.jsp?topic=/com.sybase.infocenter.dc20155.1600/doc/html/adh1376805082896.html
    """
    outarr = bytearray()
    chunk = bytearray(1024)
    while True:
        clen = lob.readinto(chunk)
        if clen == None:
            break

        outarr.extend(chunk[:clen])

    out = str(outarr)

    return out


#-------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        cmd = sys.argv[1]
        db  = 'axafocat'

    elif len(sys.argv) == 3:
        cmd = sys.argv[1]
        db  = sys.argv[2]

    else:
        print("Usage: get_value_from_sybase.py '<cmd>' <database name>")
        print("If <database name> is not given, default is axafocat.")
        print("(Don't forget '' around Sybase command.)")


    out = get_value_from_sybase(cmd, db)
#
#---- this will return binay-like string
#
    print(out)
