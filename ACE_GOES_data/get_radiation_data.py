#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       get_radiation_data.py:  extract several radiation related data for trending plots       #
#                                                                                               #
#               author: t. isobe    (tisobe@cfa.harvard.edu)                                    #
#               originally written by B. Spitzbart (bspitzbart@cfa.harvard.edy)                 #
#                                                                                               #
#           this is a python version converted from idl version written by bs                   #
#                                                                                               #
#               last update: Nov 19, 2014                                                       #
#                                                                                               #
#################################################################################################

import os
import os.path
import time
import sys
import re
import string
import random
import operator
import math
import numpy
import smtplib
from ftplib import FTP
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_Rad/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()
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
#--- set ftp site
#
ftp_site = 'ftp.sec.noaa.gov'
#
#--- set admin email address
#
receiver = 'tisobe@cfa.harvard.edu'

#------------------------------------------------------------------------------------------------
#-- get_data: run three functions to extract data needed for radation related plots           ---
#------------------------------------------------------------------------------------------------

def get_data():
    """
    run three functions to extract data needed for radation related plots
    input:  none
    output: ace_data.txt, goes_data.txt, ephsca.fits, cti_data.txt
    """
    get_noaa_data()         #---- get data from noaa ftp site   ace_data.txt, goes_data.txt
#    get_sca_data()          #---- get data from dataskeer       ephsca.fits
    get_cti_data()          #---- get data from mta cti data    cti_data.txt
#
#--- check the last time the file is updated. if it is not updated for a while
#--- send out a warning eamil.
#
    check_last_update(ace_data)
    check_last_update(goes_data)

#------------------------------------------------------------------------------------------------
#-- get_noaa_data: run all ftp retrieval procedure from noaa site                             ---
#------------------------------------------------------------------------------------------------

def get_noaa_data():
    """
    run all ftp retrieval procedure from noaa site
    input:  none but read from data directory
    output: retrieved data
    """
#
#--- ACE data extraction/update
#
    pdir   = ace_dir                                #--- a directory where the past data are saved
    dfile  = ace_data                               #--- a data file location/name
    tail   = '_ace_epam_5m.txt'                     #--- a suffix of the data file name
    dir    = 'pub/lists/ace'                        #--- a directory where data are save at the ftp site
    outdir = ace_dir                                #--- a directory where ftped data are saved
    chk    = ftp_data(pdir,  tail, dir)
    if chk > 0:
        update_data(dfile, tail)
        cmd    = 'mv *' + tail + ' ' + outdir
        os.system(cmd)
#
#--- GOES data extraction/update
#
    pdir   = goes_dir
    dfile  = goes_data
    tail   = '_Gp_pchan_5m.txt'
    dir    = 'pub/lists/pchan'
    outdir = goes_dir 
    chk    = ftp_data(pdir, tail, dir)
    if chk > 0:
        update_data(dfile, tail)
        cmd    = 'mv *' + tail + ' ' + outdir
        os.system(cmd)

#
#--- this one is not updated since 2011; so don't run it
#
#    tdir = '/pub/lists/costello'
#    dlist = ['ace_pkp_15m.txt']
#    run_ftp(tdir, dlist)

#------------------------------------------------------------------------------------------------
#-- ftp_data: set up and run to use ftp to retrieve data                                       ---
#------------------------------------------------------------------------------------------------

def ftp_data(ldir, tail, fdir, outdir='./'):
    """
    set up and run to use ftp to retrieve data
    input:  ldir    --- a local data directory where the current data are saved
            tail    --- a suffix of the data file name
            fdir    --- a directory where the data are saved at the ftp site
            outdir  --- a directory where the retrieved data are saved; default: './'
    output: extracted files
            chk     --- the numbers of files extracted
    """
    
    [lyear, lmon, lday] = find_last_entry(ldir, tail)
    data_list           = make_data_list(lyear, lmon, lday, tail)

    chk  = run_ftp(fdir, data_list, outdir=outdir)
    return chk

#------------------------------------------------------------------------------------------------
#-- find_last_entry: for a given file name (with a full path), extract date information       ---
#------------------------------------------------------------------------------------------------

def find_last_entry(dir, tail):
    """
    for a given file name (with a full path), extract date information
    input:  dir     --- the name of directory where the data are kept
            tail    --- a suffix of the data file
    output: [year, mon, day]
    """
#
#--- find the last file created
#
    cmd = 'ls ' + dir + '/*' + tail + '| tail -1 > ' + zspace
    os.system(cmd)
    file = open(zspace, 'r').read()
    mcf.rm_file(zspace)
#
#--- extract time part. assume that the file end <tail> and the time part is prepended to it
#
    atemp = re.split('/', file)
    for ent in atemp:
        chk = re.search(tail, ent)
        if chk is not None:
            btemp = re.split('_', ent)
            ldate = btemp[0]
            break
#
#--- assume that the time is in the format of yyyymmdd, e.g. 20140515
#
    year = int(float(ldate[0:4]))
    mon  = int(float(ldate[4:6]))
    day  = int(float(ldate[6:8]))
    return [year, mon, day]

#------------------------------------------------------------------------------------------------
#-- make_data_list: make a data list from the last entry date to the most current data        ---
#------------------------------------------------------------------------------------------------

def make_data_list(year, mon, day, tail):
    """
    make a data list from the last entry date to the most current data
    input:  year    --- the year of the last entry
            mon     --- the month of the last entry
            day     --- the day of month of the last entry
            tail    --- the suffix of the data file 
    output  dlist   --- a list of data names
    """
#
#--- convert the date into seconds from 1998.1.1
#
    dst   = tcnv.convertDateToTime2(year, mon, day)
#
#--- find today's time
#
    today = tcnv.currentTime()
    cyear = today[0]
    cmon  = today[1]
    cday  = today[2]
    cdst  = tcnv.convertDateToTime2(cyear, cmon, cday)

    dlist = []
#
#--- check the current date is larger than the date indicated
#--- if so find how many days between and retrieve data for each day
#
    if cdst > dst:
        step = int(( cdst - dst)/86400)
        if step >= 1:
            head  = make_header(year, mon, day)
            name  = head + tail
            dlist.append(name)

        for i in range(2, step):
            sdate = int(cdst - 86400.0 * i)
            out   = tcnv.axTimeMTA(sdate)
            atemp = re.split(':', out)
            year  = int(atemp[0])
            ydate = int(atemp[1])

            [mon, day] = tcnv.changeYdateToMonDate(year, ydate)
            head  = make_header(year, mon, day)
            name  = head + tail
            dlist.append(name)

    return dlist

#------------------------------------------------------------------------------------------------
#-- make_header: create a file head from year, month, and day of the month                    ---
#------------------------------------------------------------------------------------------------

def make_header(year, mon, day):
    """
    create a file head from year, month, and day of the month
    input:  year    --- year in 4 digits, e.g. 2014
            mon     --- month
            day     --- day of the month
    output  header  --- header, e.g. 20140415 from 2014, 4, 15
    """

    syear = str(year)
    smon  = str(mon)
    sday  = str(day)
    if mon < 10:
        smon = '0' + smon

    if day < 10:
        sday = '0' + sday

    header = syear + smon + sday

    return header

#------------------------------------------------------------------------------------------------
#-- run_ftp: retrieve files from ftp site                                                     ---
#------------------------------------------------------------------------------------------------

def run_ftp(tdir, dlist, ftp_address = ftp_site, outdir = './'):
    """
    retrieve files from ftp site
    input:  tdir        --- location of ftp file under "ftp_site"
            dlist       --- a list of file names you want to retrieve
            ftp_address --- ftp address, default: ftp_site (see the top of this script)
            outdir      --- a directory name where you want to deposit files. default: './'
    output: retrieved files in outdir
            count       --- the number of files retrieved
    """
#
#--- open ftp connection
#
    ftp = FTP(ftp_address)
    ftp.login('anonymous', 'mta@cfa.harvard.edu')
    ftp.cwd(tdir)
#
#--- check though the data
#
    count = 0
    for file in dlist:
        local_file = os.path.join(outdir, file)
        try:
            ftp.retrbinary('RETR %s' %file, open(local_file, 'wb').write) 
            count += 1
        except:
            pass
#
#--- checking whether the retrieved file is empty, if so, just remove it
#
        if os.stat(local_file)[6] == 0:
            mcf.rm_file(local_file)
    ftp.quit()

    return count 

#------------------------------------------------------------------------------------------------
#-- update_data: update the data file with newly ftped data                                    --
#------------------------------------------------------------------------------------------------

def update_data(data_file, tail):
    """
    update the data file with newly ftped data
    input:  data_file   --- the data file name
            tail        --- the suffix of the ftped data file name
    output: data_fie    --- updated data file
    """
#
#--- read the current data
#
    f    = open(data_file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    [dst, last_d] = find_last_date(data)
#
#--- remove any lines appended at the end  which are not data
#
    last_part     = len(data) - last_d
    clean_file    = data[0:last_part]
#
#--- now get the extracted data and append the data
#
    cmd  = 'ls > ' + zspace
    os.system(cmd)

    f    = open(zspace, 'r')
    new  = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)
    selected = []
#
#-- select out only the appropriate files
#
    for ent in new:
        chk = re.search(tail, ent)
        if chk is not None:
            ent  = ent.strip()
            selected.append(ent)
#
#---  if there are actually new data, procceed
#
    if len(selected) > 0:
        selected.sort()
        for ent in selected:
            f    = open(ent, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()
    
            for line in data:
#
#--- remove commented parts
#
                if line[0] == '#':
                    continue
                else:
#
#--- compare the time stamp and append the data only when it is lager than the last entry
#
                    cst = find_date_from_line(line)
                    if cst > dst:
                        clean_file.append(line)
                        dst = cst
#
#--- save the current data file
#
        cmd = 'mv ' + data_file + ' ' + data_file + '~'
        os.system(cmd)
#
#--- and print out the updated data
#
        fo = open(data_file, 'w')
        for ent in clean_file:
            fo.write(ent)
            fo.write('\n')
        fo.close()

#------------------------------------------------------------------------------------------------
#-- find_last_date: find the time of the last entry                                            --
#------------------------------------------------------------------------------------------------

def find_last_date(data):
    """
    find the time of the last entry
    input:  data        --- data list
    output: [dst, ichk] --- dst:  time in seconds from 1998.1.1
                            ichk: the last line which has a correct data fomat
    """

    dst  = -999
    ichk = 0
    k    = 0
    while(k == 0):
        line = data[len(data) -ichk -1]
        dst  = find_date_from_line(line)
        if dst > 0:
            k    = 1
            break
        else:
            ichk += 1
            if ichk >= len(data):
                k = 1

    return [dst, ichk]

#------------------------------------------------------------------------------------------------
#-- find_date_from_line: find time from the data line                                         ---
#------------------------------------------------------------------------------------------------
    
def find_date_from_line(line):
    """
    find time from the data line 
    input:  line    --- data line. the line format must bei (for example):
                        2014 10 20  0120   56950   4800  9.10e-01  1.94e-01 ....
    output: dst     --- time in seconds from 1998.1.1
                        if the format does nto match, return -999
    """

    if line[0].isdigit():
        try:
            atemp = re.split('\s+', line)
            year  = int(float(atemp[0]))
            mon   = int(float(atemp[1]))
            day   = int(float(atemp[2]))
            hh    = atemp[3][0] + atemp[3][1]
            hh    = int(float(hh))
            mm    = atemp[3][2] + atemp[3][3]
            mm    = int(float(mm))
            dst   = tcnv.convertDateToTime2(year, mon, day, hours=hh , minutes=mm)
            return dst
        except:
            return -999
    else:
        return -999

#------------------------------------------------------------------------------------------------
#-- check_last_update: if a file is not updated for a while, send out a warning email         ---
#------------------------------------------------------------------------------------------------

def check_last_update(file, test=''):
    """
    check the file updated time and if it is not updated for a while, send out a warning
    input:  file    --- the name of file to be checked
            test    --- the test indicator, if it is test, test will be run
    output: email   --- a warning email to "reciever" (defined at the top of this script)
    """
#
#--- find the file updated time 
#
    stmp = os.stat(file)
    dst  = int(stmp.st_mtime)
#
#--- find the current time
#
    cdst = int(round(time.time()))
#
#--- if the data file is not updated more than 10 days, send out a warning email to admin
#
    diff  = cdst - dst
    if (test == '') and (diff >864000):
        send_email(receiver)
#
#--- this is a test return
#
    if test == 'test':
        return diff

#------------------------------------------------------------------------------------------------
#-- send_email: sending a warning email                                                        --
#------------------------------------------------------------------------------------------------

def send_email(receiver, test= ''):

    """
    sending a warning email
    input:  receiver    --- a receiver's email address
    output: email to the receiver
    """
#
#--- a real message when the problem happened
#
    sender = 'mta@cfa.harvard.edu'
    message = """From:DOSS - Monitoring and Trends Analysis <mta@cfa.harvard.edu>
Subject: Radiation Data Check Needed
    
Radiation data files are not updated for a while. Please check the script.
    
"""
#
#--- a test message
#
    message2 = """From:DOSS - Monitoring and Trends Analysis <mta@cfa.harvard.edu>
Subject: TEST TEST TEST
    
This is a test message sent from get_radiation_data.py.
    
"""
#
#--- now send email
#
    try:
        smtpObj = smtplib.SMTP('localhost')

        if test == 'test':
            smtpObj.sendmail(sender, receiver, message2)
        else:
            smtpObj.sendmail(sender, receiver, message)

        return "Successfully sent email"
    except:
        return "Error: unable to send email"

#------------------------------------------------------------------------------------------------
#-- get_sca_data: extract ephsca.fits data file from dataseeker                                --
#------------------------------------------------------------------------------------------------

def get_sca_data():
#
# NOTE: sca00 is not updated anymore and discoutinued. 
#
    """
    extract ephsca.fits data file from dataseeker
    input:  none
    output: ephsca.fits
    """
#
#--- create an empty "test" file
#
    mcf.rm_file('./test')
    fo = open('./test', 'w')
    fo.close()
#
#--- and run dataseeker
#
    cmd1 = '/usr/bin/env PERL5LIB='
    cmd2 = ' dataseeker.pl infile=test outfile=ephsca.fits search_crit="columns=_sca00_avg" '
    cmd3 = 'clobber=yes loginFile=/home/mta/loginfile'
    cmd = cmd1 + cmd2 + cmd3
    bash(cmd, env=ascdsenv)

    mcf.rm_file('./test')

    cmd = 'mv -f ephsca.fits /data/mta4/www/DAILY/mta_rad/.'
    os.system(cmd)

#------------------------------------------------------------------------------------------------
#-- get_cti_data: get cti data                                                                 --
#------------------------------------------------------------------------------------------------

def get_cti_data(test=''):
    """
    get cti data
    input:  none
    output: cti_data.txt
    """
#
#--- get all data
#
    cmd = 'cat /data/mta/Script/ACIS/CTI/Data/Det_Data_adjust/mn_ccd* > ' + zspace
    os.system(cmd)
#
#--- check the previous data file exists. if so, move to save.
#
    if os.path.isfile('./cti_data.txt') and test == '':
        cmd = 'mv -f  cti_data.txt cti_data.txt~'
        os.system(cmd)
#
#--- sort and select out data
#
    cmd = 'sort -u -k 1,1 ' + zspace + ' -o cti_data.txt'
    os.system(cmd)
    mcf.rm_file(zspace)
#
#--- change the permission
#
    cmd = 'chmod 755 cti_data.txt'
    os.system(cmd)
    cmd = 'mv -f ./cti_data.txt /data/mta4/www/DAILY/mta_rad/'
    os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_get_cti_data(self):

        get_cti_data(test = 'test')
        cmd  = 'ls > ' + zspace
        os.system(cmd)
        f    = open(zspace, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        mcf.rm_file(zspace)
        yes = 0
        for ent in data:
            if ent == 'cti_data.txt':
                yes = 1
                break

        self.assertEquals(yes, 1)

#------------------------------------------------------------

    def test_find_date_from_line(self):

        line = '2014 10 18  0000   56948      0  2.85e-01  1.33e-01  1.88e-02  1.84e-02  1.34e-02  3.79e-03 '
        dst = find_date_from_line(line)
        self.assertEquals(dst, 529977600)

        line = '#2014 10 18  0000   56948      0  2.85e-01  1.33e-01  1.88e-02  1.84e-02  1.34e-02  3.79e-03 '
        dst = find_date_from_line(line)
        self.assertEquals(dst, -999)

#------------------------------------------------------------

    def test_find_last_date(self):

        file = house_keeping + '/test_data.txt'
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        [dst, lpos]  = find_last_date(data)
        self.assertEquals(dst, 530236500)

#------------------------------------------------------------

    def test_run_ftp(self):
        tdir = '/pub/lists/costello'
        dlist = ['ace_pkp_15m.txt']
        run_ftp(tdir, dlist)

        if os.path.isfile('ace_pkp_15m.txt'):
            if os.stat('ace_pkp_15m.txt')[6] == 0:
                yes = 0
            else:
                yes = 1
                mcf.rm_file('ace_pkp_15m.txt')
        else:
            yes = 0

        self.assertEquals(yes, 1)

#------------------------------------------------------------

    def test_find_last_entry(self):

        pdir   = goes_dir
        tail   = '_Gp_pchan_5m.txt'
        [lyear, lmon, lday] = find_last_entry(pdir, tail)

        try:
            val = float(lyear)
            val = float(lmon)
            val = float(lday)
            yes = 1
        except:
            yes = 0

        self.assertEquals(yes, 1)

#------------------------------------------------------------

    def test_check_last_update(self):

        dst1 = check_last_update(ace_data,  test='test')

        dst2 = check_last_update(goes_data, test='test')

        yes = 0
        if dst1 > 864000 or dst2 > 864000:
            yes = 0
            print "WARNING: The file is not updated for a while!!"
        elif dst1 >= 0 and dst2 >= 0:
            yes = 1

        self.assertEquals(yes, 1)

#------------------------------------------------------------

    def test_send_email(self):

        message = send_email(receiver, test= 'test')

        self.assertEquals(message, 'Successfully sent email')

#---------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            del sys.argv[1]
            unittest.main()
        else:
            get_data()
    else:
        get_data()



