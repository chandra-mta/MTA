#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#       acis_gain_update_html.py:  update the main html page and data tables                        #
#                                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                                   #
#               Last update: Mar 02, 2021                                                           #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import time

path = '/data/mta/Script/ACIS/Gain/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts

#---------------------------------------------------------------------------------------------------
#--  create_display_data_table: create a readable data table for html page                       ---
#---------------------------------------------------------------------------------------------------

def create_display_data_table():

    """
    create a readable data table for html page
    Input: none, but read from <data_dir>/ccd<ccd>_<node>
    Output: <web_dir>/ccd<ccd>_<node>
    """
    for ccd in range(0, 10):
        for node in range(0, 4):
            ifile   = 'ccd' + str(ccd) + '_' +  str(node)
#
#--- read the original data file
#
            infile  = data_dir + ifile
            data    = mcf.read_data_file(infile)
#
#--- adding heading
#
            line    = "#\n#Date            Mn K alpha     Al K alpha     "
            line    = line + "Ti K alpha       Slope   Sigma   Int     Sigma\n#\n"
            for ent in data:
                atemp = re.split('\s+', ent)
#
#--- converting the date format from chandra time into <mon> <year> for html data display
#
                stime = int(atemp[0])
                out   = mcf.convert_date_format(stime, ifmt='chandra', ofmt='%Y:%m:%d')
                atemp = re.split(':', out)
                lmon  = mcf.change_month_format(atemp[1])
                ldate = lmon + ' ' + atemp[0]
                lout  = ent.replace(atemp[0], ldate)

                line  = line + lout + '\n'

            outfile = web_dir + 'Data/' + ifile
            with open(outfile, 'w') as fo:
                fo.write(line)

#---------------------------------------------------------------------------------------------------
#--- update_main_page: update the main html page (replacing updated date)                        ---
#---------------------------------------------------------------------------------------------------

def update_main_page():

    """
    update the main html page (replacing updated date)
    Input: none, but read from <house_keeping>/acis_gain.html
    Output: <web_dir>/acis_gain.html
    """
    line = house_keeping + '/acis_gain.html'
    with  open(line, 'r') as f:
        text = f.read()

    today = time.strftime('%d-%m-%Y', time.gmtime())

    text  = text.replace('#DATE#', today)

    ifile = web_dir + '/acis_gain.html'
    with open(ifile, 'w') as fo:
        fo.write(text)

#-------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_display_data_table()
    update_main_page()

