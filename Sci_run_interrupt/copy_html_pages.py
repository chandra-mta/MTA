#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#   copy_html_pages.py: copying the contents to the secondary html location     #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string
#
#--- reading directory list
#

path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- mta common functions
#
import mta_common_functions             as mcf

#------------------------------------------------------------------------
#-- copy_html_pages: copying the contents to the secondary html location 
#------------------------------------------------------------------------

def copy_html_pages():
    """
    copying the contents to the secondary html location
    """

    cmd = 'cp ' + web_dir   + '*.html ' + web_dir2 + '.'
    os.system(cmd)

    cmd = 'cp ' + plot_dir  + '* ' + plot_dir2  + '.'
    os.system(cmd)

    cmd = 'cp ' + wdata_dir + '* ' + wdata_dir2 + '.'
    os.system(cmd)

    cmd = 'cp ' + html_dir  + '* ' + html_dir2  + '.'
    os.system(cmd)

    cmd = 'cp ' + stat_dir  + '* ' + stat_dir2  + '.'
    os.system(cmd)

    cmd = 'cp ' + goes_dir  + '* ' + goes_dir2  + '.'
    os.system(cmd)

    cmd = 'cp ' + xmm_dir   + '* ' + xmm_dir2   + '.'
    os.system(cmd)

    cmd = 'cp ' + note_dir  + '* ' + note_dir2  + '.'
    os.system(cmd)

    cmd = 'cp ' + intro_dir + '* ' + intro_dir2 + '.'
    os.system(cmd)
