#!/proj/sot/ska3/flight/bin/python

import os
import sys
import re
import string
import random
import time

tail   = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(tail)

#--------------------------------------------------------------------------
#-- close_running_process: check whether a process is running and if it does, close the process
#--------------------------------------------------------------------------

def close_running_process(process, usr='mta'):
    """
    check whether a process is running and if it does, close the process
    input:  process --- process name such as <xxxxx>.py
            usr     --- user name
    output: none
    """
#
#--- check the process is running
#
    cmd = 'ps aux|grep ' + usr + ' |grep ' + process + '> ' + zspace
    os.system(cmd)

    with open(zspace) as f:
        data = [line.strip() for line in f.readlines()]

    cmd = 'rm -f ' + zspace
    os.system(cmd)
#
#--- if the process is running, kill it
#
    for ent in data:
        atemp = re.split('\s+', ent)
        pid   = atemp[1]
        cmd   = 'kill -9 ' + pid
        os.system(cmd)

#--------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 2:
        process = sys.argv[1]

        close_running_process(process)

    elif len(sys.argv) == 3:
        process = sys.argv[1]
        usr     = sys.argv[2]

        close_running_process(process, usr)
