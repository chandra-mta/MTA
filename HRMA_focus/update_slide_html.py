#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#           update_slide_html.py: update html pages shown yearly data plots                     #
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
import random
import operator
import math
import numpy
import astropy.io.fits  as pyfits
import time
#
#--- reading directory list
#
path = '/data/mta/Script/Hrma_src/Scripts/house_keeping/dir_list'

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
zspace   = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- create_iframe_entry: update html pages shown yearly data plots                      --
#-----------------------------------------------------------------------------------------

def create_iframe_entry():
    """
    update html pages shown yearly data plots --- this is used as slide input of iframe
    input:  none, but use <house_keeping>/template.html
    output: <web_dir>/<category>/<inst>_dist_<category>_year.html
    """

    year   = int(float(time.strftime("%Y", time.gmtime())))
    templ  = house_keeping + 'template.html'
    with  open(templ, 'r') as f:
        thtml  = f.read()

    for category in ['Psf', 'Radius', 'Rotation', 'Roundness', 'Snr']:

        for inst in ['Acis_i', 'Acis_s',  'Hrc_i', 'Hrc_s']:

            head    = inst.lower() + '_dist_' + category.lower()
            savedir = web_dir + category

            cmd     = 'mkdir -p ' + savedir
            os.system(cmd)

            outname = savedir + '/' +  inst.lower() + '_dist_' + category.lower() + '_year.html'

            create_slide_window(year, thtml, category, inst, head,  outname)


#-----------------------------------------------------------------------------------------
#-- create_slide_window: create the html page based on the template                     --
#-----------------------------------------------------------------------------------------

def create_slide_window(year, thtml, category, inst, head,  outname):
    """
    create the html page based on the template
    input:  year        --- year
            thtml       --- the template of the page
            category    --- category of the data (e.g. Psf)
            inst        --- instrument (e.g., Acis_i)
            head        --- header part of the plot name
            outname     --- html page name
    output: outname
    """

    line = ''
    for year in range(1999, year+1):
        line = line + '<td><b>' + str(year) + '</b><br />'
        line = line + '<img src="../Plots/' + category + '/' + inst 
        line = line + '/' + head + '_' + str(year) + '.png" width=650px></td>\n'

    width = 650 * (year - 1999)
    thtml = thtml.replace('#WIDTH#', str(width))
    thtml = thtml.replace('#TABLE#', line)

    with open(outname, 'w') as fo:
        fo.write(thtml)

#-----------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_iframe_entry()
