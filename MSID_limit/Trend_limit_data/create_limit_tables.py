#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       create_limit_tables.py: create limit databases for msid trending                #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvrad.edu)                                   #
#                                                                                       #
#           last update: Oct 26, 2021                                                   #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import copy
import string
import math
import sqlite3
import Ska.engarchive.fetch as fetch
from Ska.engarchive import fetch_eng

limit_dir = '/data/mta/Script/MSID_limit/Trend_limit_data/'

#------------------------------------------------------------------------------------------
#-- create_limit_tables: create limit databases for msid trending                        --
#------------------------------------------------------------------------------------------

def create_limit_tables():
    """
    create limit databases for msid trending
    input:  none but read from op_limits.db and glimmon data 
    output: Limit_data/*_limit
    """
#
#--- read op_limits.db and create dictionaries
#
    [u_dict, d_dict, v_dict] = create_data_dict()
#
    ifile = limit_dir + 'house_keeping/msid_list'
#
#--- create limit data table
#
    aline = extract_limit(ifile, u_dict, d_dict, v_dict)
#
#--- print out the result
#
    out = limit_dir + 'Limit_data/op_limits_new.db'
    with open(out, 'w') as fo:
        fo.write(aline)

#------------------------------------------------------------------------------------------
#-- create_data_dict: create msid <--> unit/description/limit data dictionaries
#------------------------------------------------------------------------------------------

def create_data_dict():
    """
    read mta_limits.db and create msid <--> unit/description/data dictionaries
    input:none but read from op_limits.db
    output: u_dict  --- a dictionary of msid <---> unit
            d_dict  --- a dictionary of msid <---> description
            v_idct  --- a dictionary of msid <---> a list of lists of limit data
                        [<lower yellow>, <upper yellow>, <lower red>, <upper red>, <start time>]
    """
#
#--- read units and descriptions of msids and  create dictionaries
#
    ifile = limit_dir + 'house_keeping/msid_descriptions'
    with open(ifile, 'r') as f:
        data = [line.strip() for line in f.readlines()]

    u_dict = {}
    d_dict = {}
    for ent in data:
        atemp = re.split('#', ent)
        msid  = atemp[0].strip().lower()
        unit  = atemp[2].strip()
        desc  = atemp[3].strip()
        u_dict[msid] = unit
        d_dict[msid] = desc
#
#--- read mta limit data
#
    ifile = limit_dir + 'house_keeping/mta_op_limits.db'
    with open(ifile, 'r') as f:
        data = [line.strip() for line in f.readlines()]

    v_dict = {}
    for ent in data:
        if ent[0] == '#':
            continue
        atemp = re.split('#', ent)
        btemp = re.split('\t+', atemp[0])
        msid  = btemp[0].strip().lower()
    
        try:
            vlist = [[btemp[1], btemp[2], btemp[3], btemp[4], btemp[7]]]
        except:
            continue
        try:
            alist = v_dict[msid]
            alist = alist + vlist
            v_dict[msid] = alist
        except: 
            v_dict[msid] = vlist

    return [u_dict, d_dict, v_dict]

#------------------------------------------------------------------------------------------
#-- extract_limit: read glimmon limit database and create limit database                ---
#------------------------------------------------------------------------------------------

def extract_limit(ifile, u_dict, d_dict, v_dict):
    """
    read glimmon limit database and create limit database. if glimmon does not have
    the data, mta's op_limit.db values are used.
    input:  ifile   --- a list of msids
            u_dict  --- a dictionary of msid <---> unit
            d_dict  --- a dictionary of msid <---> description
            v_idct  --- a dictionary of msid <---> a list of lists of limit data
    output: aline   --- a strings of data table
    """
    with open(ifile, 'r') as f:
        data = [line.strip() for line in f.readlines()]
    msid_list = []
    for ent in  data:
            atemp = re.split('\s+', ent)
            msid_list.append(atemp[0].strip().lower())
    
    
    glimmon   = '/data/mta/Script/MSID_limit/glimmondb.sqlite3'
    db        = sqlite3.connect(glimmon)
    cursor    = db.cursor()
    
    aline = '#\n'
    aline = aline + '# MSID      Y Lower     Y Upper     R Lower     R Upper     '
    aline = aline + 'Cnd MSID    Sate    Time\t\t\t\t\t\t\t\t\t\tDescription'
    aline = aline + '          Uint     Limit Group\n'
    aline = aline + '#\n'

    for msid in msid_list:
        msid.strip()

        print("MSID: " + msid)

        cmd = "SELECT a.setkey, a.default_set, a.mlmenable, a.switchstate, a.mlimsw, "
        cmd = cmd + "a.caution_low, a.caution_high, a.warning_low, a.warning_high, "
        cmd = cmd + "a.datesec FROM limits AS a WHERE a.msid ='" + msid + "'"
        cursor.execute(cmd)
        allrows = cursor.fetchall()
    
        try:
            unit  = u_dict[msid]
        except:
            unit  = 'na'
        try:
            desc  = d_dict[msid]
        except:
            desc  = '                        NA          '
#
#--- mta case
#
        if len(allrows) == 0:
    
            try:
                vlist = v_dict[msid]
            except:
                vlist = [['-9999998.0', '9999998.0', '-9999999.0', '9999999.0', '48815999']]
    
            for elist in vlist:

                if len(msid) < 8:
                    line = msid + '\t\t'
                else:
                    line = msid + '\t'

                elist[0] = "%3.2f" % (float(elist[0]))
                elist[1] = "%3.2f" % (float(elist[1]))
                elist[2] = "%3.2f" % (float(elist[2]))
                elist[3] = "%3.2f" % (float(elist[3]))
                line = line + adjust_length(elist[0])
                line = line + adjust_length(elist[1])
                line = line + adjust_length(elist[2])
                line = line + adjust_length(elist[3])

                line = line + 'none\t\tnone\t' + str(int(float(elist[4])))
                line = line + '\t#' + "%50s" % desc + '\t # \t' +   unit + '\t # \tmta\n'
                aline = aline + line
#
#--- glimmon case
#
        else:
#
#--- first replace none state with others if they exist
#
            key_list = []
            st_list  = []
            cnd_list = []
            for elist in allrows:
               key_list.append(elist[0]) 
               st_list.append(elist[3])
               cnd_list.append(elist[4])
#
#--- check whether there is switch
#
               switch = 0
               for ent in cnd_list:
                   if ent != 'none':
                       switch = 1
                       break
#
#---find key <--> state correspondence
#
            k_set = list(set(key_list))
            k_len = len(k_set)
            key_dict = {}
#
#--- if there are two state with switch msid, assume that they are on and off states
#
            if (k_len == 2) and (switch > 0):
                key_dict[0] = 'on'
                key_dict[1] = 'off'
            else:
                for key in k_set:
                    key_dict[key] = 'none'

            for k in range(0, len(key_list)):
                if st_list[k] != 'none':
                    key_dict[key_list[k]] = st_list[k]
#
#--- now replace 'none' state with appropriate state (if they exist)
#
            temp_list = []
            for elist in allrows:
                elist = list(elist)
                elist[3] = key_dict[elist[0]]
                temp_list.append(elist)
#
#--- a base data list updated. start farther checking
#
            allrows = temp_list

            temp_save  = []
            state_list = []
            time_list  = []
            chk_list   = []
            cnd_msid   = 'none'
            for elist in allrows:
                elist = list(elist)
#
#--- the starting time of glimmon is the end of year 2000; extend it to 1999
#
                if  int(elist[-1]) == 83620796:
                    elist[-1] = 31536000
                else:
                    elist[-1] = int(elist[-1])

#
#--- limit checking is turned off if "mlmenable" is 0
#
                if elist[2] == 0:
                    elist[5] = '-9999998.0'
                    elist[6] = ' 9999998.0'
                    elist[7] = '-9999999.0'
                    elist[8] = ' 9999999.0'
#
#--- if limit checking is still on, format the limit values
#
                else:
                    if unit.upper() == 'K':
                        elist[5] = "%3.2f" % temp_to_k(elist[5], msid)
                        elist[6] = "%3.2f" % temp_to_k(elist[6], msid)
                        elist[7] = "%3.2f" % temp_to_k(elist[7], msid)
                        elist[8] = "%3.2f" % temp_to_k(elist[8], msid)
                    else:
                        if abs(float(elist[5])) < 0.01:
                            elist[5] = "%2.3e" % (float(elist[5]))
                            elist[6] = "%2.3e" % (float(elist[6]))
                            elist[7] = "%2.3e" % (float(elist[7]))
                            elist[8] = "%2.3e" % (float(elist[8]))
                        else:
                            elist[5] = "%3.2f" % (float(elist[5]))
                            elist[6] = "%3.2f" % (float(elist[6]))
                            elist[7] = "%3.2f" % (float(elist[7]))
                            elist[8] = "%3.2f" % (float(elist[8]))

                temp_save.append(elist)
                state_list.append(elist[3])
                time_list.append(elist[-1])
                chk_list.append(elist[2])
                if elist[3] != 'none':
                    cnd_msid = elist[4]

            s_list   = list(set(state_list))

            if len(s_list) == 1:
                lim_list = temp_save
#
#--- if the limit lists start the state of "none" but added condition 
#--- after that, assume that "none" limits are used for all states, until
#--- the other states are added to the list; so add the "none" state 
#--- limits to other state cases
#
            else:
                slen     = len(state_list)
                schk     = 0
                lim_list = []
                for k in range(0, slen):
                    lim_list.append(temp_save[k])
#
#--- check whether the following state is also "none"
#
                    if (k < slen-1) and (schk == 0) and (state_list[k] == 'none'):
                        if state_list[k+1] == 'none':
                            for state in s_list:
                                if state == 'none':
                                    continue
                                atemp = copy.deepcopy(temp_save[k])
                                atemp[3] = state
                                atemp[4] = cnd_msid
                                lim_list.append(atemp)
#
#--- the following state is not "none", but there are a time gap
#
                        elif time_list[k] < time_list[k+1]:
                            for state in s_list:
                                if state == 'none':
                                    continue
                                atemp = copy.deepcopy(temp_save[k])
                                atemp[3] = state
                                atemp[4] = cnd_msid
                                lim_list.append(atemp)
#
#--- once the other than "none" state starts in the limit, stop the procedure
#
                        else:
                            schk = 1
                    else:
                        schk = 1
#
#--- removing the same time entry; choose wider limit range
#
            l_len = len(lim_list)
            if l_len > 1:
                temp_list = []
                for m in range(0, l_len-1):
                    prev_list = lim_list[m]
                    ptime  = prev_list[-1]
                    pstate = prev_list[3]
                    chk    = 0
                    for k in range(m+1, l_len):
                        this_list = lim_list[k]
                        ctime  = this_list[-1]
                        cstate = this_list[3]
                        if (ptime == ctime) and (pstate == cstate):
                            if (this_list[5] < prev_list[5]) and (this_list[6] > prev_list[6]):
                                chk = 1
                                break
                            else:
                                this_list[5] = prev_list[5]
                                this_list[6] = prev_list[6]
                                this_list[7] = prev_list[7]
                                this_list[8] = prev_list[8]
                                lim_list[k]  = this_list
                                chk = 1
                                break
                    if chk == 0:
                        temp_list.append(prev_list)

                temp_list.append(lim_list[-1])
                lim_list = temp_list
#
#--- write out all the limit lists
#
            for elist in lim_list:

                if len(msid) < 8:
                    line = msid + '\t\t' 
                else:
                    line = msid + '\t' 

                line = line + adjust_length(elist[5])
                line = line + adjust_length(elist[6])
                line = line + adjust_length(elist[7])
                line = line + adjust_length(elist[8])

                line = line + adjust_length(elist[4])

                if len(elist[3]) < 4:
                    line = line + str(elist[3]) + '\t'
                else:
                    line = line + str(elist[3])

                line = line + '\t' + str(elist[-1])
                line = line + '\t#' + "%50s" % desc + '\t # \t' +   unit + '\t # \tglimmon\n'
                aline = aline + line
    
    return aline

#------------------------------------------------------------------------------------------
#-- find_unit: find engineering data unit                                                --
#------------------------------------------------------------------------------------------

def find_unit(msid):
    """
    find engineering data unit
    input:  msid    --- msid
    output: unit    --- uint
    """

    data = fetch_eng.Msid(msid, '2019:001')
    return data.unit

#------------------------------------------------------------------------------------------
#-- temp_to_k: convert C and F temperature to K                                          --
#------------------------------------------------------------------------------------------

def temp_to_k(val, msid):
    """
    convert C and F temperature to K
    input:  val     --- value
            msid    --- msid
    output: val     --- converted value if it is C or F
    """

    try:
        unit = find_unit(msid)
    except:
        return val

    if unit == 'K':
        try:
            out =  float(val)
        except:
            out = val

    elif unit == 'DEGC':
        try:
            out = float(val) + 273.15
        except:
            out = val

    elif unit == 'DEGF':
        try:
            out = 5.0 * (float(val) - 32.0) / 9.0 + 273.15
        except:
            out = val
    else:
        try:
            out = float(val)
        except:
            out = val

    return out

#------------------------------------------------------------------------------------------
#-- adjust_length: adjust length of the string                                           --
#------------------------------------------------------------------------------------------

def adjust_length(val):
    """
    adjust length of the string
    input:  val --- value to be adjusted
    output: val --- length adjusted string of the vlaue
    """
    
    vlen = len(val)
    if vlen < 4:
        val = val + '\t\t\t'
    elif vlen < 8:
        val = val + '\t\t'
    elif vlen < 12:
        val = val + '\t'

    return val

#------------------------------------------------------------------------------------------

if __name__ == "__main__":

    create_limit_tables()



