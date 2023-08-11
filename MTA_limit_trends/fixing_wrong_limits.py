#!/proj/sot/ska3/flight/bin/python

#
#--- this script fix wrong temperature limit 
#---
#---      May 10, 2021
#---

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
from astropy.io.fits import Column
import Chandra.Time
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
import fits_operation           as mfo  #---- fits operation collection
import read_limit_table         as rlt  #---- read limit table and create msid<--> limit dict
#
#--- other path setting
#
limit_dir = '/data/mta/Script/MSID_limit/Trend_limit_data/'
#
#--- fits generation related lists
#
col_names  = ['time', 'msid', 'med', 'std', 'min', 'max',
              'ylower', 'yupper', 'rlower', 'rupper', 'dcount',
              'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper', 'state']
col_format = ['D', '20A', 'D', 'D','D','D','D','D','D','D', 'I', 'D', 'D', 'D', 'D', '10A']

a_month = 86400 * 30
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

tstart = 733449594

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

def run():

    m_dict = get_limit_data()
    m_list = m_dict.keys()

    cmd = 'ls -d ' + data_dir + '/* >' + zspace
    os.system(cmd)
    tdir_list = mcf.read_data_file(zspace, remove=1)
    for edir in tdir_list:
        cmd = 'ls ' +  edir + "/*_short_data.fits > " + zspace
        os.system(cmd)
        f_list = mcf.read_data_file(zspace, remove=1)
        for ent in f_list:
            atemp = re.split('\/', ent)
            btemp = re.split('_short_', atemp[-1])
            msid  = btemp[0]
            if msid in m_list:
                print(msid)
                lim_list = m_dict[msid]
                sfits    = ent
                lfits    = sfits.replace('_short', '')

                try:
                    update_limit_chk(msid, sfits, lim_list)
                    update_limit_chk(msid, lfits, lim_list)
                except:
                    pass
                
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

def update_limit_chk(msid, mfits, lim_list):

    hout = pyfits.open(mfits)
    data = hout[1].data
    hout.close()
    
    clen    = len(col_names)
    cols    = col_names
    cols[1] = msid
    tlist   = []
    for col in cols:
        tlist.append(data[col])

    tlen  = len(tlist[0])
    for k in range(0, tlen):
        if tlist[0][k] < tstart:
            continue
        #tlist[6][k] = 0
        #tlist[7][k] = 0
        #tlist[8][k] = 0
        #tlist[9][k] = 0
        #yl  = lim_list[0]
        #yu  = lim_list[1]
        #rl  = lim_list[2]
        #ru  = lim_list[3]

        #tlist[11][k] = yl
        #tlist[12][k] = yu
        #tlist[13][k] = rl
        #tlist[14][k] = ru
        #continue

        
        med = float(tlist[1][k])
        yl  = lim_list[0]
        yu  = lim_list[1]
        rl  = lim_list[2]
        ru  = lim_list[3]

        tlist[11][k] = yl
        tlist[12][k] = yu
        tlist[13][k] = rl
        tlist[14][k] = ru
        if med > yl and med < yu:
            tlist[6][k] = 0
            tlist[7][k] = 0
            tlist[8][k] = 0
            tlist[9][k] = 0
        elif med > rl and med <= yl:
            tlist[6][k] = 1
            tlist[7][k] = 0
            tlist[8][k] = 0
            tlist[9][k] = 0
        elif med >= yu and med < ru:
            tlist[6][k] = 0
            tlist[7][k] = 1
            tlist[8][k] = 0
            tlist[9][k] = 0
        elif med <= rl:
            tlist[6][k] = 0
            tlist[7][k] = 0
            tlist[8][k] = 1
            tlist[9][k] = 0
        elif med >= yu:
            tlist[6][k] = 0
            tlist[7][k] = 0
            tlist[8][k] = 0
            tlist[9][k] = 1
        else:
            tlist[6][k] = 0
            tlist[7][k] = 0
            tlist[8][k] = 0
            tlist[9][k] = 0

    atemp = re.split('\/', mfits)
    ffile = atemp[-1]
    create_fits_file(msid, mfits, tlist)

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

def create_fits_file(msid, fits, data):
    """
    create a fits file
    input:  msid--- msid
            data--- a list of list of data
    output: fits
    """
    cols= col_names
    cols[1] = msid
    
    c1  = Column(name=cols[0],  format=col_format[0],  array = data[0])
    c2  = Column(name=cols[1],  format=col_format[1],  array = data[1])
    c3  = Column(name=cols[2],  format=col_format[2],  array = data[2])
    c4  = Column(name=cols[3],  format=col_format[3],  array = data[3])
    c5  = Column(name=cols[4],  format=col_format[4],  array = data[4])
    c6  = Column(name=cols[5],  format=col_format[5],  array = data[5])
    c7  = Column(name=cols[6],  format=col_format[6],  array = data[6])
    c8  = Column(name=cols[7],  format=col_format[7],  array = data[7])
    c9  = Column(name=cols[8],  format=col_format[8],  array = data[8])
    c10 = Column(name=cols[9],  format=col_format[9],  array = data[9])
    c11 = Column(name=cols[10], format=col_format[10], array = data[10])
    c12 = Column(name=cols[11], format=col_format[11], array = data[11])
    c13 = Column(name=cols[12], format=col_format[12], array = data[12])
    c14 = Column(name=cols[13], format=col_format[13], array = data[13])
    c15 = Column(name=cols[14], format=col_format[14], array = data[14])
    c16 = Column(name=cols[15], format=col_format[15], array = data[15])
    
    coldefs = pyfits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)
    
    mcf.rm_files(fits)
    
    tbhdu.writeto(fits)


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

def get_limit_data():

    ifile  = limit_dir + 'Limit_data/op_limits_new.db'
    data   = mcf.read_data_file(ifile)
    m_dict = {}
    for ent in data:
        if ent[0] == '#':
            continue

        atemp = re.split('#', ent)
        btemp = re.split('\s+', atemp[0])
        unit  = atemp[-2].strip()
        if unit == 'K':
            if btemp[6].strip() == 'none':
                msid = btemp[0].strip()
                ly   = float(btemp[1])
                uy   = float(btemp[2])
                lr   = float(btemp[3])
                ur   = float(btemp[4])
                m_dict[msid] = [ly, uy, lr, ur]


    return m_dict

#-----------------------------------------------------------------------

if __name__ == "__main__":

    run()
