#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#       extract_data.py:    extract data from mp reort and update saved data set        #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Jun 04, 2024                                                   #
#                                                                                       #
#########################################################################################

import os
import re
from datetime import datetime
import glob
from astropy.io import fits  as pyfits
import argparse
import platform

#
#--- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/Trending/Scripts'
MP_DIR = '/data/mta/www/mp_reports'
DATA_DIR = '/data/mta/Script/Trending/Trend'

#
#--- the name of data set that we want to extract
#--- (compephinkey removed Oct 9, 2018)
#
NAME_LIST = ['compaciscent', 'compacispwr', 'compgradkodak', \
             'compsimoffset', 'gradablk', 'gradahet', 'gradaincyl', 'gradcap',    \
             'gradfap', 'gradfblk', 'gradhcone', 'gradhhflex', 'gradhpflex',      \
             'gradhstrut', 'gradocyl', 'gradpcolb', 'gradperi', 'gradsstrut',     \
             'gradtfte']

#--------------------------------------------------------------------------------
#-- extract_data: extract the new data and update the data sets                --
#--------------------------------------------------------------------------------

def extract_data(name_list = NAME_LIST):
    """
    extract the new data and update the data sets.
    Input:  name_list   --- a list of the name of dataset that we want to extract/update
    Output: updated fits file (e.g. avg_compaciscent.fits)
    """

    for idir in name_list:

        fits_name = f"{DATA_DIR}/avg_{idir}.fits"
#
#--- find the last logged dom date
#
        try:
            lent      = find_last_entry_time(fits_name)
        except:
            cmd = 'cp ' + fits_name + '~ ' + fits_name
            os.system(cmd)
            try:
                lent      = find_last_entry_time(fits_name)
            except:
                print(fits_name)
                continue
#
#--- find available fits data from <mp_dir>
#
        mp_data = glob.glob(f"{MP_DIR}/*/{idir}/data/*_summ.fits")
    
        for ent in mp_data:
#
#--- find dom date
#
            dom = find_dom_from_mp_file(ent)
    
            if dom <= lent:
                continue
#
#--- now open fits file and get data
#
            else:
                cdict         = {}
                cdict['time'] = dom
    
                dout       = pyfits.getdata(ent, 1)
                cname_list = dout.field('name')
                avg_list   = dout.field('average')
                err_list   = dout.field('error')
     
                for k in range(0, len(cname_list)):
                    cname = cname_list[k].lower()
                    aname = cname + '_avg'
                    ename = cname + '_dev'
                    cdict[aname] = avg_list[k]
                    cdict[ename] = err_list[k]
     
                append_data(fits_name, cdict)


#--------------------------------------------------------------------------------
#-- find_dom_from_mp_file: find dom date from the directory path name         ---
#--------------------------------------------------------------------------------

def find_dom_from_mp_file(ent):
    """
    find dom date from the directory path name
    input:  ent --- full path to the file <mp_dir>/<date>/...
    output: dom --- day of mission
    """

    atemp = re.split(MP_DIR, ent)
    btemp = atemp[1].replace('/', '')
    year  = btemp[0] + btemp[1] + btemp[2] + btemp[3]
    month = btemp[4] + btemp[5]
    day   = btemp[6] + btemp[7]
    year  = int(float(year))
    month = int(float(month))
    day   = int(float(day))
    dom = ((datetime(year,month,day) - datetime(1999, 7, 22)) / 86400).seconds # day of mission

    return dom

#--------------------------------------------------------------------------------
#-- find_last_entry_time: find the last logged dom date                        --
#--------------------------------------------------------------------------------

def find_last_entry_time(fits):
    """
    find the last logged dom date
    """
    fdat = pyfits.open(fits)
    data = fdat[1].data
    lent = data[-1][0]

    return lent

#--------------------------------------------------------------------------------
#-- append_data: append new data row into the fits file                        --
#--------------------------------------------------------------------------------

def append_data(orig_fits, cdict):
    """
    append new data row into the fits file
    input:  orig_fits   --- fits file name
            cdict       --- dictionary of data: col name <---> value
    output: orig_fits   --- updated fits file
    """
#
#--- open the original fits file 
#
    fdat = pyfits.open(orig_fits)
    row  = fdat[1].data.shape[0]
#
#--- expand the data table to accomodate the new data. assume that only one new row of data
#
    nrow = row + 1
    hdu  = pyfits.BinTableHDU.from_columns(fdat[1].columns, nrows=nrow)
#
#--- add each data row
#
    for colname in fdat[1].columns.names:
        try:
            val = cdict[colname.lower()]
        except:
            val = -99.0

        hdu.data[colname][row:] = val
#
#--- write out the data
#
    if os.path.isfile("ztemp.fits"):
        os.remove("ztemp.fits")
    hdu.writeto('./ztemp.fits')
#
#--- check whether data are added correctly, before move 
#--- the temp fits file to the original fits file
#
    chk  = pyfits.open('ztemp.fits')
    cnt  = chk[1].data.shape[0]
    if cnt >= nrow:
        if os.path.isfile(orig_fits):
            os.system(f"mv -f {orig_fits} {orig_fits}~")
        os.system(f"mv -f ztemp.fits {orig_fits}")
    else:
        if os.path.isfile("ztemp.fits"):
            os.remove("ztemp.fits")


#-----------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", help = "Change output pathing.")
    parser.add_argument("-l", "--list", nargs = "+", help = "List of categories.")
    args = parser.parse_args()


    if args.mode == "test":
#
#--- Check that the running machine can view all neessary network directories
#
        machine = platform.node().split('.')[0]
        if machine not in ['r2d2-v', 'c3po-v', 'boba-v', 'luke-v']:
            parser.error(f"Need mta machine to view /data/mta/www. Current machine: {machine}")
#
#--- Repath directories
#
        BIN_DIR = f"{os.getcwd()}"
        OLD_DATA_DIR = DATA_DIR
        if args.path:
            DATA_DIR = args.path
        else:
            DATA_DIR = f"{BIN_DIR}/test/outTest"
        os.makedirs(DATA_DIR, exist_ok = True)

        os.system(f"cp {OLD_DATA_DIR}/*.fits {DATA_DIR}")

        if args.list:
            extract_data(args.list)
        else:
            extract_data()

    elif args.mode == "flight":

        extract_data()

