"""
**envelope_common_function.py**:    collection of functions used in envelope trending (copied from Envelope trending page)

:Author: t. isobe (tisobe@cfa.harvard.edu)
:Maintainer: w. aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Feb 24, 2026

"""

import os
import sys
import re
import math
import astropy.io.fits  as pyfits
import os.path
import unittest
import time
from datetime import timedelta
import numpy
from cxotime import CxoTime
from pathlib import Path
import glob
#
# --- Define Directory Pathing
#
_MODULE_PATH = Path(__file__).resolve()
HOUSE_KEEPING = _MODULE_PATH.parent / 'house_keeping' #: Module-level house_keeping pathing independent of os.getcwd()
MTA_DIR = "/data/mta/Script/Python3.13/MTA"
LIMIT_DESCRIPTION_DIR = "/data/mta4/MTA/data/op_limits"
LIMIT_DATA_DIR = "/data/mta/Script/MSID_limit/Trend_limit_data/Limit_data"

#
#--- append path to supplemental modules directory
#
sys.path.append(MTA_DIR)
#
import mta_common_functions as mcf  # type: ignore # noqa: E402
import fits_operation as mfits  # type: ignore # noqa: E402
#import glimmon_sql_read         as gsr  #---- glimmon database reading

#------------------------------------------------------------------------------------------------------
#-- find_current_stime: find the current time in seconds from 1998.1.1                              ---
#------------------------------------------------------------------------------------------------------

def find_current_stime():
    """
    find the current time in seconds from 1998.1.1
    input:  none
    output: sec1998 --- the current time in seconds from 1998.1.1
    """
    stime = CxoTime().secs

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
    etime = CxoTime(stime).datetime.strftime('%Y-%m-%dT%H:%M:%S') # type: ignore

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
    stime = (CxoTime("1999:203:00:00:05") + timedelta(days=dom)).secs

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
    stime = CxoTime().secs
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
    cols_in = hdulist[1].columns # type: ignore
    cols    = cols_in.names
#
#--- get data
#
    tbdata  = hdulist[1].data # type: ignore

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
    data = f[1].data # type: ignore
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

    val = f"{round(val, 2):3.2f}"
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
    with open(f"{HOUSE_KEEPING}/unit_list") as f:
        data = [line.strip() for line in f.readlines()]

    udict = {}
    ddict = read_description_from_mta_list()

    for ent in data:
        atemp = re.split(r'\s+', ent)
        try:
            udict[atemp[0].lower()] = atemp[1]
        except:
            pass
#
#--- read dataseeker unit list and replace if they are not same
#
    with open(f"{HOUSE_KEEPING}/msid_descriptions") as f:
        data = [line.strip() for line in f.readlines()]

    for ent in data:
        if ent[0] == '#':
            continue
        atemp = re.split('#', ent)
        if len(atemp) < 3:
            continue

        msid =atemp[0].strip().lower()
        try:
            float(atemp[2])
            tchk = 0
        except:
            tchk = 1
        if tchk == 1:
            if atemp[2] != '':
                udict[msid] =  atemp[2].strip()
        else:
            if msid not in udict.keys():
                udict[msid] =  ''
        ddict[msid] = atemp[-1].strip()
#
#--- farther read supplemental lists
#
    with open(f"{HOUSE_KEEPING}/unit_supple") as f:
        data = [line.strip() for line in f.readlines()]
    for ent in data:
        atemp = re.split(r'\s+', ent)
        udict[atemp[0]] = atemp[1]

    with open(f"{HOUSE_KEEPING}/description_supple") as f:
        data = [line.strip() for line in f.readlines()]

    for ent in data:
        atemp = re.split(r'\:\:', ent)
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
    with open(f"{LIMIT_DESCRIPTION_DIR}/op_limits.db") as f:
        data = [line.strip() for line in f.readlines()]

    mdict = {}
    prev  = ''
    for ent in data:
        if ent == '':
            continue 
        if ent[0] == '#':
            continue
        atemp = re.split(r'\s+', ent)

        if atemp[0] == prev:
            continue
        prev  = atemp[0]

        msid  = atemp[0].lower()
        atemp = re.split('#', ent)
        try:
            btemp = re.split(r'\s+', atemp[1])
#
#--- quite often junk got in because the format of each line is not clean
#--- remove these junks from the end of the line
#
            description = atemp[1].replace(btemp[-1],"")
            if btemp[-2] in ['K', 'V', 'AMP', 'RATE', 'CNT', 'uA', 'RPS', 'C', 'mm', 'CURRENT', 'STEP']:
                description = description.replace(btemp[-2],"")
            mdict[msid] = description.strip()
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

    aval  = f'{val:2.2e}'
    atemp = re.split('e', str(aval))
    fval  = atemp[0]
    pwrp  = int(float(atemp[1]))

    if err in [999 , 998,  99.9]:
        err = 'na'
    else:
        err  /= (10.0**pwrp)
        err   = f'{round(err, 2):2.2f}'

    line = f"({fval}+/-{err})e{pwrp}"

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
    mta_cross   --- mta msid and sql msid cross check table
    output: glim--- a list of lists of lmits. innter lists are:
    [start, stop, yl, yu, rl, ru]
    """

    mchk = mta_cross.get(msid, 0)
    if mchk == 'mta':
        glim = mta_db.get(msid, [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]])
    
    else:
        try:
            out   = gsr.read_glimmon(mchk, tchk)
            test  = str(mchk[-2] + mchk[-1]) # type: ignore
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
    tmax = 3218831995
    with open(f"{LIMIT_DATA_DIR}/op_limits_new.db") as f:
        data = [line.strip() for line in f.readlines()]
    
    mta_db = {}
    for ent in data:
        if len(ent) == 0 or ent.startswith('#'):
            continue
        atemp = ent.split()
        msid  = atemp[0].lower()

        #: Parse file entry
        yl   = float(atemp[1])
        yr   = float(atemp[2])
        rl   = float(atemp[3])
        ru   = float(atemp[4])
        ts   = float(atemp[7])
        olim = [ts, tmax, yl, yr, rl, ru]
        #: Check if already recorded a limit entry for this msid, if so, update the stop time of the last entry and append the new entry
        if msid in mta_db.keys():
            mta_db[msid][-1][1] = ts
            #: Append new entry
            mta_db[msid].append(olim)
        else:
            #: Create new entry
            mta_db[msid] = [olim]
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
    
    with open(f"{HOUSE_KEEPING}/msid_cross_check_table") as f:
        data = [line.strip() for line in f.readlines()]
    mta_cross = {}
    for ent in data:
        atemp = re.split(r'\s+', ent)
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
    data  = f[1].data # type: ignore
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

    os.remove(fits)
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
    
        searchpattern = os.path.join(outdir, f'*_{year}.fits*')
        data = glob.glob(searchpattern)
     
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

    searchpattern = os.path.join(testdir, testf)
    data = glob.glob(searchpattern)

    test = data[-1]
    
    if os.path.isfile(test):
        f = pyfits.open(test)
        data  = f[1].data # type: ignore
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
    tstop = CxoTime(tstop).secs - 86400.0 # type: ignore

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
    if isinstance(cunit,str):
        cunit = cunit.lower()
        tchk = { 'degc': 1, 'degf': 2, 'psia': 3 }.get(cunit, 0)
    else:
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
            ddict   --- dictionary of misd <---> description
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
    data = f[1].data # type: ignore
    f.close()

    ctime = numpy.max(data['time'])

    return ctime

#-------------------------------------------------------------------------------------------
#-- create_date_list_to_yesterday: find the last entry date and then make a list of dates up to yesterday
#-------------------------------------------------------------------------------------------

def create_date_list_to_yesterday(testfits, yesterday=''):
    """
    find the last entry date and then make a list of dates up to yesterday
    input:  testfits    --- a fits file to be tested
            yesterday   --- date of yesterday in the format of yyyymmdd
    output: otime   --- a list of date in the format of yyyymmdd
    """

    try:
        float(yesterday)
        chk = 1
    except:
        chk = 0
    
    if chk == 0:
        out = time.strftime('%Y:%j:00:00:00', time.gmtime())
        yesterday = CxoTime(out).secs - 86400.0 # type: ignore
#
    ltime = find_the_last_entry_time(testfits)
    out = CxoTime(ltime)
    out -= timedelta(hours=out.datetime.hour, # type: ignore
                     minutes=out.datetime.minute, # type: ignore
                     seconds=out.datetime.second) # type: ignore
    out = out.secs

    t_list = [out]
    ntime = out + 86400.0 # type: ignore
    while ntime <= yesterday: # type: ignore
        t_list.append(ntime)
        ntime += 87400.0

    otime = []
    for ent in t_list:
        otime.append(
            CxoTime(ent).datetime.strftime('%Y%m%d') # type: ignore
            )
    
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
            #: TODO Remake as CxoTime
            stime = mcf.convert_date_format(intime, ifmt='%Y-%m-%d:%H:%M:%S', ofmt='chandra')
        else:
            stime = mcf.convert_date_format(intime, ifmt='%Y-%m-%d', ofmt='chandra')
    
        return stime
#
#--- time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
#
    elif mc2 is not None:
    
        return CxoTime(intime).secs

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
    os.remove(outname)
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
    
def create_use_mta_db_list():

    with open(f"{HOUSE_KEEPING}/msid_cross_check_table") as f:
        data = [line.strip() for line in f.readlines()]
    use_mta_db_list = []
    for ent in data:
        atemp = re.split(r'\s+', ent)
        if atemp[1] == 'mta':
            use_mta_db_list.append(atemp[0])

    return use_mta_db_list

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------
    @unittest.skip("Depends on current time")
    def test_find_current_stime(self):
        #: Used in MTA limit trends
        sec1998 = find_current_stime()
        print("current time: " + str(sec1998))
#------------------------------------------------------------
    @unittest.expectedFailure
    @unittest.skip("Not used in MTA limit trends")
    def test_covertfrom1998sec(self):
        #: Not used in MTA limit trends
        stime = 119305230
        out   = covertfrom1998sec(stime)

        self.assertEqual(out, '2001-10-12T21:20:30')
#------------------------------------------------------------
    def test_stime_to_frac_year(self):
        #: Used in MTA limit trends
        stime  = 0
        fyear  = stime_to_frac_year(stime)
        self.assertAlmostEqual(fyear,1998.002737,places=5)
#------------------------------------------------------------
    @unittest.expectedFailure
    @unittest.skip("Not used in MTA limit trends")
    def test_dom_to_stime(self):
        #: Not used in MTA limit trends
        dom   = 0
        stime = dom_to_stime(dom)
        self.assertEqual(stime, 48902400.0)

        dom   = 10
        stime = dom_to_stime(dom)
        self.assertEqual(stime, 49766400.0)
#------------------------------------------------------------
    @unittest.skip("Depends on current time")
    def test_current_time(self):
        #: Used in MTA limit trends
        pass
#------------------------------------------------------------
    @unittest.skip("Simple function. Skip")
    def test_c_to_k(self):
        #: Not used in MTA limit trends
        pass
#------------------------------------------------------------
    @unittest.skip("Simple function. Skip")
    def test_f_to_k(self):
        #: Used in unit modification in glimmon_sql_read only. Can refactor. 
        pass
#------------------------------------------------------------
    @unittest.skip("Not used in MTA limit trends")
    def test_clean_dir(self):
        #: Not used in MTA limit trends
        pass
#------------------------------------------------------------
    def test_read_fits_file(self):
        #: Used in MTA limit trends
        legacy_file = "/proj/sot/ska/data/aca_bgd_mon/2001-01/kalman.fits"
        [cols, tbdata] = read_fits_file(legacy_file)
        self.assertEqual(cols, ['kalman', 'time'])
        self.assertEqual(tbdata[0][0], 1)
        self.assertEqual(tbdata[0][1], 94694112.198475)
#------------------------------------------------------------
    def test_read_fits_col(self):
        #: Used in MTA limit trends
        legacy_file = "/proj/sot/ska/data/aca_bgd_mon/2001-01/kalman.fits"
        cols = read_fits_col(legacy_file, col_list=['kalman'])
        self.assertEqual(cols[0][0], 1)
        pass
#------------------------------------------------------------
    @unittest.expectedFailure
    @unittest.skip("Implementation to be replaced with string formatting")
    def test_round_up(self):
        #: Used in MTA limit trends. Implementation to be replaced with string formatting
        val = 1.2342
        out = round_up(val)
        self.assertEqual(out, 1.23)

        val = 0.000134
        out = round_up(val)
        self.assertEqual(out, 0.00013)
#------------------------------------------------------------
    def test_read_unit_list(self):
        #: Used in MTA limit trends.
        [mdict, ddict] = read_unit_list()

        msid = '1crbt'
        self.assertEqual(mdict[msid], 'K')

        msid = 'aorwspd2'
        self.assertEqual(mdict[msid], 'RPS')

        msid = '1deamztc'
        self.assertEqual(mdict[msid], 'C')
#------------------------------------------------------------
    def test_read_description_from_mta_list(self):
        #: Used in read unit list only. Which is used elsehwere.
        ddict = read_description_from_mta_list()

        msid = '1crbt'
        self.assertEqual(ddict[msid], 'COLD RADIATOR TEMP. B')

        msid = 'aorwspd2'
        self.assertEqual(ddict[msid], 'REACTION WHEEL RATES')

        msid = '1deamztc'
        self.assertEqual(ddict[msid], 'DEA -Z PANEL TEMP')
#------------------------------------------------------------
    @unittest.skip("Commented Out")
    def test_set_limit_list(self):
        #: Used in HTMl generation. Could refactor to use get_limit instead?
        msid = '1cbat'
        out = set_limit_list(msid)
        self.assertEqual(out[0], [0, 119305230, 202.65, 223.15, 197.65, 312.65])


        msid = 'pm1thv1t'
        out = set_limit_list(msid)
        print("/tI AM HERE PM1THV1T: " + str(out))
#------------------------------------------------------------
    def test_modify_slope_dicimal(self):
        #: Used in MTA limit trends.
        val = 1.23456789e-5
        err = 0.0000123456789
        out = modify_slope_dicimal(val, err)
        self.assertEqual(out, '(1.23+/-1.23)e-5')
#------------------------------------------------------------
    @unittest.skip("Not using glimmon_sql_read")
    def test_get_limit(self):
        #: Used in MTA limit trends. But needs glimmon_sql_read.
        pass
#------------------------------------------------------------
    def test_read_mta_database(self):
        #: Used in MTA limit trends.
        mta_db = read_mta_database()
        self.assertEqual(mta_db['1cbat'][0], [31536000.0, 119305230.0, 202.65, 223.15, 197.65, 312.65])
#------------------------------------------------------------
    def test_read_cross_check_table(self):
        #: Used in MTA limit trends.
        mta_cross = read_cross_check_table()
        self.assertEqual(mta_cross['1cbat'], '1cbat')
        self.assertEqual(mta_cross['hrmastrutrnge'], 'mta')
#------------------------------------------------------------
    @unittest.skip("Live file writing required")
    def test_update_fits_file(self):
        #; Used in MTA limit trends.
        pass
#------------------------------------------------------------
    @unittest.skip("Live file writing required")
    def test_create_fits_file(self):
        #: Used in MTA limit trends.
        pass
#------------------------------------------------------------
    @unittest.skip("Directory Content Dependent")
    def test_check_zip_possible(self):
        #: Used in MTA limit trends.
        pass
#------------------------------------------------------------
    @unittest.skip("Directory Content Dependent")
    def test_find_data_collecting_period(self):
        #: Used in MTA limit trends.
        pass
#------------------------------------------------------------
    @unittest.skip("Not used in MTA limit trends")
    def test_remove_duplicate(self):
        #: Not used in MTA limit trends.
        pass
#------------------------------------------------------------
    def test_convert_unit_indicator(self):
        #: Used in MTA limit trends. Also recreated in MTA limit trends.
        self.assertEqual(convert_unit_indicator('degc'), 1)
        self.assertEqual(convert_unit_indicator('degf'), 2)
        self.assertEqual(convert_unit_indicator('psia'), 3)
        self.assertEqual(convert_unit_indicator('k'), 0)
#------------------------------------------------------------
    def test_get_basic_info_dict(self):
        #: Used in MTA limit trends.
        [udict, ddict, mta_db, mta_cross] = get_basic_info_dict()
        self.assertEqual(udict['1cbat'], 'K')
        self.assertEqual(ddict['1cbat'], 'CAMERA BODY TEMP. A')
        self.assertEqual(mta_db['1cbat'][0], [31536000.0, 119305230.0, 202.65, 223.15, 197.65, 312.65])
        self.assertEqual(mta_cross['1cbat'], '1cbat')
#------------------------------------------------------------
    def test_find_the_last_entry_time(self):
        #: Used in MTA limit trends. Also recreated in MTA limit trends.
        legacy_file = "/proj/sot/ska/data/aca_bgd_mon/2001-01/kalman.fits"
        last_time = find_the_last_entry_time(legacy_file)
        self.assertEqual(last_time, 97378497.08159013)
#------------------------------------------------------------
    def test_create_date_list_to_yesterday(self):
        #: Used in MTA limit trends.
        legacy_file = "/proj/sot/ska/data/aca_bgd_mon/2001-01/kalman.fits"
        otime = create_date_list_to_yesterday(legacy_file, yesterday=CxoTime('2001-02-05').secs) # type: ignore
        self.assertEqual(otime, ['20010201', '20010202', '20010203', '20010204'])
#------------------------------------------------------------
    @unittest.skip("Implementation to be replaced with CxoTime")
    def test_check_time_format(self):
        #: Used in MTA limit trends. Can refactor all usage into CxoTime instead.
        out = check_time_format('2001-10-12T21:20:30')
        self.assertEqual(out, 119305230)

        out = check_time_format('2001-10-12')
        self.assertEqual(out, 119298240)

        out = check_time_format('2001:285:21:20:30')
        self.assertEqual(out, 119305230)

        out = check_time_format('119305230')
        self.assertEqual(out, 119305230)
#------------------------------------------------------------
    @unittest.skip("Not used in MTA limit trends")
    def test_combine_fits(self):
        #: Not used in MTA limit trends.
        pass
#------------------------------------------------------------
    @unittest.skip("Not used in MTA limit trends")
    def test_create_use_mta_db_list(self):
        #: Not used in MTA limit trends.
        use_mta_db_list = create_use_mta_db_list()
        self.assertIn('hrmastrutrnge', use_mta_db_list)

if __name__ == "__main__":

    unittest.main()