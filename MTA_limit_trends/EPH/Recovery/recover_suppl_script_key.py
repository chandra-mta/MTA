#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################    
#                                                                                   #
#       this is to recovering data using arc5gl                                     #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: May 20, 2019                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Ska.engarchive.fetch as fetch
import Chandra.Time
import datetime
import random
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts3.6/house_keeping/dir_list'
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf        #---- contains other functions commonly used in MTA scripts
import glimmon_sql_read         as gsr
import envelope_common_function as ecf
import fits_operation           as mfo
#
#--- set a temporary file name
#
rtail  = int(time.time()* random.random())
zspace = '/tmp/zspace' + str(rtail)

mday_list  = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
mday_list2 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#
#---- CHANGE THE FOLLOWING THINGS BEFORE RUNNING!!!
#---- check also arc5gl setting and timing (week/short/log) lines from around 434-
#
data_dir = '/data/mta/Script/MTA_limit_trends/Scripts3.6/EPH/Recovery/Outdir/'
glist    = ['ephkey']

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def update_eph_data(date = ''):
    """
    collect grad and  comp data for trending
    input:  date    ---- the date in yyyymmdd format. if not given, yesterday's date is used
    output: fits file data related to grad and comp
    """
#
#--- read group names which need special treatment
#
    #sfile = 'eph_list'
    #glist = mcf.read_data_file(sfile)
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = ecf.read_mta_database()
#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = ecf.read_cross_check_table()

    day_list = []
    for year in range(2000, 2019):             #---- CHANGE CHANGE CHAGE!!!!! 
        lyear = year
        for mon in range(1, 13):
            #if year == 2018 and mon > 1:
            #    break    
            #if year == 2017 and mon < 11:
            #    continue

            cmon = str(mon)
            if mon < 10:
                cmon = '0' + cmon

            nmon = mon + 1
            if nmon > 12:
                nmon = 1
                lyear += 1

            clmon = str(nmon)
            if nmon < 10:
                clmon = '0' + clmon


            start = str(year)  + '-' + cmon  + '-01T00:00:00'
            stop  = str(lyear) + '-' + clmon + '-01T00:00:00'
    
            print "Period: "  + str(start) + "<--->" + str(stop)
    
            for group in glist:
                print "Group: " + group
#
#---CHANGE THE DETECTOR/FILETYPE BEFORE RUNNING IF IT IS DIFFERENT FROM EPHHK 
#
                line = 'operation=retrieve\n'
                line = line + 'dataset=flight\n'
                line = line + 'detector=ephin\n'
                line = line + 'level=0\n'
                line = line + 'filetype=ephhk\n'
                line = line + 'tstart='   + start + '\n'
                line = line + 'tstop='    + stop  + '\n'
                line = line + 'go\n'

                flist = mcf.run_arc5gl_process(line)

                if len(flist) < 1:
                    print "\t\tNo data"
                    continue
#
#--- combined them
#
                flen = len(flist)
     
                if flen == 0:
                    continue
     
                elif flen == 1:
                    cmd = 'cp ' + flist[0] + ' ./ztemp.fits'
                    os.system(cmd)
     
                else:
                    mfo. appendFitsTable(flist[0], flist[1], 'ztemp.fits')
                    if flen > 2:
                        for k in range(2, flen):
                            mfo. appendFitsTable('ztemp.fits', flist[k], 'out.fits')
                            cmd = 'mv out.fits ztemp.fits'
                            os.system(cmd)
#
#--- remove indivisual fits files
#

                for ent in flist:
                    cmd = 'rm -rf ' + ent 
                    os.system(cmd)
#
#--- read out the data
#
                [cols, tbdata] = ecf.read_fits_file('ztemp.fits')
     
                cmd = 'rm -f ztemp.fits out.fits'
                os.system(cmd)
#
#--- get time data in the list form
#
                dtime = list(tbdata.field('time'))
     
                for k in range(1, len(cols)):
#
#--- select col name without ST_ (which is standard dev)
#
                    col = cols[k]
                    mc  = re.search('ST_', col)
                    if mc is not None:
                        continue
                    mc  = re.search('quality', col, re.IGNORECASE)
                    if mc is not None:
                        continue
                    mc  = re.search('mjf', col, re.IGNORECASE)
                    if mc is not None:
                        continue
                    mc  = re.search('gap', col, re.IGNORECASE)
                    if mc is not None:
                        continue
                    mc  = re.search('dataqual', col, re.IGNORECASE)
                    if mc is not None:
                        continue
                    mc  = re.search('tlm_fmt', col, re.IGNORECASE)
                    if mc is not None:
                        continue
#
#---- extract data in a list form
#
                    data = list(tbdata.field(col))
#
#--- change col name to msid
#
                    msid = col.lower()
#
#--- get limit data table for the msid
#
                    try:
                        tchk  = convert_unit_indicator(udict[msid])
                    except:
                        tchk  = 0
     
                    glim  = ecf.get_limit(msid, tchk, mta_db, mta_cross)
#
#--- update database
#
                    update_database(msid, group, dtime, data, glim)



#-------------------------------------------------------------------------------------------
#-- update_database: update/create fits data files of msid                                --
#-------------------------------------------------------------------------------------------

def update_database(msid, group, dtime, data,  glim, pstart=0, pstop=0, step=3600.0):
    """
    update/create fits data files of msid
    input:  msid    --- msid
            pstart  --- starting time in seconds from 1998.1.1; defulat = 0 (find from the data)
            pstop   --- stopping time in seconds from 1998.1.1; defulat = 0 (find from the data)
            step    --- time interval of the short time data set:default 3600.0
    output: <msid>_data.fits, <msid>_short_data.fits
    """
    cols  = ['time', msid, 'med', 'std', 'min', 'max', 'ylower', \
             'yupper', 'rlower', 'rupper', 'dcount',\
             'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper']

    out_dir = data_dir + group + '/'
#
#--- make sure that the sub directory exists
#
    if not os.path.isdir(out_dir):
        cmd = 'mkdir ' + out_dir
        os.system(cmd)

    fits  = out_dir + msid + '_data.fits'
    fits2 = out_dir + msid + '_short_data.fits'
    fits3 = out_dir + msid + '_week_data.fits'
#
#-- if the starting time and stopping time are given, use them. 
#-- otherwise find from the data for the starting time and today's date -1 for the stopping time
#
    if pstart == 0:
        stday = time.strftime("%Y:%j:00:00:00", time.gmtime())
        stday = Chandra.Time.DateTime(stday).secs - 86400.0     #--- set the ending to the day before
    else:
        stday = pstop 

    mago  = stday - 31536000.0                              #--- a year ago
    mago2 = stday - 604800.0                                #--- a week ago
#
#--- if the fits files already exist, append the data  --------------------
#
    if os.path.isfile(fits):
#
#--- extract data from archive one day at a time
#
        [week_p, short_p, long_p] = process_day_data(msid, dtime, data, glim, step=0)
#
#--- add to the data to the long term fits file
#
        ecf.update_fits_file(fits,  cols, long_p)
#
#--- remove the older data from the short term fits file, then append the new data
#
        remove_old_data(fits2, cols, mago)
        ecf.update_fits_file(fits2, cols, short_p)

#--- remove the older data from the week long data fits file, then append the new data
#
        remove_old_data(fits3, cols, mago2)
        ecf.update_fits_file(fits3, cols, week_p)
#
#--- if the fits files do not exist, create new ones ----------------------
#
    else:
        return False

        if pstart == 0:
            start = 48988799                    #--- 1999:203:00:00:00
            stop  = stday
        else:
            start = pstart
            stop  = pstop
#
#--- one day step; a long term data
#
        [week_p, short_p, long_p] = process_day_data(msid, dtime, data, glim, step=0)
        ecf.create_fits_file(fits, cols, long_p)
#
#--- short term data
#
        mago    = stop - 31536000.0                              #--- a year ago
        short_d =  cut_the_data(short_p, mago)
        ecf.create_fits_file(fits2, cols, short_d)
#
#
#--- week long data
#
#        mago   = stop - 604800.0
#        week_d =  cut_the_data(week_p, mago)
#
#        ecf.create_fits_file(fits3, cols, week_d)
        ecf.create_fits_file(fits3, cols, week_p)

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def cut_the_data(data, cut):

    pos = 0
    for k in range(0, len(data[0])):
        if data[0][k] < cut:
            continue
        else:
            pos = k
            break
    
    save = []
    for k in range(0, len(data)):
        save.append(data[k][pos:])
    
    return save



#-------------------------------------------------------------------------------------------
#-- process_day_data: extract data from the archive and compute the stats           ---
#-------------------------------------------------------------------------------------------

def process_day_data(msid, dtime, data, glim, step = 3600.0):
    """
    extract data from the archive and compute the stats
    input:  msid    --- msid of the data
            glim    --- a list of limit tables
            step    --- interval of the data. defalut: 3600 sec
    output: a list of two lists which contain:
            week_p:
                wtime   --- a list of time in sec from 1998.1.1
                wdata   --- a list of the  mean of each interval
                wmed    --- a list of the median of each interval
                wstd    --- a list of the std of each interval
                wmin    --- a list of the min of each interval
                wmax    --- a list of the max of each interval
                wyl     --- a list of the rate of yellow lower violation
                wyu     --- a list of the rate of yellow upper violation
                wrl     --- a list of the rate of red lower violation
                wru     --- a list of the rate of red upper violation
                wcnt    --- a list of the total data counts
                wyl     --- a list of the lower yellow limits
                wyu     --- a list of the upper yellow limits
                wrl     --- a list of the lower red limits
                wru     --- a list of the upper red limits
            short_p:
                btime   --- a list of time in sec from 1998.1.1
                bdata   --- a list of the  mean of each interval
                bmed    --- a list of the median of each interval
                bstd    --- a list of the std of each interval
                bmin    --- a list of the min of each interval
                bmax    --- a list of the max of each interval
                byl     --- a list of the rate of yellow lower violation
                byu     --- a list of the rate of yellow upper violation
                brl     --- a list of the rate of red lower violation
                bru     --- a list of the rate of red upper violation
                bcnt    --- a list of the total data counts
                byl     --- a list of the lower yellow limits
                byu     --- a list of the upper yellow limits
                brl     --- a list of the lower red limits
                bru     --- a list of the upper red limits
            long_p:
                    --- all in one element list form
                ftime   --- a mid time of the entier extracted data period
                fdata   --- the mean of the entire extracted data 
                fstd    --- the std of the entire extracted data
                fmin    --- the min of the entire extracte data
                fmax    --- the max of the entire extracte data
                ylow    --- the reate of yellow lower violation
                yupper  --- the reate of yellow upper violation
                rlow    --- the reate of red lower violation
                rupper  --- the reate of red upper violation
                tcnt    --- the total counts of the data
                ylow    --- the lower yellow limit
                yup     --- the upper yellow limit
                rlow    --- the lower red limit
                rup     --- the upper red limit
    """
#
#--- 5 min step data
#
    wtime = []
    wdata = []
    wmed  = []
    wstd  = []
    wmin  = []
    wmax  = []
    wyl   = []
    wyu   = []
    wrl   = []
    wru   = []
    wcnt  = []
    step2 = 300
    wstart= dtime[0] - 10.0      #---- set the starting time to 10 sec before the first entry
#
#--- 1 hr step data
#
    btime = []
    bdata = []
    bmed  = []
    bstd  = []
    bmin  = []
    bmax  = []
    byl   = []
    byu   = []
    brl   = []
    bru   = []
    bcnt  = []
    step1 = 3600.0
#
#--- 1 day step data
#
    ftime = []
    fdata = []
    fmed  = []
    fstd  = []
    fmin  = []
    fmax  = []
    fyl   = []
    fyu   = []
    frl   = []
    fru   = []
    fcnt  = []
    step0 = 86400.0

    wsave = []
    vsave = []
    ysave = []

#
#--- extract data from archive
#
    spos0 = 0
    spos1 = 0
    spos2 = 0
    chk0  = 1
    chk1  = 1
    chk2  = 1
    send0 = dtime[spos0] + step0
    send1 = dtime[spos1] + step1
    send2 = dtime[spos2] + step2

    for k in range(0, len(dtime)):
#
#--- 5 min interval
#
        if dtime[k] > wstart:
            if dtime[k] < send2:
                chk2 = 0
            else:
                sdata = numpy.array(data[spos2:k])
                avg   = sdata.mean()
                med   = numpy.median(sdata)
                sig   = sdata.std()
                amin  = sdata.min()
                amax  = sdata.max()
                stime = dtime[spos2 + int(0.5 * (k-spos2))]
                vlimits = find_violation_range(glim, stime)
                [yl, yu, rl, ru, tot] = find_violation_rate(sdata, vlimits)

                wtime.append(stime)
                wdata.append(avg)
                wmed.append(med)
                wstd.append(sig)
                wmin.append(amin)
                wmax.append(amax)
                wyl.append(yl)
                wyu.append(yu)
                wrl.append(rl)
                wru.append(ru)
                wcnt.append(tot)
                wsave.append(vlimits)

                spos2 = k
                send2 = dtime[k] + step2
                chk2  = 1
        else:
            send2 = dtime[spos2] + step2
#
#--- 1 hour interval
#
        if dtime[k] < send1:
            chk1 = 0
        else:
            rdata = numpy.array(data[spos1:k])
            avg   = rdata.mean()
            med   = numpy.median(rdata)
            sig   = rdata.std()
            amin  = rdata.min()
            amax  = rdata.max()
            stime = dtime[spos1 + int(0.5 * (k-spos1))]
            vlimits = find_violation_range(glim, stime)
            [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)

            btime.append(stime)
            bdata.append(avg)
            bmed.append(med)
            bstd.append(sig)
            bmin.append(amin)
            bmax.append(amax)
            byl.append(yl)
            byu.append(yu)
            brl.append(rl)
            bru.append(ru)
            bcnt.append(tot)
            vsave.append(vlimits)

            spos1 = k
            send1 = dtime[k] + step1
            chk1  = 1
#
#--- 1 day interval
#

        if dtime[k] < send0:
            chk0 = 0
        else:
            rdata = numpy.array(data[spos0:k])
            avg   = rdata.mean()
            med   = numpy.median(rdata)
            sig   = rdata.std()
            amin  = rdata.min()
            amax  = rdata.max()
            stime = dtime[spos0 + int(0.5 * (k-spos0))]
            vlimits = find_violation_range(glim, stime)
            [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)
                
            ftime.append(stime)
            fdata.append(avg)
            fmed.append(med)
            fstd.append(sig)
            fmin.append(amin)
            fmax.append(amax)
            fyl.append(yl)
            fyu.append(yu)
            frl.append(rl)
            fru.append(ru)
            fcnt.append(tot)
            ysave.append(vlimits)

            spos0 = k
            send0 = dtime[k] + step0
            chk0  = 1
#
#--- check whether there are any left over; if so add it to the data lists
#
    if chk2 == 0:
        rdata = numpy.array(data[spos2:k])
        avg   = rdata.mean()
        med   = numpy.median(rdata)
        sig   = rdata.std()
        amin  = rdata.min()
        amax  = rdata.max()
        stime = dtime[spos2 + int(0.5 * (k-spos2))]
        vlimits = find_violation_range(glim, stime)
        [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)

        wtime.append(dtime[spos2 + int(0.5 * (k-spos2))])
        wdata.append(avg)
        wmed.append(med)
        wstd.append(sig)
        wmin.append(amin)
        wmax.append(amax)
        wyl.append(yl)
        wyu.append(yu)
        wrl.append(rl)
        wru.append(ru)
        wcnt.append(tot)
        wsave.append(vlimits)

    if chk1 == 0:
        rdata = numpy.array(data[spos1:k])
        avg   = rdata.mean()
        med   = numpy.median(rdata)
        sig   = rdata.std()
        amin  = rdata.min()
        amax  = rdata.max()
        stime = dtime[spos1 + int(0.5 * (k-spos1))]
        vlimits = find_violation_range(glim, stime)
        [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)

        btime.append(dtime[spos1 + int(0.5 * (k-spos1))])
        bdata.append(avg)
        bmed.append(med)
        bstd.append(sig)
        bmin.append(amin)
        bmax.append(amax)
        byl.append(yl)
        byu.append(yu)
        brl.append(rl)
        bru.append(ru)
        bcnt.append(tot)
        vsave.append(vlimits)

    if chk0 == 0:
        rdata = numpy.array(data[spos0:k])
        avg   = rdata.mean()
        med   = numpy.median(rdata)
        sig   = rdata.std()
        amin  = rdata.min()
        amax  = rdata.max()
        stime = dtime[spos0 + int(0.5 * (k-spos0))]
        vlimits = find_violation_range(glim, stime)
        [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)

        ftime.append(dtime[spos0 + int(0.5 * (k-spos0))])
        fdata.append(avg)
        fmed.append(med)
        fstd.append(sig)
        fmin.append(amin)
        fmax.append(amax)
        fyl.append(yl)
        fyu.append(yu)
        frl.append(rl)
        fru.append(ru)
        fcnt.append(tot)
        ysave.append(vlimits)

    week_p  = [wtime, wdata, wmed, wstd, wmin, wmax, wyl, wyu, wrl, wru, wcnt]
    short_p = [btime, bdata, bmed, bstd, bmin, bmax, byl, byu, brl, bru, bcnt]
    long_p  = [ftime, fdata, fmed, fstd, fmin, fmax, fyl, fyu, frl, fru, fcnt]
#
#--- adding limits to the table
#
    vtemp   = [[], [], [], []]
    for k in range(0, len(wsave)):
        for m in range(0, 4):
            vtemp[m].append(wsave[k][m])
    week_p = week_p + vtemp
#
    vtemp   = [[], [], [], []]
    for k in range(0, len(vsave)):
        for m in range(0, 4):
            vtemp[m].append(vsave[k][m])
    short_p = short_p + vtemp
#
    vtemp   = [[], [], [], []]
    for k in range(0, len(ysave)):
        for m in range(0, 4):
            vtemp[m].append(ysave[k][m])
    long_p = long_p + vtemp

    return [week_p, short_p, long_p]


#-------------------------------------------------------------------------------------------
#-- remove_old_data: remove the data older the cut time                                   --
#-------------------------------------------------------------------------------------------

def remove_old_data(fits, cols, cut):
    """
    remove the data older the cut time
    input:  fits    --- fits file name
            cols    --- a list of column names
            cut     --- cut time in seconds from 1998.1.1
    output: updated fits file
    """
    f     = pyfits.open(fits)
    data  = f[1].data
    f.close()
#
#--- find where the cut time
#
    pos   = 0
    dtime = list(data['time'])
    for k in range(0, len(dtime)):
        if dtime[k] >= cut:
            pos = k
            break
#
#--- remove the data before the cut time
#
    udata = []
    for k in range(0, len(cols)):
        udata.append(list(data[cols[k]][pos:]))

    mcf.rm_files(fits)
    ecf.create_fits_file(fits, cols, udata)

#-------------------------------------------------------------------------------------------
#-- find_the_last_entry_time: find the last logged time                                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry_time(yesterday):
    """
    find the last entry date and then make a list of dates up to yesterday
    input:  yesterday   --- date of yesterday in the format of yyyymmdd
    output: otime       --- a list of date in the format of yyyymmdd
    """
#
#--- find the last entry date from the "testfits" file
#
    f = pyfits.open(testfits)
    data = f[1].data
    f.close()
#
#--- find the last time logged and changed to a python standard time insecods
#
    ltime = numpy.max(data['time'])  + 883630800.0
#
#--- find the time of the start of the day
#
    ct    = time.strftime('%Y%m%d', time.gmtime(ltime))
    year  = int(ct[0:4])
    mon   = int(ct[4:6])
    day   = int(ct[6:8])
    dt    = datetime.datetime(year, mon, day)
    ltime = time.mktime(dt.timetuple())
#
#--- set starting day to the next day
#
    ltime = ltime + 86400.0
#
#--- convert yesterday to seconds
#
    yesterday = str(yesterday)
    year  = int(yesterday[0:4])
    mon   = int(yesterday[4:6])
    day   = int(yesterday[6:8])
    dt    = datetime.datetime(year, mon, day)
    stime = time.mktime(dt.timetuple())

    ctime = [ltime]
    while ltime < stime:
        ltime += 86400.0
        ctime.append(ltime)
#
#--- convert the list to yyyymmdd format
#
    otime = []
    for ent in ctime:
        oday =  time.strftime('%Y%m%d', time.gmtime(ent))
        otime.append(oday)

    return otime

#-------------------------------------------------------------------------------------------
#-- find_violation_range: set violation range                                             --
#-------------------------------------------------------------------------------------------

def find_violation_range(glim, time):
    """
    set violation range
    input:  glim    --- a list of lists of violation set [start, stop, yl, yu, rl, ru]
            time    --- time of the violation check
    output: vlimit  --- a four element list of [yl, yu, rl, ru]
    """

    vlimit = [-9.0e9, -9.0e9, 9.0e9, 9.0e9]

    for lim_set in glim:
        start = float(lim_set[0])
        stop  = float(lim_set[1])
        if (time >= start) and (time < stop):
            vlimit = [lim_set[2], lim_set[3], lim_set[4], lim_set[5]]

    return vlimit

#-------------------------------------------------------------------------------------------
#-- find_violation_rate: find rate of yellow, red violations in both lower and upper limits 
#-------------------------------------------------------------------------------------------

def find_violation_rate(carray, limits):
    """
    find rate of yellow, red violations in both lower and upper limits
    input:  carray  --- numpy array of the data
            limits  --- a list of limit [yellow lower, yellow upper, red lower, red upper]
    output: [yl, yu, rl, ru, tot]:  rate of yellow lower
                                    rate of yellow upper
                                    rate of red lower
                                    rate of red upper
                                    totla number of the data
    """
    tot  = len(carray)
    ftot = float(tot)

    yl  = find_num_of_elements(carray, limits[0], side=0)
    yu  = find_num_of_elements(carray, limits[1], side=1)
    rl  = find_num_of_elements(carray, limits[2], side=0)
    ru  = find_num_of_elements(carray, limits[3], side=1)
    yl -= rl
    yu -= ru

    yl /= ftot
    yu /= ftot
    rl /= ftot
    ru /= ftot

    return [yl, yu, rl, ru, tot]

#-------------------------------------------------------------------------------------------
#-- find_num_of_elements: find the numbers of elements above or lower than limit comparing to the total data #
#-------------------------------------------------------------------------------------------

def find_num_of_elements(carray, lim, side=0):
    """
    find the numbers of elements above or lower than limit comparing to the total data #
    input:  carray  --- numpy array of the data
            lim     --- the limit value
            side    --- lower:0 or upper:1 limit
    output: cnt     --- the numbers of the values beyond the limit
    """
#
#--- assume that the huge limit value means that there is no limit
#
    if abs(lim) > 1e6:
        return 0


    try:
        if side == 0:
            out = numpy.where(carray < lim)
        else:
            out = numpy.where(carray > lim)

        try:
            cnt = len(out[0])
        except:
            cnt = 0
    except:
        cnt = 0

    return cnt 

#-------------------------------------------------------------------------------------------
#-- convert_unit_indicator: convert the temperature unit to glim indicator                --
#-------------------------------------------------------------------------------------------

def convert_unit_indicator(cunit):
    """
    convert the temperature unit to glim indicator
    input: cunit    --- degc, degf, or psia
    output: tchk    --- 1, 2, 3 for above. all others will return 0
    """
    
    try:
        cunit = cunit.lower()
        if cunit == 'degc':
            tchk = 1
        elif cunit == 'degf':
            tchk = 2
        elif cunit == 'psia':
            tchk = 3
        else:
            tchk = 0
    except:
        tchk = 0

    return tchk

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 1:
            date = sys.argv[1]
            date.strip()
            update_eph_data(date)
    else:
        update_eph_data()

