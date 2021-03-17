#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       create_html_pages.py: create acis focal plane temperature html pages            #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Mar 03, 2021                                               #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import time
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Focal/Script/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)

#-------------------------------------------------------------------------------
#-- run_html_page_script: check whether it is the beginning of the year and update all html pages
#-------------------------------------------------------------------------------

def run_html_page_script(all):
    """
    check whether it is the beginning of the year and update all html pages
    input:  all --- if not "", update all html pages even not at the beginning of the year
    output: <web_dir>/*html
    """
    tyear = int(time.strftime("%Y", time.gmtime()))
    yday  = int(time.strftime("%j", time.gmtime()))

    if (yday < 4) or (all != 0):
#
#--- update all html from year 2000 to this year
#
        for year in range(2000, tyear+1):
            create_html_pages(year)
#
#--- symbolic link to index.html is also changed
#
        cmd = 'rm -f  ' + web_dir + 'index.html ' + web_dir + 'main_fp_temp.html'
        os.system(cmd)

        cmd = 'cd ' + web_dir + '; ln -s ./ft_main_year' + str(year) + '.html index.html'
        os.system(cmd)
        cmd = 'cd ' + web_dir + '; ln -s ./ft_main_year' + str(year) + '.html main_fp_temp.html'
        os.system(cmd)

    else:
#
#--- update just this year
#
        create_html_pages(tyear)

#-------------------------------------------------------------------------------
#-- create_html_pages: create acis focal plane temperature html pages         --
#-------------------------------------------------------------------------------

def create_html_pages(uyear):
    """
    create acis focal plane temperature html pages
    input:  uyear   --- year of which a html page is created/updated
    output: <web_dir>/ft_slide_year<uyear>.html
    """
#
#--- if year is not given, find current time
#
    tyear = int(time.strftime("%Y", time.gmtime()))
    if uyear == '':
        uyear == str(tyear)

    uyear = str(uyear)

    ifile = house_keeping + 'ft_main_template'
    with open(ifile, 'r') as f:
        main  = f.read()

    ifile = house_keeping + 'ft_slide_template'
    with open(ifile, 'r') as f:
        slide = f.read()

    line = '<table border=1 style="margin-left:auto;margin-right:auto;">\n'
    line = line + '<tr>\n'
    cnt  = 0
    for  year in range(2000, tyear+1):
        if str(year) == uyear:
            line = line + '<td><b style="color:green;">' + str(year) + '</b></td>\n'
        else:
            line = line + '<td><a href="./ft_main_year' + str(year) + '.html">' 
            line = line + str(year) + '</a></td>\n'

        if cnt == 15:
            line = line + '</tr>\n<tr>\n'
            cnt = 0
        else:
            cnt += 1

    if (cnt > 0) and (cnt < 15):
        for k in range(cnt, 16):
            line = line + '<td>&#160;</td>\n'

        line = line + '</tr>\n'

    line = line + '</table>\n'

    main = main.replace("#YEAR#", uyear)
    main = main.replace("#YTABLE#", line)
    if uyear == "2005":
        main = main.replace("#NOTE#", '<p><em><b>Note:</b> Due to instrumental problems, the focal temperature values taken between dates 2005:259.5 and 2005:289.5 are not reliable.</em></p>')
    else:
        main = main.replace("#NOTE#",'')

    out  = web_dir + 'ft_main_year' + uyear + '.html'
    fo   = open(out, 'w')
    fo.write(main)
    fo.close()

    slide = slide.replace("#YEAR#", uyear)
    slide = slide.replace("#PLINTBL#", create_plintbl(uyear))

    out  = web_dir + 'ft_slide_year' + uyear + '.html'
    with open(out, 'w') as fo:
        fo.write(slide)

#-------------------------------------------------------------------------------
#-- create_plintbl: create a ling table which shows the links to each week plot of the year 
#-------------------------------------------------------------------------------

def create_plintbl(year):
    """
    create a ling table which shows the links to each week plot of the year
    input:  year    --- year
    output: line    --- a html code of the table
    """
    line = ''
    for k in range(0, 53):
        ck = k + 1
        sck = str(ck)
        if ck < 10:
            sck = '0' + sck

        line = line + '<th><a href="javascript:WindowOpener(\'Year' + str(year) 
        line = line + '/focal_week_long_' + str(k) + '.png\')">'
        line = line + sck + '</a></th>\n'

    return line

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
        all = 1
    else:
        all = 0

    run_html_page_script(all)
