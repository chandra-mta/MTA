#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#   interrupt_suppl_functions.py: collections of python scripts for interruption    #
#                                                                                   #
#               author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                   #
#               last update: Mar 09, 2021                                           #
#                                                                                   #
#####################################################################################

import math
import re
import sys
import os
import string
import astropy.io.fits  as pyfits
import time
import Chandra.Time
#
#--- pylab plotting routine related modules
#
from pylab import *
if __name__ == '__main__':
    mpl.use('Agg')

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions         as mcf
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- need a special treatment for the following msids
#
special_list = ['3FAMTRAT', '3FAPSAT', '3FASEAAT', '3SMOTOC', '3SMOTSTL', '3TRMTRAT']

#-------------------------------------------------------------------------------------
#--- find_collection_period: find start and ending time of data collecting/plotting period
#-------------------------------------------------------------------------------------

def find_collection_period(start_year, start_yday, stop_year, stop_yday):
    """
    for given, starting year/ydate, stopping year/ydate of the interruption, 
    set data collecting/plotting period. output are: data collecting starting 
    year, yday, stopping year, yday, plotting starting year, yday, plotting 
    stopping year, yday, and numbers of pannel needed to complete the plot.
    input:  start_year      --- starting year
            start_yday      --- starting ydate
            stop_year       --- stopping year
            stop_yday       --- stopping ydate
    output: pyear_start     --- interruption starting year adjusted for plotting
            period_start    --- interruption starting ydate adjusted for plotting
            pyear_stop      --- interruption stopping year adjusted for plotting
            period_stop     --- interruption stopping ydate adjusted for plotting
            plot_year_start --- plotting starting year
            plot_start      --- plotting starting ydate
            plot_year_stop  --- plotting stopping year
            plot_stop       --- plotting stopping ydate
            pannel_num      --- number of pannels needed
    """
#   
#--- set up extract time period; starting 2 days before the interruption starts
#--- and end 5 days after the interruption ends.
#

#
#--- check beginning
#
    pyear_start  = start_year
    period_start = start_yday - 2
#   
#--- for the case the period starts from the year before
#
    if period_start < 1:
        pyear_start -= 1

        if mcf.is_leapyear(pyear_start):
            base = 366
        else:
            base = 365

        period_start += base
#
#--- check ending. If the interruption does not finish in a 5 day period, extend
#--- the period at 5 day step wise until it covers the entier interruption period.
#
    if mcf.is_leapyear(pyear_start):
        base = 366
    else:
        base = 365

    if stop_year == pyear_start:
        pyear_stop  = pyear_start
        period      = int((stop_yday - period_start) / 5) + 1
        period_stop = period_start + 5 * period

        if period_stop > base:
            period_stop -= base
            pyear_stop  += 1
    else:
#   
#--- for the case stop_year > pyear_stop
#
        pyear_stop  = stop_year
        period      = int((stop_yday + base - period_start) /5 ) + 1
        period_stop = period_start + 5 * period - base

#
#--- setting plotting time span
#
    plot_year_start = pyear_start
    plot_start      = period_start
    plot_year_stop  = pyear_stop
    plot_stop       = period_stop

    if plot_year_stop > plot_year_start:

        if mcf.is_leapyear(plot_year_start):
            base = 366
        else:
            base = 365

        plot_year_stop = plot_year_start
        period_stop   += base
#
#--- the number of panels needed
#
    pannel_num    = period


    return (pyear_start,    period_start, pyear_stop,    period_stop,\
            plot_year_start, plot_start,   plot_year_stop, plot_stop, pannel_num)


#----------------------------------------------------------------------------------------
#--- sci_run_compute_gap: for given data, recompute the science run lost time excluding rad zones
#----------------------------------------------------------------------------------------

def sci_run_compute_gap(ifile = 'NA'):
    """
    for a given file name which contains a list like: 
        "20120313        2012:03:13:22:41        2012:03:14:13:57         53.3   auto"
    recompute the lost science time (excluding radiation zone) 
    input:  file   --- input file name
    output: file   --- update file
    """
#
#--- read rad_zone_list file
#
    rfile  = data_dir + '/rad_zone_list'
    rlist  = mcf.read_data_file(rfile)
#
#--- if file is not given (if it is NA), ask the file input
#
    if ifile == 'NA':
        ifile = input('Please put the intrrupt timing list: ')

    data = mcf.read_data_file(ifile)
#
#--- a starting date of the interruption in yyyy:mm:dd:hh:mm (e.g., 2006:03:20:10:30)
#--- there could be multiple lines of date; in that is the case, the scripts add 
#---the rad zone list to each date
#
    sline = ''
    for ent in data:

        if not ent:                         #--- if it is a blank line end the operation
            break

        etemp = re.split('\s+', ent)
        atemp = re.split(':', etemp[1])
        year  = atemp[0]
        month = atemp[1]
        date  = atemp[2]
#
#--- convert to sec1998
#
        ltime = time.strftime('%Y:%j:%H:%M:00', time.strptime(etemp[1], '%Y:%m:%d:%H:%M'))
        csec  = int(Chandra.Time.DateTime(ltime).secs)

        ltime = time.strftime('%Y:%j:%H:%M:00', time.strptime(etemp[2], '%Y:%m:%d:%H:%M'))
        csec2 = int(Chandra.Time.DateTime(ltime).secs)
#
#--- date stamp for the list
#
        list_date = str(year) + str(month) + str(date)
#
#--- add up the time overlap with radiatio zones with the interruption time period
#
        isum = 0
        for record in rlist:
            atemp = re.split('\s+', record)
            if list_date == atemp[0]:
                btemp = re.split(':', atemp[1])

                for period in btemp:

                    t1 = re.split('\(', period)
                    t2 = re.split('\)', t1[1])
                    t3 = re.split('\,', t2[0])
                    pstart = float(t3[0])
                    pend   = float(t3[1])

                    if pstart >= csec and  pstart < csec2:
                        if pend <= csec2:
                            diff = pend - pstart
                            isum += diff
                        else:
                            diff = csec2 - pstart
                            isum += diff
                    elif pstart < csec2 and pend > csec:
                        if pend <= csec2:
                            diff = pend - csec
                            isum += diff
                        else:
                            diff = csec2 - csec
                            isum += diff
                break
#
#--- total science time lost excluding radiation zone passe
#
        sciLost = (csec2 - csec - isum) / 1000

        line = etemp[0] + '\t' + etemp[1]    + '\t' + etemp[2] + '\t' 
        line = line     + "%.1f" %  sciLost  + '\t' + etemp[4] + '\n'

        sline = sline + line
#
#--- update the file 
#
    cmd = 'mv ' + ifile + ' ' + ifile + '~'
    os.system(cmd)

    with open(ifile, 'w') as fo:
        fo.write(sline)

#-----------------------------------------------------------------------------------------
#---remove_none_data: remove data which is missing and replaced as a very small value   --
#-----------------------------------------------------------------------------------------

def remove_none_data(x, y, lower, upper=1e99):

    """
    remove data which is missing and replaced as a very small value.
    """
    xnew = []
    ynew = []
    for i in range(0, len(y)):
       if y[i] > lower and y[i] < upper:
          xnew.append(x[i])
          ynew.append(y[i])

    return [xnew, ynew]

#--------------------------------------------------------------------
#--- plot_rad_zone: plotting radiation zone marker                ---
#--------------------------------------------------------------------

def plot_rad_zone(radZone, xmin, xmax, ymin):
    """
    For a given radiation zone information, plotting range and ymin 
    of the plotting area, mark radiation zones on the plot"
    input:  radZone --- a list of rad zone
            xmin    --- min of x range
            xmax    --- max of x range
            ymin    --- min of y range
    """

    for ent in radZone:
#
#---  format is e.g., 90.12321:90.9934 (start and end in ydate
#
        zone = re.split(':', ent)

        zstart = float(zone[0])
        zstop  = float(zone[1])

        if (zstart >= xmin) and (zstart < xmax):
            pstart = zstart
            if zstop < xmax:
                pstop = zstop
            else:
                pstop = xmax

            pstart += 0.02
            pstop  -= 0.02
            xzone   = [pstart, pstop]
            yzone   = [ymin, ymin]

            plt.plot(xzone, yzone, color='purple', lw=8)

        elif (zstart < xmin) and (zstop> xmin):
            pstart  = xmin
            pstop   = zstop

            pstart += 0.02
            pstop  -= 0.02
            xzone   = [pstart, pstop]
            yzone   = [ymin, ymin]

            plt.plot(xzone, yzone, color='purple', lw=8)

#--------------------------------------------------------------------
#--- read_rad_zone: read radiation zone period data              ----
#--------------------------------------------------------------------

def read_rad_zone(event):

    """
    read radiation zone data from 'rad_zone_list. Format: 
        20170906    (620993028,621049287):(621218556,621279255):(621447816,621506595)
    """

    ifile = data_dir + 'rad_zone_list'
    data  = mcf.read_data_file(ifile)

    radZone = []

    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        if atemp[0] == event:
            btemp = re.split(':', atemp[1])
            for line in btemp:
                ctemp = re.split('\(', line)
                dtemp = re.split('\)', ctemp[1])
                etemp = re.split('\,', dtemp[0])
                (year1, ydate1) = ctime_to_ydate(etemp[0])
                (year2, ydate2) = ctime_to_ydate(etemp[1])

                if year1 == year2:
                    line = str(ydate1) + ':' + str(ydate2)
                    radZone.append(line) 
                else:
                    if mcf.is_leapyear(year1):
                        base = 366
                    else:
                        base = 365

                    temp = ydate2 + base
                    line = str(ydate1) + ':' + str(temp)
                    radZone.append(line)

    return radZone

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

def dtime_to_ydate(dtime):
    """
    convert display time to year and ydate
    input:  dtime   --- time in <yyyy>:<mm>:<dd>:<hh>:<mm>
    oupput: [year, ydate]. ydate is in fractional day
    """
    out   = time.strftime("%Y:%j:%H:%M", time.strptime(dtime, '%Y:%m:%d:%H:%M'))
    dout  = re.split(':', out)
    year  = int(float(dout[0]))
    ydate = float(dout[1]) + float(dout[2]) / 24.0 + float(dout[3]) / 1440.0

    return [year, ydate]

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

def ctime_to_ydate(ctime):
    """
    convert chandra time into a day of year
    input:  ctime   --- time in seconds from 1998.1.1
    output: year    --- a year
            ydate   --- a day of year (fractional)
    """
    atime = Chandra.Time.DateTime(ctime).date
    btemp = re.split(':', atime)
    year  = float(btemp[0])
    ydate = float(btemp[1])
    hour  = float(btemp[2])
    mins  = float(btemp[3])
    sec   = float(btemp[4])
    
    ydate  = ydate + (hour/24.0 + mins/1440.0 + sec/86400.0)
    
    
    return [year, ydate]

#--------------------------------------------------------------------------
#--- make_tix_label: create a y tix label skipping every other interger  --
#--------------------------------------------------------------------------

def make_tix_label(min, max):

    'for given min and max, return a list of tix label skipping every other integer.'

    j = 1
    tix_row = []
    for i in range(int(min), int(max+1)):
        if j % 2 == 0:
            tix_row.append(i)
        else:
            tix_row.append('')
        j += 1

    return tix_row

#--------------------------------------------------------------------------------------
#--- use_arc5gl: extrat data using arc5gl                                           ---
#--------------------------------------------------------------------------------------

def use_arc5gl(operation, dataset, detector, level, filetype, start, stop, deposit = './'):
    """
    extract data using arc5gl. 
    input:  start ---   stop (year and ydate) 
            operation   --- (e.g., retrive) 
            dataset     ---(e.g. flight) 
            detector    --- (e.g. hrc) 
            level       --- (eg 0, 1, 2) 
            filetype    ---(e.g, evt1)
            start       --- starting time
            stop        --- stopping time
            deposit     --- where to deposit output fits file
    output: data        --- a list of fits file extracted
    """
#
#--- set arc5gl commend
#
    line = 'operation='       + operation  + '\n'
    line = line + 'dataset='  + dataset    + '\n'
    line = line + 'detector=' + detector   + '\n'
    line = line + 'level='    + str(level) + '\n'
    line = line + 'filetype=' + filetype   + '\n'

    line = line + 'tstart='   + str(start) + '\n'
    line = line + 'tstop='    + str(stop)  + '\n'

    line = line + 'go\n'

    data   = mcf.run_arc5gl_process(line)

    return data

#-----------------------------------------------------------------------------------
#--- use_dataseeker: extract data using dataseeker.pl                             ---
#-----------------------------------------------------------------------------------

def use_dataseeker(start, stop, msid):
    """
    extract data using dataseeker. 
    input:  start   --- starting time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            stop    --- stopping tine in <yyyy>:<ddd>:<hh>:<mm>:<ss>
            msid    ---- msid
    output: data    --- two column data (time and msid data)
    """
#
#--- convert time into chandra time
#
    start = Chandra.Time.DateTime(start).secs
    stop  = Chandra.Time.DateTime(stop).secs
#
#--- check a dummy 'test' file exists. it also needs param directory
#
    if not os.path.isfile('test'):
        os.system('touch ./test')

    cmd = 'rm -rf param'
    os.system(cmd)
    cmd = 'mkdir param'
    os.system(cmd)

    mcf.rm_files('./temp_out.fits')
#
#--- name must starts with "_"
#
    mc  = re.search('deahk',  msid.lower())
    mc2 = re.search('oobthr', msid.lower())
#
#--- deahk cases
#
    if mc is not None:
        atemp = re.split('deahk', msid)
        val   = float(atemp[1])
        if val < 17:
            name = 'rdb..deahk_temp.' + msid.upper() + '_avg'
        else:
            name = 'rdb..deahk_elec.' + msid.upper() + '_avg'
#
#--- oobthr cases
#
    elif mc2 is not None:
        name = 'mtatel..obaheaters_avg._' + msid.lower() + '_avg'
#
#--- special cases (see the list at the top)
#
    elif msid.upper() in special_list:
        name = msid.upper() + '_AVG'

    else:
        name = '_' + msid.lower() + '_avg'
#
#--- create dataseeker command
#
    cmd1 = '/usr/bin/env PERL5LIB="" '
    
    cmd2 = ' source /home/mta/bin/reset_param; '
    cmd2 = ' '
    cmd2 = cmd2 + ' /home/ascds/DS.release/bin/dataseeker.pl '
    cmd2 = cmd2 + ' infile=test  outfile=temp_out.fits  '
    cmd2 = cmd2 + ' search_crit="columns=' + name
    cmd2 = cmd2 + ' timestart='  + str(start)
    cmd2 = cmd2 + ' timestop='   + str(stop)
    cmd2 = cmd2 + ' " loginFile='+ house_keeping + 'loginfile '
    
    cmd  = cmd1 + cmd2
    bash(cmd,  env=ascdsenv)
    
    cmd  = 'rm /data/mta/dataseek* 2>/dev/null'
    os.system(cmd)


    [cols, tbdata] = read_fits_file('./temp_out.fits')
    mcf.rm_files('./temp_out.fits')

    time = list(tbdata.field('time'));
    vals = list(tbdata.field(cols[1]));

    data = [time, vals]

    return data

#----------------------------------------------------------------------------------
#-- read_fits_file: read table fits data and return col names and data           --
#----------------------------------------------------------------------------------

def read_fits_file(fits):
    """
    read table fits data and return col names and data
    input:  fits--- fits file name
    output: cols--- column name
    tbdata  --- table data
    to get a data for a <col>, use:
    data = list(tbdata.field(<col>))
    """
    hdulist = pyfits.open(fits)
#
#--- get column names
#
    cols_in = hdulist[1].columns
    cols= cols_in.names
#
#--- get data
#
    tbdata  = hdulist[1].data
    
    hdulist.close()
    
    return [cols, tbdata]

