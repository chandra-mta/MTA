#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#           create_gyro_drift_ind_page.py: create gryro drift movment html pages                #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Mar 09, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/Gyro/Scripts/house_keeping/dir_list'

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
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
catg_list    = ['roll', 'pitch', 'yaw']

#---------------------------------------------------------------------------------------
#-- create_gyro_drift_ind_page: create gryro drift movment html pages                          --
#---------------------------------------------------------------------------------------

def create_gyro_drift_ind_page():
    """
    create gryro drift movment html pages
    input:  none
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<catg>_<grating>_<action>.html
    """
#
#--- read template
#
    tname    = house_keeping + 'drift_plot_template'
    with open(tname, 'r') as f:
        template = f.read()
#
#--- go through all data set to create several sub html pages related to indivisual fitting resluts
#
    for catg in catg_list:
        for grating in ['hetg', 'letg']:
            for action in ['insr', 'retr']:
                ifile = data_dir + 'gyro_drift_' + catg + '_' + grating + '_' + action
                data  = mcf.read_data_file(ifile)
                data  = mcf.separate_data_to_arrays(data, com_out='#')

                create_html_page_for_movement(catg, grating, action, data, template)

#---------------------------------------------------------------------------------------
#-- create_html_page_for_movement: create a html page for given category, grating, and movment 
#---------------------------------------------------------------------------------------

def create_html_page_for_movement(catg, grating, action, data, template):
    """
    create a html page for given category, grating, and movment
    input:  catg        --- category (roll, pitch, yaw)
            grating     --- grating
            action      --- insr or retr
            data        --- a list of lists of data
            template    --- the html tamplate of the pages
    output: <web_dir>/Individual_plots/<GRATING>_<ACTION>/<catg>_<grating>_<action>.html
    """

    line = ''
    for k in range(0, len(data[0])):
        time  = data[0][k]
        dplot = './' + str(int(time)) +  '/deviation_'  + catg + '.png'
        gplot = './' + str(int(time)) +  '/gyro_drift_' + catg + '.png'

        line  = line + create_data_row(data, k, dplot, gplot)
#
#--- insert the data
#
    template = template.replace('#CATG#',  catg.upper())
    template = template.replace('#CATGL#', catg.lower())
    template = template.replace('#GRAT#',  grating.upper())
    template = template.replace('#ACT#',   action.upper())
    template = template.replace('#TABLE#', line)

    if action == 'insr':
        template = template.replace('#ACT2#',   'insertion')
    elif action == 'retr':
        template = template.replace('#ACT2#',   'retraction')

#
#--- output file name
#
    outdir  = web_dir + 'Individual_plots/' + grating.upper() + '_' + action.upper() + '/'
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)

    outname = outdir  +  catg.lower() + '_' + grating.lower() + '_' + action.lower() +  '.html'
#
#--- print out the result
#
    with  open(outname, 'w') as fo:
        fo.write(template)

#---------------------------------------------------------------------------------------
#-- create_data_row: create a table entry of given data                               --
#---------------------------------------------------------------------------------------

def create_data_row(data, k, dplot, gplot):
    """
    create a table entry of given data
    input:  data    --- a list of lists of the data
            k       --- the position of the data row
            dplot   --- the name of the derivative plot
            gplot   --- the name of the gyro drift plot
    output: line    --- the table entry
    """
    results = create_result_table(data, k)
    stime   = data[0][k]
    ltime   = Chandra.Time.DateTime(stime).date

    line    = '<tr>\n'

    line    = line + '<th style="font-size:95%;">' + ltime + '<br />(' +  str(stime) + ')</th>\n'

    line    = line + '<th>\n'
    line    = line + '<a href="javascript:WindowOpener(\'' + gplot + '\')">\n'
    line    = line + '<img src="' + gplot + '" width=90%">\n'
    line    = line + '</a></th>\n'

    line    = line + '<th>\n'
    line    = line + '<a href="javascript:WindowOpener(\'' + dplot + '\')">\n'
    line    = line + '<img src="' + dplot + '" width=90%">\n'
    line    = line + '</a></th>\n'

    line    = line + '<td>' + results + '</td>\n'
    line    = line + '</tr>\n'

    return line

#---------------------------------------------------------------------------------------
#-- create_result_table: create the result table                                      --
#---------------------------------------------------------------------------------------

def create_result_table(data, k):
    """
    create the result table
    input:  data    --- a list of lists of fitting results
            k       --- the position of the data row
    output: line    --- a html element
    """
#
#--- create data table
#
    line = '<table broder=0>\n'
    line = line + '<tr><th style="text-align:left;">Before: </th><td>'         
    line = line + str(data[1][k])  + '</td></tr>\n'

    line = line + '<tr><th style="text-align:left;">During: </th><td>'         
    line = line + str(data[2][k])  + '</td></tr>\n'

    line = line + '<tr><th style="text-align:left;">After:  </th><td>'         
    line = line + str(data[3][k])  + '</td></tr>\n'

    line = line + '<tr><th style="text-align:left;">Before/During:</th><td>  ' 
    line = line + str(data[4][k])  + '</td></tr>\n'

    line = line + '<tr><th style="text-align:left;">After/During: </th><td>  ' 
    line = line + str(data[5][k])  + '</td></tr>\n'

    line = line + '<tr><th style="text-align:left;">Before/After: </th><td>  ' 
    line = line + str(data[6][k])  + '</td></tr>\n'

    line = line + '<tr><th>Duration:     </th><td>  ' + str(data[7][k])  + ' sec</td></tr>\n'
    line = line + '</table>\n'

    return line

#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_gyro_drift_ind_page()
