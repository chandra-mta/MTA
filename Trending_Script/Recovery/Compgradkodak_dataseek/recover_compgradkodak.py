#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#            recover_compgradkodak.py: recover compgradkodak_fits from beginning        #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Apr 06, 2017                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits

#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param ', shell='tcsh')
#
#--- add the path to mta python code directory
#
sys.path.append('/data/mta/Script/Python_script2.7/')
sys.path.append('./')

import mta_common_functions     as mcf
import convertTimeFormat        as tcnv
import recover_suppl_functions  as rsf
#
#--- define column names of compgradkodak.fits (header part only)
#
gradkodak = ['hrmaavg',   'hrmacav',    'hrmaxgrd',      'hrmaradgrd', 'obaavg',    'obaconeavg', \
             'obaaxgrd',  'obadiagrad', 'fwblkhdt',      'aftblkhdt',  'mzobacone', 'pzobacone',  \
             'hrmarange', 'tfterange',  'hrmastrutrnge', 'scstrutrnge']

#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

hpass = '/data/mta/Script/Month/Config/house_keeping/loginfile'

#------------------------------------------------------------------------
#-- create_compgradkodak_fits: recover compgradkodak_fits from beginning 
#------------------------------------------------------------------------

def create_compgradkodak_fits(start_year, start_yday, stop_year, stop_yday, pfits=''):
    """
    recover compgradkodak_fits from beginning
    input:  start_year  --- the year of the starting date
            start_yday  --- the ydate of the starting date
            stop_year   --- the year of the stopping date
            stop_yday   --- the ydate of the sopttping date
                if start_year is not given (e.g.""), then it will re-compute the entire period
            pfits       --- the previous fits file; the new data will be appended
                            if this is not given, the new result will be written on  compgradkodak.fits
    output: compgradkodak.fits
    """
#
#--- find this year
#
    if start_year == '':
        today      = time.localtime()
        start_year = 1999
        start_yday = 203
        stop_year  = today.tm_year
        stop_yday  = today.tm_yday
#
#--- create an empty list for each data
#
    otime  = []
    for ent in gradkodak:
        exec "%s_avg = []" % (ent)
        exec "%s_dev = []" % (ent)
#
#--- dom start from yday 203 of 1999
#
    chk  = 0
    dom  = set_start_dom(start_year, start_yday)
#
#--- go though one day at a time from 1999.07.21 to today
#
    for year in range(start_year, (stop_year+1)):
        if tcnv.isLeapYear(year) == 1:
            yend = 367
        else:
            yend = 366

        for yday in range(1, yend):

            if year == start_year and yday < start_yday:
                continue 
            if year == stop_year  and yday >= stop_yday:
                chk = 1
                break

            print "DATE: " + str(year) + '<-->' + str(yday)
            dom += 1

            cyday = str(int(yday))
            if yday < 10:
                cyday = '00' + cyday
            elif yday < 100:
                cyday = '0'  + cyday
#
#--- set time span for a day
#
            start  = str(year) + ':' + cyday + ':00:00:00'
            stop   = str(year) + ':' + cyday + ':23:59:59'
#
#--- run dataseeker and extract data. return a list of lists of each data
#
            try:
                e_data = extract_data(start, stop)
            except:
                continue
#
#--- compute daily avg  and std for each column of compgradkodak
#
            try:
                d_data = convert_avg(e_data)
            except:
                continue

            print "DOM: " + str(dom)
            otime.append(dom)
#
#--- first sep data are avg and from sep+1 to the end are std
#
            sep = len(gradkodak)
            for k in range(0, sep):
                data = d_data[k]
                dev  = d_data[k+sep]
                exec "%s_avg.append(%s)" % (gradkodak[k], str(data))
                exec "%s_dev.append(%s)" % (gradkodak[k], str(dev))

        if chk == 1:
            break
#
#--- create fits file
#
    col_save = []
    col      = pyfits.Column(name="time", format='F', array=otime)
    col_save.append(col)

    for nam in gradkodak:
        mname = nam + '_avg'
        dname = nam + '_dev'
        exec "marray = numpy.array(%s_avg)" % (nam)
        exec "darray = numpy.array(%s_dev)" % (nam)
        col = pyfits.Column(name=mname, format='F', array=marray)
        col_save.append(col)

        col = pyfits.Column(name=dname, format='F', array=darray)
        col_save.append(col)

    cols  = pyfits.ColDefs(col_save)
    tbhdu = pyfits.BinTableHDU.from_columns(cols)


    if pfits == "":
        if os.path.isfile('./compgradkodak.fits'):
            os.system(' mv compgradkodak.fits compgradkodak.fits~')

        tbhdu.writeto('compgradkodak.fits')
    else:
        tbhdu.writeto('add_part.fits')
        rsf.fits_append(pfits, 'add_part.fits', 'temp_out.fits')

        if os.path.isfile('./compgradkodak.fits'):
            os.system(' mv compgradkodak.fits compgradkodak.fits~')

        os.system('mv -f temp_out.fits compgradkodak.fits')

#------------------------------------------------------------------------
#-- set_start_dom: finding starting dom date                          ---
#------------------------------------------------------------------------

def set_start_dom(start_year, start_yday):
    """
    finding starting dom date
    input:  start_year  --- the year that the new dataset starts
            start_yday  --- the ydate that the new dataset starts
    output: dom         --- dom of the starting date
    """

    dom = 0
    don = 202   #---- this is not correct  as real definition of dom but for now use this
    for year in range(1999, (start_year+1)):

        if tcnv.isLeapYear(year) == 1:
            yend = 367
        else:
            yend = 366

        for yday in range(1, yend):

            if year == 1999 and yday < 203:
                continue 
            elif year == start_year  and yday >= start_yday:
                break
            else:
                dom += 1

    return dom


#------------------------------------------------------------------------
#-- convert_avg: compute avg and std of each column entry in gradkodak for the given data set
#------------------------------------------------------------------------

def convert_avg(input_list):
    """
    compute avg and std of each column entry in gradkodak for the given data set
    input: input_list   --- a list of lists. each sub-list contains dataseeker output for "_avg"
                            each entry is a dictionary which contains avg, std, min, max 
    output: a list of avg and std of each columns of gradkodak. first len(gradkodak)
            are avg of the columns and the next len(gradkodak) are std.
    """
#
#--- open the list of lists
#
    (_4rt575t_avg, _4rt700t_avg, _4rt701t_avg, _4rt702t_avg, _4rt703t_avg, _4rt704t_avg,\
     _4rt705t_avg, _4rt706t_avg, _4rt707t_avg, _4rt708t_avg, _4rt709t_avg, _4rt710t_avg,\
     _4rt711t_avg, \
     ohrthr02_avg, ohrthr03_avg, ohrthr04_avg, ohrthr05_avg, ohrthr06_avg, ohrthr07_avg, \
     ohrthr08_avg, ohrthr09_avg, ohrthr10_avg, ohrthr11_avg, ohrthr12_avg, ohrthr13_avg, \
     ohrthr14_avg, ohrthr15_avg, ohrthr17_avg, ohrthr21_avg, ohrthr22_avg, ohrthr23_avg, \
     ohrthr24_avg, ohrthr25_avg, ohrthr26_avg, ohrthr27_avg, ohrthr28_avg, ohrthr29_avg, \
     ohrthr30_avg, ohrthr31_avg, ohrthr33_avg, ohrthr34_avg, ohrthr35_avg, ohrthr36_avg, \
     ohrthr37_avg, ohrthr39_avg, ohrthr40_avg, ohrthr42_avg, ohrthr44_avg, ohrthr45_avg, \
     ohrthr46_avg, ohrthr47_avg, ohrthr49_avg, ohrthr50_avg, ohrthr51_avg, ohrthr52_avg, \
     ohrthr53_avg, ohrthr54_avg, ohrthr55_avg, ohrthr56_avg, ohrthr57_avg, ohrthr58_avg, \
     ohrthr60_avg, ohrthr61_avg, \
     oobthr02_avg, oobthr03_avg, oobthr04_avg, oobthr05_avg, oobthr06_avg, oobthr07_avg, \
     oobthr08_avg, oobthr09_avg, oobthr10_avg, oobthr11_avg, oobthr12_avg, oobthr13_avg, \
     oobthr14_avg, oobthr15_avg, oobthr17_avg, oobthr18_avg, oobthr19_avg, oobthr20_avg, \
     oobthr21_avg, oobthr22_avg, oobthr23_avg, oobthr24_avg, oobthr25_avg, oobthr26_avg, \
     oobthr27_avg, oobthr28_avg, oobthr29_avg, oobthr30_avg, oobthr31_avg, oobthr33_avg, \
     oobthr34_avg, oobthr35_avg, oobthr36_avg, oobthr37_avg, oobthr38_avg, oobthr39_avg, \
     oobthr40_avg, oobthr41_avg, oobthr42_avg, oobthr43_avg, oobthr44_avg, oobthr45_avg, \
     oobthr48_avg, oobthr49_avg, oobthr50_avg, oobthr51_avg, oobthr52_avg, oobthr53_avg, \
     oobthr54_avg, oobthr55_avg, oobthr56_avg, oobthr57_avg, oobthr58_avg, oobthr59_avg, \
     oobthr60_avg, oobthr61_avg, oobthr62_avg, oobthr63_avg \
     ) = input_list
#
#--- get avg and std of the enter entries of the given list
#
    hrmarange_list = range(2,14) + range(21,27) + [28, 29,30,33, 36, 37] + range(44,49) + range(49, 54) +[55, 56]
    [hrmaavg, hrmadev]  = get_avg_std('ohrthr', hrmarange_list, input_list)

#------------
    
    hrmacs_list = range(6, 16) + [17, 25, 26, 29, 30, 31] + range(33, 38) + [39, 40] + range(50, 59) + [60, 61]
    [hrmacavg, hrmacdev] = get_avg_std('ohrthr', hrmacs_list, input_list)

#-----------
    
    hrmaxgrad_list1   = [10, 11, 34, 35, 55, 56]
    [hrmaxgrd1, xxx]  = get_avg_std('ohrthr', hrmaxgrad_list1, input_list)

    hrmaxgrad_list2   = [12, 13, 35, 37, 57, 58]
    [hrmaxgrd2, xxx]  = get_avg_std('ohrthr', hrmaxgrad_list2, input_list)
    hrmaxgrd          = hrmaxgrd1 - hrmaxgrd2
#
#--- compute std separately for the case two outputs are add/subtracted after computed
#
    dev_list = hrmaxgrad_list1 + hrmaxgrad_list2
    [z, hrmaxgrd_dev] = get_avg_std('ohrthr', dev_list, input_list)
    
#-----------

    hrmarad1grd_list    = [8, 31, 33, 52]
    [hrmarad1grd, xxx]  = get_avg_std('ohrthr', hrmarad1grd_list, input_list)
    hrmarad2grd_list    = [9, 53, 54]
    [hrmarad2grd, xxx]  = get_avg_std('ohrthr', hrmarad2grd_list, input_list)
    hrmaradgrd          = hrmarad1grd - hrmarad2grd   

    dev_list            = hrmarad1grd_list + hrmarad2grd_list
    [z, hrmaradgrd_dev] = get_avg_std('ohrthr', dev_list, input_list)

#-----------

    obaavg_list      = range(8, 33) + range(33, 42) + [44, 45]
    [obaavg, obadev] = get_avg_std('oobthr', obaavg_list, input_list)

#-----------

    obacone_list           = range(8, 16) + range(17, 31) + range(57, 62)
    [obaconeavg, obacone_dev] = get_avg_std('oobthr', obacone_list, input_list)

#-----------
#
#--- for the case two different header entries are needed;
#
    fwblkhd_list1     = [62, 63]
    fwblkhd_list2     = [700, 712]
    [fwblkhdt, fwblkhdt_dev] = get_avg_std('oobthr', fwblkhd_list1, input_list, '_4rt', fwblkhd_list2, tail='t' )

    aftblkhdt_list    = [31, 33, 34]
    [aftblkhdt, aftblkhdt_dev] = get_avg_std('oobthr', aftblkhdt_list, input_list)
    
    obaaxgrd          = fwblkhdt - aftblkhdt   

    s_list            = fwblkhd_list1 + aftblkhdt_list
    [z, obaaxgrd_dev] = get_avg_std('oobthr', s_list, input_list, '_4rt', fwblkhd_list2, tail='t' )
    
#-----------

    mzoba_list1   = [8, 19, 25, 31, 57, 60]
    mzoba_list2   = [575]
    [mzobacone, mzobacone_dev]  = get_avg_std('oobthr', mzoba_list1, input_list, '_4rt', mzoba_list2, tail='t')

    pzoba_list    = [13, 22, 23, 28, 29, 61]
    [pzobacone, pzobacone_dev] = get_avg_std('oobthr', pzoba_list, input_list)
    
    obadiagrad    = mzobacone - pzobacone   


    d_list = mzoba_list1 + pzoba_list
    [z, obadiagrad_dev]  = get_avg_std('oobthr', d_list, input_list, '_4rt', mzoba_list2, tail='t')

#-----------
#
#--- compute the range of the data
#
    clist = range(2,14) + range(21,28) + [29,30,33, 36, 37, 42] + range(45,54) +[55, 56]
    [hrmarange, hrmarange_dev]         = get_range('ohrthr', clist, input_list)

    clist = range(2, 8)
    [hrmastrutrnge, hrmastrutrnge_dev] = get_range('oobthr', clist, input_list)

    clist = range(42, 45)
    [tfterange, tfterange_dev]         = get_range('oobthr', clist, input_list)

    clist = range(49, 55)
    [scstrutrnge, scstrutrnge_dev]     = get_range('oobthr', clist, input_list)
    

    out = []
    for  val in [hrmaavg, hrmacavg, hrmaxgrd, hrmaradgrd, obaavg, obaconeavg, obaaxgrd, obadiagrad, fwblkhdt, \
            aftblkhdt, mzobacone, pzobacone, hrmarange, tfterange, hrmastrutrnge, scstrutrnge, \
            hrmadev, hrmacdev, hrmaxgrd_dev, hrmaradgrd_dev, obadev, obacone_dev, obaaxgrd_dev, obadiagrad_dev, fwblkhdt_dev, \
            aftblkhdt_dev, mzobacone_dev, pzobacone_dev, hrmarange_dev, tfterange_dev, hrmastrutrnge_dev, scstrutrnge_dev]:

        if mcf.chkNumeric(val) == False  or str(val) == 'nan':
            val = -99.0

        out.append(val)

    return out

#-------------------------------------------------------------------------------------------
#-- get_avg_std: compute avg and std the given data list                                 ---
#-------------------------------------------------------------------------------------------

def get_avg_std(mhead, clist, input_list, mhead2 ='', clist2='',  tail=''):
    """
    compute avg and std the given data list
    input:  mhead   --- msid head part, e.g., 'ohrthr', 'oobthr', '_4rt'
            clist   --- a list of numbers of the data sets e.g. [3, 4, 5] for ohrthr03_avg, ohrthr04_avg...
            input_list  --- a list of the lists of the data
            mhead2  --- the second head part. default: "" means there is no second entry
            clist2  --- the second list of numbers. default: ""
            tail    --- the tail indicator. this is needed for _4rt case (e.g.  _4rt701t_avg and "t" is the tail)
    output: [avg, std]  --- average and std of the combined entries of the given list. 
    """

    (_4rt575t_avg, _4rt700t_avg, _4rt701t_avg, _4rt702t_avg, _4rt703t_avg, _4rt704t_avg,\
     _4rt705t_avg, _4rt706t_avg, _4rt707t_avg, _4rt708t_avg, _4rt709t_avg, _4rt710t_avg,\
     _4rt711t_avg, \
     ohrthr02_avg, ohrthr03_avg, ohrthr04_avg, ohrthr05_avg, ohrthr06_avg, ohrthr07_avg, \
     ohrthr08_avg, ohrthr09_avg, ohrthr10_avg, ohrthr11_avg, ohrthr12_avg, ohrthr13_avg, \
     ohrthr14_avg, ohrthr15_avg, ohrthr17_avg, ohrthr21_avg, ohrthr22_avg, ohrthr23_avg, \
     ohrthr24_avg, ohrthr25_avg, ohrthr26_avg, ohrthr27_avg, ohrthr28_avg, ohrthr29_avg, \
     ohrthr30_avg, ohrthr31_avg, ohrthr33_avg, ohrthr34_avg, ohrthr35_avg, ohrthr36_avg, \
     ohrthr37_avg, ohrthr39_avg, ohrthr40_avg, ohrthr42_avg, ohrthr44_avg, ohrthr45_avg, \
     ohrthr46_avg, ohrthr47_avg, ohrthr49_avg, ohrthr50_avg, ohrthr51_avg, ohrthr52_avg, \
     ohrthr53_avg, ohrthr54_avg, ohrthr55_avg, ohrthr56_avg, ohrthr57_avg, ohrthr58_avg, \
     ohrthr60_avg, ohrthr61_avg, \
     oobthr02_avg, oobthr03_avg, oobthr04_avg, oobthr05_avg, oobthr06_avg, oobthr07_avg, \
     oobthr08_avg, oobthr09_avg, oobthr10_avg, oobthr11_avg, oobthr12_avg, oobthr13_avg, \
     oobthr14_avg, oobthr15_avg, oobthr17_avg, oobthr18_avg, oobthr19_avg, oobthr20_avg, \
     oobthr21_avg, oobthr22_avg, oobthr23_avg, oobthr24_avg, oobthr25_avg, oobthr26_avg, \
     oobthr27_avg, oobthr28_avg, oobthr29_avg, oobthr30_avg, oobthr31_avg, oobthr33_avg, \
     oobthr34_avg, oobthr35_avg, oobthr36_avg, oobthr37_avg, oobthr38_avg, oobthr39_avg, \
     oobthr40_avg, oobthr41_avg, oobthr42_avg, oobthr43_avg, oobthr44_avg, oobthr45_avg, \
     oobthr48_avg, oobthr49_avg, oobthr50_avg, oobthr51_avg, oobthr52_avg, oobthr53_avg, \
     oobthr54_avg, oobthr55_avg, oobthr56_avg, oobthr57_avg, oobthr58_avg, oobthr59_avg, \
     oobthr60_avg, oobthr61_avg, oobthr62_avg, oobthr63_avg \
     ) = input_list

#
#--- save values in the list
#
    alist   = []
    for k in clist:
        ck = str(k)
        if k < 10:
            ck = '0' + ck
#
#--- the data are save in a dictionary form which has avg, std, min, and max
#
        try:
            exec 'dlist = %s%s%s_avg' % (mhead, ck, tail) 
        except:
            dlist = []
        try:
            alist = alist + list(dlist)
        except:
            pass
#
#--- for the case when the different mhead entry are requested
#
    if clist2 != '':
        for k in clist2:
            ck = str(k)
            if k < 10:
                ck = '0' + ck
            try:
                exec 'dlist = %s%s%s_avg' % (mhead2, ck, tail) 
            except:
                dlist= []
            try:
                alist = alist + list(dlist)
            except:
                pass
#
#--- make sure that all entries are float values
#
    blist = []
    for ent in alist:
        if ent == "":
            continue
        try:
            blist.append(float(ent))
        except:
            pass

    avg = numpy.mean(blist)
    std = numpy.std(blist)

    return [avg, std]


#-------------------------------------------------------------------------------------------
#-- get_range: get avg and std of data range for given group                              --
#-------------------------------------------------------------------------------------------

def get_range(mshead, clist, input_list):
    """
    get avg and std of data range for given group
    input:  mshead  --- the head part of the data group. e.g., ohrthr
            clist   --- the list of each data, e.g., 03 for ohrthr03_avg
            input_list  --- a list of lists of data
    output:  [avg, std]
    """
#
#--- open the data
#
    (_4rt575t_avg, _4rt700t_avg, _4rt701t_avg, _4rt702t_avg, _4rt703t_avg, _4rt704t_avg,\
     _4rt705t_avg, _4rt706t_avg, _4rt707t_avg, _4rt708t_avg, _4rt709t_avg, _4rt710t_avg,\
     _4rt711t_avg, \
     ohrthr02_avg, ohrthr03_avg, ohrthr04_avg, ohrthr05_avg, ohrthr06_avg, ohrthr07_avg, \
     ohrthr08_avg, ohrthr09_avg, ohrthr10_avg, ohrthr11_avg, ohrthr12_avg, ohrthr13_avg, \
     ohrthr14_avg, ohrthr15_avg, ohrthr17_avg, ohrthr21_avg, ohrthr22_avg, ohrthr23_avg, \
     ohrthr24_avg, ohrthr25_avg, ohrthr26_avg, ohrthr27_avg, ohrthr28_avg, ohrthr29_avg, \
     ohrthr30_avg, ohrthr31_avg, ohrthr33_avg, ohrthr34_avg, ohrthr35_avg, ohrthr36_avg, \
     ohrthr37_avg, ohrthr39_avg, ohrthr40_avg, ohrthr42_avg, ohrthr44_avg, ohrthr45_avg, \
     ohrthr46_avg, ohrthr47_avg, ohrthr49_avg, ohrthr50_avg, ohrthr51_avg, ohrthr52_avg, \
     ohrthr53_avg, ohrthr54_avg, ohrthr55_avg, ohrthr56_avg, ohrthr57_avg, ohrthr58_avg, \
     ohrthr60_avg, ohrthr61_avg, \
     oobthr02_avg, oobthr03_avg, oobthr04_avg, oobthr05_avg, oobthr06_avg, oobthr07_avg, \
     oobthr08_avg, oobthr09_avg, oobthr10_avg, oobthr11_avg, oobthr12_avg, oobthr13_avg, \
     oobthr14_avg, oobthr15_avg, oobthr17_avg, oobthr18_avg, oobthr19_avg, oobthr20_avg, \
     oobthr21_avg, oobthr22_avg, oobthr23_avg, oobthr24_avg, oobthr25_avg, oobthr26_avg, \
     oobthr27_avg, oobthr28_avg, oobthr29_avg, oobthr30_avg, oobthr31_avg, oobthr33_avg, \
     oobthr34_avg, oobthr35_avg, oobthr36_avg, oobthr37_avg, oobthr38_avg, oobthr39_avg, \
     oobthr40_avg, oobthr41_avg, oobthr42_avg, oobthr43_avg, oobthr44_avg, oobthr45_avg, \
     oobthr48_avg, oobthr49_avg, oobthr50_avg, oobthr51_avg, oobthr52_avg, oobthr53_avg, \
     oobthr54_avg, oobthr55_avg, oobthr56_avg, oobthr57_avg, oobthr58_avg, oobthr59_avg, \
     oobthr60_avg, oobthr61_avg, oobthr62_avg, oobthr63_avg \
    ) = input_list


    range_list = []
    min_list   = []
    max_list   = []
#
#--- find min and max of each data period (usually a day) of each group
#
    for n in clist:

        cn = str(n)
        if n < 10:
            cn = '0' + cn
#
#--- finding min and max
#
        try: 
            exec  'vlist = %s%s_avg' % (mshead, cn)

            try:
                val1 = min(vlist)
                val2 = max(vlist)
            except:
                val1 = 0.0
                val2 = 0.0

            val1 = float(val1)
            val2 = float(val2)
            if val1 == 0.0:
                val1 =  -999.0
            if val2 == 0.0:
                val2 =  -999.0
        except:
            val1 = -999.0
            val2 = -999.0
#
#--- get the interval and save
#
        if val1 != -999.0 and val2 != -999.0:
            diff = val2 - val1
            range_list.append(diff)
            min_list.append(val1)
            max_list.append(val2)

#
#--- find the avg and std of the period
#
    avg = numpy.mean(range_list)
    std = numpy.std(range_list)
    rng = max(max_list) - min(min_list)

    #return [avg, std]
    return [rng, std]


#-------------------------------------------------------------------------------------------
#-- extract_data: extract needed data for a given time period from dataseeker             --
#-------------------------------------------------------------------------------------------

def extract_data(start, stop):
    """
    extract needed data for a given time period from dataseeker
    input:  start   --- starting time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stopping time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    output: resuts  --- a list of lists of dataseeker output
    """
#
#--- there are three distinctive data groups
#
    obfwdbulkhead =\
    ('_4rt575t_avg', '_4rt700t_avg', '_4rt701t_avg', '_4rt702t_avg', '_4rt703t_avg', '_4rt704t_avg',\
     '_4rt705t_avg', '_4rt706t_avg', '_4rt707t_avg', '_4rt708t_avg', '_4rt709t_avg', '_4rt710t_avg',\
     '_4rt711t_avg')
     
    hrmaheaters = \
    ('ohrthr02_avg', 'ohrthr03_avg', 'ohrthr04_avg', 'ohrthr05_avg', 'ohrthr06_avg', 'ohrthr07_avg', \
     'ohrthr08_avg', 'ohrthr09_avg', 'ohrthr10_avg', 'ohrthr11_avg', 'ohrthr12_avg', 'ohrthr13_avg', \
     'ohrthr14_avg', 'ohrthr15_avg', 'ohrthr17_avg', 'ohrthr21_avg', 'ohrthr22_avg', 'ohrthr23_avg', \
     'ohrthr24_avg', 'ohrthr25_avg', 'ohrthr26_avg', 'ohrthr27_avg', 'ohrthr28_avg', 'ohrthr29_avg', \
     'ohrthr30_avg', 'ohrthr31_avg', 'ohrthr33_avg', 'ohrthr34_avg', 'ohrthr35_avg', 'ohrthr36_avg', \
     'ohrthr37_avg', 'ohrthr39_avg', 'ohrthr40_avg', 'ohrthr42_avg', 'ohrthr44_avg', 'ohrthr45_avg', \
     'ohrthr46_avg', 'ohrthr47_avg', 'ohrthr49_avg', 'ohrthr50_avg', 'ohrthr51_avg', 'ohrthr52_avg', \
     'ohrthr53_avg', 'ohrthr54_avg', 'ohrthr55_avg', 'ohrthr56_avg', 'ohrthr57_avg', 'ohrthr58_avg', \
     'ohrthr60_avg', 'ohrthr61_avg')

    obaheaters = \
    ('oobthr02_avg', 'oobthr03_avg', 'oobthr04_avg', 'oobthr05_avg', 'oobthr06_avg', 'oobthr07_avg', \
     'oobthr08_avg', 'oobthr09_avg', 'oobthr10_avg', 'oobthr11_avg', 'oobthr12_avg', 'oobthr13_avg', \
     'oobthr14_avg', 'oobthr15_avg', 'oobthr17_avg', 'oobthr18_avg', 'oobthr19_avg', 'oobthr20_avg', \
     'oobthr21_avg', 'oobthr22_avg', 'oobthr23_avg', 'oobthr24_avg', 'oobthr25_avg', 'oobthr26_avg', \
     'oobthr27_avg', 'oobthr28_avg', 'oobthr29_avg', 'oobthr30_avg', 'oobthr31_avg', 'oobthr33_avg', \
     'oobthr34_avg', 'oobthr35_avg', 'oobthr36_avg', 'oobthr37_avg', 'oobthr38_avg', 'oobthr39_avg', \
     'oobthr40_avg', 'oobthr41_avg', 'oobthr42_avg', 'oobthr43_avg', 'oobthr44_avg', 'oobthr45_avg', \
     'oobthr48_avg', 'oobthr49_avg', 'oobthr50_avg', 'oobthr51_avg', 'oobthr52_avg', 'oobthr53_avg', \
     'oobthr54_avg', 'oobthr55_avg', 'oobthr56_avg', 'oobthr57_avg', 'oobthr58_avg', 'oobthr59_avg', \
     'oobthr60_avg', 'oobthr61_avg', 'oobthr62_avg', 'oobthr63_avg') 
#
#--- call dataseeker function for each group, then compute stats which are saved in dict form
#
    obfwdbulkhead_data = runDataseeker(start, stop, obfwdbulkhead)

    hrmaheaters_data   = runDataseeker(start, stop, hrmaheaters)

    obaheaters_data    = runDataseeker(start, stop, obaheaters)
#
#--- combine the lists and return
#
    results = obfwdbulkhead_data + hrmaheaters_data + obaheaters_data

    return results

#-------------------------------------------------------------------------------------------
#-- runDataseeker: extract data using dataseeker                                          --
#-------------------------------------------------------------------------------------------

def runDataseeker(start, stop, col_list):
    """
    extract data using dataseeker
    input:  start   --- starting time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stopping time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            col_list    --- a list of column names
    output: data_list   --- a list of data. dataseeker return avg of 5 min interval
    """

    clen  = len(col_list)
    step  = int(clen / 3)
    begin = [0, step, 2*step]
    end   = [step, 2*step, clen]

    data_list = []
    for m in range(0, 3):
        cols  =  ''
        for col in col_list[begin[m]:end[m]]:
            if col[0] != '_':
                col = '_' + col
            mc = re.search('oobthr', col)
            if mc is not None:
                col = 'mtatel..obaheaters_avg.' + col
    
            if cols != '':
                cols  = cols + ',' + col
            else:
                cols = col
    
        if not os.path.exists('./param'):
            os.system('mkdir param')
    
        if not os.path.exists('./test'):
            os.system('touch test')
    
        cmd = ' /home/ascds/DS.release/bin/dataseeker.pl '
        cmd = cmd + 'infile=test  outfile=./ztemp.fits  search_crit="columns=' + cols + '  timestart=' + str(start)
        cmd = cmd + ' timestop=' + str(stop) +'" loginFile='+ hpass + ' clobber="yes"'
    
        run_ascds(cmd)
    
        hdulist = pyfits.open('ztemp.fits')
        tbdata  = hdulist[1].data
        for col in col_list[begin[m]:end[m]]:
            if col[0] == '_':
                col = col[1:]
            data = tbdata[col]
            data_list.append(data)
    
        mcf.rm_file('./ztemp.fits')

    return data_list

#-------------------------------------------------------------------------------------------
#-- run_ascds: run the command in ascds environment                                       --
#-------------------------------------------------------------------------------------------

def run_ascds(cmd, clean =0):
    """
    run the command in ascds environment
    input:  cmd --- command line
    clean   --- if 1, it also resets parameters default: 0
    output: command results
    """
    if clean == 1:
        acmd = '/usr/bin/env PERL5LIB=""  source /home/mta/bin/reset_param ;' + cmd
    else:
        acmd = '/usr/bin/env PERL5LIB=""  ' + cmd

    try:
        bash(acmd, env=ascdsenv)
    except:
        try:
            bash(acmd, env=ascdsenv)
        except:
            pass

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) >= 5:
        start_year = sys.argv[1]
        start_year = int(float(start_year))
        start_yday = sys.argv[2]
        start_yday = int(float(start_yday))
        stop_year  = sys.argv[3]
        stop_year  = int(float(stop_year))
        stop_yday  = sys.argv[4]
        stop_yday  = int(float(stop_yday))
        pfits      = ''
        if len(sys.argv) >= 6:
            pfits = sys.argv[5]             #--- existing table fits file to be appended
    else:
        start_year = ''
        start_yday = ''
        stop_year  = ''
        stop_yday  = ''
        pfits      = ''

    create_compgradkodak_fits(start_year, start_yday, stop_year, stop_yday, pfits)
