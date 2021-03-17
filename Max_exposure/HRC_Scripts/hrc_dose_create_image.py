#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       hrc_dose_create_image.py: convert hrc fits files to png image files                     #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Mar 09, 2021                                                               #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import fnmatch 
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
#--- append path to a privte folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- this convert fits files to image files
#
import exposureFunctions         as expf
import mta_common_functions      as mcf

#------------------------------------------------------------------------------------
#---  create_hrc_maps: create HRC image maps for given year and month            ----
#------------------------------------------------------------------------------------

def create_hrc_maps(year= 'NA', month= 'NA'):
    """
    create HRC image maps for given year and month 
    input: year    --- year
           month   --- month
    output: <outdir>/<out.png
    """
#
#--- if year and month are not given, set the date of the last month
#
    if year == 'NA' or month == 'NA':
        [year, month, day] = mcf.today_date()
        month -= 1
        if month < 1:
            month = 12
            year -= 1
#
#--- create images
#
    hrc_dose_conv_to_png(mon_hrc_dir, img_dir, year, month)
    hrc_dose_conv_to_png(cum_hrc_dir, img_dir, year, month)

#------------------------------------------------------------------------------------
#--- hrc_dose_conv_to_png: prepare to convet fits files into png images           ---
#------------------------------------------------------------------------------------

def hrc_dose_conv_to_png(indir, outdir, year, month):
    """
    prepare to convet fits files into png images, input: indir, outdir, year, month
    input:  indir   --- input directory
            outdir  --- output directory
            year    --- year
            month   --- month
    output: <outdir>/<out>.png
    """
    scale   = 'sqrt'
    color   = 'sls'

    syear = str(year)
    smon  = mcf.add_leading_zero(month)

    hname =  'HRC*' + smon + '_' + syear + '*.fits*'

    for ifile in os.listdir(indir):

        if fnmatch.fnmatch(ifile, hname):
            file_p  = indir + ifile

            btemp   = re.split('\.fits', ifile)
            out     = btemp[0]
            outfile = outdir + out + '.png'
#
#--- if the image is cummulative one, apply 99.5% cut
#
            mc = re.search('_08_1999_', file_p)
            if mc is not None:
                expf.convert_fits_to_img(file_p, scale, color, outfile, chk=1)
            else:
                expf.convert_fits_to_img(file_p, scale, color, outfile)

        else:
            pass

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':

    create_hrc_maps()


