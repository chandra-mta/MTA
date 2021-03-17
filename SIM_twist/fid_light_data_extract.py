#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#               fid_light_data_extract.py: extract fid light information                #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 03, 2021                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
import Ska.engarchive.fetch as fetch
#
#--- reading directory list
#
path = '/data/mta/Script/ALIGNMENT/Sim_twist/Scripts/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf  #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())  
zspace = '/tmp/zspace' + str(rtail)

mon_list = [0, 31, 59, 90, 120, 151, 181, 212, 234, 373, 304, 334]

#------------------------------------------------------------------------------------------
#-- fid_light_data_extract: extract aca position i and j, sim postion, and creates a table 
#------------------------------------------------------------------------------------------

def fid_light_data_extract(tstart='', tstop='', year=''):
    """
    extract aca position i and j, sim postion, and creates a table
    input:  tstart  --- starting time
            tstop   --- stopping time
            year    --- year
            if these are not given, the the interval of the previous month are used
    output: udated data file, e.g., I-1, S-3, H-I-1, H-S-3 etc in <data_dir>
    """
#
#--- if the starting and stopping time are not given, set them
#
    if tstart == '':
        [tstart, tstop] = find_start_and_stop_time()
#
#--- get fid light information
#
    [file_id, fid_detect] = extract_fidlight_data(tstart, tstop)
#
#--- get oterh informatin related to the fid information and print out the results
#
    get_acen_data(tstart, tstop, file_id, fid_detect)

#------------------------------------------------------------------------------------------
#-- find_start_and_stop_time: find start and stop time                                  ---
#------------------------------------------------------------------------------------------

def find_start_and_stop_time():
    """
    find start and stop time (set for the last month)
    """
    out = time.strftime("%Y:%m", time.gmtime())
    [lyear, lmon] = re.split(':', out)
    tstop = lyear+':'+ lmon + ':01'
    tstop = mcf.convert_date_format(tstop, ifmt='%Y:%m:%d', ofmt='%Y:%j:00:00:00')

    year  = int(float(lyear))
    mon   = int(float(lmon))
    pyear = year
    pmon  = mon - 1
    if pmon < 1:
        pmon   = 12
        pyear -= 1

    tstart = str(pyear) + ':' + mcf.add_leading_zero(pmon) + ':01'
    tstart = mcf.convert_date_format(tstart, ifmt='%Y:%m:%d', ofmt='%Y:%j:00:00:00')

    return [tstart, tstop]

#------------------------------------------------------------------------------------------
#-- get_acen_data: for given fid light information, extract acen fits files and extract needed information
#------------------------------------------------------------------------------------------

def get_acen_data(tstart, tstop, file_id, fid_detect):
    """
    for given fid light information, extract acen fits files and extract needed information
    input:  tstart  --- starting time
            tstop   --- stopping time
            file_id --- id of the acen fits file
            fid_detect  --- a dictionary of information [<slot id>, <id string> <id number>]
    output: udated data file, e.g., I-1, S-3, H-I-1, H-S-3 etc in <data_dir>
    """
#
#--- first just get a list of potential acent fits files
#
    acent_list = call_arc5gl('browse', 'pcad', 1, tstart=tstart, tstop=tstop,\
                              filetype='acacent', sub='aca')
#
#--- compare the list with a file id, and if it is found, procceed farther
#
    for fname in file_id:
        chk = 0
        for comp in acent_list:
            mc = re.search(fname, comp)
            if mc is not None:
                filename = comp
                chk = 1
                break
        if chk == 0:
            continue
#
#--- extract an acen fits file
#
        [fits] = call_arc5gl('retrieve', 'pcad', 1, tstart='', tstop='',\
                             filetype='acacent', filename=filename, sub='aca')

        ff     = pyfits.open(fits)
        data   = ff[1].data
        ff.close()
        mcf.rm_file(fits)
#
#--- extract needed information for each slot 
#
        for m in range(0, len(fid_detect[fname][0])):
            slot_id =  fid_detect[fname][0][m]
            mask    = data['slot'] == slot_id
            out     = data[mask]
            time    = out['time']
            cent_i  = out['cent_i']
            cent_j  = out['cent_j']
            ang_y   = out['ang_y']
            ang_z   = out['ang_z']
            alg     = out['alg']

            if len(time) == 0:
                continue
#
#---- take 5 min average for the data
#
            try:
                begin  = time[0]
            except:
                continue
            end    = begin + 300.0
            m      = 0
            k_list = []
            sline   = ''
            for k in range(m, len(time)):
                if time[k] < begin:
                    continue
                elif time[k] >= begin and time[k] < end:
                    k_list.append(k)
                else:
                    try:
                        atime   = numpy.mean(time[k_list[0]:k_list[-1]])
                        acent_i = numpy.mean(cent_i[k_list[0]:k_list[-1]])
                        acent_j = numpy.mean(cent_j[k_list[0]:k_list[-1]])
                        aang_y  = numpy.mean(ang_y[k_list[0]:k_list[-1]])
                        aang_z  = numpy.mean(ang_z[k_list[0]:k_list[-1]])
                        aalg    = alg[k_list[-1]]
                    except:
                        continue
#
#--- find fapos and tscpos info near to the given time interval
#
                    flist   = fetch.MSID('3fapos',  time[k_list[0]], time[k_list[-1]])
                    tslist  = fetch.MSID('3tscpos', time[k_list[0]], time[k_list[-1]])
                    fapos   = numpy.mean(flist.vals)
                    tscpos  = numpy.mean(tslist.vals)

                    sline    = sline  + str(atime) + '\t'
                    sline    = sline  + str(fid_detect[fname][0][m]) + '\t'
                    sline    = sline  + str(fid_detect[fname][2][m]) + '\t'
                    sline    = sline  + str(aalg)    + '\t'
                    sline    = sline  + str(format(acent_i, '.3f'))  + '\t'
                    sline    = sline  + str(format(acent_j, '.3f'))  + '\t'
                    sline    = sline  + str(format(aang_y,  '.6f'))  + '\t'
                    sline    = sline  + str(format(aang_z,  '.6f'))  + '\t'
                    sline    = sline  + str(fapos)   + '\t'
                    sline    = sline  + str(tscpos)  + '\n'
    
                    k_list = []
                    begin  = end
                    end   += 300.0
#
#--- write out the results
#
            ofile  = data_dir + fid_detect[fname][1][m]
            with open(ofile, 'a') as fo:
                fo.write(sline)

#------------------------------------------------------------------------------------------
#-- extract_fidlight_data: get fid light information from fidpr fits file                --
#------------------------------------------------------------------------------------------

def extract_fidlight_data(tstart, tstop):
    """
    get fid light information from fidpr fits file
    input:  tstart      --- starting time
            tstop       --- stopping time
    output: file_id     --- acent fits file id
            fid_detect  --- a dictionary of information [<slot id>, <id string> <id number>]
                            id string is I-<#>/S-<#> for ACIS and H-I-<#>/H-S-<#> for HRC

        pcadf286408332N003_fidpr1.fits
        ROW    slot       id_string    id_num

        1          0 ACIS-I-1              1
        2          1 ACIS-I-5              5
        3          2 ACIS-I-6              6
    """
#
#--- retrieve fidpr fits file
#
    fid_list = call_arc5gl('retrieve', 'pcad', 1, tstart=tstart, tstop=tstop,\
                            filetype='fidprops', sub='aca')
    file_id    = []
    fid_detect = {}
    for fits in fid_list:
        atemp   = re.split('pcadf', fits)
        btemp   = re.split('N',  atemp[1])
        file_n  = btemp[0]
#
#--- get fit light infor. see above for the structure of the table data
#
        ff      = pyfits.open(fits)
        data    = ff[1].data
        ff.close()
        slot    = data['slot']
        sid     = get_id_name(data['id_string'])
        id_n    = data['id_num']
#
#--- data is saved as a dictionary form
#
        fid_detect[file_n] = [slot, sid, id_n]
        file_id.append(file_n)

        mcf.rm_file(fits)

    return [file_id, fid_detect]

#------------------------------------------------------------------------------------------
#-- get_id_name: constract chip id                                                       --
#------------------------------------------------------------------------------------------

def get_id_name(i_list):
    """
    constract chip id
    input:  i_list  --- a list of id string from fidpr fits file
    output: out     --- a list of chip ids
    """
    out = []
    for ent in i_list:
        mc = re.search('ACIS', ent)
        if mc is not None:
            atemp = re.split('ACIS-', ent)
            out.append(atemp[1])

        else:
            atemp = re.split('HRC-',  ent)
            name = 'H-' + str(atemp[1])
            out.append(name)

    return out
    
#------------------------------------------------------------------------------------------
#-- call_arc5gl: using arc5gl to extract a fits file list or a file itself              ---
#------------------------------------------------------------------------------------------

def call_arc5gl(op, detector, level, tstart='', tstop='', filetype='', sub='', filename=''):
    """
    using arc5gl to extract a fits file list or a file itself
    input:  op      ---- operation: retreive/browse
            detector    --- detector
            level       --- level
            tstart      --- starting time if file name is provided, it is ignored
            tstop       --- stopping time if file name is provided, it is ignored
            filetype    --- filetype if file name is provided, it is ignored
            sub         --- sub detector name; default ""
            filename    --- file name; default ""
    output: flist       --- a list of fits file, either results of browse or extracted file name
    """

    line = 'operation=' + op + '\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector='     + detector    + '\n'

    if sub != '':
        line = line + 'subdetector=' + sub      + '\n'

    line = line + 'level='        + str(level)  + '\n'
    line = line + 'filetype='     + filetype    + '\n'

    if filename == '':
        line = line + 'tstart='   + str(tstart) + '\n'
        line = line + 'tstop='    + str(tstop)  + '\n'
    else:
        line = line + 'filename=' + filename    + '\n'
    line = line + 'go\n'


    flist = mcf.run_arc5gl_process(line)

    return flist

#------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 3:
        tstart = sys.argv[1]
        tstop  = sys.argv[2]
        year   = int(float(sys.argv[3]))
    else:
        tstart = ''
        tstop  = ''
        year   = ''

    fid_light_data_extract(tstart, tstop, year)
