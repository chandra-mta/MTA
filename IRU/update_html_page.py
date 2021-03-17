#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       update_html_page.py: udate html pages                                           #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Mar 09, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import math
import numpy
import time
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/IRU/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import function
#
import mta_common_functions       as mcf
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)
#
#--- some data
#
mon_list = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

#----------------------------------------------------------------------------------
#-- update_html_page: update the html page                                       --
#----------------------------------------------------------------------------------

def update_html_page(syear=''):
    """
    update the html page
    input:  syear   --- starting year. if it is blank, syear is this year
    output: <web_dir>/iru_bias_trend_year<year>.html
    """
#
#--- find today's date
#
    date  = time.strftime("%Y:%m:%d", time.gmtime())
    atemp = re.split(':', date)
    tyear = int(atemp[0])
    tmon  = int(atemp[1])
    tday  = int(atemp[2])

    if syear == '':
        syear = tyear
#
#--- read template
#
    ifile    = house_keeping + 'iru_template'
    with open(ifile, 'r') as f:
        template = f.read()

    for  year in range(1999, tyear+1):
        mon_b = 1
        mon_e = 12
        if year == 1999:
            mon_b = 9
        elif year == tyear:
            mon_e = tmon

        update_page_for_year(year, tyear, mon_b, mon_e, template)
#
#--- make a symbolic link to the latest year to the main page
#
    mpage = web_dir + 'iru_bias_trend.html'
    cmd   = 'rm -rf ' + mpage
    os.system(cmd)

    tpage = web_dir + 'iru_bias_trend_year' + str(tyear) + '.html'
    cmd   = 'ln -s ' + tpage + ' ' + mpage
    os.system(cmd)

#----------------------------------------------------------------------------------
#-- update_page_for_year: create html page for the given year                    --
#----------------------------------------------------------------------------------

def update_page_for_year(myear, tyear, mon_b, mon_e, template):
    """
    create html page for the given year
    input:  myear   --- year to be the page is created
            tyear   --- this year
            mon_b   --- starting month, usually 1 (Jan)
            mon_e   --- ending month, usualy 12 (Dec)
            template    --- template of the page
    output: <web_dir>/iru_bias_trend_year<year>.html
    """
#
#--- monthly bias/hist popup plots
#
    plink = '<tr>\n'
    if mon_b > 1:
        plink = plink + fill_blank_plot_link(1, mon_b)

    for mon in range(mon_b, mon_e+1):
        plink = plink + create_plot_link(myear, mon)

    if mon_e < 12:
        plink = plink + fill_blank_plot_link(mon_e+1, 13)

    plink = plink + '</tr>\n'

#
#--- table link to other years
#
    tlink = '<tr>\n'
    m     = 0
    for year in range(1999, tyear+1):
        if year == myear:
            tlink = tlink + '<th style="color:green;"><b>' + str(year) + '</b></th>\n'
        else:
            tlink = tlink + create_table_link(year)
        m += 1
        if m % 10 == 0:
            tlink = tlink + '</tr>\n<tr>\n'
            m = 0

    if m != 0:
        for k in range(m, 10):
            tlink = tlink + '<th>&#160;</th>\n'

    tlink = tlink + '</tr>\n'
#
#--- link direction buttons
#
    direct = create_direct_button(myear, tyear)
#
#--- replace the table entry to the template
#
    template = template.replace('#YEAR#',   str(myear))
    template = template.replace('#DIRECT#', direct)
    template = template.replace('#PLOTS#',  plink)
    template = template.replace('#YTABLE#', tlink)
#
#--- create the table
#
    outfile  = web_dir + 'iru_bias_trend_year' + str(myear) + '.html'
    with open(outfile, 'w') as fo:
        fo.write(template)

#----------------------------------------------------------------------------------
#-- create_plot_link: create table entry for a monthly plot link                 --
#----------------------------------------------------------------------------------

def create_plot_link(year, mon):
    """
    create table entry for a monthly plot link
    input:  year    --- year
            mon     --- month
    output: line    --- table entry
    """
    tyear = str(year)
    syr   = tyear[2] + tyear[3]
    line = "<th><a href=\"javascript:WindowOpener("
    line = line + "'" + str(year) + "/" + mon_list[mon-1] + syr + "_bias.png',"
    line = line + "'" + str(year) + "/" + mon_list[mon-1] + syr + "_hist.png')\">"
    line = line + mon_list[mon-1].capitalize() + "</a></th>\n"

    return line

#----------------------------------------------------------------------------------
#-- fill_blank_plot_link: create table entry for a blank plot link               --
#----------------------------------------------------------------------------------

def fill_blank_plot_link(start, stop):
    """
    create table entry for a blank plot link
    input:  start   --- starting month 
            stop    --- stopping month
    output: line    --- table entry
    """
    line = ''
    for mon in range(start, stop):
        line = line  + '<th>' + mon_list[mon-1].capitalize() + '</th>\n'

    return line

#----------------------------------------------------------------------------------
#-- create_table_link: create table entry to year table                          --
#----------------------------------------------------------------------------------

def create_table_link(year):
    """
    create table entry to year table
    input:  year    --- year
    output: line    --- table entry
    """
    line = '<th><a href="./iru_bias_trend_year' + str(year) + '.html">'
    line = line + str(year) + '</a></th>\n'

    return line

#----------------------------------------------------------------------------------
#-- create_direct_button: create directional button for the page                 --
#----------------------------------------------------------------------------------

def create_direct_button(myear, tyear):
    """
    create directional button for the page
    input:  myear   --- year to be the page is created
            tyear   --- this year
    output: line    --- the html code with the button
    """
    if myear == 1999:
        line = 'Go to: <a href="./iru_bias_trend_year2000.html"><em>Next Year</em></a>'
    elif myear == tyear:
        line = 'Go to: <a href="./iru_bias_trend_year'+ str(tyear-1) + '.html"><em>Prev Year</em></a>'
    else:
        line = 'Go to: <a href="./iru_bias_trend_year'+ str(myear-1) + '.html"><em>Prev Year</em></a>'
        line = line + ' / '
        line = line + '<a href="./iru_bias_trend_year'+ str(myear+1) + '.html"><em>Next Year</em></a>'

    return line

#----------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    update_html_page(year)

