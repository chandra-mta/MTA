#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#       read_limit_table.py: read a limit table and create msid <--> limit dictionary       #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 01, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
from astropy.io.fits import Column
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf  #---- contains other functions commonly used in MTA scripts
import envelope_common_function as ecf  #---- contains other functions commonly used in envelope

kptops = 0.145038             #--- kp to psia conversion

#--------------------------------------------------------------------------------
#-- get_limit_table: create msid <---> limit table dictionary                 ---
#--------------------------------------------------------------------------------

def get_limit_table():
    """
    create msid <---> limit table dictionary
    input:  none but read from <limit_dir>/op_limit_new.db
    output: lim_dict    --- a dict of lists of limit data. Each inner list contains:
                    [
                     <period start time>, <period end time>, cnd_msid, 
                     <possibe key lists>, <limit dictonary: key <--> [y_low, y_top, r_low, r_top]
                    ]
            cnd_dict    --- a dictionary of msid <---> condition msid
    """
#
#--- create msid <--> unit dict
#
    [unit_dict, disc_dict]  = ecf.read_unit_list()
#
#--- read limit data table
#
    ifile = limit_dir + 'Limit_data/op_limits_new.db'
    ldata = mcf.read_data_file(ifile)
#
#--- create a list of lists in the form of 
#--- [<time stamp>, <condition msid>, <switch>, <y_low>, <y_top>, <r_low>, <r_top>]
#
    lim_dict = {}
    cnd_dict = {}
    msid     = ''
    save     = []
    csave    = 'none'
    for ent in ldata:
        if ent[0] == '#':
            continue

        atemp = re.split('#', ent)

        btemp = re.split('\t+', atemp[0])
#
#--- if the msid is same as one before add the data to the save
#
        if btemp[0].strip() == msid:
            try:
                unit = unit_dict[msid].lower()
            except:
                unit = ''
            if unit  == 'psia':
                alist =[int(float(btemp[7])), btemp[5], btemp[6], 
                    float(btemp[1])/kptops, float(btemp[2])/kptops, 
                    float(btemp[3])/kptops, float(btemp[4])/kptops]
            else:
                alist =[int(float(btemp[7])), btemp[5], btemp[6], 
                    float(btemp[1]), float(btemp[2]), float(btemp[3]), float(btemp[4])]
            save.append(alist)
            cnd_msid = btemp[5].strip()
            if cnd_msid != 'none':
                csave = cnd_msid

        else:
#
#--- the first msid set
#
            if msid == '':
                msid = btemp[0].strip()
                try:
                    unit = unit_dict[msid].lower()
                except:
                    unit = ''
                if unit == 'psia':
                    alist =[int(float(btemp[7])), btemp[5], btemp[6], 
                    float(btemp[1])/kptops, float(btemp[2])/kptops, 
                    float(btemp[3])/kptops, float(btemp[4])/kptops]
                else:
                    alist =[int(float(btemp[7])), btemp[5], btemp[6], 
                        float(btemp[1]), float(btemp[2]), float(btemp[3]), float(btemp[4])]
                save = [alist]
                csave = btemp[6].strip()
            else:
#
#--- add ending time of the limit check: year 2200.01.01
#
                alist = [6374591994, 'none', 'none', -9999998.0, 9999998.0, -9999999.0, 9999999.0]
                save.append(alist)
                asave = create_limit_table(save)
                lim_dict[msid] = asave
                cnd_dict[msid] = csave
#
#--- start for the next msid
#
                msid  = btemp[0].strip()
                try:
                    unit = unit_dict[msid].lower()
                except:
                    unit = ''
                if unit == 'psia':
                    alist =[int(float(btemp[7])), btemp[5], btemp[6], 
                    float(btemp[1])/kptops, float(btemp[2])/kptops, 
                    float(btemp[3])/kptops, float(btemp[4])/kptops]
                else:
                    alist =[int(float(btemp[7])), btemp[5], btemp[6], 
                        float(btemp[1]), float(btemp[2]), float(btemp[3]), float(btemp[4])]
                save  = [alist]
                csave = 'none'
#
#--- the last entry
#
    if save != []:
        alist = [6374591994, 'none', 'none', -9999998.0, 9999998.0, -9999999.0, 9999999.0]
        save.append(alist)
        asave = create_limit_table(save)
        lim_dict[msid] = asave
        cnd_dict[msid] = csave

    return [lim_dict, cnd_dict]

#--------------------------------------------------------------------------------
#-- create_limit_table: create condition dependent limit data table list       --
#--------------------------------------------------------------------------------

def create_limit_table(limit_save):
    """
    create condition dependent limit data table list
    input: limit_save   --- a list of lists of limits: 
                            [<time>,<cnd msid>,<condition>, <y low>, <y up>, <r low>, <r up>] 
    output: asave   --- a list of lists of limit data. Each inner list contains:
                    [
                     <period start time>, <period end time>, cnd_msid, 
                     <possibe key lists>, <limit dictonary: key <--> [y_low, y_top, r_low, r_top]
                    ]
    """
#
#--- now find out all switch values (such as 'none', 'on', 'off', etc) 
#--- and starting time of each period
#
    slist  = []
    tlist  = []
    for ent in limit_save:
        slist.append(ent[2])
        tlist.append(ent[0])
#
#--- clean switch list 
#
    slist = list(set(slist))
    slen  = len(slist)
#
#--- initialize limit dict
#
    a_dict = {}
    for ent in slist:
        a_dict[ent] = [-9999998.0, 9999998.0, -9999999.0, 9999999.0]

    a_dict['none'] = [-9999998.0, 9999998.0, -9999999.0, 9999999.0]
#
#--- make a list of unique starting time list in ascending order
#
    tlist = sorted(tlist)
    temp  = [tlist[0]]
    prev  = tlist[0]
    for ent in tlist[1:]:
        if ent == prev:
            continue
        else:
            temp.append(ent)
            prev = ent
    tlist = temp
    tlen  = len(tlist)
#
#--- make a list of lists of:
#---    [<starting time>, <ending time>, <key list>,<limit dictionary with cond_msid as key>]
#
    asave = []
    for k in range(0, tlen-1):
#
#--- save in a list
#
        temp = []
        temp.append(tlist[k])
        temp.append(tlist[k+1])
        temp.append(slist)
#
#--- keep limits in a temporary dict
#
        t_dict = {}
        for key in slist:
#
#--- first time, set it to a default limit range
#
            if k == 0:
                t_dict[key] = a_dict[key]
#
#--- otherwise, set it to the previous limit range
#
            else:
                t_dict[key] = asave[k-1][3][key]
#
#--- now check whether the limits are updated in this period
#
        k_list = []
        for ent in limit_save:
            if ent[0] == tlist[k]:
                key = ent[2]
                limits = [ent[3], ent[4], ent[5], ent[6]]
                t_dict[key] = limits
#
#--- k_list contains the keys showed up this round
#
                k_list.append(key)
#
#--- if there is 'none' entry and some keys are missing
#--- substitute the missing key entry with 'none' list
#
##        k_list = list(set(k_list))
##        if 'none' in k_list:
##            dlist = list(set(slist) - set(k_list))
##            for key in dlist:
##                t_dict[key] = t_dict['none']


        temp.append(t_dict)
        asave.append(temp)

    return asave

#--------------------------------------------------------------------------------

if __name__ == "__main__":

    [limit_dict, cnd_dict]  = get_limit_table()

    out = limit_dict['1pin1at']
    print(str(out))

    out = cnd_dict['1pin1at']
    print("\nSTATE: " + str(out))


    print("\n\n")
#
#    out = limit_dict['1dahbcu']
#    print(str(out))
#
#    print("3 : " + str(out[3][3]))
#
#    ddict = out[4][3]['on']
#    print("\nON CASE: " + str(ddict))
#
#    out = cnd_dict['1dahbcu']
#    print("\nSTATE: " + str(out))
#
#
#    print("\n\n")
#
#    out = limit_dict['1dahbcu']
#    print(str(out))
#
#    print("3 : " + str(out[3][3]))
#
#    ddict = out[4][3]['on']
#    print("\nON CASE: " + str(ddict))
#
#    out = cnd_dict['1dahbcu']
#    print("\nSTATE: " + str(out))
#
#    out = limit_dict['airu1g1t']
#    print(str(out))
