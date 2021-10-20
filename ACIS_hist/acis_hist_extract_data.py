#!/usr/bin/env /data/mta/Script/Python3.9/bin/python3

#####################################################################################################
#                                                                                                   #
#   acis_hist_extract_data.py: extract acis histgram data and estimates Mn, Al, and Ti K-alpha line #
#                              parameters                                                           #
#                                                                                                   #
#                       author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                                   #
#                       last update: Oct 20, 2021                                                   #
#                                                                                                   #
#####################################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import time
import random
import astropy.io.fits as pyfits
from astropy.table import Table
from scipy.optimize import curve_fit
import matplotlib as mpl

if __name__ =='__main__':
    mpl.use('Agg')
#
#--- read argv
#
try:
    option, remainder = getopt.getopt(sys.argv[1:], 't:m:y:d:h',['test','manual','date=', 'help'])
except getopt.GetoptError as err:
    print (str(err))
    sys.exit(2)

optin       = 0
manual      = ''
year        = ''
month       = ''
for opt, arg  in option:

    if opt in ('-m', '--manual'):
        manual = 'yes'
        optin  = 1

    if opt in ('-d', '--date'):
        date  = arg
        temp  = re.split('\:', date)
        year  = int(temp[0])
        month = int(temp[1])
        optin = 1

    if opt in ('-h', '--help'):
        print("\n\n")
        print("Usage:  acis_hist_extract_data.py <option>")
        print("options:")
        print("     --manual: ask year and month")
        print("     --date=<year>:<month>    extract the result")
        print("               for given year and month")
        exit(1)
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/Acis_hist/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- add an extra dir name
#
dir_name = data_dir + 'Dist_data/'
sys.path.append(mta_dir)
sys.path.append(bin_dir)
sys.path.append(sp_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
#--- mta common functions
#
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- arc5gl user name
#
arc_user = 'isobe'

#------------------------------------------------------------------------------------
#---- acis_hist_extract_data: extract acis histgram data                           --
#------------------------------------------------------------------------------------

def acis_hist_extract_data(year, month):
    """
    extract acis histgram data
    input:  year    --- year
            month   --- month
    output: <data_dir>/ccd<ccd>_node<node>_<lpos>
    """
#
#--- clean up and/or create working directries
#
    if os.path.isdir(exc_dir):
        cmd = 'rm  -f ' + exc_dir + '*.fits* 2>/dev/null'
    else:
        cmd = 'mkdir -p ' + exc_dir
    os.system(cmd)

    t_dir = exc_dir + 'Temp_dir'
    if os.path.isdir(t_dir):
        cmd = 'rm  -f ' + t_dir + '/* 2>/dev/null'
    else:
        cmd = 'mkdir -p ' + t_dir
    os.system(cmd)
#
#--- define extracting period in seconds from 1.1.1998
#
    end_year  = year
    end_month = month + 1

    if end_month > 12:
        end_month = 1
        end_year += 1

    cmon   = str(month)
    if month < 10:
        cmon = '0' + cmon
    sdate  = str(year) + ':'+ cmon + ':01:00:00:00'
    pstart = mcf.convert_time_to_stime(sdate, tformat='%Y:%m:%d:%H:%M:%S')

    cmon   = str(end_month)
    if end_month < 10:
        cmon = '0' + cmon
    pdate  = str(end_year) + ':'+ cmon + ':01:00:00:00'
    pend   = mcf.convert_time_to_stime(pdate, tformat='%Y:%m:%d:%H:%M:%S')

    mdate  = 0.5 * (pstart + pend)
#
#--- extract sim position information
#
    twoarray = extract_sim_position(year, pstart, pend)

    sim_time = twoarray[0]
    sim_pos  = twoarray[1]
#
#----extract acis hist data from archive using arc5gl
#
    data_list = use_arc5gl_acis_hist(year, month, end_year, end_month)
#
#--- create data array: histogram row: 4000, ccd #: 10, node #: 4, position: 0, 1
#
    hdata    = numpy.zeros((4000, 10, 4, 2))
    duration = numpy.zeros((10, 4, 2))
#
#--- go though each extracted acis hist data
#
    for ifile in data_list:
        atemp = re.split('\/', ifile)
        fname = atemp[len(atemp)-1]
        fname = fname.replace('.fits', '')
#
#--- extract head info
#
        ccd_info = extract_head_info(ifile)
        [fep, ccd, node, pblock, tstart, tstop, expcount, date_obs, date_end] = ccd_info
        tdiff  = float(tstop) - float(tstart)
        ccd    = int(ccd)
#
#--- we need to check only ccd = 1, 2, 3, 6, and 7
#
        if ccd in [0, 4, 5, 8, 9]:
            mcf.rm_files(ifile)
            continue

        pblock = int(pblock)
        tstart = int(tstart)
        tstop  = int(tstop)
        if pblock in [2334740, 2342932, 2334756, 2342948]:
            pass
        else:
            continue
#
#--- find average sim position
#
        sim_info = find_sim_position(sim_time, sim_pos, tstart, tstop)
        [sim_avg, sim_min, sim_max] = sim_info
#
#--- for the case that the sim is at the external calibration source position
#
        if (sim_min > -100800 and sim_min < -98400) and (sim_max > -100800 and sim_max < -98400):
#
#
#--- pblock values were changed in year 2012 (2012.1.1 == 441763197). ---------
#
            if float(tstart) < 441763197:
#
#--- ccd rows are between 801 and 1001 before Year 2012
#
                if pblock == 2334740:
                    hist_data = extract_hist_data(ifile)
                    duration[ccd][node][1] += tdiff

                    for i in range(0, 4000):
                        hdata[i][ccd][node][1] += hist_data[i]
#
#--- ccd rows are between 21 and 221 before Year 2012
#
                elif pblock == 2342932:
                    hist_data = extract_hist_data(ifile)
                    duration[ccd][node][0] += tdiff

                    for i in range(0, 4000):
                        hdata[i][ccd][node][0] += hist_data[i]
#
#--- after 2012.1.1 ---------
#
            else:
#
#--- ccd rows are between 801 and 1001 from Year 2012
#
                if pblock == 2334756:
                    hist_data = extract_hist_data(ifile)
                    duration[ccd][node][1] += tdiff

                    for i in range(0, 4000):
                        hdata[i][ccd][node][1] += hist_data[i]
#
#--- ccd rows are between 21 and 221 from Year 2012
#
                elif pblock == 2342948:
                    hist_data = extract_hist_data(ifile)
                    duration[ccd][node][0] += tdiff

                    for i in range(0, 4000):
                        hdata[i][ccd][node][0] += hist_data[i]

        mcf.rm_files(ifile)
#
#--- now fit the parameters for a combined data set
#
    test_out = []
    for pos in(0, 1):
        for ccd in (1, 2, 3, 6, 7):
            for node in range(0, 4):
                darray = [0 for x in range(0, 4000)]
                dsum   = 0
                for i in range(0, 4000):
                    darray[i] = hdata[i][ccd][node][pos]
                    dsum     += hdata[i][ccd][node][pos]
                if dsum > 10:
                    peak_info = find_peaks(darray)

                    if pos == 0:
                        lpos = 'low'
                    else:
                        lpos = 'high'

                    ifile = data_dir + 'ccd' + str(ccd) + '_node' + str(node) + '_' + lpos
                    with open(ifile, 'a') as fo:
                        line = str(year) + ':' + str(month) + '\t'+ str(mdate) + '\t'
                        line = line + str(peak_info[0]) + '\t' +  str(peak_info[9])  + '\t'
                        line = line + str(peak_info[1]) + '\t' +  str(peak_info[10]) + '\t'
                        line = line + str(peak_info[2]) + '\t' +  str(peak_info[11]) + '\t'
                        line = line + str(peak_info[3]) + '\t' +  str(peak_info[12]) + '\t'
                        line = line + str(peak_info[4]) + '\t' +  str(peak_info[13]) + '\t'
                        line = line + str(peak_info[5]) + '\t' +  str(peak_info[14]) + '\t'
                        line = line + str(peak_info[6]) + '\t' +  str(peak_info[15]) + '\t'
                        line = line + str(peak_info[7]) + '\t' +  str(peak_info[16]) + '\t'
                        line = line + str(peak_info[8]) + '\t' +  str(peak_info[17]) + '\t'
                        line = line + str(duration[ccd][node][pos]) + '\n'
                        fo.write(line)
    
                    lmonth = str(month)
                    if month < 10:
                        lmonth = '0' + lmonth
                    fname = 'hist_' + str(year) + '_' + lmonth
    
                    eparam = peak_info[0:9]
    
                    plot_fit(darray, eparam, fname, ccd, node, lpos)

#------------------------------------------------------------------------------------
#--- extract_sim_position: find sim position from comprehensive_data_summary      ---
#------------------------------------------------------------------------------------

def extract_sim_position(year, period_start, period_end):
    """
    extract sim position information from comprehensive_data_summary data file
    input: year          --- year (in form of 2012) 
            period_start --- start time in seconds from 1.1.1998
            period_end   ---  stop time  in seconds from 1.1.1998
    output: time         --- (seconds from 1.1.1998) 
            sim_position
    """
    sim_time = []
    sim_pos  = []

    ifile = mj_dir + '/comprehensive_data_summary' + str(year)
    data  = mcf.read_data_file(ifile)

    for ent in data:
        atemp = re.split('\s+|\t+', ent)

        try:
            tinsec = mcf.convert_time_to_stime(atemp[0], tformat='%Y:%j:%H:%M:%S')
        except:
            continue

        if tinsec >= period_start and tinsec < period_end:
            sim_time.append(float(tinsec))
            sim_pos.append(float(atemp[1]))

    return [sim_time, sim_pos]

#------------------------------------------------------------------------------------
#--- use_arc5gl_acis_hist: using arc5gl to extract acis hist data                 ---
#------------------------------------------------------------------------------------

def use_arc5gl_acis_hist(year, month, end_year, end_month):

    '''
    using arc5gl, extreact acis hist data
    input: year, month, end_year, end_month (the last two are in sec from 1.1.1998)
    output: acis hist data in fits files saved in exc_dir/Temp_dir
    '''
#
#--- prep for output files
#
    tdir = exc_dir + 'Temp_dir'
    mcf.mk_empty_dir(tdir)
#
#--- write a command file
#
    with  open(zspace, 'w') as f:
        f.write("operation=retrieve\n")
        f.write("dataset=flight\n")
        f.write("detector=acis\n")
        f.write("level=0\n")
        f.write("filetype=histogr\n")
    
        lmon = str(month)
        if month < 10:
            lmon = '0' + lmon
        lyear = str(year)
        line = 'tstart=' + lyear + '-' +  lmon + '-01T00:00:00\n'
        f.write(line)
     
        lmon = str(int(end_month))
        if end_month < 10:
            lmon = '0' + lmon
        lyear = str(end_year)
        line = 'tstop=' + lyear + '-' +  lmon + '-01T00:00:00\n'
        f.write(line)
        f.write("go\n")
#
#--- run arc5gl
#
    try:
        cmd =  'cd ' + exc_dir + '; /proj/sot/ska/bin/arc5gl -user ' + arc_user + ' -script ' + zspace
        os.system(cmd)
    except:
        cmd1 = "/usr/bin/env PERL5LIB= "
        cmd2 = '  cd ' + exc_dir + '; /proj/axaf/simul/bin/arc5gl -user ' + arc_user + ' -script ' + zspace
        os.system(cmd2)

    mcf.rm_files(zspace)
#
#--- check whether the files are extracted. if not just exit.
#
    cmd = 'ls ' + exc_dir + '* > ' + zspace
    os.system(cmd)
    chk = open(zspace, 'r').read()
    mcf.rm_files(zspace)

    m  = re.search('fits.gz', chk)
    if m is None:
        exit(1)

    if mcf.check_file_with_name(exc_dir, 'fits') == False:
        exit(1)

    cmd = 'mv ' + exc_dir + '*fits.gz '  + exc_dir + 'Temp_dir/.'
    os.system(cmd)
    cmd = 'gzip -d ' + exc_dir + 'Temp_dir/*.gz'
    os.system(cmd)
#
#--- make a list of extracted fits files
#
    cmd = 'ls ' + exc_dir + 'Temp_dir/*fits > ' + zspace
    os.system(cmd)

    data = mcf.read_data_file(zspace, remove=1)

    return data

#------------------------------------------------------------------------------------
#--- extract_head_info: extract information from fits head descriptions           ---
#------------------------------------------------------------------------------------

def extract_head_info(ifile):
    """
    extreact information about the data from the fits file
    input:  ifile    ---fits file name
    output: head_info =[fep, ccd, node, pblock, tstart, tstop, expcount, date_obs, date_end]
    """
#
#--- check whether the temp file exists. if so, remove it
#
    cmd = 'rm -f ' + exc_dir + 'zout'
    os.system(cmd)
#
#--- extract header information
#
    header   = pyfits.getheader(ifile, 1)

    fep      = header['FEP_ID']
    ccd      = header['CCD_ID']
    node     = header['NODE_ID']
    pblock   = header['PBLOCK']
    tstart   = header['TSTART']
    tstop    = header['TSTOP']
    expcount = header['EXPCOUNT']
    date_obs = header['DATE-OBS']
    date_end = header['DATE-END']
#
#--- return the info
#
    head_info =[fep, ccd, node, pblock, tstart, tstop, expcount, date_obs, date_end]

    return head_info

#------------------------------------------------------------------------------------
#---  extract_hist_data: extracting acis hist data from fits file                 ---
#------------------------------------------------------------------------------------

def extract_hist_data(ifile):
    """
    extracting acis hist data from fits file 
    input:  ifile       ---  fits file name
    output: hist_data   --- a list of histgram data
    """
    tdata = Table.read(ifile, hdu=1)
    cols  = tdata.columns
    sdata = tdata['COUNTS']

    hist_data = []
    for ent in sdata:
        if mcf.is_neumeric(ent):
            hist_data.append(float(ent))

    return hist_data

#------------------------------------------------------------------------------------
#-- find_sim_postion: for a given time find where the sim is located               --
#------------------------------------------------------------------------------------

def find_sim_position(sim_time, sim_pos, tstart, tstop):
    """
    for a given time find where the sim is located
    input: sim_time --- list of time data
           sim_pos  --- list of sim position
           tstart   --- interval start time
           tstop    --- interval stop time
    output:sim_avg  --- average sim position
           smin     --- min of sim position
           smax     --- max of sim position

        HRC-I    +127.0 mm    -51700 - -49300 motor steps
        HRC-S    +250.1 mm    -100800 - -98400 motor steps
        ACIS-S   -190.1 mm   72000-77000 motor steps
        ACIS-I   -233.6 mm   92000-95000 motor steps
        HRC-S, you would expect the external calibration source.
        HRC-I, you would expect only background.  
    """
    sim_avg = 0
    dsum    = 0
    smin    =  1000000
    smax    = -1000000
    tcnt    = 0

    tstart  = float(tstart)
    tstop   = float(tstop)

    for istep in range(0, len(sim_time)):
        stime = sim_time[istep]

        if stime > tstart and stime <= tstop:
            dsum += sim_pos[istep]

            if sim_pos[istep] < smin:
                smin = sim_pos[istep]

            if sim_pos[istep] > smax:
                smax = sim_pos[istep]

            tcnt += 1

        elif stime > tstop:
            if tcnt == 0:
#
#--- for the case there is no data corrected at the end of the file...
#
                sim_avg = 0.5 * (sim_pos[istep-1] + sim_pos[istep])

                if sim_pos[istep -1] == sim_pos[istep]:
                    smin = sim_avg
                    smax = sim_avg

                elif sim_pos[istep -1] > sim_pos[istep]:
                    smin = sim_pos[istep]
                    smax = sim_pos[istep-1]
                else:
                    smin = sim_pos[istep-1]
                    smax = sim_pos[istep]
                break;

    if tcnt > 0:
        sim_avg = int(dsum / tcnt)
    
    if sim_avg == 0:
        smin  = 0
        smax  = 0

    return  [sim_avg, smin, smax]

#------------------------------------------------------------------------------------
#-- print_sim_data: print out sim position data                                   ---
#------------------------------------------------------------------------------------

def print_sim_data(peak_info, sim_pos_info, ccd_info, loc, web_dir, name):

    """
    print out sim poisition data
    input: peak_info:    peak1, cnt1, width1, peak2, cnt2, width2, peak3, cnt3, width3
           sim_pos_info: sim_avg, sim_min, sim_max
           ccd_info:     fep, ccd, node, pblock, tstart, tstop, expcount, date_obs, date_end
           loc:          location of data collected region usually high or low
    output: <web_dir>/Results/CCD<ccd>/node<node>_loc
    """

    [peak1, cnt1, width1, peak2, cnt2, width2, peak3, cnt3, width3]       = peak_info
    [sim_avg, sim_min, sim_max]                                           = sim_pos_info
    [fep, ccd, node, pblock, tstart, tstop, expcount, date_obs, date_end] = ccd_info

    out_dir = data_dir + 'Results/CCD' + str(ccd) + '/node' + str(node) + '_' + loc

    with open(out_dir, 'a') as f:

        line = str(tstart) + '\t'
        line = line + str(tstop) + '\t'
        line = line + str(expcount) + '\t'
        line = line + str(fep) + '\t'

        line = line + '%6d\t' % (int(sim_avg))
        line = line + '%6d\t' %(int(sim_min))
        line = line + '%6d\t' %(int(sim_max))
        line = line + '%6d\t' %(int(peak1))
        line = line + '%6d\t' %(int(cnt1))
        line = line + '%6d\t' %(int(width1))
        line = line + '%6d\t' %(int(peak2))
        line = line + '%6d\t' %(int(cnt2))
        line = line + '%6d\t' %(int(width2))
        line = line + '%6d\t' %(int(peak3))
        line = line + '%6d\t' %(int(cnt3))
        line = line + '%6d\t' %(int(width3))

        line = line + name + '\n'

        f.write(line)

#------------------------------------------------------------------------------------
#--find_peaks: find 3 peaks from data                                             ---
#------------------------------------------------------------------------------------

def find_peaks(hist_data):
    """
    find three peaks (mn, al, ti) and fit a gaussian profile
    input: hist_data ---     distribution data
    output: peak, counts, and width of each peak
    """
    ymax      = -999
    xmax      = 0;
    cnt       = 0
    xdata     = []
    ydata     = []
#
#--- save data in the arrays and find the max count postion
#
    for ent in hist_data:
        if cnt > 2500:
            break

        xdata.append(cnt)
        ydata.append(ent)

        if cnt > 1000:
            if ymax < ent:
                xmax = cnt
                ymax  = ent

        cnt += 1
#
#--- Mn peak
#
    try:
        [pos1, count1, width1, perr1, cerr1, werr1] =  fits_gaus_line(xmax, ymax, 200, xdata, ydata, cnt)
    except:
        [pos1, count1, width1, perr1, cerr1, werr1] = [-999,-999,-999, -999,-999,-999]
#
#--- Al peak
#
    try:
        [pos2, count2, width2, perr2, cerr2, werr2] =  fits_gaus_line(0.25 * xmax, 0.5 * ymax, 50, xdata, ydata, cnt)
    except:
        [pos2, count2, width2, perr2, cerr2, werr2] = [-999,-999,-999, -999,-999,-999]
#
#---- Ti peak
#
    try:
        [pos3, count3, width3, perr3, cerr3, werr3] =  fits_gaus_line(0.765 * xmax, 0.5 * ymax, 100,  xdata, ydata, cnt)
    except:
        [pos3, count3, width3, perr3, cerr3, werr3] = [-999,-999,-999, -999,-999,-999]


    return [pos1, count1, width1, pos2, count2, width2, pos3, count3, width3, perr1,\
            cerr1, werr1, perr2, cerr2, werr2,perr3, cerr3, werr3]

#------------------------------------------------------------------------------------
#-- fits_gaus_line: fit gaussian profile                                          ---
#------------------------------------------------------------------------------------

def fits_gaus_line(center, max_cnt,  drange, xdata, ydata, dcnt):
    """
    fit a gaussian profile
    input: center   --- gaussian center position
           max_cnt  --- gaussinan peak count
           drange   --- width of the data collecting area center +/- drange
           xdata    --- a list of the full sim position data
           ydata    --- a list of the full sim count data
           dcnt     --- a number of data points
    output: [center position, count rate, width of the peak]
    """
    freturn = [-999, -999, -999, -999, -999, -999]
    xval    = []
    yval    = []
    chk     = 0
    
    rmin    = int(center - drange)
    rmax    = int(center + drange)

    for i in range(0, dcnt):
       if xdata[i] >= rmin and xdata[i] <= rmax:
           xval.append(xdata[i])
           yval.append(ydata[i])
           chk += 1
#
#--- least squares fitting
#
    if chk > 0 and max_cnt > 0:

        paramsinitial = (center, max_cnt, 10)
        try:

            popt, pcov = curve_fit(g_function, xval, yval, p0=paramsinitial)
            [pos,  count, width] = list(popt)
            pos   = float('%4.8f' % pos)
            count = float('%4.8f' % count)
            width = float('%4.8f' % width)
            try:
                [perr, cerr,  werr]  = list(numpy.sqrt(numpy.diag(pcov)))
                perr  = float('%4.8f' % perr)
                cerr  = float('%4.8f' % cerr)
                werr  = float('%4.8f' % werr)
            except:
                [perr, cerr, werr]   = [-999, -999, -999]

            return [pos, count, width, perr, cerr, werr]

        except:
            return [center, max_cnt, 10, -999, -999, -999]

    else:
        return  [center, max_cnt, 10, -999, -999, -999]

#-----------------------------------------------------------------------------------,
#-- residuals: compute residuals for Gaussian profile                             ---
#------------------------------------------------------------------------------------

def g_function(x, peak, counts, width):
    """
    compute residuals for Gaussian profile
    input:  param =  (peak, count, width), data = (x, y)
    output: res --- residual
    """
    z = (x - peak) / (width/2.354)
    y =  counts * exp(-1.0 * (z * z)/2.0)

    return y

#------------------------------------------------------------------------------------
#--- plot_fit: using pyplot, make a distribution plot                             ---
#------------------------------------------------------------------------------------

def plot_fit(hist_data, peak_info, name, ccd, node, loc):
    """
    usiing pyplot, make a distribution plot
    input:  hist_data   --- a list of histgram data
            peak_info   --- a information of the peak (pos, cnt, width)
            name        --- the name of the line
            ccd         --- ccd
            node        --- node
            loc         --- location of the sampling
    output: <web_dir>/Plot_indivisual/CCD<ccd>/<name>_node</node>_loc.png
            <data_dir>/Dist_data/CCD<ccd>/<name>_node</node>_loc
    """
    plot_out = web_dir  + 'Plot_indivisual/CCD' + str(ccd) + '/node' + str(node) 
    plot_out = plot_out + '/'+ loc + '/' +  name + '.png'

    data_out = data_dir + 'Dist_data/CCD' + str(ccd) + '/node' + str(node) 
    data_out = data_out + '/' +  loc + '/' + name

    title    =  name + ': CCD' +  str(ccd) + ' Node' + str(node)

    total = len(hist_data)
    if total < 5:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + plot_out
        os.system(cmd)

    else:
        xmin = 0
        xmax = 2000
        xtext= 100
        ymin = 0; 
        ymax = 1.1 * max(hist_data)
        ytext= 0.9 * ymax

        xval = []
        hist = []
        yest = []
        with open(data_out, 'w') as f:
            for i in range(0, 2000):
                xval.append(i)
                hist.append(hist_data[i])
                yest.append(model(i, peak_info))
                line = str(int(hist_data[i])) + '\n'
                f.write(line)
#
#---- setting a few parameters
#
        plt.close('all')
        mpl.rcParams['font.size'] = 9
        props = font_manager.FontProperties(size=6)

        ax = plt.subplot(1,1,1)
#
#--- setting params
#
        ax.set_autoscale_on(False)         #---- these three may not be needed for the new pylab, but 
        ax.set_xbound(xmin,xmax)           #---- they are necessary for the older version to set

        ax.set_xlim(left=xmin,   right=xmax, auto=False)
        ax.set_ylim(bottom=ymin, top=ymax,   auto=False)
#
#--- plotting data
#
        plt.plot(xval, hist, color='black',  lw=0, marker='+', markersize=1.5)
#
#--- plotting model
#
        plt.plot(xval, yest,  color='blue',  lw=1)
#
#--- naming
#
        plt.text(xtext, ytext, title)
#
#--- axis
#
        ax.set_ylabel("Counts")
        ax.set_xlabel("Channel")
#
#--- set the size of the plotting area in inch (width: 5.0.in, height 3.0in)
#
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(8.0, 4.0)
        fig.tight_layout()
#
#--- save the plot in png format
#
        plt.savefig(plot_out, format='png', dpi=100)
        plt.close('all')

#------------------------------------------------------------------------------------
#--- model: three peak model fitting                                              ---
#------------------------------------------------------------------------------------

def model(x, params):
    """
    three peak model fitting
    input: x        --- position
           params   --- three sets of peak position, peak count, and width of the peak
    output: estimate
    """
    [pos1, cnt1, width1, pos2, cnt2, width2, pos3, cnt3, width3] = params

    est1 = 0
    est2 = 0
    est3 = 0
    if width1 > 0:
        z = (x - pos1)/(width1/2.354)
        est1 = cnt1 * exp(-1.0 * (z * z)/2.0)

    if width2 > 0:
        z = (x - pos2)/(width2/2.354)
        est2 = cnt2 * exp(-1.0 * (z * z)/2.0)

    if width3 > 0:
        z = (x - pos3)/(width3/2.354)
        est3 = cnt3 * exp(-1.0 * (z * z)/2.0)

    return est1 + est2 + est3

#-----------------------------------------------------------------------------------
#--- prep_for_test: create and preapare for the test out put directories         ---
#-----------------------------------------------------------------------------------

def prep_for_test():

    line = 'mkdir ' + test_dir
    os.system(line)
    line = 'mkdir ' + test_dir + '/Data'
    os.system(line)
    line = 'mkdir ' + test_dir + '/Data/Results/'
    os.system(line)
    for i in range(0, 10):
        line = 'mkdir ' + test_dir + '/Data/Results/CCD'+ str(i)
        os.system(line)

    line = 'cp ' + comp_dir + 'Results/CCD3/* ' + test_dir  + '/Data/Results/CCD3/'
    os.system(line)

    line = 'mkdir ' + test_dir + '/Data/Dist_data'
    os.system(line)
    for i in range(0, 10):
        line = 'mkdir ' + test_dir + '/Data/Dist_data/CCD' + str(i)
        os.system(line)

        for j in range(0, 4):

            line = 'mkdir ' + test_dir + '/Data/Dist_data/CCD' + str(i) + '/node' + str(j)
            os.system(line)
            line = 'mkdir ' + test_dir + '/Data/Dist_data/CCD' + str(i) + '/node' + str(j) + '/high'
            os.system(line)
            line = 'mkdir ' + test_dir + '/Data/Dist_data/CCD' + str(i) + '/node' + str(j) + '/low'
            os.system(line)

    line = 'mkdir ' + test_dir + '/Save'
    os.system(line)

    line = 'mkdir ' + test_dir + '/mta_acis_hist'
    os.system(line)
    line = 'mkdir ' + test_dir + '/mta_acis_hist/Plot_trend'
    os.system(line)
    line = 'mkdir ' + test_dir + '/mta_acis_hist/Plot_trend/CCD3'
    os.system(line)

    line = 'mkdir ' + test_dir + '/mta_acis_hist/Plot_indivisual'
    os.system(line)
    for i in range(0, 10):
        line = 'mkdir ' + test_dir + '/mta_acis_hist/Plot_indivisual/CCD' + str(i)
        os.system(line)
        for j in range(0, 4):
            line = 'mkdir ' + test_dir + '/mta_acis_hist/Plot_indivisual/CCD' + str(i) + '/node' + str(j)
            os.system(line)
            line = 'mkdir ' + test_dir + '/mta_acis_hist/Plot_indivisual/CCD' + str(i) + '/node' + str(j) + '/high'
            os.system(line)

#--------------------------------------------------------------------------------------
#--- monthly_op: batch operation, collect and process the last month's data         ---
#--------------------------------------------------------------------------------------

def monthly_op():

    out        = time.strftime('%Y:%m', time.localtime())
    atemp      = re.split(':', out)
    year       = int(float(atemp[0]))
    last_month = int(float(atemp[1]))


    if last_month < 1:
        last_month = 12
        year = year -1

    vals = (year, last_month)
    return vals

#--------------------------------------------------------------------------------------
#--- manual_op: ask a user to input a specific year and month to run the operation  ---
#--------------------------------------------------------------------------------------

def manual_op():
    year = raw_input("Year: ")
    if year == '' or year == 'NA':
        year = int(float(time.strftime('%Y', time.localtime()))) 

    else:
        month = raw_input("Month: ")
        if month == '' or month == 'NA':
            month = int(float(time.strftime('%m', time.localtime()))) 

    year = int(year)
    month = int(month)
    print('Extracting data for ' + str(year) + ' ' + str(month))

    vals = (year, month)
    return vals

#--------------------------------------------------------------------------------------
#--- choose_and_run_op: choose and run the operation mode                           ---
#--------------------------------------------------------------------------------------

def choose_and_run_op(year, month, optin, manual):
#
#--- normal case
#
    if optin == 0:
        (year, last_month) = monthly_op()
        acis_hist_extract_data(year, last_month)

    else:
#
#--- if the user asked manual input
#
        if manual == 'yes': 
            (year, month) = monthly_op()
            acis_hist_extract_data(year, month)
#
#--- for the case, year and month are given
#
        else:
            print("Working on  Year: " + str(year) +' Month: ' + str(month))
            acis_hist_extract_data(year, month)

#--------------------------------------------------------------------------------------
#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    if len(sys.argv) == 3:
        year   = int(float(sys.argv[1]))
        month  = int(float(sys.argv[2]))
        optin  = 100
        manual = ""

    else:
        year   = ''
        month  = ''
        optin  = 0
        manual = ''

    choose_and_run_op(year, month, optin,  manual)
