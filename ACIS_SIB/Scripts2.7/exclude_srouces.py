#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           exclude_srouces.py:   remove the area around the main source and all point sources from data    #
#                                 probably this is a good one to use evt2 files as it takes too much time   #
#                                 run on evt1 file. The results save in Reg_files can be used to removed    #
#                                 sources from evt 1 files.                                                 #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Apr 07, 2016                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import Cookie
import unittest
import time
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release;  source /home/mta/bin/reset_param ', shell='tcsh')
#ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/Lev1/Reportdir/'
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- directory path
#
s_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/'
b_dir = s_dir + 'Sib_corr/'

#
#--- append path to a private folders
#
sys.path.append(b_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import sib_corr_functions   as scf

#
#--- temp writing file name
#
rtail   = int(time.time())
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
#--- read which ccds are used and several other info from fits header
#
    cmd = ' dmlist ' + fits + ' opt=head > ' + zspace
    scf.run_ascds(cmd)

    data = scf.read_file(zspace, remove=1)

    ccd_list = []
    for ent in data:
        mc = re.search('bias file used', ent)
        if mc is not None:
            atemp = re.split('CCD', ent)
            val   = atemp[1].strip()
            ccd_list.append(val)
            continue

        for name in ['SIM_X', 'SIM_Y', 'SIM_Z', 'RA_NOM', 'DEC_NOM', 'ROLL_NOM', 'RA_TARG', 'DEC_TARG']:
            mc = re.search(name, ent)
            if mc is not None:
                lname = name.lower()
                atemp = re.split('\s+', ent)
                val   = atemp[2].strip()
                exec "%s = %s" % (lname, val)

                break
#
#--- sort ccd list
#
    ccd_list.sort()
#
#--- guess a source center position on the sky coordinates from the information extracted from the header
#
    cmd = ' dmcoords none none opt=cel '
    cmd = cmd + ' ra=' + str(ra_targ)  + ' dec=' + str(dec_targ )
    cmd = cmd + ' sim="' + str(sim_x) + ' ' +  str(sim_y) + ' ' + str(sim_z) + '" ' 
    cmd = cmd + ' detector=acis celfmt=deg '
    cmd = cmd + ' ra_nom=' + str(ra_nom) + ' dec_nom=' + str(dec_nom) + ' roll_nom=' + str(roll_nom) + ' ' 
    cmd = cmd + ' ra_asp=")ra_nom" dec_asp=")dec_nom" verbose=1 >' + zspace 

    scf.run_ascds(cmd)

    data = scf.read_file(zspace, remove=1)

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

    fo         = open(ofile, 'w')
    fo.write(line)
    fo.close()
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
        cmd = ' dmcopy "' + fits + '[ccd_id=' + str(ccd) + ']" outfile=test.fits clobber=yes'
        scf.run_ascds(cmd)
        
        cmd  = 'ls -l test.fits > ' + zspace
        os.system(cmd)

        data = scf.read_file(zspace, remove=1)

        for line in data:
            atemp = re.split('\s+', line)
            if mcf.chkNumeric(atemp[4]):
                size[ccd] = int(float(atemp[4]))
            else:
                size[ccd] = int(float(atemp[3]))

        mcf.rm_file('test.fits')
#
#--- now separate observations to indivisual ccds
#
    file_list = []
    for ccd in ccd_list:
        tail = '_ccd' + str(ccd) + '.fits'
        out  = o_fits.replace('.fits', tail)
        file_list.append(out)

        cmd = ' dmcopy "source_removed.fits[ccd_id=' + ccd + ']" outfile= ' + out + ' clobber=yes'
        scf.run_ascds(cmd)

    mcf.rm_file('source_removed.fits')
#
#--- process each ccd
#
    for pfits in file_list:
        reg_file = pfits.replace('.fits', '_block_src.reg')
#
#--- find point sources
#
        cmd = ' celldetect infile=' + pfits 
        cmd = cmd + ' outfile=acisi_block_src.fits regfile=acisi_block_src.reg clobber=yes'
        scf.run_ascds(cmd)

        data = scf.read_file('acisi_block_src.reg')
        
        exclude = []
        for ent in data:
            atemp =  re.split('\,', ent)
#
#--- increase the area covered around the sources 3time to make sure leaks from a bright source is minimized
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
                    cmd = ' dmcopy "' + pfits + '[exclude sky=' + line +']" outfile=out.fits clobber="yes"'
                    scf.run_ascds(cmd)
                    round += 1
                else:
                    cmd = 'mv out.fits temp.fits'
                    os.system(cmd)
                    cmd = ' dmcopy "temp.fits[exclude sky=' + line +']" outfile=out.fits clobber="yes"'
                    scf.run_ascds(cmd)
                    round += 1

                if chk > 0:
                    break 
                else:
                    line = ''

            mcf.rm_file('temp.fits')
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

        data = scf.read_file(zspace, remove=1)

        for line in data:
            atemp = re.split('\s+', line)
            if mcf.chkNumeric(atemp[4]):
                asize = float(atemp[4])
            else:
                asize = float(atempp[3])
    
        for pccd in range(0, 10):
            check = 'ccd' + str(pccd)
            mc  = re.search(check,  out_name)
            if mc is not None:
                break
#
#--- compute the ratio of the cleaned to the original file; 1 - ratio is the  potion that we removed
#--- from the original data
#
        ratio = asize / float(size[str(pccd)])
#
#--- record the ratio for later use
#
        fo   = open('./Reg_files/ratio_table', 'a')
        line = reg_file + ': ' + str(ratio) + '\n'
        fo.write(line)
        fo.close()
                    
        cmd = 'mv acisi_block_src.reg ./Reg_files/' + reg_file
        os.system(cmd)
        mcf.rm_file('acisi_block_src.fits')

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        fits = sys.argv[1]
        fits.strip()

    exclude_sources(fits)

