#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

import sys
import os
import string
import re
import math
import random
import time
script_dir = '/data/mta/Script/SIM_extract/'
sys.path.append(script_dir)
import extract_sim_data          as esd

mta_dir = '/data/mta/Script/Python3.8/MTA/'
sys.path.append(mta_dir)
import mta_common_functions       as mcf 
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

def run_script():

    for year in range(1999,2015):

        if mcf.is_leapyear(year):
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

            lyday = str(yday)
            if yday < 10:
                lyday = '00' + lyday
            elif yday < 100:
                lyday = '0'  + lyday
            dtime = str(year) + ':' + lyday

            start = dtime + ':00:00:00'
            stop  = dtime + ':23:59:59'

            line  = 'operation = retrieve\n'
            line  = line + 'dataset = flight\n'
            line  = line + 'detector = telem\n'
            line  = line + 'level = raw\n'
            line  = line + 'tstart = ' + start + '\n'
            line  = line + 'tstop  = ' + stop  + '\n'
            line  = line + 'go\n'

            out   = mcf.run_arc5gl_process(line)

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


