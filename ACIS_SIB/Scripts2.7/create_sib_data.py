#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################################
#                                                                                                           #
#           create_sib_data.py: create sib data for report                                                  #
#                                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                           #
#           Last Update: Jan 03, 2018                                                                       #
#                                                                                                           #
#############################################################################################################

import sys
import os
import string
import re
import copy
import math
import unittest
import time
import random

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param ', shell='tcsh')
ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACIS/SIB/Correct_excess/Lev1/Reportdir/'
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
####s_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/Test/'
####b_dir = '/data/mta/Script/ACIS/SIB/Correct_excess/Sib_corr/'
#
#--- append path to a private folders
#
sys.path.append(b_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import convertTimeFormat    as tcnv
import sib_corr_functions   as scf
import ccd_comb_plot        as ccp
import update_html          as uph
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------
#-- create_report: process the accumulated sib data and create a month long data fits files 
#-----------------------------------------------------------------------------------------

def create_report():
    """
    process the accumulated sib data and create a month long data fits files
    input:  none but read from <lev>/Outdir/lres/*fits
    output: lres_ccd<ccd>_merged.fits in ./Data/ directory
    """
#
#--- find data periods
#
    [begin, end, syear, smon, eyear, emon] = set_date()
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
        dname = '/data/mta/Script/ACIS/SIB/Data/Data_'      + str(syear) + '_' + lmon
    else:
        dname = '/data/mta/Script/ACIS/SIB/Lev2/Data/Data_' + str(syear) + '_' + lmon
    cmd   = 'mkdir ' + dname
    os.system(cmd)

    cmd   = 'mv ' + s_dir  + lev +  '/Data/* ' + dname
    os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- set_date: set the data for the last month                                          ---
#-----------------------------------------------------------------------------------------

def set_date():
    """
    set the data for the last month
    input:  none
    output: begni   --- starting date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            end     --- stopping date in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            syear   --- year of the starting time
            smon    --- month of the starting time
            eyear   --- year of the ending time
            emon    --- month of the ending time
    """
#
#--- find today's date information (in local time)
#
    tlist = time.localtime()
#
#--- set data time interval to the 1st of the last month to the 1st of this month
#
    eyear  = tlist[0]
    emon   = tlist[1]

    tline = str(eyear) + ' ' +str(emon) + ' 1'
    tlist = time.strptime(tline, "%Y %m %d")
    eyday = tlist[7]

    end   = str(eyear) + ':' + str(eyday) + ':00:00:00'

    syear  = eyear
    smon   = emon - 1
    if smon < 1:
        syear -= 1
        smon   = 12

    tline = str(syear) + ' ' +str(smon) + ' 1'
    tlist = time.strptime(tline, "%Y %m %d")
    syday = tlist[7]

    begin = str(syear) + ':' + str(syday) + ':00:00:00'

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

    lmon = tcnv.changeMonthFormat(mon)
    lmon = lmon.lower()

    cmd = 'mv ' + s_dir + lev + '/Outdir/lres ' 
    cmd = cmd   + s_dir + lev + '/Outdir/lres_' + lmon +str(year) + '_modified'
    os.system(cmd)

    cmd = 'rm -rf ' + s_dir + lev + '/Outdir/ctirm_dir'
    os.system(cmd)
    cmd = 'rm -rf ' + s_dir + lev + '/Outdir/filtered'
    os.system(cmd)
    cmd = 'rm -rf ' + s_dir + lev + '/Outdir/hres'
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
    file = s_dir + lev + '/Reg_files/ratio_table'
    data = scf.read_file(file)

    ratio    = {}
    for ent in data:
        #atemp = re.split('\s+', ent)
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
    cmd = 'ls ' + s_dir + lev + '/Outdir/lres/mtaf*.fits > ' + zspace
    os.system(cmd)
    data = scf.read_file(zspace, remove=1)

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
#--- correct the observation rate by devided by the ratio (all sources removed area)/(original are)
#
        elif div > 0:
            line  = 'SSoft=SSoft/' + str(div) + ',Soft=Soft/' + str(div) + ',Med=Med/' + str(div) + ','
            line  = line + 'Hard=Hard/' + str(div) + ',Harder=Harder/' + str(div) + ',Hardest=Hardest/' + str(div)

            cmd   = 'dmtcalc infile =' + ent + ' outfile=out.fits expression="' + line + '" clobber=yes'
            scf.run_ascds(cmd)

            cmd   = 'mv out.fits ' + ent
            os.system(cmd)

        else:
            print "Warning!!! div < 0 for " + str(ent)
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
        lres = s_dir + lev + '/Outdir/lres/'

        cmd  = 'ls ' + lres + 'mtaf*fits > ' + zspace
        os.system(cmd)
        data = scf.read_file(zspace, remove=1)
    
        cmd  = 'mkdir ' + lres + 'Save'
        os.system(cmd)

        for ent in data:
            cmd = 'dmlist ' + ent + ' opt=data > ' + zspace
            try:
                scf.run_ascds(cmd)
            except:
                continue

            out = scf.read_file(zspace, remove=1)
            ssoft   = 0.0
            soft    = 0.0
            med     = 0.0
            hard    = 0.0
            harder  = 0.0
            hardest = 0.0
            tot     = 0
            for val in out:
                atemp    = re.split('\s+', val)
                if mcf.chkNumeric(atemp[0]):
                    ssoft   += float(atemp[6])
                    soft    += float(atemp[7])
                    med     += float(atemp[8])
                    hard    += float(atemp[9])
                    harder  += float(atemp[10])
                    hardest += float(atemp[11])
                    tot     += 1
                else:
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
        epath =  s_dir + '/Lev2/Outdir/lres/Save/'
        if os.listdir(epath) != []:

            cmd = 'ls ' + s_dir + '/Lev2/Outdir/lres/Save/*fits > ' + zspace
            os.system(cmd)
            data = scf.read_file(zspace, remove=1)
    
            l1_lres =  s_dir + '/Lev1/Outdir/lres/'
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
    tstart = tcnv.axTimeMTA(start)
    tstop  = tcnv.axTimeMTA(stop)
#
#--- make a list of data fits files
#
    lres = s_dir + lev + '/Outdir/lres/'
    cmd  = 'ls ' + lres + '*fits > ' + zspace
    os.system(cmd)
    data = scf.read_file(zspace, remove=1)
#
#--- initialize ccd_list<ccd>
#
    for ccd in range(0, 10):
        exec 'ccd_list%s = []' % (str(ccd))

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
                    line = str(ent)
                    exec "ccd_list%s.append('%s')" % (str(ccd), line)
                    break
#
#--- combined all fits files of a specific ccd into one fits file
#
    for ccd in range(0, 10):
        exec "alist = ccd_list%s"  % (str(ccd))
        if len(alist) > 0:
#
#--- the first of the list is simply copied to temp.fits
#
            cmd = 'cp ' + alist[0] + ' temp.fits'
            os.system(cmd)

            for k in range(1, len(alist)):

                cmd = 'dmmerge "' + alist[k] + ',temp.fits" outfile=zmerged.fits outBlock=""'
                cmd = cmd + 'columnList="" clobber="yes"'
                try:
                    scf.run_ascds(cmd)
                except:
                    continue

                cmd = 'mv ./zmerged.fits ./temp.fits'
                os.system(cmd)

            cmd = 'mv ./temp.fits ' + s_dir + lev +  '/Data/lres_ccd' + str(ccd) + '_merged.fits'
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
    cmd = 'dmstat "' + fits + '[cols time]" centroid=no >' + zspace
    try:
        scf.run_ascds(cmd)
    except:
        return [0, 0]

    out = scf.read_file(zspace, remove=1)

    chk = 0
    for val in out:
        mc1 = re.search('min', val)
        mc2 = re.search('max', val)

        if mc1 is not None:
            atemp = re.split('\s+', val)
            tmin  = int(float(atemp[1]))
            chk  += 1

        elif mc2 is not None:
            atemp = re.split('\s+', val)
            tmax  = int(float(atemp[1]))
            chk  += 1

        if chk > 1:
            break

    return [tmin, tmax]


#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    create_report()
