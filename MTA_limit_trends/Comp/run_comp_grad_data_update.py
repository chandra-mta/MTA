#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#           run_comp_grad_data_update.py: update comp and grad related msid data            #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: May 06, 2024                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import numpy
import astropy.io.fits  as pyfits
from astropy.io.fits import Column
import Ska.engarchive.fetch as fetch
import Chandra.Time
import traceback
import signal
import argparse
import getpass
#
#--- Define Directory Pathing
#
BIN_DIR = "/data/mta/Script/MTA_limit_trends/Scripts"
MTA_DIR = "/data/mta4/Script/Python3.11/MTA"
DEPOSIT_DIR = "/data/mta/Script/MTA_limit_trends/Deposit"
COMP_DIR = f"{DEPOSIT_DIR}/Comp_save"
GRAD_DIR = f"{DEPOSIT_DIR}/Grad_save"
DATA_DIR = "/data/mta/Script/MTA_limit_trends/Data"

#
#--- append path to a private folder
#
sys.path.append(BIN_DIR)
sys.path.append(MTA_DIR)
#
#--- import several functions
#
import fits_operation           as mfo  #---- fits operation collection
import read_limit_table         as rlt  #---- read limit table and create msid<--> limit dict

#
#--- Define globals
#
FULL_GEN = False #Used for determining whether to generate the fill fits files or build off the last time entry
DTYPE = ['long', 'short', 'week']
#
#--- fits generation related lists
#
COL_NAMES  = ['time', 'msid', 'med', 'std', 'min', 'max', 
              'ylower', 'yupper', 'rlower', 'rupper', 'dcount', 
              'ylimlower', 'ylimupper', 'rlimlower', 'rlimupper', 'state']
COL_FORMAT = ['D', '20A', 'D', 'D','D','D','D','D','D','D', 'I', 'D', 'D', 'D', 'D', '10A']

#
#--- create msid <---> category dict
#
[lim_dict, cnd_dict] = rlt.get_limit_table()
#
#---comp/grad msids
#
compgradkodak = ['hrmaavg', 'hrmacav', 'hrmaxgrd', 'hrmaradgrd', 'obaavg', 'obaconeavg',\
                 'fwblkhdt', 'aftblkhdt', 'obaaxgrd', 'mzobacone', 'pzobacone', 'obadiagrad',\
                 'hrmarange', 'tfterange', 'hrmastrutrnge', 'scstrutrnge']

compacispwr   = ['1dppwra', '1dppwrb']

compsimoffset = ['flexadif', 'flexbdif', 'flexcdif']

gradablk      = ['haftbgrd1', 'haftbgrd2', 'haftbgrd3']

gradahet      = ['haheatgrd1', 'haheatgrd2', 'haheatgrd3']

gradaincyl    = ['haicylgrd',]

gradcap       = ['hcapgrd1', 'hcapgrd2', 'hcapgrd3', 'hcapgrd4',\
                 'hcapgrd5', 'hcapgrd6', 'hcapgrd7', 'hcapgrd8']

gradfap       = ['hfapgrd1', 'hfapgrd2', 'hfapgrd3', 'hfapgrd4', 'hfapgrd5',\
                 'hfapgrd6', 'hfapgrd7', 'hfapgrd8', 'hfapgrd9']

gradfblk      = ['hfrdbgrd1', 'hfrdbgrd2', 'hfrdbgrd3', 'hfrdbgrd4',\
                 'hfrdbgrd5', 'hfrdbgrd7', 'hfrdbgrd8', 'hfrdbgrd10',\
                 'hfrdbgrd11', 'hfrdbgrd12', 'hfrdbgrd13', 'hfrdbgrd14']

gradhcone     = ['hconegrd1',  'hconegrd2',  'hconegrd3',  'hconegrd4',  'hconegrd5',\
                 'hconegrd6',  'hconegrd7',  'hconegrd8',  'hconegrd9',  'hconegrd10',\
                 'hconegrd11', 'hconegrd12', 'hconegrd13', 'hconegrd14', 'hconegrd15',\
                 'hconegrd16', 'hconegrd17', 'hconegrd18', 'hconegrd19', 'hconegrd20',\
                 'hconegrd21', 'hconegrd22', 'hconegrd23', 'hconegrd24', 'hconegrd25',\
                 'hconegrd26', 'hconegrd27', 'hconegrd28', 'hconegrd29', 'hconegrd30',\
                 'hconegrd31', 'hconegrd32', 'hconegrd33', 'hconegrd34', 'hconegrd35',\
                 'hconegrd36', 'hconegrd37', 'hconegrd38', 'hconegrd39', 'hconegrd40',\
                 'hconegrd41', 'hconegrd42', 'hconegrd43', 'hconegrd44']

gradhhflex    = ['hhflxgrd1', 'hhflxgrd2', 'hhflxgrd3', 'hhflxgrd4', 'hhflxgrd5',\
                 'hhflxgrd6', 'hhflxgrd7', 'hhflxgrd8', 'hhflxgrd9']

gradhpflex    = ['hpflxgrd1', 'hpflxgrd2', 'hpflxgrd3', 'hpflxgrd4', 'hpflxgrd5',\
                 'hpflxgrd6', 'hpflxgrd7', 'hpflxgrd8', 'hpflxgrd9']

gradhstrut    = ['hstrtgrd1', 'hstrtgrd2', 'hstrtgrd3', \
                 'hstrtgrd4', 'hstrtgrd5', 'hstrtgrd6']

gradocyl      = ['hocylgrd1', 'hocylgrd2', 'hocylgrd3', \
                 'hocylgrd4', 'hocylgrd5', 'hocylgrd6']

gradpcolb     = ['hpcolbgrd1', 'hpcolbgrd2']

gradperi      = ['hprigrd',]

gradsstrut    = ['hsstrtgrd1', 'hsstrtgrd2', 'hsstrtgrd3',\
                 'hsstrtgrd4', 'hsstrtgrd5', 'hsstrtgrd6']
gradtfte      = ['htftegrd1', 'htftegrd2', 'htftegrd3', 'htftegrd4', \
                 'htftegrd5', 'htftegrd6', 'htftegrd7', 'htftegrd8', \
                 'htftegrd9', 'htftegrd10', 'htftegrd11', 'htftegrd12']
#
#--- set them in the dictionary
#

GROUP_MSID_DICT = {
    'Compgradkodak': compgradkodak,
    'Compacispwr': compacispwr,
    'Compsimoffset': compsimoffset,
    'Gradablk': gradablk,
    'Gradahet': gradahet,
    'Gradaincyl': gradaincyl,
    'Gradcap': gradcap,
    'Gradfap': gradfap,
    'Gradfblk': gradfblk,
    'Gradhcone': gradhcone,
    'Gradhhflex': gradhhflex,
    'Gradhpflex': gradhpflex,
    'Gradhstrut': gradhstrut,
    'Gradocyl': gradocyl,
    'Gradpcolb': gradpcolb,
    'Gradperi': gradperi,
    'Gradsstrut': gradsstrut,
    'Gradtfte': gradtfte,
}

#--------------------------------------------------------------------------------
#-- run_comp_grad_data_update: a control function to update comp/grad related msid data
#--------------------------------------------------------------------------------

def run_comp_grad_data_update():
    """
    a control function to update comp/grad related msid data
    input: none, but use comp/grad msid lists and group name list
    output: <data_dir>/<gname>/<msid>_<dtye>_data.fits
    """
#
#--- set ending time
#
    today = time.strftime('%Y:%j:00:00:00', time.gmtime())
    atemp = re.split(':', today)
    eyear = int(float(atemp[0]))
    yday  = int(float(atemp[1]))
    etime = Chandra.Time.DateTime(today).secs
#
#--- go through all groups and their msid to update the data
#
    for group, msid_list in GROUP_MSID_DICT.items():
        print(f"Processing: {group}")
        try:
            update_comp_data(group, msid_list, eyear, etime)
        except:
            traceback.print_exc()
#
#--- compress the last year's fits file
#
    if yday >= 3 and yday < 5:
        os.system(f"gzip -fq {DEPOSIT_DIR}/*/*/*_full_data_{eyear - 1}.fits")

#--------------------------------------------------------------------------------
#-- update_comp_data: update comp/grad related msid data                       --
#--------------------------------------------------------------------------------

def update_comp_data(gname, msid_list, eyear, etime):
    """
    update comp/grad related msid data
    input:  gname       --- group name
            msid_list   --- a list of comp msids
            eyear       --- the last data entry year
            etime       --- today's date in seconds from 1998.1.1
    output: <data_dir>/<gname>/<msid>_<dtye>_data.fits
    """
    #make the group suibdirectory in case it doesn't exist
    os.makedirs(f"{DATA_DIR}/{gname}", exist_ok=True)
    for msid in msid_list:
#
#--- set sub-directory depending on msids
#
        mc  = re.search('grad', gname.lower())
        mc2 = re.search('comp', gname.lower())
        if mc is not None:
            if mc2 is not None:
                sub_dir = COMP_DIR
            else:
                sub_dir = GRAD_DIR
        else:
            sub_dir = COMP_DIR
#
#--- set limit data (a list of lists of limit values)
#
        alimit   = lim_dict[msid]

        for dtype in DTYPE:
            if dtype == 'long':
                ofile = msid + '_data.fits'
            else:
                ofile = msid + '_' + dtype + '_data.fits'
#
#--- database file name
#
            dfile = f"{DATA_DIR}/{gname}/{ofile}"
#
#--- If the FULL_GEN option is set to true, then remove this file to fully regenerate it
#
            if os.path.isfile(dfile) and FULL_GEN:
                os.remove(dfile)
#
#--- find the last entry time
#
            tstart = find_last_entry_time(dfile, dtype, etime)
            out    = Chandra.Time.DateTime(tstart).date
            atemp  = re.split(':', out)
            syear  = int(float(atemp[0]))
#
#--- to cover the case that the data collection time goes over two year, go between syear and eyear
#
            for year in range(syear, eyear+1):
                print(" Year: " + str(year) + " MSID: " + str(msid) + ' Dtype: ' + dtype)
#
#--- set the input fits file name
#
                fits = f"{sub_dir}/{gname}/{msid}_full_data_{year}.fits"
                if not os.path.isfile(fits):
                    fits = f"{fits}.gz"
                    if not os.path.isfile(fits):
                        print(f"Could not find {fits[:-3]} or gz.")
                        continue
#
#--- extract the data part needed and save in a fits file 
#
                tbhdu = extract_data_from_deposit(msid, fits, tstart, etime, dtype, alimit)
                if tbhdu == False:
                    print("Something went wrong for " + msid + ' in year: ' + str(year))
                    continue

                else:
                    #If not false, then managed to create the table HDU,
                    #save to a fits file and append to original table
                    appendfile = f"{DATA_DIR}/{gname}/{msid}_{dtype}_append.fits"
                    tbhdu.writeto(appendfile)
#
#--- append the new data part to the database
#
                    if os.path.isfile(dfile):
                        mfo.appendFitsTable(dfile, appendfile,'./temp.fits' ) 
                        cmd = 'mv -f ' + dfile + ' ' + dfile + '~'
                        os.system(cmd)
                        try:
                            cmd = 'mv ./temp.fits ' +  dfile
                            os.system(cmd)
                        except:
                            traceback.print_exc()
#
#--- check the file is actually updated. if not put back the old one 
#
                        if os.path.isfile(dfile):
                            cmd = 'rm -rf ' + dfile  + '~' 
                            os.system(cmd)
                        else:
                            cmd = 'mv -f ' + dfile + '~ ' + dfile
                            os.system(cmd)

                        os.system('rm -rf ' + appendfile)
#
#--- for the short time data, remove data older than 1.5 years
#--- for the week data, remove data older than 7 days
#
                        if dtype == 'short':
                            cut   = etime - 86400 * 548
                            remove_old_data_from_fits(dfile, cut)

                        elif dtype == 'week':
                            cut   = etime - 86400 * 7
                            remove_old_data_from_fits(dfile, cut)
                    else:
                        cmd = 'mv ' + appendfile + ' ' +  dfile
                        os.system(cmd)

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
#-- extract_data_from_deposit: extract data from deposit database and created data fits file 
#--------------------------------------------------------------------------------

def extract_data_from_deposit(msid, fits, start, stop, dtype, alimit):
    """
    extract data from deposit database and created data fits file
    input:  msid    --- msid
            fits    --- fits file name (with full path)
            start   --- period starting time in seconds from 1998.1.1
            stop    --- period ending time  in seconds from 1998.1.1
            dtype   --- data type:  week, short or  long (blank is fine)
            alimit  --- a list of lists of limit data table
    output: <msid>_<dtye>_data table HDU
    """
    period = dtype_to_period(dtype)
    fdata  = run_condtion_msid(msid, fits, start, stop, period, alimit, 'none')

    if fdata != []:
        tbhdu = create_fits_table(msid, fdata)
        return tbhdu
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
            traceback.print_exc()
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
                traceback.print_exc()
                ltable = alimit[k][3]['none']
            break 

    if ltable == []:
        ltable = [-9999998.0, 9999998.0, -9999999.0, 9999999.0]

    return ltable

#--------------------------------------------------------------------------------
#-- create_fits_file: create a fits file                                       --
#--------------------------------------------------------------------------------

def create_fits_table(msid, data):
    """
    create a fits file
    input:  msid    --- msid
            data    --- a list of list of data
    output: ./<msid>_<dtype>_data table HDU
    """
    cols    = COL_NAMES
    cols[1] = msid

    c1  = Column(name=cols[0],  format=COL_FORMAT[0],  array = data[0])
    c2  = Column(name=cols[1],  format=COL_FORMAT[1],  array = data[1])
    c3  = Column(name=cols[2],  format=COL_FORMAT[2],  array = data[2])
    c4  = Column(name=cols[3],  format=COL_FORMAT[3],  array = data[3])
    c5  = Column(name=cols[4],  format=COL_FORMAT[4],  array = data[4])
    c6  = Column(name=cols[5],  format=COL_FORMAT[5],  array = data[5])
    c7  = Column(name=cols[6],  format=COL_FORMAT[6],  array = data[6])
    c8  = Column(name=cols[7],  format=COL_FORMAT[7],  array = data[7])
    c9  = Column(name=cols[8],  format=COL_FORMAT[8],  array = data[8])
    c10 = Column(name=cols[9],  format=COL_FORMAT[9],  array = data[9])
    c11 = Column(name=cols[10], format=COL_FORMAT[10], array = data[10])
    c12 = Column(name=cols[11], format=COL_FORMAT[11], array = data[11])
    c13 = Column(name=cols[12], format=COL_FORMAT[12], array = data[12])
    c14 = Column(name=cols[13], format=COL_FORMAT[13], array = data[13])
    c15 = Column(name=cols[14], format=COL_FORMAT[14], array = data[14])
    c16 = Column(name=cols[15], format=COL_FORMAT[15], array = data[15])
        
    coldefs = pyfits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16])
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)

    return tbhdu

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
        tbhdu = create_fits_table(col_list[1], udata)
        tbhdu.writeto(fits)
        if os.path.isfile(sfits):
            os.remove(sfits)
    except:
        #If the try block fails to write a new fits file,
        #then move the saved ~ file back into place instead
        cmd = 'mv ' + sfits + ' ' + fits
        os.system(cmd)
        print(f'Error making :{fits}, moving back.')
        traceback.print_exc()

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-d", "--data", help = "Determine Data output file path.")
    parser.add_argument("--deposit", help = "Determine Deposit input file path.")
    parser.add_argument("-t",'--dtype', nargs = '*', required = False, choices = ['long', 'short', 'week'], help = "List of data types to generate.")
    parser.add_argument('--full',help = "Determine whether to full regenerate fits, or use the last recorded time entry.", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    
    if args.dtype:
        DTYPE = args.dtype

    if args.mode == 'test':
        #Smaller test subset
        GROUP_MSID_DICT = {
            'Compgradkodak': ['hrmaavg']
        }

        if args.full is not None:
            FULL_GEN = args.full
        if args.data:
            DATA_DIR = args.data
        else:
            DATA_DIR = f"{os.getcwd()}/test/outTest"
            os.makedirs(DATA_DIR, exist_ok=True)
        if args.deposit:
            DEPOSIT_DIR = args.deposit

        run_comp_grad_data_update()

    elif args.mode == "flight":
#
#--- Create a lock file and exit strategy in case of race conditions
#

        name = os.path.basename(__file__).split(".")[0]
        user = getpass.getuser()
        if os.path.isfile(f"/tmp/{user}/{name}.lock"):
            notification = f"Lock file exists as /tmp/{user}/{name}.lock at {time.strftime('%Y:%j:%H:%M:%S',time.localtime())}\n"
            notification += "Process already running/errored out. Check calling scripts/cronjob/cronlog. Killing old process."
            print(notification)
            with open(f"/tmp/{user}/{name}.lock") as f:
                pid = int(f.readlines()[-1].strip())
            #Kill old stalling process and remove corresponding lock file.
            os.remove(f"/tmp/{user}/{name}.lock")
            os.kill(pid,signal.SIGTERM)
            #Generate lock file for the current corresponding process
            os.system(f"mkdir -p /tmp/{user}; echo '{os.getpid()}' > /tmp/{user}/{name}.lock")
        else:
            #Previous script run must have completed successfully. Prepare lock file for this script run.
            os.system(f"mkdir -p /tmp/{user}; echo '{os.getpid()}' > /tmp/{user}/{name}.lock")
        
        try:
            run_comp_grad_data_update()
        except:
            traceback.print_exc()
#
#--- Remove lock file once process is completed
#
        os.system(f"rm /tmp/{user}/{name}.lock")