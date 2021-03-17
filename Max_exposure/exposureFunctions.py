#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#   exposureFunctions.py: collection of Max exposure related functions                  #
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
import getpass
import fnmatch
import time
import random
import Chandra.Time
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; \
                   source /home/mta/bin/reset_param', shell='tcsh')
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

import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#--------------------------------------------------------------------------------------------
#-- readExpData: read data from acis/hrc history data files                               ---
#--------------------------------------------------------------------------------------------

def readExpData(indir, inst):
    """
    read data from acis/hrc history data files
    input: indir    --- directory where the data locate
           inst     --- instruments hrci, hrcs, or acis data such as i_2_n_1 (for i_2_n_1_dff_out)
    output: a list of lists
                    [date,year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,\
                     max_apos,asig1, asig2, asig3, mean_dff,std_dff,min_dff, \
                     min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3]
    """
#
#--- monthly or cumulative
#
    save = []
    for iset in ('acc', 'dff'):
        m = re.search('hrc', inst)
#
#--- HRC data
#
        if m is not None:
            ifile = indir +  inst + '_' + iset + '_out'
#
#--- ACIS data
#
        else:
            ifile = indir +  inst + '_' + iset + '_out'

        out = read_exp_stat_data(ifile)
        save.append(out)
# 
#--- odata contains:
#---  [date,year,month,mean_acc,std_acc,min_acc,min_apos, max_acc,\
#---   max_apos,asig1, asig2, asig3, mean_dff,std_dff,min_dff, \
#---   min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3]
#
    odata = save[0] + save[1][3:]           #--- skipping date part from the second list
    return odata

#-------------------------------------------------------------------------------
#-- read_exp_stat_data: read a data file and seven column data lists          --
#-------------------------------------------------------------------------------

def read_exp_stat_data(ifile):
    """
    read a data file and seven column data lists
    input:  ifile   --- input file
    output: a list of lists of:
            date, mean, min, max, s1, s2, s3
    """
    data  = mcf.read_data_file(ifile)
    out   = mcf.separate_data_to_arrays(data)
#    avg   = out[2]
#    smin  = out[4]
#    smax  = out[6]
#    s1    = out[8]
#    s2    = out[9]
#    s3    = out[10]
##
##--- replace 'NA' into 0
##
#    avg   = [0 if str(x).lower() == 'na' else x for x in avg]
#    smin  = [0 if str(x).lower() == 'na' else x for x in smin]
#    smax  = [0 if str(x).lower() == 'na' else x for x in smax]
#    s1    = [0 if str(x).lower() == 'na' else x for x in s1]
#    s2    = [0 if str(x).lower() == 'na' else x for x in s2]
#    s3    = [0 if str(x).lower() == 'na' else x for x in s3]
    mout = []
    for ent in out:
        fixed = [0 if str(x).lower() == 'na' else x for x in ent]
        mout.append(fixed)
#
#--- time is in fractional year format
#
    date  = []
    for k in range(0, len(mout[0])):
        time  = float(mout[0][k]) + float(mout[1][k])/12.0 + 0.5
        date.append(time)
    
    rout  = [date]
    rout  = rout + mout

    return  rout

#-----------------------------------------------------------------------------------------
#--   clean_data: clean up and correct ACIS/HRC data.                                   --
#-----------------------------------------------------------------------------------------

def clean_data(idir, startYear = 'NA', startMonth = 'NA' , stopYear= 'NA', stopMonth = 'NA'):
    """
    clean up and correct ACIS/HRC data. if there is duplicated line, remove it. 
    if there are missing line add one (with NA)
    input:  idir        --- a full path to the directory to be checked
                            usually <data_dir>
            startYear   --- starting year
            startMonth  --- starting month
            stopYear    --- stopping year
            stopMonth   --- stopping month
    output: cleaned up data files
                example names of files:  i_2_n_3_dff_out / s_2_n_2_acc_out
    """
#
#--- if range is not defined, give them
#
    if startYear == 'NA':
        startYear = 1999
    if startMonth == 'NA':
        startMonth = 9

    out = time.strftime('%Y:%m', time.gmtime())
    atemp = re.split(':', out)
    cyear = int(atemp[0])
    cmon  = int(atemp[1])

    if stopYear == 'NA':
        stopYear = cyear
    if stopMonth == 'NA':
        stopMonth = cmon -1
        if stopMonth < 1:
            stopMonth = 12
            stopYear -= 1

    for itype in ('*_acc*', '*_dff*'):
#
#--- find file names
#
        for fout in os.listdir(idir):
            if fnmatch.fnmatch(fout , itype):
                ent = idir + fout
                
                data = mcf.read_data_file(ent)

                cyear  = startYear
                cmonth = startMonth
                pyear  = 0
                pmonth = 0
                line   = ''
    
                for aent in data:
                    atemp = re.split('\s+|\t+', aent)
                    year  = int(atemp[0])
                    month = int(atemp[1])
#
#--- if entry is duplicated, remove
#
                    if(year == pyear) and (month == pmonth):
                        pass

                    elif (year == cyear) and (month == cmonth):
                        line  = line + aent + '\n'
                        pyear = year
                        pmonth = month
                        cmonth += 1
                        if cmonth > 12:
                            cmonth = 1
                            cyear += 1
                            if(cyear == stopYear) and (cmonth > stopMonth):
                                break
#
#--- if entries are missing, add "NA" 
#
                    elif(year == cyear) and (month > cmonth):
                        for i in range (cmonth, month):
                            smon = str(i)
                            if i < 10:
                                smon = '0' + smon
                            line = line + str(year) + '\t' + smon 
                            line = line + '\tNA      NA      NA      NA      '
                            line = line + 'NA      NA      NA      NA\n'

                        line = line + aent + '\n'
     
                        pyear = year
                        pmonth = month
                        cmonth += 1
                        if cmonth > 12:
                            cmonth = 1
                            cyear += 1
                            if (cyear == stopYear) and (cmonth > stopMonth):
                                break
     
                with  open(ent, 'w') as fo:
                    fo.write(line)

#-----------------------------------------------------------------------------------------------------
#--- combine_image: combine two fits image files. combined fits file is renamed to the second fits ---
#-----------------------------------------------------------------------------------------------------

def combine_image(fits1, fits2):
    """
    combine two fits image files. 
    input : fits1 
            fits2  
    output: fits2   --- a combined fits file is moved to fits2
    """
    if os.path.isfile(fits2):
        try:
            cmd1 = "/usr/bin/env PERL5LIB="
            cmd2 = ' dmimgcalc infile=' + fits1 + ' infile2=' + fits2 
            cmd2 = cmd2 + ' outfile=mtemp.fits operation=add  clobber=yes'
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)

            mcf.rm_files(fits1)
#
#--- rename the combined fits image to "fits2"
#
            cmd = 'mv mtemp.fits ' + fits2
            os.system(cmd)
        except:
            mcf.rm_files(fits1)
            mcf.rm_files('mtemp.fits')
    else:
        cmd =  'mv ' + fits1 + ' ' + fits2
        os.system(cmd)

#-----------------------------------------------------------------------------------------------------
#--- create_image: create image file according to instruction                                      ---
#-----------------------------------------------------------------------------------------------------

def create_image(line, outfile):
    """
    create image file according to instruction "line".
    input:  line     --- instruction
            outfile  --- output file name
    output: outfile
            return 0/1  --- image is not created/created
    """
    cmd = ' dmcopy "' + line + '" out.fits option=image clobber=yes'
    bash(cmd,  env=ascdsenv)
    run_ascds(cmd)
    try:
        cmd = ' dmstat out.fits centroid=no > stest'
        run_ascds(cmd)
    except:
        pass
#
#--- if there is actually data, condense the iamge so that it won't take too much space
#
    sdata = mcf.read_data_file('stest', remove=1)

    val = 'NA'
    for lent in sdata:
        m = re.search('mean', lent)
        if m is not None:
            atemp = re.split('\s+', lent)
            val = atemp[1]
            break

    if val != 'NA' and float(val) > 0:
        cmd = 'mv out.fits ' + outfile
        os.system(cmd)

        return 1                        #--- the image file was created
    else:
        return 0                        #--- the image file was not created


#-------------------------------------------------------------------------------------
#-- make_month_list: create an appropriate month list for a given conditions      ----
#-------------------------------------------------------------------------------------

def make_month_list(year, startYear, stopYear, startMonth, stopMonth):
    """
    create an appropriate month list for a given conditions
    input:  year 
            startYear 
            stopYear 
            startMonth 
            stopMonth
    output: month_list  --- a list of month
    """
#
#--- fill up the month list
#
    month_list = []

    if startYear == stopYear:
#
#--- the period is in the same year
#
        month_list = range(startMonth, stopMonth+1)
    else:
#
#--- if the period is over two or more years, we need to set three sets of month list
#
        if year == startYear:
            month_list = range(startMonth, 13)
        elif year == stopYear:
            month_list = range(1,stopMonth+1)
        else:
            month_list = range(1,13)

    return month_list

#-------------------------------------------------------------------------------
#-- three_sigma_values: find 1, 2, and 3 sigma values of an image fits file   --
#-------------------------------------------------------------------------------

def three_sigma_values(fits_file):
    """
    find 1, 2, and 3 sigma values of an image fits file
    input:  fits_file   --- input image fits file name
    output: sigma1  --- one sigma value
            sigma2  --- two sigma value
            sigma3  --- three sigma value
    """
#
#-- make histgram
#
    cmd = ' dmimghist infile=' + fits_file
    cmd = cmd + '  outfile=outfile.fits hist=1::1 strict=yes clobber=yes'
    run_ascds(cmd)
    
    cmd = ' dmlist infile=outfile.fits outfile=' + zspace + ' opt=data'
    run_ascds(cmd)
    
    data = mcf.read_data_file(zspace, remove=1)
#
#--- read bin # and its count rate
#
    hbin = []
    hcnt = []
    vsum = 0
    
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        if mcf.is_neumeric(atemp[0]):
            hbin.append(float(atemp[1]))
            val = int(atemp[4])
            hcnt.append(val)
            vsum += val
#
#--- checking one, two and three sigma counts
#

    if len(hbin) > 0:
        v68    = int(0.68 * vsum)
        v95    = int(0.95 * vsum)
        v99    = int(0.997 * vsum)
        sigma1 = -999
        sigma2 = -999
        sigma3 = -999
        acc= 0
        for i in range(0, len(hbin)):
            acc += hcnt[i]
            if acc > v68 and sigma1 < 0:
                sigma1 = hbin[i]
            elif acc > v95 and sigma2 < 0:
                sigma2 = hbin[i]
            elif acc > v99 and sigma3 < 0:
                sigma3 = hbin[i]
                break
    
        return [sigma1, sigma2, sigma3]
    
    else:
        return[0, 0, 0]

#-------------------------------------------------------------------------------
#-- run_ascds: set ascds environment and run the command                      --
#-------------------------------------------------------------------------------

def run_ascds(cmd2):
    """
    set ascds environment and run the command
    input:  cmd2    --- command line
    output: results of the command
    """
    cmd1 = "/usr/bin/env  PERL5LIB= "
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)

#--------------------------------------------------------------------------------
#-- send_warning_email: sending out a warning email                            --
#--------------------------------------------------------------------------------

def send_warning_email(subject, content):
    """
    sending out a warning email
    input:  subject --- subject line
            content --- contents of emal
    output: emai sent out
    """
    with open(zspace, 'w') as fo:
        fo.write(content + '\n')

    cmd = 'cat ' + zspace
    cmd = cmd + '|mailx -s"Subject: ' + subject + ' " tisobe@cfa.harvard.edu'

#--------------------------------------------------------------------------------
#-- convert_fits_to_img: convert an image fits to a png image                  --
#--------------------------------------------------------------------------------

def convert_fits_to_img(fits, scale, color, outfile, chk=0):
    """
    convert an image fits to a png image
    input:  fits    --- image fits file name
            scale   --- scale, such sqrt, log, or linear
            color   --- color map name
            outfile --- output file name
            chk     --- if it is >0, 99.5% cut will be applied for the data
    output: outfile
            
    note: see: http://ds9.si.edu/doc/ref/command.html for option details
    """
    cmd = "/usr/bin/env PERL5LIB= "
    cmd = cmd + ' ds9 ' + fits + ' -geometry 760x1024 -zoom to fit '
    if chk > 0:
        cmd = cmd + '-scale mode 99.5  -scale ' + scale  +' -cmap ' + color 
    else:
        cmd = cmd + '-scale ' + scale  +' -cmap ' + color

    cmd = cmd + ' -colorbar yes -colorbar vertical -colorbar numerics yes -colorbar space value '
    cmd = cmd + ' -colorbar fontsize 12  -saveimage png ' + outfile + ' -exit'
    
    bash(cmd,  env=ascdsenv)
