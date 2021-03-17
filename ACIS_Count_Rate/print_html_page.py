#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#        print_html_page.py update/create html page related acis does plots         #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               Last Update: Mar 03, 2021                                           #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import time

path = '/data/mta/Script/ACIS/Count_rate/house_keeping/dir_list_py'
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
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------
#--- print_html_page:  print all html pages for ACIS Dose Plots                     ---
#--------------------------------------------------------------------------------------

def print_html_page(year=''):
    """
    driving function to print all html pages for ACIS Dose Plots
    input:  in_year --- year;   default ""
    output: html pages in <web_dir> and <web_dir>/<mon_dir_name>  (e.g. JAN2013)
    """
#
#--- find today's date
#
    ldate = time.strftime("%d-%m-%Y", time.gmtime())
    lyear = int(float(time.strftime("%Y", time.gmtime())))
    yday  = int(float(time.strfimte('%j', time.gmtime())))
#
#--- if year and month is given, create a page for that month.
#
    if year == '':
        year = lyear

    chk  = 0
    line = '<tr>\n'
    for syear in range(1999, lyear+1):
        line = line + '<td><a href="./Htmls/plot_page_' + str(syear) + '.html">' 
        line = line+ str(syear) + '</a></td>\n'
        if chk >= 9:
            line = line + '</tr>\n'
            chk  = 0
        else:
            chk += 1
    if chk < 9:
        for k in range(chk, 10):
            line = line + '<td>&#160;</td>\n'
        line = line + '</tr>\n'
#
#--- update main page
#
    ifile = house_keeping + 'main_page_template'
    with open(ifile, 'r') as f:
        out = f.read()

    out = out.replace('#TABLE#',  line)
    out = out.replace('#UPDATE#', ldate)

    outfile = web_dir + 'main_acis_dose_plot.html'
    with open(outfile, 'w') as fo:
        fo.write(out)
#
#--- update this year's page
#
    ifile = house_keeping + 'yearly_template'
    with open(ifile, 'r') as f:
        out = f.read()

    out = out.replace('#YEAR#',   str(year))
    out = out.replace('#UPDATE#', ldate)

    if year < 2019:
        out = out.replace('#EPHINTITLE#', 'Ephin Rate')

        ephline = "<a href=\"javascript:WindowOpener('" + str(year) + "/ephin_rate.png')\">"
        ephline = ephline + "<img src=\"../Plots/" + str(year) + "/ephin_rate.png\" "
        ephline = ephline + "style=\"text-align:center; width: 95%\"></a>"
        out = out.replace('#EPHIN#', ephline)
    else:
        out = out.replace('#EPHINTITLE#', '&#160;')
        out = out.replace('#EPHIN#',      '&#160;')


    if year == 1999:
        dline = '<a href="https://cxc.cfa.harvard.edu/mta_days/mta_dose_count/Htmls/plot_page_2000.html">  Next Year</a>'
    elif year == lyear:
        prev  = str(year - 1)
        dline = '<a href="https://cxc.cfa.harvard.edu/mta_days/mta_dose_count/Htmls/plot_page_'+prev+'.html">Prev Year  </a>'
    else:
        prev   = str(year - 1)
        after  = str(year + 1)
        dline = '<a href="https://cxc.cfa.harvard.edu/mta_days/mta_dose_count/Htmls/plot_page_'+prev+'.html">Prev Year </a>'
        dline = dline + '--'
        dline = dline + '<a href="https://cxc.cfa.harvard.edu/mta_days/mta_dose_count/Htmls/plot_page_'+after+'.html"> Next Year</a>'

    out = out.replace("#DIRECT#", dline)


    outfile = web_dir + 'Htmls/plot_page_' + str(year) + '.html'
    with open(outfile, 'w') as fo:
        fo.write(out)

#--------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    print_html_page(year)
#
#--- if this is the first several days of the year, udate the last year's html page
#
    yday = int(float(time.strftime('%j', time.gmtime())))
    if yday < 10:
        lyear = int(float(time.strftime('%Y', time.gmtime()))) -1
        print_html_page(lyear)
