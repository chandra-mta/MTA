#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#           extract_soloar_panel_data.py: extract soloar panel related msid data                #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 12, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import time
import random
import numpy
import astropy.io.fits  as pyfits
import unittest
import Chandra.Time
import Ska.engarchive.fetch as fetch
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; punlearn dataseeker  ', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Sol_panel/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions   as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few lists
#
msid_list  = ['tmysada', 'tpysada', 'tsamyt', 'tsapyt', 'tfssbkt1', 'tfssbkt2', 'tpc_fsse']
dcol_list  = ['obattpwr', 'ohrmapwr', 'oobapwr']   
angle_list = [40, 60, 80, 100, 120, 140, 160]
#
#--- some other definitions
#
header     = 'time\tsuncent\ttmysada\ttpysada\ttsamyt\ttsapyt\ttfssbkt1\ttfssbkt2'
header     = header + '\ttpc_fsse\telbi\telbv\tobattpwr\tohrmapwr\toobapwr'
solor_file = 'solar_panel_all_data'
orb_data   = '/data/mta/DataSeeker/data/repository/orb_angle.rdb'

#---------------------------------------------------------------------------------------
#-- extract_soloar_panel_data: extract sun cneter angle and soloar panel             ---
#---------------------------------------------------------------------------------------

def extract_soloar_panel_data(tstart='', tstop=''):
    """
    extract sun cneter angle and soloar panel related msid quantities to make a data table
    input:  tstart  --- starting time
            tstop   --- stopping time
    output: <data_dir>/<solor_file>
    """
#
#--- if starting time is not given, find the last entry time
#
    if tstart == '':
        tstart = find_last_entry_time()
    tbegin = Chandra.Time.DateTime(tstart).date
#
#--- if stopping time is not given, use today's date
#
    if tstop == '':
        tend  = time.strftime("%Y:%j:00:00:00", time.gmtime())
        tstop = Chandra.Time.DateTime(tend).secs
    else:
        tend  = Chandra.Time.DateTime(tstop).date

    print("Period: " + tbegin + '<--->' + tend)
#
#--- extract sun cent angle data
#
    [stime, suncent]  = get_sunangle_data(tstart, tstop)
    all_data          = [stime, suncent]
#
#--- extract first data, and match which elements match with those of sun center data
#--- and create a list of indicies which will be used for other msid data
#
    [mtime, data] = get_data_from_ska(msid_list[0], tstart, tstop)
    index         = match_to_suncent(stime, mtime)
    data          = select_by_index(data, index)
    all_data.append(data)
#
#--- run the rest
#
    for msid in msid_list[1:]:
        [mtime, data] = get_data_from_ska(msid, tstart, tstop)
        data          = select_by_index(data, index)
        all_data.append(data)
#
#--- elbi and elbv have 100 times more dense data; so use only 1 in 100 data points
#
    [mtime, data] = get_data_from_ska('elbi', tstart, tstop)
    mtime         = mtime[::100]
    data          = data[::100]
    index         = match_to_suncent(stime, mtime)
    data          = select_by_index(data, index)
    all_data.append(data)

    [mtime, data] = get_data_from_ska('elbv', tstart, tstop)
    data          = data[::100]
    data          = select_by_index(data, index)
    all_data.append(data)
#
#--- dataseeker results
#
    [dtime, obattpwr, ohrmapwr, oobapwr] = get_data_with_dataseeker(tstart, tstop, dcol_list)

    index  = match_to_suncent(stime,   dtime)

    data   = select_by_index(obattpwr, index)
    all_data.append(data)

    data   = select_by_index(ohrmapwr, index)
    all_data.append(data)

    data   = select_by_index(oobapwr,  index)
    all_data.append(data)
#
#--- initialize data saver
#
    sdata = []
    for k in range(0, len(all_data)):
        sdata.append([])

    line = ''
    for k in range(0, len(all_data[0])):

        val  = all_data[0][k]
        line = line + "%d" % val
        sdata[0].append(int(val))

        for m in range(1, len(all_data)):
            val  = "%3.3f" % all_data[m][k]
            line = line +  "\t"  + val
            sdata[m].append(float(val))

        line = line + '\n'
#
#--- write out data
#
    outname = data_dir + solor_file

    if os.path.isfile(outname):
        with open(outname, 'a') as fo:
            fo.write(line)
#
#--- if this is the first time, add the hader
#
    else:
        aline = "#" + header + '\n'
        aline = aline + "#" +  '-'*120 + '\n'
        aline = aline + line
        with  open(outname, 'w') as fo:
            fo.write(aline)
#
#--- separate data into several angle interval files
#
    separate_data_into_angle_step(sdata, tstart)
    
#---------------------------------------------------------------------------------------
#-- find_last_entry_time: find the last data entry time                               --
#---------------------------------------------------------------------------------------

def find_last_entry_time():
    """
    find the last data entry time
    input:  none, but read <data_dir>/solar+panel_all_data
    output: ltiem   --- the last entry time in seconds from 1998.1.1
    """
    try:
        ifile = data_dir + solor_file
        data  = mcf.read_data_file(ifile)
        atemp = re.split('\s+', data[-1])
        ltime = int(float(atemp[0]))
    except:
        ltime = 63071999            #--- 2000:001:00:00:00

    return ltime

#---------------------------------------------------------------------------------------
#-- select_by_index: select data elements by a list of indicies                       --
#---------------------------------------------------------------------------------------

def select_by_index(data, index):
    """
    select data elements by a list of indicies
    input:  data    --- data list
            index   --- a list of inicies of which elements will be selected
    output: data    --- selected data
    """
    data     = numpy.array(data)
    data     = data[index]
    data     = list(data)

    return data
    
#---------------------------------------------------------------------------------------
#-- get_sunangle_data: read sunangle data                                             --
#---------------------------------------------------------------------------------------

def get_sunangle_data(tstart, tstop):
    """
    read sunangle data
    input:  tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output  stime   --- a list of time
            suncent --- a list of sun center angle
    """
#
#--- sun center angle
#
    data    = mcf.read_data_file(orb_data)
    data    = mcf.separate_data_to_arrays(data)
#
#--- first two rows are headers; skip them
#
    stime   = data[0][2:]
    suncent = data[1][2:]

    istart  = -999
    istop   = len(stime)

    for k in range(0, len(stime)):
        if (istart < 0) and (stime[k] > tstart):
           istart = k  
        elif stime[k] > tstop:
            istop = k
            break

    if istart < 0:
        istart = 0

    try:
        stime   = stime[istart:istop]
        suncent = suncent[istart:istop]
    except:
        exit(1)

    if len(stime) < 1:
        exit(1)

    return [stime, suncent]

#---------------------------------------------------------------------------------------
#-- get_data_from_ska: extract data from ska database                                 --
#---------------------------------------------------------------------------------------

def get_data_from_ska(msid, tstart, tstop):
    """
    extract data from ska database
    input:  msid    --- msid
            tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
    output: time    --- a list of time
            data    --- a list of data
    """
    out  = fetch.MSID(msid, tstart, tstop)
    time = out.times
    data = out.vals

    return [time, data]

#---------------------------------------------------------------------------------------
#-- match_to_suncent: create an index list which indicates  which elements match with the suncent entries
#---------------------------------------------------------------------------------------

def match_to_suncent(stime, mtime):
    """
    create an index list which indicates  which elements match with the suncent entries
    input:  stime   --- a list of time from suncent
            mtime   --- a list of time in which index will be selected
    output: save    --- a list of indices which match the suncent time
    """
    slen = len(stime)
    mlen = len(mtime)
    save = []
    m    = 0
    for k in range(0, slen):
        kup = 0
        for n in range(m, mlen-1):
            if (stime[k] >= mtime[n]) and (stime[k] < mtime[n+1]):
                save.append(n)
                kup = 1
                m   = n
                break
            elif (stime[k] < mtime[n]):

                if n >= mlen-2:
                    m = mlen -2
                    save.append(m)
                    continue
                save.append(n)
                kup = 1
            elif stime[k] > mtime[n+1]:
                m -= 5
                if m < 0:
                    m = 0
                    if stime[k] < mtime[m]:
                        save.append(m)
                        kup = 1
                        break
                else:
                    continue

        if kup == 1:
            continue

    return save

#---------------------------------------------------------------------------------------
#-- get_data_with_dataseeker: extract data using dataseeker                          ---
#---------------------------------------------------------------------------------------

def get_data_with_dataseeker(tstart, tstop, col_list):
    """
    extract data using dataseeker
    input:  tstart  --- starting time in seconds from 1998.1.1
            tstop   --- stopping time in seconds from 1998.1.1
            col_list    --- data name to be extracted (without _ or _avg part)
    output: save        --- a list of lists of data, including time list
    """
#
#--- check wehter enmpty command file exist. if not, create
#
    if not os.path.isfile('test'):
        cmd = 'touch test'
        os.system(cmd)
#
#--- create dataseeker command
#
    cmd1 = '/usr/bin/env PERL5LIB="" '

    cmd2 = 'dataseeker.pl infile=test outfile=temp.fits '
    cmd2 = cmd2 + 'search_crit="columns='
#
#--- column name start with '_' and end '_avg'
#
    for k in range(0, len(col_list)):
        col = col_list[k]
        if k == 0 :
            acol = '_'  + col + '_avg'
        else:
            acol = ',_' + col + '_avg'

        cmd2 = cmd2 + acol

    cmd2 = cmd2 + ' timestart=' + str(tstart)   + ' timestop=' + str(tstop) + '"'
    cmd2 = cmd2 + ' loginFile=' + house_keeping + 'loginfile '
#
#--- run the dataseeker command under ascds environment
#
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- read the data and create a list of lists 
#
    hrd  = pyfits.open('temp.fits')
    data = hrd[1].data
    hrd.close()

    dtime = data['time']
    save  = [dtime]
    for col in col_list:
        acol = col + '_avg'
        save.append(data[acol])
#
#--- clean up
#
    mcf.rm_files('test')
    mcf.rm_files('temp.fits')

    return save

#---------------------------------------------------------------------------------------
#-- separate_data_into_angle_step: separate a full data set into several angle interval data sets 
#---------------------------------------------------------------------------------------

def separate_data_into_angle_step(data, tstart=0):
    """
    separate a full data set into several angle interval data sets
    input:  data    --- data matrix of <col numbers> x <data length>
            tstart  --- starting time in seconds from 1998.1.1
    output: <data_dir>/solar_panel_angle_<angle>
    """
#
#--- set a few things
#
    alen  = len(angle_list)             #--- the numbers of angle intervals
    clen  = len(data)                   #--- the numbers of data columns
    save  = []                          #--- a list of lists to sve the data
    for k in range(0, alen):
        save.append([])
#
#--- go through all time entries, but ignore time before tstart
#
    for k in range(0, len(data[0])):
        if data[0][k] < tstart:
            continue

        for m in range(0, alen):
#
#--- set angle interval; data[1] is the column to keep sun center angle
#
            abeg = angle_list[m]
            aend = abeg + 20
            if (data[1][k] >= abeg) and (data[1][k] < aend):
                line = create_data_line(data, clen, k)
                save[m].append(line)
                break
#
#--- create/update the data file for each angle interval
#
    for k in range(0, alen):
        outname = data_dir + 'solar_panel_angle_' + str(angle_list[k])

#
#--- print the data
#
        if len(save[k]) == 0:
            continue

        line = ''
        for ent in save[k]:
            line = line + ent + '\n'

        if os.path.isfile(outname):
            with open(outname, 'a') as fo:
                fo.write(line)
#
#--- if this is the first time, add the header
#
        else:
            aline = "#" + header + '\n'
            aline = aline + '#' + '-'*120 + '\n'
            aline = aline + line
            with open(outname, 'w') as fo:
                fo.write(aline)

#---------------------------------------------------------------------------------------
#-- create_data_line: create output data line                                         --
#---------------------------------------------------------------------------------------

def create_data_line(data, clen, k):
    """
    create output data line
    input:  data    --- data matrix of clen x len(data[0])
    output: line    --- a line of data of clen elements
    """

    line = str(data[0][k])
    for m in range(1, clen):
        line = line + '\t' + str(data[m][k])

    return line

#---------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST   --
#---------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#---------------------------------------------------------------------------------------

    def test_get_sunangle_data(self):

        tstart   = 631151994
        tstop    = 631929594
        out      = get_sunangle_data(tstart, tstop)

        print("get_sunangle_data: " +  str(out[0][0]) + '\t' + str(out[1][0]) + '\n')

#---------------------------------------------------------------------------------------

    def test_match_to_suncent(self):

        stime = range(0, 30)
        mtime = range(0, 30, 4)

        index = match_to_suncent(stime, mtime)

        print("match_to_suncent:" + str(index))

#---------------------------------------------------------------------------------------

    def test_get_data_from_ska(self):

        msid     = 'tmysada'
        tstart   = 631151994
        tstop    = 631929594
        out      = get_data_from_ska(msid, tstart, tstop)

        print("get_data_from_ska:" + str(out[0][0]) + '\t' + str(out[1][0]) + '\n')

#---------------------------------------------------------------------------------------

    def test_get_data_with_dataseeker(self):

        print("I AM HERE RUNNIGN Dataseeker")
        tstart   = 631151994
        tstop    = 631929594
        col_list = dcol_list
        out      = get_data_with_dataseeker(tstart, tstop, col_list)

        print("get_data_with_dataseeker: " + str(out[0][0]) + '\t' + str(out[1][0]) + '\t' + str(out[2][0]) + '\t' + str(out[3][0]) + '\n')

#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1].lower() == 'test':
#
#--TEST TEST TEST TEST TEST TEST ----------------------------
#

            sys.argv = [sys.argv[0]]
            unittest.main()

#
#-- REGULAR RUN                  ----------------------------
#
        else:
            if len(sys.argv) == 2:
                tstart = float(sys.argv[1])
        
            if len(sys.argv) > 2:
                tstart = float(sys.argv[1])
                tstop  = float(sys.argv[2])
            else:
                tstart = ''
                tstop  = ''
        
            extract_soloar_panel_data(tstart, tstop)
    else:
        extract_soloar_panel_data()

    exit(1)

#-- DATA RE-RUN                  ----------------------------


    ifile = data_dir + solor_file
    cmd   = 'mv ' + ifile + ' ' + file + '~'
    os.system(cmd)

    ystart = ['001', '090', '180', '270']
    ystop  = ['090', '180', '270', '001']
    for year in range(2000, 2019):
        for k in range(0, 4):

            if year == 2018 and k ==2:
                break

            nyear = year
            if k == 3:
                nyear += 1

            tstart = str(year)  + ':' +  ystart[k] + ':00:00:00'
            tstop  = str(nyear) + ':' +  ystop[k]  + ':00:00:00'

            print("Period: " + tstart + '<-->' + tstop)

            tstart = Chandra.Time.DateTime(tstart).secs
            tstop  = Chandra.Time.DateTime(tstop).secs
            print("\t" + str(tstart) + '<-->' + str(tstop))

            extract_soloar_panel_data(tstart, tstop)


