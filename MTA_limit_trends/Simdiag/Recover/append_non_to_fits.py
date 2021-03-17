#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python
#
#--- adding "state" column to an existing fits file without the state column. Only "none" is added
#
#           Jan 16, 2020
#
import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import random

path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions     as mcf   
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

out_dir  = '/data/mta/Script/MTA_limit_trends/Scripts/Simdiag/Recover/Outdir/'
#
#--- read and save msids and corresponding group names
#
group_list = []
msid_list  = []
ifile = house_keeping + 'msid_list_simdiag'
out   = mcf.read_data_file(ifile)
for ent in out:
    atemp = re.split('\s+', ent)
    msid_list.append(atemp[0])
    group_list.append(atemp[1])

ifile = house_keeping + 'msid_list_simactu_supple'
out   = mcf.read_data_file(ifile)
for ent in out:
    atemp = re.split('\s+', ent)
    msid_list.append(atemp[0])
    group_list.append(atemp[1])

for k in range(0, len(msid_list)):
    group = group_list[k]
    msid  = msid_list[k]
#
#--- three data sets for long, short, and week data
#
    for tail in ['_data', '_short_data', '_week_data']:
#
#--- set input and output file names
#
        in_file  = data_dir + group + '/' + msid + tail + '.fits'
        out_file = out_dir  + group + '/' + msid + tail + '.fits'
#
#--- read the original fits column data
#
        with pyfits.open(in_file) as hdu:
            org_table = hdu[1].data
            org_cols  = org_table.columns
#
#--- create new 'state' column data with 'none' entries
#
        n_list  = ['none'] * len(org_table)
        n_array = numpy.array(n_list)
        new_col = pyfits.ColDefs([
                    pyfits.Column(name='state', format='10A', array=n_array)
                    ])
#
#--- combine them
#
        nhdu = pyfits.BinTableHDU.from_columns(org_cols + new_col)
#
#--- create a new fits file
#
        nhdu.writeto(out_file)
