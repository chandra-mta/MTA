#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#       check_staled_process.py: check whether any staled process                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Oct 13, 2023                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import platform
import random
import Chandra.Time
import subprocess  
from subprocess import check_output
import getpass
#
#--- admin email addresses (list)
#
ADMIN = ['mtadude@cfa.harvard.edu']#hardcoded mtadude to be notification of email alert
#
#--- a list of processes that we don't mind to kill without checking 
#
KILL_LIST = ['update_rdb.py', 'run_filter_scripts.py', 'run_otg_proc.py', 'analyze_sim_data.py',\
             'copy_data_from_occ.py', 'plot_msid_latest_conda.py', 'MTA_limit_trends',
             'Disk_check/Scripts/update_html_page.py']

USER_LIST = ['mta','cus']
PS_FORMAT = ['user','pid','%cpu','%mem','vsz','stat','start','etime','time','cmd']#list of formatting choices for the ps call

#-----------------------------------------------------------------------------------------
#-- set_ldate: create date in <Mmm><dd> of 'day_ago'                                    --
#-----------------------------------------------------------------------------------------

def set_ldate(day_ago):
    """
    create date in <Mmm><dd> of 'day_ago'
    input:  day_ago --- the date of how many days ago to create; 1 --- one day ago
    ouput:  date    --- the data in <Mmm><dd>, e,g Jun05
    """
    y_day = Chandra.Time.DateTime().secs -  day_ago * 86400.0
    y_day = Chandra.Time.DateTime(y_day).date
    atemp = re.split('\.', y_day)
    y_day = atemp[0]
    out   = time.strftime('%m:%d', time.strptime(y_day, '%Y:%j:%H:%M:%S'))
    atemp = re.split(':', out)
    mon   = int(atemp[0])
    lmon  = change_month_format(mon)
    date  = lmon + atemp[1]

    return date
#
#--- set the past three day's dates in <Mmm><dd> format
#
DATES_LIST = [set_ldate(1), set_ldate(2), set_ldate(3)]

#-----------------------------------------------------------------------------------------
#-- check_staled_process: check whether any staled process                              --
#-----------------------------------------------------------------------------------------

def check_staled_process():
    """
    check whether any staled process
    input:  none
    output: email sent to admin if there are staled processes
    """
#--- find which cpu this one is
#
    out     = platform.node()
    atemp   = re.split('\.', out)
    machine = atemp[0]
#
#--- check currently running processes in the past three days
#
    '''
    for date in [aday1, aday2, aday3]:
#
#--- check mta first then cus
#
        if chk == 0:
            cmd = 'ps aux | grep python | grep -v -e grep -e ps | grep mta | grep ' + date + ' >' + zspace
            chk = 1
        else:
            cmd = 'ps aux | grep python | grep -v -e grep -e ps | grep mta | grep ' + date + ' >>' + zspace
        x = check_output(cmd, shell=True)

        cmd = 'ps aux | grep python | grep -v -e grep -e ps | grep cus | grep ' + date + ' >>' + zspace
        x = check_output(cmd, shell=True)
    '''
    #TODO change formating of ps aux
    cmd = f'ps -eo {",".join(PS_FORMAT)} | grep python | grep -v -e grep -e ps | grep -e {" -e ".join(USER_LIST)} | grep -e {" -e ".join(DATES_LIST)}'
    x = check_output(cmd,Shell=True)
    data = [i.strip() for i in x.decode().split("\n") if i != '']

    '''
    with open(zspace, 'r') as f:
            data = [line.strip() for line in f.readlines()]
    os.system(f"rm -rf {zspace}")
    '''
#
#--- if nothing is left, terminate the process
#
    if len(data) == 0:
        exit(1)
#
#--- check whether the processes running are in kill list. if so, just kill them
#
    s_list  = []
    temp_list  = ''                     #---- REMOVE!!
    for ent in data:
        chk = 0
        for s_name in KILL_LIST:
            mc = re.search(s_name, ent)
            if mc is not None:
                temp_list = temp_list + ent + '\n'  #---- REMOVE!!
                atemp = re.split('\s+', ent)
                pid   = atemp[PS_FORMAT.index('pid')]
                cmd   = 'kill -9 ' + str(pid)
                x = subprocess.run(cmd, shell=True)
                chk = 1
                break

        if chk == 0:
            s_list.append(ent)

##   REMOVE REMOVE REMOVE REMOVE      #############
    if temp_list != '':
        '''
        with open(zspace, 'w') as fx:
            fx.write(temp_list)
        cmd = 'cat ' + zspace + '|mailx -s "Subject: Killed Stale Process on ' + machine + '" ' + ' '.join(ADMIN)
        os.system(cmd)

        cmd = 'rm ' + zspace
        os.system(cmd)
        '''
        temp = f"The following processes were found stale and killed as of {time.strftime('%d/%m/%Y - %H:%M:%S',time.localtime())} \n"
        temp = temp + f"{' ; '.join(PS_FORMAT)}\n"
        templist = x + temp_list
        cmd = f'echo {temp_list} | mailx -s "Subject: Killed Stale Process on {machine}" {" ".join(ADMIN)}'
        os.system(cmd)
##   REMOVE REMOVE REMOVE REMOVE      #############
#
#--- if the processes which are not in the kill lists show up, report it to admin
#
    if len(s_list) > 0:
        if len(s_list) == 1:
            line = f"As of {time.strftime('%d/%m/%Y - %H:%M:%S',time.localtime())}, There is a staled process on {machine}:\n"
            line = line + f"{' ; '.join(PS_FORMAT)}\n"
        else:
            line = f"As of {time.strftime('%d/%m/%Y - %H:%M:%S',time.localtime())}, There are staled processes on {machine}:\n"
            line = line + f"{' ; '.join(PS_FORMAT)}\n"

        for ent in s_list:
            line = line + ent + '\n'

        line = line + '\nPlease check and, if it is necessary, remove it.\n'
        '''
        with  open(zspace, 'w') as fx:
            fx.write(line)

        cmd = 'cat ' + zspace + '|mailx -s "Subject: Stale Process on ' + machine + '" ' + ' '.join(ADMIN)
        os.system(cmd)
        
        cmd = 'rm ' + zspace
        os.system(cmd)
        '''
        cmd = f'echo {line} | mailx -s "Subject: Stale Process on {machine}" {" ".join(ADMIN)}'
        os.system(cmd)

#--------------------------------------------------------------------------
#-- change_month_format: convert month format between digit and three letter month 
#--------------------------------------------------------------------------

def change_month_format(month):
    """
    cnvert month format between digit and three letter month
    input:  month   --- either digit month or letter month
    oupupt: either digit month or letter month
    """
    m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',\
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#--- check whether the input is digit
#
    try:
        var = int(float(month))
        if (var < 1) or (var > 12):
            return 'NA'
        else:
            return m_list[var-1]
#
#--- if not, return month #
#
    except:
        mon = 'NA'
        var = month.lower()
        for k in range(0, 12):
            if var == m_list[k].lower():
                return k+1

        return mon

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

    check_staled_process()
    
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")
