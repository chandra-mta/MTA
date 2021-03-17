#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#   extract_bad_pix.py: find ACIS bad pixels and bad columns and records daily variations   #
#                                                                                           #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                           #
#       last update Mar 02, 2021                                                            #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import astropy.io.fits as pyfits
import Chandra.Time
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'
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
import mta_common_functions    as mcf        #---- contains other functions commonly used in MTA scripts
import bad_pix_common_function as bcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)
#
#--- setting limits: factors for how much std out from the mean
#
factor     = 5.0        #--- warm pixel 
col_factor = 3.0        #--- warm column 
hot_factor = 1000.0     #--- hot pixel
#
#-- day limits
#
day30      = 2592000.0  #---- (in sec)
day14      = 1209600.0
day7       =  604800.0

#------------------------------------------------------------------------------------------
#--- find_bad_pix_main: contorl function to extract bad pixels and bad columns          ---
#------------------------------------------------------------------------------------------

def find_bad_pix_main(tstart, tstop):
    """
    contorl function to extract bad pixels and bad columns
    input:  tstart  --- interval starting time in seconds from 1998.1.1
            tstop   --- interval stopping time in seconds from 1998.1.1
    output: updated bad pixel and bad column list files
    """
    if tstart == '':
        [tstart, tstop]  = find_data_collection_interval()

    kcnt = int((tstop - tstart) / 86400.0)
    if kcnt < 1:
        kcnt = 1

    for k in range(0, kcnt):
        ctime = tstart + 86400 * k 
        get_bad_pix_data(ctime)
#
#--- move old data to archive
#
        mv_old_file(ctime)

#------------------------------------------------------------------------------------------
#-- get_bad_pix_data: extract bad pixel data of 24 hr period                             --
#------------------------------------------------------------------------------------------

def get_bad_pix_data(ctime):
    """
    extract bad pixel data of 24 hr period
    input:  ctime   --- starting time in seconds from 1998.1.1
    output: updated bad pixel and bad column list files
    """
#
#---check whether "Working_dir" exists
#
    if os.path.isdir('./Working_dir'):
        mcf.rm_files('./Working_dir/*')
    else:
        cmd = 'mkdir ./Working_dir'
        os.system(cmd)
#
#--- date collection period is 24 hrs from ctime
#
    stop      = ctime + 86400
    data_list = get_data_out(ctime, stop)
#
#--- create data lists in ./Working_dir/new_data_ccd<ccd>
#
    nccd_list = int_file_for_day(data_list)
#
#--- check today's bad cols and pixs
#
    stime = setup_to_extract(nccd_list)
#
#--- if there is no data, stime <= 0 
#
    if stime  <= 0:
        print("No data in the period")
        return 

    for ccd in range(0, 10):
        warm_data_list = []
        hot_data_list  = []
#
#--- bad pix selected at each quad; so go though all of them and combine them
#
        for quad in range(0, 4):

            (warm_data, hot_data) = select_bad_pix(ccd, quad)

            if quad == 0:
                warm_data_list = warm_data
                hot_data_list  =  hot_data
            else:
                warm_data_list = combine_ccd(warm_data_list, warm_data, quad)
                hot_data_list  = combine_ccd(hot_data_list,  hot_data,  quad)

        if len(warm_data_list) > 1:
            warm_data_list = mcf.remove_duplicated_lines(warm_data_list,  chk = 0)
        
        if len(hot_data_list)  > 1:
            hot_data_list =  mcf.remove_duplicated_lines(hot_data_list,   chk = 0)
#
#---- print out newly found warm and hot pixels
#
        print_bad_pix_data(ccd, warm_data_list, 'warm', today_time = stime)
        print_bad_pix_data(ccd, hot_data_list,  'hot',  today_time = stime)

        bad_col_list = chk_bad_col(ccd)
        print_bad_col(ccd, bad_col_list, stime)
#
#--- clean up the Exc area
#
    mcf.rm_files('./Working_dir')

#------------------------------------------------------------------------------------------
#--- combine_ccd: combine bad pixel positions from a different quad to one CCD coordinate system 
#------------------------------------------------------------------------------------------

def combine_ccd(base, new, quad):
    """
    combine bad pixel positions from a different quad to one CCD coordinate system
    input:  base -- bad pixel positions already recorded in a CCD coordinates
                    data format: <ccd>:<quad>:<year>:<ydate>:<x>:<y>
            new  -- new bad pixel position listed in quad coordinated
            quad -- quad # 0 - 3
    output: base -- updated list of bad pixels in CCD coordinates
    """

    for ent in new:
        atemp = re.split(':', ent)
        ccd   = atemp[0]
        mtime = atemp[2] + ':' + atemp[3]
        x     = str(int(atemp[4]) + 256  * int(quad))
        y     = atemp[5]
        line  = ccd + ':' + str(quad) + ':' + mtime + ':' + x + ':' + y
        base.append(line)

    return base

#-------------------------------------------------------------------------------------------
#--- int_file_for_day: separate each data into appropriate ccd data list                 ---
#-------------------------------------------------------------------------------------------

def int_file_for_day(data_list):
    """
    separate each data into appropriate ccd data list
    input:  data_list --- a list of bias.fits files
    output: <data_dir>/data_used.<ccd> 
                    --- a record of which data used for the analysis
            ./Working_dir/new_data_ccd.<ccd>      
                    --- a list of the data which will be used for today's analysis
    """
#
#--- check each data and select out appropriate data
#
    a_list = []
    for k in range(0, 10):
        a_list.append([])

    for ent in data_list:
        stime      = bcf.extractTimePart(ent)
        if stime > 0:
            head = 'acis' + str(int(stime))
#
#--- extract information of the ccd
#
            [ccd, readmode, date_obs, overclock_a, overclock_b, overclock_c, overclock_d]  = extractCCDInfo(ent)
#
#--- only TIMED data will be used
#
            m = re.search('TIMED', readmode)
            if m is not None:
#
#--- keep the record of which data we used
#
                ccd   = int(float(ccd))
                ntemp = re.split('acisf', ent)

                out   = mcf.convert_date_format(date_obs, ifmt="%Y-%m-%dT%H:%M:%S", ofmt='%Y:%j')
                line  = out + ':acisf' + ntemp[1] + '\n'

                out1  = data_dir + '/data_used.' + str(ccd)
                out2  = './Working_dir/new_data_ccd.'     + str(ccd)
                with open(out1, 'a') as f:
                    f.write(line)
#
#--- a list of data to be analyzed kept in ./Working_dir
#
                a_list[ccd].append(ent)

                with open(out2, 'a') as f:
                    f.write(ent + '\n')
    return a_list
    
#-------------------------------------------------------------------------------------------
#--- setup_to_extract: prepare to extract data                                            --
#-------------------------------------------------------------------------------------------

def setup_to_extract(ccd_list):
    """
    prepare to extract data
    input:  ccd_list    --- a list of lists of ccd data
    output: stime       --- time in Chandra Time of the observation 
                            (today, unless the original data are given)
            output from a function "extract" written in ./Working_dir
    """
    stime = -999
    for ccd in range(0, 10):
#
#--- only when data exists, procced
#
        if len(ccd_list[ccd]) == 0:
            continue

        ifile  = ccd_list[ccd][0]
        stime = bcf.extractTimePart(ifile)

        if stime > 0:
            out      = mcf.convert_date_format(stime, ofmt='%Y:%j')
            atemp    = re.split(':', out)
            date_obs = str(atemp[0]) + ':' + str(int(float(atemp[1])))
            head     = 'acis' + str(int(stime))
#
#--- comb.fits is an img fits file combined all image fits files extracted
#
            wfile = './Working_dir/comb.fits'
            mcf.rm_files(wfile) 

            cmd   = 'cp ' + ifile +  ' ' + wfile
            os.system(cmd)

            f     = pyfits.open(wfile)
            sdata = f[0].data
            hdr   = f[0].header

            sdata[sdata <    0] = 0
            sdata[sdata > 4000] = 0
            pyfits.update(wfile, sdata, hdr)
            f.close()
#
#--- if there are more than one file, merge all fits into one
#
            if len(ccd_list[ccd]) > 1:
                for j in range(1, len(ccd_list[ccd])): 

                    f     = pyfits.open(ccd_list[ccd][j])
                    tdata = f[0].data
                    tdata[tdata <    0] = 0
                    tdata[tdata > 4000] = 0
                    f.close()

                    sdata = sdata + tdata

                pyfits.update(wfile, sdata, hdr)
#
#--- get time stamp of the last file
#
            ifile = ccd_list[ccd][len(ccd_list[ccd]) -1]
            stime = bcf.extractTimePart(ifile)
#
#--- extract(date_obs, ccd_dir, <fits header>, <input file>, <which quad>, 
#---         <column position>, <x start>, <x end>)
#
            ccd_dir = house_keeping + '/Defect/CCD' + str(ccd)

            extract(ccd, date_obs, ccd_dir, head, wfile,  0,   0,   0,  255)
            extract(ccd, date_obs, ccd_dir, head, wfile,  1, 256, 256,  511)
            extract(ccd, date_obs, ccd_dir, head, wfile,  2, 512, 512,  767)
            extract(ccd, date_obs, ccd_dir, head, wfile,  3, 768, 768, 1023)

    return (stime)

#-------------------------------------------------------------------------------------------
#-- extract: find bad pix and bad column for the data given                              ---
#-------------------------------------------------------------------------------------------

def extract(ccd, date_obs, ccd_dir, head, infile, quad, cstart, rstart, rend):
    """
    find bad pix and bad column for the data given
    input:  ccd      --- ccd #
            date_obs --- observation date
            ccd_dir  --- the location of ccd<ccd #> data kpet
            head     --- header for the file
            infile   --- the data fits file location
            quad     --- quad # (0 - 3)
            cstart   --- column postion
            rstart   --- column starting postion
            rend     --- column ending position
    output:  output from find_bad_col (warm/hot column locations)
             output from find_bad_pix_candidate (warm/hot pixel positions)
    """
#
#--- create data files; it could be empty at the end, but it will be used for bookkeeping 
#
    max_file     = head + '_q' + str(quad) + '_max'
    hot_max_file = head + '_q' + str(quad) + '_hot'
#
#--- extract the region we need 
#
    f      = pyfits.open(infile)
    sdata  = f[0].data
    varray = sdata[0:1023,int(rstart):int(rend)]
    f.close()
#
#---- find bad columns
#
    wout_dir = './Working_dir/today_bad_col_' + str(ccd)
    mcf.rm_files(wout_dir)

    find_bad_col(varray, ccd, cstart, ccd_dir, head)
#
#--- find today's warm and hot pixel candidates
#
    find_bad_pix_candidate(varray, ccd, quad, date_obs, ccd_dir, max_file, hot_max_file)

#---------------------------------------------------------------------------------------------------
#--- mv_old_data: move the older data to the achive directory                                    ---
#---------------------------------------------------------------------------------------------------

def mv_old_data(ccd):
#
#--- find when is the 7 days ago in second from 1998.1.1
#
    out      = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    today    = Chandra.Time.DateTime(out).secs
#    cut_date = today - day7
    cut_date = today - day30
#
#--- get the list in the directory
#
    dfile = house_keeping + 'Defect/CCD' + str(ccd) + '/'
#
#--- check whether the directory is empty
#
    if not os.listdir(dfile):
        cmd = 'ls ' + house_keeping + 'Defect/CCD' + str(ccd) + '/* > ' +  zspace
        os.system(cmd)

        data = mcf.read_data_file(zspace)
        mcf.rm_file(zspace)
#
#--- compare the time stamp to the cut off time and if the file is older 
#--- than that date, move to gzip it and move to a save directory
#
        for ent in data:
            try:
                atemp = re.split('acis', ent)
                btemp = re.split('_',    atemp[1])
                bdate = float(btemp[0])
                if bdate < cut_date:
                    cmd = 'gzip ' + ent
                    os.system(cmd)
                    cmd = 'mv ' + ent + '.gz ' + data_dir + 'Old_data/CCD' + str(ccd) + '/.'
                    os.system(cmd)
            except:
                pass

#-------------------------------------------------------------------------------------------
#--- find_bad_col: find warm columns                                                     ---
#-------------------------------------------------------------------------------------------

def find_bad_col(varray, ccd, cstart, ccd_dir, head ):
    """
    find warm columns
    input:  varray  --- data in 2 dim form [y, x] (numpy array)
            ccd     --- ccd #
            cstart  --- starting column #. the data are binned between 0 and 255.
            ccd_dir --- location of data saved
            head    --- header of the file
    output: <ccd_dir>/<head>col --- a file which keeps a list of warm columns
    """
#
#--- read known bad col list
#
    bad_col_list = read_bad_col_list()
#
#--- set a data file name to record actual today's bad column positions
#
    bad_col_name = head + '_col'
    outdir_name  = ccd_dir + '/' + bad_col_name
#
#--- today's bad column list name at a working directory
#
    wout_dir     = './Working_dir/today_bad_col_' + str(ccd)
#
#--- bad column list for ccd
#
    bad_cols = bad_col_list[ccd]
    bcnt     = len(bad_cols)
    bList    = []
#
#---- make a list of just column # (no starting /ending row #)
#
    if bcnt > 0:
        for ent in bad_cols:
            ent   = ent.replace('"', '')
            atemp = re.split(':', ent)
            bList.append(int(atemp[0]))
#
#--- create a list of averaged column values
#
    avg_cols = create_col_avg(varray)
#
#--- set a global limit to find outlyers
#
    cfactor = col_factor
    climit  = find_local_col_limit(avg_cols, 0, 255, cfactor)

    bcnum = 0
    for i in range(0, 255):
#
#--- check whether the row is a known bad column
#
        cloc = cstart + i               #---- modify to the actual column position on the CCD
        chk  = 0
        if bcnt > 0:
            for comp in bList:
                if cloc == comp:
                    chk = 1
                    break
        if chk == 1:
            continue
#
#--- find the average of the column and if the column is warmer than the limit, check farther
#
        if avg_cols[i] > climit:
#
#--- local limit
#
            (llow, ltop) = find_local_range(i)
            cfactor      = 2.0
            l_lim        = find_local_col_limit(avg_cols, llow, ltop, cfactor, ex = i)
#
#--- if the column is warmer than the local limit, record it
#
            if avg_cols[i] > l_lim:
                if cloc != 0:
                    print_result(outdir_name, cloc)
                    bcnum += 1
#
#---- clean up the file (removing duplicated lines)
#
    if bcnum > 0:
        mcf.remove_duplicated_lines(outdir_name)
#
#--- record today's bad column list name at a working directory
#
        print_result(wout_dir, bad_col_name)

#-------------------------------------------------------------------------------------------
#-- find_local_range: set a local range                                                   --
#-------------------------------------------------------------------------------------------

def find_local_range(i):
    """
    set a local range
    input:  i       --- pixel postion
    ouput:  llow    --- low limit
            ltop    --- top limit
    """
#
#--- setting a local area range
#
    llow  = i - 5
    ltop  = i + 5
#
#--- at the edge of the area, you still want to keep 10 column length
#
    if llow < 0:
        ltop -= llow
        llow  = 0

    if ltop > 255:
        llow -= ltop - 255
        ltop  = 255

    return(llow, ltop)

#-------------------------------------------------------------------------------------------
#-- create_col_avg: compute the average of column value                                   --
#-------------------------------------------------------------------------------------------

def create_col_avg(varray):
    """
    compute the average of column value
    input: varray       --- a two dim array of the data
    output: avg_cols    --- a list of average values of columns
    """
    avg_cols = [0 for x in range(0, 255)]
    for i in range(0, 255):
        l_mean = numpy.mean(varray[:,i])
        avg_cols[i] = l_mean

    return avg_cols

#-------------------------------------------------------------------------------------------
#-- find_local_col_limit: find local colun limit value                                    --
#-------------------------------------------------------------------------------------------

def find_local_col_limit(avg_cols, llow, ltop, cfactor,  ex=-999):
    """
    find local colun limit value
    input:  avg_cols    --- a list of average values of colums
            llow        --- a low limit range
            ltop        --- a top limit range
            cfactor     --- the factor to set the limit
    output: l_lim       --- local column limit
    """
    csum = 0
    tot  = 0
    for i in range(llow,ltop):
        if i == ex:
            continue
    
        csum  += avg_cols[i]
        tot   += 1
    
    lavg = csum / tot

    csum2 = 0
    tot   = 0
    for i in range(llow,ltop):
        if i == ex:
            continue
    
        ldiff  = avg_cols[i] - lavg
        csum2 += ldiff * ldiff
        tot   += 1
    
    lstd = math.sqrt(csum2 / tot)
    
#    l_lim = lavg + col_factor * lstd
    l_lim = lavg + cfactor * lstd
    
    return l_lim

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def print_result(outdir_name, line):

    with open(outdir_name, 'a') as fo:
        fo.write(str(line) + '\n')

#-------------------------------------------------------------------------------------------
#--- chk_bad_col: find bad columns for a given ccd                                       ---
#-------------------------------------------------------------------------------------------

def chk_bad_col(ccd):
    """
    find bad columns for a given ccd
    input:  ccd      --- ccd #
    output: bad_cols --- a list of bad columns
    """
    bad_cols = []

    dfile = house_keeping + 'Defect/CCD' + str(ccd) + '/'

    if  os.listdir(dfile):
        cmd     = 'ls -rt ' + dfile + '/* > ' + zspace
        os.system(cmd)
        test = open(zspace).read()
        mcf.rm_file(zspace)
        m1 = re.search('col', test)
        if m1 is not None:
            chk = 1
        else:
            chk = 0
    else:
        chk = 0

    if chk == 1:

        cmd     = 'ls -rt ' + dfile + '/*col > ' + zspace
        os.system(cmd)
        collist = mcf.read_data_file(zspace, remove=1)
#
#--- if there is more than three col files and if we have new bad col today, procced the process
#
        dlen = len(collist)
    
        if dlen > 2:
            ifile  = collist[dlen-1]
            file1 = mcf.read_data_file(ifile)
    
            ifile  = collist[dlen-2]
            file2 = mcf.read_data_file(ifile)
    
            colcand = []
            for ent in file1:
                try:
                    val = float(ent)            #--- try to weed out none digit entries
                    for comp in file2:
                        if ent == comp:
                            colcand.append(ent)
                            break
                except:
                    pass
#
#--- if columns appear in both files, try the third
#
            if len(colcand) > 0: 
    
                ifile = collist[dlen-2]
                file3 = mcf.read_data_file(ifile)
    
                for ent in colcand:
                    for comp in file3:
                        if ent == comp:
                            bad_cols.append(ent)
                            break
    
    if len(bad_cols) > 0:
        bad_cols = list(set(bad_cols))
        bad_cols = [int(x) for x in bad_cols]
        bad_cols = sorted(bad_cols)
        bad_cols = [str(x) for x in bad_cols]

    return bad_cols

 
#-------------------------------------------------------------------------------------------
#--- print_bad_col: update bad column output files                                       ---
#-------------------------------------------------------------------------------------------

def print_bad_col(ccd, bad_col_list, stime):
    """
    update bad column output files
    input:  ccd                     --- ccd #
            bad_col_list            --- a list of bad columns on the ccd
            stime                   --- today's (or given data's) seconds from 1998.1.
    output: <data_dir>/col<ccd#>      --- today's bad columns
            <data_dir>/hit_col<ccd#>  --- history of bad columns
    """
    blen  = len(bad_col_list)
    stime = int(stime)
    date  = mcf.convert_date_format(stime, ifmt='chandra', ofmt='%Y:%j')
    atemp = re.split(':', date)
    date  = atemp[0] + ':' + atemp[1].lstrip('0')
#
#--- even if there is no data, update history file
#
    line1 = ''
    line2 = ''
    if blen == 0:
        line2 = line2 + str(stime) + '<>' + date + '<>:\n'

    else:
#
#--- if there are bad col, update history file and update col<ccd> file
#
        line2 = line2 +  str(stime) + '<>' + date + '<>' 
        for ent in bad_col_list:
            line1 = line1 + ent + '\n'

            line2 = line2 + ':' + ent

        line2  = line2 + '\n'

    out1 = data_dir + 'col' + str(ccd)
    out2 = data_dir + 'hist_col' + str(ccd)

    if line1 != '':
        with open(out1, 'w') as f1:
            f1.write(line1)

    with open(out2, 'a') as f2:
        f2.write(line2)

    #mcf.remove_duplicated_lines(out2, chk =1)
 
#-------------------------------------------------------------------------------------------
#--- find_bad_pix_candidate: find bad pixel candidates for the next step                ----
#-------------------------------------------------------------------------------------------

def  find_bad_pix_candidate(varray, ccd, quad, date_obs, ccd_dir, max_file, hot_max_file):
    """
    find dad pixel candidates for the next step... they are bad pixel for just today's data
    Input:  varray       --- 2x2 data surface  [y, x] (numpy array)
            ccd          --- ccd #
            quad         --- quad 0 - 3
            date_obs     --- obs date
            ccd_dir      --- data location
            max_file     --- <head>_<quad>_max: a file name which will contain warm pixel data  (e.g. acis485603580_q1_max)
            hot_max_file --- <head>_<quad>_hot: a file name which will contain hot pixel data (e.g. acis485603580_q1_hot)
    Output: <ccd_dir>/max_file     --- file contains warm pixel list
            <ccd_dir>/hot_max_file --- file contains hot pixel list
    """
#
#--- set a couple of arrays
#
    warm_list = []
    hot_list  = []
    wsave     = ''
    hsave     = ''
#
#--- divide the quad to 8x32 areas so that we can compare the each pix to a local average
#
    for ry in range(0, 32):
        ybot  = 32 * ry
        ytop  = ybot + 31
        ybot2 = ybot
        ytop2 = ytop
#
#--- even if the pixel is at the edge, use 8 x 32 area
#
        if ytop > 1023:
            diff   = ytop -1023 
            ytop2  = 1023
            ybot2 -= diff

        for rx in range (0, 8):
            xbot  = 32 * rx
            xtop  = xbot + 31
            xbot2 = xbot
            xtop2 = xtop

            if xtop > 255:
                diff   = xtop - 255
                xtop2  = 255
                xbot2 -= diff

            lsum  = 0.0
            lsum2 = 0.0
            lcnt  = 0.0
            for ix in range(xbot2, xtop2):
                for iy in range(ybot2, ytop2):
                    lsum  += varray[iy, ix]
                    lcnt  += 1

            if lcnt < 1:
                continue

            lmean = float(lsum) / float(lcnt)

            for ix in range(xbot2, xtop2):
                for iy in range(ybot2, ytop2):
                    lsum2 += (varray[iy, ix]  - lmean) * (varray[iy, ix]  - lmean)

            lstd  = math.sqrt(lsum2 / float(lcnt))
            warm  = lmean + factor * lstd
            hot   = lmean + hot_factor

            for ix in range(xbot, xtop2):
                for iy in range(ybot, ytop2):
                    if varray[iy, ix]  >= warm:
                        (cwarm, chot, cmean, cstd) = local_chk(varray, ix, iy, lmean, lstd, warm , hot)
#
#--- hot pix check
#
                        if varray[iy, ix] > chot:
                            line = ccd_dir + '/' + hot_max_file
                            hot_list.append(line)
#
#--- adjusting to correction position
#
                            mix   = ix + 1
                            miy   = iy + 1
                            aline = str(mix) + '\t' + str(miy) + '\t' + str(varray[iy, ix]) + '\t' 
                            aline = aline + date_obs + '\t' + str(cmean) + '\t' + str(cstd) + '\n'

                            with open(line, 'a') as fo:
                                fo.write(aline)
#
#--- warm pix check
#
                        elif varray[iy, ix] > cwarm:
                            line = ccd_dir + '/' + max_file
                            warm_list.append(line)

                            mix   = ix + 1
                            miy   = iy + 1
                            aline = str(mix) + '\t' + str(miy) + '\t' + str(varray[iy, ix]) + '\t' 
                            aline = aline + date_obs + '\t' + str(cmean) + '\t' + str(cstd) + '\n'

                            with open(line, 'a') as fo:
                                fo.write(aline)
#
#--- remove dupulicated line.
#
    if len(warm_list) > 0:
        today_warm_list = mcf.remove_duplicated_lines(warm_list, chk = 0)
    else:
        today_warm_list = []

    if len(hot_list) > 0:
        today_hot_list  = mcf.remove_duplicated_lines(hot_list,  chk = 0)
    else:
        today_hot_list  = []
#
#--- print out the data; even if it is empty, we still create a file
#
    line = ccd_dir + '/' + max_file
    try:
        if len(today_warm_list) > 0:
#
#--- keep the record of today's data
#
            aline = './Working_dir/today_bad_pix_' + str(ccd) + '_q' + str(quad)
            with open(aline,  'a') as fo:
                fo.write(line + '\n')

    except:
        pass

    line = ccd_dir + '/' + hot_max_file
    try:
        if len(today_hot_list) > 0:

            aline = './Working_dir/today_hot_pix_' + str(ccd) + '_q' + str(quad)
            with open(aline,  'a') as fo:
                fo.write(hot_max_file + '\n')
    except:
        pass

#-------------------------------------------------------------------------------------------
#--- select_bad_pix: find bad pixels                                                     ---
#-------------------------------------------------------------------------------------------

def select_bad_pix(ccd, quad):
    """
    find bad pixels for a given ccd/quad
    input:  ccd   --- ccd #
            quad  --- quad #
    output: output from identifyBadEntry
            warm_data_list
            hot_data_list
    """
#
#--- warm pixels
#
    warm_data_list = identifyBadEntry(ccd, quad, 'today_bad_pix', '_max')
#
#--- hot pixels
#
    hot_data_list  = identifyBadEntry(ccd, quad, 'today_hot_pix', '_hot')

    return(warm_data_list, hot_data_list)

#-------------------------------------------------------------------------------------------
#--- identifyBadEntry: find which pixels are warm/hot the last three observations         --
#-------------------------------------------------------------------------------------------

def identifyBadEntry(ccd, quad, today_list, ftail):
    """
    find which pixels are warm/hot the last three observations
    input:  ccd        --- ccd #
            quad       --- quad #
            today_list --- today's list
            ftail      ---  pix (warm case)/hot (hot_case)
    output: bad_list   --- warm/hot pixel list
    """
    bad_list = []
#
#--- check whether we have any bad pixels/columns in today's data
#
    ifile = './Working_dir/' + today_list +  '_' + str(ccd) + '_q' + str(quad)
    bad   = mcf.read_data_file(ifile)

    if len(bad) == 0:
        return bad_list
#
#--- a list is not empty
#
    for i in range(0, len(bad)):
#
#--- if there is a bad data, check the past data: find two previous records
#
        if not os.path.isfile(bad[i]):
            continue

        if os.stat(bad[i]).st_size > 0:
            cmd  = 'ls ' + house_keeping + '/Defect/CCD' + str(ccd) 
            cmd  = cmd   + '/acis*_q' + str(quad) + ftail + '>' + zspace
            os.system(cmd)

            data = mcf.read_data_file(zspace, remove=1)
            lcnt = len(data)
            if lcnt == 0:
                continue

            lcnt1 = lcnt -1
            for k in range(0, lcnt):
                j = lcnt1 - k
#
#--- we located today's data in the data directory
#
                if data[j] == bad[i]:
                    if j > 1:
#
#--- check whether one before is empty or not
#
                        if os.stat(data[j-1]).st_size > 0:
#
#--- if it is not, empty, check whether one before is empty or not
#
                            if os.stat(data[j-2]).st_size > 0:
#
#--- three consecuitve data sets are not empty, let check whether 
#--- any pixels are warm three consecutive time.
#
                                file1 = bad[i]
                                file2 = data[j-1]
                                file3 = data[j-2]

                                #--- I AM NOT QUITE SURE THE FOLLOWING FIX IS CORRECT!!!! (03/21/19)
                                #bad_list = find_bad_pix(ccd, quad, file1, file2, file3)
                                bad_list = bad_list + find_bad_pix(ccd, quad, file1, file2, file3)

    return bad_list

#-------------------------------------------------------------------------------------------
#-- print_bad_pix_data: update bad pixel data files                                      ---
#-------------------------------------------------------------------------------------------

def print_bad_pix_data(ccd, data_list, bind, today_time = 'NA'):
    """
    update bad pixel data files
    input:  ccd   --- ccd #
            data_list  --- bad pixel list
            bind       --- warm/hot
            today_time --- DOM of the data
    output: totally_new<ccd>
            all_past_bad_pix<ccd>
            new_ccd<ccd>
            ccd<ccd>
            hist_ccd<ccd>

            similar output for hot pixel data
    """
    if today_time != 'NA':
        stime  = today_time
        out    = Chandra.Time.DateTime(stime).date
        atemp  = re.split(":", out)
    else:
        out    = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
        stime  = Chandra.Time.DateTime(out).secs
        atemp  = re.split(':', out)

    date = str(atemp[0]) + ':' + str(int(atemp[1]))
#
#--- check any pixels are listed in totally_new<ccd> list (which lists new 
#--- bad pix occured only in the last two weeks)
#
    if bind == 'warm':
        file5 = data_dir + 'hist_ccd'  + str(ccd)
    else:
        file5 = data_dir + 'hist_hccd' + str(ccd)

    pline = str(stime) + '<>' + date +  '<>'

    if len(data_list) > 0:
        for ent in data_list:
            atemp = re.split(':', ent)
            pline = pline + ':(' + atemp[4] + ',' + atemp[5] + ')' 

        pline = pline + '\n'
    else:
        pline = pline + ':' + '\n'
#
#--- add to history data
#--- first check whether this is a duplicated date, if so, just ignore
#
    data = mcf.read_data_file(file5)
    aaa = re.split('<>', data[-1])
    if len(data) > 0:
        dline = ''
        for ent in data:
            atemp = re.split('<>', ent)
            try:
                ltime  = int(float(atemp[0]))
            except:
                continue

            if ltime < stime:
                dline = dline + ent + '\n'
            else:
                break

        with open(file5, 'w') as fo:
            fo.write(dline)
            fo.write(pline)

    else:
        with open(file5, 'w') as fo:
            fo.write(pline)

#-------------------------------------------------------------------------------------------
#--- find_bad_pix: find bad pixel by comparing three consecutive data                    ---
#-------------------------------------------------------------------------------------------

def  find_bad_pix(ccd, quad,  file1, file2, file3):
    """
    find bad pixel by comparing three consecutive data
    input:  ccd     --- ccd #
            quad    --- quad #
            file1   --- first data file
            file2   --- second data file
            file3   --- thrid data file
    output: cleaned --- bad pixel list
    """
    out_file = []

    [x1, y1, line1] = readBFile(ccd, file1)
    [x2, y2, line2] = readBFile(ccd, file2)
#
#--- comparing first two files to see whether there are same pixels listed
#--- if they do, save the information $cnt_s will be > 0 if the results are positive
#
    if len(x1) > 0 and len(x2) > 0:
        [xs, ys, ls ] = pickSamePix(x1, y1, line1, x2, y2, line2)

        if len(xs) > 0:
            [x3, y3, line3] = readBFile(ccd, file3)
            [xs2, ys2, ls2] = pickSamePix(xs, ys, ls, x3, y3, line3)

            if len(xs2) > 0:
                for i in range(0, len(xs2)):
                    try:
                        val   = float(xs2[i])
                        atemp = re.split('\s+|\t+', ls2[i])
                        line  = str(ccd) + ':' + str(quad) + ':' + atemp[3] 
                        line  = line + ':' + xs[i] + ':' + ys[i]
                        out_file.append(line)
                    except:
                        pass

    if len(out_file) > 0:
        cleaned = mcf.remove_duplicated_lines(out_file, chk = 0)
    else:
        cleaned = []

    return cleaned

#-------------------------------------------------------------------------------------------
#---  readBFile: read out ccd data file                                                 ----
#-------------------------------------------------------------------------------------------

def readBFile(ccd, ifile):                  #--- ccd is not used!!!
    """
    read out ccd data file
    input:  ccd  --- ccd #
            file --- file name
    output: a list of (x position list, y position list, value list)
    """
    data = mcf.read_data_file(ifile)

    xa = []
    ya = []
    la = []
    if len(data) > 0:
        for ent in data:
            atemp = re.split('\s+|\t+', ent)
            xa.append(atemp[0])
            ya.append(atemp[1])
            la.append(ent)

    return (xa, ya, la)

#-------------------------------------------------------------------------------------------
#--- pickSamePix: find pixels appear in two files given                                  ---
#-------------------------------------------------------------------------------------------

def pickSamePix(x1, y1, line1, x2, y2, line2):
    """
    find pixels appear in two files given
    input:  x1    --- x coordinates of the first file
            y1    --- y coordinates of the first file
            line1 --- all data information associates to x1, y1 pixel
            x2    --- x coordinates of the second file
            y2    --- y coordinates of the second file
            line2 --- all data information associates to x2, y2 pixel
    output: list of [x coordinates, y coordinates, pixel info]
    """
    x_save = []
    y_save = []
    l_save = []

    for i in range(0, len(x1)):
        for j in range(0, len(x2)):
            if x1[i] == x2[j] and y1[i] == y2[j] and x1[i] != '':
                x_save.append(x1[i])
                y_save.append(y1[i])
                l_save.append(line1[i])
                break
    return (x_save, y_save, l_save)

#-------------------------------------------------------------------------------------------
#--- local_chk: compute local mean, std, warm limit and hot limit                        ---
#-------------------------------------------------------------------------------------------

def local_chk(varray, ix, iy, lmean, lstd, warm, hot):
    """
    compute local mean, std, warm limit and hot limit 
    input:  varray --- data array (2D) [y, x] (numpy array)
            ix     --- x coordinate of the pixel of interest
            iy     --- y coordinate of the pixel of interest
            lmean  --- mean value of the area
            lstd   --- standard deviation of the area
            warm   --- warm limit of the area
            hot    --- hot limit of the area
    output: leanm  --- mean value of the local area
            lstd   --- standard deviation of the local area
            warm   --- warm limit of the local area
            hot    --- hot limit of the local area
    """
#
#--- check the case, when the pixel is located at the coner, and cannot
#--- take 16x16 around it.  if that is the case, shift the area
#
    x1 = ix - 8
    x2 = ix + 8
    if(x1 < 0):
        x2 += abs(x1)
        x1  = 0
    elif x2 > 255:
        x1 -= (x2 - 255)
        x2  = 255

    y1 = iy - 8
    y2 = iy + 8
    if(y1 < 0):
        y2 += abs(y1)
        y1  = 0
    elif y2 > 1023:
        y1 -= (y2 - 1023)
        y2  = 1023 

    csum  = 0.0
    csum2 = 0.0
    ccnt  = 0.0
    for xx in range(x1, x2+1):
        for yy in range(y1, y2+1):
            try:
                cval = float(varray[yy, xx])
                cval = int(cval)
            except:
                cval = 0
            csum  += cval
            csum2 += cval * cval 
            ccnt  += 1
    try: 
        cmean = float(csum) /float(ccnt)
        cstd  = math.sqrt(float(csum2) / float(ccnt) - cmean * cmean)
        cwarm = cmean + factor * cstd
        chot  = cmean + hot_factor
        return (cwarm, chot, cmean, cstd)
    except:
        cwarm = lmean + factor * lstd
        chot  = lmean + hot_factor
        return (lmean, lstd, warm, hot)

#-------------------------------------------------------------------------------------------
#--- extractCCDInfo: extract CCD information from a fits file                            ---
#-------------------------------------------------------------------------------------------

def extractCCDInfo(ifile):
    """
    extreact CCD infromation from a fits file
    input:  ifile       --- fits file name
    output: ccd_id      --- ccd #
            readmode    --- read mode
            date_obs    --- observation date
            overclock_a --- overclock a 
            overclock_b --- overclock b 
            overclock_c --- overclock c 
            overclock_d --- overclock d 
    """
#
#--- read fits file header
#
    try:
        f           = pyfits.open(ifile)
        hdr         = f[0].header
        ccd_id      = hdr['CCD_ID']
        readmode    = hdr['READMODE']
        date_obs    = hdr['DATE-OBS']
        overclock_a = hdr['INITOCLA']
        overclock_b = hdr['INITOCLB']
        overclock_c = hdr['INITOCLC']
        overclock_d = hdr['INITOCLD']
        f.close()
    
        return [ccd_id, readmode, date_obs, overclock_a, overclock_b, overclock_c, overclock_d]
    except:
        return ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']

#-------------------------------------------------------------------------------------------
#--- read_bad_pix_list: read knwon bad pixel list                                        ---
#-------------------------------------------------------------------------------------------

def read_bad_pix_list():
    """
    read knwon bad pixel list
    input:  <house_keeping>/Defect/bad_pix_list
    output: bad_pix_list --- a list of lists of bad pixels separated by CCD
    """
#
#--- initialize the list
#
    bad_pix_list = []
    for i in range(0, 10):
        bad_pix_list.append([])
#
#--- read data
#
    line = house_keeping + '/Defect/bad_pix_list'
    data = mcf.read_data_file(line)
#
#--- separate bad pixels into different CCDs
#
    for ent in data:
        m = re.search('#', ent)
        if m is None:
            atemp = re.split(':', ent)
            k     = int(float(atemp[0]))
            line  = '"' + str(atemp[2]) + ':' + str(atemp[3]) + '"'
            bad_pix_list[k].append(line)

    return bad_pix_list

#-------------------------------------------------------------------------------------------
#---  read_bad_col_list: read in known bad column lists                                  ---
#-------------------------------------------------------------------------------------------

def read_bad_col_list():
    """
    read in known bad column lists
    input:  <house_keeping>/Defect/bad_col_list
    output: bad_col_list --- a list of list of bad columns separated by CCDs
    """
#
#--- initialize the list
#
    bad_col_list = []
    for i in range(0, 10):
        bad_col_list.append([])
#
#--- read data
#
    line = house_keeping + '/Defect/bad_col_list'
    data = mcf.read_data_file(line)
#
#--- separate bad columns  into different CCDs
#
    for ent in data:
        m = re.search('#', ent)
        if m is None:
            atemp = re.split(':', ent)
            k     = int(float(atemp[0]))
            line  = '"' + str(atemp[3]) + ':' + str(atemp[2]) + ':' + str(atemp[3]) + '"'
            bad_col_list[k].append(line)

    return bad_col_list

#-------------------------------------------------------------------------------------------
#--- removeIncompteData: removing files which indicated "imcoplete"                     ----
#-------------------------------------------------------------------------------------------

def removeIncompteData(cut_time):
    """
    remove files which are indicated "imcoplete" by cut_time 
    (if the file is created after cut_time)
    input:  cut_time    --- the cut time which indicates when to remove the data file
                            time is in seconds from 1998.1.1
    output: None, but delete files
    """
    for ccd in range(0, 10):
        ifile = data_dir + 'data_used' + str(ccd)
        trimFile(ifile, cut_time, 0)
        
    for head in ('change_ccd', 'change_col', 'imp_ccd', 'new_ccd', 'imp_col', 'new_col'):
        for ccd in range(0, 10):
            ifile  =  data_dir +  head + str(ccd)
            trimFile(ifile, cut_time, 1)

    for ccd in range(0, 10):
        ifile = data_dir + 'hist_ccd' + str(ccd)
        trimFile(ifile, cut_time, 1)

#-------------------------------------------------------------------------------------------
#---  trimFile: drop the part of the data from the file if the data is created after cut_time 
#-------------------------------------------------------------------------------------------

def trimFile(ifile, cut_time, dtype):
    """
    drop the part of the data from the file if the data is created after cut_time
    input:  ifile    --- file name
            cut_time --- the cut time
            dtype    --- how to find a stime, if dtype == 0: the time is in form of 20013:135. 
                         otherwise, in stime (seconds from 1998.1.1)
    output: file     --- updated file
    """

    try:
        data = mcf.read_data_file(ifile)
        if len(data) > 0:
            sline = ''
            for  ent in data:
                try:
                    if dtype == 0:
                        atemp = re.split(':', ent)
                        year  = int(float(atemp[0]))
                        ydate = int(float(atemp[1]))
                        ydate = mcf.add_leading_zero(ydate, 3)
                        ltime = atemp[0] + ':' + ydate + ':00:00:00'
                        dtime = int(Chandra.Time.DateTime(ltime).secs)
                    else:
                        atemp = re.split('<>', ent)
                        dtime = int(atemp[0])

                    if dtime >= cut_time:
                        break
                    else:
                        sline = sline + ent  + '\n'
                except:
                    pass

            with open(zspace, 'w') as fo:
                fo.write(sline)
            
            cmd = 'mv ' + zspace + ' ' + ifile
            os.system(cmd)
    except:
        pass

#-------------------------------------------------------------------------------------------
#-- get_data_out: extract acis bias data file                                             --
#-------------------------------------------------------------------------------------------

def get_data_out(start, stop):
    """
    extract acis bias data file
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: asic bias data fits files
            save    --- a list of fits files extracted
    """
#
#--- convert data format
#
    tstart = mcf.convert_date_format(start, ofmt="%Y-%m-%dT%H:%M:%S")
    tstop  = mcf.convert_date_format(stop,  ofmt="%Y-%m-%dT%H:%M:%S")
#
#---clean up the temporary output directory
#
    fdir = exc_dir + 'Temp_data/'
    if os.path.isdir(fdir):
        cmd  = 'rm  -rf ' + fdir + '/*'
        os.system(cmd)
    else:
        cmd  = 'mkdir ' + fdir
        os.system(cmd)
#
#--- write  required arc5gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=acis\n'
    line = line + 'level=0\n'
    line = line + 'filetype=bias0\n'
    line = line + 'tstart=' + str(tstart) + '\n'
    line = line + 'tstop='  + str(tstop) + '\n'
    line = line + 'go\n'
    with open(zspace, 'w') as f:
        f.write(line)
#
#--- run arc5gl
#
    outf = exc_dir + 'Temp_data/zout'
    try:
        cmd = 'cd ' + exc_dir +  'Temp_data; /proj/sot/ska/bin/arc5gl -user isobe -script ' 
        cmd = cmd   + zspace  + ' > ' + outf
        os.system(cmd)
    except:
        cmd1 = "/usr/bin/env PERL5LIB= "
        cmd2 = '  cd ' + exc_dir + 'Temp_data; /proj/axaf/simul/bin/arc5gl -user isobe -script ' 
        cmd2 = cmd2    + zspace  + '> ' + outf
        try:
            os.system(cmd2)
        except:
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)

    mcf.rm_files(zspace)
#
#--- get a list of retrieved fits files
#
    data = mcf.read_data_file(outf)
    mcf.rm_files(outf)

    save = []
    for ent in data:
        mc = re.search('fits', ent)
        if mc is not None:
            fname = fdir + ent
            save.append(fname)

    return save

#---------------------------------------------------------------------------------------
#-- find_data_collection_interval: find data collection period in dom---
#---------------------------------------------------------------------------------------

def find_data_collection_interval():
    """
    find data collection period in dom
    input:  none but read from <data_dir>/Dis_dir/hist_ccd3
    output: ldate   --- starting time in seconds from 1998.1.1
            tdate   --- stopping time in seconds from 1998.1.1
    """
#
#--- find today's  date
#
    tout  = time.strftime('%Y:%j:00:00:00', time.gmtime())
    tdate = int(mcf.convert_date_format(tout, ofmt='chandra'))
#
#--- find the date of the last entry
#
    ifile = data_dir + 'hist_ccd3'
    data  = mcf.read_data_file(ifile)
    data.reverse()
    
    for ent in data:
        atemp = re.split('<>', ent)
        try:
            ldate = int(float(atemp[0]))
            break
        except:
            continue
#
#--- the data colleciton starts from the next day of the last entry date
#--- make sure that the time start 0hr.
#
    ldate += 90000.0
    ltime  = Chandra.Time.DateTime(ldate).date
    atemp  = re.split(':', ltime)
    ltime  = atemp[0] + ':' + atemp[1] + ':00:00:00'
    ldate  = int(Chandra.Time.DateTime(ltime).secs)

    return [ldate, tdate]

#---------------------------------------------------------------------------------------
#-- mv_old_file: move supplemental data file older than 30 day to a reserve           --
#---------------------------------------------------------------------------------------

def mv_old_file(tdate):
    """
    move supplemental data file older than 30 day to a reserve
    input:  tdate   --- the current time in seconds from 1998.1.1
    output: none but older files are moved
    """
    tdate -= 30 * 86400

    cmd = 'ls ' + house_keeping + '/Defect/CCD*/* > ' + zspace
    os.system(cmd)
    ldata = mcf.read_data_file(zspace, remove=1)
    
    for ent in ldata:
        atemp = re.split('\/acis', ent)
        btemp = re.split('_', atemp[1])
    
    if int(btemp[0]) < tdate:
        out = ent
        out = out.replace('Defect', 'Defect/Save')
        cmd = 'mv ' + ent + ' ' + out
        os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_bad_pix(self):

        mcf.mk_empty_dir('/data/mta/Script/ACIS/Bad_pixels/Data/Ztemp_dir')
        cmd = 'mv /data/mta/Script/ACIS/Bad_pixels/Data/data_used*  /data/mta/Script/ACIS/Bad_pixels/Data/Ztemp_dir'
        os.system(cmd)
        cmd = 'cp -r /data/mta/Script/ACIS/Bad_pixels/Data/Ztemp_dir/* /data/mta/Script/ACIS/Bad_pixels/Data/.'
        os.system(cmd)
        mcf.mk_empty_dir('./Working_dir')

        mcf.rm_file('./Working_dir/*_list')
        a_list = int_file_for_day(main_list[0])
        dom = setup_to_extract()

        ccd = 3
        quad= 0
        (warm_data, hot_data) = select_bad_pix(ccd, quad)

        test_data = ['3:0:2014:255:21:95']

        self.assertEquals(warm_data, test_data)

        cmd = 'mv /data/mta/Script/ACIS/Bad_pixels/Data/Ztemp_dir/* /data/mta/Script/ACIS/Bad_pixels/Data/.'
        os.system(cmd)

#--------------------------------------------------------------------

if __name__ == '__main__':

    #unittest.main()

    if len(sys.argv) > 1:
        tstart = float(sys.argv[1])
        tstop  = float(sys.argv[2])
    else:
        tstart = ''
        tstop  = ''

    find_bad_pix_main(tstart, tstop)

