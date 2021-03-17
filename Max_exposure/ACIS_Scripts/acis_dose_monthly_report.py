#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_monthly_report.py: create monthly report tables                       #
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
#
import mta_common_functions as mcf
import exposureFunctions    as expf

rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------
#-- acis_dose_monthly_report: create monthly report tables                ---
#----------------------------------------------------------------------------

def acis_dose_monthly_report(year='NA', month='NA'):
    """
    create monthly report tables 
    input:  year    --- year
            month   --- month
    output: monthly_diff_<mm>_<yyyy>
            monthly_acc_<mm>_<yyyy>
    """
#
#--- if year and/or month is not given, find the latest year month entry
#
    if year == 'NA' or month == 'NA':
        ifile = data_out + 'i_2_n_0_acc_out'
        data  = mcf.read_data_file(ifile)

        line  = data[-1]
        atemp = re.split('\s+|\t+', line)
        year  = int(atemp[0])
        month = int(atemp[1])

    syear = str(year)
    smon  = mcf.add_leading_zero(month)
    dline = ''
    aline = ''
#
#--- convert month in digit to month in letter
#
    lmon = mcf.change_month_format(month)
    lmon = lmon.lower()
#
#--- find monthly stat
#
    diff = mon_acis_dir + 'ACIS_' + smon + '_' + syear + '.fits.gz'
    (mean, std, dmin, dmax) = getstat(diff)

    dline = dline + 'ACIS_' + lmon + syear[2] + syear[3] + ' 6004901       '
    dline = dline + '%3.3f         %3.3f           %3.1f     %4d\n\n' % (mean, std, dmin, dmax)
#
#--- find cumulative stat
#
    acc  = cum_acis_dir + 'ACIS_07_1999_'  + smon + '_' + syear + '.fits.gz'
    (mean, std, amin, amax) = getstat(acc)

    aline =  aline + 'ACIS_total   6004901       '
    aline =  aline + '%3.3f         %3.3f           %3.1f   %6d\n\n' % (mean, std, amin, amax)
#
#--- now print stat for each section
#
    for inst in ('i', 's'):                     #--- acis i or s
        for ccd in (2, 3):                      #--- ccd 2 or 3 (i2/i3/s2/s3)
            dline = dline + '\n'
            aline = aline + '\n'

            for node in (0, 1, 2, 3):           #--- node

                for dtype in ('dff', 'acc'):    #--- monthly or cumulative

                    ifile = data_out + inst + '_' + str(ccd) +  '_n_' 
                    ifile = ifile    + str(node)  + '_' + dtype + '_out'
                    data  = mcf.read_data_file(ifile)

                    if year == 'NA' or month == 'NA':
                        out   = data[-1]
                        atemp = re.split('\s+', out)
                    else:
                        for ent in data:
                            atemp = re.split('\s+', ent)
                            if int(atemp[0]) == year and int(atemp[1]) == month:
                                break

                    mline  =  inst.upper() + str(ccd) + ' node ' + str(node) + '  262654\t'
                    mline  = mline + '%3.6f\t' % (float(atemp[2]))
                    mline  = mline + '%3.6f\t' % (float(atemp[3]))
                    mline  = mline + '%3.1f\t' % (float(atemp[4]))
                    mline  = mline + '%5.1f\n' % (float(atemp[6]))
                    if dtype == 'dff':
                        dline = dline + mline
                    else:
                        aline = aline + mline

    ofile = './monthly_diff_' + smon + '_' + syear
    with open(ofile, 'w') as fo:
        fo.write(dline)

    ofile = './monthly_acc_'  + smon + '_' + syear
    with open(ofile, 'w') as fo:
        fo.write(aline)

#----------------------------------------------------------------------------
#-- getstat: compute stat for fits image                                   --
#----------------------------------------------------------------------------

def getstat(fits):
    """
    compute stat for fits image
    input:  fits    --- fits file name
    output: mean    --- mean
            std     --- standard deviation
            vmin    --- min
            vmax    --- max
    """
    cmd = 'dmstat ' + fits + ' centroid=no > ' + zspace
    expf.run_ascds(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    for ent in data:
        m1 = re.search('min',   ent)
        m2 = re.search('max',   ent)
        m3 = re.search('mean',  ent)
        m4 = re.search('sigma', ent)

        if m1 is not None:
            atemp = re.split('\s+|\t+', ent)
            vmin  = float(atemp[1])
            continue

        if m2 is not None:
            atemp = re.split('\s+|\t+', ent)
            atemp = re.split('\s+|\t+', ent)
            vmax  = int(atemp[1])
            continue

        if m3 is not None:
            atemp = re.split('\s+|\t+', ent)
            mean  = float(atemp[1])
            continue

        if m4 is not None:
            atemp = re.split('\s+|\t+', ent)
            std   = float(atemp[1])
            continue

    return (mean, std, vmin, vmax)

#----------------------------------------------------------------------------

if __name__ == '__main__':
    
    acis_dose_monthly_report(year='NA', month='NA')
