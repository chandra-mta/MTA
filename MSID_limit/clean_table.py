#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       clean_table.py: clean up op_limits.db table                             #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Sep 27, 2021                                       #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import time
import random
import math

#
#--- reading directory list
#
path = '/data/mta/Script/MSID_limit/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)

import mta_common_functions as mcf 

rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- database file name
#
db_file = main_dir + 'op_limits.db'

#-------------------------------------------------------------------------------
#-- clean_table: clean up op_limits.db                                         -
#-------------------------------------------------------------------------------

def clean_table():
    """
    clean up op_limits.db
    input:  op_limits.db
    output: cleaned up op_limits.db
    """
#
#--- if the change was a made a while ago, don't clean up
#
    current = time.time()
    updated = os.path.getmtime(db_file)
    diff    = current - updated
    if diff > 1800:
        exit(1)
#
#--- first, correct data format; the data part is delimited by tab, not a space
#
    data = mcf.read_data_file(db_file)
    
    save = []
    for ent in data:
        if ent == '':
            save.append('')
        elif ent[0] == '#':
            save.append(ent)
            continue
        else:
            atemp = re.split('#', ent)
            btemp = re.split('\s+', atemp[0])
            if len(btemp[0]) < 8:
                line =btemp[0].strip() + '\t\t'
            else:
                line =btemp[0].strip() + '\t'
    
            line = line + '%0.2f\t' % round(float(btemp[1].strip()), 2)
            line = line + '%0.2f\t' % round(float(btemp[2].strip()), 2)
            line = line + '%0.2f\t' % round(float(btemp[3].strip()), 2)
            line = line + '%0.2f\t' % round(float(btemp[4].strip()), 2)
            line = line + '%0.1f\t' % round(float(btemp[5].strip()), 2)
            try:
                line = line + '#' + atemp[1]
            except:
                pass
             
            save.append(line)
#
#--- now reorder each msid entry by time and remove duplicates
#
    msid_list = []
    prev      = ''
    m_dict    = {}
#
#--- first collect all entries of each msid and create msid list and disctionary
#--- with msid as a key. the dict points to a lists holds all entries of each msid
#
    for ent in save:
        if ent == '':
            continue
    
        chk = 0
        if ent[0] == '#':
            continue
        else:
            atemp = re.split('\s+', ent)
            msid  = atemp[0]
            try:
                out = m_dict[msid]
            except:
                out = []
            out.append(ent)
            m_dict[msid] = out
    
            if msid != prev:
                if msid in msid_list:
                    continue
                else:
                    if not (msid in msid_list):
                        msid_list.append(msid)
                    prev = msid
                    continue
            else:
                continue
#
#--- go through each msid/dict entry and remove duplicate and sort in time order
#
    for msid in msid_list:
        t_dict = {}
        t_list = []
        for ent in m_dict[msid]:
            atemp = re.split('\t+', ent)
            stime = float(atemp[5])
            t_dict[stime] = ent
            t_list.append(stime)
    
        t_list = sorted(list(set(t_list)))
        out = []
        for stime in t_list:
            out.append(t_dict[stime])
    
        m_dict[msid] = out
#
#--- back to the table and print create a clean table
#
    line = ''
    prev = ''
    done = []
    for ent in data:
        if ent == '':
            line = line + '\n'
        elif ent[0] == '#':
                line = line + ent + '\n'
                continue
        else:
            atemp = re.split('\s+', ent)
            msid  = atemp[0].replace('#', '')
            if msid == prev:
                continue
            if msid in done:
                prev = msid
                continue
            done.append(msid)
            out = m_dict[msid]
            for val in out:
                line = line + val + '\n'
            prev = msid
#
#--- update the op_limits.db 
#
    cmd = 'mv ' + db_file + ' ' + db_file + '~'
    os.system(cmd)

    with open(db_file, 'w') as fo:
        fo.write(line)

    cmd = 'cp -f ' + db_file + ' /data/mta4/MTA/data/op_limits/op_limits.db'
    os.system(cmd)

#-------------------------------------------------------------------------------
#-- check_entry: check whether new op_limit.db is missing any entries from the older data set
#-------------------------------------------------------------------------------

def check_entry():
    """
    check whether new op_limit.db is missing any entries from the older data set
    input: none but read from <past_dir>/op_limits.db_<mmddyy>
    output: email notification sent out if it find a missing data
    """
    cmd = 'ls -lrt ' + main_dir + '/Past_data/op_limits* > ' + zspace
    os.system(cmd)
    olist = mcf.read_data_file(zspace, remove=1)
    out   = olist[-1]
    atemp = re.split('\s+', out)
    lfile1 = atemp[-2]
    lfile2 = atemp[-1]

    cmd   = 'diff ' + lfile1 + ' ' + lfile2 + ' > ' + zspace
    os.system(cmd)
    out  = mcf.read_data_file(zspace, remove=1)
    missing = []
    for ent in out:
        if ent[0] == ">":
            continue
        else:
            missing.append(ent)

    if len(missing) > 0:
        line = 'Following lines are missing/different in the updata data from the past data:\n\n'
        for ent in missing:
            line = line + ent + '\n'

        with open(zspace, 'w') as fo:
            fo.write(line)

        cmd = 'cat ' + zspace + ' |mailx -s "Subject: Possible op_limit Problems" msobolewska@cfa.harvard.edu'
        os.system(cmd)

        mcf.rm_files(zspace)

#------------------------------------------------------------------------

if __name__ == "__main__":

    clean_table()
    check_entry()
