#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_create_image.py: convert acis fits files to png image files           #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 09, 2021                                                       #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import fnmatch 
import time
import random
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
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
#--- this convert fits files to image files
#
#import mta_convert_fits_to_image as mtaimg
import exposureFunctions    as expf
import mta_common_functions as mcf
#
#--- set temp directory/file
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------
#---  create_acis_maps: create HRC image maps for given year and month       ----
#--------------------------------------------------------------------------------

def create_acis_maps(year, month):
    """
    create ACIS image maps for given year and month 
    input:  year    --- year
            month   --- month
    """
#
#--- images for the center part; <mon_dir> etc. are read from <house_keeping>/dir_list
#
    acis_dose_conv_to_png(mon_acis_dir, img_dir, year, month)
    acis_dose_conv_to_png(cum_acis_dir, img_dir, year, month)

#--------------------------------------------------------------------------------
#--- acis_dose_conv_to_png: prepare to convet fits files into png images      ---
#--------------------------------------------------------------------------------

def acis_dose_conv_to_png(indir, outdir, year, month):
    """
    prepare to convet fits files into png images, 
    input:  indir   --- directory where input fits file located
            outdir  --- directory where png files will be moved
            year    --- year
            month   --- month
    output: outfile --- <outdir>/ACIS*_<smon>_<syear>.png
    """
    scale   = 'sqrt'
    #color   = 'rainbow'
    color   ='sls'

    syear = str(year)
    smon  = mcf.add_leading_zero(month)
    hname =  'ACIS*' + smon + '_' + syear + '*.fits*'

    for ifile in os.listdir(indir):

        if fnmatch.fnmatch(ifile, hname):
            file_p  = indir + ifile

            btemp   = re.split('\.fits', ifile)
            out     = btemp[0]
            outfile = outdir + out + '.png'

            expf.convert_fits_to_img(file_p, scale, color, outfile, chk=1)
        else:
            pass

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def old_fit_to_image(file_p, outfile):
    """
    this one is an older form of create_acis_img --- not used 
    """
    mtaimg.mta_convert_fits_to_image(file_p, outfile, 'log', '125x125', 'heat', 'png')
    cmd = 'convert -trim ' + outfile + '.png ztemp.png'
    os.system(cmd)
    cmd = 'mv ztemp.png ' + outfile + '.png'
    os.system(cmd)

#--------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 3:
        year  = int(sys.argv[1])
        month = int(sys.argv[2])

        create_acis_maps(year, month)
    else:
        print("Provide year and month of the image to be created")
