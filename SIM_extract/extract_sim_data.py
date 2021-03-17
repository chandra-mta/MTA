#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#           extract_sim_data.py: extract sim data from PRIMARYCCDM_*.*.tl                   #
#                                                                                           #
#               author: t. isobe    (tisobe@cfa.harvard.edu)                                #
#                  based on scripts written by b. spitzbart (bspitzbart@cfa.harvard.edu)    #
#                                                                                           #
#               last update: Mar 06, 2015                                                   #
#                                                                                           #
#############################################################################################

import sys
import os
import string
import re
import math
import random
 
mta_dir = '/data/mta/Script/Python_script2.7/'
sys.path.append(mta_dir)
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts


#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#datadir = '/data/mta_www/mta_sim/Scripts/'
dumpdir = '/data/mta/Script/Dumps/'
outdir  = '/data/mta/www/mta_sim/Scripts/'

#--------------------------------------------------------------------------------------------------
#-- extract_sim_data: extract sim data from PRIMARYCCDM_*.*.tl                                  ---
#--------------------------------------------------------------------------------------------------

def extract_sim_data():

    """
    extract sim data from PRIMARYCCDM_*.*.tl
    input: none but read from <dumpdir>/PRIMARYCCDM_*.*.tl
    output: <outdir>sim_data.out
    """
#
#--- find the time of the last entry from the sim_data.out
#
    sfile = outdir + 'sim_data.out'
    f     = open(sfile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- cleaning up the data; drop the data which the date starts from ":" e.g. :2014
#
    pdata = []
    for ent in data:
        if re.search('^:', ent):
            continue
        else:
            pdata.append(ent)

#
#--- the last entiry values
#
    if len(pdata) > 0:
        atemp  = re.split('\s+', pdata[len(pdata)-1])
        ltime  = tcnv.axTimeMTA(atemp[0])               #--- converting time to sec from 1998.1.1
        time_2 = atemp[0]
        col1_2 = atemp[1]
        col2_2 = atemp[2]
        col3_2 = atemp[3]
    else:
        ltime  = 0
        time_2 = 0
        col1_2 = ''
        col2_2 = ''
        col3_2 = ''
#
#--- check whether input files exists 
#
    cmd = 'ls -rt ' + dumpdir + 'PRIMARYCCDM_*.*.tl >' + zspace
    os.system(cmd)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cmd = 'rm ' + zspace
    os.system(cmd)

    dlen = len(data)

    if dlen < 1:
        exit(1)

#
#--- files exist. read the data from the last 10 files
#
    tlist = data[dlen-40:]

    for ent in tlist:
        cmd = 'cat ' +ent + ' >> ' + zspace
        os.system(cmd)

    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cmd = 'rm ' + zspace
    os.system(cmd)

    prev = ''
    fo = open('./temp_save', 'w')
#
#--- go though each data line
#
    for ent in data:
        try:
#
#--- expect the first letter of the data line is numeric (e.g. 2014).
#
            val = float(ent[0])         
        except:
            continue
#
#--- only data with "FMT" format will be used
#
        mc    = re.search('FMT', ent)
        if mc is None:
            continue

        atemp = re.split('\t+', ent)
#
#--- if there are less than 20 entries, something wrong; skip it
#
        if len(atemp) < 20:             
            continue
#
#--- convert time format
#
        time  = atemp[0]
        time  = time.strip();
        time  = time.replace(' ', ':')
        time  = time.replace(':::', ':00')
        time  = time.replace('::', ':0')
#
#--- if the time is exactly same as one before, skip it
#
        if time == time_2:
            continue
#
#--- if the time is already in the database, keip it
#
        stime = tcnv.axTimeMTA(time)
        if stime <= ltime:
            continue
#
#--- use only data which tscpos and fapos have numeric values
#
        tscpos = atemp[4].strip()
        fapos  = atemp[5].strip()

        if tscpos == "" or fapos == "":
            continue
        else:
            tscpos = int(float(tscpos))
            fapos  = int(float(fapos))

#        aopc   = atemp[11].strip()
#        if aopc == '':
#            aopc = '0'

        mpwm = atemp[12].strip()
        if mcf.chkNumeric(mpwm):
            mpwm = int(float(mpwm))
            mpwm = str(mpwm)
        else:
            mpwm = '0'


#
#--- we want to print only beginning and ending of the same data entries.
#--- skip the line if all three entiries are same as one before, except the last one
#
        if col1_2 == tscpos and col2_2 == fapos and col3_2 == mpwm:
            time_2 = time
            continue

        line = time + '\t' + str(tscpos) + '\t' + str(fapos) + '\t' + mpwm + '\n'
        if line == prev:
            continue
        else:
            pline = time_2  + '\t' + str(col1_2) + '\t' + str(col2_2) + '\t' + str(col3_2) + '\n'
            fo.write(pline)
            fo.write(line)
            prev   = line
            time_2 = time
            col1_2 = tscpos
            col2_2 = fapos
            col3_2 = mpwm

    fo.close()

    sfile2 = sfile + '~'
    cmd    = 'cp  ' + sfile + ' ' + sfile2
    os.system(cmd)
    cmd    = 'cat ./temp_save >> ' + sfile
    os.system(cmd)
#    cmd = 'rm ./temp_save'
#    os.system(cmd)


#------------------------------------------------------------------------------------

if __name__ == "__main__":

    extract_sim_data()
