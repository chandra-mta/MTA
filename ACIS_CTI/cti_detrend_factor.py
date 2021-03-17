#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       cti_detrend_factor.py: create detrended cti tables                      #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Mar 02, 2021                                           #
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
import astropy.io.fits as pyfits
import time
import unittest
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf  #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)
#
#--- a couple of things needed
#
working_dir = exc_dir + '/Working_dir/'
temp_dir    = exc_dir + '/Temp_dir/'

#---------------------------------------------------------------------------------------------------
#-- cti_detrend_factor: update detrend factor table, then update detrend data table              ---
#---------------------------------------------------------------------------------------------------

def cti_detrend_factor():
    """
    update detrend factor table, then update detrend data table
    Input:  none
    Output: amp_avg_list    --- detrend factor table kept in <house_keeping>
            detrended data table, e.g. Det_Results/<elm>_ccd<ccd#>
    """
#
#--- update detrend factor table (amp_avg_list)
#
    update_detrend_factor_table()
#
#--- update detrend data tables 
#
    make_detrended_data_table()

#--------------------------------------------------------------------------------------
#-- cti_detrend_factor: extract information about amp_avg values and update amp_avg_list
#--------------------------------------------------------------------------------------

def update_detrend_factor_table():
    """
    extract information about amp_avg values and update <house_keeping>/amp_avg_list
    Input:  none
    Output: <house_keeping>/amp_avg_list
    """
#
#--- clean up temp_dir so that we can put new fits files
#
    mcf.mk_empty_dir(temp_dir)
#
#--- extract stat fits files
#
    new_entry = get_new_entry()
#
#--- if files are extracted, compute amvp_avg values for the obsid
#
    if len(new_entry) > 0:
        processed_list = update_amp_avg_list(new_entry)
#
#--- clean up "keep_entry" and amp_avg_list 
#
        update_holding_list(new_entry, processed_list)
        cleanup_amp_list()

#------------------------------------------------------------------------------------
#-- update_amp_avg_list: extract amp_avg information from a fits file for a given obsid
#-----------------------------------------------------------------------------------

def update_amp_avg_list(new_entry):
    """
    extract update amp_avg_list information 
    Input:  new_entry    --- a list of obsids
    Output: amp_avg_lst  --- a list of avg_amp kept in hosue_keeping dir 
                             (format: 2013-10-27T06:11:52 0.218615253807107   53275)
            processed_list - a list of obsid which actually used to generate avg_amp
    """
    [processed_list, amp_data_list] = get_amp_avg_data(new_entry)

    ofile = house_keeping + '/amp_avg_list'
    with open(ofile, 'a') as fo:
        for line in amp_data_list:
            fo.write(line)

    return processed_list

#-----------------------------------------------------------------------------------
#-- update_amp_avg_list: extract amp_avg information from a fits file for a given obsid 
#-----------------------------------------------------------------------------------

def get_amp_avg_data(new_entry):
    """
    extract amp_avg information from a fits file for a given obsid
    Input:  new_entry    --- a list of obsids
    Output: amp_data_lst  --- a list of avg_amp kept in hosue_keeping dir 
                             (format: 2013-10-27T06:11:52 0.218615253807107   53275)
            processed_list - a list of obsid which actually used to generate avg_amp
    """
#
#--- remove dupilcated entries of obsid
#
    new_entry      = sorted(list(set(new_entry)))
    processed_list = []
    amp_data_list  = []

    for obsid in new_entry:
#
#--- extract fits file(s)
#
        fits_list = extract_stat_fits_file(obsid, out_dir=temp_dir)
        for fits in fits_list:
#
#--- read header entry
#
            dout = pyfits.open(fits)
            date = dout[0].header['DATE-OBS']
            date.strip()
#
#--- extreact column data for ccd_id and drop_amp
#
            data     = pyfits.getdata(fits, 1)
            ccdid    = data.field('ccd_id')
            drop_amp = data.field('drop_amp')

            amp_data = []
            isum     = 0
            for i in range(0, len(ccdid)):
#
#--- amp data is computed from when ccd 7 drop_amp
#
                if int(ccdid[i]) == 7:
                    val = float(drop_amp[i])
                    amp_data.append(val)
                    isum += val

            if len(amp_data) > 0:
#
#--- 0.00323 is given by cgrant (03/07/05)
#
                norm_avg = 0.00323 * isum / float(len(amp_data))

                line = date + '\t' + str(norm_avg) + '\t' + str(obsid) + '\n'
            else:
                line = date + '\t' + '999999'      + '\t' + str(obsid) + '\n'

            processed_list.append(obsid)
            amp_data_list.append(line)

    return [processed_list, amp_data_list]

#---------------------------------------------------------------------------------------------------
#-- get_new_entry: create a list of obsids which need to be proccessed                            --
#---------------------------------------------------------------------------------------------------

def get_new_entry():
    """
    create a list of obsids which need to be proccessed
    Input: amp_avg_list --- a list kept in <house_keeping> directory
           new_entry    --- a list newly created during this session
    Output: a list of obsid which are not proccessed yet
    """
#
#--- prepare a data list file
#
    cmd = 'cp ' + house_keeping + '/amp_avg_list ' + house_keeping + '/amp_avg_list~'
    os.system(cmd)
#
#--- create a list of obsids which are already proccessed before
#
    ifile = house_keeping + '/amp_avg_list'
    amp   = mcf.read_data_file(ifile)
    comp  = []
    for ent in amp:
        atemp = re.split('\s+|\t+', ent)
        comp.append(atemp[2])
#
#--- read a new obsid list
#
    ifile =  working_dir + '/new_entry'
    test = mcf.read_data_file(ifile)
#
#--- add a list of old obsids which have not been proccessed.
#
    ifile = house_keeping + '/keep_entry'
    test2 = mcf.read_data_file(ifile)
    test  = test + test2
#
#--- find which obsids are new ones
#
    out = list(numpy.setdiff1d(test, comp))
    return  out

#---------------------------------------------------------------------------------------------------
#-- extract_stat_fits_file: extract acis stat fits files using arc5gl                            ---
#---------------------------------------------------------------------------------------------------

def extract_stat_fits_file(obsid, out_dir='./'):
    """
    extract acis stat fits files using arc5gl
    Input:  obsid   --- obsid
            out_dir --- a directory in which the fits file is deposited. default is "./"
    Output: acis stat fits file (decompressed) in out_dir
            data    --- a list of fits files extracted
    """
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=1\n'
    line = line + 'filetype=expstats\n'
    line = line + 'obsid=' + str(obsid) + '\n'
    line = line + 'go\n'

    with open(zspace, 'w') as fo:
        fo.write(line)
    try:
        try:
            cmd = ' /proj/sot/ska/bin/arc5gl -user isobe -script ' + zspace
            os.system(cmd)
        except:
            cmd  = ' /proj/axaf/simul/bin/arc5gl -user isobe -script ' + zspace
            os.system(cmd)
    
        cmd  = 'ls ' + exc_dir + '> ' + zspace
        os.system(cmd)
        with open(zspace, 'r') as f:
            test = f.read()

        mcf.rm_files(zspace)
    
        m1   = re.search('stat1.fits.gz', test)
        if m1 is not None:
            cmd  = 'mv ' + exc_dir +'/*stat1.fits.gz ' + out_dir + '/.'
            os.system(cmd)

            cmd  = 'gzip -d ' + out_dir + '/*stat1.fits.gz'
            os.system(cmd)
     
            cmd  = 'ls ' + out_dir + '/*' + str(obsid) + '*stat1.fits > ' + zspace
            os.system(cmd)
     
            data = mcf.read_data_file(zspace, remove=1)
    
            return data
        else:
            return []
    except:
        mcf.rm_file(zspace)
        return []

#---------------------------------------------------------------------------------------------------
#-- update_holding_list: update <hosue_keeping>/keep_entry list                                  ---
#---------------------------------------------------------------------------------------------------

def update_holding_list(new_entry, processed_list):
    """
    update <hosue_keeping>/keep_entry list
    Input:  new_entry      --- a list of obsids used
            processed_list --- a list of obsids actually processed
    Output: <hosue_keeping>/keep_entry list
    """
#
#-- find whether any of obsids were not proccessed
#
    missing = list(numpy.setdiff1d(new_entry, processed_list))

    if len(missing) > 0:
#
#--- if so, print them out
#
        sline = ''
        for ent in missing:
            sline = sline + ent + '\n'

        ofile  = house_keeping + 'keep_entry'
        with open(ofile, 'w') as fo:
            fo.write(line)

#---------------------------------------------------------------------------------------------------
#-- cleanup_amp_list: remove duplicated obsid entries: keep the newest entry only                ---
#---------------------------------------------------------------------------------------------------

def cleanup_amp_list():
    """
    remove duplicated obsid entries: keep the newest entry only
    Input:  read from: <hosue_keeping>/amp_avg_lst
    Output: updated <hosue_keeping>/amp_avg_lst
    """
    ifile = house_keeping + 'amp_avg_list'
    data  = mcf.read_data_file(ifile)
#
#--- reverse the list so that we can check from the newest entry
#
    data.reverse()
#
#--- find out which obsids are listed multiple times
#
    obsidlist = []
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        obsid = int(float(atemp[2]))
        obsidlist.append(obsid)

    obsidlist.sort()

    obsidmulti = []
    comp = obsidlist[0]
    for i in range(1, len(obsidlist)):
        if comp == obsidlist[i]:
            obsidmulti.append(obsidlist[i])
        else:
            comp = obsidlist[i]
#
#--- if there are multiple obsid entries, keep the newest one and remove older ones
#
    cleaned   = []
    if len(obsidmulti) > 0:
        obsidmulti = list(set(obsidmulti))
#
#--- "marked" is a marker which indicates whether a specific obsid is already listed
#
        for i in range(0, len(obsidmulti)):
            marked[i] = 0

        for ent in data:
            atemp = re.split('\s+', ent)
            obsid = int(atemp[2])
            chk   = 0
            for i in range(0, len(obsidmulti)):
                if (obsid == obsidmulti[i]) and (marked[i] == 0):
                    marked[i] = 1
                    break
                elif (obsid == obsidmulti[i]) and (marked[i] > 0):
                    chk = 1
                    break

            if chk == 0:
                cleaned.append(ent)
    else: 
        cleaned = data 
#
#--- reverse back to the original order
#
    cleaned.reverse()
#
#--- print out the cleaned list
#
    with open(ifile, 'w') as fo:
        for ent in cleaned:
            fo.write(ent + '\n')

#---------------------------------------------------------------------------------------------------
#-- make_detrended_data_table: update detrended cti tables                                       ---
#---------------------------------------------------------------------------------------------------

def make_detrended_data_table():
    """
    update detrended cti tables
    Input:  none, but read from data_dir/Results/<elm>_ccd<ccd#> and <house_keeping>/amp_avg_list
    Output: <data_dir>/Det_Results/<elm>_ccd<ccd#>
    """
#
#--- read detrending factor table
#
    detrend_factors = read_correction_factor()      #--- detrend_factors is a dictionary
#
#--- go through all imaging ccds for each element
#
    for elm in ['al', 'mn', 'ti']:

        for ccd in [0, 1, 2, 3, 4, 6, 8, 9]:
#
#--- read original data table
#
            infile  = data_dir + '/Results/'     + elm + '_ccd' + str(ccd)
            data    = mcf.read_data_file(infile)

            sline = ''
            for ent in data:
                atemp = re.split('\s+|\t+', ent)
#
#--- find a corresponding correction foactor
#
                obsid = int(float(atemp[5]))
                try:
                    det_val = detrend_factors[obsid]
                except:
                    det_val = 999
#
#--- if the detrending value is found and acceptable, correct cti values
#
                if det_val < 999:

                    sline = sline + atemp[0] + '\t'       #---- starting date

                    for i in range(1, 5):
                        corrected = correct_det(atemp[i], det_val)
                        sline     = sline + corrected + '\t'

                    sline = sline + atemp[5]  + '\t'      #--- obsid
                    sline = sline + atemp[6]  + '\t'      #--- ending date
                    sline = sline + atemp[7]  + '\t'      #--- avg focal temperature
                    sline = sline + atemp[8]  + '\t'      #--- sigma for the focal temperature
                    sline = sline + atemp[9]  + '\t'      #---  min focal temperature
                    sline = sline + atemp[10] + '\t'      #--- max focal temperature
                    sline = sline + atemp[11] + '\t'      #--- starting time in sec
                    sline = sline + atemp[12] + '\n'      #--- ending time in sec
#
#--- open output detrended table
#
            outfile = data_dir + '/Det_Results/' + elm + '_ccd' + str(ccd)
            with  open(outfile, 'w') as fo:
                fo.write(sline)

#---------------------------------------------------------------------------------------------------
#-- read_correction_factor: read a detrend correction factor table and create a dictionary       ---
#---------------------------------------------------------------------------------------------------

def read_correction_factor():
    """
    read a detrend correction factor table and create a dictionary with obsid <---> factor
    Input:  none, but read from <hosue_keeping>/amp_avg_list
    Outupt: detrend_factors --- a dictionary obsid <---> factor
    """
#
#--- read correction factor table
#
    ifile = house_keeping + '/amp_avg_list'
    data  = mcf.read_data_file(ifile)
#
#--- create a dictionary
#
    detrend_factors = {}
    for ent in data:
        try:
            atemp = re.split('\s+', ent)
        except:
            continue

        obsid = int(float(atemp[2].strip()))
        detrend_factors[obsid] = float(atemp[1].strip())

    return detrend_factors

#---------------------------------------------------------------------------------------------------
#--  correct_det: correct cti with a given detrending factor                                     ---
#---------------------------------------------------------------------------------------------------

def correct_det(quad, det_val):
    """
    correct cti with a given detrending factor
    Input:  quad    --- cti value +/- error
            det_val --- detrending factor
    Output: cti     --- corrected cti +/- error
    """
    m = re.search('99999', quad)
    if m is not None:
        return quad
    else:
        atemp = re.split('\+\-', quad)
        val   = float(atemp[0]) + det_val
        val   = round(val, 3)
        val   = str(val)
        vcnt  = len(val)
    
        if vcnt < 5:
            for i in range(vcnt, 5):
                val = val + '0'
        cti   = str(val) + '+-' + atemp[1]

        return cti
        
#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """

#------------------------------------------------------------

    def test_get_amp_avg_data(self):

        new_entry           = [52675]
        processed_list_test = [52675]
        amp_data_test       = ['2014-06-27T04:21:09\t0.199661945312\t52675\n']

        [processed_list, amp_data_list] = get_amp_avg_data(new_entry)

        self.assertEquals(processed_list, processed_list_test)
        self.assertEquals(amp_data_list,  amp_data_test)

#--------------------------------------------------------------------

if __name__ == '__main__':

    cti_detrend_factor()
