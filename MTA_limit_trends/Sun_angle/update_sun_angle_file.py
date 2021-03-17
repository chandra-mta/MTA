#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#           update_sun_angle_file.py: update sun_angle.fits file                #
#                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                               #
#           last update: Feb 02, 2021                                           #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.Sun
import Ska.astro
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

cols = ['time', 'sun_angle']

fits_file = data_dir +  'sun_angle.fits' 

#-----------------------------------------------------------------------------------
#-- run_sun_angle_update: update sun_angle.fits file                              --
#-----------------------------------------------------------------------------------

def run_sun_angle_update():
    """
    update sun_angle.fits file
    input:  none but read <data_dir>/sun_angle.fits
    output: updated <data_dir>/sun_angle.fits
    """
#
#--- check whether the data file exists
#
    if os.path.isfile(fits_file):
#
#--- find the last entry date
#
        f = pyfits.open(fits_file)
        data  = f[1].data
        f.close()
        begin = data['time'][-1]

    else:
        begin = Chandra.Time.DateTime('1999:202:00:00:00').secs

    update_sun_angle_file(begin)

#-----------------------------------------------------------------------------------
#-- update_sun_angle_file: update sun_angle.fits from begining to yesterday's date -
#-----------------------------------------------------------------------------------

def update_sun_angle_file(begin):
        """
        update sun_angle.fits from begining to yesterday's date
        input:  begin   --- starting time in seconds from 1998.1.1
        output: updated <data_dir>/sun_angle.fits
        """
#
#--- find the yesterday's date in seconds from 1998.1.1
#
        stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
        stday = Chandra.Time.DateTime(stday).secs - 86400.0     #--- set the ending to the day before
#
#--- fill up the data till yesterday
#
        if stday > begin:
            end = begin + 86400.0
            while stday > begin:

                u = Chandra.Time.DateTime(begin)
                print(u.date)

                try:
                    cdata = find_pitch_angle(begin, end)
                    ecf.update_fits_file(fits_file, cols, cdata)
                except:
                    pass

                begin = end
                end   = begin + 86400.0
                if begin >= stday:
                    break

#-----------------------------------------------------------------------------------
#-- find_pitch_angle: create a table of time and sun pitch angle                  --
#-----------------------------------------------------------------------------------

def find_pitch_angle(start, stop):
    """
    create a table of time and sun pitch angle
    input:  start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
    output: time    --- a list of time in seconds from 1998.1.1
            pitch   --- a list of ptich in degree
    """
#
#--- extract pcad aspsol fits files for the given time period
#
    line = 'operation=retrieve\n'
    line = line + 'dataset = flight\n'
    line = line + 'detector = pcad\n'
    line = line + 'subdetector = aca\n'
    line = line + 'level = 1\n'
    line = line + 'filetype =aspsol\n'
    line = line + 'tstart = '   + str(start) + '\n'
    line = line + 'tstop = '    + str(stop)  + '\n'
    line = line + 'go\n'
    data_list = mcf.run_arc5gl_process(line)
    [cols, tbdata] = ecf.read_fits_file(data_list[0])

    for ent in data_list:
        cmd = 'rm -rf ' + ent
        os.system(cmd)

    time       = tbdata['time']
    ra         = tbdata['ra']
    dec        = tbdata['dec']

    time_list  = []
    pitch_list = []
    prev       = 0.0
    m          = 0
    for k in range(0, len(time)):
#
#--- select one data every 5 mins
#
        itime = int(time[k])
        if itime == prev:
            continue

        if m % 300 == 0:
#
#--- get the sun angle
#
            pitch = find_chandra_pitch(time[k], ra[k], dec[k])
            time_list.append(itime)
            pitch_list.append(pitch)

        prev  = itime
        m += 1

    time  = numpy.array(time_list)
    pitch = numpy.array(pitch_list)

    return [time, pitch]

#-----------------------------------------------------------------------------------
#-- find_chandra_pitch: compute the sun angle                                     --
#-----------------------------------------------------------------------------------

def find_chandra_pitch(time, ra, dec):
    """
    compute the sun angle
    input:  time    --- time in seconds from 1998.1.1
            ra      --- ra of Chandra pointing direction
            dec     --- dec of Chandra pointing direction
    output: pitch   --- sun angle in degree
    """
    [sun_ra, sun_dec] =  Ska.Sun.position(time)
    pitch = Ska.astro.sph_dist(ra, dec, sun_ra, sun_dec)

    return pitch

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) == 3:
        tstart = float(sys.argv[1])
        tstop  = float(sys.argv[2])
        cdata  = find_pitch_angle(tstart, tstop)    
        update_fits_file('./temp_sun_angle.fits', cols, cdata)

    else:
        run_sun_angle_update()

