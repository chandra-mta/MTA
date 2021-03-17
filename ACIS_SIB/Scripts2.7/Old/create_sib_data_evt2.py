#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           create_sib_data_evt2.py: create sib data for report (Lev 2)                                     #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Sep 18, 2015                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import unittest
import time
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/Lev1/Reportdir/'
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append path to a private folders
#
#sys.path.append(base_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
    
#
#--- directory path
#
s_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/'

#-----------------------------------------------------------------------------------------
#-- create_sib_data_evt2: create sib data for report (Lev 2)                            --
#-----------------------------------------------------------------------------------------

def create_sib_data_evt2():
    """
    """
#
#--- find today's date information (in local time)
#
    tlist = time.localtime()
#
#--- set data time interval to the 1st of the last month to the 1st of this month
#
    eyear  = tlist[0]
    emon   = tlist[1]

    tline = str(eyear) + ' ' +str(emon) + ' 1'
    tlist = time.strptime(tline, "%Y %m %d")
    eyday = tlist[7]

    end   = str(eyear) + ':' + str(eyday) + ':00:00:00'

    syear  = eyear
    smon   = emon - 1
    if smon < 1:
        syear -= 1
        smon   = 12

    tline = str(syear) + ' ' +str(smon) + ' 1'
    tlist = time.strptime(tline, "%Y %m %d")
    syday = tlist[7]

    begin = str(syear) + ':' + str(syday) + ':00:00:00'
        
#
#--- correct factor
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' perl ' + s_dir + 'Lev2/correct_factor.perl'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#---   exclude all high count rate observations
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' perl  ' + s_dir + 'Sib_corr/find_excess_file.perl'
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- combine all data
#
    cmd1 = "/usr/bin/env PERL5LIB="
    cmd2 = ' perl  ' + s_dir + 'Sib_corr/sib_corr_comb.perl ' + begin + ' ' + end 
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- make data directory
#
    lmon = str(smon)
    if smon < 10:
        lmon = '0' + lmon

    dname = '/data/mta/Script/ACIS/SIB/Lev2/Data/Data_' + str(syear) + '_' + lmon
    cmd   = 'mkdir ' + dname
    os.system(cmd)

    cmd   = 'mv ' + s_dir + 'Lev2/Data/* ' + dname
    os.system(cmd)
#
#--- plot data
#
    cmd = s_dir + 'Scripts/ccd_comb_plot.py lev2'
    os.system(cmd)
    cmd = s_dir + 'Scripts/update_html.py   lev2'
    os.system(cmd)
#
#--- clean updata
#
    lmon = tcnv.changeMonthFormat(smon)
    lmon = lmon.lower()

    cmd = 'mv ' + s_dir + 'Lev2/Outdir/lres ' 
    cmd = cmd   + s_dir + 'Lev2/Outdir/lres_' + lmon +str(syear)
    #os.system(cmd)

    cmd = 'rm -rf ' + s_dir + 'Lev2/Outdir/ctirm_dir'
    #os.system(cmd)
    cmd = 'rm -rf ' + s_dir + 'Lev2/Outdir/filtered'
    #os.system(cmd)
    cmd = 'rm -rf ' + s_dir + 'Lev2/Outdir/hres'
    #os.system(cmd)

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    create_sib_data_evt2()

