#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#       hrc_dose_extract_stat_data_month.py: extract statistics from HRC S and I files          #
#                               output is avg, min, max,                                        #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: Mar 09, 2021                                                               #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import random
import time
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
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#----------------------------------------------------------------------------------
#--- comp_stat: compute statistics for the hrc image and print out the result    --
#----------------------------------------------------------------------------------

def comp_stat(ifile, year, month, out):
    """
    compute statistics for the hrc image and print out the result 
    input:  ifile   --- hrc image file, 
            year    --- year
            month   --- month
            out     --- output file name.
    output: out
    """
    if os.path.isfile(ifile):
#
#--- to avoid getting min value from the outside of the frame edge of a CCD, set threshold
#
        try:
            cmd = ' /bin/nice -n15 dmimgthresh infile=' + ifile 
            cmd = cmd + ' outfile=zcut.fits  cut="0:1.e10" value=0 clobber=yes'
            expf.run_ascds(cmd)

            cmd = ' dmstat  infile=zcut.fits  centroid=no >' + zspace
            expf.run_ascds(cmd)

            mcf.rm_files('./zcut.fits')

            data = mcf.read_data_file(zspace)
        except:
            data = []
        
        val = 'NA'
        for ent in data:
            ent.lstrip()
            m = re.search('mean', ent)
            if m is not None:
                atemp = re.split('\s+|\t', ent)
                val   = atemp[1]
                break

        if val != 'NA':
            (mean,  dev,  vmin,  vmax , min_pos_x,  min_pos_y,  max_pos_x,  max_pos_y) \
                                            = readStat(zspace)
            (sig1, sig2, sig3) = expf.three_sigma_values(ifile)

        else:
            (mean,  dev,  vmin,  vmax , min_pos_x,  min_pos_y,  max_pos_x,  max_pos_y)  \
                               = ('NA','NA','NA','NA','NA','NA','NA','NA')
            (sig1, sig2, sig3) = ('NA', 'NA', 'NA')

        mcf.rm_files(zspace)
    else:
        (mean,  dev,  vmin,  vmax , min_pos_x,  min_pos_y,  max_pos_x,  max_pos_y)  \
                           = ('NA','NA','NA','NA','NA','NA','NA','NA')
        (sig1, sig2, sig3) = ('NA', 'NA', 'NA')
#
#--- print out the results
#
    if mean == 'NA':
        line = '%d\t%d\t' % (year, month)
        line = line + 'NA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\n'
    else:
        line = '%d\t%d\t' % (year, month)
        line = line +  '%5.6f\t'   % (float(mean))
        line = line +  '%5.6f\t'   % (float(dev))
        line = line +  '%5.1f\t'   % (float(vmin))
        line = line +  '(%d,%d)\t' % (float(min_pos_x), float(min_pos_y))
        line = line +  '%5.1f\t'   % (float(vmax))
        line = line +  '(%d,%d)\t' % (float(max_pos_x), float(max_pos_y))
        line = line +  '%5.1f\t'   % (float(sig1))
        line = line +  '%5.1f\t'   % (float(sig2))
        line = line +  '%5.1f\n'   % (float(sig3))

    if os.path.isfile(out):
        with open(out, 'a') as f:
            f.write(line)
    else:
        with open(out, 'w') as f:
            f.write(line)

#----------------------------------------------------------------------------------
#--- readStat:  dmstat output file and extract data values.                     ---
#----------------------------------------------------------------------------------

def readStat(ifile):
    """
    read dmstat output file and extract data values. 
    input:  ifile   --- input file name
    output: (mean, dev, vmin, vmax, min_pos_x, min_pos_y, max_pos_x, max_pos_y)
    """
    mean      = 'NA'
    dev       = 'NA'
    vmin      = 'NA'
    vmax      = 'NA'
    min_pos_x = 'NA'
    min_pos_y = 'NA'
    max_pos_x = 'NA'
    max_pos_y = 'NA'

    data = mcf.read_data_file(ifile)

    for ent in data:
        ent.lstrip()
        atemp = re.split('\s+|\t+', ent)
        m1 = re.search('mean',  ent)
        m2 = re.search('sigma', ent)
        m3 = re.search('min',   ent)
        m4 = re.search('max',   ent)

        if m1 is not None:
            mean = float(atemp[1])
        elif m2 is not None:
            dev  = float(atemp[1])
        elif m3 is not None:
            vmin  = float(atemp[1])
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            min_pos_x = float(ctemp[1])
            min_pos_y = float(ctemp[2])
        elif m4 is not None:
            vmax  = float(atemp[1])
            btemp = re.split('\(', ent)
            ctemp = re.split('\s+|\t+', btemp[1])
            max_pos_x = float(ctemp[1])
            max_pos_y = float(ctemp[2])

    return (mean, dev, vmin, vmax, min_pos_x, min_pos_y, max_pos_x, max_pos_y)

#----------------------------------------------------------------------------------
#--- hrc_dose_extract_stat_data_month: compute HRC statistics                   ---
#----------------------------------------------------------------------------------

def hrc_dose_extract_stat_data_month(year, month):
    """
    compute HRC statistics: 
    input   year    --- year
            month   --- month
    output: <data_dir>/hrc<inst>_<acc/dff>_out
    """
    year  = int(year)
    month = int(month)

    syear  = str(year)
    smonth = mcf.add_leading_zero(month)
#
#--- center exposure map stat
#
    ifile = cum_hrc_dir  + '/HRCS_08_1999_' + smonth + '_' + syear + '.fits.gz'
    out   = data_out + '/hrcs_acc_out'
    comp_stat(ifile, year, month, out)

    ifile = mon_hrc_dir + '/HRCS_'          + smonth + '_' + syear + '.fits.gz'
    out   = data_out + '/hrcs_dff_out'
    comp_stat(ifile, year, month, out)

    ifile = cum_hrc_dir  + '/HRCI_08_1999_' + smonth + '_' + syear + '.fits.gz'
    out   = data_out + '/hrci_acc_out'
    comp_stat(ifile, year, month, out)

    ifile = mon_hrc_dir + '/HRCI_'          + smonth + '_' + syear + '.fits.gz'
    out   = data_out + '/hrci_dff_out'
    comp_stat(ifile, year, month, out)

#------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 2:
        year  = int(sys.argv[1])
        month = int(sys.argv[2])

        hrc_dose_extract_stat_data_month(year, month)
    else:
        print("Pleae provide year and month")
        exit(1)
