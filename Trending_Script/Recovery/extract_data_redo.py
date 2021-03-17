#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#           extract_data_redo.py:    extract data from archive                                          #
#                   modify lines around 124 - 133 to an appropriate period                              #
#                                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                       #
#               last update: Nov 20, 2014                                                               #
#                                                                                                       #
#########################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
from astropy.io import fits 
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')

#
#--- reading directory list
#
path = '/data/mta/Script/Trending/Recovery/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- the name of data set that we want to extract
#
#name_list = ['compaciscent', 'compacispwr', 'compephinkeyrates', 'compgradkodak',  'compsimoffset']    #---- comp*fits are not avaialble 
name_list = ['gradablk', 'gradahet', 'gradaincyl', 'gradcap', 'gradfap', 'gradfblk', 'gradhcone',\
             'gradhhflex', 'gradhpflex', 'gradhstrut', 'gradocyl', 'gradpcolb', 'gradperi',  \
             'gradsstrut', 'gradtfte']
#
#--- a couple of things needed
#
dare   = mcf.get_val('.dare',   dir = bindata_dir, lst=1)
hakama = mcf.get_val('.hakama', dir = bindata_dir, lst=1)

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def run_script(name_list):
    """
    extract the new data and update the data sets.
    Input:  name_list   --- a list of the name of dataset that we want to extract/update
    Output: updated fits file (e.g. avg_compaciscent.fits)
    """

    for dir in name_list:

        nfile = house_keeping + dir
        f     = open(nfile, 'r')
        data  = [line.strip() for line in f.readlines()]
        f.close()

        col_list = []
        for ent in data:
            atemp = re.split('\s+', ent)
            col_list.append(atemp[0])
#
#--- prepare the input for the case there is no data or bad data
#
        dlen  = len(col_list)
        dlen2 = 2 * dlen
        eline = '-999'
        for i in range(1, dlen2):
            eline = eline + '\t-999'
    
        outfile   = './Results/' + dir
#
#---  collect data
#
        try:
            collect_data(dir, col_list, outfile, eline)
        except:
            pass

#
#---- now creating fits file
#
        convert_to_fits(dir, col_list)

#--------------------------------------------------------------------------------------------------------
#-- CHANGE THE YEAR AND MONTH BELOW TO RECOVER THE DATA !!!       ---------------------------------------
#--------------------------------------------------------------------------------------------------------

def collect_data(dir, col_list, outfile,  eline):

#
#--- now loop through year and ydate
#
   for year in range(2015, 2017):
       for month in range(1, 13):

            if year == 2014 and month < 12:
                continue 

            chk = tcnv.isLeapYear(year)
            if(year == 2016) and (month > 6):
                break

            print "Date year: " + str(year) + ' month: ' + str(month) + ' : ' + str(dir)

            try:
                line = extract_new_data(dir, col_list, year, month)
            except:
                line = 'na'
                cmd = 'rm ./mta*fits* ./Working_dir/mta*fits*'
                os.system(cmd)

            fo = open(outfile, 'a') 
            if line != 'na':
                fo.write(line)
            else:
                dom  = int(tcnv.YdateToDOM(year, yday))
                line = str(dom) + '\t' + eline + '\n'
                fo.write(line)

            fo.close()


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def convert_to_fits(dir, col_list):

        file = './Results/' + dir
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
#
#--- define column names
#
        col_names =[]
        for ent in col_list:
            aname = ent + '_AVG'
            col_names.append(aname)
            ename = ent + '_DEV'
            col_names.append(ename)


        dlen  = len(col_list)
        dlen2 = 2 * dlen
        time  = []
        data_set = [[] for x in range(0, dlen2)]
        for ent in data:
            atemp = re.split('\t', ent)
            time.append(atemp[0])

            for j in range(1, len(atemp)):
                data_set[j-1].append(atemp[j])

        time  = numpy.array(time)
        col = fits.Column(name='Time', format='D', array=time)
        col_list = [col]

        for j in range(0, dlen2):
            data_set[j] = numpy.array(data_set[j])
            col = fits.Column(name=col_names[j], format='D', array=data_set[j])
            col_list.append(col)

        cols = fits.ColDefs(col_list)
        tbhdu = fits.BinTableHDU.from_columns(cols)            # --- version 0.42
#        tbhdu = fits.new_table(cols)                            # --- versuib 0.30
#
#---- create a bare minimum header
#
        prihdr = fits.Header()
        prihdu = fits.PrimaryHDU(header=prihdr)

        out_name = './Results/avg_' + dir + '.fits'
#
#--- create the fits file
#
        cmd = 'rm ' + out_name
        os.system(cmd)

        thdulist = fits.HDUList([prihdu, tbhdu])
        thdulist.writeto(out_name)


#--------------------------------------------------------------------------------------------------------
#-- extract_new_data: read out currently available data from mp report directory                       --
#--------------------------------------------------------------------------------------------------------


def extract_new_data(dir, col_list,  year, month):

    syear = str(year)
    smon  = str(month)
    if month < 10:
        smon = '0' + smon

    lyear  = year
    lmonth = month +1
    if lmonth > 12:
        lmonth = 1
        lyear += 1
    slyear = str(lyear)
    slmon  = str(lmonth)
    if lmonth < 10:
        slmon = '0' + slmon

    #start = smon  + '/01/' + syear[2]  + syear[3]  + ',00:00:00'
    #stop  = slmon + '/01/' + slyear[2] + slyear[3] + ',00:00:00'
    start = syear + '-' + smon + '-01T00:00:00'
    stop  = slyear + '-' + slmon + '-01T00:00:00'

    print "\tPeriod: " + start + '<--->' + stop

    out   =  extract_new_data_sub(dir, col_list,  start, stop, year, month)
    if out != 'na':
        line = out
    else:
        line = ''

    return line

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def extract_new_data_sub(dir, col_list,  start, stop, year, month):

#
#---  extract data 
#
    line = 'operation=retrieve\n'
    line = line + 'dataset = mta\n'
    line = line + 'detector = grad\n'
    line = line + 'level = 0.5\n'
    line = line + 'filetype =' + dir   + '\n'
    line = line + 'tstart='    + start + '\n'
    line = line + 'tstop='     + stop  + '\n'
    line = line + 'go\n'
    fo = open(zspace, 'w')
    fo.write(line)
    fo.close()

    cmd1 = "/usr/bin/env PERL5LIB="
    #cmd2 =  '  echo ' +  hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i' + zspace
    cmd2 =  ' /proj/axaf/simul/bin/arc5gl -user isobe  -script ' + zspace
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
    mcf.rm_file(zspace)
    cmd  = 'mv *gz ./Working_dir/.'
    os.system(cmd)

    cmd = 'gzip -d ./Working_dir/*.gz'
    os.system(cmd)

    cmd  = 'ls ./Working_dir/*.fits > ' + zspace
    os.system(cmd)
    f    = open(zspace, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    mcf.rm_file(zspace)

    if len(data) == 0:
        return 'na'
#
#--- extract each column data and stored in arrays
#
    elen = len(col_list)
    dat_save = [[] for x in range(0, elen)]
    time_dat = [] 

    for file in data:
        dout = fits.getdata(file, 1)
        time = dout.field('time')
        for ent in time:
            time_dat.append(ent)

        for k in range(0, elen):
            col = col_list[k]
            sta = 'ST_' + col
            val = dout.field(col)
            chk = dout.field(sta)
            for j in range(0, len(chk)):
                if chk[j] >= 0:
                    dat_save[k].append(val[j])
#
#--- set the beginning of the and the end of the first day of the data
#
    ydate = tcnv.findYearDate(year, month, 1)
    tent  = str(year) + ':' + str(ydate) + ':00:00:00'
    begin = tcnv.axTimeMTA(tent)

    smonth = month + 1
    syear  = year
    if smonth > 12:
        smonth = 1
        syear += 1
    ydate = tcnv.findYearDate(syear, smonth, 1)
    tent  = str(syear) + ':' + str(ydate) + ':00:00:00'
    stop = tcnv.axTimeMTA(tent)

    end   = begin + 86400
    if end > stop:
        end = stop

    dom   = int(tcnv.stimeToDom(begin))
    sline = str(dom)

    dsumming= [[] for x in range(0, elen)]
#
#--- find mean and std of each columns
#
    for k in range(0, len(time_dat)):
        if time_dat[k] >= begin and time_dat[k] < end:
            for i in range(0, elen):
                dsumming[i].append(dat_save[i][k])
        elif time_dat[k] < begin:
            continue
        elif time_dat[k] >= end:
            for i in range(0, elen):
                narray = numpy.array(dsumming[i])
                avg    = numpy.mean(narray)
                avg    = '%.4f' % round(avg, 4)
                err    = numpy.std(narray)
                err    = '%.4f' % round(err, 4)
                sline = sline + '\t' + str(avg) + '\t' + str(err)

            sline = sline + '\n'
#
#--- reintialize for the next day
#
            begin += 86400
            if begin >= stop:
                break
            end   = begin + 86400
            if end > stop:
                end = stop
            dom   = int(tcnv.stimeToDom(begin))

            sline = sline + str(dom)
            dsumming= [[] for x in range(0, elen)]

    cmd = 'rm ./Working_dir/*.fits*'
    os.system(cmd)

    return sline


#-----------------------------------------------------------------------

if __name__ == "__main__":

    run_script(name_list)


