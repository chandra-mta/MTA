#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       create_cti_data_table.py: extract cti values from data and create cti data tables       #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               Last update: Mar 02, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits
import time
import Chandra.Time
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/CTI/Exc/Temp_comp_area/'
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

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
import mta_common_functions as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)
#
#--- define a few directories we need to run flt_run_pipe
#
working_dir    = exc_dir + '/Working_dir/'
temp_dir       = exc_dir + '/Temp_dir/'
temp_comp_area = exc_dir + '/Temp_comp_area/'

#---------------------------------------------------------------------------------------------------
#--- create_cti_table: run flt_run_pipe on the fits data and extract al/mn/ti cti                ---
#---------------------------------------------------------------------------------------------------

def create_cti_table():
    """
    run flt_run_pipe on the fits data and extract al/mn/ti cti
    Input: none:
    Output: updated <elm>_<ccd#> table
    """
#
#--- sometime param direcoty gets empty out; so just in a case, copy the content
#
    cmd = 'cp -rf ' + house_keeping + 'param ' + exc_dir + '/. '
    os.system(cmd)
#
#--- get fits data list
#
    if os.listdir(working_dir):
        cmd = 'ls ' +  working_dir + '* > ' + zspace
        os.system(cmd)

        with open(zspace, 'r') as f:
            test = f.read()
        mcf.rm_files(zspace)

        m1   = re.search('fits', test)

        if m1 is not None:
            cmd = 'ls ' +  working_dir + '*.fits* > ' + zspace
            os.system(cmd)
            fits_list = mcf.read_data_file(zspace, remove=1)
        else:
            fits_list = []
    
    else:
        cmd = 'rm -rf ' + working_dir + '/*  ' +  temp_dir + '/*  ' + temp_comp_area +  '/* '
        os.system(cmd)
        fits_list = []
#
#--- create focal temperature list
#
    if len(fits_list) > 0:
        [fstart, fstop, file_list] = create_fp_list()

    for fits in fits_list:
#
#--- find starting time in sec from 1998.1.1.
#
        hfits = pyfits.open(fits)
        hdr   = hfits[0].header
        stime = hdr['TSTART']
        stime2= hdr['TSTOP']
        hfits.close()
#
#--- find when the data starts and ends
#
        try:
            dout  = pyfits.getdata(fits, 1)
            time_list = dout.field('TIME')
            date1 = min(time_list)
            date2 = max(time_list)
#
#--- choose the focal temperature files which covers the fits file range
#
            selected_fp_files = choose_fpt_files(date1, date2, fstart, fstop, file_list)
#
#--- make time <---> focal temp lists
#
            [avg_temp, sig, tmin, tmax] =  create_fp_temp_list(date1, date2, selected_fp_files)

            try:
                cmd = 'rm -rf ' + temp_comp_area
                os.system(cmd)
                cmd = 'mkdir -p ' + temp_comp_area
                os.system(cmd)
            except:
                cmd = 'mkdir -p ' + temp_comp_area
                os.system(cmd)
#
#--- run mta flt pipe: results will be in <temp_comp_area>/photons/....
#
            ftemp = re.split('\/', fits)

            ifile = temp_comp_area + ftemp[-1]
            cmd  = 'cp ' + fits  + ' ' + ifile
            os.system(cmd)

            chk = run_flt_pipe(ifile)

            if chk == 0:
#
#--- extract cti values
#
                full_list = find_cti_values_from_file()
                for alist in full_list:
                    if len(alist) > 0:
                        (ccdno, obsid, obsnum, date_obs, date_end, al_cti, mn_cti, ti_cti) = alist
#
#--- print the results
#
                        print_cti_result(ccdno, obsid, obsnum, date_obs, date_end, al_cti,\
                                         mn_cti, ti_cti, avg_temp, sig, tmin, tmax, stime, stime2)
                    else:
                        pass
            else:
                print(str(fits))
        except:
            print("Something wrong about: " + str(fits))
#
#--- keep the record of "bad" obsid
#
            atemp = re.split('acisf', fits)
            btemp = re.split('_', atemp[1])
            ofile = house_keeping + 'exclude_obsid_list'
            with open(ofile, 'a') as fo:
                fo.write(btemp[0] + '\n')

#---------------------------------------------------------------------------------------------------
#-- create_fp_list: create a focal plane temperature fle list                                    ---
#---------------------------------------------------------------------------------------------------

def create_fp_list():
    """
    create a focal plane temperature file list
    Input:      none, but read from /data/mta/Script/ACIS/Focal/Short_term/
    Ooutput:    fstart  --- a list of start time of the files
                fstop   --- a list of stop time of the files
                f_list  --- a list of file names
    """
    cmd = 'ls /data/mta/Script/ACIS/Focal/Short_term/data_* > '+  zspace
    os.system(cmd)
    temperature_file_list = mcf.read_data_file(zspace, remove=1)

    fstart = []
    fstop  = []
    f_list = []

    for tfile in temperature_file_list:
#
#--- tfile has a format of "data_2012_285_0003_285_1130"
#
        chk = re.search('data_', tfile)
        if chk is not None:
            atemp   = re.split('data_', tfile)
            if len(atemp) > 0:
                btemp   = re.split('_', atemp[1])

                year    = int(btemp[0])
                year2   = year
                ydate   = int(btemp[1])
                ydate2  = int(btemp[3])
                if ydate > ydate2:
                    year2 += 1
    
                ttemp   = btemp[2]
                ttemp   = list(ttemp)
                if len(ttemp) == 4:
                    hour    = ttemp[0] + ttemp[1]
                    minutes = ttemp[2] + ttemp[3]
                    dpart   = add_leading_zeros(btemp[1])
                    line    = btemp[0] + ':' + dpart + ':' + hour + ':' + minutes + ':00'
                    begin   = Chandra.Time.DateTime(line).secs
     
                    ttemp   = btemp[4]
                    ttemp   = list(ttemp)
                    hour    = ttemp[0] + ttemp[1]
                    minutes = ttemp[2] + ttemp[3]
                    dpart   = add_leading_zeros(btemp[3])
                    line    = str(year2) + ':' + dpart + ':' + hour + ':' + minutes + ':00'
                    end     = Chandra.Time.DateTime(line).secs

                    fstart.append(begin)
                    fstop.append(end)
                    f_list.append(tfile)

    return(fstart, fstop, f_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def add_leading_zeros(ent, dlen=3):

    ent  = str(ent)
    elen = len(ent)
    if elen < dlen:
        for k in range(elen, dlen):
            ent = '0' + ent

    return ent

#---------------------------------------------------------------------------------------------------
#-- choose_fpt_files: choose focal plane temperature files which cover the given time span       ---
#---------------------------------------------------------------------------------------------------

def choose_fpt_files(date1, date2, fstart, fstop, file_list):
    """
    choose focal plane temperature files which cover the given time span
    Input:  date1       --- starting time (in sec from 1998.1.1)
            date2       --- stopping time (in sec from 1998.1.1)
            fstart      --- a list of starting times of the focal plane temp files
            fstop       --- a list of stopping time of the focal plane temp files
            file_list   --- a list of focal plane temperature files
    Output: selected_file --- a list of focal plane temperature file which covers the time span
    """
    selected_file = []
    for i in range(0, len(fstart)):
        if   (date1 >= fstart[i]) and (date1 <  fstop[i]):
            selected_file.append(file_list[i])

        elif (date2 >  fstart[i]) and (date2 <= fstop[i]):
            selected_file.append(file_list[i])

        elif (date1 >= fstart[i]) and (date2 <= fstop[i]):
            selected_file.append(file_list[i])

        elif (date1 <= fstart[i]) and (date2 >= fstop[i]):
            selected_file.append(file_list[i])

    return selected_file

#---------------------------------------------------------------------------------------------------
#-- create_fp_temp_list: create a list of date and a list of focal temperature                   ---
#---------------------------------------------------------------------------------------------------

def create_fp_temp_list(date1, date2, fp_file_list):
    """
    create a list of date and a list of focal temperature
    Input:      date1   --- starting time
                date2   --- stopping time
                fp_file_list    --- a list of focal plane temperature files
    Output:     date    --- a list of time
                focal   --- a list of focal temperature
    """
    sum1  = 0.0
    sum2  = 0.0
    tot   = 0.0
    tmin  =  99999.0
    tmax  = -99999.0

    chk   = 0
    fp_file_list.sort()
    for ifile in fp_file_list:
#
#--- find the year the file created
#
        atemp = re.split('data_', ifile)
        btemp = re.split('_', atemp[1])
        year  = int(btemp[0])

        data  = mcf.read_data_file(ifile)

        prev  = -1
        for ent in data:
            try:
                atemp = re.split('\s+|\t+', ent)
                btemp = re.split(':', atemp[1])
                ydate = int(btemp[0])
#
#--- check whether the year changed during this file were created
#
                if ydate < prev:
                    year += 1
                prev = ydate 
    
                rest   = float(btemp[1])/ 86400.0
                rest1  = rest * 24.0
                hour   = int(rest1)
                rest2  = (rest1 - float(hour)) * 60.0
                minute = int(rest2)
    
                dpart  = add_leading_zeros(ydate)
                hpart  = add_leading_zeros(hour, dlen=2)
                mpart  = add_leading_zeros(minute, dlen=2)

                line   = str(year) + ':' + dpart + ':' + hpart + ':' + mpart + ':00'
                stime  = Chandra.Time.DateTime(line).secs
    
                if stime > date2:
                    break
                elif stime >=  date1:
                    ftemp = float(atemp[2])
                    if ftemp < -80:
                        sum1 += ftemp
                        sum2 += ftemp * ftemp
                        tot  += 1
                        if ftemp < tmin:
                            tmin = ftemp
                        if ftemp > tmax:
                            tmax = ftemp
            except:
                pass

    avg = sum1 / float(tot)
    sig = math.sqrt(sum2 / float(tot) - avg * avg)
    return (avg, sig, tmin, tmax)

#---------------------------------------------------------------------------------------------------
#-- run_flt_pipe: run mta flt_run_pipe to extract cti data                                       ---
#---------------------------------------------------------------------------------------------------

def run_flt_pipe(part_fits):
    """
    run mta flt_run_pipe to extract cti data
    Input:  part_fits --- fits file name
    Output: <temp_comp_area>/photons/....   cti data
            0 if the operation was successful
            1 if the operation failed
    """
    p_dir = exc_dir + 'Temp_comp_area/photons/'
    try:
#
#--- create input information file for flt_run_pipe
#
        cmd = 'echo ' + part_fits  + '> ' + temp_comp_area + 'zcomp_dat.lis'
        os.system(cmd)

        cmd = 'rm -rf ' + p_dir
        os.system(cmd)
#
#--- run the pipe
#
        pipe_cmd1 = '/usr/bin/env PERL5LIB='
        pipe_cmd2 = " flt_run_pipe  -r zcomp -i" + temp_comp_area +" -o" 
        pipe_cmd2 = pipe_cmd2 + temp_comp_area + " -t mta_monitor_cti.ped -a \"genrpt=yes\" "
        pipe_cmd  = pipe_cmd1 + pipe_cmd2
    
        bash(pipe_cmd, env=ascdsenv, logfile=open('log.txt', 'w'))
#
#--- check wether the computation actually worked. we assume that if "photons" 
#--- directory crated, it did.
#
        if os.path.isdir(p_dir):
            return test_photon_dir()

    except:

        return 1

#---------------------------------------------------------------------------------------------------
#-- test_photon_dir: check whether cti directories are correctly created                         ---
#---------------------------------------------------------------------------------------------------

def test_photon_dir():
    """
    check whether cti directories are correctly created
    Input: none, but read from <temp_comp_are>/....
    Outpu: 0     if it is OK
           1     if there is a problem
    """
    try:
        cmd = 'ls ' + temp_comp_area + 'photons/acis/cti/*/ccd*/ccd*html > ' + zspace
        os.system(cmd)

        test = mcf.read_data_file(zspace, remove=1)

        if len(test) > 0:
            return 0
        else:
            return 1
    except:
        return 1

#---------------------------------------------------------------------------------------------------
#-- find_cti_values_from_file: extract cti information from flt_run_pipe output                  ---
#---------------------------------------------------------------------------------------------------

def find_cti_values_from_file():
    """
    extract cti information from flt_run_pipe output
    Input:  none, but read from <temp_comp_area>/photons/acis/cti/*/ccd*/ccd*html
    Output: full_list --- a list of lists which contains:
            ccdno   --- ccd #
            obsid   --- obsid
            obsnum  --- verion #
            date_obs--- starting date
            date_end--- ending date
            al_cti  --- a list of al cti
            ti_cti  --- a list of ti cti
            mn_cti  --- a list of mn cti
    """
    cmd = 'ls ' + temp_comp_area + 'photons/acis/cti/*/ccd*/ccd*html > ' + zspace
    os.system(cmd)

    result_list = mcf.read_data_file(zspace, remove=1)

    full_list= []
#
#--- "file" is .../ccd<ccd#>.html
#--- and "data" is the content of the ccd<ccd#>.html
#
    for ifile in result_list:

        data     = mcf.read_data_file(ifile)
        ccdno    = -9999
        obsid    =  9999
        obsnum   = 0
        date_obs = ''
        date_end = ''
        si_read  = 0
        al_node  = 0 
        ti_node  = 0 
        mn_node  = 0 
        al_cti   = []
        ti_cti   = []
        mn_cti   = []
        al_err   = []
        ti_err   = []
        mn_err   = []
        elm      = ''

        try:
            for ent in data:
#
#--- detrmine which line we are reading
#
                m1 = re.search('Al Ka', ent)
                m2 = re.search('Mn Ka', ent)
                m3 = re.search('Ti Ka', ent)
                if m1 is not None:
                    elm = 'al'
                elif m2 is not None:
                    elm = 'mn'
                elif m3 is not None:
                    elm = 'ti'
#
#--- indicator for cti section
#
                ms = re.search('S/Ix10', ent)
                if ms is not None:
                    si_read = 1
#
#--- book keeping data
#
                if ccdno == -9999:
                    m = re.search('MTA ACIS CTI Node Analysis Report', ent)
                    if m is not None:
                        atemp = re.split('CCD', ent)
                        btemp = re.split('<', atemp[1])
                        ccdno = btemp[0]

                if obsid == 9999:
                    outval = find_value_from_line(ent, 'OBS_ID')
                    if outval != '':
                        obsid = outval

                if obsnum == 0:
                    outval = find_value_from_line(ent, 'OBI_NUM')
                    if outval != '':
                        obsnum = outval

                if date_obs == '':
                    date_obs = find_value_from_line(ent, 'DATE-OBS')

                if date_end == '':
                    date_end = find_value_from_line(ent, 'DATE-END')
#
#--- read cti values (reading order must be al, mn, then ti)
#
                if (si_read == 1) and (al_node < 4):
                    out = find_cti_from_line(ent)
                    if out != '':
                        al_cti.append(out)
                        al_node += 1
                        if al_node > 3:
                            si_read = 0

                if (si_read == 1) and (al_node > 3) and (mn_node < 4):
                    out = find_cti_from_line(ent)
                    if out != '':
                        mn_cti.append(out)
                        mn_node += 1
                        if mn_node > 3:
                            si_read = 0

                if (si_read == 1) and (mn_node > 3) and (ti_node < 4):
                    out = find_cti_from_line(ent)
                    if out != '':
                        ti_cti.append(out)
                        ti_node += 1
                        if ti_node > 3:
                            si_read = 0
                 
            plist = [ccdno, obsid, obsnum, date_obs, date_end, al_cti, mn_cti, ti_cti]
            full_list.append(plist)

        except:
            plist = []
            full_list.append(plist)

    return full_list

#---------------------------------------------------------------------------------------------------
#-- find_value_from_line: find value for "div_string"                                            ---
#---------------------------------------------------------------------------------------------------

def find_value_from_line(ent, div_string):
    """
    find value for "div_string". this works with only a specifict input file from flt_run_pipe
    Input:  ent         --- input line
            div_string  --- the name of the value we are looking for
    Output: value of the "div_string" or ''. an emptry string is returned when the entry
            does not have the "div_string"
    """
    m1   = re.search('TD ALIGN="CENTER"', ent)
    m2   = re.search('TD ALIGN=center',   ent)
    m3   = re.search(div_string, ent)
    if ((m1 is not None) or (m2 is not None) ) and (m3 is not None):
        atemp   = re.split('<FONT SIZE=-1.7>', ent)
        btemp   = re.split('<', atemp[1])

        return btemp[0]
    else:
        return ''

#---------------------------------------------------------------------------------------------------
#-- find_cti_from_line: find cti values from data line                                           ---
#---------------------------------------------------------------------------------------------------

def find_cti_from_line(ent):
    """
    find cti values from data line. this works only a specific input file from flt_run_pipe
    Input:  ent --- line of data
    Output: line --- cti value +- error. if the line does not contain cti, it return ""
    """
    m1 = re.search('<FONT SIZE=-1.7 ALIGN=RIGHT WIDTH=125>', ent)
    if m1 is not None:
        try:
            atemp = re.split('WIDTH=125>', ent)
            btemp = re.split('</FONT>', atemp[1])
            line  = btemp[0]
            m  = re.search('\*\*\*', ent)
            if m is not None:
                line = '-99999+-00000'
    
            return line
    
        except:
            line = '-99999+-00000'
            return line
    else:
        return ''

#---------------------------------------------------------------------------------------------------
#-- print_cti_result: print out data                                                              --
#---------------------------------------------------------------------------------------------------

def print_cti_result(ccdno, obsid, obsnum, date_obs, date_end, al_cti, mn_cti, ti_cti,\
                     temperature, sig, tmin, tmax, stime, stime2):
    """
    print out data
    Input:  ccdno   --- ccd #
            obsid   --- obsid
            obsnum  --- version #
            date_obs--- starting date
            date_end--- ending date
            al_cti  --- a list of al cti for each node
            mn_cti  --- a list of mn cti for each node
            ti_cti  --- a list of ti cti for each node
            temperature --- temperature
            span    --- how long this period lasted
    Output: <data_dir>/Results/<elm>_<ccd#>
    """
#
#--- print out data
#
    for elm in('al', 'ti', 'mn'):
        cti_data = eval("%s_cti" % (elm))
        line = date_obs + '\t' 
        for i in range(0, 4):
            try:
                atemp = re.split('\+\-', cti_data[i])
                vtest = float(atemp[0])
                if (vtest < 0.0) or (vtest > 10.0):
                    line = line + '-99999+-00000' + '\t'
                else:
                    line = line + cti_data[i] + '\t'
            except:
                line = line + '-99999+-00000' + '\t'
    
        line = line + str(obsid) + '\t' + date_end + '\t'  
        line = line + str(round(temperature,2)) + '\t\t' + str(round(sig,2))   + '\t' 
        line = line + str(round(tmin,2))        + '\t\t' +  str(round(tmax,2)) + '\t'
        line = line + str(int(stime)) + '\t' + str(int(stime2)) + '\n'

        if (int(ccdno) >= 0) and (int(ccdno) <= 9):
            out_dir = data_dir + '/Results/' + elm + '_ccd' + str(ccdno)
            with  open(out_dir, 'a') as fo:
                fo.write(line)
        
#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

#    def test_choose_fpt_files(self):
#
#        test_out = ['/data/mta/Script/ACIS/Focal/Short_term/data_2014_178_0351_178_1306']
#
#        fits      = './acisf52675_000N001_evt1.fits.gz'
#        dout      = pyfits.getdata(fits, 1)
#        time_list = dout.field('TIME')
#        date1     = min(time_list)
#        date2     = max(time_list)
#        
#        [fstart, fstop, file_list] = create_fp_list()
#        selected_fp_files = choose_fpt_files(date1, date2, fstart, fstop, file_list)
#
#        self.assertEquals(selected_fp_files, test_out)

#------------------------------------------------------------

#    def test_run_flt_pipe(self):
#
#        mcf.mk_empty_dir(temp_comp_area)
#        cmd = 'cp ./acisf52675_000N001_evt1.fits.gz ' + temp_comp_area
#        os.system(cmd)
#        cmd = 'gzip -d ' + temp_comp_area + '/*.gz'
#        os.system(cmd)
#        ifile = temp_comp_area + '/acisf52675_000N001_evt1.fits'
#        chk = run_flt_pipe(ifile)
#
#        self.assertEquals(chk, 0)

#------------------------------------------------------------

#        test_list = ['0', '52675', '0', '2014-06-27T04:21:09', '2014-06-27T08:31:19', ['5.390+-0.449', '6.721+-0.277', '-99999+-00000', '0.533+-0.229'], ['2.695+-0.036', '1.303+-0.033', '1.371+-0.028', '1.191+-0.023'], ['1.303+-0.050', '2.531+-0.024', '1.352+-0.033', '1.372+-0.036']]
#
#        full_list = find_cti_values_from_file()
#
#
#        self.assertEquals(full_list[0], test_list)


#--------------------------------------------------------------------

if __name__ == '__main__':

    create_cti_table()

