#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#############################################################################################
#                                                                                           #
#           update_rdb_and_html.py: update otg rdb files and a html page                    #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: May 23, 2019                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
#
#--- read direcotry path
#
path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions as mcf
#
#--- temp writing file name
#
import random
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- update_rdb_and_html: update rdb files and the html page                               --
#-------------------------------------------------------------------------------------------

def update_rdb_and_html():
    """
    update rdb files and the html page
    input: none, but read from <arc_dir>//OTG_summary.rdb
    output: <arc_dir>/OTG_filtered.rdb
            <arc_dir>/OTG_filtered_short.rdb
            <arc_dir>/OTG_sorted.rdb
            <arc_dir>/otg.html
    """
    update_rdb_files()

    update_html_page()

#-------------------------------------------------------------------------------------------
#-- update_rdb_files: update rdb files                                                    --
#-------------------------------------------------------------------------------------------

def update_rdb_files():
    """
    update rdb files: OTG_filtered.rdb/OTG_filtered_short.rdb/OTG_sorted.rdb
    input: none, but read from <arc_dir>/OTG_summary.rdb
    output: <arc_dir>/OTG_filtered.rdb
            <arc_dir>/OTG_filtered_short.rdb
            <arc_dir>/OTG_sorted.rdb
    """
#
#--- set file names
#
    infile = arc_dir + 'OTG_summary.rdb'
    ofile1 = arc_dir + 'OTG_filtered.rdb'
    ofile2 = arc_dir + 'OTG_filtered_short.rdb'
    ofile3 = arc_dir + 'OTG_sorted.rdb'

    if not os.path.isfile(infile):
        exit(1)
#
#--- clean up OTG_summary.rdb file
#
    sdata = clean_up_summary_file(infile)
#
#--- update filtered rdb file
#
    update_filtered_rdb(ofile1, sdata)
#
#--- create short rdb file --- used to create a html page
#
    create_short_rdb(ofile1, ofile2)
#
#--- sort the data with GRATING, DIRN, and START_TIME
#
    update_sorted_rdb(infile, ofile3)

#-------------------------------------------------------------------------------------------
#-- clean_up_summary_file: sort and remove the duplicated data from OTG_summary.rdb       --
#-------------------------------------------------------------------------------------------

def clean_up_summary_file(infile):
    """
    sort and remove the duplicated data from OTG_summary.rdb
    input:  infile  --- data file name
    output: infile  --- updated data file
            sdata   --- a list of data with headers (top two lines)
    """
    [t_list, hdr1, hdr2] = remove_duplicated_entry(infile)
#
#-- update the data and the data file
#
    sdata = [hdr1, hdr2] + t_list

    line = hdr1 + '\n' + hdr2 + '\n'

    for ent in t_list:
        line = line + ent + '\n'

    with open(infile, 'w') as fo:
        fo.write(line)

    return sdata

#-------------------------------------------------------------------------------------------
#-- update_filtered_rdb: updated filted rdb data file                                     --
#-------------------------------------------------------------------------------------------

def update_filtered_rdb(ofile, sdata):
    """
    updated filted rdb data file
    input:  ofile   --- data file name
            sdata   --- data list
    ouput:  ofile   --- updated filtered rdb data file
    """
#
#--- convert the data into a dictionary form
#
    hdr1   = sdata[0]
    h_list = re.split('\s+', hdr1)
    hdr2   = sdata[1]
    d_dict = create_dict(sdata, chk=2)
#
#--- create a list of indicies where the condition changes and remove duplicated entries
#
    cpos_list = select_entries(d_dict)
    d_dict    = cleanup_dict(cpos_list, d_dict)
#
#--- update the rdb file
#
    line = hdr1 + '\n' + hdr2 + '\n'

    dlen  = len(d_dict['START_TIME'])
    klen  = len(h_list)
    for m in range(0, dlen):
        line = line + str(d_dict[h_list[0]][m])

        for k in range(1, klen):
            val  = str(d_dict[h_list[k]][m])

            if len(val) < 4:
                line = line + '\t' + val + '\t'
            else:
                line = line + '\t' + val 
        line = line + '\n'

    with open(ofile, 'w') as fo:
        fo.write(line)

#-------------------------------------------------------------------------------------------
#-- create_short_rdb: create short rdb file                                               --
#-------------------------------------------------------------------------------------------

def create_short_rdb(ofile1, ofile3):
    """
    create short rdb file --- used to create a html page
    input:  ofile1  --- input data file name
            ofile3  --- output data file name
    output: ofile3  --- updated output data file
    """
#
#--- read the main data file
#
    data = mcf.read_data_file(ofile1)
    hdr1 = data[0]
    hdr2 = data[1]
#
#--- select the last 20 lines
#
    dlist = data[-20:]

    line = hdr1 + '\n' + hdr2 + '\n'

    for ent in dlist:
        line = line + ent + '\n'

    with open(ofile3, 'w') as fo:
        fo.write(line)

#-------------------------------------------------------------------------------------------
#-- update_sorted_rdb: sort the data with GRATING, DIRN, and START_TIME                   --
#-------------------------------------------------------------------------------------------

def update_sorted_rdb(ofile, ofile2):
    """
    sort the data with GRATING, DIRN, and START_TIME
    input:  ofile   --- data file name
    output: ofile2  --- output file name
    """
#
#--- find headers
#
    data   = mcf.read_data_file(ofile)
    hdr1   = data[0]
    hdr2   = data[1]
#
#--- read the data part and create a data dictionary
#
    o_dict = create_dict(ofile)
#
#--- sort the data
#
    o_dict = sort_by_three_condition(o_dict, hdr1)
#
#--- print out the result
#
    line = hdr1 + '\n' + hdr2 + '\n'

    head   = re.split('\s+', hdr1)
    hlen   = len(head)

    for m in range(0, len(o_dict['DIRN'])):
        line = line + o_dict[head[0]][m]

        for k in range(1, hlen):
            val  = str(o_dict[head[k]][m])

            if len(val) < 4:
                line = line + '\t' + val + '\t'
            else:
                line = line + '\t' + val

        line = line + '\n'

    with open(ofile2, 'w') as fo:
        fo.write(line)
    fo.close()

#-------------------------------------------------------------------------------------------
#-- remove_duplicated_entry: sort and remove the duplicated data from <infile>            --
#-------------------------------------------------------------------------------------------

def remove_duplicated_entry(infile):
    """
    sort and remove the duplicated data from <infile>
    input:  infile  --- input file name
    output: infile  --- cleaned data file
    """
    data   = mcf.read_data_file(infile)
    hdr1   = data[0]
    hdr2   = data[1]
    t_dict = {}
    t_list = []
    for ent in data[2:]:
        atemp = re.split('\s+', ent)
        atime = atemp[2]
        t_dict[atime] = ent
        t_list.append(atime)
    t_list = list(set(t_list))

    t_list.sort()
    save = []
    for ent in t_list:
        save.append(t_dict[ent])

    return [save, hdr1, hdr2]

#-------------------------------------------------------------------------------------------
#-- select_entries: find when the things change and keep the index of the changing position 
#-------------------------------------------------------------------------------------------

def select_entries(d_dict):
    """
    find when the things change and keep the index of the changing position
    input:  d_dict  --- data dictionary
    output: isave   --- a list of indecies where the entry values change
    """
    grat   = d_dict['GRATING']
    dirn   = d_dict['DIRN']
    start  = [float(i) for i in d_dict['START_TIME']]
    stop   = [float(i) for i in d_dict['STOP_TIME']]

    glen   = len(grat)
    isave  = []

    for i in range(0,glen):
        ok  = 1
        grat_i  = grat[i]
        dirn_i  = dirn[i]
        start_i = start[i]
        stop_i  = stop[i]

        for j in range(i+1, glen):
            if (grat[j] == grat_i) and (dirn[j] == dirn_i):
                start_j = start[j]
                stop_j  = stop[j]
                dt      = abs(start_i - start_j) + abs(stop_i - stop_j)

                if start_i > start_j:
                    t0 = start_i
                else:
                    t0 = start_j

                if stop_i < stop_j:
                    t1 = stop_i
                else:
                    t1 = stop_j

                if dt < (t1 - t0) / 10.0:
                    ok = 0
                    break
                else:
                    continue

            else:
                continue

        if ok > 0:
            isave.append(i)

    gm = glen -1
    if isave[-1] != gm:
        isave.append(gm)

    return isave

#-------------------------------------------------------------------------------------------
#-- cleanup_dict: remove duplicated data from data dictionary                             --
#-------------------------------------------------------------------------------------------

def cleanup_dict(isave, d_dict):
    """
    remove duplicated data from data dictionary
    input:  isave   --- a list of indicies where the values changed (GRATING, DIRN, and START_TIME)
            d_dict  --- a data dictionary
    output: d_dict  --- cleaned up data dictionary
    """
    key   = d_dict.keys()
    #klen  = len(d_dict[key[0]])
    isave = list(set(isave))

    for key in d_dict.keys():
        d_list = d_dict[key]
        n_list = []

        for k in isave:
            n_list.append(d_list[k])

        d_dict[key] = n_list

    return d_dict

#-------------------------------------------------------------------------------------------
#-- sort_an_array: sort a data list in the dictionary with a given list                   --
#-------------------------------------------------------------------------------------------

def sort_an_array(slist, d_dict):
    """
    sort a data list in the dictionary with a given list
    input:  slist   --- a list to be used to sort
            d_dict  --- data dictionary
    output: d_dict  --- updated data dictionary
    """
    sarray = numpy.array(slist)
    index  = numpy.argsort(sarray)

    for key in d_dict.keys():
        sarray = numpy.array(d_dict[key])
        sarray = sarray[index]
        d_dict[key] = list(sarray)

    return d_dict

#-------------------------------------------------------------------------------------------
#-- sort_by_three_condition: sort by GRATING, DIRN, then START_TIME                       --
#-------------------------------------------------------------------------------------------

def sort_by_three_condition(d_dict, hdr):
    """
    sort by GRATING, DIRN, then START_TIME
    input:  d_dict  --- a dictionary of data
            hdr     --- a header of the data
    output: o_dict  --- a sorted dictionary of data
    """
#
#--- a list of header entries
#
    h_list = re.split('\s+', hdr)
    hlen   = len(h_list)

    dlen   = len(d_dict['GRATING'])
#
#--- convert a dctionary into a list of lists
#
    s_list = []
    for m in range(0, dlen):
        t_list = []

        for k in range(0, hlen):
            t_list.append(d_dict[h_list[k]][m])

        s_list.append(numpy.array(t_list))
#
#--- sort by GRATING, DIRN, then START_TIME; we assume their positions is 1, 0, and 2 of the list
#
    s_list.sort(key=lambda x: (x[1], x[0], x[2]))
#
#---- put them back to a dictionary form
#
    o_dict = {}
    for k in range(0, hlen):
        t_list = []

        for m in range(0, dlen):
            t_list.append(s_list[m][k])

        o_dict[h_list[k]] = t_list
    
    return o_dict

#-------------------------------------------------------------------------------------------
#-- create_dict: convert data list into a dictionary form                                 --
#-------------------------------------------------------------------------------------------

def create_dict(infile, chk = 0):
    """
    convert data list into a dictionary form
    input:  infile  --- assume that the first two lines are header
    output: d_dict  --- dictionary of header <---> data list
    """
    if chk == 0:
        data = mcf.read_data_file(infile)
    else:
        data = infile

    head   = re.split('\s+', data[0].strip())
    hlen   = len(head)
    save   = []
    for k in range(0, hlen):
        save.append([])
#
#--- top two lines of the data are headers
#
    dpart  = data[2:]
    d_dict = {}

    for ent in dpart:

        atemp = re.split('\s+', ent)
        if len(atemp) == hlen:
            for k in range(0, hlen):
                save[k].append(atemp[k])

    for k in range(0, hlen):
        d_dict[head[k]] = save[k]

    return d_dict

#-----------------------------------------------------------------------------------------------
#-- update_html_page: update otg html page                                                  ----
#-----------------------------------------------------------------------------------------------

def update_html_page():
    """
    update otg html page
    input:  none, but read from <arc_dir>/OTG_filtered_short.rdb
    output: <arc_dir>/otg.html
    """
#
#--- read the template
#
    temp  = house_keeping + 'html_template'
    with open(temp, 'r') as f:
        hline = f.read()
#
#--- create the table to insert
#
    hdepot = './Sub_html/'
    ofile = arc_dir + 'OTG_filtered_short.rdb'
    data  = mcf.read_data_file(ofile)
    data  = data[2:]
    tline = ''
    for ent in data:
        atemp = re.split('\s+', ent)
        tline = tline + '<tr>\n'
        tline = tline + '<td>' + atemp[0] + '</td>\n'
        tline = tline + '<td>' + atemp[1] + '</td>\n'
        tline = tline + '<td>' + atemp[2] + '</td>\n'
        tline = tline + '<td>' + atemp[3] + '</td>\n'
        tline = tline + '<td>' + atemp[4] + '</td>\n'
        tline = tline + '<td>' + atemp[5] + '</td>\n'
        tline = tline + '<td><a href="' + hdepot + atemp[2] + '">Summary</a></td>\n'
        tline = tline + '</tr>\n'

    hline = hline.replace('#TABLE#', tline)
#
#--- print out
#
    ofile = arc_dir + 'otg.html'
    with open(ofile, 'w') as fo:
        fo.write(hline)

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_rdb_and_html()
