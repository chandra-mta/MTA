#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       acis_gain_extract_data.py: extract gain data from acis _vt1 files       #
#                                                                               #
#           author: t. isobe(tisobe@cfa.harvard.edu)                            #
#                                                                               #
#           Last Update:    Mar 03, 2021                                        #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import astropy.io.fits as pyfits
from astropy.table import Table
import scipy
from scipy.optimize import curve_fit
import time

import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Gain/house_keeping/dir_list_py'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf      #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)
working_dir = exc_dir + '/Working_dir/'
#
#---- peak position for peaks are:
#---- $pos2: Al K<---> 1486.70;
#---- $pos3: Ti K<---> 4510.84;
#---- $pos1: Mn K<---> 5898.75;
#
peak_ev = [1486.70, 4510.84, 5898.75]
cselect = ['time', 'ccd_id', 'node_id', 'pha', 'grade']

#-------------------------------------------------------------------------------------------
#-- acis_gain_get_data: extract acis evt1 files and compute monnth averaged gain and offset-
#-------------------------------------------------------------------------------------------

def acis_gain_get_data(year='', month=''):
    """
    extract acis evt1 files and compute month averaged gain and offset
    Input:  year/month:     the month you want to compute. if 0, the last month is used
    Ouput:  <data_dir>/ccd<ccd>_<node>: 
                <s time> <al peak> <mn peak> <ti peak> <slope> <s error> <intercept> <ierro>
    """
#
#--- get a new data list
#
    [obsid_list, start_list, stop_list] = get_input_data_list(year, month)

    if len(obsid_list) > 0:

        tstart = start_list[0]
        tstop  = stop_list[len(stop_list)-1]
        mtime  = int (tstart + 0.5 * (tstop - tstart))
#
#--- if there is no new data, just exit
#
        if len(obsid_list) > 0:
#
#--- extract alldata
#
            data_set  = get_new_data(obsid_list,start_list, stop_list)
#
#--- get pha profile parameter for each ccd and node

            ik = 0
            for ccd in range(0, 10):
                for node in range(0, 4):
#
#--- check whether parameters are computed. if not skip the ccd/node
#
                    out =  extract_gain_info(data_set, ccd, node)
    
                    if len(out) <= 1:
                        continue
    
                    [al_cent, mn_cent, ti_cent, b, a, be, ae] = out
    
                    alpos    = str(round(al_cent, 4))
                    mnpos    = str(round(mn_cent, 4))
                    tipos    = str(round(ti_cent, 4))
                    slope    = str(round(b,       4))
                    intcept  = str(round(a,       4))
                    serr     = str(round(be,      4))
                    ierr     = str(round(ae,      4))
#
#--- data line
#
                    line     = str(mtime)     + '\t' + alpos + '\t' 
                    line     = line + mnpos   + '\t' + tipos + '\t'
                    line     = line + slope   + '\t' + serr  + '\t'  
                    line     = line + intcept + '\t' + ierr  + '\n'
#
#--- now print
#
                    out_name = data_dir + 'ccd' + str(ccd) + '_' + str(node)
                    with open(out_name, 'a') as fo:
                        fo.write(line)

#-------------------------------------------------------------------------------------------
#-- get_new_data: extract fits for the obsid, then extrat data needed                     --
#-------------------------------------------------------------------------------------------

def get_new_data(obsid_list, start_list, stop_list):
    """
    extract fits for the obsid, then extrat data needed
    input:  obsid_list  --- a list of obsids
            start_list  --- a list of start time of the observation
            stop_list   --- a list of stop time of the observation
    output: data_set    --- a list of data sets
    """
#
#--- find middle of the time. it will be used as a time stamp for this data set
#
    tstart = start_list[0]
    tstop  = stop_list[len(stop_list)-1]
    mtime  = int (tstart + 0.5 * (tstop - tstart))
#    
#--- extract acis event1 file and combined all of them
#
    mcf.mk_empty_dir(working_dir)

    pobsid    = []
    fits_list = []
    
    data_set  = []
    for i in range(0, len(obsid_list)):
        obsid = obsid_list[i]
        start = start_list[i]
        stop  = stop_list[i]
#
#--- check whether this data is already extreacted. if so, don't re-extrad the data
#
        chk = 0
        for comp in pobsid:
            if obsid == comp:
                chk = 1
                break

        if chk == 0:
            fits   = extract_acis_evt1(obsid)
            pobsid.append(obsid)
            if fits != 'na':
                fits_list.append(fits)
        else:
            fits = 'na'
            for ent in fits_list:
                m1 = re.search(obsid, ent)
                if m1 is not None:
                    fits = ent
                    break

        if fits == 'na':
                continue
#
#--- "Table.read" opens fits file and read fits table data
#
        rfits = working_dir + fits
        tdata = Table.read(rfits, hdu=1)
        tdiff = stop - start
#
#--- extract specified time range, pha range, and chipy
#
        mask  = (tdata.field('time')   >= start) & (tdata.field('time') <= stop) \
                 & (tdata.field('pha') <= 4000)  & (tdata.field('chipy') <= 20) 
        tdata = tdata[mask]

        if len(tdata) < 1000:
            continue

        tdata = tdata[cselect]
#
#--- grade
#
        mask  = (tdata.field('grade') <= 6) & (tdata.field('grade') != 1) \
                 & (tdata.field('grade') != 5)
        tdata = tdata[mask]

        data_set.append(tdata)

    return data_set

#-------------------------------------------------------------------------------------------
#-- extract_gain_info: create pha count profile from given data sets and fit model parameters
#-------------------------------------------------------------------------------------------

def extract_gain_info(data_set, ccd, node):
    """
    create pha count profile from given data sets and fit model parameters
    input: data_set         --- a list of extracted fits data
           ccd              --- ccd #
           node             --- node #
    output: d_list : [al_cent, mn_cent, ti_cent, b, a, be, ae]
                    al_cent --- center of al line
                    mn_cent --- center of mn line
                    ti_cent --- center of ti line
                    b       --- slope of the fitted line
                    a       --- intercept of the fitted line
                    be      --- the error of the slope
                    ae      --- the error of the intercept
    """
#
#--- create a histgram data for specified CCD / Node combination
#
    hist = extract_hist_data(data_set, ccd, node)
#
#--- if the hist data is empty, just add an empty list for house keeping
#
    if hist == 'na':
        return []
#
#--- Mn K alpha
#
    y      = hist[1200:2500]

    ymax   = max(y)
    xpos   = y.index(ymax) + 1200
    hwidth = 200
#
#--- if the count rate is too low, we cannot fit the data; so limit data larger than 20 counts
#
    start  = xpos - hwidth
    stop   = xpos + hwidth
    ybin   = hist[start:stop]
    chk    = 0
    for ent in ybin:
        chk += int(ent)

    if chk < 20:
        return []

    [mn_amp, mn_cent, mn_width, floor] = fit_pmodel(hist, ymax, xpos, hwidth)
#
#--- AL K alpha
#
    ymax   = 0.5  * mn_amp
    xpos   = 0.25 * mn_cent
    hwidth = 50

    [al_amp, al_cent, al_width, floor] = fit_pmodel(hist, ymax, xpos, hwidth)
#
#--- Ti K alpha
#
    ymax   = 0.5   * mn_amp
    xpos   = 0.765 * mn_cent
    hwidth = 100

    [ti_amp, ti_cent, ti_width, floor] = fit_pmodel(hist, ymax, xpos, hwidth)
#
#--- fit a straight line
#
    pos        = [al_cent, ti_cent, mn_cent]
    p0         = [0, 1]

    popt, pcov = curve_fit(lmodel, peak_ev, pos, p0=p0)
    [a, b]     = list(popt)
    [ae, be]   = list(numpy.sqrt(numpy.diag(pcov)))

    d_list     = [al_cent, mn_cent, ti_cent, b, a, be, ae]

    return d_list        
    
#-------------------------------------------------------------------------------------------
#-- extract_hist_data: extract histgram data for given ccd and node                      ---
#-------------------------------------------------------------------------------------------

def extract_hist_data(data_set, ccd, node):
    """
    extract histgram data for given ccd and node
    input:  data_set    ---- mixed data
            ccd         ---- ccd id
            node        ---- node #
    output: hist        ---- histgram profile data
    """
    hist = [0 for x in range(0, 4000)]

    for tdata in data_set:
        mask  = tdata.field('ccd_id') == ccd
        tdata = tdata[mask]

        if len(tdata) == 0:
            continue

        mask  = tdata.field('node_id') == node
        tdata = tdata[mask]

        if len(tdata) == 0:
            continue

        hdata = list(tdata['pha'])

        for ent in hdata:
            try:
                k = int(ent) 
                if k < 4000:
                    hist[k] += 1
            except:
                pass
#
#--- make sure that it actually has data
#
    test = 0
    for k in range(0, 4000):
        test += hist[k]
    if test == 0:
        return 'na'
    else:
        return hist

#-------------------------------------------------------------------------------------------
#-- fit_pmodel: for a given histgram data, fit a gaussian distribution                   ---
#-------------------------------------------------------------------------------------------

def fit_pmodel(hist, ymax, xpos, hwidth):
    """
    for a given histgram data, fit a gaussian distribution
    input:  hist    --- hist data
            ymax    --- initial guess height of the profile
            xpos    --- initial guess center postion
            hwidth  --- initial guess sigma

    Output: amp     --- estimated height of the profile
            cent    --- estimated center postion
            width   --- estimated sigma
            floor   --- estimated floor level
    """
    start  = int(xpos) - hwidth
    stop   = int(xpos) + hwidth

    ybin   = hist[start:stop]
    xbin   = [x for x in range(start, stop)]
    err    = numpy.ones(2 * hwidth)
    p0     = [ymax, xpos, 10, 0]

    try:
        popt, pcov                = curve_fit(funcG, xbin, ybin, p0=p0)
        [amp, cent, width, floor] = list(popt)
    except:
        [amp, cent, width, floor] =  p0


    return [amp, cent, width, floor]

#-------------------------------------------------------------------------------------------
#--- lmodel: linear model for data fitting                                                --
#-------------------------------------------------------------------------------------------

def lmodel(x, a, b):
    """
    linear model for data fitting
    Input:  p --- (a, b): intercept and slope
            x --- independent variable values
    Oputput: estimated y values
    """
    y = a + b*x
    return y

#-------------------------------------------------------------------------------------------
#-- extract_acis_evt1: extract acis evt1 file                                             --
#-------------------------------------------------------------------------------------------

def extract_acis_evt1(obsid):
    """
    extract acis evt1 file 
    Input: obsid    --- obsid of the data
    Output: acisf<obsid>*evt1.fits.gz
            file name if the data is extracted. if not ''
    """
#
#--- write  required arc5gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=evt1\n'
    line = line + 'obsid=' + str(obsid) + '\n'
    line = line + 'go\n'
    with  open(zspace, 'w') as fo:
        fo.write(line)
#
#--- run arc5gl
#
    try:
        cmd = ' /proj/sot/ska/bin/arc5gl -user isobe -script ' + zspace
        os.system(cmd)
    except:
        cmd  = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ' + zspace
        os.system(cmd)
        
    mcf.rm_files(zspace)
#
#--- check the data is actually extracted
#
    try:
        cmd  = 'ls *'+ str(obsid) + '*evt1.fits.gz >' + zspace
        os.system(cmd)
    except:
        return 'na'

    data = mcf.read_data_file(zspace, remove=1)
#
#--- if multiple evt1 files are extracted, don't use it, but keep the record of them 
#
    if len(data) > 1:
        cmd  = 'rm *'+ str(obsid) + '*evt1.fits.gz '
        os.system(cmd)

        ifile = house_keeping + '/keep_entry'
        with open(ifile, 'a') as fo:
            fo.write(obsid + '\n')
 
        return 'na'
    
    elif len(data) == 1:
#
#--- normal case, only one file extracted
#
        line = data[0].replace('.gz', '')

        cmd  = 'chmod 755 ' + data[0]
        os.system(cmd)
        cmd  = 'mv ' + data[0] + ' '  + working_dir + '/.'
        os.system(cmd)
        cmd  = 'gzip -d ' + working_dir + '*gz'
        os.system(cmd)
    
        return line
    else:
#
#--- no file is extracted
#
        return 'na'

#-------------------------------------------------------------------------------------------
#--- get_input_data_list: read obsid and the period where the focal temperature is < -119.7C from CTI data
#-------------------------------------------------------------------------------------------

def get_input_data_list(year = 0, mon = 0):
    """
    read obsid and the period where the focal temperature is < -119.7C from CTI data and 
    makes a list of input data for a given year/month. if year/month is not given, the last
    month is used. 
    Input:  year/month  --- the year/month that data will be collected if 0, the last month is used.
    Ouput: a list of lists: [obsid, start, stop]
    """
#
#--- if the date is not given, set the period to the last month
#
    if year == 0:
        out   = time.strftime('%Y:%m', time.gmtime())
        tlist = re.split(':', out)
        year  = int(float(tlist[0]))
        mon   = int(float(tlist[1]))
        mon  -= 1
#
#--- for the case that the last month is the last year
#
        if mon < 1:
            mon   = 12
            year -= 1
#
#--- we need only data with the focal temp <= -119.7C before May 2006 and <= -119.0C from May 2006
#--- and observation interval longer than 1000 sec
#
    if year > 2006:
        tlimit = -119.0

    elif (year == 2006) and (mon >= 5):
        tlimit = -119.0

    else:
        tlimit = -119.7

    save    = []
    for ccd in range(0, 10):
        ifile = cti_dir + 'ti_ccd' + str(ccd)
        data  = mcf.read_data_file(ifile)

        for ent in data:
            atemp = re.split('\s+', ent)
            dtime = float(atemp[12]) - float(atemp[11])
            temp  = float(atemp[7])
            if temp <= tlimit:
                if dtime > 1000:
                    line  = atemp[0] + '\t' + atemp[5] + '\t' 
                    line  = line + str(dtime) + '\t' + atemp[7]  + '\t' 
                    line  = line + atemp[11] + '\t' + atemp[12]
                    save.append(line)
#
#--- remove duplicated entries
#
    clist = list(set(save))
    clist = sorted(clist)

    obsid = []
    start = []
    stop  = []
    sline = ''
    for ent in clist:
        sline  = sline + str(ent) + '\n'
#
#--- setlect out the data for year/month
#
        atemp = re.split('-', ent)
        cyear = int(atemp[0])
        cmon  = int(atemp[1])

        if (cyear == year) and (cmon == mon):
            atemp = re.split('\s+', ent)
            obsid.append(atemp[1])
            start.append(int(atemp[4]))
            stop.append(int(atemp[5]))

    with open('./input_list', 'w') as fo:
        fo.write(sline)

    return [obsid, start, stop]

#----------------------------------------------------------------------------------
#-- funcG: Model function is a gaussian                                         ---
#----------------------------------------------------------------------------------

def funcG(x, A, mu, sigma, zerolev):
    """
    Model function is a gaussian
    Input:  p   --- (A, mu, sigma, zerolev) 
            x  
    Output: estimated y values
    """
    return( A * numpy.exp(-(x-mu)*(x-mu)/(2*sigma*sigma)) + zerolev )

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_get_input_data_list(self):

        [obsid, start, stop] = get_input_data_list(2014, 1)
        test_out = ['53117', '62674', '53102', '53089', '53082', '53069', '53061']

        self.assertEquals(obsid, test_out)

#--------------------------------------------------------------------

    def test_get_new_data(self):

        obsid = ['53117', '62674'] 
        start = [504955553, 505683278]
        stop  = [504968158, 505803066]

        data_set  = get_new_data(obsid, start, stop)
        info_save = extract_gain_info(data_set, 3, 1)

        test_out  = [377.71818836179369, 1496.9270128895018, 1145.878719890527, 0.25372580295403135, \
                     0.7093958711330367, 0.00025627917431867857, 1.1205577882714126]

        self.assertEquals(info_save, test_out)

#--------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 3:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
    else:
        year  = 0
        month = 0
    
    acis_gain_get_data(year, month)

