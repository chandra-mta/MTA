#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       acis_compute_stat: compute statistics for given month data              #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last updated: Mar 09, 2021                                              #
#                                                                               #
#################################################################################

import sys
import os
import string
import re
import random
import time
#
#--- reading directory list
#
path = '/data/mta/Script/Exposure/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
sys.path.append(acis_bin_dir)
#
import mta_common_functions as mcf
import exposureFunctions    as expf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------
#--- acis_dose_extract_stat_data_month: driving fuction to compute statistics
#-------------------------------------------------------------------------------

def acis_dose_extract_stat_data_month(year='NA', month='NA'):
    """
    driving fuction to compute statistics
    input:  year    --- year
            month   --- month
    output: updated <data_dir>/<ccd#>_<node#>_<diff/acc>_out
    """
    if year == 'NA' or month == 'NA':
        year  = raw_input("Year: ")
        year  = int(year)
        month = raw_input('Month: ')
        month = int(month)
#
#--- ACIS I2
#
#--- the last few columns are dropped to avoid bad pixles at the edge
#
    head  = 'i_2'
    area  = ['[1:1024,1:256]', '[1:1024,257:508]', '[1:1024,513:768]', '[1:1024,769:1020]']
    sec   =  ['0', '1', '2', '3']
    run_comp_stat(year, month, head, sec, area)
#
#--- ACIS I3
#
    head  = 'i_3'
    area  = ['[1:1024,769:1020]', '[1:1024,513:768]', '[1:1024,257:508]', '[1:1024,1:256]']
    run_comp_stat(year, month, head, sec, area)
#
#--- ACIS S2
#
    head  = 's_2'
    area  = ['[1:256,1:1020]', '[257:508,1:1020]', '[513:768,1:1020]', '[769:1024,1:1020]']
    run_comp_stat(year, month, head, sec, area)
#
#--- ACIS S3
#
    head  = 's_3'
    area  = ['[1:256,1:1020]', '[257:508,1:1020]', '[513:768,1:1020]', '[769:1024,1:1020]']
    run_comp_stat(year, month, head, sec, area)

#----------------------------------------------------------------------------
#-- run_comp_stat: set up the input and run comp_stat to write out the stat results 
#----------------------------------------------------------------------------

def run_comp_stat(year, month, head, sec, area):
    """
    set up the input and run comp_stat to write out the stat results
    input:  year    --- year
            month   --- month
            head    --- indicator of which ccd (e.g., 'i_2', 's_3)
            sec     --- a list of section of ccd
            area    --- a list of area of ccd to be extracted (e.g., '[1:256,1:1020]')
    output: updated <data_dir>/<ccd#>_<node#>_<diff/acc>_out
    """
#
#--- set input file names
#
    tail  = head.replace('_', '')
    syear = str(year)
    smon  = mcf.add_leading_zero(month)

    name1 = cum_acis_dir + 'ACIS_07_1999_' + smon + '_' + syear + '_' + tail + '.fits.gz'
    name2 = mon_acis_dir + 'ACIS_'         + smon + '_' + syear + '_' + tail + '.fits.gz'

    for k in range(0, 4):
#
#--- cummulative stat
#
        line = name1 + area[k]
        out  = head + '_n_' + str(sec[k]) + '_acc_out'
        comp_stat(line, year, month, out)
#
#--- this month's stat
#
        line = name2 + area[k]
        out  = head + '_n_' + str(sec[k]) + '_dff_out'
        comp_stat(line, year, month, out)

#-------------------------------------------------------------------------------
#-- comp_stat: compute statistics and print them out                         ---
#-------------------------------------------------------------------------------

def comp_stat(line, year, month, outfile):
    """
    compute statistics and print them out
    input:  line    --- command line, year, month, and output file name
                        command line is used by dmcopy to extract a specific location 
                            Example: ACIS_04_2012.fits.gz[1:1024,1:256]
            year    --- year
            month   --- month
            outfile --- output file name
    output: outfile --- stat results in outfile
    """
    cmd = ' dmcopy ' + line + ' temp.fits clobber="yes"'
    expf.run_ascds(cmd)
#
#-- to avoid get min from outside of the edge of a CCD
#
    cmd = ' dmimgthresh infile=temp.fits  outfile=zcut.fits  cut="0:1e10" value=0 clobber=yes'
    expf.run_ascds(cmd)
#
#-- find avg, min, max and deviation
#
    [avg, minv, minp, maxv, maxp, dev] = extract_stat_result('zcut.fits')
#
#-- find the one sigma and two sigma count rate:
#
    [sigma1, sigma2, sigma3] = expf.three_sigma_values('zcut.fits')

    print_stat(avg, minv, minp, maxv, maxp, dev, sigma1, sigma2, sigma3,\
               year, month, outfile)

    mcf.rm_files('temp.fits')
    mcf.rm_files('zcut.fits')

#-------------------------------------------------------------------------------
#-- extract_stat_result: extract stat informaiton                             --
#-------------------------------------------------------------------------------

def extract_stat_result(ifile):
    """
    extract stat informaiton
    input:  ifile   --- image fits file 
    output: avg     --- mean
            minp    --- min
            maxp    --- max
            devp    --- sigma
    """
    cmd = ' dmstat infile=' + ifile + '  centroid=no >' + zspace
    expf.run_ascds(cmd)

    data = mcf.read_data_file(zspace, remove=1)
#
#--- extract mean, dev, min, and max
#
    for  ent in data:
        atemp = re.split('\s+|\t+', ent)

        m1 = re.search('mean', ent)
        m2 = re.search('min',  ent)
        m3 = re.search('max',  ent)
        m4 = re.search('sigma',ent)

        if m1 is not None:
            avg   = atemp[1]

        if m2 is not None:
            minv   = atemp[1]
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            minp  = '(' + ctemp[1] + ',' + ctemp[2] + ')'

        if m3 is not None:
            maxv   = atemp[1]
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            maxp  = '(' + ctemp[1] + ',' + ctemp[2] + ')'

        if m4 is not None:
            dev = atemp[1]

    return [avg, minv, minp, maxv,  maxp, dev]

#-------------------------------------------------------------------------------
#-- print_stat: print out statistic                                          ---
#-------------------------------------------------------------------------------

def print_stat(avg, minv, minp, maxv, maxp, dev, sigma1, sigma2, sigma3,\
               year, month, outfile):
    """
    print out statistics
    input:  avg     --- mean
            minv    --- min value
            minp    --- min position
            maxv    --- max value
            maxp    --- max position
            dev     --- dev
            sigma1  --- one sigma value
            simga2  --- two sigma value
            sigma3  --- trhee sigma value
            year    --- year
            month   --- month
            outfile --- the name of output file
    output: outfile
    """
#
#--- print out data
#
    line = '%i\t%i\t'       % (year, month)
    line = line + '%5.6f\t%5.6f\t' % (float(avg), float(dev))
    line = line + '%5.1f\t%s\t'    % (float(minv), minp)
    line = line + '%5.1f\t%s\t'    % (float(maxv), maxp)
    line = line + '%5.1f\t%5.1f\t%5.1f\n'    % (float(sigma1), float(sigma2), float(sigma3))

    out  = data_out + outfile
    with open(out, 'a') as f:
        f.write(line)

#----------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 3:
        year = sys.argv[1] 
        year = int(year)
        mon  = sys.argv[2]
        mon  = int(mon)
    else:
        year = 'na'
        mon  = 'na'
    
    acis_dose_extract_stat_data_month(year, mon)
