#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#############################################################################
#                                                                           #
#       getnrt_control.py: run getnrt under ascds environment               #
#                                                                           #
#           Author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: May 22, 2019                                       #
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
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"


cmd = "/usr/bin/env PERL5LIB='' "
cmd = cmd + '/data/mta/www/mta_sim/Scripts/getdata'
bash(cmd, env=ascdsenv)

