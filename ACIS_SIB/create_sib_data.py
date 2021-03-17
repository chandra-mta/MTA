#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#           create_sib_data.py: create sib data for report                  #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           Last Update: Mar 03, 2021                                       #
#                                                                           #
#############################################################################

import sys
import os
import string
import re
import math
import unittest
import astropy.io.fits as pyfits
import time
import Chandra.Time
import random
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
import ccd_comb_plot        as ccp
import update_html          as uph
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- create_report: process the accumulated sib data and create a month long data fits files 
#-----------------------------------------------------------------------------------------

def create_report(year='', mon=''):
    """
    process the accumulated sib data and create a month long data fits files
    input:  year    --- year; optional, if it is not given, the script will assign
            mon     --- mon; optional, if it is not given, the script will assign
            read from <lev>/Outdir/lres/*fits
    output: lres_ccd<ccd>_merged.fits in ./Data/ directory
    """
#
#--- find data periods
#
    [begin, end, syear, smon, eyear, emon] = set_date(year, mon)
#
#--- process all data for the month
#
    create_sib_data("Lev2", begin, end, syear, smon)
    create_sib_data("Lev1", begin, end, syear, smon)
#
#--- plot data and update html pages
#
    ccp.ccd_comb_plot('normal')
    uph.update_html()
    uph.add_date_on_html()
#
#--- clean up directories
#
    cleanup_sib_dir("Lev1", smon, syear)
    cleanup_sib_dir("Lev2", smon, syear)

#-----------------------------------------------------------------------------------------
#-- create_sib_data: create sib data for report                                         --
#-----------------------------------------------------------------------------------------

def create_sib_data(lev, begin, end, syear, smon):
    """
    create sib data for report
    input:  lev --- level of data either Lev1 or Lev2
    output: combined data, plots, and updated html pages
    """
#
#--- correct factor
#
    correct_factor(lev)
#
#---   exclude all high count rate observations
#
    find_excess_file(lev)
#
#---   combine the data
#
    sib_corr_comb(begin, end , lev)
#
#--- make data directory
#
    lmon = str(smon)
    if smon < 10:
        lmon = '0' + lmon

    if lev == 'Lev1':
        dname = data_dir  + 'Data_' + str(syear) + '_' + lmon
    else:
        dname = data_dir2 + 'Data_' + str(syear) + '_' + lmon

    cmd   = 'mkdir -p ' + dname
    os.system(cmd)

    cmd   = 'mv -f ' + cor_dir  + lev +  '/Data/* ' + dname
    os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- set_date: set the data for the last month                                          ---
#-----------------------------------------------------------------------------------------

def set_date(year, mon):
    """
    set the data for the last month
    input:  year    --- year; optional
            mon     --- mon; optional
    output: begni   --- starting date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            end     --- stopping date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            syear   --- year of the starting time
            smon    --- month of the starting time
            eyear   --- year of the ending time
            emon    --- month of the ending time
    """
#
#--- if the year/month are not give, find today's date information (in local time)
#
    if year == '':
        tlist = time.localtime()
#
#--- set data time interval to the 1st of the last month to the 1st of this month
#
        eyear  = tlist[0]
        emon   = tlist[1]
    else:
        eyear  = year
        emon   = mon + 1
        if emon > 12:
            emon   = 1
            eyear += 1

    tline = str(eyear) + ' ' +str(emon) + ' 1'
    tlist = time.strptime(tline, "%Y %m %d")
    eyday = tlist[7]

    lyday = mcf.add_leading_zero(eyday, 3)
    end   = str(eyear) + ':' + str(lyday) + ':00:00:00'

    syear  = eyear
    smon   = emon - 1
    if smon < 1:
        syear -= 1
        smon   = 12

    tline = str(syear) + ' ' +str(smon) + ' 1'
    tlist = time.strptime(tline, "%Y %m %d")
    syday = tlist[7]

    lyday = mcf.add_leading_zero(syday, 3)
    begin = str(syear) + ':' + str(lyday) + ':00:00:00'

    return [begin, end, syear, smon, eyear, emon]

#-----------------------------------------------------------------------------------------
#-- cleanup_sib_dir: clean up the working directories                                   --
#-----------------------------------------------------------------------------------------

def cleanup_sib_dir(lev, mon, year):
    """
    clean up the working directories
    input:  lev     --- data level
            mon     --- month of the data processed
            year    --- year of the data processd
    output: none
    """
    lmon = mcf.change_month_format(mon)
    lmon = lmon.lower()

    cmd = 'mv ' + cor_dir + lev + '/Outdir/lres ' 
    cmd = cmd   + cor_dir + lev + '/Outdir/lres_' + lmon +str(year) + '_modified'
    os.system(cmd)

    cmd = 'rm -rf ' + cor_dir + lev + '/Outdir/ctirm_dir'
    os.system(cmd)
    cmd = 'rm -rf ' + cor_dir + lev + '/Outdir/filtered'
    os.system(cmd)
    cmd = 'rm -rf ' + cor_dir + lev + '/Outdir/hres'
    os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- correct_factor: adjust lres reuslts files for the area removed as the sources remvoed 
#-----------------------------------------------------------------------------------------

def correct_factor(lev):
    """
    adjust lres reuslts files for the area removed as the sources remvoed
    input:  lev --- level 1 or 2  
    output: adjusted fits files in lres 
    """
#
#--- read all correciton factor information
#
    ifile = cor_dir + lev + '/Reg_files/ratio_table'
    data  = mcf.read_data_file(ifile)

    ratio    = {}
    for ent in data:
        atemp = re.split(':', ent)
        rate  = float(atemp[1].strip())

        btemp = re.split('N',  atemp[0])
        mc    = re.search('_', btemp[0])
        if mc is not None:
            ctemp = re.split('_', btemp[0])
            msid  = ctemp[0]
        else:
            msid  = btemp[0]

        ctemp = re.split('ccd', atemp[0])
        dtemp = re.split('_',   ctemp[1])
        ccd   = dtemp[0]

        ind   = str(msid) + '.' + str(ccd)
        ratio[ind] = rate
#
#--- find all fits file names processed
#
    cmd = 'ls ' + cor_dir + lev + '/Outdir/lres/mtaf*.fits > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    for fits in data:
        atemp = re.split('N', fits)
        btemp = re.split('mtaf', atemp[0])
        msid  = btemp[1]

        mc = re.search('_', msid)
        if mc is not None:
            ctemp = re.split('_', msid)
            msid  = ctemp[0]

        atemp = re.split('acis', fits)
        btemp = re.split('lres', atemp[1])
        ccd   = btemp[0]

        ind   = str(msid) + '.' + str(ccd)
        try:
            div   = ratio[ind]
        except:
            continue 

        if div >= 1:
            continue
#
#--- correct the observation rate by devided by the ratio 
#--- (all sources removed area)/(original are)
#
        elif div > 0:
            line = 'SSoft=SSoft/'      + str(div)     + ',Soft=Soft/'
            line = line + str(div)     + ',Med=Med/'  + str(div) + ','
            line = line + 'Hard=Hard/' + str(div)     + ',Harder=Harder/' 
            line = line + str(div)     + ',Hardest=Hardest/' + str(div)

            cmd  = 'dmtcalc infile =' + ent + ' outfile=out.fits expression="' 
            cmd  = cmd  + line + '" clobber=yes'
            scf.run_ascds(cmd)

            cmd   = 'mv out.fits ' + ent
            os.system(cmd)

        else:
            print("Warning!!! div < 0 for " + str(ent))
            continue

#-----------------------------------------------------------------------------------------
#-- find_excess_file: find data with extremely high radiation and remove it             --
#-----------------------------------------------------------------------------------------

def find_excess_file(lev = 'Lev2'):
    """
    find data with extremely high radiation and remove it. 
    this is done mainly in Lev2 and copied the procesure in Lev2
    input:  lev --- level. default Lev2 (other option is Lev1)
    output: excess radiation data fits files in ./lres/Save/.
    """
    if lev == 'Lev2':
        lres = cor_dir + lev + '/Outdir/lres/'

        cmd  = 'ls ' + lres + 'mtaf*fits > ' + zspace
        os.system(cmd)
        data = mcf.read_data_file(zspace, remove=1)
    
        cmd  = 'mkdir ' + lres + 'Save'
        os.system(cmd)

        for ent in data:
            cmd = 'dmlist ' + ent + ' opt=data > ' + zspace
            try:
                scf.run_ascds(cmd)
            except:
                continue

            out = mcf.read_data_file(zspace, remove=1)
            ssoft   = 0.0
            soft    = 0.0
            med     = 0.0
            hard    = 0.0
            harder  = 0.0
            hardest = 0.0
            tot     = 0.0
            for val in out:
                atemp    = re.split('\s+', val)
                try:
                    chk      = float(atemp[0])

                    ssoft   += float(atemp[6])
                    soft    += float(atemp[7])
                    med     += float(atemp[8])
                    hard    += float(atemp[9])
                    harder  += float(atemp[10])
                    hardest += float(atemp[11])
                    tot     += 1.0
                except:
                    continue

            if tot > 1:
                ssoft   /= tot
                soft    /= tot
                med     /= tot
                hard    /= tot
                harder  /= tot
                hardest /= tot

            mc = re.search('acis6', ent)
            chk = 0
            if mc is not None:
                if (med > 200):
                    chk = 1
            else:
                if (soft > 500) or (med > 150):
                    chk = 1

            if chk > 0:
                cmd = 'mv ' + ent + ' ' + lres + 'Save/.'
                os.system(cmd)

    else:
#
#--- for Lev1, we move the files which removed in Lev2. we assume that we already
#--- run Lev2 on this function
#
        epath =  cor_dir + '/Lev2/Outdir/lres/Save/'
        if os.listdir(epath) != []:

            cmd = 'ls ' + cor_dir + '/Lev2/Outdir/lres/Save/*fits > ' + zspace
            os.system(cmd)
            data = mcf.read_data_file(zspace, remove=1)
    
            l1_lres =  cor_dir + '/Lev1/Outdir/lres/'
            l1_dir  =  l1_lres  + '/Save/'
            cmd     = 'mkdir ' + l1_dir
            os.system(cmd)
     
            for ent in data:
                atemp = re.split('mtaf', ent)
                btemp = re.split('N', atemp[1])
                mc = re.search('_', btemp[0])
                if mc is not None:
                    ctemp = re.split('_', btemp[0])
                    obsid = ctemp[0]
                else:
                    obsid = btemp[0]
    
                atemp = re.split('acis', ent)
                btemp = re.split('lres', atemp[1])
                ccd   = btemp[0]
                cid   = 'acis' + str(ccd) + 'lres_sibkg.fits'
    
                cmd = 'mv ' + l1_lres + 'mtaf' + obsid + '*' + cid + '  '  + l1_dir + '/.'
                os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- sib_corr_comb: combined fits files into one per ccd                                 --
#-----------------------------------------------------------------------------------------

def sib_corr_comb(start, stop, lev):
    """
    combined fits files into one per ccd
    input:  start   --- start time of the interval <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stop time of the interval  <yyyy>:<ddd>:<hh>:<mm>:<ss>
            lev     --- data level "Lev1" or "Lve2"
    output: combined data: lres_ccd<ccd>_merged.fits in Data directory
    """
#
#--- convert the time to seconds from 1998.1.1
#
    tstart = Chandra.Time.DateTime(start).secs
    tstop  = Chandra.Time.DateTime(stop).secs
#
#--- make a list of data fits files
#
    lres = cor_dir + lev + '/Outdir/lres/'
    cmd  = 'ls ' + lres + '*fits > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)
#
#--- initialize ccd_list
#
    ccd_list = [[] for x in range(0, 10)]
    for ent in data:
#
#--- check whether the data are inside of the specified time period
#
        [tmin, tmax] = find_time_interval(ent)
        if tmin >= tstart and tmax <= tstop:
            btemp = re.split('_acis', ent)
            head  = btemp[0]
#
#--- add the fits file to ccd_list 
#
            for ccd in range(0, 10):
                chk = 'acis' + str(ccd)
                mc = re.search(chk, ent)
                if mc is not None:
                    ccd_list[ccd].append(str(ent))
                    break
#
#--- combined all fits files of a specific ccd into one fits file
#
    for ccd in range(0, 10):
        if len(ccd_list[ccd]) > 0:
#
#--- the first of the list is simply copied to temp.fits
#
            cmd = 'cp ' + ccd_list[ccd][0] + ' temp.fits'
            os.system(cmd)

            for k in range(1, len(ccd_list[ccd])):
                cmd = 'dmmerge "' + ccd_list[ccd][k] 
                cmd = cmd + ',temp.fits" outfile=zmerged.fits outBlock=""'
                cmd = cmd + 'columnList="" clobber="yes"'
                try:
                    scf.run_ascds(cmd)
                except:
                    continue

                cmd = 'mv ./zmerged.fits ./temp.fits'
                os.system(cmd)

            cmd = 'mv ./temp.fits ' + cor_dir + lev +  '/Data/lres_ccd' 
            cmd = cmd + str(ccd) + '_merged.fits'
            os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- find_time_interval: find time interval of the fits file                             --
#-----------------------------------------------------------------------------------------

def find_time_interval(fits):
    """
    find time interval of the fits file
    input:  fits            --- fits file name
    output: [tmin, tmax]    --- start and stop time in seconds from 1998.1.1
    """
    fout  = pyfits.open(fits)
    fdata = fout[1].data
    tout  = fdata['time']

    tmin  = min(tout)
    tmax  = max(tout)

    return [tmin, tmax]

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv)  == 3:
        year = int(sys.argv[1])
        mon  = int(sys.argv[2])

        create_report(year=year, mon=mon)
    else:
        create_report()





