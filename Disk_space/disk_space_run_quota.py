#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       disk_space_run_quota.py: check of home directory quota                  # 
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Mar 04, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time
import socket
import getpass
import random
#
#--- reading directory list
#
path = '/data/mta/Script/Disk_check/house_keeping/dir_list_py'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions_short as mcf
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------------
#-- disk_space_run_quota: check the quota of home directory                                   --
#-----------------------------------------------------------------------------------------------

def disk_space_run_quota():
    """
    check the quota of home directory
    input:  none
    output: <data_out>/quota_<user name>. time and  rate of the space used against the limit
            email --- if the quota reached above 90% of the limit, 
                      the warning email will be sent out
    """
#
#--- find the quota information
#
    cmd  = 'quota -A > ' + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    out  = re.split('\s+', data[-1].strip())
#
#--- current usage
#
    vnow  = out[0]
#
#--- if the value is with 'M' change the value in millions
#
    mc   = re.search('M', vnow)
    if mc is not None:
        vnow = vnow.replace('M', '000000')
    vnow = float(vnow)
#
#--- find the limit quota
#
    dmax = out[1]
    mc   = re.search('M', dmax)
    if mc is not None:
        dmax = dmax.replace('M', '000000')
    dmax = float(dmax)
#
#--- check the ratio
#
    ratio   = vnow / dmax
    cratio  = '%2.3f' % round(ratio, 3)
#
#--- record the value: <time>:<ratio>
#
    stday   = time.strftime("%Y:%j", time.gmtime())
    line    = stday + ':' + cratio + '\n'
#
#--- find the user (usually, mta or cus)
#
    user    = getpass.getuser()
    outname = data_out + 'quota_' + user

    with  open(outname, 'a') as fo:
        fo.write(line)
#
#--- if the quota exceeded 90% of the limit, send out a warning email
#
    if ratio > 0.9:
        mline = '/home/' + user + ': the quota is exceeded 90% level.\n\n'
        for ent in data:
            mline = mline + ent + '\n'

        with open(zspace, 'w') as fo:
            fo.write(mline)

        cmd = 'cat ' + zspace + ' |mailx -s\"Subject: Disk Quota Warning\n\" '
        cmd = cmd    + 'isobe\@head.cfa.harvard.edu'
        os.system(cmd)

        mcf.rm_files(zspace)

#--------------------------------------------------------------------

if __name__ == '__main__':

    disk_space_run_quota()
