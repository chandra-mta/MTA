#!/proj/sot/ska3/flight/bin/python

#####################################################################################    
#                                                                                   #
#       run_fetch.py: extracting data from SKA engineering database                 #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Feb 01, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import Ska.engarchive.fetch as fetch
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
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
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

def get_data(msid, start, stop):
    """
    create an interactive html page for a given msid
    input:  msid    --- msid
            oup   --- group name
            start   --- start time
            stop    --- stop time
    output: ttime   --- a list of time data
            tdata   --- a list of data
    """
#    start = ecf.check_time_format(start)
#    stop  = ecf.check_time_format(stop)
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
#
#--- get limit data table for the msid
#
    try:
        uck   = udict[msid]
        if uck.lower() == 'k':
            tchk = 1
        else:
            tchk  = ecf.convert_unit_indicator(uchk)
    except:
        tchk  = 0

    glim  = ecf.get_limit(msid, tchk, mta_db, mta_cross)
#
#--- extract data from archive
#
    chk = 0
    try:
        out     = fetch.MSID(msid, start, stop)
        tdata   = out.vals
        ttime   = out.times
    except:
        tdata   = []
        ttime   = []


    return [ttime, tdata]

#-------------------------------------------------------------------------------------------

if __name__ == "__main__":

    [ttime, tdata] = get_data('1cbat', '2020:001:00:00:00', '2020:002:00:00:00')
    print("I AM HERE: " + str(len(ttime)))
