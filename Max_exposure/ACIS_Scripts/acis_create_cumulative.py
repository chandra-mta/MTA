#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       acis_create_cumulative.py: separate given acis image to sections and crate      #
#                                  cumulative image files                               #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Mar 09, 2021                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
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

import mta_common_functions as mcf
import exposureFunctions    as expf

#-------------------------------------------------------------------------------------------
#-- acis_create_cumulative: create four small section images and create cumulatvie images --
#-------------------------------------------------------------------------------------------
            
def acis_create_cumulative(ifile='NA'):

    """
    create four small section images and create cumulatvie images
    input: ifile    --- input file name (e.g. ACIS_05_2012.fits)
    output: <cum_acis_dir>/ACIS_07_1999_<mm>_<yyyy>*.fits.gz
    """
    if ifile == 'NA':
        ifile = raw_input('Input file name (ACIS_<month>_<year>.fits*): ')
        ifile = ifile.strip()
#
#--- find the designated date of the fits file (ifile example: ACIS_12_2018.fits)
#
    atemp = re.split('.fits', ifile)
    btemp = re.split('ACIS_', atemp[0])
    erange= btemp[1]
    ctemp = re.split('_', erange)
    mon   = int(ctemp[0])
    year  = int(ctemp[1])
#
#--- set the date of the last cummulative data files  (a month before current one)
#
    lmon  = mon - 1
    lyear = year
    if lmon < 1:
        lmon   = 12
        lyear -= 1

    smon  = mcf.add_leading_zero(lmon)
    syear = str(lyear)
#
#--- full image
#
    last = cum_acis_dir  + 'ACIS_07_1999_' + smon   + '_' + syear + '.fits.gz'
    out  = cum_acis_dir  + 'ACIS_07_1999_' + erange + '.fits'
    cmd  = 'dmimgcalc ' + last + ' ' + ifile + ' ' + out + ' add'
    expf.run_ascds(cmd)

    cmd  = 'gzip -f ' + out
    os.system(cmd)
#
#--- CCD I2
#
    section_cum(ifile, erange, syear, smon, 'i2', '[264:1285,1416:2435]')
#
#--- CCD I3
#
    section_cum(ifile, erange, syear, smon, 'i3', '[1310:2331,1416:2435]')
#
#--- CCD S2
#
    section_cum(ifile, erange, syear, smon, 's2', '[80:1098,56:1076]')
#
#--- CCD S3
#
    section_cum(ifile, erange, syear, smon, 's3', '[1122:2141,56:1076]')
#
#--- moving this month's full image fits file to an appropriate directory
#
    mc = re.search('gz', ifile)
    if mc is None:
        cmd = 'gzip -f ' +  ifile
        os.system(cmd)

    mc = re.search(mon_acis_dir, ifile)
    if mc is None:
        cmd = 'mv ' + ifile + '* ' + mon_acis_dir + '/.'
        os.system(cmd)

#--------------------------------------------------------------------------------
#-- section_cum: create cummulative image of chip specified                    --
#--------------------------------------------------------------------------------

def section_cum(ifile, erange, syear, smon, chip, s_out):
    """
    create cummulative image of chip specified
    input:  ifile   --- full ACIS image
            erange  --- date of the current image (e.g. 12_2018)
            syear   --- year of the last cummulative image
            smon    --- month of the last cummulative image
            chip    --- ccd (e.g., i2, s3)
            s_out   --- chip rnage (e.g. [264:1285,1416:2435] for i2)
    output: <cum_acis_dir>/ACIS_07_1999_<mm>_<yyyy>_<chip>.fits.gz
            <mon_acis_dir>/ACIS_<mm>_<yyy>_<chip>.fits.gz
    """
#
#--- create an image fits file for a given ccd (chip) of this month
#
    sec  = mon_acis_dir + 'ACIS_' + erange + '_' + chip + '.fits'
    cmd  = 'dmcopy ' + ifile + s_out + ' ' + sec
    expf.run_ascds(cmd)
#
#--- create an cummulative image fits file for the ccd
#
    last = cum_acis_dir + 'ACIS_07_1999_' + smon   + '_' + syear + '_' + chip + '.fits.gz'
    out  = cum_acis_dir + 'ACIS_07_1999_' + erange               + '_' + chip + '.fits'
    cmd  = 'dmimgcalc ' + last + ' ' + sec + ' ' + out + ' add'
    expf.run_ascds(cmd)
#
#--- gzip the created files
#
    cmd = 'gzip -f ' + sec + ' ' + out
    os.system(cmd)


#--------------------------------------------------------------------------------

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        ifile = sys.argv[1].strip()
    else:
        ifile = 'NA'

    acis_create_cumulative(ifile)
