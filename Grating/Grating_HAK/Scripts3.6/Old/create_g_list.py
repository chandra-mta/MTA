#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           create_g_list.py: create an input file (obs2html.lst) for idl code: obs2html.pro    #
#                              which generate grat index.html page                              #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Apr 04, 2018                                                           #
#                                                                                               #
#################################################################################################

import os
import re
import random
import numpy
import time

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few global variables
#
month_list    = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
data_location = '/data/mta_www/mta_grat/'
sot_directory = '/data/mta4/obs_ss/sot_ocat.out'

#----------------------------------------------------------------------------------------------
#-- create_g_list: create an input file (obs2html.lst) for idl code: obs2html.pro            --
#----------------------------------------------------------------------------------------------

def create_g_list():

    """
    create an input file (obs2html.lst) for idl code: obs2html.pro 
    Input:  none, but read from <data_location> and <sot_directory>
    Output: <data_lication>/obs2html.lst
    """
#
#--- read sot database
#
    [sot_obsid, sot_date, index_date] = get_obsdate()
#
#--- set a couple of length related parameters
#
    slen = len(sot_obsid)
    temp = re.split('\/', data_location)
    tlen = len(temp)
#
#--- create a list of paths to data depositories
#
    for month in month_list:
        cmd = 'ls -d ' + data_location +  month  + '*/* >> ' +  zspace
        try:
            os.system(cmd)
        except:
            pass
    
    f     = open(zspace, 'r')
    dlist = [line.strip() for line in f.readlines()]
    f.close()
    
    cmd = 'rm ' + zspace
    os.system(cmd)
    
    acis_l_obsid = []
    acis_l_date  = []
    acis_l_date2 = []
    acis_l_date3 = []
    acis_h_obsid = []
    acis_h_date  = []
    acis_h_date2 = []
    acis_h_date3 = []
    hrc_l_obsid  = []
    hrc_l_date   = []
    hrc_l_date2  = []
    hrc_l_date3  = []
    
    for ent in dlist:
#
#--- get starting date of the obsid from sot data/date lists
#
        temp  = re.split('\/', ent)
        try:
            float(temp[tlen])
        except:
            continue

        date  = temp[tlen-1]
        obsid = int(temp[tlen])

        date2 = ''
        idate = ''
        for i in range(0, slen):
            if obsid == sot_obsid[i]:
                date2 = sot_date[i]
                idate = index_date[i]
                break

#
#--- read the content of *html file
#
        cmd  = 'cat ' + ent + '/*.html > ' + zspace
        os.system(cmd)

        text = open(zspace, 'r').read()
    
        cmd = 'rm ' + zspace
        os.system(cmd)
#
#--- check the file contain the words "ACIS-S", "HRC", "HETG", or "LETG"
#
        chk1  = re.search('ACIS-S', text)  
        chk2  = re.search('HRC',    text)  
        chk3  = re.search('HETG',   text)  
        chk4  = re.search('LETG',   text)  
#
#--- according to the words contained in the file, determine which category 
#--- this observation belong to
#
        if chk1 is  not None:
            if chk3 is not None:
                acis_h_obsid.append(obsid)
                acis_h_date.append(date)
                acis_h_date2.append(date2)
                acis_h_date3.append(idate)
            elif chk4 is not None:
                acis_l_obsid.append(obsid)
                acis_l_date.append(date)
                acis_l_date2.append(date2)
                acis_l_date3.append(idate)
        elif chk2 is not None:
            if chk4 is not None:
                hrc_l_obsid.append(obsid)
                hrc_l_date.append(date)
                hrc_l_date2.append(date2)
                hrc_l_date3.append(idate)
#
#--- print out the results
#
    fout = data_location + 'obs2html.lst'
    fo   = open(fout, 'w')
    
    line = 'ACIS-S/LETG\n'
    fo.write(line)
    print_list(fo, acis_l_obsid, acis_l_date, acis_l_date2, acis_l_date3)
    
    line = 'ACIS-S/HETG\n'
    fo.write(line)
    print_list(fo, acis_h_obsid, acis_h_date, acis_h_date2, acis_h_date3)
    
    line = 'HRC-S/LETG\n'
    fo.write(line)
    print_list(fo, hrc_l_obsid,  hrc_l_date,  hrc_l_date2,  hrc_l_date3)

    fo.close()


#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

def print_list(fo, obsid, date, date2, date3):

    """
    print out a list of obsid and its observation date
    Input:  fo      --- write link
            obsid   --- a list of obsid
            date    --- a list of date (e.g., May14)
            date2   --- a list of date (e.g., 05/06/14)
            date3   --- a list of date (e.g., 20140506)
    Output: printing out the list (in the form of: 'May14 05/06/14 15661')
    """

    hold = []
#
#--- sort the list according to date3
#
    sorted_index = numpy.argsort(date3)
    obsid = [obsid[i] for i in sorted_index]
    date  = [date[i]  for i in sorted_index]
    date2 = [date2[i] for i in sorted_index]
    for i in range(0, len(obsid)):
        if date[i] != '' and date2[i] != '' and obsid[i] != '':
            line = date[i] + ' ' + date2[i] + ' ' + str(obsid[i]) + '\n'
            hold.append(line)
    hlen = len(hold)
#
#--- reverse the list so that the newest at the top
#
    for i in range(0, hlen):
        j = hlen - i -1
        fo.write(hold[j])

#------------------------------------------------------------------------------------
#-- get_obsdate: read sot database and make a list of obsids and observation dates --
#------------------------------------------------------------------------------------

def get_obsdate():

    """
    read sot database and make a list of obsids and its observation dates
    Input:  none, but read data from <sot_direcotry>
    Output: (obsid_list, start_date, index_date)
             where obsid_list: a list of obsids
                   start_date: a list of start date in the form of 05/23/14
                   index_date: a list of start date in the form of 20140523
    """

#
#--- read sot data
#
    f    = open(sot_directory, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    obsid_list = []
    start_date = []
    index_date = []
    for ent in data:
        temp = re.split('\^', ent)
        obsid = temp[1]
#
#--- check the data are valid
#
        try:
            atemp = re.split('\s+', temp[13])
            mon   = atemp[0]
            date  = atemp[1]
            year  = atemp[2][2] + atemp[2][3]
        except:
            continue
#
#--- convert month in letter into digit
#
        for i in range(0, 12):
            if mon == month_list[i]:
                mon = i + 1
                break
#
#--- two forms of starting date: 05/23/14 and 20140523
#
        lmon = str(mon)
        if int(mon) < 10:
            lmon = '0' + lmon
        ldate = str(date)
        if int(date) <  10:
            ldate = '0' + ldate

        dline = lmon + '/' + ldate + '/' + year
        iline = atemp[2] + lmon + ldate

        obsid_list.append(int(obsid))
        start_date.append(dline)
        index_date.append(iline)

    return (obsid_list, start_date, index_date)

#------------------------------------------------------------------------------------

if __name__ == '__main__':

    create_g_list()
