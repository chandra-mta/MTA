#!/proj/sot/ska3/flight/bin/python

#####################################################################################################
#                                                                                                   #
#       envelope_common_function.py:    collection of functions used in envelope trending           #
#               ---- this is copied from Envelop trending page                                      #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Jan 22, 2020                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import math
import astropy.io.fits  as pyfits
import os.path
import sqlite3
import unittest
import time
import numpy
import datetime
from time import gmtime, strftime, localtime
import Chandra.Time
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
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
sys.path.append("/data/mta4/Script/Python3.10/MTA")
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import fits_operation           as mfits
#import glimmon_sql_read         as gsr  #---- glimmon database reading
#import read_mta_limits_db       as rmld #---- mta databse reading
#
#--- set a temporary file name
#
import random
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- need a special treatment for the following msids
#
special_list = ['3FAMTRAT', '3FAPSAT', '3FASEAAT', '3SMOTOC', '3SMOTSTL', '3TRMTRAT']
#
#--- other settings
#
NULL   = 'null'
#
#--- month list
#
m_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
#
#--- read mta limit data base as back up limit database
#
#mta_db = rmld.read_mta_limits_db()

ifile  =  house_keeping + 'msid_cross_check_table'
with open(ifile, 'r') as f:
    data  = [line.strip() for line in f.readlines()]

use_mta_db_list = []
for ent in data:
    atemp = re.split('\s+', ent)
    if atemp[1] == 'mta':
        use_mta_db_list.append(atemp[0])

#------------------------------------------------------------------------------------------------------
#-- find_current_stime: find the current time in seconds from 1998.1.1                              ---
#------------------------------------------------------------------------------------------------------

def find_current_stime():
    """
    find the current time in seconds from 1998.1.1
    input:  none
    output: sec1998 --- the current time in seconds from 1998.1.1
    """
    today = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    stime = Chandra.Time.DateTime(today).secs

    return stime

#------------------------------------------------------------------------------------------------------
#-- covertfrom1998sec: convert second from 1998.1.1 to yyyy-mm-ddThh:mm:ss format                    --
#------------------------------------------------------------------------------------------------------

def covertfrom1998sec(stime):
    """
    convert second from 1998.1.1 to yyyy-mm-ddThh:mm:ss format 
    input:  stime   --- second from 1998.1.1
    output: etime   --- time in yyyy-mm-ddThh:mm:ss
    """
    etime = mcf.convert_date_format(stime, ifmt='chandra', ofmt='%Y-%m-%dT%H:%M:%S')

    return etime

#------------------------------------------------------------------------------------------------------
#-- stime_to_frac_year: convert seconds from 1998.1.1 to fractional year format                     ---
#------------------------------------------------------------------------------------------------------

def stime_to_frac_year(stime):
    """
    convert seconds from 1998.1.1 to fractional year format
    input:  stime   --- seconds from 1998.1.1
            etime   --- time in fractinal year;, e.g., 2012.223
    """
    etime = mcf.chandratime_to_fraq_year(stime)

    return etime

#------------------------------------------------------------------------------------------------------
#-- dom_to_stime: convert dom into seconds from 1998.1.1                                            ---
#------------------------------------------------------------------------------------------------------

def dom_to_stime(dom):
    """
    convert dom into seconds from 1998.1.1
    input:  dom     --- dom (day of mission)
    output: stime   --- seconds from 1998.1.1
    """
    [year, ydate] = mcf.dom_to_ydate(dom)
    etime         = str(year) + ':' + str(ydate)
    stime         = mcf.convert_date_format(etime, ifmt='%Y:%j', ofmt='chandra')

    return stime

#------------------------------------------------------------------------------------------------------
#-- current_time: return current time in fractional year                                            ---
#------------------------------------------------------------------------------------------------------

def current_time():
    """
    return current time in fractional year
    input:  none
    output: fyear
    """
    otime = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    stime = Chandra.Time.DateTime(otime).secs
    fyear = mcf.chandratime_to_fraq_year(stime)

    return fyear

#------------------------------------------------------------------------------------------------------
#-- c_to_k: convert the temperature from C to K                                                      --
#------------------------------------------------------------------------------------------------------

def c_to_k(c_temp):
    """
    convert the temperature from C to K
    input:  c_temp  --- temperature in C
    output: k_temp  --- temperature in K
    """
    k_temp = c_temp + 273.15

    return k_temp

#------------------------------------------------------------------------------------------------------
#-- f_to_k: convert the temperature from F to K                                                      --
#------------------------------------------------------------------------------------------------------

def f_to_k(f_temp):
    """
    convert the temperature from F to K
    input:  f_temp  --- temperature in F
    output: k_temp  --- temperature in K
    """
    k_temp = (f_temp -32.0) * 0.55555 + 273.15

    return k_temp

#-----------------------------------------------------------------------------------------------
#-- clean_dir: empty out the directory content                                                --
#-----------------------------------------------------------------------------------------------

def clean_dir(tdir):
    """
    empty out the directory content
    input:  tdir    --- a directory path
    output: tdir if it does not exist before
    """
    chk = 0
    if os.listdir(tdir):
        chk = 1

    if chk == 1:
        cmd   = 'rm -rf ' +  tdir + '/*'
        os.system(cmd)
    else:
        cmd   = 'mkdir ' + tdir
        os.system(cmd)


#------------------------------------------------------------------------------------------------------
#-- read_fits_file: read table fits data and return col names and data                               --
#------------------------------------------------------------------------------------------------------

def read_fits_file(fits):
    """
    read table fits data and return col names and data
    input:  fits    --- fits file name
    output: cols    --- column name
    tbdata  --- table data
                to get a data for a <col>, use:
                data = list(tbdata.field(<col>))
    """
    hdulist = pyfits.open(fits)
#
#--- get column names
#
    cols_in = hdulist[1].columns
    cols    = cols_in.names
#
#--- get data
#
    tbdata  = hdulist[1].data

    hdulist.close()

    return [cols, tbdata]

#-----------------------------------------------------------------------------------
#-- read_fits_col: read  column data from a fits data for given columns          ---
#-----------------------------------------------------------------------------------

def read_fits_col(fits, col_list):
    """
    read  column data from a fits data for given columns
    input:  fits    --- file name
            col_list--- a list of column names to be extracted 
    output: out     --- a list of data arrays corresponding to the column list
    """
    f = pyfits.open(fits)
    data = f[1].data
    f.close()
    
    out = []
    for col in col_list:
        out.append(data[col])
    
    return out
    
#-----------------------------------------------------------------------------------
#-- round_up: round out the value in two digit                                  ----
#-----------------------------------------------------------------------------------

def round_up(val):
    """
    round out the value in two digit
    input:  val --- value
    output: val --- rounded value
    """
    try:
        dist = int(math.log10(abs(val)))
        if dist < -2:
            val *= 10 ** abs(dist)
    except:
        dist = 0

    val = "%3.2f" % (round(val, 2))
    val = float(val)

    if dist < -2:
        val *= 10**(dist)

    return val

#------------------------------------------------------------------------------------------------------
#-- read_unit_list: read unit list and make into a dictionary form                                   --
#------------------------------------------------------------------------------------------------------

def read_unit_list():
    """
    read unit list and make into a dictionary form
    input: none but read from <house_keeping>/unit_list
    output: udict   --- a dictionary of <msid> <---> <unit>
    """
#
#--- read the main unit file and description of msid
#
    ulist = house_keeping + 'unit_list'
    data  = mcf.read_data_file(ulist)

    udict = {}
    ddict = read_description_from_mta_list()

    for ent in data:
        atemp = re.split('\s+', ent)
        try:
            udict[atemp[0].lower()] = atemp[1]
        except:
            pass
#
#--- read dataseeker unit list and replace if they are not same
#
    ulist = house_keeping + 'msid_descriptions'
    data  = mcf.read_data_file(ulist)
    for ent in data:
        if ent[0] == '#':
            continue
        atemp = re.split('#', ent)
        if len(atemp) < 3:
            continue

        msid =atemp[0].strip().lower()
        try:
            test = float(atemp[2])
            tchk = 0
        except:
            tchk = 1
        if tchk == 1:
            if atemp[2] != '':
                udict[msid] =  atemp[2].strip()
        else:
            try:
                test = udict[msid]
            except:
                udict[msid] =  ''
        ddict[msid] = atemp[-1].strip()
#
#--- farther read supplemental lists
#
    ulist = house_keeping + 'unit_supple'
    data  = mcf.read_data_file(ulist)
    for ent in data:
        atemp = re.split('\s+', ent)
        udict[atemp[0]] = atemp[1]

    dlist = house_keeping + 'description_supple'
    data  = mcf.read_data_file(dlist)
    for ent in data:
        atemp = re.split('\:\:', ent)
        msid  = atemp[0].strip()
        descr = atemp[1].strip()
        ddict[msid] = descr

    return [udict, ddict]

#------------------------------------------------------------------------------------------------------
#-- read_description_from_mta_list: read descriptions of msid from mta limit table                   --
#------------------------------------------------------------------------------------------------------

def read_description_from_mta_list():
    """
    read descriptions of msid from mta limit table
    input:  none but read from <house_keeping>/mta_limits.db
    output: mdict   --- a dictionary of msid<--->description
    """
    mfile =  mlim_dir  + 'op_limits.db'
    data  = mcf.read_data_file(mfile)

    mdict = {}
    prev  = ''
    for ent in data:
        if ent == '':
            continue 
        if ent[0] == '#':
            continue
        atemp = re.split('\s+', ent)

        if atemp[0] == prev:
            continue
        prev  = atemp[0]

        msid  = atemp[0].lower()
        atemp = re.split('#', ent)
        try:
            btemp = re.split('\s+', atemp[1])
#
#--- quite often junk got in because the format of each line is not clean
#--- remove these junks from the end of the line
#
            discription = atemp[1].replace(btemp[-1],"")
            if btemp[-2] in ['K', 'V', 'AMP', 'RATE', 'CNT', 'uA', 'RPS', 'C', 'mm', 'CURRENT', 'STEP']:
                discription = discription.replace(btemp[-2],"")
    
            mdict[msid] = discription
        except:
            pass

    return mdict

#------------------------------------------------------------------------------------------------------
#-- set_limit_list: read upper and lower yellow and red limits for each period                       --
#------------------------------------------------------------------------------------------------------

#def set_limit_list(msid):
#    """
#    read upper and lower yellow and red limits for each period
#    input:  msid--- msid
#    output: l_list  --- a list of list of [<start time>, <stop time>, <yellow min>, <yellow max>, <red min>, <red max>]
#    """
#    [udict, ddict]  = read_unit_list()
#    tchk = 0
#    try:
#        unit = udict[msid.lower()]
#        if unit.lower() in ['k', 'degc']:
#            tchk = 1
#        elif unit.lower() == 'degf':
#            tchk = 2
#        elif unit.lower() == 'psia':
#            tchk = 3
#        elif msid[-1].lower()  == 't':
#            tchk = 1
#    except:
#        if msid[-1].lower()  == 't':
#            tchk = 1
##
##--- primary limit database is directly from glimmon database. however there are those
##--- only aviailable in mta op_limit.db or prefer to use mta limits. if that is the
##--- the case, use mta_db. 
##
#    if msid in use_mta_db_list:
#        l_list = []
#    else:
#        l_list = gsr.read_glimmon(msid, tchk)
#
#    if len(l_list) == 0:
#        try:
#            l_list = mta_db[msid]
#        except:
#            l_list = []
##
##--- if there is no limt given, set dummy limits
##
#    if len(l_list) == 0:
#        tstart = 31536000                               #---- 1999:001:00:00:00
#        tstop  = find_current_stime()
#        l_list = [[tstart, tstop, -998, 998, -999, 999]]
#
#        return l_list
#
#    cleaned = []
#    for alist in l_list:
#        if alist[0] == alist[1]:
#            continue
#        else:
#            cleaned.append(alist)
#    
#    cleaned2 = []
#    alist = cleaned[0]
#    for k in range(1, len(cleaned)):
#        blist = cleaned[k]
#        if (alist[2] == blist[2]) and (alist[3] == blist[3]) and (alist[4] == blist[4]) and (alist[5] == blist[5]):
#            alist[1] = blist[1]
#        else:
#            cleaned2.append(alist)
#            alist = blist
#
#    cleaned2.append(alist)
#
#    return cleaned2
#

#------------------------------------------------------------------------------------------------------
#-- modify_slope_dicimal: adjust the format of the slope and error print out                        ---
#------------------------------------------------------------------------------------------------------

def modify_slope_dicimal(val, err):
    """
    adjust the format of the slope and error print out
    input:  val     --- slope value
            err     --- slope error value
    output: line    --- slope expression
    """

    aval  = '%2.2e' %(val)
    atemp = re.split('e', str(aval))
    fval  = atemp[0]
    pwrp  = int(float(atemp[1]))

    if err in [999 , 998,  99.9]:
        err = 'na'
    else:
        err  /= (10.0**pwrp)
        err   = '%2.2f'  % round(err, 2)

    line  = '(' + fval + '+/-' + err + ')e' + str(pwrp)

    return line

#-------------------------------------------------------------------------------------------
#-- get_limit: find the limit lists for the msid  --
#-------------------------------------------------------------------------------------------

def get_limit(msid, tchk, mta_db, mta_cross):
    """
    find the limit lists for the msid
    input:  msid--- msid
    tchk--- whether temp conversion needed 0: no/1: degc/2: degf/3: pcs
    mta_db  --- a dictionary of mta msid <---> limist
    mta_corss   --- mta msid and sql msid cross check table
    output: glim--- a list of lists of lmits. innter lists are:
    [start, stop, yl, yu, rl, ru]
    """
    
    try:
        mchk = mta_cross[msid]
    except:
        mchk = 0
    
    if mchk == 'mta':
        try:
            glim = mta_db[msid]
        except:
            glim = [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]]
    
    else:
        try:
            out   = gsr.read_glimmon(mchk, tchk)
            test  = str(mchk[-2] + mchk[-1])
            if test.lower() == 'tc':
                glim = []
                for ent in out:
                    for k in range(2,6):
                        ent[k] -= 273.15
                glim.append(ent)
            else:
                glim = out
         
        except:
            glim = [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]]
    
    return glim

#-------------------------------------------------------------------------------------------
#-- read_mta_database: read the mta limit database--
#-------------------------------------------------------------------------------------------

def read_mta_database():
    """
    read the mta limit database
    input:  none, but read from /data/mta4/MTA/data/op_limits/op_limits.db
    output: mta_db  --- dictionary of msid <--> a list of lists of limits
    the inner list is [start, stop, yl, yu, rl, ru]
    """
    tmin = 0
    tmax = 3218831995
    ifile = limit_dir + 'Limit_data/op_limits_new.db'
    data = mcf.read_data_file(ifile)
    
    mta_db = {}
    prev   = ''
    save   = []
    for ent in data:
        if len(ent) == 0:
            continue
        if ent[0] == '#':
            continue
    
        atemp = re.split('\s+', ent)
        msid  = atemp[0].lower()
    
        try:
            out  = mta_db[msid]
            yl   = float(atemp[1])
            yr   = float(atemp[2])
            rl   = float(atemp[3])
            ru   = float(atemp[4])
            ts   = float(atemp[7])
            olim = [ts, tmax, yl, yr, rl, ru]
            out[-1][1] = ts
            out.append(olim)
            mta_db[msid] = out
        except:
            yl   = float(atemp[1])
            yr   = float(atemp[2])
            rl   = float(atemp[3])
            ru   = float(atemp[4])
            ts   = float(atemp[7])
            olim = [ts, tmax, yl, yr, rl, ru]
            out  = [olim]
            mta_db[msid] = out
    
    return mta_db

#-------------------------------------------------------------------------------------------
#-- read_cross_check_table: read the mta msid and sql database msid cross table  ---
#-------------------------------------------------------------------------------------------

def read_cross_check_table():
    """
    read the mta msid and sql database msid cross table
    input: none but read from <house_keeping>/msid_cross_check_table
    output: mta_cross   --- a dictionary of mta msid and sql database msid
    note: if there is no correspondece, it will return "mta"
    """
    
    ifile = house_keeping + 'msid_cross_check_table'
    data = mcf.read_data_file(ifile)
    
    mta_cross = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        mta_cross[atemp[0]] = atemp[1]
    
    return mta_cross

#-------------------------------------------------------------------------------------------
#-- update_fits_file: update fits file                                                    --
#-------------------------------------------------------------------------------------------

def update_fits_file(fits, cols, cdata, tcut=0):
    """
    update fits file
    input:  fits    --- fits file name
            cols    --- a list of column names
            cdata   --- a list of lists of data values
            tcut    --- a time to cut the data; default: 0 --- no cut
    output: updated fits file
    """
    f = pyfits.open(fits)
    data  = f[1].data
    f.close()
    
    udata = []
    chk   = 0
    for k in range(0, len(cols)):
        try:
            nlist   = list(data[cols[k]]) + list(cdata[k])
            udata.append(numpy.array(nlist))
        except:
            chk = 1
            break

    if chk == 0:
        if tcut > 0:
            cdata = []
            cind = [udata[0] > tcut]
            for k in range(0, len(cols)):
                cdata.append(udata[k][cind])
        else:
            cdata = udata
            
        try:
            create_fits_file(fits, cols, cdata)
        except:
            pass

#-------------------------------------------------------------------------------------------
#-- create_fits_file: create a new fits file for a given data set                         --
#-------------------------------------------------------------------------------------------

def create_fits_file(fits, cols, cdata):
    """
    create a new fits file for a given data set
    input:  fits    --- fits file name
            cols    --- a list of column names
            cdata   --- a list of lists of data values
    output: newly created fits file "fits"
    """
    dlist = []
    for k in range(0, len(cols)):
        aent = numpy.array(cdata[k])
        try:
            dcol = pyfits.Column(name=cols[k], format='F',   array=aent)
        except:
            dcol = pyfits.Column(name=cols[k], format='10A', array=aent)
        dlist.append(dcol)
    
    dcols = pyfits.ColDefs(dlist)
    tbhdu = pyfits.BinTableHDU.from_columns(dcols)
    
    mcf.rm_files(fits)
    tbhdu.writeto(fits)

#-------------------------------------------------------------------------------------------
#--check_zip_possible: at the year change, gzip the data of year before                   --
#-------------------------------------------------------------------------------------------

def check_zip_possible(outdir):
    """
    at the year change, gzip the data of year before
    input:  outdir: the locations where the data are saved
    output: gzipped fits file from the last year
    """
    yday  = float(time.strftime("%j", time.gmtime()))
    
    if (yday > 1) and (yday < 5):
        year  = int(float(time.strftime("%Y", time.gmtime()))) - 1
    
        cmd   = 'ls ' + outdir + '*_' + str(year) + '.fits* > ' + zspace
        os.system(cmd)
        data = mcf.read_data_file(zspace, remove=1)
     
        for ent in data:
            mc = re.search('.gz', ent)
            if mc is not None:
                continue
            else:
                cmd = 'gzip -f ' + ent
                os.system(cmd)

#-----------------------------------------------------------------------------------------
#-- find_data_collecting_period: find data collection time period from the last entry   --
#-----------------------------------------------------------------------------------------

def find_data_collecting_period(testdir, testf):
    """
    find data collection time period from the last entry
    input:  testdir --- the directory path to the data
            testf   --- test fits file name 
    output: tstart  --- the data collecting starting time in seconds from 1998.1.1
            tstop   --- the data colleciton stopping time in seconds from 1998.1.1
            year    --- the year of the file updated
    """
#
#--- find the last entry
#
    cmd  = 'ls ' + testdir + '/' + testf + ' > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)
    test = data[-1]
    
    if os.path.isfile(test):
        f = pyfits.open(test)
        data  = f[1].data
        f.close()
        dtime = data['time']
        tstart = numpy.max(dtime)
    else:
        tstart = 0.0
#
#--- find yesterday's date
#
    year  = time.strftime("%Y", time.gmtime())
    tstop = time.strftime("%Y:%j:00:00:00", time.gmtime())
    tstop = Chandra.Time.DateTime(tstop).secs - 86400.0

    return [tstart, tstop, year]

#-------------------------------------------------------------------------------------------
#-- remove_duplicate: remove duplicated entry by time (the first entry)                   --
#-------------------------------------------------------------------------------------------

def remove_duplicate(cdata):
    """
    remove duplicated entry by time (the first entry)
    input:  cdata   --- a list of lists; the first entry must be time stamp
    output: ndat--- a cealn list of lists
    """
    clen  = len(cdata)  #--- the numbers of the lists in the list
    dlen  = len(cdata[0])   #--- the numbers of elements in each list
    tdict = {}
    tlist = []
#
#--- make a dictionary as time as a key
#
    for k in range(0, dlen):
        tdat = []
        for m in range(0, clen):
            tdat.append(cdata[m][k])
    
    tdict[cdata[0][k]] = tdat
    tlist.append(cdata[0][k])
#
#--- select the uniqe time stamps
#
    tset  = set(tlist)
    tlist = list(tset)
    tlist.sort()
#
#--- create a uniqu data set
#
    ndata = []
    for m in range(0, clen):
        ndata.append([])
    
    for ent in tlist:
        out = tdict[ent]
        for  m in range(0, clen):
            ndata[m].append(out[m])
    
    return ndata

#-------------------------------------------------------------------------------------------
#-- convert_unit_indicator: convert the temperature unit to glim indicator                --
#-------------------------------------------------------------------------------------------

def convert_unit_indicator(cunit):
    """
    convert the temperature unit to glim indicator
    input: cunit--- degc, degf, or psia
    output: tchk--- 1, 2, 3 for above. all others will return 0
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
#-- get_basic_info_dict: extract basic information dict and lists                         --
#-------------------------------------------------------------------------------------------

def get_basic_info_dict():
    """
    extract basic information dict and lists
    input:  none
    output: udict   --- dictionary of msid <---> unit
            ddict   --- dictionary of misd <---> discription
            mta_db  --- mta limit database dictonary
            mta_cross   --- dictionary of msid <---> alias
    """
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = read_unit_list()
#
#--- read mta database
#
    mta_db = read_mta_database()

#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = read_cross_check_table()


    return [udict, ddict, mta_db, mta_cross]

#-------------------------------------------------------------------------------------------
#-- find_the_last_entry_time: find the last logged time                                   --
#-------------------------------------------------------------------------------------------

def find_the_last_entry_time(fits):
    """
    find the last logged time
    input:  fits    --- fits file name
    output: ctime   --- the last logged time
    """
    f = pyfits.open(fits)
    data = f[1].data
    f.close()

    ctime = numpy.max(data['time'])

    return ctime

#-------------------------------------------------------------------------------------------
#-- create_date_list_to_yestaday: find the last entry date and then make a list of dates up to yesterday
#-------------------------------------------------------------------------------------------

def create_date_list_to_yestaday(testfits, yesterday=''):
    """
    find the last entry date and then make a list of dates up to yesterday
    input:  testfits    --- a fits file to be tested
            yesterday   --- date of yesterday in the format of yyyymmdd
    output: otime   --- a list of date in the format of yyyymmdd
    """

    try:
        test = float(yesterday)
        chk = 1
    except:
        chk = 0
    
    if chk == 0:
        out = time.strftime('%Y:%j:00:00:00', time.gmtime())
        yesterday = Chandra.Time.DateTime(out).secs - 86400.0
#
    ltime = find_the_last_entry_time(testfits)

    out = mcf.convert_date_format(ltime, ifmt='chandra', ofmt='%Y:%j:00:00:00')
    out = Chandra.Time.DateTime(out).secs

    t_list = [out]
    ntime = out + 86400.0
    while ntime <=  yesterday:
        t_list.append(ntime)
        ntime += 87400.0

    otime = []
    for ent in t_list:
        out = mcf.convert_date_format(ent, ifmt='chandra', ofmt='%Y%m%d')
        otime.append(out)
    
    return otime

#----------------------------------------------------------------------------------
#-- check_time_format: return time in Chandra time                               --
#----------------------------------------------------------------------------------

def check_time_format(intime):
    """
    return time in Chandra time
    input:  intime  --- time in <yyyy>:<ddd>:<hh>:<mm>:<ss> or <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss> or chandra time
    output: time in chandra time (seconds from 1998.1.1)
    """
    mc1 = re.search('-', intime)
    mc2 = re.search(':', intime)
#
#--- it is already chandra format
#
    if mcf.chkNumeric(intime):
        return int(float(intime))
#
#--- time in <yyyy>-<mm>-<dd>T<hh>:<mm>:<ss>
#
    elif mc1 is not None:
        mc2 = re.search('T', intime)
        if mc2 is not None:
            stime = mcf.convert_date_format(intime, ifmt='%Y-%m-%d:%H:%M:%S', ofmt='chandra')
        else:
            stime = mcf.convert_date_format(intime, ifmt='%Y-%m-%d', ofmt='chandra')
    
        return stime
#
#--- time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
#
    elif mc2 is not None:
    
        return Chandra.Time.DateTime(intime).secs

#-----------------------------------------------------------------------------------
#-- combine_fits: combine fits files in the list  --
#-----------------------------------------------------------------------------------

def combine_fits(flist, outname):
    """
    combine fits files in the list
    input:  flist   --- a list of fits file names
            outname --- a outputfits file name
    output: outname --- a combined fits file
    """
    mcf.rm_files(outname)
    cmd = 'mv ' + flist[0] + ' ' + outname
    os.system(cmd)
    
    for k in range(1, len(flist)):
        try:
            mfits.appendFitsTable(outname, flist[k], 'temp.fits')
        except:
            continue
     
        cmd = 'mv temp.fits ' + outname
        os.system(cmd)
        cmd = 'rm -f ' + flist[k]
        os.system(cmd)
    
    cmd = 'rm -rf *fits.gz'
    os.system(cmd)
    
    return outname

    
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
    
def create_use_mta_db_list():

    ifile =  house_keeping + 'msid_cross_check_table'
    data  = mcf.read_data_file(ifile)

    use_mta_db_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        if atemp[1] == 'mta':
            use_mta_db_list.append(atemp[0])

    return use_mta_db_list

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------

    def test_find_current_stime(self):

        sec1998 = find_current_stime()
        print("current time: " + str(sec1998))


#------------------------------------------------------------

    def test_covertfrom1998sec(self):

        stime = 119305230
        out   = covertfrom1998sec(stime)

        self.assertEquals(out, '2001-10-12T21:20:30')

#------------------------------------------------------------
    
    def test_dom_to_stime(self):

        dom   = 0
        stime = dom_to_stime(dom)
        self.assertEquals(stime, 48902400.0)

        dom   = 10
        stime = dom_to_stime(dom)
        self.assertEquals(stime, 49766400.0)


#------------------------------------------------------------

    def test_data_seek(self):

        comp  = [147.6113739, 147.6113739, 147.6113739, 147.6113739, 147.6113739]

        msid  = '1crbt'
        name  = msid + '_avg'
        start = 536457596           #---- 2015:001:00:00:00
        stop  = 536543996           #---- 2015:002:00:00:00

        data_seeker(start, stop, msid)

        fits = 'temp_out.fits'
        [col, tbdata] = read_fits_file(fits)
        data = tbdata.field(name)

        test = []
        for k in range(0, 5):
            test.append(round(data[k], 7))

        self.assertEquals(test, comp)

#------------------------------------------------------------

    def test_stime_to_frac_year(self):

        stime  = 549590396
        fyear  = stime_to_frac_year(stime)

        print("I AM HERE: " + str(fyear) + '<--->2916,419')


#------------------------------------------------------------

    def test_read_unit_list(self):

        [mdict, ddict] = read_unit_list()

        msid = '1crbt'
        self.assertEquals(ddict[msid], 'COLD RADIATOR TEMP. B')
        self.assertEquals(mdict[msid], 'DEGC')

        msid = 'aorwspd2'
        self.assertEquals(mdict[msid], 'RPS')

        msid = '1deamztc'
        self.assertEquals(mdict[msid], 'C')

#------------------------------------------------------------

    def test_set_limit_list(self):

        msid = '1cbat'
        out = set_limit_list(msid)
        self.assertEquals(out[0], [0, 119305230, 202.65, 223.15, 197.65, 312.65])


        #msid = 'oobthr04'
        #out = set_limit_list(msid)
        #print("/tI AM HERE OOBTHR04: " + str(out))

        msid = 'pm1thv1t'
        out = set_limit_list(msid)
        print("/tI AM HERE PM1THV1T: " + str(out))

#------------------------------------------------------------
    
    def test_round_up(self):

        val = 1.2342
        out = round_up(val)
        self.assertEquals(out, 1.23)

        val = 0.000134
        out = round_up(val)
        self.assertEquals(out, 0.00013)
        

#-----------------------------------------------------------------------------------


if __name__ == "__main__":

#    unittest.main()
    msid = 'pm1thv1t'
    out = set_limit_list(msid)
    for ent in out:
        print(str(ent))

