#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           extract_grating_ede.py: extract grating E/dE data                                   #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Jul 18, 2018                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import random
import numpy
import time
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/Grating/Grating_EdE/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import convertTimeFormat    as tcnv
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

catg_list = ['HEGp1', 'HEGm1', 'MEGp1', 'MEGm1', 'LEGpAll', 'LEGmAll']
type_list = ['hetg',  'hetg',  'metg',  'metg',  'letg',    'letg']
header    = '#year obsid   energy  fwhm denergy error   order   cnt roi_cnt acf acf_err  link'

#----------------------------------------------------------------------------------------------
#-- extract_grating_ede: extract grating E/dE data                                           --
#----------------------------------------------------------------------------------------------

def extract_grating_ede():
    """
    extract grating E/dE data
    input:  none but read from  <gdata_dir>/*/*/*Sky_<catg>_linelist.rdb
    output: <data_dir>/<catg.lower>_data
    """

#
#--- go through each data set
#
    for k in range(0, 6):
        catg    = catg_list[k]
#
#--- is there new file?
#
        n_list  = find_new_entries(catg)
        if len(n_list) == 0:
            continue

        outfile = data_dir + catg.lower() + '_data'

        if  os.path.isfile(outfile):
            fo = open(outfile, 'a')

        else:
            fo = open(outfile, 'w')
            fo.write(header)
            fo.write('\n')
#
#--- go through each data file
#
        for ent in n_list:
            out   = read_rdb_file(ent)
            data  = select_data(out, type_list[k])

            if len(data[0]) == 0:
                continue
#
#--- if there are data, update the data file
#
            for n in range(0, len(data[0])):
                line = str(data[0][n]) + '\t' + str(data[1][n])
                for m in range(2, 12):
                    line = line + '\t' + str(data[m][n])
                line = line  + '\n'
                fo.write(line)
        fo.close()

#----------------------------------------------------------------------------------------------
#-- find_new_entries: find un-processed data file names                                      --
#----------------------------------------------------------------------------------------------

def find_new_entries(catg):
    """
    find un-processed data file names
    input:  catg    --- category of the data
    output: new     --- a list of the file names
    """
#
#--- read already processed data files
#
    pfile = house_keeping + catg
    try:
        pdata = read_data_file(pfile)
    except:
        pdata = []
#
#--- get current data file list
#
    cmd   = 'ls ' + gdata_dir + '/*/*/*Sky_' + catg + '_linelist.rdb > ' + zspace
    os.system(cmd)
    ndata = read_data_file(zspace)
#
#--- move the current list to <house_keeping>
#
    cmd   = 'mv ' + zspace + ' ' + pfile
    os.system(cmd)
#
#--- find un-processed data files
#
    new   = list(set(ndata) - set(pdata))

    return new

#----------------------------------------------------------------------------------------------
#-- select_data: select out data which fit to the selection criteria                         --
#----------------------------------------------------------------------------------------------

def select_data(idata, type):

    """
    select out data which fit to the selection criteria
    input:  indata
                    idata[0]:   year    
                    idata[1]:   obsid   
                    idata[2]:   energy  
                    idata[3]:   fwhm    
                    idata[4]:   denergy 
                    idata[5]:   error   
                    idata[6]:   order   
                    idata[7]:   cnt     
                    idata[8]:   roi_cnt 
                    idata[9]:   acf     
                    idata[10]:  acf_err 
                    idata[11]:   links   
            type    --- type of the data; letg, metg, hetg
    output: out --- selected potion of the data
    """

    out = []
    for k in range(0, 12):
        out.append([])

    for m in range(0, len(idata[0])):

        if (idata[5][m] / idata[3][m] < 0.15):
#
#-- letg case
#
            if type == 'letg':
                for k in range(0, 12):
                    out[k].append(idata[k][m])
#
#--- metg case
#
            elif idata[3][m] * 1.0e3 / idata[2][m] < 5.0:
                if type == 'metg':
                    for k in range(0, 12):
                        out[k].append(idata[k][m])
#
#--- hetg case
#
                else:
                    if abs(idata[3][m] - 1.01) > 0.01:
                        for k in range(0, 12):
                            out[k].append(idata[k][m])

    return out


#----------------------------------------------------------------------------------------------
#-- read_rdb_file: read rdb data file                                                        --
#----------------------------------------------------------------------------------------------

def read_rdb_file(infile):
    """
    read data file
    input:  infile  --- input file name
    output: a list of:
                    idata[0]:   year    
                    idata[1]:   obsid   
                    idata[2]:   energy  
                    idata[3]:   fwhm    
                    idata[4]:   denergy 
                    idata[5]:   error   
                    idata[6]:   order   
                    idata[7]:   cnt     
                    idata[8]:   roi_cnt 
                    idata[9]:   acf     
                    idata[10]:  acf_err 
                    idata[11]:   links   
    """
    atemp = re.split('\/', infile)
    year  = int(float(atemp[-3][3] + atemp[-3][4]))
    if year > 90:
        year += 1900
    else:
        year += 2000

    obsid  = atemp[-2]
    line   = 'obsid_' + obsid + '_Sky_summary.html'
    link   = infile.replace(atemp[-1], line)

    f    = open(infile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    year_l  = []
    obsid_l = []
    energy  = []
    fwhm    = []
    error   = []
    denergy = []
    order   = []
    cnt     = []
    roi_cnt = []
    acf     = []
    acf_err = []
    links_l = []

    chk     = 0
    for k in range(20, len(data)):
        ent = data[k]
#
#--- find the spot that the data actually start
#
        if ent[0] == '#':
            continue

        if chk == 0:
            if ent[0] == 'N':
                chk = 1
            continue

        atemp = re.split('\s+', ent)
#
#--- drop bad data
#
        try:
            eng  = float(atemp[3])
            deng = float(atemp[7])
        except:
            continue

        if (eng < 0.0)  or (deng < 0.0):
            continue

        year_l.append(year)
        obsid_l.append(obsid)

        energy.append(eng)
        fwhm.append(float(atemp[5]))
        error.append(float(atemp[6]))
        denergy.append(deng)
        order.append(1)
        cnt.append(int(float(atemp[1])))
        roi_cnt.append(float(atemp[8]))
        acf.append(float(atemp[9]))
        acf_err.append(float(atemp[10]))

        links_l.append(link)
#
#--- a couple of data are useful as numpy array
#
    year_l    = numpy.array(year_l)
    energy  = numpy.array(energy)
    denergy = numpy.array(denergy)

    return [year_l, obsid_l, energy, fwhm, denergy, error, order, cnt, roi_cnt, acf, acf_err, links_l]

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):

    f     = open(ifile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    if remove > 0:
        mcf.rm_file(ifile)


    return data

#----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    extract_grating_ede()

