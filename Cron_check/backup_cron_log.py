#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#           backup_cron_log.py: backup cron log files                                           #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           Last Update: Jul 09, 2021                                                           #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import getpass
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

import mta_common_functions     as mcf
#
#--- check whose account, and set a path to temp location
#
user = getpass.getuser()
user = user.strip()
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

month_ago = 86400 * 30
year_ago  = 86400 * 365
now       = int(Chandra.Time.DateTime().secs)

#------------------------------------------------------------------------------------------------------
#-- backup_cron_log: backup cron job logs; it also removes older log files                           --
#------------------------------------------------------------------------------------------------------

def backup_cron_log():
    """
    backup cron job logs; it also removes older log files
    input:  none but read from /home/<user>/Logs/<cron log name>
    output: /home/<user>/Logs/Past_logs/<cron log name>_<yyymmdd>

    Note: this must be run on all machines which create log files even if they share a log directory
    """
#
#--- set a log file directory, today's date, and a backup copy tail
#
    fpath = '/home/' + user + '/Logs/'
    mday  = int(time.strftime('%d', time.gmtime()))
    tail  = time.strftime('%Y%m%d', time.gmtime())
#
#--- find cron job under this machine
#
    out = extract_cron_file_name()
#
#--- go through each cron job
#
    for ent in out:
        atemp = re.split(':', ent)
        categ = atemp[0]
        ifile = atemp[1]
#
#--- cron jobs which run once a day or less are backed up once a month on first day of the month
#--- if the jobs run more than once a day, it is backed up once a day
#
        if categ == 0 and mday != 1:
            continue

        cfile = fpath + ifile
        dfile = fpath + 'Past_logs/' + ifile + '_'+ tail
        cmd   = 'mv ' + cfile + ' ' + dfile 
        os.system(cmd)
#
#--- remove older files; either older than a month or older than a year depending on cron type
#
        remove_old_file(ifile, categ)

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
    
        data = mcf.read_data_file(zspace, remove=1)
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

                atemp = re.split('\s+', ent)
                btemp = re.split(',', atemp[0])
                if len(btemp) > 1:
                    categ = 1
                else:
#
#--- if it is hourly cron job, add to daily backup
#
                    if atemp[1] == '*':
                        categ = 1
                    else:
                        categ = 0
                        
                line = str(categ) + ':' + cron
                cron_file_name.append(line)
            except:
                continue
#
#--- removing duplicated lines
#
    cron_file_name = list(set(cron_file_name))

    return cron_file_name

#--------------------------------------------------------------------------------------------------
#-- check_creation_time: find the file creation time in Chandra time                             --
#--------------------------------------------------------------------------------------------------

def check_creation_time(tfile):
    """
    find the file creation time in Chandra time
    input:  tfile   --- a file name
    output: stime   --- a creation time in Chandra time
    """
    out   = os.path.getctime(tfile)
    out   = str(datetime.datetime.fromtimestamp(out))
    atemp = re.split('\s+', out)
    out   = time.strftime('%Y:%j:00:00:00', time.strptime(atemp[0], '%Y-%m-%d'))
    stime = int(Chandra.Time.DateTime(out).secs)

    return stime

#--------------------------------------------------------------------------------------------------
#-- remove_old_file: remove old backup files                                                     --
#--------------------------------------------------------------------------------------------------

def remove_old_file(fname, categ):
    """
    remove old backup files
    input:  fname   --- a file name
            categ   --- a category of the file. 0: monthly backup / 1: daily backup
    output: none
    """
#
#--- set cutting date
#
    if categ == 1:
        cut = now - month_ago
    else:
        cut = now - year_ago
#
#--- find all backed up file names
#
    cmd  = 'ls /home/' + user + '/Logs/Past_logs/' + fname + '* > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    for ent in data:
#
#--- check the file creation time and if the file created before the cutting date, remove
#
        ctime = check_creation_time(ent)
        if ctime < cut:
            cmd = 'rm -rf ' + ent
            os.system(cmd)

#--------------------------------------------------------------------------------------------------
#-- remove_old_error_logs: removing older error log files                                       ---
#--------------------------------------------------------------------------------------------------

def remove_old_error_logs():
    """
    removing older error log files
    input:  none but read from <house_keeping>/Records/Past_errors/*
    output: none
    """

    cut   = now - year_ago

    cmd   = 'ls -d ' + house_keeping + '/Records/Past_errors/* > ' +  zspace
    os.system(cmd)
    data  = mcf.read_data_file(zspace, remove=1)
    for ent in data:
        try:
            ctime = check_creation_time(ent)
        except:
            continue

        if ctime < cut:
            cmd = 'rm -rf ' + ent
            os.system(cmd)


#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    backup_cron_log()
    remove_old_error_logs()



