#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#       convert_ephem_data.py: convert a binary data into ascii data        #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: Mar 08, 2021                                       #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import random
import math
import numpy
import time
import datetime
import julian
import Chandra.Time
import struct
path = '/data/mta/Script/Ephem/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" % (var, line))
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
jd1998  = 2450815.0         #---- 1998.1.1 in julian date
r2d     = 180.0/math.pi     #---- radian to degree 
mfactor = 1e7               #---- factor to convert the data size
mfactor2= 1e7/864.0         #---- factor to convert the data size

#----------------------------------------------------------------------
#-- convert_ephem_data: convert a binary data into ascii data        --
#----------------------------------------------------------------------

def convert_ephem_data(ifile):
    """
    convert a binary data into ascii data 
    input:  ifile   --- a data file name which contains binary data
    output: ofile   --- a data file name which contains ascii data
            example: DE19147.EPH --->  DE19147.EPH.dat0
    """
#
#--- input file 
#
    dfile = eph_dir + ifile
#
#--- check whether the data is multiple of 2800 bytes. There should be, at least, 2 blocks 
#
    nbytes = find_data_size(dfile)
    ncnt   = int(nbytes / 2800)
    if nbytes != ncnt * 2800:
        print('Warning!! Not an integral number of 2800-byte records in file: ' + str(ifile))
    if ncnt  < 2:
        print('Warning!! Too few 2800-byte records in file: ' + str(ifile))
#
#--- read out ephemeris data
#
    r1  = read_ephemeris(dfile, 0)
    r2  = read_ephemeris(dfile, 1)
    s   = read_ephemeris(dfile, 2)
#
#---- print out ephemris general information on screen
#
    report_about_data(r1)
#
#---- accumulate ephem data; there could be more than one saved; each block is 4800 bytes
#---- and there are 10 data entries
#
    s_list = [s]
    for k in range(3, ncnt):
        r = read_ephemeris(dfile, k)
        if len(r.keys()) == 11:
            s_list.append(r)
        elif k < ncnt-1:
            print('Warning!! Non-Type-2 record found in wrong place in file: ' + dfile)
#
    valid_data = 1
    line       = ''
    for k in range(0, len(s_list)):
#
#--- read starting time
#
        syear  = int(float(s_list[k]['date_first_point']) / 10000)
        syear  = mcf.add_leading_zero(syear)
        year   = time.strftime('%Y', time.strptime(syear, '%y'))
        doy    = s_list[k]['days_in_year_first_point']
        sec    = s_list[k]['sec_in_day_first_point']
        step   = s_list[k]['step_time']
#
#---- create lists of times (year, month, date, hour, min, and sec)
#
        [y_list, m_list, d_list, hr_list, mm_list, ss_list, c_time]\
                        = convert_time_format_in_array(year, doy, sec, step)
    
        p_vector = s_list[k]['first_pos_vector']
        v_vector = s_list[k]['first_vel_vector']
        p_v_data = s_list[k]['pos_vel_data_2_50']
#
#--- create lists for positional and velocity from the initial postion and velocity
#
        px = [p_vector[0] * mfactor]
        py = [p_vector[1] * mfactor]
        pz = [p_vector[2] * mfactor]
        vx = [v_vector[0] * mfactor]
        vy = [v_vector[1] * mfactor]
        vz = [v_vector[2] * mfactor]
#        vx = [v_vector[0] * mfactor2]
#        vy = [v_vector[1] * mfactor2]
#        vz = [v_vector[2] * mfactor2]
#
#---- append the rest of the data
#
        for m in range(0, len(p_v_data)):
            px.append(p_v_data[m][0] * mfactor)
            py.append(p_v_data[m][1] * mfactor)
            pz.append(p_v_data[m][2] * mfactor)
            vx.append(p_v_data[m][3] * mfactor)
            vy.append(p_v_data[m][4] * mfactor)
            vz.append(p_v_data[m][5] * mfactor)
#
#--- create each data line with the valid data
#
        for m in range(0, len(px)):
            if (px[m] < 1.0e22) and (valid_data > 0):
                line = line + '%16.3f' % c_time[m]
                line = line + '%16.3f' % px[m]
                line = line + '%16.3f' % py[m]
                line = line + '%16.3f' % pz[m]
                line = line + '%16.3f' % vx[m]
                line = line + '%16.3f' % vy[m]
                line = line + '%16.3f' % vz[m]
                line = line + '%12.6f' % y_list[m]
                line = line + '%4d'    % m_list[m]
                line = line + '%4d'    % d_list[m]
                line = line + '%4d'    % hr_list[m]
                line = line + '%4d'    % mm_list[m]
                line = line + '%4d'    % ss_list[m]
                line = line + '\n'
            else:
                valid_data = 0
                break
#
#--- write out the data in the output file (something like: DE16046.EPH.dat0)
#
    ofile = dfile + '.dat0'
    with open(ofile, 'w') as fo:
        fo.write(line)

#----------------------------------------------------------------------
#-- find_data_size: find data size in bytes                          --
#----------------------------------------------------------------------

def find_data_size(dfile):
    """
    find data size in bytes
    input:  dfile   --- data file name
    output: nbytes  --- a file data size in bytes
    """
    cmd = 'wc -c ' + dfile + '> ' + zspace
    os.system(cmd)

    with open(zspace, 'r') as f:
        out = f.read()
    mcf.rm_files(zspace)

    atemp = re.split('\s+', out)
    
    nbytes = int(float(atemp[0]))

    return nbytes

#----------------------------------------------------------------------
#-- convert_time_format_in_array: create nlen length of lists of time from given data
#----------------------------------------------------------------------

def convert_time_format_in_array(year, doy, sec, step, nlen=50):
    """
    create nlen length of lists of time from given data
    input:  year    --- starting year
            doy     --- starting day of year
            sec     --- starting time in seconds
            step    --- step size of the time interval
            nlen    --- the numbers of element to be created
    output: y_list  --- a list of fractoinal year
            m_list  --- a list of month
            d_list  --- a list of day
            hr_list --- a list of hour
            mm_list --- a list of minutes
            ss_list --- a list of seconds
            stime   --- a list of chandra time
    """
#
#--- find starting time in Chandra Time
#--- NOTE: there are about 96 sec difference between chandra time computated by
#--- the original IDL version and that computed by Chandra.Time library. 
#--- I decided to stick to the original version to keep the same time sequences
#
#    line   = str(year) + ':' + str(doy) + ':00:00:00' 
#    s1998  = Chandra.Time.DateTime(line).secs + sec
    jd     = convert_to_julian_date(year, 1, 1)
    s1998  = (jd - jd1998 + doy -1) * 86400.0 + sec
#
#--- create an array with <nlen> elements with <step> second interval
#
    tarray  = (numpy.array(list(range(0,nlen))) * step) + s1998
#
#--- create lists of year, month, day, hour, min, and seconds
#
    y_list  = []
    m_list  = []
    d_list  = []
    hr_list = []
    mm_list = []
    ss_list = []
    for k in range(0, len(tarray)):
        out = Chandra.Time.DateTime(tarray[k]).fits
        atemp = re.split('T', out)
        btemp = re.split('-', atemp[0])
        ctemp = re.split(':', atemp[1])
        year  = int(float(btemp[0]))
        month = int(float(btemp[1]))
        day   = int(float(btemp[2]))
        hour  = int(float(ctemp[0]))
        mins  = int(float(ctemp[1]))
        secs  = int(float(ctemp[2]))
        fyear = convert_to_fyear(year, month, day, hour, mins, secs)
        y_list.append(fyear)
        m_list.append(month)
        d_list.append(day)
        hr_list.append(hour)
        mm_list.append(mins)
        ss_list.append(secs)

    return [y_list, m_list, d_list, hr_list, mm_list, ss_list, list(tarray)]

#----------------------------------------------------------------------
#-- convert_to_julian_date: convert calender date to julian date    ---
#----------------------------------------------------------------------

def convert_to_julian_date(year, mon, day):
    """
    convert calender date to julian date
    input:  year    --- year
            mon     --- month
            day     --- day
    output: jd      --- julian date
    """
    line = str(year) + ':' + str(mcf.add_leading_zero(mon)) 
    line = line + ':' + str(mcf.add_leading_zero(day))
    dt   = datetime.datetime.strptime(line, '%Y:%m:%d')
    jd = julian.to_jd(dt + datetime.timedelta(hours=12), fmt='jd')

    return jd

#----------------------------------------------------------------------
#-- convert_to_fyear: convert calendar date to a fractional year     --
#----------------------------------------------------------------------

def convert_to_fyear(year, mon, day, hh, mm, ss):
    """
    convert calendar date to a fractional year
    input:  year    --- year
            mon     --- month
            day     --- day
            hh      --- hour
            mm      --- minute
            ss      --- second
    output: fyear   --- time in fractional year
    """
    if mcf.is_leapyear(year):
        base = 366.0
    else:
        base = 365.0

    line  = str(year) + ':' + str(mon) + ':' + str(day)
    out   = time.strftime('%Y:%j', time.strptime(line, '%Y:%m:%d'))
    atemp = re.split(':', out)
    year  = float(atemp[0])
    yday  = float(atemp[1])

    fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base

    return fyear

#----------------------------------------------------------------------
#-- report_about_data: reporting the general ephemeris information    -
#----------------------------------------------------------------------

def report_about_data(r1):
    """
    reporting the general ephemeris information 
    input:  r1  --- the dictionary of ephemeris information
    output: screen print out of the information
    """
    line = ''
    dval = str(r1['start_date'])
    mc   = re.search('\.', dval)
    if mc is not None:
        atemp = re.split('\.', dval)
        dval  = atemp[0]

    out  = mcf.convert_date_format(dval, ifmt='%y%m%d', ofmt= '%Y:%m:%d')
    [year, mon, day] = re.split(':', out)
    line = line + 'Date of first ephemeris point (Year, Month, Day): ' 
    line = line + year + ' ' + mon + ' ' + day + '\n'
#
#--- convert date format:e.g., 190505.0 --> 20190505.0
#
    if r1['start_date'] < 500000:
        r1['start_date'] += 20000000
    else:
        r1['start_date'] += 19000000

    if r1['stop_date'] < 500000:
        r1['stop_date'] += 20000000
    else:
        r1['stop_date'] += 19000000

    if r1['epoch_year'] < 50:
        r1['epoch_year'] += 2000
    else:
        r1['epoch_year'] += 1900
    line = line + "Start/Stop/Epoc Date: " + str(r1['start_date']) + ' : ' + str(r1['stop_date']) 
    line = line + ' : ' + str(r1['epoch_year']) + '\n'

    line = line + '\nChandra Keplerian Elements: \n'
    line = line + 'Elements Epoch: \n'
    line = line + '    (YYYY MM DD hh mm ss.sss):' + str(int(r1['epoch_year'])) + ', ' 
    line = line + str(int(r1['epoch_month'])) + ', ' + str(int(r1['epoch_day'])) + ', ' 
    line = line + str(int(r1['epoch_hour']))  + ', ' + str(int(r1['epoch_min'])) + ', ' 
    line = line + str(int(r1['epoch_millisec'] / 1000.0)) + '.' 
    line = line + str(int(r1['epoch_millisec'] % 1000))
    line = line + '\n'
    line = line + '    (Seconds since start of 1985): %16.3f\n' % r1['epoch_time']
    line = line + '\n\n'
    line = line + ' Semi-major axis (km):            ' + str(r1['smajor_axis'])      + '\n'
    line = line + ' Eccentricity:                    ' + str(r1['eccent'])           + '\n'
    line = line + ' Inclination (deg):               ' + str(r1['inclin'] * r2d)     + '\n'
    line = line + ' Argument of Perigee (deg):       ' + str(r1['perigee'] * r2d)    + '\n'
    line = line + ' RA of Ascending Node (deg):      ' + str(r1['raan'] * r2d)       + '\n'
    line = line + ' Mean Anomaly (deg):              ' + str(r1['mean_anom'] * r2d)  + '\n'
    line = line + ' True Anomaly (deg):              ' + str(r1['true_anom'] * r2d)  + '\n'
    line = line + ' Arg of Perigee + True Anom (deg):' + str(r1['sum_aprgta'] * r2d) + '\n'
    line = line + ' (approx.) Period (hours):        ' + str(24 * r1['period']/100)  + '\n'
    line = line + ' (approx.) Mean Motion (deg/hour):' 
    line = line + str(r1['mean_motn'] * r2d * 100/ 24) + '\n'
    line = line + ' (wrong) Rate of change of RA of AN (deg/day):'
    line = line + str(r1['rate_ascnd'] * r2d * 100.0) + '\n'

    print(line)

#----------------------------------------------------------------------
#-- read_ephemeris: read ephemeris file                              --
#----------------------------------------------------------------------

def read_ephemeris(ifile, rec):
    """
    read ephemeris file
    input:  ifile   --- input file name
            rec     --- record type
    output: ephem   --- a dictionary of data
    """
    ephem = {}
    with open(ifile, 'rb') as f:
        if rec == 0:
            ephem['record_type']       = 1
            ephem['tape_id']           = get_double(f, 0)
            ephem['satellite_id']      = get_double(f, 8)
            ephem['utc_flag']          = get_double(f, 16)
            ephem['start_date']        = get_double(f, 24)
            ephem['start_day_count']   = get_double(f, 32)
            ephem['start_sec_count']   = get_double(f, 40)
            ephem['stop_date']         = get_double(f, 48)
            ephem['stop_day_count']    = get_double(f, 56)
            ephem['stop_sec_count']    = get_double(f, 64)
            ephem['step_size']         = get_double(f, 72)
            ephem['rec1_spare1']       = get_bytes(f, 80, 136)
            ephem['ref_date']          = get_double(f, 216)
            ephem['coord_type']        = get_long(f, 224)
            ephem['rec1_spare2']       = get_bytes(f, 228, 132)
            ephem['epoch_time']        = get_double(f, 360)
            ephem['epoch_year']        = get_double(f, 368)
            ephem['epoch_month']       = get_double(f, 376)
            ephem['epoch_day']         = get_double(f, 384)
            ephem['epoch_hour']        = get_double(f, 392)
            ephem['epoch_min']         = get_double(f, 400)
            ephem['epoch_millisec']    = get_double(f, 408)
            ephem['smajor_axis']       = get_double(f, 416)
            ephem['eccent']            = get_double(f, 424)
            ephem['inclin']            = get_double(f, 432)
            ephem['perigee']           = get_double(f, 440)
            ephem['raan']              = get_double(f, 448)
            ephem['mean_anom']         = get_double(f, 456)
            ephem['true_anom']         = get_double(f, 464)
            ephem['sum_aprgta']        = get_double(f, 472)
            ephem['rec1_spare6']       = get_bytes(f, 480, 16)
            ephem['period']            = get_double(f, 496)
            ephem['rec1_spare7']       = get_bytes(f, 504, 16)
            ephem['mean_motn']         = get_double(f, 520)
            ephem['rec1_spare8']       = get_bytes(f, 528, 8)
            ephem['rate_ascnd']        = get_double(f, 536)
            ephem['pos_vector']        = get_multi_double(f, 544,3)
            ephem['vel_vector']        = get_multi_double(f, 568,3)
            ephem['rec1_spare3']       = get_bytes(f, 592, 456)
            ephem['solar_pos']         = get_multi_double(f, 1048, 3)
            ephem['rec1_spare4']       = get_bytes(f, 1072, 520)
            ephem['grhour_angle']      = get_double(f, 1592)
            ephem['rec1_spare5']       = get_bytes(f, 1600, 1200)

        elif rec == 1:
            b_add = 2800
            ephem['record_type' ]      = 2
            ephem['rec2_spare1']       = get_bytes(f, b_add, 2800)

        else:
            chk = sentinels(f)
            b_add = 2800 * rec
            if chk != 0.0:
                ephem['record_type']               = 3
                ephem['date_first_point']          = get_double(f, b_add)
                ephem['junk1']                     = get_long(f, b_add + 8)
                ephem['days_in_year_first_point']  = get_long(f, b_add + 12)
                ephem['junk2']                     = get_long(f, b_add + 16)
                ephem['sec_in_day_first_point']    = get_long(f, b_add + 20)
                ephem['step_time']                 = get_double(f, b_add + 24)
                ephem['first_pos_vector']          = get_multi_double(f, b_add + 32, 3)
                ephem['first_vel_vector']          = get_multi_double(f, b_add + 56, 3)
                ephem['pos_vel_data_2_50']         = get_multi_dim_double(f, b_add + 80, 6, 49)
                ephem['rec3_spare1']               = get_bytes(f, b_add + 2432, 368)

            else:
                ephem['record_type']   = 4
                ephem['sentinel']      = chk
                ephem['rec4_spare1']   = get_bytes(f, 80, 2720)

    return ephem

#----------------------------------------------------------------------
#-- get_double: convert bytes data into a double                     --
#----------------------------------------------------------------------

def get_double(f, pos):
    """
    convert bytes data into a double 
    input:  f       --- a data pointer
            pos     --- starting position of the byte data
    output: dout    --- a double precison float
    """
    f.seek(pos, 0)
    out  = f.read(8)
    dout = struct.unpack('>d',out)[0]

    return dout

#----------------------------------------------------------------------
#-- get_multi_double: convert bytes data into a vector of  double    --
#----------------------------------------------------------------------

def get_multi_double(f, pos, cnt):
    """
    convert bytes data into a vector of  double 
    input:  f       --- a data pointer
            pos     --- starting position of the byte data
            cnt     --- numbers of values to read
    output: save    --- a vector of double precision data
    """

    save  = []
    start = pos
    for k in range(0, cnt):
        save.append(get_double(f, start))
        start += 8

    return save

#----------------------------------------------------------------------
#-- get_multi_dim_double: convert bytes data into a two dimentinal array of  double
#----------------------------------------------------------------------

def get_multi_dim_double(f, pos, cnt, dim):
    """
    convert bytes data into a two dimentinal array of  double 
    input:  f       --- a data pointer
            pos     --- starting position of the byte data
            cnt     --- numbers of values to read
            dim     --- the second dimension of the array
    output: save    --- two dimensional array of double precision data
    """
    save = []
    start =pos 
    for k in range(0, dim):
        save.append(get_multi_double(f, start, cnt))
        start += 8 * cnt

    return save

#----------------------------------------------------------------------
#-- get_long: convert bytes data into a long                         --
#----------------------------------------------------------------------

def get_long(f, pos):
    """
    convert bytes data into a long
    input:  f   --- a data pointer
            pos --- starting position of the byte data
    output: lout    --- long interger
    """
    f.seek(pos, 0)
    out  = f.read(4)
    lout = struct.unpack('>l', out)[0]

    return lout

#----------------------------------------------------------------------
#-- get_bytes: get byte values                                       --
#----------------------------------------------------------------------

def get_bytes(f, pos, cnt):
    """
    get byte values
    input:  f   --- a data pointer
            pos --- starting position of the byte data
            cnt --- numbers of values to read
    output: out --- data read
    """
    f.seek(pos, 0)
    out = f.read(cnt)

    return out

#----------------------------------------------------------------------
#-- sentinels: data checking mechanism                               --
#----------------------------------------------------------------------

def sentinels(f):
    """
    data checking mechanism
    input:  f       --- data poiter
    output: total   --- value computed
    """
    start = 0
    save  = []
    for k in range(0, 10):
        f.seek(start, 0)
        out = f.read(8)
        out2 =  struct.unpack('>d',out)
        save.append(out2[0])
        start += 8

    scomp = [1.e16] * 10
    scomp = numpy.array(scomp)
    sout  = numpy.array(out2) - scomp
    total = sum(sout)

    return total

#----------------------------------------------------------------------

if __name__ == "__main__":

    ifile = sys.argv[1]
    convert_ephem_data(ifile)
