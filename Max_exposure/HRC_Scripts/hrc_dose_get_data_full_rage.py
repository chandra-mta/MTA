#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_get_data_full_rage.py: obtain HRC Evt 1 data for a month and create    #
#                                cumulative data fits files in multiple image files     #
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
import time
import random
import astropy.io.fits  as pyfits
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import exposureFunctions    as expf

#-----------------------------------------------------------------------------------------------
#--- hrc_dose_get_data: extract HRC evt1 data from a month and create cumulative data fits file -
#-----------------------------------------------------------------------------------------------

def hrc_dose_get_data(startYear='NA', startMonth='NA', stopYear='NA', stopMonth='NA'):
    """
    extract HRC evt1 data from a month and create cumulative data fits file. 
    input:  startYear   --- start year 
            startMonth  --- start month 
            stopYear    --- stop year 
            stopMonth   --- stop month
    output: image fits files for the month and cumulative cases
    """
#
#--- if the dates are not given, set them to the last month
#
    if startYear == 'NA':
        [stopYear, stopMonth, day] = mcf.today_date()

        startYear  = stopYear
        stopMonth -= 1
        startMonth = stopMonth
        if startMonth < 1:
            startMonth = 12
            startYear -= 1
#
#--- start extracting the data for the year/month period
#
    for year in range(startYear, stopYear+1):
        lyear = str(year)
        syear = lyear[2] + lyear[3]
#
#--- create a list of month appropriate for the year
#
        month_list = expf.make_month_list(year, startYear, stopYear, startMonth, stopMonth) 

        for month in month_list:
            smonth = mcf.add_leading_zero(month)
#
#--- output file name settings
#
            outfile_i = './HRCI_' + str(smonth) + '_' + str(lyear) + '.fits'
            outfile_s = './HRCS_' + str(smonth) + '_' + str(lyear) + '.fits'
#
#--- using ar5gl, get file names
#
            smonth = mcf.add_leading_zero(month)
            syear = str(year)
            start = syear + '-' + smonth + '-01T00:00:00'

            nextMonth = month + 1
            if nextMonth > 12:
                lyear     = year + 1
                nextMonth = 1
            else:
                lyear  = year                

            smonth = mcf.add_leading_zero(nextMonth)
            syear = str(lyear)
            stop  = str(lyear) + '-' + smonth + '-01T00:00:00'

            line = 'operation=browse\n'
            line = line + 'dataset=flight\n'
            line = line + 'detector=hrc\n'
            line = line + 'level=1\n'
            line = line + 'filetype=evt1\n'
            line = line + 'tstart=' + start + '\n'
            line = line + 'tstop=' +  stop  + '\n'
            line = line + 'go\n'

            fitsList = mcf.run_arc5gl_process(line)
#
#--- extract each evt1 file, extract the central part, and combine them into a one file
#
#--- set counters for how many hrc-i and hrc-s are extracted
#
            hrci_cnt = 0
            hrcs_cnt = 0
            for fitsName in fitsList:
                print("Fits file: " + fitsName)
                m = re.search('fits', fitsName)
                if m is None:
                    continue
                try:
                    line = 'operation=retrieve\n'
                    line = line + 'dataset=flight\n'
                    line = line + 'detector=hrc\n'
                    line = line + 'level=1\n'
                    line = line + 'filetype=evt1\n'
                    line = line + 'filename=' + fitsName + '\n'
                    line = line + 'go\n'
                    out  = mcf.run_arc5gl_process(line)

                    if len(out) < 1:
                        continue

                    ofits = out[0]
                    cmd   = 'gzip -d ' + ofits
                    os.system(cmd)

                    ofits = ofits.replace('.gz', '')
                except:
                    continue
#
#--- checking which HRC (S or I)
#
                hout     = pyfits.open(ofits)
                data     = hout[1].header
                detector = data['DETNAM']
                hout.close()
#
#--- creating the center part image
#                
                line = set_cmd_line(ofits, detector)
                ichk = expf.create_image(line, 'ztemp.fits')
#
#--- for HRC S
#
                if detector == 'HRC-S' and ichk > 0:
                    expf.combine_image('ztemp.fits', 'total_s.fits')
                    hrcs_cnt += 1
#
#--- for HRC I
#
                elif detector == 'HRC-I' and ichk > 0:
                    expf.combine_image('ztemp.fits', 'total_i.fits')
                    hrci_cnt += 1

                mcf.rm_files('out.fits')
                mcf.rm_files(ofits)
#
#--- move the file to a depository 
#
            if hrcs_cnt > 0:
                cmd = 'mv total_s.fits ' + web_dir + 'Month_hrc/' +  outfile_s
                os.system(cmd)
                cmd = 'gzip ' + web_dir + '/Month_hrc/*.fits'
                os.system(cmd)

            if hrci_cnt > 0:
                cmd = 'mv total_i.fits ' + web_dir + 'Month_hrc/' +  outfile_i
                os.system(cmd)
                cmd = 'gzip ' + web_dir + '/Month_hrc/*.fits'
                os.system(cmd)
            
            createCumulative(year, month, 'HRC-S', web_dir)
            createCumulative(year, month, 'HRC-I', web_dir)

#-----------------------------------------------------------------------------------------
#-- set_cmd_line: generate image creating command line for dmcopy                      ---
#-----------------------------------------------------------------------------------------

def set_cmd_line(fitsName, detector):
    """
    generate image creating command line for dmcopy 
    input:  fitsName    --- fits file name
            detector    --- HRC-I or HRC-S 
    output: line        --- command
    """
    if detector == 'HRC-I':
        xstart = '6144'
        xend   = '10239'
        ystart = '6144'
        yend   = '10239'
        mem    = '80'

    elif detector == 'HRC-S':
        xstart =  '0'
        xend   = '4095'
        ystart = '22528'
        yend   = '26623'
        mem    = '80'

    line = fitsName + '[EVENTS][bin rawx='+ xstart + ':' + xend 
    line = line + ':1, rawy=' + ystart + ':' + yend + ':1]'
    line = line + '[status=xxxxxx00xxxxxxxxx000x000xx00xxxx][option type=i4,mem='+ mem + ']'

    return line

#-----------------------------------------------------------------------------------------
#--- createCumulative: create cumulative hrc data                                       --
#-----------------------------------------------------------------------------------------

def createCumulative(year, month, detector,arch_dir):
    """
    create cumulative hrc data for a given year and month
    input:  year        --- year
            month       --- month
            detector    --- HRC-I or HRC-S
            arch_dir    --- archieve dir
    output: <cum_dir>/HRC<inst>_08_1999_<mm>_<yyyy>.fits.gz
    """
#
#--- find the previous period
#
    pyear = year
    pmonth = month -1

    if pmonth < 1:
        pmonth = 12
        pyear -= 1

    syear  = str(year)
    smonth = mcf.add_leading_zero(month)

    spyear  = str(pyear)
    spmonth = mcf.add_leading_zero(pmonth)

    if detector == 'HRC-I':
        inst = 'HRCI'
    else:
        inst = 'HRCS'

#
#--- set file names
#
    hrc   = inst + '_'         + smonth  + '_' + syear  + '.fits.gz'
    chrc  = inst + '_08_1999_' + spmonth + '_' + spyear + '.fits.gz'
    chrc2 = inst + '_08_1999_' + smonth  + '_' + syear  + '.fits'
#
#--- if the monthly file exists, reduce the size of the file before combine 
#--- it into a cumulative data
#
    cdir  = arch_dir + '/Month_hrc/'
    ifile = cdir + hrc

    if os.path.isfile(ifile):
        line = arch_dir + '/Month_hrc/' + hrc + '[opt type=i2,null=-99]'
        cmd  = ' dmcopy infile="' + line + '"  outfile="./ztemp.fits"  clobber="yes"'
        expf.run_ascds(cmd)

        cmd  = ' dmimgcalc infile=' + arch_dir + 'Cumulative_hrc/' + chrc 
        cmd  =  cmd  + ' infile2=ztemp.fits outfile =' + chrc2 + ' operation=add clobber=yes'
        expf.run_ascds(cmd)

        mcf.rm_files('./ztemp.fits')

        cmd  = 'gzip ' + chrc2
        os.system(cmd)

        cmd  = 'mv ' + chrc2 + '.gz ' + arch_dir + 'Cumulative_hrc/.'
        os.system(cmd)
#
#--- if the monthly fie does not exist, just copy the last month's cumulative data
#
    else:
        try:
            #test = arch_dir + 'Cumulative_hrc/' + chrc
            #with open(test, 'r') as f:
            #    xtest = f.read()

            cmd = 'cp ' + arch_dir + 'Cumulative_hrc/' + chrc + ' '  
            cmd = cmd   + arch_dir + 'Cumulative_hrc/'  + chrc2 + '.gz'
            print("I AM HERE CMD: " + str(cmd))
            #os.system(cmd)
        except:
            print("There are no last month cumulative hrc data")
            subject = 'Missing HRC cumulative data'
            content = 'It seems that the cummulative HRC from the last months are missing'
            expf.send_warning_email(subject, content)
            exit(1)

#--------------------------------------------------------------------------------

if __name__ == '__main__':
    
    if len(sys.argv) > 4:
        startYear  = int(sys.argv[1])
        startMonth = int(sys.argv[2])
        stopYear   = int(sys.argv[3])
        stopMonth  = int(sys.argv[4])
    else:
        startYear  = 'NA'
        startMonth = 'NA'
        stopYear   = 'NA'
        stopMonth  = 'NA'

    hrc_dose_get_data(startYear, startMonth, stopYear, stopMonth)

