#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#           find_pointing_data.py: update pointing database                 #
#                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                   #
#                                                                           #
#               last update: Mar 03, 2021                                   #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
import astropy.io.fits as pyfits
import unittest
from datetime import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; punlearn dataseeker  ', shell='tcsh')
#
#--- plotting routine
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
#
#--- reading directory list
#
path = '/data/mta/Script/ALIGNMENT/Abs_pointing/Scripts/house_keeping/dir_list'

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
import mta_common_functions as mcf #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
import random

rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- year 2000 1.1
#
y2000 = 63071999.0
d_rad = 0.017453292

#---------------------------------------------------------------------------------------
#-- update_pointing_data: update pointing database                                   ---
#---------------------------------------------------------------------------------------

def update_pointing_data():
    """
    update pointing database
    input:  none
    output: acis_i_data/aics_s_data/hrc_i_data/hrc_s_data in <data_dir>
    """
#
#--- read all avaialble observations
#
    [obsid_list,obs_dict, inst_dict] = create_obsid_name_dict()

    obs_coord_dict  = find_candidate(obsid_list, obs_dict)
    if obs_coord_dict == False:
        exit(1)

    obsid_list = obs_coord_dict.keys()

    acis_i     = []
    acis_s     = []
    hrc_i      = []
    hrc_s      = []
    for obsid in obsid_list:
        detector = inst_dict[obsid].lower()
        atemp    = re.split('-', detector)
        inst     = atemp[0].lower()

        fits = run_arc5gl('retrieve', 'flight', inst, '1', 'evt1', obsid)
        if fits == '':
            continue

        try:
            [otime, grating, roll] = read_header_info(fits)
        except:
            mcf.rm_files(fits)
            continue

        try:
            cout = find_source_coord(fits, detector)
        except:
            mcf.rm_files(fits)
            continue

        mcf.rm_files(fits)

        if cout == False:
            continue

        [ra, dec, dra, ddec]   = obs_coord_dict[obsid]
        [ra, dec]              = convert_ra_dec_format(ra, dec)
        [ra, dec]              = correct_prop_motion(ra, dec, dra, ddec, otime)

        [dx, dy]               = find_coord_diff(ra, dec, cout[0], cout[1], roll)
#
#--- remove the large coordinate difference source; probably they are pointing a wrong source
#
        try:
            adx = abs(dx)
            ady = abs(dy)
        except:
            continue
        if (adx > 3 ) or (ady > 3):
            continue

        name = obs_dict[obsid]
        try:
            line = create_data_line(otime, obsid, name, ra, dec, cout[0], cout[1],\
                                    dx, dy, grating)
        except:
            continue

        if detector == 'acis-i':
            write_file(line, 'acis_i_data', ls=0)

        elif detector == 'acis-s':
            write_file(line, 'acis_s_data', ls=0)

        elif detector == 'hrc-i':
            write_file(line, 'hrc_i_data',  ls=0)

        elif detector == 'hrc-s':
            write_file(line, 'hrc_s_data',  ls=0)

#---------------------------------------------------------------------------------------
#-- create_data_line: create output data line                                         --
#---------------------------------------------------------------------------------------

def create_data_line(otime, obsid, name, ra, dec, cra, cdec, dy, dz, grating):        
    """
    create output data line
    input:  otime   --- time in seconds from 1998.1.1
            obsid   --- obsid
            name    --- object name
            ra      --- nominal ra
            dec     --- nominal dec
            cra     --- estimated ra
            cdec    --- estimated dec
            dy      --- difference in y coords
            dz      --- difference in z coords
            grating --- grating
    output: line    --- formated output line
    """

    line = "%d\t%d\t" % (otime, obsid)
    line = line + name.rjust(16) + '\t'
    line = line + '%3.9f\t' % ra
    line = line + '%3.9f\t' % dec
    line = line + '%3.9f\t' % cra
    line = line + '%3.9f\t' % cdec
    line = line + '%3.4f\t' % dy
    line = line + '%3.4f\t' % dz
    line = line + grating + '\n'

    return line

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def update_data(acis_i, acis_s, hrc_i, hrc_s):

    if len(acis_i) > 0:
        write_file(acis_i, 'acis_i_data')

    if len(acis_s) > 0:
        write_file(acis_s, 'acis_s_data')

    if len(hrc_i) > 0:
        write_file(hrc_i,  'hrc_i_data')

    if len(hrc_s) > 0:
        write_file(hrc_s,  'hrc_s_data')

#---------------------------------------------------------------------------------------
#-- write_file: create/update data file                                              ---
#---------------------------------------------------------------------------------------

def write_file(data, outfile, ls=1):
    """
    create/update data file
    input:  data    --- data, either a line or a list
            outfile --- a output file name
            ls      --- if 0, input is a line, else, it is a list
    output: <data_dir>/outfile
    """

    outfile = data_dir + outfile

    if ls == 0:
        with open(outfile, 'a') as fo:
            fo.write(data)
    else:
        line = ''
        for ent in data:
            line = line + ent

        with open(outfile, 'a') as fo:
            fo.write(ent)
    
        cmd = 'sort ' + outfile
        os.system(cmd)

#---------------------------------------------------------------------------------------
#-- find_candidate: find candiates for farther analysis                               --
#---------------------------------------------------------------------------------------

def find_candidate(obsid_list, obs_dict):
    """
    find candiates for farther analysis
    input:  obsid_list  --- a list of obsids
            obs_idct    --- a dictionary of obsid <---> object name
    output: obsid_coord_dict    --- a dictionary of obsid <---> coordinates
                                    it may return False, if there is no candidate
    """
#
#--- find already processed data
#
    ifile      = house_keeping + 'observed_obsids'
    done_list  = mcf.read_data_file(ifile)
#
#--- find which ones are not processed
#
    not_done   = list(numpy.setdiff1d(obsid_list, done_list))

    if len(not_done) > 0:
#
#--- update observed_obsids list
#
        sline = ''
        for ent in obsid_list:
            sline = sline + str(ent) + '\n'

        with open(ifile, 'w') as fo:
            fo.write(sline)
#
#--- find candidates
#
        obs_coord_dict = create_candidate_obsid_list(not_done, obs_dict)

        return obs_coord_dict

    else:
        return False

#---------------------------------------------------------------------------------------
#-- create_candidate_obsid_list: create a list of objects which requres farther analysis 
#---------------------------------------------------------------------------------------

def create_candidate_obsid_list(not_done, obs_dict):
    """
    create a list of objects which requres farther analysis
    input:  not_done            --- a list of obsids which have not been analyzed
            obs_dict            --- a dictioinary of obsid <---> object name
    output: obsid_coord_dict    --- a dictionary of obsid <---> coordinates
                                    it may return False, if there is no candidate
    """
#
#--- read already known coordinates
#
    coord_dict = make_coord_list()

    obsid_coord_dict = {}
    ofile = house_keeping + 'coord_list'

    line  = ''
    for obsid in not_done:
        print("OBSID: " + str(obsid))

        try:
            obj = obs_dict[obsid].strip()
        except:
            continue

        try:
            coordinates = coord_dict[obj.lower()]
        except:
#
#--- if we cannot find the object in the known coordinate list, go to simbad to find it
#
            try:
                coordinates = find_coordinate_from_simbad(obj)
            except:
                coordinates = ['99:99:99.999', '99:99:99.999', 0, 0]
#
#--- add new object to coord_list
#
            coord_dict[obj.lower()] = coordinates

            line = line + obj  + '\t' 
            line = line + coordinates[0]      + '\t' + coordinates[1]      + '\t'
            line = line + str(coordinates[2]) + '\t' + str(coordinates[3]) + '\n'

        if coordinates[0] != '99:99:99.999':
#
#--- only when arcsec is accurate to 3 decimal point, use the observation
#
            if check_coord_accuracy(coordinates[0], coordinates[1]):
                obsid_coord_dict[obsid] = coordinates
#
#--- write the new coordinates found
#
    if line != '':
        with open(ofile, 'a') as fo:
            fo.write(line)
#
#--- only when we find coordinates and they are accurate enough, return the result
#
    if len(obsid_coord_dict.keys()) > 0:
        return obsid_coord_dict
    else:
        return False

#---------------------------------------------------------------------------------------
#-- create_obsid_name_dict: create obsid <---> obj name and obsid <---> instrument dictionaries
#---------------------------------------------------------------------------------------

def create_obsid_name_dict():
    """
    create obsid <---> obj name and obsid <---> instrument dictionaries
    input:  none, but read from /data/mta4/obs_ss/sot_ocat.out
    output: obsid_list  --- a list of obsids
            obs_dict    --- a dictionary obsid <---> obj name
            inst_idct   --- a dictionary obsid <---> instrument
    """
#
#--- read all avaialble observations
#
    data = mcf.read_data_file('/data/mta4/obs_ss/sot_ocat.out')
    save = []
    for ent in data:
        mc = re.search('unobserved', ent)
        if (mc is not None):
            continue
        else:
            save.append(ent)
    out  = mcf.separate_data_into_col_data(save, spliter='\^')

    obsid_list = list(numpy.array(out[1]).astype(int))
#
#--- get rid of "note" part of the object name
#
    obj_list   = []
    for ent in out[4]:
        mc = re.search(',', str(ent))
        if mc is not None:
            atemp = re.split(',', ent)
            ent   = atemp[0]
        obj_list.append(ent)

    inst_list  = out[12]
    obs_dict   = make_dict(obsid_list, obj_list)
    inst_dict  = make_dict(obsid_list, inst_list)

    return [obsid_list, obs_dict, inst_dict]

#---------------------------------------------------------------------------------------
#-- make_dict: make a dictionary from two eqal length lists                           --
#---------------------------------------------------------------------------------------

def make_dict(list1, list2):
    """
    make a dictionary from two eqal length lists
    input:  list1   --- a list
            list2   --- a list
    output: adict   --- a dictionary adict[list1[k]] = list2[k]
    """
    adict = {}
    for k in range(0, len(list1)):
        try:
            adict[int(list1[k])] = list2[k].upper()
        except:
            continue

    return adict

#---------------------------------------------------------------------------------------
#-- find_coordinate_from_simbad: find coordinates of the object from simbad site      --
#---------------------------------------------------------------------------------------

def find_coordinate_from_simbad(name):
    """
    find coordinates of the object from simbad site
    input:  name    --- object name
    output: ra      --- ra
            dec     --- dec
            pra     --- proper motion in ra direction
            pdec    --- proper motion in dec direction
    """
    cmd  = '/usr/bin/wget -O ' + zspace + ' -q '
    cmd  = cmd + ' http://simbad.u-strasbg.fr/simbad/sim-id\?'
    cmd  = cmd + 'output.format=ASCII\&Ident="' + name + '"'
    os.system(cmd)
#
#--- assume the top most entry of "Coordinates" is the most accurate entry
#
    out  = mcf.read_data_file(zspace, remove=1)
    chk  = 0
    for ent in out:
        mc1 = re.search('Coordinates', ent)
        if (chk == 0) and (mc1 is not None):
            atemp = re.split(':', ent)
            btemp = re.split('\s+', atemp[1])
            ra    = btemp[1] + ':' + btemp[2] + ':' + btemp[3]
            dec   = btemp[4] + ':' + btemp[5] + ':' + btemp[6]
            chk  += 1
            continue
        if chk == 0:
            continue
#
#--- proper mtion extact; sometime they are not there; then set them to 0, 0
#
        mc2 = re.search('Proper', ent)
        atemp = re.split(':', ent)
        btemp = re.split('\s+', atemp[1])
        try:
            pra   = float(btemp[1])
            pdec  = float(btemp[2])
        except:
            pra   = 0
            pdec  = 0

        break
#
#--- if it cannot find the coordinate, return dummy entry
#
    if chk == 0:
        return ['99:99:99.999', '99:99:99.999', 0, 0]

    else:
        return [ra, dec, pra, pdec]

#---------------------------------------------------------------------------------------
#-- make_coord_list: read coord_list and create a dictionary of obj name <---> coordindates 
#---------------------------------------------------------------------------------------

def make_coord_list():
    """
    read coord_list and create a dictionary of obj name <---> coordindates
    input:  none, but read from <house_keeping>/coord_list
    output: cidct   --- a dictionary of:
                        <obj name> <---> [ra, dec, ra prop motion, dec prop motion]
    """
    cdict = {}
    ifile = house_keeping + 'coord_list'
#
#--- sort the data before reading
#
    cmd   = 'sort ' + ifile + ' > ' + zspace
    os.system(cmd)
    cmd   = 'mv ' + zspace + ' ' + ifile
    os.system(cmd)
#
#--- now create name <--> coord dictionary
#
    data  = mcf.read_data_file(ifile)
    for ent in data:
        if ent == '\s+':
            continue
        try:
            atemp = re.split('\t+', ent)
            if atemp[0] == '':
                continue

            cdict[atemp[0].lower()] = [atemp[1], atemp[2], atemp[3], atemp[4]]
        except:
            pass

    return cdict

#---------------------------------------------------------------------------------------
#-- check_coord_accuracy: check coordinate accuracy: whether arcsec is accurate to 3 dicimal 
#---------------------------------------------------------------------------------------

def check_coord_accuracy(ra, dec):
    """
    check coordinate accuracy: whether arcsec is accurate to 3 dicimal
    input:  ra  --- ra
            dec --- dec
    output: True/False  if arcse part is accurate to 3 dicimal:True, otherwise False
    """
    try:
        atemp = re.split(':', ra)
        btemp = re.split('\.', str(atemp[-1]))
        rlen  = len(btemp[-1])
    except:
        return False

    try:
        atemp = re.split(':', dec)
        btemp = re.split('\.', str(atemp[-1]))
        dlen  = len(btemp[-1])
    except:
        return False

    if (rlen >=3) and (dlen >= 3):
        return True
    else:
        return False

#---------------------------------------------------------------------------------------
#-- run_arc5gl: run arc5gl to extract fits file                                       --
#---------------------------------------------------------------------------------------

def run_arc5gl(operation, dataset, detector, level, filetype, obsid):
    """
    run arc5gl to extract fits file
    input:  operation   --- operation, retrive/browse
            dataset     --- data set, usually flight
            level       --- level
            filetype    --- file type, eg evt1
            obsid       --- obsid
    output: fits        --- extracted fits file name
    """
    line = 'operation='       + operation + '\n'
    line = line + 'dataset='  + dataset   + '\n'
    line = line + 'detector=' + detector  + '\n'
    line = line + 'level='    + level     + '\n'
    line = line + 'filetype=' + filetype  + '\n'
    line = line + 'obsid='    + str(obsid)+ '\n'
    line = line + 'go\n'
    
    out  = mcf.run_arc5gl_process(line)
    try:
        fits = out[0]
    except:
        fits =''

    return fits

#---------------------------------------------------------------------------------------
#-- find_source_coord: find a center source coordinates                               --
#---------------------------------------------------------------------------------------

def find_source_coord(fits, inst):
    """
    find a center source coordinates
    input:  fits    --- fits file name
            inst    --- instrument name acis-i/acis-s/hrc-i/hrc-s
    output: ra      --- ra
            dec     --- dec
    """
    cmd1 = "/usr/bin/env PERL5LIB= "
#
#--- limit the area in the center potion
#
    if (inst == 'acis-s') or (inst == 'acis-i'):
        cmd2 = 'dmcopy "' + fits + '[bin x=3500:4900:1,y=3650:5100:1]"     ./ztemp_img.fits'
    elif inst == 'hrc-i':
        cmd2 = 'dmcopy "' + fits + '[bin x=16000:17000:1,y=16000:17000:1]" ./ztemp_img.fits'
    elif inst == 'hrc-s':
        cmd2 = 'dmcopy "' + fits + '[bin x=32500:33500:1,y=32500:33500:1]" ./ztemp_img.fits'
    else:
        return False

    cmd  = cmd1 + cmd2
    try:
        bash(cmd,  env=ascdsenv)
    except:
        cmd = 'rm -rf *.fits*'
        os.system(cmd)
        return False
#
#--- find the source(s)
#
    cmd2 = "wavdetect ./ztemp_img.fits  ./out.fits ./cell.fits ./t_img.fits ./bkg.fits "
    cmd2 = cmd2 + "expfile=none scale='2 4' psffile=''  clobber=yes"

    cmd  = cmd1 + cmd2
    try:
        bash(cmd,  env=ascdsenv)
    except:
        cmd = 'rm -rf *.fits*'
        os.system(cmd)
        return False

    try:
        hdata    = pyfits.open('out.fits')
        data     = hdata[1].data
        ncnt     = data['net_counts']
        ra_list  = data['ra']
        dec_list = data['dec']
        hdata.close()
    except:
        cmd = 'rm -rf *.fits*'
        os.system(cmd)
        return False
#
#--- assume that max count position is the center of the source
#
    m_pos    = ncnt.argmax(axis=0)
    ra       = ra_list[m_pos]
    dec      = dec_list[m_pos]

    cmd = 'rm -rf *.fits*'
    os.system(cmd)

    return [ra, dec]

#---------------------------------------------------------------------------------------
#-- read_header_info: read fits file header info                                      --
#---------------------------------------------------------------------------------------

def read_header_info(fits):
    """
    read fits file header info
    input:  fits    --- fits file name
    output: date    --- obs start time in seconds from 1998.1.1
            grating --- grating
            roll    --- roll angle
    """
    hdata   = pyfits.open(fits)

    date    = hdata[1].header['tstart']
    grating = hdata[1].header['GRATING']
    roll    = float(hdata[1].header['roll_nom'])

    hdata.close()

    return [date, grating, roll]

#---------------------------------------------------------------------------------------
#-- convert_ra_dec_format: convert ra dec format from hh:mm:ss to degree              --
#---------------------------------------------------------------------------------------

def convert_ra_dec_format(ra, dec):
    """
    convert ra dec format from hh:mm:ss to degree
    input:  ra  --- ra in hh:mm:ss
            dec --- dec in hh:mm:ss
    output: ra  --- ra in degree
            dec --- dec in degree
    """
    atemp = re.split(':', ra)
    ra    = 15.0 * (float(atemp[0]) + float(atemp[1])/60.0 + float(atemp[2])/3600.0)

    atemp = re.split(':', dec)
    sign  = 1
    top   = float(atemp[0])
    if top < 0:
        sign = -1
    dec   = sign * (abs(top) + float(atemp[1])/60.0 + float(atemp[2])/3600.0)

    return [ra, dec]

#---------------------------------------------------------------------------------------
#-- correct_prop_motion: correct proper motion of object                              --
#---------------------------------------------------------------------------------------

def correct_prop_motion(ra, dec, dra, ddec, otime):
    """
    correct proper motion of object
    input:  ra          --- ra
            dec         --- dec
            dra         --- ra direction proper motion
            ddec        --- dec direction proper motion
    output: [ra, dec]   --- corrected ra dec
    """
#
#--- find the time difference in fractional year
#
    tdiff = (otime - y2000) / 31536000.0        #--- 365.0 days
#
#--- correct the proper motion; check dra and ddec are in digit
#
    try:
        dra  = float(dra)
        ddec = float(ddec)

        ra   += dra  / 3600000.0 * tdiff
        dec  += ddec / 3600000.0 * tdiff
    except:
        pass

    return [ra, dec]

#---------------------------------------------------------------------------------------
#-- find_coord_diff: compute coordinate diffrence                                    ---
#---------------------------------------------------------------------------------------

def find_coord_diff(ra, dec, cra, cdec, roll):
    """
    compute coordinate diffrence
    input:  ra      --- nominal ra
            ded     --- nominal dec
            cra     --- observed ra
            cdec    --- observed dec
            roll    --- roll angle
    output: y       --- difference in y direction
            z       --- difference in z direction
    """
    ra   = float(ra)
    dec  = float(dec)
    cra  = float(cra)
    cdec = float(cdec)
    roll = float(roll)

    dra  = 3600.0 * (ra  - cra)
    ddec = 3600.0 * (dec - cdec)
#
#--- if the different is too large, something is not right; skip it
#
    if (dra > 10) or (ddec) > 10:
        return ['na', 'na']

    try:
        y    = sqrt(dra**2 + ddec**2) * math.cos(math.atan2(ddec, dra) + roll * d_rad)
        z    = sqrt(dra**2 + ddec**2) * math.sin(math.atan2(ddec, dra) + roll * d_rad)

        return [y, z]

    except:

        return ['na', 'na']

#---------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST   --
#---------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#---------------------------------------------------------------------------------------

    def test_create_obsid_name_dict(self):

        [obsid_list, obs_dict, inst_dict] = create_obsid_name_dict()

        obj = obs_dict[14277]
        self.assertEquals(obj.upper(), '31 COM')

        inst = inst_dict[14277]
        self.assertEquals(inst, 'HRC-I')


#---------------------------------------------------------------------------------------

    def test_find_coordinate_from_simbad(self):

        obj = 'MU AUR'
        coord = ['05:57:45.36142', '+29:35:08.1361', 5.0, 54.0]
        out   = find_coordinate_from_simbad(obj)
        self.assertEquals(coord, out)

#---------------------------------------------------------------------------------------
    
    def test_make_coord_list(self):

        obj = 'MU AUR'
        coord = ['05:57:45.36142', '+29:35:08.1361', 5.0, 54.0]
        odict = make_coord_list()
        out   = odict[obj.lower()]
        self.assertEquals(coord, out)

#---------------------------------------------------------------------------------------
    
    def test_check_coord_accuracy(self):

        ra  = '22:08:40.8180'
        dec = '+45:44:32.116'
        if check_coord_accuracy(ra, dec):
            print("Coord Accuracy Passed")
        else:
            print("Coord Accuracy Failed")

#---------------------------------------------------------------------------------------

    def test_run_arc5gl(self):

        obsid = 20794
        detector = 'acis'

        run_arc5gl('retrieve', 'flight', detector, '1', 'evt1', obsid)

#---------------------------------------------------------------------------------------

    def test_read_header_info(self):

        expected = [622191546.16386, 'NONE', 214.15673255764]
        fits = house_keeping + '/Test_input/acisf20794_000N001_evt1.fits.gz'

        out  = read_header_info(fits)

        self.assertEquals(out, expected)

#---------------------------------------------------------------------------------------

    def test_find_source_coord(self):

        fits = house_keeping + '/Test_input/acisf20794_000N001_evt1.fits.gz'
        inst = 'acis-s'
        out  = find_source_coord(fits, inst)

        print("I AM HERE SOURCE: " + str(out))

#---------------------------------------------------------------------------------------

    def test_convert_ra_dec_format(self):

        ra   = '12:51:41.9216'
        dec  = '+27:32:26.565'
        [cra, cdec] = convert_ra_dec_format(ra, dec)

        print("Coord change: " + str(cra) + '<-->' + str(cdec))

#---------------------------------------------------------------------------------------

    def test_correct_prop_motion(self):

        expected = ['299.59030', '35.20157']
        otime = 622191546.16386
    
        [ra, dec, dra, ddec] = ['19:58:21.6756', '+35:12:05.775', -3.82, -7.62]
        [ra, dec]            = convert_ra_dec_format(ra, dec)
        [ra, dec]            = correct_prop_motion(ra, dec, dra, ddec, otime)

        out = '%.5f' % round(ra, 5)
        self.assertEquals(expected[0], out)

        out = '%.5f' % round(dec, 5)
        self.assertEquals(expected[1], out)

#---------------------------------------------------------------------------------------

    def test_find_coord_diff(self):
    
        expected    = ['-0.24889', '0.75582']

        [ra, dec]   = ['13:25:27.6152',   '-43:01:08.805']
        [ra, dec]   = convert_ra_dec_format(ra, dec)
        [dra, ddec] = [0, 0]
        otime       = 622191546.16386
        roll        = 214.15673255764
        [ra, dec]   = correct_prop_motion(ra, dec, dra, ddec, otime)

        [cra, cdec] = [201.3651239994764, -43.018899948742813]

        [dx, dy]    = find_coord_diff(ra, dec, cra, cdec, roll)

        out = '%.5f' % dx
        self.assertEquals(expected[0], out)

        out = '%.5f' % dy
        self.assertEquals(expected[1], out)

#---------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_pointing_data()
    #unittest.main()

