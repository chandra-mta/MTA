#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#   find_cron_records.py:reads cron job file and find newly recorded error message of each job  #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           Last Update: Oct 06, 2021                                                           #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import getpass
import socket
import random
import time
import Chandra.Time
import datetime
#
#--- reading directory list
#
path = '/data/mta/Script/Cron_check/house_keeping/dir_list_py'

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
#--- check whose account, and set a path to temp location
#
user = getpass.getuser()
user = user.strip()
#
#---- find host machine name
#
machine = socket.gethostname()
machine = machine.strip()
atemp   = re.split('\.', machine)
machine = atemp[0]
#
#--- possible machine names and user name lists
#
cpu_list     = ['colossus-v', 'c3po-v', 'r2d2-v', 'boba-v']
usr_list     = ['mta', 'cus']
cpu_usr_list = ['colossus-v_mta', 'r2d2-v_mta', 'r2d2-v_cus', 'c3po-v_mta', 'c3po-v_cus',\
                'boba-v_mta', 'boba-v_cus']
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- a list of error signatures
#
elist = ['error', 'cannot', 'permission denied', 'not found', 'failed', 'invalid',\
         'out of range', 'undefined']
#
#--- a list of none-real error signature (to be ignored)
#
nlist = ['cleartool', 'file exists', 'cannot remove', '\/usr\/bin\/du']

#------------------------------------------------------------------------------------------------------
#-- check_cron_errors: reads cron job file and find newly recorded error message of each job 
#------------------------------------------------------------------------------------------------------

def check_cron_records():
    """
    driving script: reads cron job file and find newly recorded error message of each job
    Input:      none but use cronjob listing for the <user> on <manchine>
                it also reads <house_keeping>/Records/<machine>_<user> for the past record
                the errors are read from /home/<user>/Logs/xxx.cron files
    Output: <house_keeping>/Records/<machine>_<user>            --- updated
            <house_keeping>/Records/<machine>_<user>_error_list --- a list of the errors
    """
#
#--- setup a record file name depending on the user and the machine
#
    cfile = house_keeping  + 'Records/' + machine + '_' + user
#
#--- if there is the past record, read it
#
    if os.path.isfile(cfile):

        [pname, ptime, psize] = get_prev_data(cfile)
#
#--- move the previous record 
#
        cmd = 'mv ' + cfile + ' ' + cfile + '~'
        os.system(cmd)
    
        lname = extract_cron_file_name()

        [cname, ctime, csize] = update_record_file(cfile, lname)
#
#--- find error messages and create error list
#
        compare_and_find(cname, ctime, csize, pname, ptime, psize)
#
#--- if this is the first time, just create a record file 
#
    else:
#
#--- crate a list of cron jobs
#
        lname = extract_cron_file_name()
#
#--- find the last update time and the file size of the files in the list
#
        [cname, ctime, csize] = update_record_file(cfile, lname)

#--------------------------------------------------------------------------------------------------
#-- update_record_file: for each cron job, find the last updated time and the current file length
#--------------------------------------------------------------------------------------------------

def update_record_file(cfile, lname):
    """
    for each cron job, find the last updated time and the current file length (in line #)
    Input:  cfile   --- output file name <house_keeping>/Records/<machine>_<user>
            lname   --- a list of cron jobs
    Output: cfile   --- an updated recorded file in <house_keeping>/Records/
            cname   --- a list of the current file names
            ctime   --- a list of the last updated time of each cron job
            csize   --- a list of the current file length in line # of each cron record file
    """
    cname = []
    ctime = []
    csize = []
    sline = ''
    for ent in lname:
        ifile  =  '/home/' + user + '/Logs/' + ent

        if os.path.isfile(ifile):
            time  = modification_date(ifile)
            fsize = file_length(ifile)

            cname.append(ent)
            ctime.append(time)
            csize.append(fsize)
    
            sline = sline +  ifile + ' : '+ str(time) + ' : ' + str(fsize) + '\n'

    if sline != '':
        with open(cfile, 'w') as fo:
            fo.write(sline)

    return [cname, ctime, csize]

#--------------------------------------------------------------------------------------------------
#-- get_prev_data: read the last recorded data from <hosue_keeping>/<machine>_<user>            ---
#--------------------------------------------------------------------------------------------------

def get_prev_data(cfile):
    """
    read the last recorded data from <hosue_keeping>/<machine>_<user>
    Input:  cfile   --- the input file name: <hosue_keeping>/<machine>_<user>
    Output: jname   --- a list of the cron job names
            jtime   --- a list of the last updated time of each cron job
            jsize   --- a list of the file size of each cron job
    """
    prev = read_data_file(cfile)

    jname = []
    jtime = []
    jsize = []
    for ent in prev:
        atemp = re.split(' : ', ent)
        try:
            val  = int(float(atemp[1]))
            val2 = int(float(atemp[2]))

            jname.append(atemp[0])
            jtime.append(val)
            jsize.append(val2)
        except:
            continue

    return [jname, jtime, jsize]

#--------------------------------------------------------------------------------------------------
#--- extract_cron_file_name: extract cron error message file names for the current user/machine ---
#--------------------------------------------------------------------------------------------------

def extract_cron_file_name():
    """
    extract cron error message file names for the current user/machine
    output: cron_file_name:   a list of cron file names (file names only no directory path)
    """
    try:
        cmd = 'crontab -l >' + zspace 
        os.system(cmd)
    
        data = read_data_file(zspace, remove=1)
    except:
       exit(1)

    cron_file_name = []
    for ent in data:
        m = re.search('Logs', ent)
        if m is not None and ent[0] != '#':
            try:
                atemp = re.split('Logs/', ent)
                btemp = re.split('2>&1',  atemp[1])
                cron  = btemp[0]
                cron  = cron.strip()
                cron_file_name.append(cron)
            except:
                continue
#
#--- removing duplicated lines
#
    cron_file_name = list(set(cron_file_name))

    return cron_file_name

#--------------------------------------------------------------------------------------------------
#-- modification_date: find the time of the file modified                                       ---
#--------------------------------------------------------------------------------------------------

def modification_date(filename):
    """
    find the time of the file modified
    http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
    Input:  filename    --- file name
    Output: time        --- time in seconds from 1998.1.1.
    """
    t     = os.path.getmtime(filename)
    ltime = datetime.datetime.fromtimestamp(t)

    return convert_time_format(ltime)

#--------------------------------------------------------------------------------------------------
#-- convert_time_format: convert time format from datetime format to seconds from 1998.1.1      ---
#--------------------------------------------------------------------------------------------------

def convert_time_format(ltime):
    """
    convert time format from datetime format to seconds from 1998.1.1
    Input:  ltime   --- time from datetime.datetime function
    Output: time    --- time in seconds from 1998.1.1
    """
    line = ltime.strftime("%Y%m%d%H%M%S")
    #stime = Chandra.Time.DateTime(line).secs

    stime = int(float(line))

    return stime

#--------------------------------------------------------------------------------------------------
#-- file_length: find a file length in line number                                               --
#--------------------------------------------------------------------------------------------------

def file_length(filename):
    """
    find a file length in line number
    Input:  filename    --- inputfile name
    Output: length      --- the file length in line number
    """
    data = read_data_file(filename)

    return len(data)

#-------------------------------------------------------------------------------------------------
#-- compare_and_find: compare the current cron job output to find new error messages
#--------------------------------------------------------------------------------------------------

def compare_and_find(cname, ctime, csize, pname, ptime, psize):
    """
    compare the current cron job output to that of the past and find new error messages
    (we assume that the cron files are accumulate so that any new potion indicated 
     by line # is the new record)
    Input:  cname   --- a list of the cron job record output file names
            ctime   --- a list of the latest update time of each cron job
            csize   --- a list of the lattest size of the cron job record output file
            pname   --- a list of the cron job record output file names in the last recorded file
            ptime   --- a list of the last update time of each cron job
            psize   --- a list of the last size of the cron job record output file
    Output: a file <house_keeping>/Records/<machine>_<user>_error_list
    """
    file_changed = []
    for i in range(0, len(cname)):
        for j in range(0, len(pname)):
            m  = re.search(cname[i], pname[j])
            if m is not None:
                if ctime[i] > ptime[j]:
                    if (str(csize[i]) <=  str(psize[j])):
#
#--- if the file size is same as before or smaller, we assme that the file is replaced
#
                        error = check_for_error(pname[j])

                        if error != 'na':
                            record_error(cname[i], ctime[i], error)
#
#--- if the file size is larger this round, then a new output from cron job 
#--- is appended to the old file
#
                    if str(csize[i]) > str(psize[j]):
                        error = check_for_error(pname[j], start = int(psize[j]))

                        if error != 'na':
                            record_error(cname[i], ctime[i], error)
                break

#-------------------------------------------------------------------------------------------------
#-- check_for_error: find errors reported in the file. check only newly appended part            --
#--------------------------------------------------------------------------------------------------

def check_for_error(ifile, start=0):
    """
    find errors reported in the file. check only newly appended part
    Input:  ifile   --- cron job output file name
            start   --- the last line of the last record. if this is not given, 
                        check from the beginning
    Output: error_list --- a list of error messages collected from the file
    """
    data = read_data_file(ifile)

    error_list = []
    for i in range(start, len(data)):
        ent  = data[i]
        lent = ent.lower()
#
#--- check the line contains error signatures
#
#
#--- ignore some idl specific error messages
#
        ms1 = re.search('arithmetic', lent)
        ms2 = re.search('underflow', lent)
        if (ms1 is not None) and (ms2 is not None):
            continue 
        ms3 = re.search('% Type conversion error', lent)
        if (ms3 is not None):
            continue
#
#--- ignore 'ls ' error
#
        ms4 = re.search('ls: cannot access', lent)
        if ms4 is not None:
            continue
#
#--- ignore 'image header' error
#
        ms5 = re.search('improper image header', lent)
        if ms5 is not None:
            continue
#
#--- ignore 'warning'
#
        ms6 = re.search('RuntimeWarning', lent)
        if ms6 is not None:
            continue
#
#--- ignore 'cannot stat' error
#
        ms7 = re.search('cannot stat', lent)
        if ms7 is not None:
            continue

        chk = 0
        for test in elist:

            m = re.search(test, lent)
            if m is not None:
                chk = 1
                break
#
#--- check whether they are non significant error. if so ignore
#
        if chk == 1:
            for test in nlist:
                m = re.search(test, lent)
                if m is  not None:
                    chk = 0
                    break

        if chk > 0:
            error_list.append(ent)
                
    error_list = list(set(error_list))

    if len(error_list) == 0:
        return 'na'
    else:
        return error_list

#-----------------------------------------------------------------------------------------------
#-- record_error: append the error messages in the error record file                         ---
#-----------------------------------------------------------------------------------------------

def record_error(fname, stime, error_list):
    """
    append the error messages in the error record file
    Input:  fname       --- a cron job output file name
            stime       --- the time of the last updated
            error_list  --- a list of the error detected from the file
    Output: <house_keeping>/Records/<machine>_<user>_error_list     
                        --- the file contains error messages
    """
    ofile = house_keeping + 'Records/' +  machine + '_' + user + '_error_list'

    with open(ofile, 'a') as fo:
        for ent in error_list:
            line = fname + ' : ' + str(stime) + ' : ' + ent + "\n"
            fo.write(line)

#--------------------------------------------------------------------------
#-- read_data_file: read a data file and create a data list  --
#--------------------------------------------------------------------------

def read_data_file(ifile, remove=0, ctype='r'):
    """
    read a data file and create a data list
    input:  ifile   --- input file name
    remove  --- if > 0, remove the file after reading it
    ctype   --- reading type such as 'r' or 'b'
    output: data--- a list of data
    """
#
#--- if a file specified does not exist, return an empty list
#
    if not os.path.isfile(ifile):
        return []
    
    try:
        with open(ifile, ctype) as f:
            data = [line.strip() for line in f.readlines()]
    except:
        with codecs.open(ifile, ctype, encoding='utf-8', errors='ignore') as f:
            data = [line.strip() for line in f.readlines()]
#
#--- if asked, remove the file after reading it
#
    if remove > 0:
        cmd = 'rm -rf ' + ifile
        os.system(cmd)
    
    return data

#------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    check_cron_records()

