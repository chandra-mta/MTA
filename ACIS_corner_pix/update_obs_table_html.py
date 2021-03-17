#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       # 
#       update_obs_table_html.py: update corner pixel html page                         #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 03, 2021                                                       #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import time 
import Chandra.Time
import random
#
#--- reading directory list
#
path = '/data/mta/Script/Corner_pix/Scripts/house_keeping/dir_list'

with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
#
#--- temporary saving file
#
tail = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(tail)

#-------------------------------------------------------------------------------
#-- update_obs_table_html: update corner pixel html page                      --
#-------------------------------------------------------------------------------

def update_obs_table_html():
    """
    update corner pixel html page
    input:  none
    output: <web_page>/cpix.html
    """
#
#--- get the last 2 weeks of acis observations
#
    obsid_list = get_recent_obsid()
#
#--- collect plot names related to each obsid and create a table entry line
#
    sline = ''
    if len(obsid_list) > 0:
        for obsid in obsid_list:
            olinks = get_plot_list(obsid)
    
            if olinks == 'NA':
                continue
    
            sline = sline + '<tr>\n'
            sline = sline + '<th>' + str(obsid) + '</th>\n'
            sline = sline + olinks
            sline = sline + '</tr>\n\n'
#
#--- read a html page template
#
    ifile = house_keeping + 'cpix.html'
    with open(ifile, 'r') as f:
        template = f.read()
#
#--- find today's date
#
    update = mcf.today_date_display()
#
#--- relpace table and today's date
#
    template = template.replace('#TABLE#',  sline)
    template = template.replace('#UPDATE#', update)
#
#--- update the html page
#
    outfile = web_dir + 'cpix.html'

    with open(outfile, 'w') as fo:
        fo.write(template)
#
#--- compress older plot files
#
    zip_old_plot_file()

#-------------------------------------------------------------------------------
#-- get_recent_obsid: make a list of recent acis observation                  --
#-------------------------------------------------------------------------------

def get_recent_obsid():
    """
    make a list of recent acis observation
    input: none
    output: a_list  --- a list of obsid
    """
#
#--- extract a list of the last two weeks of acis observations
#
    stop   = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    stop   = Chandra.Time.DateTime(stop).secs
    start  = stop - 86400 * 14

    a_list = make_obsid_list(start, stop)

    return a_list

#-------------------------------------------------------------------------------
#-- get_plot_list: create html table entry for the obsid                      --
#-------------------------------------------------------------------------------

def get_plot_list(obsid):
    """
    create html table entry for the obsid
    input:  obsid   --- obsid
    output: sline   --- a <td>...</td> line for the obsid
    """
#
#--- find plot directory related to the obsid exists
#
    dpath = 'Plots/Ind_Plots/acisf' + str(obsid) + '_plots/'
    test  = web_dir + dpath
    if os.path.isdir(test):
#
#--- if so, check which plots exit, and create entry for the line
#
        head  = 'acisf' + str(obsid)
        sline = ''
        for tail in ['ahist', 'hist']:
            achk = 0
            for ccd in ['I2', 'I3', 'S2', 'S3']:
#
#--- link to histogram plots
#
                name = dpath + head + '_' + ccd + '_' + tail + '.png'
                test = web_dir + name

                if os.path.isfile(test):
                    line = '<td><a href="javascript:WindowOpener2(\'' + name +'\')">'
                    line = line + ccd + tail + '</a></td>\n'
                    achk += 1

                else:
                    line = '<td>No Plot</td>\n'

                sline = sline + line
#
#--- link to frame trend plots
#
            if tail == 'ahist':
                name = dpath + head + '_norm_acp.png'
                np   = 'acp'
            else:
                name = dpath + head + '_norm_cp.png'
                np   = 'pc'
#
#--- if it is ahist and no hist plot is created, no link to acp plot either.
#
            if achk ==0 and np == 'acp':
                line = '<td>acp</td>\n'
            else:
                line  = '<td><a href="javascript:WindowOpener2(\'' + name +'\')">'
                line  = line + np + '</a></td>\n'

            sline = sline + line
        return sline

    else:
        return 'NA'

#-------------------------------------------------------------------------------
#-- zip_old_plot_file: compress older plots files                             --
#-------------------------------------------------------------------------------

def zip_old_plot_file(a1=30, a2=60):
    """
    compress older plots files
    input:  a1  --- up to how many days ago from today; default 30 days
            a2  --- starting from how many days ago from today default 60 days
    output: none, but compressed png files 
    """

    today  = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    today  = Chandra.Time.DateTime(today).secs
    stop   = today - 86400 * a1
    start  = today - 86400 * a2

    a_list = make_obsid_list(start, stop)

    for obsid in a_list:

        cdir = plot_dir + 'Ind_Plots/acisf' + str(obsid) + '_plot'
        if os.path.isdir(cdir):
            cmd = 'gzip -f ' +  cdir + '/*.png'
            os.system(cmd)

#-------------------------------------------------------------------------------
#-- make_obsid_list: create a list of acis observation for a given period     --
#-------------------------------------------------------------------------------

def make_obsid_list(start, stop):
    """
    create a list of acis observation for a given period
    input:  start   --- starting time
            stop    --- stopping time
    output: a_lis   --- a list of obsids
    """
    line = 'operation=browse\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=evt1\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'

    out  = mcf.run_arc5gl_process(line)
#
#--- save obsids
#
    a_list = []
    if len(out) > 0:
        for ent in out:
            atemp = re.split('acisf', ent)
            btemp = re.split('_', atemp[1])
            obsid = btemp[0]
#
#--- make sure that obsid is numeric
#
            try:
                chk = float(obsid)
            except:
                continue

            a_list.append(obsid)

    return a_list

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    update_obs_table_html()
