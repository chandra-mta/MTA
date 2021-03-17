#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#       ccd_comb_plot.py: read data and create SIB plots                                    #
#                           monthly, quorterly, one year, and last year                     #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               Last Update: Mar 03, 2021                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import operator
import numpy
import time
import astropy.io.fits as pyfits

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
#
#--- reading directory list
#
path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
import robust_linear        as robust
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a list of the name of the data
#
nameList = ['Super Soft Photons', 'Soft Photons', 'Moderate Energy Photons',\
            'Hard Photons', 'Very Hard Photons', 'Beyond 10 keV']
#
#--- set line color list
#
colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon',\
             'black', 'yellow', 'olive')

#-------------------------------------------------------------------------------
#-- ccd_comb_plot: a control script to create plots                          ---
#-------------------------------------------------------------------------------

def ccd_comb_plot(choice='normal', syear = 2000, smonth = 1, eyear = 2000, emonth = 1, header = 'plot_ccd'):
    """
    a control script to create plots
    Input:  choice      --- if normal, monthly updates of plots are created.
                            if check,  plots for a given period are created
            syear       --- starting year of the period,  choice must be 'check'
            smonth      --- starting month of the period, choice must be 'check'
            eyear       --- ending year of the period,    choice must be 'check'
            emonth      --- ending month of the period,   choice must be 'check'
            header      --- a header of the plot file     choice must be 'check'
    Output: png formated plotting files
    """
#
#--- special case which we need to specify periods
#
    if choice == 'check':
        dlist    = collect_data_file_names('check', syear, smonth, eyear, emonth)
        plot_out = web_dir + 'Plots/Plot_' + str(syear) + '_' + mcf.add_leading_zero(smonth) + '/'
        check_and_create_dir(plot_out)
        plot_data(dlist, plot_out, header, yr=syear, mo=smonth)
#
#--- normal monthly operation
#
    else:
#
#--- find today's date, and set a few thing needed to set output directory and file name
#
        out = time.strftime('%Y:%m', time.gmtime())
        [year, mon] = re.split(':', out)
        year = int(year)
        mon  = int(mon)

        syear  = str(year)
        smonth = mcf.add_leading_zero(mon)

        lyear = year 
        lmon  = mon - 1
        if lmon < 1:
            lmon   = 12
            lyear -= 1
    
        slyear  = str(lyear)
        slmonth = mcf.add_leading_zero(lmon)
#
#--- monthly plot
#
        dlist    = collect_data_file_names('month')
        plot_out = web_dir + '/Plots/Plot_' +  slyear + '_' + slmonth + '/'
        check_and_create_dir(plot_out)
        header   =  'month_plot_ccd'
        plot_data(dlist, plot_out, header, yr=slyear, mo=slmonth,  psize=2.5)
#
#--- quarterly plot
#
        dlist    = collect_data_file_names('quarter')
        plot_out = web_dir + '/Plots/Plot_quarter/'
        check_and_create_dir(plot_out)
        header   = 'quarter_plot_ccd'
        plot_data(dlist, plot_out, header)
    
        dlist    = collect_data_file_names('year')
        plot_out = web_dir + '/Plots/Plot_past_year/'
        check_and_create_dir(plot_out)
        header   = 'one_year_plot_ccd'
        plot_data(dlist, plot_out, header)
#
#--- full previous year's plot. only updated in Jan of new year
#
        if mon == 1:
            dlist    = collect_data_file_names('lyear')
            lyear    = year -1
            plot_out = web_dir + '/Plots/Plot_' + str(lyear) + '/'
            check_and_create_dir(plot_out)
            header   =  'year_plot_ccd'
            plot_data(dlist, plot_out, header, yr=slyear)
#
#--- entire trend plot
#
        dlist    = collect_data_file_names('full')
        plot_out = web_dir + '/Plots/Plot_long_term/'
        check_and_create_dir(plot_out)
        header   = 'full_plot_ccd'
        plot_data(dlist, plot_out, header, xunit='year')
     
#-----------------------------------------------------------------------------------
#-- check_and_create_dir: check whether a directory exist, if not, create one    ---
#-----------------------------------------------------------------------------------

def check_and_create_dir(idir):
    """
    check whether a directory exist, if not, create one
    Input:      idir --- directory name
    Output:     directory created if it was not there.
    """
    if not os.path.isdir(idir):
        cmd = 'mkdir -p ' + idir
        os.system(cmd)

#-----------------------------------------------------------------------------------
#-- define_x_range: set time plotting range                                      ---
#-----------------------------------------------------------------------------------

def define_x_range(dlist, xunit=''):
    """
    set time plotting range
    Input:  dlist       --- list of data files (e.g., Data_2012_09)
    Output: start       --- starting time in either ydate or fractional year
            end         --- ending time in either ydate or fractional year
    """
    num = len(dlist)
    if num == 1:
        atemp  = re.split('\/',    dlist[0])
        btemp  = re.split('Data_', atemp[-1])
        ctemp  = re.split('_',     btemp[1])
        year   = int(ctemp[0])
        month  = int(ctemp[1])
        nyear  = year
        nmonth = month + 1
        if nmonth > 12:
            nmonth = 1
            nyear += 1
    else:
        slist  = sorted(dlist)
        atemp  = re.split('\/',    slist[0])
        btemp  = re.split('Data_', atemp[-1])
        ctemp  = re.split('_',     btemp[1])
        year   = int(ctemp[0])
        month  = int(ctemp[1])

        atemp  = re.split('\/',    slist[-1])
        btemp  = re.split('Data_', atemp[-1])
        ctemp  = re.split('_',     btemp[1])
        tyear  = int(ctemp[0])
        tmonth = int(ctemp[1])
        nyear  = tyear
        nmonth = tmonth + 1
        if nmonth > 12:
            nmonth = 1
            nyear += 1
#
#--- get day of year
#
    start = str(year)  + ':' + mcf.add_leading_zero(month)  + ':01'
    stop  = str(nyear) + ':' + mcf.add_leading_zero(nmonth) + ':01'
    start = int(mcf.convert_date_format(start, ifmt='%Y:%m:%d', ofmt='%j'))
    stop  = int(mcf.convert_date_format(stop,  ifmt='%Y:%m:%d', ofmt='%j'))
#
#--- for te case it is a month plot
#
    if nyear > year:
        if mcf.is_leapyear(year):
            end = stop + 366
        else:
            end = stop + 365
    else:
        end = stop
#
#--- for the case it is a longer plot
#
    if xunit == 'year':
        if mcf.is_leapyear(year):
            base = 366.0
        else:
            base = 365.0
        start = year + float(start) / base

        if mcf.is_leapyear(nyear):
            base = 366.0
        else:
            base = 365.0
        end = nyear + float(stop) / base

    return [start, end]

#-----------------------------------------------------------------------------------
#-- plot_data: for a given data directory list, prepare data sets and create plots--
#-----------------------------------------------------------------------------------

def plot_data(dlist, plot_out, header, yr='', mo='', xunit='', psize=1):
    """
    for a given data directory list, prepare data sets and create plots
    Input:  dlist   --- a list of input data directories
            plot_out -- a directory name where the plots are deposited
            header  --- a head part of the plotting file
            yr      --- a year in string form optional
            mo      --- a month in letter form optional
            xunit   --- if "year", the plotting is made with fractional year, otherwise in dom
            psize   --- a size of plotting point.
    Output: a png formated file
    """
#
#--- set lists for accumulated data sets
#
    time_full  = []
    count_full = []
    time_ccd5  = []
    count_ccd5 = []
    time_ccd6  = []
    count_ccd6 = []
    time_ccd7  = []
    count_ccd7 = []
#
#--- set plotting range for x
#
    [xmin, xmax] = define_x_range(dlist, xunit=xunit)
#
#--- go though all ccds
#
    for ccd in range(0, 10):

        outname  = plot_out + header + str(ccd) + '.png'
        filename = 'lres_ccd' + str(ccd) + '_merged.fits'
#
#--- extract data from data files in the list and combine them
#
        [atime, assoft, asoft, amed, ahard, aharder, ahardest] = accumulate_data(dlist, filename)

        if len(atime) > 0:
#
#--- if the plot is a long term, use the unit of year. otherwise,  day of year
#
            if xunit == 'year':
                xtime = convert_time(atime, format=1) 
            else:
                xtime = convert_time(atime)
#
#--- create the full range and ccd 5, 6, and 7  data sets
#
            xdata = []
            ydata = []
            for i in range(0, len(xtime)):
                time_full.append(xtime[i])
                xdata.append(xtime[i])
                asum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                count_full.append(asum)
                ydata.append(asum)

            if ccd == 5:
                time_ccd5 = xtime
                for i in range(0, len(xtime)):
                    asum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                    count_ccd5.append(asum)

            elif ccd == 6:
                time_ccd6 = xtime
                for i in range(0, len(xtime)):
                    asum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                    count_ccd6.append(asum)

            elif ccd == 7:
                time_ccd7 = xtime
                for i in range(0, len(xtime)):
                    asum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                    count_ccd7.append(asum)
#
#--- prepare for the indivisual plot
#
            xsets = []
            for i in range(0, 6):
                xsets.append(xtime)
            data_list = (assoft, asoft, amed, ahard, aharder, ahardest)
#
#--- plotting data
#
            entLabels = nameList
            plot_data_sub(xsets, data_list, entLabels, xmin, xmax,  outname, xunit=xunit)
#
#--- combined data for the ccd
#
            xset_comb  = [xdata]
            data_comb  = [ydata]
            name       = 'CCD' + str(ccd) + ' combined'
            entLabels  = [name]
            outname2   = change_outname_comb(header, plot_out, ccd)
            plot_data_sub(xset_comb, data_comb, entLabels, xmin, xmax,  outname2, xunit=xunit)

        else:
            cmd = 'cp ' + house_keeping + 'no_data.png ' + outname
            os.system(cmd)
            outname2 = change_outname_comb(header, plot_out, ccd)
            cmd = 'cp ' + house_keeping + 'no_data.png ' + outname2
            os.system(cmd)
#
#--- combined data plot
#
    xsets     = [time_full]
    data_list = [count_full]
    entLabels = ['Total SIB']
    outname   = plot_out + header + '_combined.png'
    plot_data_sub(xsets, data_list, entLabels, xmin, xmax,  outname, xunit=xunit)
#
#--- ccd5, ccd6, and ccd7
#
    xsets     = [time_ccd5,  time_ccd6,  time_ccd7]
    data_list = [count_ccd5, count_ccd6, count_ccd7]
    entLabels = ['CCD5', 'CCD6', 'CCD7']
    outname   = plot_out + header + '_ccd567.png'
    plot_data_sub(xsets, data_list, entLabels, xmin, xmax,  outname, xunit=xunit)
#
#--- add html page
#
    ptype  = 'other'
    if yr != '':
        ptype = 'year'
        if  mo != '':
            ptype = 'month'

    if (ptype == 'month') or (ptype == 'year'):
        add_html_page(ptype, plot_out, yr, mo)

#-----------------------------------------------------------------------------------
#-- add_html_page: update/add html page to Plot directory                        ---
#-----------------------------------------------------------------------------------

def add_html_page(ptype, plot_out,  yr, mo):
    """
    update/add html page to Plot directory
    Input:  ptype       --- indiecator of which html page to be updated
            plot_out    --- a directory where the html page is updated/created
            yr          --- a year of the file
            mo          --- a month of the file
    Output: either month.html or year.hmtl in an appropriate directory
    """
    current = time.strftime('%m-%d-%Y', time.gmtime())
    lmon    = ''

    if ptype == 'month':
        ofile  = plot_out + 'month.html'
        lmon   = mcf.change_month_format(int(mo))
        ifile  = house_keeping + 'month.html'

    elif ptype == 'year':
        ofile  = plot_out + 'year.html'
        ifile = house_keeping + 'year.html'

    with open(ifile, 'r') as f:
        text = f.read()

    text = text.replace('#YEAR#',  str(yr))
    text = text.replace('#MONTH#', str(lmon))
    text = text.replace('#DATE#',  str(current))
    
    with open(ofile, 'w') as fo:
        fo.write(text)

#-----------------------------------------------------------------------------------
#-- change_outname_comb: change file name to "comb" form                         ---
#-----------------------------------------------------------------------------------

def change_outname_comb(header, plot_out, ccd):
    """
    change file name to "comb" form
    Input:  header      --- original header form
            plot_out    --- output directory name
            ccd         --- ccd #
    Output: outname     --- <plot_out>_<modified header>_ccd<ccd#>.png
    """
    for nchk in ('month', 'quarter', 'one_year', 'year_plot', 'full_plot'):
        n1 = re.search(nchk, header)
        if n1 is not None:
            rword = nchk
            ptype = nchk
            nword = 'combined_' + nchk
            break

    header  = header.replace(rword, nword)
    outname = plot_out + header + str(ccd) + '.png'

    return outname

#-----------------------------------------------------------------------------------
#-- plot_data_sub: plotting data                                                 ---
#-----------------------------------------------------------------------------------

def plot_data_sub(xSets, data_list, entLabels, xmin, xmax,  outname, xunit=0, psize=1.0):
    """
    plotting data
    Input:  XSets       --- a list of lists of x values
            data_list   --- a list of lists of y values
            entLabels   --- a list of names of the data
            xmin        --- starting of x range
            xmax        --- ending of x range
            outname     --- output file name
            xunit       --- if "year" x is plotted in year format, otherwise dom
            psize       --- size of the plotting point
    Output: outname     --- a png formated plot 
    """
    xmin = int(xmin)
    xmax = int(xmax)
    try:
        if xunit == 'year':
            xmax += 2
        else:
            xdiff = xmax - xmin
            xmin -= 0.05 * xdiff
            xmax += 0.05 * xdiff
#
#--- now set y related quantities
#
        ySets    = []
        yMinSets = []
        yMaxSets = []
        for data in data_list:
            yMinSets.append(0)
            ySets.append(data)
    
            if len(data) > 0:
                ymax = set_Ymax(data)
                yMaxSets.append(ymax)
            else:
                yMaxSets.append(1)
    
        if xunit == 'year':
            xname = 'Time (Year)'
        else:
            xname = 'Time (Year Date)'
        yname = 'cnts/s'
#
#--- actual plotting is done here
#
        plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname,\
                  entLabels, outname, psize=psize)
    except:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + outname
        os.system(cmd)

#-----------------------------------------------------------------------------------
#-- set_Ymax: find a plotting range                                              ---
#-----------------------------------------------------------------------------------

def set_Ymax(data):
    """
    find a plotting range
    Input:      data --- data
    Output:     ymax --- max rnage set in 4.0 sigma from the mean
    """
    avg = numpy.mean(data)
    sig = numpy.std(data)
    ymax = avg + 4.0 * sig
    if ymax > 20:
        ymax = 20

    return ymax

#-----------------------------------------------------------------------------------
#-- collect_data_file_names: or a given period, create a list of directory names ---
#-----------------------------------------------------------------------------------

def collect_data_file_names(period, syear=2000, smonth=1, eyear=2000, emonth=12):
    """
    for a given period, create a list of directory names
    Input:  period   --- indicator of which peirod, "month", "quarter", 
                         "year", "lyear", "full", and "check'"
            if period == 'check', then you need to give a period in year and month
            syear    --- year of the starting date
            smonth   --- month of the starting date
            eyear    --- year of the ending date
            emonth   --- month of the ending date
    Output  data_lst --- a list of the directory names
    """
#
#--- find today's date
#
    out         = time.strftime('%Y:%m', time.gmtime())
    [year, mon] = re.split(':', out)
    year = int(year)
    mon  = int(mon)

    data_list = []
#
#--- find the last month 
#
    if period == 'month':
        mon -= 1
        if mon < 1:
            mon = 12
            year -= 1

        cmon  = mcf.add_leading_zero(mon)
        dfile = data_dir + 'Data_' + str(year) + '_' + cmon
        data_list.append(dfile)
#
#--- find the last three months 
#
    if period == 'quarter':
        for i in range(1, 4):
            lyear = year
            month = mon -i
            if month < 1:
                month = 12 + month
                lyear = year -1

            cmon  = mcf.add_leading_zero(month)
            dfile = data_dir + 'Data_' + str(lyear) + '_' + cmon
            data_list.append(dfile)
#
#--- find data for the last one year (ending the last month)
#
    elif period == 'year':
        cnt = 0
        if mon > 1:
            for i in range(1, mon):
                cmon  = mcf.add_leading_zero(i)
                dfile = data_dir + 'Data_' + str(year) + '_' + cmon
                data_list.append(dfile)

                cnt += 1
        if cnt < 11:
            year -= 1
            for i in range(mon, 13):
                cmon  = mcf.add_leading_zero(i)
                dfile = data_dir + 'Data_' + str(year) + '_' + cmon
                data_list.append(dfile)
#
#--- fill the list with the past year's data
#
    elif period == 'lyear':
        year -= 1
        for i in range(1, 13):
            cmon  = mcf.add_leading_zero(i)
            dfile = data_dir + 'Data_' + str(year) + '_' + cmon
            data_list.append(dfile)
#
#--- fill the list with the entire data
#
    elif period == 'full':
        for iyear in range(2000, year+1):
            for i in range (1, 13):
                cmon  = mcf.add_leading_zero(i)
                dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                data_list.append(dfile)
#
#--- if the period is given, use them
#
    elif period == 'check':
        syear  = int(syear)
        eyear  = int(eyear)
        smonth = int(smonth)
        emonth = int(emonth)
        if syear == eyear:
            for i in range(smonth, emonth+1):
                cmon  = mcf.add_leading_zero(i)
                dfile = data_dir + 'Data_' + str(syear) + '_' + cmon
                data_list.append(dfile)

        elif syear < eyear:
            for iyear in range(syear, eyear+1):
                if iyear == syear:
                    for month in range(smonth, 13):
                        cmon  = mcf.add_leading_zero(i)
                        dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                        data_list.append(dfile)

                elif iyear == eyear:
                    for month in range(1, emonth+1):
                        cmon  = mcf.add_leading_zero(i)
                        dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                        data_list.append(dfile)

                else:
                    for month in range(1, 13):
                        cmon  = mcf.add_leading_zero(i)
                        dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                        data_list.append(dfile)

    return data_list

#-----------------------------------------------------------------------------------
#-- read_evt_data: read out needed data from a given file                       ---
#-----------------------------------------------------------------------------------

def read_evt_data(fits):
    """
    read out needed data from a given file
    Input:  fits    --- input file name
    Output: a list of lists of data: [time, ssoft, soft, med, hard, harder, hardest]
    """
    try:
        hdulist = pyfits.open(fits)
        tbdata  = hdulist[1].data
#
#--- extracted data are 5 minutes accumulation; convert it into cnt/sec
#
        time    = tbdata.field('time').tolist()
        ssoft   = (tbdata.field('SSoft')   / 600.0).tolist()
        soft    = (tbdata.field('Soft')    / 600.0).tolist()
        med     = (tbdata.field('Med')     / 600.0).tolist()
        hard    = (tbdata.field('Hard')    / 600.0).tolist()
        harder  = (tbdata.field('Harder')  / 600.0).tolist()
        hardest = (tbdata.field('Hardest') / 600.0).tolist()
    
        hdulist.close()
    
        return [time, ssoft, soft, med, hard, harder, hardest]
    except:
        return [[], [], [], [], [], [], []]

#-----------------------------------------------------------------------------------
#-- accumulate_data: combine the data in the given period                        ---
#-----------------------------------------------------------------------------------

def accumulate_data(inlist, ifile):
    """
    combine the data in the given period
    Input:  inlist: a list of data directories to extract data
            file:   a file name of the data
    Output: a list of combined data lst: [atime, assoft, asoft, amed, ahard, aharder, ahardest]
    """
    atime    = []
    assoft   = []
    asoft    = []
    amed     = []
    ahard    = []
    aharder  = []
    ahardest = []
    for dname in inlist:
        infile = dname + '/' + ifile

        test_file = infile + '.gz'
        if os.path.isfile(test_file):
            infile = test_file
        elif os.path.isfile(infile):
            pass
        else:
            continue

        try:
            [time, ssoft, soft, med, hard, harder, hardest] = read_evt_data(infile)
            atime    = atime    + time
            assoft   = assoft   + ssoft
            asoft    = asoft    + soft
            amed     = amed     + med
            ahard    = ahard    + hard
            aharder  = aharder  + harder
            ahardest = ahardest + hardest
        except:
            pass
#
#--- if there are too many data points to plot, use only "drop"-th data points
#
    if len(atime) > 2000:
        drop     = int(len(atime)/2000)
        atime    = atime[::drop]
        assoft   = assoft[::drop]
        asoft    = asoft[::drop]
        amed     = amed[::drop]
        ahard    = ahard[::drop]
        aharder  = aharder[::drop]
        ahardest = ahardest[::drop]

    return [atime, assoft, asoft, amed, ahard, aharder, ahardest]

#---------------------------------------------------------------------------------------------------
#-- convert_time: convert time format from seconds from 1998.1.1 to dom or fractional year       ---
#---------------------------------------------------------------------------------------------------

def convert_time(time, format  = 0):
    """
    convert time format from seconds from 1998.1.1 to data of year or fractional year
    Input:  time    --- a list of time in seconds
            format  --- if 0, convert into day of year, otherwise, fractional year
    Output: timeconverted --- a list of conveted time
    """
    t_list = []
    if format == 0:
        for ent in time:
            t_list.append(mcf.chandratime_to_yday(ent))
    else:
        for ent in time:
            t_list.append(mcf.chandratime_to_fraq_year(ent))
        
    return t_list

#-----------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                           ---
#-----------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname,\
              entLabels, outname, psize=1.0):
    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            yMinSets: a list of ymin 
            yMaxSets: a list of ymax
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- start plotting each data
#
    for i in range(0, len(entLabels)):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec("%s = plt.subplot(%s)"       % (axNam, line))
        exec("%s.set_autoscale_on(False)" % (axNam))
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))

        exec("%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam))
        exec("%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam))

        xdata  = xSets[i]
        ydata  = ySets[i]
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=psize, lw =0)
#
#---- compute fitting line
#
        (intc, slope, berr) = robust.robust_fit(xdata, ydata)

        cslope = str('%.4f' % round(slope, 4))

        ystart = intc + slope * xmin
        yend   = intc + slope * xmax

        plt.plot([xmin, xmax], [ystart, yend], color=(colorList[i+2]), lw=1)
#
#--- add legend
#
        tline = entLabels[i] + ' Slope: ' + cslope
        leg = legend([p],  [tline], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec("%s.set_ylabel(yname, size=8)" % (axNam))
#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            line = eval("%s.get_xticklabels()" % (ax))
            for label in  line:
                label.set_visible(False)
        else:
            pass

    xlabel(xname)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=200)

#--------------------------------------------------------------------

if __name__ == '__main__':
    ccd_comb_plot()
    #ccd_comb_plot('check', syear=2019, smonth=7, eyear=2019, emonth=7, header='month_plot_ccd')


