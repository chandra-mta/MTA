#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#           create_history_file.py: create count history file and the information file              #
#                                                                                                   #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                                   #
#                   last update: Mar 02, 2021                                                       #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
#import time

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/dir_list_py'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions   as mcf        #---- contains other functions commonly used in MTA scripts

#------------------------------------------------------------------------------------------------
#--- create_history_file: create count history file and the information file                  ---
#------------------------------------------------------------------------------------------------

def create_history_file(head):

    """
    create count history file and the information file containing current bad entry information
    input:  head                --- ccd, hccd, or col to indicate which data to handle
    output: <head>_ccd<ccd>_cnt --- count history data:
                                    <stime><><year:ydate><><cumlative cnt><><cnt for the day>
            <head>_ccd<ccd>_information --- current information of the bad entries. 
                                            Example, list of warm pixels, flickering pixels, 
                                                      totally new pixels, 
                                                      and all past and current warm pixels.
    """
    for ccd in range(0, 10):
#
#--- read data file head is either ccd, hccd, or col
#
        ifile = data_dir + 'hist_' + head + str(ccd)
        data = mcf.read_data_file(ifile)

        bad_dat_list = []                       #--- save all bad data as elements
        bad_dat_save = []                       #--- save all bad data as a list for each day

        stime = []
        ydate = []
        dcnt  = []                              #--- keep discreate count history
        ccnt  = []                              #--- keep cumulative count history
        new   = []                              #--- keep totally new bad entries in the last 5 days
        pcnt  = 0
        k     = 0
        tot   = len(data)

        for ent in data:
#
#--- read only data entries written in a correct format: <stime><><year>:<ydate><>:<bad_data>...
#
            atemp = re.split('<>', ent)
            chk1  = mcf.is_neumeric(atemp[0])
            btemp = re.split(':', atemp[1])
            chk2  = mcf.is_neumeric(btemp[1])

            if (chk1 == True) and (int(atemp[0]) > 0)  and (chk2 == True) and (int(btemp[1]) > 0):
                stime.append(atemp[0])
                ydate.append(atemp[1])
#
#--- check the bad data is recorded for the given day
#
                if head == 'ccd' or head == 'hccd':
                    m1 = re.search('\(', atemp[2])
                else:
                    btemp = re.split(':', atemp[2])                 #--- case for warm columns
                    if mcf.is_neumeric(btemp[len(btemp) -1]):
                        m1 = 'OK'
                    else:
                        m1 = None

                if m1 is not None:
                    btemp = re.split(':', atemp[2])
                    if btemp != '':
                        dcnt.append(len(btemp))
#
#--- for the last five days, check whether there are any totally new bad entries exists
#
                    if k > tot - 5:
                        for test in btemp:
                            chk = 0
                            for comp in bad_dat_list:
                                if test == comp:
                                    chk = 1
                                    continue
                            if chk == 0:
                                new.append(test)

                    bad_dat_list = bad_dat_list + btemp
                    out          = list(set(bad_dat_list))

                    pcnt         = len(out)
                    ccnt.append(pcnt)
                    bad_dat_save.append(btemp)
                else:
                    dcnt.append(0)
                    bad_dat_save.append([])
                    ccnt.append(pcnt)

            k += 1                                  #--- k is incremented to check the last 5 days
#
#--- find out which entries are warm/hot and flickering
#
        [warm, flick, b_list, p_list]=  find_warm_and_flickering(bad_dat_save)
#
#--- open output file to print current information
#
        ofile = data_dir + '/'+ head + str(ccd) + '_information'
        with open(ofile, 'w') as fo:
            fo.write("warm:\t")
            print_data(fo, warm)
    
            fo.write('flick:\t')
            print_data(fo, flick)
    
            fo.write('new:\t')
            out = list(set(new))
            print_data(fo, out)
    
            fo.write('past:\t')
            out = list(set(bad_dat_list))
            print_data(fo, out)
    
#
#--- open output file to print out count history
#
        line = ''
        for i in range(0, len(stime)):
            if i < 13:
                line = line + stime[i] + '<>' + ydate[i] + '<>' + str(ccnt[i]) + '<>'  
                line = line + str(dcnt[i]) + '<>0<>0\n'
            else:
                line = line + stime[i] + '<>' + ydate[i] + '<>' + str(ccnt[i]) + '<>'  
                line = line + str(dcnt[i]) + '<>'+ str(b_list[i-13]) + '<>' + str(p_list[i-13]) + '\n'

        ofile = data_dir + '' + head + str(ccd) + '_cnt'
        with  open(ofile, 'w') as fo:
            fo.write(line)

#-------------------------------------------------------------------------------------------------
#---  print_data: print out data                                                               ---
#-------------------------------------------------------------------------------------------------

def print_data(fo, data):

    """
    print out data
    input:  fo      --- file hander
            data    --- data
    output: data writting in the given format in the output file
    """
    tlen  = len(data)
    tlen1 = len(data) -1
    for i in range(tlen):
        if data[i] != '':
            fo.write(data[i])
            if i < tlen1:
                fo.write(' : ')
    fo.write('\n')

#-------------------------------------------------------------------------------------------------
#--- find_warm_and_flickering: determine which entries are bad or flickering                  ----
#-------------------------------------------------------------------------------------------------

def find_warm_and_flickering(rlist):

    """
    check the last two week amounts of data and determine which entries are bad or flickering
    if the data exit more than 70% of thetime, it is "warm" and if it exists more than 30% but less 
    than 70% of the time, it is flickering

    input:      rlist   --- a list of list of bad entries separated by each dom
    output:     warm    --- a list of warm entries
                flick   --- a list of flickering entries
    """
    tlen  = len(rlist)
    tlen1 = len(rlist)

    bad_cnt_hist           = []
    potential_bad_cnt_hist = []
    warm                   = []
    flick                  = []
    for j in range(13, tlen1):
        start = j - 13
        stop  = j + 1

        pix_list = []
        for k in range(start, stop):
            if len(rlist[k]) > 0:
                pix_list = pix_list + rlist[k]
#
#--- select out unique entries
#
        oset = list(set(pix_list))
        olen = len(oset)

        if olen > 0:
            mlist = [0 for x in range(0, olen)]
            for i in range(0, olen):
#
#--- count how many times the same entry appears in the data set
#
                for ent in pix_list:

                    if oset[i] == ent:
                        mlist[i] += 1
#
#--- if the data appears more than 70% of the time, it is warm, 
#--- if it appears more than 30% but less than 70% of the time, it is flickering
#
        warm  = []
        flick = []
        for i in range(0, olen):
            if oset[i] != '':
                rate = float(mlist[i]) / 14.0
    
                if rate > 0.7:
                    warm.append(oset[i])

                elif rate > 0.3:
                    flick.append(oset[i])
#
#--- add to real and potential bad point count history
#
        bad_cnt_hist.append(len(warm))
        potential_bad_cnt_hist.append(len(flick))
#
#--- return only the latest warm pix (col), flickering pix( col) data and history data
#
    return (warm, flick, bad_cnt_hist, potential_bad_cnt_hist)


#-------------------------------------------------------------

if __name__ == "__main__":

#
#--- warm pixel case
#
    head = 'ccd'
    create_history_file(head)
#
#--- hot pixel case
#
    head = 'hccd'
    create_history_file(head)
#
#--- warm column case
#
    head = 'col'
    create_history_file(head)

