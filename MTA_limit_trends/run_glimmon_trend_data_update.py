#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#   run_glimmon_trend_data_update.py: update trend data with limits in glimmon database     #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 01, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import numpy
import argparse
import getpass
import astropy.io.fits  as pyfits
from astropy.io.fits import Column
import Ska.engarchive.fetch as fetch
import Chandra.Time

#
#--- Define Directory Pathing
#
BIN_DIR = "/data/mta/Script/MTA_limit_trends/Scripts"
LIMIT_DIR = "/data/mta/Script/MSID_limit/Trend_limit_data"
OUT_DATA_DIR = "/data/mta/Script/MTA_limit_trends/Data"
HOUSE_KEEPING = "/data/mta/Script/MTA_limit_trends/Scripts/house_keeping"
#
#--- append path to a private folder
#
sys.path.append(BIN_DIR)
sys.path.append("/data/mta4/Script/Python3.11/MTA")
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

#--------------------------------------------------------------------------------
#-- run_glimmon_trend_data_update: update trend data with limits in glimmon database
#--------------------------------------------------------------------------------

def run_glimmon_trend_data_update():
    """
    update trend data with limits in glimmon database
    input:  none
    output: <data_dir>/<cateogry>/<msid>_<dtype>_data.fits
    """
#
#--- create msid <---> category dict
#
    catg_dict = create_category_dict()
#
#--- multi state data --- no more distinction (Jan 22, 2020)
#
    run_data_update('m', catg_dict)
#
#--- no state data
#
#    run_data_update('n', catg_dict)

#--------------------------------------------------------------------------------
#-- run_data_update: extract data for the specified limit category type       ---
#--------------------------------------------------------------------------------

def run_data_update(mtype, catg_dict):
    """
    extract data for the specified limit category type
    input:  mtype       --- limit state type; m: multi state/n: no state
            catg_dict   --- a dictionary of msid <---> cateogry
    output: updated data fits files
    """
    [lim_dict, cnd_dict] = rlt.get_limit_table()

    ifile = f"{LIMIT_DIR}/Limit_data/op_limits_new.db"
#
#--- first find which msids are in that category, and extract data
#
    with open(ifile) as f:
        data = [line.strip() for line in f.readlines()]
    for ent in data:
        if ent[0] == '#':
            continue
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        catg  = catg_dict[msid]
#
#--- just in a case the data category directory does not exist
#
        os.makedir(f"{OUT_DATA_DIR}/{atemp[1]}", exist_ok = True)

        print("MSID: " + catg + '/' + msid)
#
#--- three different data length
#
        for dtype in ['week', 'short', 'long']:
#
#--- set data period
#
            [dfile, start, stop] = find_data_collection_period(msid, catg, dtype)
#
#--- extract new data part; saved as a local fits file
#
            alimit   = lim_dict[msid]
            cnd_msid = cnd_dict[msid]
            out = extract_data_from_ska(msid, start, stop, dtype, alimit, cnd_msid)
#
#--- update the main fits file, either move the local file or append the new part
#
            if out == True:
                update_data_file(dfile, msid, dtype)

#--------------------------------------------------------------------------------
#-- run_for_msid_list: extract data from ska database for a given msid_list   ---
#--------------------------------------------------------------------------------

def run_for_msid_list(msid_list, dtype):
    """
    extract data from ska database for a given msid_list
    input:  misd_list   --- the file name of the msid_list
            dtype       --- data type , week, short, or long
    output: updated data fits files
    """
    [lim_dict, cnd_dict] = rlt.get_limit_table()

    ifile = f"{HOUSE_KEEPING}/{msid_list}"
    with open(ifile) as f:
        data = [line.strip() for line in f.readlines()]

    for ent in data:
        if ent[0] == '#':
            continue
        elif ent.strip() == '':
            continue

        atemp = re.split('\s+', ent)
        msid  = atemp[0].strip()
        catg  = atemp[1].strip()

        print("MSID: " + catg + '/' + msid)
#
#--- just in a case the data category directory does not exist
#
        os.makedir(f"{OUT_DATA_DIR}/{atemp[1]}", exist_ok = True)
#
#--- set data period
#
        [dfile, start, stop] = find_data_collection_period(msid, catg, dtype)
#
#--- extract new data part; saved as a local fits file
#
        try:
            alimit   = lim_dict[msid]
            cnd_msid = cnd_dict[msid]
#
#--- if the collection time is larger than a month, extract data for 30 day chunk
#
            diff = stop - start
            if diff > a_month:
                mcnt = int(diff / a_month)
                for m in range(0, mcnt):
                    mstart = start + a_month * m
                    mstop  = mstart + a_month
                    lstart = f"{mcf.chandratime_to_fraq_year(mstart):4.2f}"
                    lstop = f"{mcf.chandratime_to_fraq_year(mstop):4.2f}"
                    print("Computing: " + str(lstart) + '<-->' + str(lstop))
#
#--- extract data and make a local fits file
#
                    out = extract_data_from_ska(msid, mstart, mstop, dtype, alimit, cnd_msid)
#
#--- update the main fits file, either move the local file or append the new part
#
                    if out == True:
                        update_data_file(dfile, msid, dtype)

                out = extract_data_from_ska(msid, mstop, stop, dtype, alimit, cnd_msid)
                if out == True:
                    update_data_file(dfile, msid, dtype)
#
#--- the data collection period is < 30 days
#
            else:
                out = extract_data_from_ska(msid, start, stop, dtype, alimit, cnd_msid)
                if out == True:
                    update_data_file(dfile, msid, dtype)
        except:
            #print(msid + ' is not in glimmon database')
            print(msid + ' is not in ska fetch database')
            continue


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
        dfile = f"{OUT_DATA_DIR}/{catg}/{msid}_week_data.fits"
        stime = etime  - 86400 * 14
#
#--- for others, find the last entry time from the exisiting fits data file
#
    elif dtype == 'short':
        dfile = f"{OUT_DATA_DIR}/{catg}/{msid}_short_data.fits"
        stime = find_last_entry_time(dfile, dtype, etime)

    else:
        dfile = f"{OUT_DATA_DIR}/{catg}/{msid}_data.fits"
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
        os.remove('./ztemp./fits')
        mfo.appendFitsTable(dfile, lfile, './ztemp.fits')
        os.system(f"mv -f ./ztemp.fits {dfile}")
        os.remove(lfile)
    else:
        os.system(f"mv {lfile} {dfile}")

#--------------------------------------------------------------------------------
#-- extract_data_from_ska: extract data from ska database and created data fits file 
#--------------------------------------------------------------------------------

def extract_data_from_ska(msid, start, stop, dtype, alimit, cnd_msid):
    """
    extract data from ska database and created data fits file
    input:  msid    --- msid
            start   --- period starting time in seconds from 1998.1.1
            stop    --- period ending time  in seconds from 1998.1.1
            dtype   --- data type:  week, short or  long (blank is fine)
    output: <msid>_<dtye>_data.fits
    """
    period = dtype_to_period(dtype)

    fdata = run_condtion_msid(msid, start, stop, period, alimit, cnd_msid)

    if fdata != []:
        create_fits_file(msid, fdata, dtype)
        return True
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

def run_condtion_msid(msid, start, stop, period, alimit, cnd_msid):
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
    out     = fetch.MSID(msid, start, stop)
    ok      = ~out.bads
    dtime   = out.times[ok]
    if len(dtime) < 1:
        return []

    tdata   = out.vals[ok]
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
    
    os.remove(ofits)

    tbhdu.writeto(ofits)

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
        ecf.create_fits_file(fits, cols, udata)
        os.remove(sfits)
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
    ifile = f"{LIMIT_DIR}/house_keeping/msid_list"
    with open(ifile) as f:
        data = [line.strip() for line in f.readlines()]
    catg_dict = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        catg_dict[atemp[0]] = atemp[1]
   
    return catg_dict

#--------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")
    

    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--period',help='Process specific time length. Choices are last two weeks, 1.5 years, or since 1999:201 respectively', \
                        action="extend",nargs='*',type=str, choices=["week","short","long"])
    parser.add_argument("-m","--msid_list",help="File name of msid list to use from housekeeping",type=str)
    
    parser.add_argument("--msid", help="Process specific MSID",type=str)
    parser.add_argument("--start", help="Start time in seconds from 1998.1.1",type=float)
    parser.add_argument("--stop", help="Stop time in seconds from 1998.1.1",type=float)
    args = parser.parse_args()

    if args.msid is not None:
        [lim_dict, cnd_dict] = rlt.get_limit_table()
        alimit   = lim_dict[args.msid]
        cnd_msid = cnd_dict[args.msid]

    if args.period is not None:
        for dtype in args.period:
            if args.msid is not None:
                extract_data_from_ska(args.msid, args.start, args.stop, dtype, alimit, cnd_msid)
            elif args.msid_list is not None:
                run_for_msid_list(args.msid_list, dtype)
    else:
        run_glimmon_trend_data_update()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")