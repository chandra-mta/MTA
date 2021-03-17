#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#   exclude_srouces.py:   remove the area around the main source and all point sources from data    #
#                         probably this is a good one to use evt2 files as it takes too much time   #
#                         run on evt1 file. The results save in Reg_files can be used to removed    #
#                         sources from evt 1 files.                                                 #
#                                                                                                   #
#   author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                   #
#   Last Update: Mar 03, 2021                                                                       #
#                                                                                                   #
#####################################################################################################

import sys
import os
import string
import re
import copy
import math
import unittest
import time
import random
import numpy
import astropy.io.fits as pyfits
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release;  source /home/mta/bin/reset_param ', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folders
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import sib_corr_functions   as scf
#
#--- temp writing file name
#
rtail   = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- exclude_sources: remove the area around the main source and all point sources from data 
#-----------------------------------------------------------------------------------------

def exclude_sources(fits):
    """
    remove the area around the main source and all point sources from data
    input:  fits        --- input fits file name
    output: out_name    --- source removed fits file (<header>_ccd<ccd>_cleaned.fits)
    """
#
#--- read fits header
#
    fout = pyfits.open(fits)
#
#--- find which ccds used
#
    ccd_list = []
    for k in range(0, 10):
        bname = 'BIASFIL' + str(k)
        try:
            val = fout[1].header[bname]
            ccd_list.append(k)
        except:
            continue

    ccd_list.sort()
#
#--- create key word dictionary
#
    v_dict = {}
    for name in ['SIM_X', 'SIM_Y', 'SIM_Z', 'RA_NOM', 'DEC_NOM', 'ROLL_NOM', 'RA_TARG', 'DEC_TARG']:
        lname = name.lower()
        try:
            out = fout[1].header[name]
            v_dict[lname] = str(out)
        except:
            v_dict[lname] =  'NA'
#
#--- guess a source center position on the sky coordinates from the information extracted from the header
#
    cmd = ' dmcoords none none opt=cel '
    cmd = cmd + ' ra=' + v_dict['ra_targ'] + ' dec=' + v_dict['dec_targ']
    cmd = cmd + ' sim="' + v_dict['sim_x'] + ' ' +  v_dict['sim_y'] + ' ' + v_dict['sim_z'] + '" ' 
    cmd = cmd + ' detector=acis celfmt=deg '     + ' ra_nom=' + v_dict['ra_nom'] 
    cmd = cmd + ' dec_nom=' + v_dict['dec_nom']  + ' roll_nom=' + v_dict['roll_nom'] + ' ' 
    cmd = cmd + ' ra_asp=")ra_nom" dec_asp=")dec_nom" verbose=1 >' + zspace 

    scf.run_ascds(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    for ent in data:
        mc = re.search('SKY', ent)
        if mc is not None:
            atemp = re.split('\s+', ent)
            skyx  = atemp[1]
            skyy  = atemp[2]
            break
#
#-- keep the record of the source position for the later use (e.g. used for evt1 processing);
#
    o_fits     = fits.replace('.gz', '')
    coord_file = o_fits.replace('.fits', '_source_coord')
    ofile      = './Reg_files/' + coord_file
    line       = str(skyx) + ':' + str(skyy) + '\n'

    with open(ofile, 'w') as fo:
        fo.write(line)
#
#-- remove the 200 pix radius area around the source
#
    cmd = ' dmcopy "' + fits + '[exclude sky=circle(' + skyx + ',' + skyy + ',200)]" '
    cmd = cmd + ' outfile=source_removed.fits clobber="yes"'
    scf.run_ascds(cmd)
#
#--- get a file size: will be used to measure the size of removed area later.
#--- assumption here is the x-ray hit ccd evenly, but of course it is not, 
#--- but this is the best guess we canget
#
    size = {}
    for ccd in ccd_list:
        cmd = ' dmcopy "' + fits + '[ccd_id=' + str(ccd) 
        cmd = cmd + ']" outfile=test.fits clobber=yes'
        scf.run_ascds(cmd)
        
        cmd  = 'ls -l test.fits > ' + zspace
        os.system(cmd)

        data = mcf.read_data_file(zspace, remove=1)

        for line in data:
            atemp = re.split('\s+', line)
            try:
                size[ccd] = int(float(atemp[4]))
            except:
                size[ccd] = int(float(atemp[3]))

        mcf.rm_files('test.fits')
#
#--- now separate observations to indivisual ccds
#
    file_list = []
    for ccd in ccd_list:
        tail = '_ccd' + str(ccd) + '.fits'
        out  = o_fits.replace('.fits', tail)
        file_list.append(out)

        cmd = ' dmcopy "source_removed.fits[ccd_id=' + str(ccd)
        cmd = cmd + ']" outfile= ' + out + ' clobber=yes'
        scf.run_ascds(cmd)

    mcf.rm_files('source_removed.fits')
#
#--- process each ccd
#
    for pfits in file_list:
        reg_file = pfits.replace('.fits', '_block_src.reg')
#
#--- find point sources
#
        cmd = ' celldetect infile=' + pfits 
        cmd = cmd + ' fixedcell=9 outfile=acisi_block_src.fits regfile=acisi_block_src.reg clobber=yes'
        scf.run_ascds(cmd)

        data = mcf.read_data_file('acisi_block_src.reg')
        
        exclude = []
        for ent in data:
            atemp =  re.split('\,', ent)
#
#--- increase the area covered around the sources 3 times to make sure leaks 
#--- from a bright source is minimized
#
            val2 = float(atemp[2]) * 3
            val3 = float(atemp[3]) * 3
            line = atemp[0] + ',' + atemp[1] + ',' + str(val2) + ',' + str(val3) +',' + atemp[4]
            exclude.append(line)

        out_name = pfits.replace('.gz','')
        out_name = out_name.replace('.fits', '_cleaned.fits')
#
#--- if we actually found point sources, remove them from the ccds
#
        e_cnt = len(exclude)
        if e_cnt  > 0:
            cnt   = 0
            chk   = 0
            round = 0
            line  = ''
            while cnt < e_cnt:
#
#--- remove 6 sources at a time so that it won't tax memory too much
#
                for i in range(cnt, cnt + 6):
                    if i >= e_cnt:
                        chk += 1
                        break

                    if line == '':
                        line = exclude[i]
                    else:
                        line = line + '+' + exclude[i]

                cnt += 6
                if round == 0:
                    cmd = ' dmcopy "' + pfits + '[exclude sky=' + line 
                    cmd = cmd +']" outfile=out.fits clobber="yes"'
                    scf.run_ascds(cmd)
                    round += 1
                else:
                    cmd = 'mv out.fits temp.fits'
                    os.system(cmd)
                    cmd = ' dmcopy "temp.fits[exclude sky=' + line 
                    cmd = cmd +']" outfile=out.fits clobber="yes"'
                    scf.run_ascds(cmd)
                    round += 1

                if chk > 0:
                    break 
                else:
                    line = ''

            mcf.rm_files('temp.fits')
            cmd = 'mv out.fits ' + out_name
            os.system(cmd)
        else:
            cmd = 'cp ' + pfits + ' ' + out_name
            os.system(cmd)
#
#--- find the size of cleaned up file size
#
        cmd = 'ls -l ' + out_name + '>' + zspace
        os.system(cmd)

        data = mcf.read_data_file(zspace, remove=1)

        for line in data:
            atemp = re.split('\s+', line)
            try:
                asize = float(atemp[4])
            except:
                asize = float(atempp[3])
    
        for pccd in range(0, 10):
            check = 'ccd' + str(pccd)
            mc  = re.search(check,  out_name)
            if mc is not None:
                break
#
#--- compute the ratio of the cleaned to the original file; 
#--- 1 - ratio is the  potion that we removed from the original data
#
        #ratio = asize / float(size[str(pccd)])
        ratio = asize / float(size[pccd])
#
#--- record the ratio for later use
#
        with open('./Reg_files/ratio_table', 'a') as fo:
            line = reg_file + ': ' + str(ratio) + '\n'
            fo.write(line)
                    
        cmd = 'mv acisi_block_src.reg ./Reg_files/' + reg_file
        os.system(cmd)
        mcf.rm_files('acisi_block_src.fits')

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        fits = sys.argv[1]
        fits.strip()

        exclude_sources(fits)

    else:
        print("Provide a fits file name")

