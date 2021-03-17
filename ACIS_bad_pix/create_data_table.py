#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#    create_html_page.py: create a data display html sub pages                      #
#                                                                                   #
#               author: t. isobe (tisobe@head.cfa.harvard.edu)                      #
#                                                                                   #
#               Last upated: Mar 02, 2021                                           #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import operator
import time
import Chandra.Time


path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'
with open(path, 'r') as f:
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

#-----------------------------------------------------------------------------------
#--- create_html_page: create a data display html sub pages                     ---
#-----------------------------------------------------------------------------------

def create_html_page():
    """
    create a data display html
    input:  None, but read from <data_dir>/*
    output: <web_dir>/Html_dir/ccd_data<ccd>.html
    """
    new_bad_pix_list = []
    new_hot_pix_list = []
    new_col_pix_list = []
    past_bad_list    = []
    past_hot_list    = []
    past_col_list    = []

    for ccd in range(0, 10):
#
#--- warm pixel cases
#
        (warm, flick, new, past) = readData(ccd, 'ccd')
        past_bad_list.append(len(past))
        new_bad_pix_list.append(new)
#
#--- hot pixel cases
#
        (warm, flick, new, past) = readData(ccd, 'hccd')
        past_hot_list.append(len(past))
        new_hot_pix_list.append(new)
#
#--- bad column cases
#
        (warm, flick, new, past) = readData(ccd, 'col')
        past_col_list.append(len(past))
        new_col_pix_list.append(new)
#
#--- create the main html page
#
    pline = create_main_head_part(new_bad_pix_list, new_hot_pix_list, new_col_pix_list)
    pline = pline + create_main_mid_part(past_bad_list, past_hot_list, past_col_list)

    tfile = house_keeping + 'tail'
    with open(tfile, 'r') as f:
        tail_part = f.read()

    pline = pline + tail_part

    ofile = web_dir + '/mta_bad_pixel_list.html'
    with open(ofile, 'w') as fo:
        fo.write(pline)

#-----------------------------------------------------------------------------------
#-- create_main_head_part: create the top part of the main html page              --
#-----------------------------------------------------------------------------------

def  create_main_head_part(new_bad_pix_list, new_hot_pix_list, new_col_pix_list):
    """
    create the top part of the main html page
    input:  new_bad_pix_list --- a list of new warm pixels
            new_hot_pix_list --- a list of new hot pixels
            new_col_pix_list --- a list of new bad column list
    output: head_part        --- updated top part of the html
    """
#
#--- read template
#
    hfile  = house_keeping + 'head'
    with open(hfile, 'r') as f:
        head_part = f.read()
#
#--- set data updated time
#
    ltime     = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    ctime     = int(Chandra.Time.DateTime(ltime).secs)
    atemp     = re.split(':', ltime)
    yday      = atemp[1]
    dtime     = time.strftime("%Y-%m-%d",  time.gmtime())

    head_part = head_part.replace('#DISPLAY# ', dtime)
    head_part = head_part.replace('#YDATE#', str(yday))
    head_part = head_part.replace('#STIME#', str(ctime))
#
#--- warm pixels
#
    line = ''
    chk  = 0
    for i in range(0, 10):
        if new_bad_pix_list[i][0] != '':
            chk += 1
            line = line + 'CCD' + str(i) + ': '
            for ent in new_bad_pix_list[i]:
                line = line + ent
            line = line + '<br />\n'
    if chk == 0:
            line = 'No New Warm Pixel'

    head_part = head_part.replace('#WARMPIX#', line)
#
#--- hot pixels
#
    line = ''
    chk  = 0
    for i in range(0, 10):
        if new_hot_pix_list[i][0] != '':
            chk += 1
            line = line + 'CCD' + str(i) + ': '
            for ent in new_hot_pix_list[i]:
                line = line + ent
            line = line + '<br />\n'
    if chk == 0:
            line = 'No New Hot Pixel'

    head_part = head_part.replace('#HOTPIX#', line)
#
#--- warm columns
#
    line = ''
    chk  = 0
    for i in range(0, 10):
        if new_col_pix_list[i][0] != '':
            chk += 1
            line = line + 'CCD' + str(i) + ': '
            for ent in new_col_pix_list[i]:
                line = line + ent
            line = line + '<br />\n'
    if chk == 0:
            line = 'No New Warm Column'

    head_part = head_part.replace('#WARMCOL#', line)

    return head_part

#-----------------------------------------------------------------------------------
#-- create_main_mid_part: create main table of the html page                      --
#-----------------------------------------------------------------------------------

def create_main_mid_part(past_bad_list, past_hot_list, past_col_list):
    """
    create main table of the html page
    input:  past_bad_list   --- a list of past warm pixel list
            past_hot_lis    --- a list of past hot pixel list
            past_col_list   --- a list of past bad column list
    output: line            --- a table part of the main html page
    """
    line = ''
    for ccd in range(0, 10):
        line  = line + '<tr><td>CCD' + str(ccd) + '</td>\n'
        aline = find_current_codition(ccd,'ccd')
        line  = line + aline
        aline = find_current_codition(ccd,'hccd')
        line  = line + aline
        aline = find_current_codition(ccd,'col')
        line  = line + aline

        if past_bad_list[ccd] <= 1:
            line = line + '<td>No History</td>\n'
        else:
            line = line + '<td><a href="./Data/hist_ccd' + str(ccd) + '">Data</a> \n'
            line = line + '<a href="javascript:WindowOpener(\'hist_plot_ccd'+str(ccd)
            line = line + '.png\')">Plot</a><br /> \n'
            line = line + '<a href="./Html_dir/past_ccd' + str(ccd) + '">Past Warm Pixels</a></td>'

        if past_hot_list[ccd] <= 1:
            line = line + '<td>No History</td>\n'
        else:
            line = line + '<td><a href="./Data/hist_hccd' + str(ccd) + '">Data</a>\n'
            line = line + '<a href="javascript:WindowOpener(\'hist_plot_hccd'+str(ccd)
            line = line + '.png\')">Plot</a><br />\n'
            line = line + '<a href="./Html_dir/past_hccd' + str(ccd) + '">Past Hot Pixels</a></td>'

        if past_col_list[ccd] <= 1:
            line = line + '<td>No History</td>\n'
        else:
            line = line + '<td><a href="./Data/hist_col' + str(ccd) + '">Data</a>\n'
            line = line + '<a href="javascript:WindowOpener(\'hist_plot_col'+str(ccd)
            line = line + '.png\')">Plot</a><br />\n'
            line = line + '<a href="./Html_dir/past_col' + str(ccd) + '">Past Warm Columns</a></td>'

        line = line + '</tr>\n'

    line = line + '</table>\n'

    return line

#-----------------------------------------------------------------------------------
#-- find_current_codition: find out the current condition of ccd/column           --
#-----------------------------------------------------------------------------------

def find_current_codition(ccd, head):
    """
    find out the current condition of ccd/column
    input: ccd      --- ccd #
            head    --- header part of the data: ccd/hccd/col
    output: line    --- a part of html table data
            past_<head><ccd>    --- a file with the past warm/hot pixels/columns
    """
    (warm, flick, new, past) = readData(ccd, head)

    line = '<td>'
    for ent in warm:
        if ent != '':
            line = line + ent + '<br />'
    line = line + '</td>'

    line = line + '<td>'
    for ent in flick:
        if ent != '':
            line = line + ent + '<br />'
    line = line + '</td>'
#
#--- print out the past data list
#
    ifile = web_dir +  'Html_dir/past_'+ head + str(ccd)
    with open(ifile, 'w') as fo:
        for ent in past:
            fo.write(ent + '\n')

    return line

#-----------------------------------------------------------------------------------
#--- readData: read data from three files and return three list of data          ---
#-----------------------------------------------------------------------------------

def readData(ccd, head):
    """
    read data from three files and return three list of data
    Input:  infile1, infile2, infile3 --- three input file names
    Output: file1,   file2,   file3   --- three list of data
    """
    ifile  = data_dir + '/' + head + str(ccd) + '_information'

    data = mcf.read_data_file(ifile)

    warm  = get_elm(data[0])
    flick = get_elm(data[1])
    new   = get_elm(data[2])
    past  = get_elm(data[3])

    return [warm, flick, new, past]

#-----------------------------------------------------------------------------------
#-- get_elm: eparate data into a list                                             --
#-----------------------------------------------------------------------------------

def get_elm(line):
    """
    separate data into a list
    input:  line    --- a data line
    output: dlist   --- a list of data
    """
    dlist = []
    line  = line.replace(' ', '')
    atemp = re.split(':', line)
    if len(atemp) > 1:
        for k in range(1, len(atemp)):
            ent = atemp[k].strip()
            dlist.append(ent)

    return dlist

#--------------------------------------------------------------------

if __name__ == '__main__':

    create_html_page()
