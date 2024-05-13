#!/proj/sot/ska3/flight/bin/python

#################################################################################################
#                                                                                               #
#       mta_convert_fits_to_image.py: convert a fits img file to a ps, gif, jpg, or png file    #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Mar 15, 2021                                                               #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import time
import random
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- add mta common function
#
mta_dir = '/data/mta4/Script/Python3.11/MTA/'
sys.path.append(mta_dir)
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------------
#-- mta_convert_fits_to_image: convert a fits img file to a ps, gif, jpg, or png file ---
#----------------------------------------------------------------------------------------

def mta_convert_fits_to_image(infile, outfile, scale = 'log', \
                              size = '125x125', color = 'heat', itype = 'png'):
    """
    convert a fits img file to a ps, gif, jpg, or png file 
    input:  infile  --- input fits file name
            outfile --- output png file name without a suffix
            scale   --- scale of the output image; log, linear, or power
            size    --- size of the output image; format: 125x125 
                            --- no contorl of size on ps and jpg file
            color   --- color of the output image: hear, rainbow1 etc. default is grey
                        to see which color is available, 
                        type: 'ls /home/ascds/DS.release/data/*.lut'
            itype    --- image type: ps, gif, jpg, or png
    output: outfile
    """
#
#--- set scale
#
    if (scale.lower() != 'log') and (scale.lower() != 'power'):
        scale = 'linear'
#
#--- set default size
#
    if size == '' or size == '-':
        size = '125x125'
#
#--- read color list
#
    cmd  = 'ls /home/ascds/DS.release/data/*.lut > ' + zspace
    os.system(cmd)
    with open(zspace) as f:
        data = [line.strip() for line in f.readlines()]

    color_list = []
    for ent in data:
        atemp = re.split('data\/', ent)
        btemp = re.split('\.lut',  atemp[1])
        color_list.append(btemp[0])
#
#--- make sure the color specified is in the list, if not, assign grey
#
    if not (color in color_list):
        color = 'grey'
#
#--- set output format
#
    if not (itype.lower() in ['ps', 'gif', 'jpg', 'png']):
        itype = 'gif'
#
#--- define output file name
#
    outfile = outfile + '.' + itype
#
#--- convert a fits image into an eps image
#
    cmd2 = 'dmimg2jpg ' + infile + ' greenfile="" bluefile="" regionfile="" '
    cmd2 = cmd2 + 'outfile="foo.jpg" scalefunction="'+ scale 
    cmd2 = cmd2 + '" psfile="foo.ps"  lut=")lut.'    + color + '" showgrid=no  clobber="yes"'

    cmd1 = "/usr/bin/env PERL5LIB= "
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
#
#--- convert and move the image to the correct format and file name
#
    if itype == 'ps':
        cmd = 'mv foo.ps ' + outfile
        os.system(cmd)

    elif itype == 'jpg':
        cmd = 'mv foo.jpg ' + outfile
        os.system(cmd)

    elif itype == 'gif':
        cmd = 'echo ""|gs -sDEVICE=ppmraw  -r' + size 
        cmd = cmd + '  -q -NOPAUSE -sOutputFile=-  ./foo.ps |' 
        cmd = cmd + 'ppmtogif > ' + outfile
        os.system(cmd)

    elif itype == 'png':
        cmd = 'echo ""|gs -sDEVICE=ppmraw  -r' + size 
        cmd = cmd + '  -q -NOPAUSE -sOutputFile=-  ./foo.ps |' 
        cmd = cmd +  'pnmtopng > ' + outfile
        os.system(cmd)

    os.system('rm foo.*')

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) < 3:
        infile = '/data/mta_www/mta_max_exp/Cumulative/ACIS_07_1999_04_2012_s3.fits.gz'
        outfile='test'
        scale  = 'log'
        size   = '125x125'
        color  = 'heat'
        itype  = 'png'
    else:
        infile  = sys.argv[1]
        outfile = sys.argv[2]
        scale  = 'log'
        size   = '125x125'
        color  = 'heat'
        itype  = 'png'

    mta_convert_fits_to_image(infile, outfile, scale, size, color, itype)


