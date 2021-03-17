#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       check_staled_process.py: check whether any staled process                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Oct 11, 2018                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import platform
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

m_list  = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#--- admin email address
#
admin   = 'tisobe@cfa.harvard.edu'

#-----------------------------------------------------------------------------------------
#-- check_staled_process: check whether any staled process                              --
#-----------------------------------------------------------------------------------------

def check_staled_process():
    """
    check whether any staled process
    input:  none
    output: email sent to admin if there are staled processes
    """
#
#--- find which cpu this one is
#
    out     = platform.node()
    atemp   = re.split('\.', out)
    machine = atemp[0]

    for proc in ['python', 'idl']:
#
#--- check currently running processes
#
        cmd     = 'ps aux | grep python >' + zspace
        os.system(cmd)
    
        f       = open(zspace, 'r')
        data    = [line.strip() for line in f.readlines()]
        f.close()
        cmd     = 'rm ' + zspace
        os.system(cmd)

        s_list  = []
        for ent in data:
            atemp = re.split('\s+', ent)
            if atemp[0] in ['mta', 'cus']:
                tt    = atemp[8]
                mc    = re.search(':', tt)
                if mc is None:
                    s_list.append(ent)

    if len(s_list) > 0:
        if len(s_list) == 1:
            line = 'There is a staled process on ' + machine  + ':\n ' 
        else:
            line = 'There are staled processes on ' + machine  + ':\n' 

        for ent in s_list:
            line = line + ent + '\n'

        line = line + '\nPlease check and, if it is necessary, remove it.\n'

        fx   = open(zspace, 'w')
        fx.write(line)
        fx.close()

        cmd = 'cat ' + zspace + '|mailx -s "Subject: Staled Process on ' + machine + '" ' + admin
        os.system(cmd)
        
        cmd = 'rm ' + zspace
        os.system(cmd)

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    check_staled_process()
    
