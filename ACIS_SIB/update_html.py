#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#   update_html.py: update the main sib page (sib_main.html) and update modified dates for      #
#                   a few sub html pages                                                        #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           Last Update: Mar 03, 2021                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import numpy
import time
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
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
import sib_corr_functions   as scf

#-------------------------------------------------------------------------------
#-- update_html: update the main html page (sib_main.html)                    --
#-------------------------------------------------------------------------------

def update_html():
    """
    update the main html page (sib_main.html)
    Input: none, but read a part from <house_keeping>/sim_head_part
    Output: <web_dir>/sib_main.html
    """
#
#--- find today's date, and set a few thing needed to set output directory and file name
#
    out    = time.strftime('%Y:%m', time.gmtime())
    [year, mon] = re.split(':', out)
    year   = int(float(year))
    mon    = int(float(mon))
    syear  = str(year)
    smonth = mcf.add_leading_zero(mon)

    lyear = year 
    lmon  = mon - 1
    if lmon < 1:
        lmon   = 12
        lyear -= 1

    slyear  = str(lyear)
    slmonth = mcf.add_leading_zero(lmon)
#
#--- read the head part from the house_keeping
#
    cmd = 'cp ' + house_keeping + '/sib_head_part ' + web_dir + '/sib_main.html'
    os.system(cmd)
#
#--- add the rest
#
    sline = ''
    for iyear in range(year, 1999, -1):
        sline = sline + "<tr>\n"

        if iyear == year:
            sline = sline + '<th>' + syear  + '</th><td>---</td>\n'
        else:
            sline = sline + '<th>' + str(iyear) + '</th><td><a href="./Plots/Plot_' 
            sline = sline   + str(iyear) + '/year.html">' + str(iyear) + '</a></td>\n'

        for imonth in range(1, 13):
            simonth = mcf.add_leading_zero(imonth)

            if (iyear == year) and (imonth >= mon):
                sline = sline + '<td>' + simonth + '</td>\n'
            else:
                sline = sline + '<td><a href="./Plots/Plot_' + str(iyear) 
                sline = sline + '_' + simonth + '/month.html">' + simonth + '</a></td>\n'

        sline = sline + "</tr>\n"

    sline = sline + "</table>\n"

    sline = sline + '<p style="padding-top:40px;padding-bottom:20px"> \n <hr /> \n </p> \n'
#
#--- add updated date
#
    date = mcf.today_date_display()

    sline = sline + '<p style="padding-top:10px">Last Updated: ' + str(date) +'<br />'   + "\n";
    sline = sline + '<em style="padding-top:10px">If you have any questions, contact: '
    sline = sline + '<a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a></p>'
    sline = sline + "\n"
    sline = sline + "</body>\n"
    sline = sline + "</html>\n"

    ofile = web_dir + '/sib_main.html'
    with  open(ofile, 'a') as fo:
        fo.write(sline)
#
#--- remove old reg files from Reg_files direcotries
#
    scf.remove_old_reg_file(1)
    scf.remove_old_reg_file(2)
#
#--- gzip fits files saved in Outdir
#
    cmd = 'gzip ' + cor_dir + 'Lev1/Outdir/lres*/*.fits '
    os.system(cmd)

    cmd = 'gzip ' + cor_dir + 'Lev2/Outdir/lres*/*.fits '
    os.system(cmd)


#-------------------------------------------------------------------------------
#-- add_date_on_html: updating the modified date on three html files          --
#-------------------------------------------------------------------------------

def add_date_on_html():
    """
    updating the modified date on three html files
    Input:  None
    Outpu:  three htmla pages updated
    """
    current   = mcf.today_date_display()

    top_level = '/'
    html_file = 'long_term.html'
    plot_out  =  top_level + 'Plots/Plot_long_term/'
    change_date(current, html_file, plot_out)

    html_file = 'past_one_year.html'
    plot_out  =  top_level + 'Plots/Plot_past_year/'
    change_date(current, html_file, plot_out)

    html_file = 'quarter.html'
    plot_out  =  top_level + 'Plots/Plot_quarter/'
    change_date(current, html_file, plot_out)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def  change_date(current, html_file, plot_out):
    """
    find a #DATE# form a html page and replace with the current date
    Input:  current     --- current date
            html_file   --- htmlpage file name
            plot_out    --- plot output directory name where html_file is located
    Output: html_fie    --- updated one
    """
    ifile = house_keeping + html_file 
    with open(ifile, 'r') as f:
        text = f.read()

    text = text.replace('#DATE#', current)

    out  = web_dir + plot_out + html_file
    with open(out, 'w') as fo:
        fo.write(text)

#---------------------------------------------------------------------------------

if __name__ == "__main__":

    update_html()
    add_date_on_html()
