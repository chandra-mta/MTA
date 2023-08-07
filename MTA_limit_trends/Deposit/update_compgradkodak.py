#!/proj/sot/ska3/flight/bin/python

#####################################################################################    
#                                                                                   #
#           update_compgradkodak.py: update compgradkodak related datasets          #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Feb 02, 2021                                               #
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
import getpass
#
#--- reading directory list
#
#path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
path = '/data/mta4/testDEA/Scripts/house_keeping/dir_list'
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
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------------------
#-- update_compgradkodak: update compgradkodak related data sets                          --
#-------------------------------------------------------------------------------------------

def update_compgradkodak():
    """
    update compgradkodak related data sets
    input: none
    output: <out_dir>/<msid>_fill_data_<year>.fits
    """
    t_file  = 'obaavg_full_data_*.fits*'
    out_dir = deposit_dir + '/Comp_save/Compgradkodak/'
    
    [tstart, tstop, year] = ecf.find_data_collecting_period(out_dir, t_file)
    
    print("Period: " + str(tstart) + '<-->' + str(tstop) + ' in Year: ' + str(year))
    
    get_data(tstart, tstop, year, out_dir)
#
#--- zip the fits file from the last year at the beginning of the year
#
    ecf.check_zip_possible(out_dir)

#-------------------------------------------------------------------------------------------
#-- get_data: extract data and update the compgradkodak related data sets for the given period 
#-------------------------------------------------------------------------------------------

def get_data(start, stop, year, out_dir):
    """
    extract data and update the compgradkodak related data sets for the given period
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
            out_dir --- output_directory
    output: <out_dir>/<msid>_fill_data_<year>.fits
    """
    empty  = [0]
#
#--- extract  4rt*** data
#
    rt7  = []
    for k  in range(0, 12):
        if k < 10:
            msid = '4rt70' + str(k) + 't'
        else:
            msid = '4rt7'  + str(k) + 't'

        try:
            out   = fetch.MSID(msid, start, stop)
            data  = out.vals
            ttime = out.times
            tlist = list(ttime)
            rt7.append(data)
        except:
            rt7.append(empty)
#
#--- extract 4rt575t separately
#
    out    = fetch.MSID('4rt575t', start, stop)
    rt575  = out.vals
#
#--- create empty array and initialize ohrthr and oobthr lists
#
    tlen   = len(ttime)
    empty  = numpy.zeros(tlen)
    ohrthr = [empty]
    oobthr = [empty]
#
#--- fill them up
#
    for k in range(1, 65):
        if k < 10:
            msid = 'ohrthr0' + str(k)
        else:
            msid = 'ohrthr'  + str(k)
        try:
            out   = fetch.MSID(msid, start, stop)
            data  = out.vals
            otime = out.times
#
#--- since 4rt arrays are 36 time dense, match the ohrthr and oobtrhr 
#--- by filling the gaps between
#
            adata = fill_gaps(ttime, otime, data)

            ohrthr.append(adata)
        except:
            ohrthr.append(empty)

        if k < 10:
            msid = 'oobthr0' + str(k)
        else:
            msid = 'oobthr'  + str(k)
        try:
            out   = fetch.MSID(msid, start, stop)
            data  = out.vals
            otime = out.times

            adata = fill_gaps(ttime, otime, data)

            oobthr.append(adata)
        except:
            oobthr.append(empty)
#
#--- now compute each quantity for the given time period
#
    hrmaavg         = []
    hrmacav         = []
    hrmaxgrd        = []
    hrmaradgrd      = []
    obaavg          = []
    obaconeavg      = []
    
    fwblkhdt        = []
    aftblkhdt       = []
    obaaxgrd        = []
    
    mzobacone       = []
    pzobacone       = []
    obadiagrad      = []
    
    hrmarange       = []
    tfterange       = []
    hrmastrutrnge   = []
    scstrutrnge     = []
#
#--- save time stamp separately for each data   
#
    t_hrmaavg       = []
    t_hrmacav       = []
    t_hrmaxgrd      = []
    t_hrmaradgrd    = []
    t_obaavg        = []
    t_obaconeavg    = []
    
    t_fwblkhdt      = []
    t_aftblkhdt     = []
    t_obaaxgrd      = []
    
    t_mzobacone     = []
    t_pzobacone     = []
    t_obadiagrad    = []
    
    t_hrmarange     = []
    t_tfterange     = []
    t_hrmastrutrnge = []
    t_scstrutrnge   = []
    
    for k in range(0, tlen):
        out = compute_hrmaavg(ohrthr, k )
        if out != 'na':
            hrmaavg.append(out)
            t_hrmaavg.append(tlist[k])

#-------------------------
        out = compute_hrmacav(ohrthr, k )
        if out != 'na':
            hrmacav.append(out)
            t_hrmacav.append(tlist[k])
#-------------------------
        out = compute_hrmaxgrd(ohrthr, k )
        if out != 'na':
            hrmaxgrd.append(out)
            t_hrmaxgrd.append(tlist[k])
#------------------------ 
        out = compute_hrmaradgrd(ohrthr, k )
        if out != 'na':
            hrmaradgrd.append(out)
            t_hrmaradgrd.append(tlist[k])
#------------------------ 
        out = compute_obaavg(oobthr, k )
        if out != 'na':
            obaavg.append(out)
            t_obaavg.append(tlist[k])
#------------------------     
        out = compute_obaconeavg(oobthr, k )
        if out != 'na':
            obaconeavg.append(out)
            t_obaconeavg.append(tlist[k])
#------------------------     
        out = compute_fwblkhdt(oobthr, rt7, k )
        chk1 = 0
        if out != 'na':
            fwblkhdt.append(out)
            t_fwblkhdt.append(tlist[k])
            chk1 = 1
#------------------------     
        out = compute_aftblkhdt(oobthr, k )
        chk2 = 0
        if out != 'na':
            aftblkhdt.append(out)
            t_aftblkhdt.append(tlist[k])
            chk2 = 1
#------------------------     
        if (chk1 == 1) and (chk2 == 1):
            out = compute_obaaxgrd(fwblkhdt[-1], aftblkhdt[-1])
            if out != 'na':
                obaaxgrd.append(out)
                t_obaaxgrd.append(tlist[k])
#------------------------     
        out = compute_mzobacone(oobthr, rt575, k )
        chk1 = 0
        if out != 'na':
            mzobacone.append(out)
            t_mzobacone.append(tlist[k])
            chk1 = 1
#------------------------     
        out = compute_pzobacone(oobthr, k )
        chk2 = 0
        if out != 'na':
            pzobacone.append(out)
            t_pzobacone.append(tlist[k])
            chk2 = 1
#------------------------     
        if (chk1 == 1) and (chk2 == 1):
            out = compute_obadiagrad(mzobacone[-1], pzobacone[-1])
            if out != 'na':
                obadiagrad.append(out)
                t_obadiagrad.append(tlist[k])
#------------------------     
        out = compute_hrmarange(ohrthr, k )
        if out != 'na':
            hrmarange.append(out)
            t_hrmarange.append(tlist[k])
#------------------------     
        out = compute_tfterange(oobthr, k )
        if out != 'na':
            tfterange.append(out)
            t_tfterange.append(tlist[k])
#------------------------     
        out = compute_hrmastrutrnge(oobthr, k )
        if out != 'na':
            hrmastrutrnge.append(out)
            t_hrmastrutrnge.append(tlist[k])
#------------------------     
        out = compute_scstrutrnge(oobthr, k )
        if out != 'na':
            scstrutrnge.append(out)
            t_scstrutrnge.append(tlist[k])
#
#--- now create/update output fits files
#
    for col in ['hrmaavg', 'hrmacav', 'hrmaxgrd', 'hrmaradgrd', 'obaavg', 'obaconeavg', 'fwblkhdt',\
                'aftblkhdt', 'obaaxgrd', 'mzobacone', 'pzobacone', 'obadiagrad', 'hrmarange',\
                'tfterange', 'hrmastrutrnge', 'scstrutrnge']:

        odata = eval("%s"   % (col))
        tdata = eval("t_%s" % (col))
        

        olen  = len(odata)

        tdata = numpy.array(tdata)
        odata = numpy.array(odata)

        cdata = [tdata, odata]
        cols  = ['time', col]

        fits  = out_dir + col + '_full_data_' + str(year) + '.fits'
        if os.path.isfile(fits):
            ecf.update_fits_file(fits, cols, cdata)
        else:
            ecf.create_fits_file(fits, cols, cdata)

#-------------------------------------------------------------------------------------------
#-- compute_hrmaavg: compute hrma temp average                                            --
#-------------------------------------------------------------------------------------------

def compute_hrmaavg(ohrthr, pos):
    """
    compute hrma temp average
    input:  ohrthr  --- a list of ohrthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: hrmaavg --- hrma temp average
    """
    olist    = list(range(2,14)) + list(range(21,31)) + [33, 36, 37, 42] 
    olist    = olist + list(range(44,48)) + list(range(49,54)) + [55, 56]
    hrmaavg  = take_sum(olist, ohrthr, pos, achk=1)

    return hrmaavg

#-------------------------------------------------------------------------------------------
#-- compute_hrmacav: compute hrma cavity temp average                                     --
#-------------------------------------------------------------------------------------------

def compute_hrmacav(ohrthr, pos):
    """
    compute hrma cavity temp average
    input:  ohrthr  --- a list of ohrthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: hrmacav --- hrma temp average
    """
    olist   = list(range(6,16))+ [17, 25, 26] + list(range(29,32))
    olist   = olist + list(range(33,38)) +[39, 40] + list(range(50,59)) + [60, 61]
    hrmacav = take_sum(olist, ohrthr, pos, achk=1)

    return hrmacav

#-------------------------------------------------------------------------------------------
#-- compute_hrmaxgrd: compute hrma axial gradient                                         --
#-------------------------------------------------------------------------------------------

def compute_hrmaxgrd(ohrthr, pos):
    """
    compute hrma axial gradient 
    input:  ohrthr  --- a list of ohrthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: hrmaxgrd    --- hrma axial gradient
    """
    olist1    = [10, 11, 34, 35, 55, 56]
    olist2    = [12, 13, 36, 37, 57, 58]
    hrmaxgrd1 = take_sum(olist1, ohrthr, pos, achk=1)
    hrmaxgrd2 = take_sum(olist2, ohrthr, pos, achk=1)

    try:
        hrmaxgrd  = hrmaxgrd1 - hrmaxgrd2
    except:
        hrmaxgrd  = 'na'

    return hrmaxgrd

#-------------------------------------------------------------------------------------------
#-- compute_hrmaradgrd: compute hrma radial gradient                                      --
#-------------------------------------------------------------------------------------------

def compute_hrmaradgrd(ohrthr, pos):
    """
    compute hrma radial gradient
    input:  ohrthr  --- a list of ohrthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: hrmaradgrd  --- hrma radial gradient
    """
    olist1     = [8, 31, 33, 52]
    olist2     = [9, 53, 54]
    hrmarad1   = take_sum(olist1, ohrthr, pos, achk=1)
    hrmarad2   = take_sum(olist2, ohrthr, pos, achk=1)

    try:
        hrmaradgrd = hrmarad1 - hrmarad2
    except:
        hrmaradgrd = 'na'

    return hrmaradgrd

#-------------------------------------------------------------------------------------------
#-- compute_obaavg: compute oba/tfte temp average                                         --
#-------------------------------------------------------------------------------------------

def compute_obaavg(oobthr, pos):
    """
    compute oba/tfte temp average
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: obaavg  --- oba/tfte temp average
    """
    olist  = list(range(8,16)) + list(range(17,32)) + list(range(33,42)) + [44, 45, 11, 12, 36]
    obaavg = take_sum(olist, oobthr, pos, achk=1)

    return obaavg 

#-------------------------------------------------------------------------------------------
#-- compute_obaconeavg: compute oba cone temperature average                              --
#-------------------------------------------------------------------------------------------

def compute_obaconeavg(oobthr, pos):
    """
    compute oba cone temperature average
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: obaconeavg  --- oba cone temperature average
    """
    olist      = list(range(8,16)) + list(range(17,31)) + list(range(57,62))
    obaconeavg = take_sum(olist, oobthr, pos, achk=1)

    return obaconeavg

#-------------------------------------------------------------------------------------------
#-- compute_fwblkhdt: compute oba forward bulkhead temperature average                    --
#-------------------------------------------------------------------------------------------

def compute_fwblkhdt(oobthr, rt7, pos):
    """
    compute oba forward bulkhead temperature average
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: fwblkhdt  --- oba forward bulkhead temperature average
    """
    olist   = [62, 63]
    oobtsum = take_sum(olist, oobthr, pos, achk=1)

    olist   = list(range(0,12))
    rt7sum  = take_sum(olist, rt7, pos, achk=1)

    if oobtsum == 'na':
        if rt7sum == 'na':
            fwblkhdt = 'na'
        else:
            fwblkhdt =  rt7sum
    else:
        if rt7sum == 'na':
            fwblkhdt = oobtsum
        else:
            fwblkhdt = (oobtsum * 2 + rt7sum * 12) / 14.0

    return fwblkhdt

#-------------------------------------------------------------------------------------------
#-- compute_aftblkhdt: compute oba aft bulkhead temperature average                       --
#-------------------------------------------------------------------------------------------

def compute_aftblkhdt(oobthr, pos):
    """
    compute oba aft bulkhead temperature average
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: aftlkhdt  --- oba aft bulkhead temperature average
    """
    olist     = [31, 33, 34]
    aftblkhdt = take_sum(olist, oobthr, pos, achk=1)

    return aftblkhdt

#-------------------------------------------------------------------------------------------
#-- compute_obaaxgrd: compute oba axial gradient                                          --
#-------------------------------------------------------------------------------------------

def compute_obaaxgrd(fwblkhdt, aftblkhdt):
    """
    compute oba axial gradient
    input:  fwblkhdt    --- oba forward bulkhead temperature average
            aftlkhdt    --- oba aft bulkhead temperature average
    output: obaaxgrd    --- oba axial gradient
    """
    if (fwblkhdt != 'na') and (aftblkhdt != 'na'):
        obaaxgrd = fwblkhdt - aftblkhdt
    else:
        obaaxgrd = 'na'

    return obaaxgrd

#-------------------------------------------------------------------------------------------
#-- compute_mzobacone: compute oba -z side temperature average                            --
#-------------------------------------------------------------------------------------------

def compute_mzobacone(oobthr, rt575, pos):
    """
    compute oba -z side temperature average
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: mzobacone   --- oba -z side temperature average
    """
    olist = [8, 19, 26, 31, 57, 60]
    msum  = take_sum(olist, oobthr, pos, achk=1)

    if msum == 'na':
        if rt575[pos] == 0:
            mzobacone = 'na'
        else:
            mzobacone = rt575[pos]
    else:
        if rt575[pos] == 0:
            mzobacone = msum 
        else:
            mzobacone = (msum * 6.0 + rt575[pos]) / 7.0

    return mzobacone

#-------------------------------------------------------------------------------------------
#-- compute_pzobacone: compute oba +z side temperature average                            --
#-------------------------------------------------------------------------------------------

def compute_pzobacone(oobthr, pos):
    """
    compute oba +z side temperature average
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: pzobacone   --- oba +z side temperature average
    """
    olist = [13, 22, 23, 28, 29, 61]

    pzobacone = take_sum(olist, oobthr, pos, achk=1)

    return pzobacone

#-------------------------------------------------------------------------------------------
#-- compute_obadiagrad: compute oba diagnal gradient                                      --
#-------------------------------------------------------------------------------------------

def compute_obadiagrad(mzobacone, pzobacone):
    """
    compute oba diagnal gradient
    input:  mzobacone   --- oba -z side temperature average
            pzobacone   --- oba +z side temperature average
    output: obadiagrad  --- oba diagnal gradient
    """
    if (mzobacone != 'na') and (pzobacone != 'na'):
        obadiagrad = mzobacone - pzobacone
    else:
        obadiagrad = 'na'

    return obadiagrad

#-------------------------------------------------------------------------------------------
#-- compute_hrmarange: compute hrma total temp range                                      --
#-------------------------------------------------------------------------------------------

def compute_hrmarange(ohrthr, pos):
    """
    compute hrma total temp range
    input:  ohrthr  --- a list of ohrthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: hrmarange   ---  hrma total temp range
    """
    olist = list(range(2,14)) + list(range(21,28)) + [29, 30, 33, 36, 37, 42] 
    olist = olist + list(range(44,48)) +  list(range(49,54)) +[55, 56]

    hrmarange  = find_range(olist, ohrthr, pos)

    return hrmarange

#-------------------------------------------------------------------------------------------
#-- compute_tfterange: compute tfte vent/rad temp range                                   --
#-------------------------------------------------------------------------------------------

def compute_tfterange(oobthr, pos):
    """
    compute tfte vent/rad temp range
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: tfterange   --- tfte vent/rad temp range
    """
    olist     = [42, 43, 44]
    tfterange = find_range(olist, oobthr, pos)

    return tfterange

#-------------------------------------------------------------------------------------------
#-- compute_hrmastrutrnge: compute hrma strut temp range                                  --
#-------------------------------------------------------------------------------------------

def compute_hrmastrutrnge(oobthr, pos):
    """
    compute hrma strut temp range
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: hrmastrutrnge   --- hrma strut temp range
    """
    olist         = list(range(2,8))
    hrmastrutrnge = find_range(olist, oobthr, pos)

    return hrmastrutrnge


#-------------------------------------------------------------------------------------------
#-- compute_scstrutrnge: compute sc strut temp range                                      --
#-------------------------------------------------------------------------------------------

def compute_scstrutrnge(oobthr, pos):
    """
    compute sc strut temp range
    input:  oobthr  --- a list of oobthr data lists
            pos     --- the position of the data in the ohrthr[*]
    output: scstrutrnge --- compute sc strut temp range
    """
    olist       = list(range(49,55))
    scstrutrnge = find_range(olist, oobthr, pos)

    return scstrutrnge


#-------------------------------------------------------------------------------------------
#-- take_sum: take average of the given data                                              --
#-------------------------------------------------------------------------------------------

def take_sum(olist, data, pos, achk=0):
    """
    take average of the given data
    input:  olist   --- a list of data ids
            data    --- a list of data
            pos     --- the position of the data to be used in data[*]
            achk    --- if 0, just retur the sum, if >0, take an average
    output: asum or avg --- asum (achk=0): sum of the values
                            avg  (achk>0): averaged of the values
    """
    asum = 0.0
    tot  = 0.0
    for k in olist:
        try:
            val = data[k][pos]
            if val > 0:
                asum += data[k][pos]
                tot  += 1.0
        except:
            pass

    if achk == 0:
        return asum

    else:
        try:
            avg = asum / tot
        except:
            avg = 'na'

        return avg

#-------------------------------------------------------------------------------------------
#-- find_range: find the range of the values in the data                                  --
#-------------------------------------------------------------------------------------------

def find_range(olist, data, pos):
    """
    find the range of the values in the data
    input:  olist   --- a list of data ids
            data    --- a list of data
            pos     --- the position of the data to be used in data[*]
    output: arange  --- the range of the data
    """
    amin = ''
    amax = ''
    for k in olist:
        try:
            val = data[k][pos]
            if amin == '':
                amin = val
                amax = val
            else:
                if val > amax:
                    amax = val
                if val < amin:
                    amin = val
        except:
            pass
    
    if amin == '':
        arange = 'na'
    else:
        arange = amax - amin
    
    return arange

#-------------------------------------------------------------------------------------------
#-- fill_gaps: match the numbers of entries accroding to two time lists                   --
#-------------------------------------------------------------------------------------------

def fill_gaps(ttime, otime, data):
    """
    match the numbers of entries accroding to two time lists
    the data are repeated between two time stamps of the data to be filled
    input:  ttime   --- an array of time to be matched
            otime   --- an array of time of the data
                        len(ttime) > len(otime)
            data    --- an array of data
    output: adata   --- adjusted data
    """
#
#--- convert numpy array to list
#
    ttime = list(ttime)
    data  = list(data)
    otime = list(otime)

    tlen  = len(ttime)
    mlen  = len(otime)

    adata = []
    n     = 0
    chk   = 0
    for m in range(0, tlen):
        if ttime[m] > otime[n]:
            while ttime[m] > otime[n]:
                n += 1
                if n >= mlen:
                    diff = tlen - len(adata)
                    for nk in range(0, diff):
                        adata.append(data[n-1])
                    chk = 1
                    break
                else:
                    if ttime[m] == otime[n]:
                        adata.append(data[n])
                        break
        elif ttime[m] < otime[n]:
            adata.append(data[n])
        else:
            adata.append(data[n])
            n += 1
            if n >= mlen:
                diff = tlen - len(adata)
                for nk in range(0, diff):
                    adata.append(data[n-1])
                chk = 1
        if chk == 1:
            break
#
#--- put back into numpy array
#
    adata = numpy.array(adata)

    return adata

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

    update_compgradkodak()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")