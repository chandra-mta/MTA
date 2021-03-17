#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#       getnrt_control.py: run getnrt under ascds environment               #
#                                                                           #
#           Author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: Mar 04, 2021                                       #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import multiprocessing
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"


def run():
    cmd = "/usr/bin/env PERL5LIB='' "
    cmd = cmd + '/data/mta/www/mta_sim/Scripts/getdata'
    bash(cmd, env=ascdsenv)

#----------------------------------------------------------------------

if __name__ == '__main__':
#
#--- start run as a process
#
    p = multiprocessing.Process(target=run, name="Run")
    p.start()
#
#--- wait tspan seconds for foo
#
    tspan = 2 * 86400.
    p.join(tspan)
#
#--- terminate process
#
    if p.is_alive():
        p.terminate()
        p.join()

