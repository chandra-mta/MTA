#!/usr/bin/env /proj/sot/ska/bin/python

import sys
import os
import string
import re
import math
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv0 = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

script_dir = '/data/mta/Script/Temp/Test/'
sys.path.append(script_dir)
import extract_sim_data as esd

mta_dir = '/data/mta/Script/Python_script2.7/'
sys.path.append(mta_dir)
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

bindata_dir = '/data/mta/Script/Exposure/house_keeping/Info_dir/'
#
#--- a couple of things needed
#
dare   = mcf.get_val('.dare',   dir = bindata_dir, lst=1)
hakama = mcf.get_val('.hakama', dir = bindata_dir, lst=1)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

def run_script():

    for year in range(1999,2015):

        leap = tcnv.isLeapYear(year)
        if leap == 1:
            dend = 367
        else:
            dend = 366
        syear = str(year)
        lyear = syear[2] + syear[3]

        for yday in range(1,dend):
            if year == 1999 and yday < 239:
                continue

            if year == 2014 and yday > 316:
                break

            print "Year: " + str(year) + ' Ydate: ' + str(yday)

            [month, date] =tcnv.changeYdateToMonDate(year, yday)
            smonth = str(month)
            if month < 10:
                smonth = '0' + smonth
            sdate = str(date)
            if date < 10:
                sdate = '0' + sdate

            start = smonth + '/' + sdate + '/' + lyear + ',00:00:00'
            stop  = smonth + '/' + sdate + '/' + lyear + ',23:59:59'

            line  = 'operation = retrieve\n'
            line  = line + 'dataset = flight\n'
            line  = line + 'detector = telem\n'
            line  = line + 'level = raw\n'
            line  = line + 'tstart = ' + start + '\n'
            line  = line + 'tstop  = ' + stop  + '\n'
            line  = line + 'go\n'

            fo    = open(zspace, 'w')
            fo.write(line)
            fo.close()

            cmd1 = "/usr/bin/env PERL5LIB="
            cmd2 =  ' echo ' +  hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i' + zspace
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv0)
            mcf.rm_file(zspace)

            cmd = 'ls * > ' + zspace
            os.system(cmd)
            test = open(zspace, 'r').read()
            mc   = re.search('sto', test)
            if mc is not None:
                os.system('rm *log*')
                os.system('gzip -fd *gz')
                os.system('ls *.sto > xtmpnew')
                os.system('nice  ./filters_ccdm')
                esd.extract_sim_data()

            os.system('rm  -rf *.sto *.tl')

#---------------------------------------------------------------------------------------------

if __name__ == "__main__":

    run_script()


