#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#       update_limit_table.py: update html limit table for display          #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: Feb 01, 2021                                       #
#                                                                           #
#############################################################################

import sys
import os
import string
import re
import time
import random

path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- envelope common functions
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

obegin =  ecf.stime_to_frac_year(48815999) #--- 1999:201:00:00:00

#---------------------------------------------------------------------------------
#-- update_limit_table: update html limit table for display                      --
#---------------------------------------------------------------------------------

def update_limit_table():
    """
    update html limit table for display
    input:  none, but read from <limit_dir>/Limit_data/op_limits.db
    output: <html_dir>/<Group>/Limit_table/<msid>_limit_table.html
    """
#
#--- create msid <---> group name dictionary
#
    g_dict = create_group_dict()
    u_dict = {}
#
#--- read limit database
#
    ifile = limit_dir + 'Limit_data/op_limits_new.db'
    data  = mcf.read_data_file(ifile)
#
#--- separate the data into each msid
#
    prev  = ''
    save  = []
    for ent in data:
        if ent[0] == '#':
            continue

        atemp = re.split('#', ent)
        btemp = re.split('\s+', atemp[0])
        msid  = btemp[0].strip()
        unit  = atemp[2].strip()
        u_dict[msid] = unit

        if msid == prev:
            save.append(btemp)
        else:
            if prev == '':
                prev = msid
                save.append(btemp)
                continue
            else:
#
#--- collected all limits for the msid; create a limit table html page
#
                try:
                    group = g_dict[prev]
                except:
                    #print("MSID MISSED: " + str(prev))
                    prev = msid
                    save = [btemp]
                    continue
                unit = u_dict[prev]
                create_limit_table(save, prev, group, unit)
                prev  = msid
                save  = [btemp]
#
#--- create a html page for the last entry
#
    if len(save) > 0:
        try:
            group = g_dict[msid]
            unit  = u_dict[msid]
            create_limit_table(save, msid, group, unit)
        except:
            pass

#---------------------------------------------------------------------------------
#-- create_limit_table: update html limit table for display                     --
#---------------------------------------------------------------------------------

def create_limit_table(dlist, msid, group, unit):
    """
    update html limit table for display
    input:  dlist   --- a list of lists of: [<msid>, <yl>, <yu>, <rl>, <ru>, <cmsid>, <state>, <time>]
            msid    --- msid
            group   --- groupd name
            unit    --- unit
    output: <html_dir>/<Group>/Limit_table/<msid>_limit_table.html
    """
    yl_list = []
    yu_list = []
    rl_list = []
    ru_list = []
    st_list = []
    tm_list = []
    for ent in dlist:
        msid  = ent[0]
        yl    = ent[1]
        yu    = ent[2]
        rl    = ent[3]
        ru    = ent[4]
        state = ent[6]
        stime = ent[7]
        yl_list.append(yl)
        yu_list.append(yu)
        rl_list.append(rl)
        ru_list.append(ru)
        st_list.append(state)
        tm_list.append(stime)
#
#--- check which states are in the list
#
    states = list(set(st_list))
    slen   = len(states)

    nchk = 0
    if 'none' in states:
        nchk = 1
#
#--- check 'none' case first
#
    n_list = []
    if nchk  == 1:
        for k in range(0, len(st_list)):
            if st_list[k] == 'none':
#
#--- convert time from seconds from 1998.1.1 to fractional year
#
                time = ecf.stime_to_frac_year(tm_list[k])
                n_list.append([time, yl_list[k], yu_list[k], rl_list[k], ru_list[k]])
#
#--- if  none limit start later than 1999.201, extend the beginning to 1999.201
#
        try:
            n_list = compress_time_periods(n_list)
        except:
            pass
        try:
            n_list = combine_same_start(n_list)
        except:
            pass
        try:
            [n_list, ochk] = extend_start_range(n_list)
        except:
            pass
#
#--- check other cases
#
    if  nchk == 0 or slen > 1:
        all_list   = []
        for state in states:
            if state == 'none':
                continue

            t_list = []
            for k in range(0, len(st_list)):
                if state == st_list[k]:
                    time = ecf.stime_to_frac_year(tm_list[k])
                    t_list.append([time, yl_list[k], yu_list[k], rl_list[k], ru_list[k]])
            if t_list[0][0] > obegin:
                try:
                    non_first = n_list[0]
                    t_list = [non_first] + t_list
                except:
                    [t_list, ochk] = extend_start_range(t_list)

            t_list = compress_time_periods(t_list)
            all_list.append(t_list)
#
#--- found only none case
#
    if nchk == 1 and slen == 1:
#
#--- create html limit table
#
        aline = create_html_table(n_list, states)
#
#--- found only other cases
#
    elif nchk == 0:
        aline = create_html_table(all_list, states)
#
#--- found both none and other cases
#
    else:
        all_list = [n_list] + all_list

        tstates = ['none']
        for state in states:
            if state != 'none':
                tstates.append(state)

        aline = create_html_table(all_list, tstates)
#
#--- print out html page
#
    line = '<!DOCTYPE html>\n'
    line = line + '<html>\n'
    line = line + '<head>\n'
    line = line +'    <title>MTA Trending: "  ' + msid + ' limit table  "</title>\n'
    line = line +'    <style>\n'
    line = line +'    </style>\n'
    line = line +'</head>\n'
    line = line +'<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FAEBD7;'
    line = line +'font-family:Georgia, "Times New Roman", Times, serif">\n'
    line = line +'<h2>' + msid.upper() + ' (' + unit + ')</h2>\n'

    line = line + aline

    line = line + '</body>\n</html>\n'

    outdir  = web_dir + group.capitalize() + '/Limit_table/'
    cmd     = 'mkdir -p ' + outdir
    os.system(cmd)
    outname = outdir  + msid + '_limit_table.html'
    with open(outname, 'w') as fo:
        fo.write(line)
                
#---------------------------------------------------------------------------------
#-- combine_same_start: combine limit lists of the same start time              --
#---------------------------------------------------------------------------------

def combine_same_start(n_list):
    """
    combine limit lists of the same start time 
    input:  n_list  --- a list of lists [<time>, <yl>, <yu>, <rl>, <ru>]
    output: s_list  --- a list of lists with combined list
    """
    s_list = []
    nlen   = len(n_list)
    if nlen == 1:
        return n_list

    skip = 0
    for k in range(0, nlen-1):
        if skip  > 0:
            skip = 0
            continue
#
#--- we assume that the same starting time lists are next each other
#
        if n_list[k][0] == n_list[k+1][0]:
            a_list = combine_two_limits(n_list[k], n_list[k+1])
            s_list.append(a_list)
            skip = 1
            continue
        else:
            s_list.append(n_list[k])

    s_list.append(n_list[nlen-1])
    return s_list

#---------------------------------------------------------------------------------
#-- combine_two_limits: combine two limit table; take wider range              ---
#---------------------------------------------------------------------------------

def combine_two_limits(a_list, b_list):
    """
    combine two limit table; take wider range
    input:  a_list  --- a list of limits
            b_list  --- another list of limits
    output: combined list
            assume that the list has [<time>, <yl>, <yu>, <rl>, <ru>]
    """
    if a_list[1] <= b_list[1]:
        yl = a_list[1]
    else:
        yl = b_list[1]

    if a_list[2] >= b_list[2]:
        yu = a_list[2]
    else:
        yu = b_list[2]

    if a_list[3] <= b_list[3]:
        rl = a_list[3]
    else:
        rl = b_list[3]

    if a_list[4] >= b_list[4]:
        ru = a_list[4]
    else:
        ru = b_list[4]

    return [a_list[0], yl, yu, rl, ru]

#---------------------------------------------------------------------------------
#-- compress_time_periods: check whether the limits are same as one before      --
#---------------------------------------------------------------------------------

def compress_time_periods(a_list):
    """
    check whether the limits are same as one before and if so, remove that set
    input:  a_list  --- a list of lists of [<time>, <y_low>, <y_up>, <r_low>, <r_up>,..]
    output: n_list  --- an updated lists of lists
    """

    alen   = len(a_list)
    n_list = [a_list[0]]
    for k in range(0, alen-1):
        if a_list[k][1] != a_list[k+1][1]:
            n_list.append(a_list[k+1])
            continue

        elif a_list[k][2] != a_list[k+1][2]:
            n_list.append(a_list[k+1])
            continue

        elif a_list[k][3] != a_list[k+1][3]:
            n_list.append(a_list[k+1])
            continue

        elif a_list[k][4] != a_list[k+1][4]:
            n_list.append(a_list[k+1])
            continue

        else:
            continue

    return n_list


#---------------------------------------------------------------------------------
#-- extend_start_range: if the begining is not 1999:201 or before, set date to 1999:201
#---------------------------------------------------------------------------------

def extend_start_range(t_list):
    """
    if the begining is not 1999:201 or before, set date to 1999:201
    input:  t_list  --- a list of [[<time>, ....], [...], ...]
    output  t_list  --- an updated list
            tchk    --- if 1, the the date is updated. otherwise, it is the same as before
    """
    tchk = 0
    if t_list[0][0] > obegin:
        t_list[0][0] = 1999.55068493
        tchk = 1

    return [t_list, tchk]

#---------------------------------------------------------------------------------
#-- create_html_table: create html data table                                   --
#---------------------------------------------------------------------------------

def create_html_table(all_list, states):
    """
    create html data table
    input:  all_list    --- a list of lists of data: [<time>, <y_low>, <y_top>, <r_low>, <r_top>]
            states      --- a list of states
    output: aline       --- html string of table part
    """
    tlen  = len(states)
    if tlen == 1 and states[0] == 'none':
        all_list = [all_list]
    aline = '<table border=1 cellspan=2>\n'
    for m in range(0, tlen):
        a_list = all_list[m]
#
#--- unless the state is 'none', put the header to show which state these limits show
#
        if len(states) > 1 or  states[m] != 'none':
            aline  = aline + '<tr><td colspan=6 style="text-align:left;">State: ' + states[m] + '</td></tr>\n'

        aline = aline + '<tr><th>Start Time</th><th>Stop Time</th>\n'
        aline = aline + '<th>Yellow Lower</th><th>Yellow Upper</th>\n'
        aline = aline + '<th>Red Lower</th><th>Red Upper</th></tr>\n'

        alen  = len(a_list)
        for k in range(0, alen):
#
#--- setting start and stop time. if the ending is open, use '---'
#
            aline = aline + '<tr><td>' + format_data(a_list[k][0])  + '</td>\n'
            if k < alen-1:
                aline = aline + '<td>' + format_data(a_list[k+1][0])  + '</td>\n'
            else:
                aline = aline + '<td> --- </td>\n'
#
#--- yellow lower, yellow upper, red lower, red upper
#
            aline = aline + '<td>' + format_data(a_list[k][1]) + '</td>\n'
            aline = aline + '<td>' + format_data(a_list[k][2]) + '</td>\n'
            aline = aline + '<td>' + format_data(a_list[k][3]) + '</td>\n'
            aline = aline + '<td>' + format_data(a_list[k][4]) + '</td>\n'
            aline = aline + '</tr>\n'
    if tlen == 0:
        aline = aline + '<tr><td>1999.0</td><td> --- <td>\n'
        aline = aline + '<td>-998</td><td>998</td><td>-999</td><td>999</td>\n'
        aline = aline + '</tr>\n'

    aline = aline + '</table><br />\n'

    return aline

#---------------------------------------------------------------------------------
#-- format_data: format digit to clean form                                    ---
#---------------------------------------------------------------------------------

def format_data(val):
    """
    format digit to clean form
    input:  val --- numeric value
    output: val --- cleaned up value
    """
    try:
        val = float(val)
    except:
        return val

    if abs(val) < 0.01:
        val = '%3.3e' % val
    elif val > 10000:
        val = '%3.2e' % val
    else:
        val = '%3.2f' % round(val, 2)

    return val

#---------------------------------------------------------------------------------
#-- create_group_dict: create msid <---> group dictionary                      ---
#---------------------------------------------------------------------------------

def create_group_dict():
    """
    create msid <---> group dictionary
    input:  none but read from <house_keeping>/msid_list
    output: g_dict  --- a dictionary of msid <--> group
    """
    ifile  = house_keeping + 'msid_list_all'
    data   = mcf.read_data_file(ifile)
    g_dict = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0].strip()
        group = atemp[1].strip()
        g_dict[msid] = group

    return g_dict

#---------------------------------------------------------------------------------

if __name__ == '__main__':

    update_limit_table()
