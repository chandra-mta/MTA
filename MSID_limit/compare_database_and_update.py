#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#       compare_database_and_update.py: compare the current mta limit data base     #
#                                       to glimmon and update the former            #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Sep 27, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import random
import math
import sqlite3
import unittest
import time
import Chandra.Time

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
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few names etc
#
mta_op_limit = '/data/mta4/MTA/data/op_limits/op_limits.db'
glimmon      = main_dir + 'glimmondb.sqlite3'
admin        = 'msobolewska@cfa.harvard.edu'
temp_opfile  = main_dir + 'op_limits_new'

#-----------------------------------------------------------------------------------
#-- compare_database_and_update: compare the current mta limit data base to glimmon and update the former
#-----------------------------------------------------------------------------------

def compare_database_and_update():
    """
    compare the current mta limit data base to glimmon and update the former
    input: none, but read from  /data/mta4/MTA/data/op_limits/op_limits.db
           and glimmondb.sqlite3. you may need to download this from the web
    output: updated op_limits.db (locally saved)
    """
#
#--- read the special_msid_list
#
    sfile = house_keeping + 'special_msid_list'
    special_msid_list = mcf.read_data_file(sfile)
#
#--- get time stamps
#
    today   = time.strftime('%Y:%j:00:00:00', time.gmtime())
    stime   = Chandra.Time.DateTime(today).secs
    atemp   = re.split(':', today)
    today   = atemp[0] + ':' + atemp[1]
#
#--- download the current glimmon sql data base
#
    download_glimmon()
#
#-- read the current op_limit.db
#
    [msids, y_min, y_max, r_min, r_max, fline, tind, org_data] = read_mta_database()
#
#--- save updated line in a msid based dictionary
#
    updates      = {}

    for msid in msids:
#
#--- if the msid is in the special_msid_list, skip --- they are manually defined by mta
#
        if msid.lower() in special_msid_list:
            continue
#
#--- there are temperature related msids based on K and C. update both
#
        ind = tind[msid]
        name = msid
#
#--- temp msid with C ends "TC"
#
        tail = name[-2] + name[-1]
        if tail == 'TC':
            name = msid[:-1]
            ind = 0
        if name[-1] == 'T':
            ind = 1
        mc = re.search('ARWA', msid)
        if mc is not None:
            ind = 1
#
#--- read data out from glimmon sqlite database
#
        out = read_glimmon(name, ind)

        if len(out) == 0:
            continue

        else:
#
#--- compare two database and save only updated data line
#
            [gy_min, gy_max, gr_min, gr_max] = out
            fy_min = float(gy_min)
            fy_max = float(gy_max)
            fr_min = float(gr_min)
            fr_max = float(gr_max)

            try:
                chk = 0
                ty_min = float(y_min[msid])
                ty_max = float(y_max[msid])
                tr_min = float(r_min[msid])
                tr_max = float(r_max[msid])
            except:
                chk = 1

            if (chk == 0) and ((ty_min == fy_min) and (ty_max == fy_max)  \
                and (tr_min == fr_min) and (tr_max == fr_max)):
                continue
            else:

                line = fline[msid]
                atemp = re.split('#', line)
                temp = re.split('\s+', atemp[0])

                if len(msid) < 8:
                    aline = msid.upper() + '\t\t'
                else:
                    aline = msid.upper() + '\t'

                aline = aline + "%3.2f\t" % (float(gy_min))
                aline = aline + "%3.2f\t" % (float(gy_max))
                aline = aline + "%3.2f\t" % (float(gr_min))
                aline = aline + "%3.2f\t" % (float(gr_max))
#
#--- time stamp 
#
                aline = aline + str(float(int(stime))) + ' #'
#
#--- new data entry indicator
#
                temp = re.split('\s+', atemp[1])
                org  = temp[-1].strip()
                bline = atemp[1].replace(org, today)

                line = aline + bline + '\n'

                updates[msid] = line

#
#--- now update the original data. append the updated line to the end of each msid entry
#
    prev  = ''
    sline = ''
    for ent in org_data:
        if ent == '':
            sline = sline + '\n'
            continue
        if ent[0] == '#':
            sline = sline + ent + '\n'
            continue

        if prev == "":
            atemp = re.split('\s+', ent)
            prev  = atemp[0]
            sline = sline + ent + '\n'
        else:
#
#--- for the case msid is the same as the previous; do nothing
#
            atemp = re.split('\s+', ent)
            if prev == atemp[0]:
                sline = sline + ent + '\n'
                continue
            else:
#
#--- if the msid changed from the last entry line, check there is an update 
#--- for the previous msid. if so, add the line before printing the current line
#
                try:
                    if prev.lower() in special_msid_list:
                        line = ent
                    else:
                        line = updates[prev] 
                        line = line + ent
                except:
                    line = ent

                sline = sline + line + '\n'

                atemp = re.split('\s+', ent)
                prev  = atemp[0]


    with open(temp_opfile, 'w') as fo:
        fo.write(sline)
#
#--- check whether there are any changes and if so, save/update databases
#
    test_and_save()

#-----------------------------------------------------------------------------------
#-- read_mta_database: read mta limit database                                    --
#-----------------------------------------------------------------------------------

def read_mta_database():
    """
    read mta limit database
    input: none but read data from database: <mta_op_limit>
    ouput:  msids   --- a list of msids
            y_min   --- a msid based dictionary of yellow lower limit
            y_max   --- a msid based dictionary of yellow upper limit
            r_min   --- a msid based dictionary of red lower limit
            r_max   --- a msid based dictionary of red upper limit
            fline   --- a msid based dictionary of the entire line belong to the msid (the last entry)
            tind    --- a msid based dictionary of an indicator 
                        that whether this is a temperature related msid and in K. 0: no, 1: yes
            data    --- a list of all lines read from the database
    """
#
#--- read the database
#
    data  = mcf.read_data_file(mta_op_limit)

    prev  = ''
    ymin  = ''
    ymax  = ''
    rmin  = ''
    rmax  = ''

    y_min = {}
    y_max = {}
    r_min = {}
    r_max = {}
    tind  = {}
    fline = {}
    msids = []
    for ent in data:
#
#--- skip the line which is commented out
#
        test = re.split('\s+', ent)
        mc   = re.search('#', test[0])

        if mc is not None:
            continue
#
#--- go through the data and fill each dictionary. if there are
#--- multiple entries for the particular msid, only data from the last entry is kept
#
        atemp = re.split('\s+', ent)
        if (prev != '') and (atemp[0] != prev):
            msids.append(prev)
            y_min[prev] = ymin
            y_max[prev] = ymax
            r_min[prev] = rmin
            r_max[prev] = rmax
            tind[prev]  = temp
            fline[prev] = line

        if len(atemp) > 4:
            line = ent
            prev = atemp[0]
            ymin = atemp[1]
            ymax = atemp[2]
            rmin = atemp[3]
            rmax = atemp[4]
#
#--- check whether this is a temperature related msid and it is in K
#
            temp = 0
            if atemp[-1] == 'K' or atemp[-2] == 'K':
                temp = 1


    return [msids, y_min, y_max, r_min, r_max, fline,  tind, data]


#-----------------------------------------------------------------------------------
#-- read_glimmon: read glimmondb.sqlite3 and return yellow and red lower and upper limits 
#-----------------------------------------------------------------------------------

def read_glimmon(msid, tind):
    """
    read glimmondb.sqlite3 and return yellow and red lower and upper limits
    input:  msid    --- msid
            tind    --- whether this is a temperature related msid and in K. O; no, 1: yes
    output: y_min   --- lower yellow limit
            y_max   --- upper yellow limit
            r_min   --- lower red limit
            r_max   --- upper red limit
    """

    msid = msid.lower()
#
#--- glimmon keeps the temperature related quantities in C. convert it into K.
#
    if tind == 0:
        add = 0
    else:
        add = 273.15

    db = sqlite3.connect(glimmon)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM limits WHERE msid='%s'" %msid)
    allrows = cursor.fetchall()

    if len(allrows) == 0:
        return []

    tup   = allrows[-1]
    #y_min = str(float(tup[11] + add))
    #y_max = str(float(tup[10] + add))
    #r_min = str(float(tup[13] + add))
    #r_max = str(float(tup[12] + add))

    y_min = "%3.2f" % (round(float(tup[11]) + add, 2))
    y_max = "%3.2f" % (round(float(tup[10]) + add, 2))
    r_min = "%3.2f" % (round(float(tup[13]) + add, 2))
    r_max = "%3.2f" % (round(float(tup[12]) + add, 2))

    return [y_min, y_max, r_min, r_max]

#-----------------------------------------------------------------------------------------
#-- download_glimmon: downloading glimmon data from the website                         --
#-----------------------------------------------------------------------------------------

def download_glimmon():
    """
    downloading glimmon data from the website
    input: none but read from:
            https://occweb.cfa.harvard.edu/occweb/FOT/engineering/thermal/AXAFAUTO_RSYNC/G_LIMMON_Archive/glimmondb.sqlite3
    output: './glimmondb.sqlite3'
    """
#
#--- save the last one
#
    cmd = 'mv -f  ' + glimmon + ' ' + glimmon + '~'
    os.system(cmd)

    with open('/home/isobe/.occpass' , 'r') as f:
        out = f.read().strip()
#
#--- download the database
#
    cmd = 'curl -u tisobe:' + out 
    cmd = cmd + ' https://occweb.cfa.harvard.edu/occweb/FOT/engineering/thermal/'
    cmd = cmd + 'AXAFAUTO_RSYNC/G_LIMMON_Archive/glimmondb.sqlite3 > ' +  glimmon

    os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- test_and_save: save a copy of op_limit.db and glimon to Past_data directory         --
#-----------------------------------------------------------------------------------------

def test_and_save():
    """
     save a copy of op_limit.db and glimon to Past_data directory and also 
     update the main mta limit database
     input: none but read from op_limits.db and the current mta limit database
     output: ./Past_data/op_limits.db_<time stamp>
             ./Past_data/glimmondb.sqlite3_<time stamp>
             /data/mta4/MTA/data/op_limits/op_limits.db
    """
#
#--- check whether the local file exist before start checking
#
    if not os.path.isfile(temp_opfile):
        return  False 
#
#--- check whether there are any differences from the current mta limit database
#
    cmd  = 'diff ' + mta_op_limit + ' ' +  temp_opfile + ' > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)
#
#--- if so, save a copy of op_limit.db and glimon to Past_data directory and also 
#--- update the main mta limit database
#
    if len(data) < 1:
        cmd = 'rm '  + temp_opfile
        os.system(cmd)
    else:
        cmd  = 'mv ' + temp_opfile + ' ' + main_dir +'op_limits.db'
        os.system(cmd)

        tail = time.strftime("%m%d%y", time.gmtime())
        cmd  = 'cp ' + main_dir + 'op_limits.db ' + main_dir + 'Past_data/op_limits.db_' + tail
        os.system(cmd)

        cmd = 'cp -f ' + main_dir + glimmon  + '/data/mta4/MTA/data/op_limits/.'
        os.system(cmd)

        cmd = 'cp ' + main_dir  +  glimmon + ' ' + main_dir + 'Past_data/' + glimmon + '_' + tail
        os.system(cmd)
#
#--- notify the changes to admin person
#
        line = 'There are some changes in mta limit database; '
        line = line + 'check /data/mta/Script/MSID_limit/* '
        line = line + 'and /data/mta4/MTA/data/op_limits/op_limits.db.\n'

        with  open(zspace, 'w') as fo:
            fo.write(line)

        cmd = 'cat ' + zspace + '| mailx -s "Subject: MTA limit database updated  " ' + admin
        os.system(cmd)

        mcf.rm_files(zspace)

        cmd = 'chgrp mtagroup ./*'
        os.system(cmd)
        cmd = 'chgrp mtagroup ./Past_data/*'
        os.system(cmd)
        cmd = 'chgrp mtagroup ' + mta_op_limit
        os.system(cmd)

    return True 

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_read_mta_database(self):

        [msids, y_min, y_max, r_min, r_max, fline, tind, org_data] = read_mta_database()

        print(str(msids[:10]))

        print(str(y_min['OHRTHR44']))
        print(str(y_max['OHRTHR44']))
        print(str(r_min['OHRTHR44']))
        print(str(r_max['OHRTHR44']))

        print(str(tind['OHRTHR44']))

#------------------------------------------------------------

    def test_read_glimmon(self):
    
        msid = 'OHRTHR44'
        #msid = '1CBAT'
        tind = 1
        out = read_glimmon(msid, tind)
        print(str(out))

        msid  = '1DAHBVO'
        tind = 1
        out = read_glimmon(msid, tind)
        print(str(out))

#------------------------------------------------------------

    def test_read_glimmon(self):

        download_glimmon()

        cmd =  'ls -lrt ' + glimmon + '> zzz'
        os.system(cmd)

        f   = open('zzz', 'r')
        test = f.read()
        print(test)
        cmd =  'rm zzz'
        os.system(cmd)

#-----------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- if you want to test the script, add "test" after
#--- compare_database_and_update.py
#
    test = 0
    if len(sys.argv) == 2:
        if sys.argv[1] == 'test':
            test = 1
            del sys.argv[1:]

    if test == 0:
        compare_database_and_update()
    else:
        unittest.main()

