#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#       ephem_run_script.py: update dephem.rdb file                                                 #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Jan 04, 2016                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import subprocess
import unittest
import urllib2

path = '/data/mta/Script/Ephem/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()
for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few paths
#
eph_data = '/data/mta/Script/Ephem/EPH_Data'
rdb      = '/data/mta/DataSeeker/data/repository/dephem.rdb'
idl_path = '+/data/mta/Script/Ephem/Scripts/:+/usr/local/rsi/user_contrib/astron_Oct09/pro:+/home/mta/IDL:/home/nadams/pros:+/data/swolk/idl_libs:/home/mta/IDL/tara:widget_tools:utilities:event_browser'

#-------------------------------------------------------------------------------------------
#-- update_dephem_data: the main script to update dephem.rdb file                        ---
#-------------------------------------------------------------------------------------------

def update_dephem_data():
    """
    the main script to update dephem.rdb file
    input:  none
    output: rdb (/data/mta/DataSeeker/data/repository/dephem.rdb)
    """
#
#--- copy idl scripts to the current directory
#
    cmd = 'cp ' + bin_dir + '/*.pro ' + exc_dir + '/.'
    os.system(cmd)
    cmd = 'chmod 755 ' + exc_dir + '/*pro'
    os.system(cmd)
#
#--- find currently available data from GOT site
#
    cdata = find_available_deph_data()
#
#--- check already processed data
#
    last = find_the_last_entry()
#
#--- compare them and process the new eph data
#
    for ent in cdata:
        atemp = re.split('\/', ent)
        btemp = re.split('.EPH', atemp[len(atemp)-1])
        ctemp = re.split('DE', btemp[0])
        try:
            time  = int(ctemp[1])
        except:
            continue

        if time <= last:
            continue
        else:
#
#---- using lephem.pro, create an ascii file
#
            chk = run_lephem(ent, time)
            if chk == 0:
                continue                            #---- the process failed; skip the rest
#
#--- using kplookup, put soloar wind information
#
            chk = run_kplookup(time)
#
#--- compute/convert data format suitable for the dataseek database
#
            chk = convert_data_format(time)
            if chk == 0:
                continue
#
#---- select a new data from dephem.gsme and append to /data/mta/DataSeeker/data/repository/dephem.rdb
#
            update_rdb()

#-------------------------------------------------------------------------------------------
#-- find_available_deph_data: create a list of potential new data file name               --
#-------------------------------------------------------------------------------------------

def find_available_deph_data():
    """
    create a list of potential new data file name
    input:  none, but read from /dsops/GOT/aux/DEPH.dir/
    output: cdata   --- a list of the data file names
    """
#
#--- find current time
#
    ttemp = tcnv.currentTime()
    year  = int(ttemp[0])
    ydate = int(ttemp[7])

    syear = str(year)
    tyear = syear[2] + syear[3]
#
#--- first 20 days of the year, we also check the last year input data
#
    if ydate < 20:
        lyear  = year -1
        slyear = str(lyear)
        ltyear = slyear[2] + slyear[3]

        cmd = 'ls /dsops/GOT/aux/DEPH.dir/DE' + ltyear + '*.EPH >  ' + zspace
        os.system(cmd)
        cmd = 'ls /dsops/GOT/aux/DEPH.dir/DE' + tyear  + '*.EPH >> ' + zspace
        try:
            os.system(cmd)
        except:
            pass
    else:
        cmd = 'ls /dsops/GOT/aux/DEPH.dir/DE' + tyear  + '*.EPH >  ' + zspace
        try:
            os.system(cmd)
        except:
            pass

    try:
        f     = open(zspace, 'r')
        cdata = [line.strip() for line in f.readlines()]
        f.close()
    except:
        cdata = []

    mcf.rm_file(zspace)

    return cdata

#-------------------------------------------------------------------------------------------
#-- find_the_last_entry: find the time stamp of the last processed data                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry():
    """
    find the time stamp of the last processed data
    input:  none, but read from /data/mta/Script/Ephem/EPH_Data/*dat0
    output: last    --- the time stamp of the last data file proccessed: <yy><ydate>
    """

    cmd = 'ls /data/mta/Script/Ephem/EPH_Data/DE*.EPH.dat00 > ' + zspace
    os.system(cmd)

    f     = open(zspace, 'r')
    pdata = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)

    last  = pdata[len(pdata) -1]
    atemp = re.split('DE', last)
    btemp = re.split('.EPH', atemp[1])
    last  = int(btemp[0])

    return last

#-------------------------------------------------------------------------------------------
#-- run_lephem: run idl script lephem.pro which convert the data into ascii data         ---
#-------------------------------------------------------------------------------------------

def run_lephem(fname, time):
    """
    run idl script lephem.pro which convert the data into ascii data
    input:  fname   --- the name of the input file: DE<time>.EPH
            time    --- time stamp of the file copied
    output: ascii data file -- DE<time>.EPH.dat0
    """

    cmd = 'cp ' + fname + ' ' +  eph_data + '/.'
    os.system(cmd)

    cname = 'DE' + str(time) + '.EPH'
    
    try:
        line = "lephem,'" + str(cname) + "'\n"
        line = line + "exit\n"
        fo  = open('./eph_run.pro', 'w')
        fo.write(line)
        fo.close()

        os.environ['IDL_PATH'] = idl_path
        subprocess.call("idl eph_run.pro",  shell=True)
        mcf.rm_file('./eph_run.pro')
        return 1
    except:
        return 0

#-------------------------------------------------------------------------------------------
#-- run_kplookup: run idl script kplookup.pro which adjusts the data for the solar wind   --
#-------------------------------------------------------------------------------------------

def run_kplookup(time):
    """
    run idl script kplookup.pro which adjusts the data for the solar wind influence
    input:  time    --- time in the format of <yy><ydate>
    output: DE<time>.EPH.dat0 updated for the soloar wind influence
    """

    xxx = 999
    if xxx ==999:
#    try:
        line = "kplookup,'/data/mta/Script/Ephem/EPH_Data/DE" + str(time) + ".EPH.dat0'" + "\n"
        line = line + "exit\n"
     
        fo  = open('./kp_run.pro', 'w')
        fo.write(line)
        fo.close()
    
        os.environ['IDL_PATH'] = idl_path
        subprocess.call("idl kp_run.pro", shell=True)
        cmd = 'idl kp_run.pro'
        os.system(cmd)
        mcf.rm_file('./kp_run.pro')
    
        return  1
#    except:
#        return  0

#-------------------------------------------------------------------------------------------
#-- convert_data_format: using cocochan fortran code, convert the data format             --
#-------------------------------------------------------------------------------------------

def convert_data_format(time):
    """
    using cocochan fortran code, convert the data format
    input:  time    --- time in format of <yy><ydate>
    output: ./dephem.gsme 
    """
#
#--- cp the data with "DE<time>.EPHH.dat0" to ./dephem.data
#
    cmd = 'cp  ' + eph_data + '/DE' + str(time) + '.EPH.dat00  ./dephem.dat'
    os.system(cmd)
#
#--- run a fortran code cocochan. this converts the format to that of the rdb file
#
    try:
        cmd = bin_dir + '/geopack/cocochan'
        os.system(cmd)
        mcf.rm_file('./dephem.dat')

        return 1
    except:
        mcf.rm_file('./dephem.dat')
        return 0

#-------------------------------------------------------------------------------------------
#-- update_rdb: update dephem.rdb file                                                   ---
#-------------------------------------------------------------------------------------------

def update_rdb():
    """
    update dephem.rdb file
    input: none but read from dephem.rdb and dephem.gsme. the latter must be
           in the current directory. 
    output: updated dephem.rdb
    """
#
#--- read the rdb file (dephem.rdb)
#
    rdb_file  = '/data/mta/DataSeeker/data/repository/dephem.rdb'
    f    = open(rdb_file)
    rdb  = [line.strip() for line in f.readlines()]
    f.close()
#
#--- read the new data file
#
    f    = open('./dephem.gsme', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    if len(data) < 1:
        return 
#
#--- find the starting time of the new data
#
    atemp = re.split('\s+', data[0])
    stime = float(atemp[0])
#
#---- extract the data from dephem.rdb up to the starting time of the new data
#
    lsave = []
    for ent in rdb:
        atemp = re.split('\s+|\t+', ent)

        try:
            rtime = float(atemp[0])
        except:
            continue 

        if rtime < stime:
            lsave.append(ent)
        else:
            break
#
#--- now add the newest data
#
    for ent in data:
        ent = ent.replace('|', '\t')
        lsave.append(ent)
#
#--- update dephem.rdb
#
    fo = open(rdb_file, 'w')
    line = 'time    ALT ECIX    ECIY    ECIZ    GSMX    GSMY    GSMZ    CRMREG\n'
    fo.write(line)
    line = 'N   N   N   N   N   N   N   N   N\n'
    fo.write(line)

    for ent in lsave:
        fo.write(ent)
        fo.write('\n')
    fo.close()

    mcf.rm_file('./dephem.gsme')

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_dephem_data()
