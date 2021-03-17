#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Jan 22, 2020                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
from astropy.io.fits import Column
import Ska.engarchive.fetch as fetch
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions     as mcf  #---- contains other functions commonly used in MTA scripts
import envelope_common_function as ecf  #---- contains other functions commonly used in envelope
import fits_operation           as mfo  #---- fits operation collection
import read_limit_table         as rlt  #---- read limit table and create msid<--> limit dict
#
#--- fits generation related lists
#
col_names  = ['time', 'msid', 'med', 'std', 'min', 'max', 
              'ylower', 'yupper', 'rlower', 'rupper', 'dcount', 
              'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper', 'state']
col_format = ['D', '20A', 'D', 'D','D','D','D','D','D','D', 'I', 'D', 'D', 'D', 'D', '10A']

a_month = 86400 * 30
#
#--- create msid <---> category dict
#
[lim_dict, cnd_dict] = rlt.get_limit_table()
#
#--- directories
#
comp_dir = '/data/mta/Script/MTA_limit_trends/Deposit/Comp_save/'
#
#---comp msids
#
compgradkodak = ['hrmaavg', 'hrmacav', 'hrmaxgrd', 'hrmaradgrd', 'obaavg', 'obaconeavg',\
                 'fwblkhdt', 'aftblkhdt', 'obaaxgrd', 'mzobacone', 'pzobacone', 'obadiagrad',\
                 'hrmarange', 'tfterange', 'hrmastrutrnge', 'scstrutrnge']

compaciscent  = ['1cbat', '1cbbt', '1crat', '1crbt', '1dactbt', '1deamzt', '1dpamyt',\
                 '1dpamzt', '1mahcat', '1mahcbt', '1mahoat', '1mahobt', '1oahat', \
                 '1oahbt', '1pdeaat', '1pdeabt', '1pin1at', '1wrat', '1wrbt']

compacispwr   = ['1dppwra', '1dppwrb']

compsimoffset = ['flexadif', 'flexbdif', 'flexcdif']

group_name  = ['Compgradkodak', 'Compacispwr', 'Compsimoffset']
g_msid_list = [compgradkodak,    compacispwr,   compsimoffset]

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def update_comp_data():

    for k in range(0, len(catg_list)):
        catg  = catg_list[k]
        print(catg)
        mlist = g_msid_list[k]
        cmd   = ' mkdir -p ./Out/' + catg
        os.system(cmd)


        for year in range(1999, 2020):
            start = str(year)     + ':001:00:00:00'
            stop  = str(year + 1) + ':001:00:00:00'
    
            tstart = Chandra.Time.DateTime(start).secs
            tstop  = Chandra.Time.DateTime(stop).secs
    
            for msid in mlist:
                for dtype in ['long', 'short']:
                    if dtype == 'short' and year < 2019:
                        continue
    
                    print(" Year: " + str(year) + " MSID: " + str(msid) + ' Dtype: ' + dtype)
    
                    alimit   = lim_dict[msid]
                    fits     = comp_dir + catg + '/' + msid + '_full_data_' + str(year) + '.fits.gz'
                    out      = extract_data_from_deposit(msid, fits, tstart, tstop, dtype, alimit)
                    if out == False:
                        print("Something went wrong for " + msid + ' in year: ' + str(year))
                    else:
                        bfits = './' + catg + '/' + out
                        if os.path.isfile(bfits):
                            mfo.appendFitsTable(bfits, out,'./temp.fits' ) 
                            cmd = 'mv -f ' + bfits + ' ' + bfits + '~'
                            os.system(cmd)
                            cmd = 'mv ./temp.fits ' +  bfits
                            os.system(cmd)
    
                            os.system("rm -rf " + out)
    
                        else:
                            cmd = 'mv ' + out + ' ./' + catg + '/' + out
                            os.system(cmd)



#--------------------------------------------------------------------------------
#-- find_data_collection_period: set start and stop time of data collection period 
#--------------------------------------------------------------------------------

def find_data_collection_period(msid, catg, dtype):
    """
    set start and stop time of data collection period
    input:  msid    --- msid
            catg    --- category name of the msid
            dtype   --- data type: week, short, long
    output: dfile   --- data file name
            stime   --- starting time in seconds from 1998.1.1
            etime   --- stopping time in seconds from 1998.1.1
    """
#
#--- set today's date as the ending time
#
    etime = today_date_chandra()
#
#--- week data are always extracted from two weeks ago up to today
#
    if dtype == 'week':
        dfile = data_dir +  catg + '/' + msid + '_week_data.fits'
        stime = etime  - 86400 * 14
#
#--- for others, find the last entry time from the exisiting fits data file
#
    elif dtype == 'short':
        dfile = data_dir +  catg + '/' + msid + '_short_data.fits'
        stime = find_last_entry_time(dfile, dtype, etime)

    else:
        dfile = data_dir +  catg + '/' + msid + '_data.fits'
        stime = find_last_entry_time(dfile, dtype, etime)


    return [dfile, stime, etime]

#--------------------------------------------------------------------------------
#-- today_date_chandra: get today's time (0 hr) in seconds from 1998.1.1      ---
#--------------------------------------------------------------------------------

def today_date_chandra():
    """
    get today's time (0 hr) in seconds from 1998.1.1
    input:  none
    output: stime   --- today's date (0 hr) in seconds from 1998.1.1
    """
    today = time.strftime('%Y:%j:00:00:00', time.gmtime())
    stime = Chandra.Time.DateTime(today).secs

    return stime

#--------------------------------------------------------------------------------
#-- find_last_entry_time: find the last entry time                             --
#--------------------------------------------------------------------------------

def find_last_entry_time(dfile, dtype, today):
    """
    find the last entry time
    input:  dfile   --- fits data file name
            dtype   --- data type: week, short, long
            today   --- today's time in seconds from 1998.1.1
    output: tend    --- the last entry time in seconds from 1998.1.1
                        if the past file does not exist, a standard time is given
                        (two week for week data, two years for short, 
                         and 1998.201 for the long)
    """
#
#--- check the previous fits data file exists. if it does, find the last entry time
#
    if os.path.isfile(dfile):
        hdout = pyfits.open(dfile)
        data  = hdout[1].data
        dtime = data['time']
        tend  = dtime[-1]
        hdout.close()
#
#--- otherwise, set a standard starting time
#
    else:
        if dtype == 'week':
            tend =  today - 86400 * 14          #--- two weeks ago

        elif dtype == 'short':
            tend = today - 86400 * 548          #--- 1.5 years ago

        else:
            tend = 48815999.0                   #--- 1999.201

    return tend

#--------------------------------------------------------------------------------
#-- update_data_file: update data file                                        ---
#--------------------------------------------------------------------------------

def update_data_file(dfile, msid, dtype):
    """
    update data file
    input:  dfile   --- fits data file name
            msid    --- msid
            dtype   --- data type: week, short or long
    output: dfile   --- updated fits data file
    """
#
#--- the name of the fits file containing the new data section
#
    if dtype == 'week':
        lfile = msid + '_week_data.fits'

    elif dtype == 'short':
        lfile = msid + '_short_data.fits'
#
#--- for the short time data, remove data older than 1.5 years
#--- before appending the new data
#
        if os.path.isfile(dfile):
            today = today_date_chandra()
            cut   = today - 86400 * 548
            remove_old_data_from_fits(dfile, cut)
    else:
        lfile = msid + '_data.fits'
#
#--- week data is just replaced, but others are appended if the past data exists
#
    if (dtype != 'week') and os.path.isfile(dfile):
        mcf.rm_files('./ztemp.fits')
        mfo.appendFitsTable(dfile, lfile, './ztemp.fits')
        cmd = 'mv -f ./ztemp.fits ' + dfile
        os.system(cmd)
        mcf.rm_files(lfile)
    else:
        cmd = 'mv ' + lfile + ' ' + dfile
        os.system(cmd)

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def extract_data_from_deposit(msid, fits, start, stop, dtype, alimit):
    """
    extract data from ska database and created data fits file
    input:  msid    --- msid
            start   --- period starting time in seconds from 1998.1.1
            stop    --- period ending time  in seconds from 1998.1.1
            dtype   --- data type:  week, short or  long (blank is fine)
    output: <msid>_<dtye>_data.fits
    """
    period = dtype_to_period(dtype)
    fdata  = run_condtion_msid(msid, fits, start, stop, period, alimit, 'none')

    if fdata != []:
        out = create_fits_file(msid, fdata, dtype)
        return out 
    else:
        return False

#--------------------------------------------------------------------------------
#-- dtype_to_period: set data average interval period for a given data type    --
#--------------------------------------------------------------------------------

def dtype_to_period(dtype):
    """
    set data average interval period for a given data type
    input:  dtype   --- data type: week, short or others
    output: peiod   --- time period in seconds
    """
    if dtype == 'week':
        period = 300.0

    elif dtype == 'short':
        period = 3600.0

    else:
        period = 86400.0

    return period

#--------------------------------------------------------------------------------
#-- run_condtion_msid: extract data from ska database and analyze data         --
#--------------------------------------------------------------------------------

def run_condtion_msid(msid, fits, start, stop, period, alimit, cnd_msid):
    """
    extract data from ska database and analyze data
    input:  msid    --- msid 
            start   --- starting time in seconds from 1998.1.1
            stop    --- stopping time in seconds from 1998.1.1
            period  --- data collection interval in seconds (e.g. 300, 3600, or 86400)
            alimit  --- a list of lists of limits
            cnd_msid    ---- msid which tells which limit set to use for given time
    output: save    --- a list of list of data:
                            time, average, median, std, min, max, 
                            ratio of yellow lower violation,
                            ratio of yellow upper violation,
                            ratio of rd  lower violation,
                            ratio of red upper violation,
                            total data in the period,
                            yellow lower limit, yellow upper limit,
                            red lower limit, red upper limit
                            state
    """
#
#--- extract data with ska fetch for the given time period
#
    out     = pyfits.open(fits)
    data    = out[1].data
    dtime   = data['time']
    if len(dtime) < 1:
        return []

    tdata   = data[msid]
    tmax    = dtime[-1]
#
#--- for the case this is multi limit case
#
    if cnd_msid != 'none':
        out   = fetch.MSID(cnd_msid, start, stop)
        mtime = out.times
        mdata = out.vals
        mlen  = len(mdata)
#
#--- for the case this is single limit case
#
    else:
        mdata = ['none'] * len(dtime)
#
#--- there are 15 elements to keep in the output data
#
    save = []
    for k in range(0, 16):
        save.append([])
#
#--- compute how many data collection periods exist for a given data period
#
    n_period = int((stop - start) / period) + 1
#
#--- collect data in each time period and compute statistics
#
    for k in range(0, n_period):
        begin = start + k * period
        end   = begin + period
        ctime = begin + 0.5 * period
#
#--- find the state of condition msid for this period of time
#
        if cnd_msid == 'none':
            mkey = 'none'
        else:
            pos  = int(mlen * begin /tmax) - 1
            if pos < 0:
                pos = 0
            if pos >= mlen:
                pos = mlen -1
            mkey = mdata[pos].lower()
#
#--- set limit range only once at the beginning of each data collection period
#
        try:
            limit_table = find_limits(begin, mkey, alimit)
            [y_low, y_top, r_low, r_top] = limit_table
        except:
            limit_table = [-9999998.0, 9999998.0, -9999999.0, 9999999.0]
            [y_low, y_top, r_low, r_top] = [-9999998.0, 9999998.0, -9999999.0, 9999999.0]
#
#--- select data between the period
#
        ind   = dtime >= begin
        btemp = dtime[ind]
        sdata = tdata[ind]

        ind   = btemp <  end
        sdata = sdata[ind]
        dcnt  = len(sdata)
        if dcnt < 1:
            continue
#
#--- get stats
#
        dmin  = min(sdata)
        dmax  = max(sdata)
        avg   = numpy.mean(sdata)
#
#--- if the value is too large something is wrong: so skip it
#
        if abs(avg) > 100000000.0:
            continue

        med   = numpy.median(sdata)
        std   = numpy.std(sdata)
#
#--- count number of violations
#
        [y_lc, y_uc, r_lc, r_uc] = find_limit_violatons(sdata, limit_table)
#
#--- save the resuts
#
        save[0].append(float(int(ctime)))
        save[1].append(float("%3.2f" % avg))
        save[2].append(float("%3.2f" % med))
        save[3].append(float("%3.2f" % std))
        save[4].append(float("%3.2f" % dmin))
        save[5].append(float("%3.2f" % dmax))
        save[6].append(float("%1.3f" % (y_lc /dcnt)))
        save[7].append(float("%1.3f" % (y_uc /dcnt)))
        save[8].append(float("%1.3f" % (r_lc /dcnt)))
        save[9].append(float("%1.3f" % (r_uc /dcnt)))
        save[10].append(dcnt)
        save[11].append(float("%3.2f" % y_low))
        save[12].append(float("%3.2f" % y_top))
        save[13].append(float("%3.2f" % r_low))
        save[14].append(float("%3.2f" % r_top))
        save[15].append(mkey)

    return save

#--------------------------------------------------------------------------------
#-- find_limit_violatons: count numbers of yellow/red violation in the given data set
#--------------------------------------------------------------------------------

def find_limit_violatons(sdata, limit_table):
    """
    count numbers of yellow/red violation in the given data set
    input:  sdata       --- a list of data
            limit_table --- a list of limit values
                            this could contain two set of limit values
    output:  [y_lc, y_uc, r_lc, r_uc]
    """
#
#--- count number of violations: multi limit set case
#
    if isinstance(limit_table[0], list):
        y_lc = 0
        y_uc = 0
        r_lc = 0
        r_uc = 0
        for val in sdata:
#
#--- no violation
#
            for ltable in limit_table:
                if (val > ltable[0]) and (val < ltable[1]):
                    continue

            for ltable in limit_table:
#
#--- yellow violation
#
                if (val >ltable[2]) and (val <= ltable[0]):
                    y_lc += 1
                    continue
                if( val < ltable[3]) and (val >= ltable[1]):
                    y_uc += 1
                    continue
#
#--- red violation
#
                if (val < ltable[2]):
                    r_lc += 1
                    continue
                if (val > ltable[3]):
                    r_uc += 1
                    continue
#
#--- single set of limit case
#
    else:
        [y_low, y_top, r_low, r_top] = limit_table
        ind   = sdata < r_low
        r_lc  = len(sdata[ind])             #--- red lower violation
        ind   = sdata < y_low
        y_lc  = len(sdata[ind]) - r_lc      #--- yellow lower violation

        ind   = sdata > r_top
        r_uc  = len(sdata[ind])             #--- red upper violation
        ind   = sdata > y_top
        y_uc  = len(sdata[ind]) - r_uc      #--- yellow upper violation

    return [y_lc, y_uc, r_lc, r_uc]

#--------------------------------------------------------------------------------
#-- find_limits: find a set of limit for the given time and what condition msid indicates
#--------------------------------------------------------------------------------

def find_limits(stime, mkey, alimit):
    """
    find a set of limit for the given time and what condition msid indicates
    input:  stime   --- tine in seconds from 1998.1.1
            mkey    --- condtion given by condtion msid
            alimit  --- a full limit table
                the structure of alimit is:
                    [
                        [<start>,<stop>,<switch value list>,
                         <limit dictionary with the switch as key>
                        ]
                    ]
    output: [y_low, y_top, r_low, r_top]
    """
    stime = int(stime)
    mkey  = mkey.strip()

    ltable = []
    for k in range(0, len(alimit)):
        begin = alimit[k][0]
        end   = alimit[k][1]
        if (stime >= begin) and (stime < end):
            try:
                ltable = alimit[k][3][mkey]
            except:
                ltable = alimit[k][3]['none']
            break 

    if ltable == []:
        ltable = [-9999998.0, 9999998.0, -9999999.0, 9999999.0]

    return ltable

#--------------------------------------------------------------------------------
#-- create_fits_file: create a fits file                                       --
#--------------------------------------------------------------------------------

def create_fits_file(msid, data, dtype):
    """
    create a fits file
    input:  msid    --- msid
            data    --- a list of list of data
            dtype   --- data type (week, short, or others)
    output: ./<msid>_<dtype>_data.fits
    """
    cols    = col_names
    cols[1] = msid

    c1  = Column(name=cols[0],  format=col_format[0],  array = data[0])
    c2  = Column(name=cols[1],  format=col_format[1],  array = data[1])
    c3  = Column(name=cols[2],  format=col_format[2],  array = data[2])
    c4  = Column(name=cols[3],  format=col_format[3],  array = data[3])
    c5  = Column(name=cols[4],  format=col_format[4],  array = data[4])
    c6  = Column(name=cols[5],  format=col_format[5],  array = data[5])
    c7  = Column(name=cols[6],  format=col_format[6],  array = data[6])
    c8  = Column(name=cols[7],  format=col_format[7],  array = data[7])
    c9  = Column(name=cols[8],  format=col_format[8],  array = data[8])
    c10 = Column(name=cols[9],  format=col_format[9],  array = data[9])
    c11 = Column(name=cols[10], format=col_format[10], array = data[10])
    c12 = Column(name=cols[11], format=col_format[11], array = data[11])
    c13 = Column(name=cols[12], format=col_format[12], array = data[12])
    c14 = Column(name=cols[13], format=col_format[13], array = data[13])
    c15 = Column(name=cols[14], format=col_format[14], array = data[14])
    c16 = Column(name=cols[15], format=col_format[15], array = data[15])
        
    coldefs = pyfits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)

    if dtype == 'week':
        ofits = msid + '_week_data.fits'
    elif dtype == 'short':
        ofits = msid + '_short_data.fits'
    else:
        ofits = msid + '_data.fits'
    
    mcf.rm_files(ofits)

    tbhdu.writeto(ofits)

    return ofits

#--------------------------------------------------------------------------------
#-- remove_old_data_from_fits: remove old part of the data from fits file      --
#--------------------------------------------------------------------------------

def remove_old_data_from_fits(fits, cut):
    """
    remove old part of the data from fits file
    input:  fits    --- fits file name
            cut     --- cut date in seconds from 1998.1.1
    output: fits    --- updated fits file
    """
#
#--- open the fits file
#
    hbdata   = pyfits.open(fits)
    data     = hbdata[1].data
    cols     = hbdata[1].columns
    col_list = cols.names
    hbdata.close()
#
#--- create a mask
#
    dtime    = data['time']
    index    = dtime > cut
#
#--- using the mask get only data > cut
#
    udata = []
    for col in col_list:
        out       = data[col]
        nout      = out[index]
        udata.append(list(nout))
#
#--- update the data and save then in the fits file
#
    sfits = fits + '~'
    cmd   = 'mv ' + fits + ' ' + sfits
    os.system(cmd)
    try:
        create_fits_file(fits, cols, udata)
        mcf.rm_file(sfits)
    except:
        cmd = 'mv ' + sfits + ' ' + fits
        os.system(cmd)

#--------------------------------------------------------------------------------
#-- create_category_dict: create msid <---> category dict                      --
#--------------------------------------------------------------------------------

def create_category_dict():
    """
    create msid <---> category dict
    input:  none but read from <house_keeping>/msid_list
    output: catg_dict
    """
    ifile = limit_dir + 'house_keeping/msid_list'
    data  = mcf.read_data_file(ifile)
    catg_dict = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        catg_dict[atemp[0]] = atemp[1]
   
    return catg_dict

#--------------------------------------------------------------------------------

if __name__ == "__main__":

    update_comp_data()
#    msid  = sys.argv[1].strip()         #--- msid
#    fits  = sys.argv[2].strip()
#    start = float(sys.argv[3])          #--- start time in seconds from 1998.1.1
#    stop  = float(sys.argv[4])          #--- stop  time in seconds from 1998.1.1
#    dtype = sys.argv[5].strip()         #--- week, short, long
#
#    alimit   = lim_dict[msid]
#    extract_data_from_deposit(msid, fits, start, stop, dtype, alimit):
