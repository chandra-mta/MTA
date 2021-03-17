#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#   update_html.py: update the main sib page (sib_main.html) and update modified dates for      #
#                   a few sub html pages                                                        #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           Last Update: Feb  4, 2014                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import pyfits
import numpy

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

#
#--- reading directory list
#
comp_test = 'live'

if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'
#
#--- check whether this is run for lev2
#
level = 1
if len(sys.argv) == 2:
    if sys.argv[1] == 'lev2':
        level = 2

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import robust_linear        as robust
#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#-- update_html: update the main html page (sib_main.html)                                        --
#---------------------------------------------------------------------------------------------------

def update_html():

    """
    update the main html page (sib_main.html)
    Input: none, but read a part from <house_keeping>/sim_head_part
    Output: <web_dir>/sib_main.html
    """
#
#--- find today's date, and set a few thing needed to set output directory and file name
#
    [year, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()

    syear  = str(year)
    smonth = str(mon)
    if mon < 10:
        smonth = '0'+ smonth

    lyear = year 
    lmon  = mon - 1
    if lmon < 1:
        lmon   = 12
        lyear -= 1

    slyear  = str(lyear)
    slmonth = str(lmon)
    if lmon < 10:
        slmonth = '0' + slmonth
#
#--- read the head part from the house_keeping
#
    if level == 1:
        cmd = 'cp ' + house_keeping + '/sib_head_part ' + web_dir + '/sib_main.html'
    else:
        cmd = 'cp ' + house_keeping + '/sib_head_part2 ' + web_dir + '/sib_main_lev2.html'
    os.system(cmd)
#
#--- add the rest
#
    if level == 1:
        line = web_dir + '/sib_main.html'
    else:
        line = web_dir + '/sib_main_lev2.html'
    fo  = open(line, 'a')
    for iyear in range(year, 1999, -1):

        fo.write("<tr>\n")

        if iyear == year:
            line = '<th>' + syear  + '</th><td>---</td>'
        else:
            if level == 1:
                line = '<th>' + str(iyear) + '</th><td><a href="./Plots/Plot_' + str(iyear) + '/year.html">' + str(iyear) + '</a></td>'
            else:
                line = '<th>' + str(iyear) + '</th><td><a href="./Lev2/Plots/Plot_' + str(iyear) + '/year.html">' + str(iyear) + '</a></td>'
        fo.write(line)
        fo.write("\n")
        for imonth in range(1, 13):
            simonth = str(imonth)
            if imonth < 10:
                simonth = '0' + simonth

            if (iyear == year) and (imonth >= mon):
                line = '<td>' + simonth + '</td>'
            else:
                if level == 1:
                    line = '<td><a href="./Plots/Plot_' + str(iyear) + '_' + simonth + '/month.html">' + simonth + '</a></td>'
                else:
                    line = '<td><a href="./Lev2/Plots/Plot_' + str(iyear) + '_' + simonth + '/month.html">' + simonth + '</a></td>'
            fo.write(line)
            fo.write("\n")

        fo.write("</tr>\n")

    fo.write("</table>\n")

    line = '<p style="padding-top:40px;padding-bottom:20px"> \n <hr /> \n </p> \n'
    fo.write(line)
#
#--- add updated date
#
    date = tcnv.currentTime(format='Display')

    line = '<p style="padding-top:10px">Last Updated: ' + str(date) +'<br />'   + "\n";
    fo.write(line)
    line = '<em style="padding-top:10px">If you have any questions, contact: <a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a></p>'
    fo.write(line)
    fo.write("\n")
    fo.write("</body>\n")
    fo.write("</html>\n")

    fo.close()

#---------------------------------------------------------------------------------------------------
#-- add_date_on_html: updating the modified date on three html files                              --
#---------------------------------------------------------------------------------------------------

def add_date_on_html():

    """
    updating the modified date on three html files
    Input:  None
    Outpu:  three htmla pages updated
    """

    current   = tcnv.currentTime(format='Display')

    if level == 1:
            top_level = '/'
    else:
            top_level = '/Lev2/'
    html_file = 'long_term.html'
    plot_out  =  top_level + 'Plots/Plot_long_term/'
    change_date(current, html_file, plot_out)

    html_file = 'past_one_year.html'
    plot_out  =  top_level + 'Plots/Plot_past_year/'
    change_date(current, html_file, plot_out)

    html_file = 'quarter.html'
    plot_out  =  top_level + 'Plots/Plot_quarter/'
    change_date(current, html_file, plot_out)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def  change_date(current, html_file, plot_out):
    """
    find a #DATE# form a html page and replace with the current date
    Input:  current     --- current date
            html_file   --- htmlpage file name
            plot_out    --- plot output directory name where html_file is located
    Output: html_fie    --- updated one
    """
    file = house_keeping + html_file 
    text = open(file, 'r').read()
    text = text.replace('#DATE#', current)

    out  = web_dir + plot_out + html_file
    f    = open(out, 'w')
    f.write(text)
    f.close()

#--------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    update_html()
    add_date_on_html()
