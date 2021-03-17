#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#      send_error_list_email.py: read the current error lists and send out email        #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           Last Update: Mar 03, 2021                                                   #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import getpass
import socket
import random
import time
import datetime
import Chandra.Time
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
#--- import several functions
#
import mta_common_functions as mcf   #---- contains other functions commonly used in MTA scripts
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
#
#--- possible machine names and user name lists
#
cpu_list     = ['colossus-v', 'c3po-v', 'r2d2-v', 'boba-v']
usr_list     = ['mta', 'cus']
cpu_usr_list = ['colossus-v_mta', 'r2d2-v_mta', 'r2d2-v_cus', 'c3po-v_mta',\
                'c3po-v_cus', 'boba-v_mta', 'boba-v_cus']
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

email_list = ['tisobe@cfa.harvard.edu','swolk@head.cfa.harvard.edu',\
              'msobolewska@cfa.harvard.edu','lina.pulgarin-duque@cfa.harvard.edu']

#--------------------------------------------------------------------------------------------------
#-- report_error: read errors from <cup_usr_list>_error_list, sort it out, clean, and send out email
#--------------------------------------------------------------------------------------------------

def report_error():
    """
    read errors from <cup_usr_list>_error_list, sort it out, clean, and send out email
    Input:  none but read from <cup_usr_list>_error_list
    Output: email sent out
    """
#
#--- find the current time
#
    out = time.strftime('%Y:%m:%d', time.gmtime())
    [year, mon, day] = re.split(':', out)
#
#--- set cutting date for the report
#
    out = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    cut = Chandra.Time.DateTime(out).secs - 1.5 * 86400.0
#
#--- create surfix for files which will be saved in Past_errors directory
#
    smon = mcf.add_leading_zero(mon)
    sday = mcf.add_leading_zero(day, dlen=3)
    tail = str(year) + smon + sday

    for tag in cpu_usr_list:
        efile = house_keeping + 'Records/' + tag + '_error_list'
        pfile = house_keeping + 'Records/Past_errors/' + tag + '_error_list_' + tail
        prev_line = ''

        if os.path.isfile(efile):
#
#--- read error messages from the file
#
            data = mcf.read_data_file(efile)
#
#--- sort the data so that we can correct messages to each cron job together
#
            data.sort()

            task_list = []
            time_list = []
            mssg_list = []
            for ent in data:
                atemp = re.split(' : ' , ent)

                otime = int(float(atemp[1]))
                dtime = mcf.convert_date_format(str(otime), ifmt='%Y%m%d%H%M%S', ofmt='%Y:%j:%H:%M:%S')
#
#--- if the error is more than <cut> day old, ignore
#
                stime = Chandra.Time.DateTime(dtime).secs
                if stime < cut:
                    continue

                task_list.append(atemp[0])
                time_list.append(dtime)

                mssg_list.append(atemp[2])
#
#--- write out cron job name
#
            cname  = task_list[0]
            sline  = '\n\n' + cname + '\n____________________\n\n'

            for i in range(1, len(mssg_list)):
                if task_list[i] != cname:
                    cname = task_list[i]
                    sline  =  sline + '\n\n' + cname + '\n____________________\n\n'
#
#--- create each line. if it is exactly same as one line before, skip it
#
                line = time_list[i] + ' : ' + mssg_list[i] + '\n'

                if line != prev_line:
                    sline = sline + line
                prev_line = line

            with open(zspace, 'w') as fo:
                fo.write(sline)
#
#--- send email out
#
            send_mail(tag, email_list)
#
#--- move the error list to Past_errors directory
#
            if os.path.isfile(efile):                   #--- 03/06/19
                cmd = 'mv ' + efile + ' ' + pfile
                os.system(cmd)

#--------------------------------------------------------------------------------------------------
#-- send_mail: sending email out                                                                ---
#--------------------------------------------------------------------------------------------------

def send_mail(tag, email_list):
    """
    sending email out
    Input:  tag     --- user and machine name in the form of c3po-v_mat
            email_list  --- a list of email address
    Output: email sent out
    """
    if os.path.isfile(zspace):
        if os.stat(zspace).st_size > 0:

            atemp = re.split('_', tag)

            for email_address in email_list:
                cmd = 'cat ' + zspace + ' | mailx -s "Subject: Cron Error : ' 
                cmd = cmd    + atemp[1] + ' on ' + atemp[0] + '"  ' + email_address
                os.system(cmd)

    mcf.rm_files(zspace)

#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    report_error()

