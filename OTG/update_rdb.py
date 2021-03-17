#!/usr/bin/env  /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################
#                                                                               #
#   update_rdb.py: update dataseeker rdb files for ccdm, pacd, mups, and elbi   #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: May 23, 2019                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import time

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
#
#--- import several functions
#
import pcadfilter
import ccdmfilter
import maverage
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#-- run_rdb_updates: update dataseeker rdb files of ccdm, pacad, mups, and elbilow -
#-----------------------------------------------------------------------------------

def run_rdb_updates():
    """
    update dataseeker rdb files of ccdm, pacad, mups, and elbilow
    input:  none but read from the current trace log files
    output: updated rdb files of ccdm, pacad, mups, and elbilow
    """
#
#--- read the already processed data list
#
    pfile  = house_keeping + 'rdb_processed_list'
    pdata = mcf.read_data_file(pfile)
#
#--- read the currently available data list
#
    cmd   = 'ls ' + main_dir + '/*.tl > ' + zspace
    os.system(cmd)

    cdata = mcf.read_data_file(zspace, remove=1)
#
#--- find new data
#
    ndata = list(set(cdata) - set(pdata))
#
#--- if there is no new data, exit
#
    if len(ndata) == 0:
        exit(1)
#
#--- make lists for ccdm, pcad, mups...
#--- also update already processed data list
#
    fo = open(pfile, 'w')
    fc = open('./ccdmlist',  'w')
    fp = open('./pcadlist',  'w')
    fm = open('./mupslist1', 'w')
    fn = open('./mupslist2', 'w')
    fe = open('./elbilist',  'w')

    for ent in ndata:
        fo.write(ent + '\n')

        if make_select_list(fc, ent, 'CCDM'):
            continue

        if make_select_list(fp, ent, 'PCAD'):
            continue

        if make_select_list(fm, ent, 'MUPSMUPS1'):
            continue

        if make_select_list(fn, ent, 'MUPSMUPS2'):
            continue

        if make_select_list(fe, ent, 'ELBILOW'):
            continue

    fo.close()
    fc.close()
    fp.close()
    fm.close()
    fn.close()
    fe.close()
#
#--- run pcad  update
#
    pcadfilter.pcadfilter('./pcadlist')
#
#--- run ccdm update
#
    ccdmfilter.ccdmfilter('./ccdmlist')
#
#--- run mups1 udpate; mups2 update will be done separately
#
    maverage.maverage('mupslist1', 'mups_1.rdb')
    maverage.maverage('mupslist2', 'mups_2.rdb')
#
#---- run elbi_low update
#
    maverage.maverage('elbilist', 'elbi_low.rdb')
    elbi_file = ds_dir + 'elbi_low.rdb'
    maverage.filtersort(elbi_file)
#
#--- clean up 
#
    mcf.rm_files('./ccdmlist')
    mcf.rm_files('./pcadlist')
    mcf.rm_files('./mupslist1')
    mcf.rm_files('./mupslist2')
    mcf.rm_files('./elbilist')

#---------------------------------------------------------------------------
#-- make_select_list: write a line if the line contain "word"            ---
#---------------------------------------------------------------------------

def make_select_list(f, line, word):
    """
    write a line if the line contain "word"
    input:  f       --- file indicator
            line    --- a line to check and add
            word    --- a word to check whether it is in the line
    output: updated file
            return True/False
    """
    mc = re.search(word, line)
    if mc is not None:
        line = line.strip()
        f.write(line)
        f.write('\n')

        return True
    else:
        return False 

#---------------------------------------------------------------------------

if __name__ == "__main__":

    run_rdb_updates()
