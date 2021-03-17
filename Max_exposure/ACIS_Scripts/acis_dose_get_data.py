#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_get_data.py: obtain ACIS Evt 1 data for a month and combine them      #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Mar 09, 2021                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
#
#--- reading directory list
#
path = '/data/mta/Script/Exposure/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions as mcf
import exposureFunctions    as expf

#-----------------------------------------------------------------------------------
#-- acis_dose_get_data: extract ACIS evt1 data and create combined image file    ---
#-----------------------------------------------------------------------------------

def acis_dose_get_data(startYear='', startMonth='', stopYear='', stopMonth=''):
    """
    extract ACIS evt1 data from a month and create combined image file. 
    input:  startYear   --- year of starting time
            startMonth  --- month of starting time
            stopYear    --- year of stopping time
            stopMonth   --- month of stopping time
    """
    if startYear == '' or startMonth == ''or stopYear == '' or stopMonth == '':

        startYear  = raw_input('Start Year: ')
        startYear  = int(float(startYear))
        startMonth = raw_input('Start Month: ')
        startMonth = int(float(startMonth))

        stopYear   = raw_input('Stop Year: ')
        stopYear   = int(float(stopYear))
        stopMonth  = raw_input('Stop Month: ')
        stopMonth  = int(float(stopMonth))
#
#--- start extracting the data for the year/month period
#
    for year in range(startYear, stopYear+1):
#
#--- create a list of month appropriate for the year
#
        month_list =  expf.make_month_list(year, startYear, stopYear, startMonth, stopMonth)

        for month in month_list:
            smon = mcf.add_leading_zero(month)
            start = str(year) + '-' + smon + '-01T00:00:00'

            nextMonth = month + 1
            nyear =  year
            if nextMonth > 12:
                nextMonth = 1
                nyear += 1
            smon  = mcf.add_leading_zero(nextMonth)
            stop = str(nyear) + '-' + smon + '-01T00:00:00'
#
#--- using ar5gl, get a list of file names
#
            line = 'operation=browse\n'
            line = line + 'dataset=flight\n'
            line = line + 'detector=acis\n'
            line = line + 'level=1\n'
            line = line + 'filetype=evt1\n'
            line = line + 'tstart=' + start + '\n'
            line = line + 'tstop=' +  stop  + '\n'
            line = line + 'go\n'

            fitsList = mcf.run_arc5gl_process(line)
#
#--- extract each evt1 file, extract the central part, and combine them into a one file
#
            for  fits in fitsList:
                print("FITS File: " + fits)
                atemp = re.split('\s+', line)
                line  = 'operation=retrieve\n'
                line  = line + 'dataset=flight\n'
                line  = line + 'detector=acis\n'
                line  = line + 'level=1\n'
                line  = line + 'filetype=evt1\n'
                line  = line + 'filename=' + fits + '\n'
                line  = line + 'go\n'

                out   = mcf.run_arc5gl_process(line)
#
#--- check whether the fits file actually extracted and if so, ungip the file
#
                if len(out) < 1:
                    continue
                cmd = 'gzip -d ' + out[0]
                os.system(cmd)

                line = fits + '[EVENTS][bin tdetx=2800:5200:1, tdety=1650:4150:1][option type=i4]'
#
#--- create an image file
#
                ichk =  expf.create_image(line, 'ztemp.fits')
#
#--- combined images
#
                if ichk > 0:
                    expf.combine_image('ztemp.fits', 'total.fits')
            
                mcf.rm_files(fits)
                mcf.rm_files('ztemp.fits')
#
#--- rename the file
#
            lyear   = str(startYear)
            lmon    = mcf.add_leading_zero(startMonth)
            outfile = './ACIS_' + lmon + '_' + lyear + '_full.fits'
            cmd     = 'mv total.fits ' + outfile
            os.system(cmd)
#
#--- trim the extreme values
#
            upper = find_10th(outfile)
            if mcf.is_neumeric(upper):
                outfile2 = './ACIS_' + lmon + '_' + lyear + '.fits'
                cmd = ' dmimgthresh infile=' + outfile + ' outfile=' 
                cmd = cmd + outfile2 + ' cut="0:' + str(upper) + '" value=0 clobber=yes'
                expf.run_ascds(cmd)
            else:
                cmd = 'cp -f ' + outfile + ' ' + outfile2
                os.system(cmd)

            cmd   = 'gzip ' + outfile
            os.system(cmd)
#
#--- move full one to the data dir; keep other in <exc_dir> to be used to create cumlative files
#
            cmd   = 'mv ' + outfile + '* ' + mon_acis_dir + '/.'
            os.system(cmd)

#-----------------------------------------------------------------------------------
#-- find_10th: find 10th brightest value                                         ---
#-----------------------------------------------------------------------------------

def find_10th(fits_file):
    """
    find 10th brightest value    
    input: fits_file    --- image fits file name
    output: 10th brightest value
    """
#
#-- make histgram
#
    cmd = ' dmimghist infile=' + fits_file 
    cmd = cmd + '  outfile=outfile.fits hist=1::1 strict=yes clobber=yes'
    expf.run_ascds(cmd)

    cmd =' dmlist infile=outfile.fits outfile=./zout opt=data'
    expf.run_ascds(cmd)

    data = mcf.read_data_file('./zout', remove=1)
    mcf.rm_files('outfile.fits')
#
#--- read bin # and its count rate
#
    hbin = []
    hcnt = []

    for ent in data:
        try:
            atemp = re.split('\s+|\t+', ent)
            if (len(atemp) > 3) and mcf.is_neumeric(atemp[1])  \
                    and mcf.is_neumeric(atemp[2])  and (int(atemp[4]) > 0):
                hbin.append(float(atemp[1]))
                hcnt.append(int(atemp[4]))
        except:
            pass
#
#--- checking 10 th bright position
#
    try:
        j = 0
        for i in  range(len(hbin)-1, 0, -1):
            if j == 9:
                val = i
                break
            else:
#
#--- only when the value is larger than 0, record as count
#
                if hcnt[i] > 0:
                    j += 1

        return hbin[val]
    except:
        return 'I/INDEF'

#--------------------------------------------------------------------------------

if __name__ == '__main__':
    
    if len(sys.argv) > 4:
        startYear  = int(sys.argv[1])
        startMonth = int(sys.argv[2])
        stopYear   = int(sys.argv[3])
        stopMonth  = int(sys.argv[4])
    else:
        startYear  = ''
        startMonth = ''
        stopYear   = ''
        stopMonth  = ''

    acis_dose_get_data(startYear, startMonth, stopYear, stopMonth)


