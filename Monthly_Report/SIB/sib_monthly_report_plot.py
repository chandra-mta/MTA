#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#       sib_monthly_report_plot.py: read data and create SIB plots                          #
#                           for MTA monthly report.                                         #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               Last Update: Mar 10, 2021                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import astropy.io.fits  as pyfits
import numpy
import time
import Chandra.Time

import matplotlib as mpl
if __name__ == '__main__':

    mpl.use('Agg')
#
#--- reading directory list
#
comp_test = 'live'

if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/Month/SIB/dir_list'

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

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a list of the name of the data
#
nameList = ['Super Soft Photons', 'Soft Photons', 'Moderate Energy Photons',\
            'Hard Photons', 'Very Hard Photons', 'Beyond 10 keV']

#---------------------------------------------------------------------------------------------------
#-- ccd_comb_plot: a control script to create plots                                              ---
#---------------------------------------------------------------------------------------------------

def ccd_comb_plot(choice):

    """
    a control script to create plots
    Input:  choice      --- if check, you will be asked to provide year and month
                            all oter cases, the script will use the previous month
    Output: png formated plotting files
    """
#
#--- find today's date, and set a few thing needed to set output directory and file name
#
    if choice == 'check':
        year = input("Year: ")
        mon  = input("Month: ")
        year = int(float(year))
        mon  = int(float(mon))
    else:
        out  = time.strftime('%Y:%m:%d', time.gmtime())
        out  = re.split(':', out)
        year = int(float(out[0]))
        mon  = int(float(out[1]))

    syear  = str(year)
    smonth = str(mon)
    if mon < 10:
        smonth = '0'+ smonth

    lyear = year 
    lmon  = mon - 1
    if lmon < 1:
        lmon   = 12
        lyear -= 1

    slyear  = str(lyear)
    slmonth = str(lmon)
    if lmon < 10:
        slmonth = '0' + slmonth
#
#--- monthly plot
#
    dlist    = collect_data_file_names('month')
    plot_out = './'
    header   =  'month_plot_ccd'
    plot_data(dlist, plot_out, header, yr=slyear, mo=slmonth,  psize=2.5, xunit='ydate')
     
#---------------------------------------------------------------------------------------------------
#-- define_x_range: set time plotting range                                                      ---
#---------------------------------------------------------------------------------------------------

def define_x_range(dlist, xunit=''):

    """
    set time plotting range
    Input:  dlist       --- list of data files (e.g., Data_2012_09)
            xunit       --- if it is 'year', it will give fraq year, if ydate, ydate
                            otherwise, DOM. default: DOM
    Output: start       --- starting time in either DOM, fractional year, or ydate
            end         --- ending time in either DOM, fractional year, or ydate
    """

    num = len(dlist)
    if num == 1:
        atemp  = re.split('Data_', dlist[0])
        btemp  = re.split('_',     atemp[1])
        year   = int(btemp[0])
        month  = int(btemp[1])
        nyear  = year
        nmonth = month + 1
        if nmonth > 12:
            nmonth = 1
            nyear += 1
    else:
        slist  = sorted(dlist)
        atemp  = re.split('Data_', slist[0])
        btemp  = re.split('_',     atemp[1])
        year   = int(btemp[0])
        month  = int(btemp[1])

        atemp  = re.split('Data_', slist[len(slist)-1])
        btemp  = re.split('_',     atemp[1])
        tyear  = int(btemp[0])
        tmonth = int(btemp[1])
        nyear  = tyear
        nmonth = tmonth + 1
        if nmonth > 12:
            nmonth = 1
            nyear += 1

    line   = str(year) + ':' + str(month) + ':01'
    ydate  = float(time.strftime('%j', time.strptime(line, '%Y:%m:%d')))
    start  = mcf.ydate_to_dom(year, ydate)

    line   = str(nyear) + ':' + str(nmonth) + ':01'
    nydate = float(time.strftime('%j', time.strptime(line, '%Y:%m:%d')))
    end    = mcf.ydate_to_dom(nyear, nydate)
#
#--- if it is a long term, unit is in year
#
    if xunit == 'year':
        if mcf.is_leapyear(year):
            base = 366
        else:
            base = 365
        start = year + ydate / base

        if mcf.is_leapyear(nyear):
            base = 366
        else:
            base = 365
        end  = nyear + nydate /base

    elif xunit == 'ydate':
        start = ydate
        end   = nydate
        if start > end:
            chk = 4.0 * int(0.25 * nyear)
            if chk == nyear:
                end = 366
            else:
                end = 365

    return [start, end]

#---------------------------------------------------------------------------------------------------
#-- plot_data: for a given data directory list, prepare data sets and create plots               ---
#---------------------------------------------------------------------------------------------------

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
    time_ccd3  = []
    count_ccd3 = []
    ssoft3     = []
    soft3      = []
    med3       = []
    hard3      = []
    hader3     = []
    hardest3   = []

    time_ccd5  = []
    count_ccd5 = []
    ssoft5     = []
    soft5      = []
    med5       = []
    hard5      = []
    hader5     = []

    time_ccd7  = []
    count_ccd7 = []
    ssoft7     = []
    soft7      = []
    med7       = []
    hard7      = []
    hader7     = []

    eng_list   = ('ssoft', 'soft', 'med', 'hard', 'harder', 'hardest')
#
#--- set plotting range for x
#
    [xmin, xmax] = define_x_range(dlist, xunit=xunit)
#
#--- go though all ccds
#
    [time_ccd3, count_ccd3, ssoft3, soft3, med3, hard3, harder3, hardest3]\
                                    = aaccu_data(3, dlist, plot_out, header, xunit)
    [time_ccd5, count_ccd5, ssoft5, soft5, med5, hard5, harder5, hardest5]\
                                    = aaccu_data(5, dlist, plot_out, header, xunit)
    [time_ccd7, count_ccd7, ssoft7, soft7, med7, hard7, harder7, hardest7]\
                                    = aaccu_data(7, dlist, plot_out, header, xunit)
#    for ccd in (3, 5, 7):
#
#        outname  = plot_out + header + str(ccd) + '.png'
#        filename = 'lres_ccd' + str(ccd) + '_merged.fits'
##
##--- extract data from data files in the list and combine them
##
#        [atime, assoft, asoft, amed, ahard, aharder, ahardest] = accumulate_data(dlist, filename)
#
#        if len(atime) > 0:
##
##--- if the plot is a long term, use the unit of year. otherwise, dom
##
#            if xunit == 'year':
#                xtime = convert_time(atime, format=2) 
#            elif xunit == 'ydate':
#                xtime = convert_time(atime, format=1) 
#            else:
#                xtime = convert_time(atime)
##
##--- create the full range and ccd 5, 6, and 7  data sets
##
#            for i in range(0, len(xtime)):
#                dsum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
#                name = 'count_ccd' + str(ccd)
#                exec("%s.append(%s)" %(name, dsum))
#
#            exec("time_ccd%s = %s" % (ccd, xtime))
#
#            for eng in eng_list:
#                eng2 = 'a' + eng
#                eng3 = eng + str(ccd)
#                exec("%s = %s" % (eng3, eng2))
#
#--- ccd3, ccd5, and ccd7
#
    xsets     = [time_ccd3,  time_ccd5,  time_ccd7]
    data_list = [count_ccd3, count_ccd5, count_ccd7]
    entLabels = ['CCD3', 'CCD5', 'CCD7']
    outname   = 'SIB_Data_' + str(yr) + '_' + str(mo) + '_total.png'

    plot_data_sub(xsets, data_list, entLabels, xmin, xmax,  outname, xunit=xunit)

#
#--- six panel plot for each energy range
#
    fsize  = 9
    lsize  = 0
    xdata1 = time_ccd3
    xdata2 = time_ccd5
    xdata3 = time_ccd7
    temp   = xdata1 + xdata2 + xdata3
    xmin   = min(temp)
    xmax   = max(temp)

    plt.close("all")
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08, wspace=0.08)

    for  i in range(0, len(eng_list)):
        eng    = eng_list[i]
        ydata1 = eval("%s3" %(eng))
        ydata2 = eval("%s5" %(eng))
        ydata3 = eval("%s7" %(eng))
        temp = ydata1 + ydata2 + ydata3
        ymin = 0
        ymax = max(temp)

        j   = i + 1
        pos = '32' +str(j)

        axNam = 'ax' + str(j)

        exec("%s = plt.subplot(%s)"       % (axNam, pos))
        exec("%s.set_autoscale_on(False)" % (axNam))
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))

        exec("%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam))
        exec("%s.set_ylim(ymin=0, ymax=ymax, auto=False)" % (axNam) )

        plt.plot(xdata1, ydata1, color='green', lw =lsize , marker='o', markersize=2, label='CCD3')
        plt.plot(xdata2, ydata2, color='blue',  lw =lsize , marker='o', markersize=2, label='CCD5')
        plt.plot(xdata3, ydata3, color='red',   lw =lsize , marker='o', markersize=2, label='CCD7')
        if i == 0:
            plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, borderaxespad=0.)

        if i == 0 or i%2 == 0:
            exec("%s.set_ylabel('Cnt/Sec', size=fsize)" % (axNam))

        if i < 4:
            line = eval("%s.get_xticklabels()" % (axNam))
            for label in  line:
                label.set_visible(False)
        else:
            exec("%s.set_xlabel('Time (Year Date)', size=fsize)" % (axNam))

        xpos = 0.05 * (xmax - xmin) + xmin
        ypos = 0.90 * ymax
        text(xpos, ypos, nameList[i], fontsize=11,style='italic', weight='bold')

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 7.5)

    outname   = 'SIB_Data_' + str(yr) + '_' + str(mo) + '_bands.png'

    plt.savefig(outname, format='png', dpi=100)


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def aaccu_data(ccd, dlist, plot_out, header, xunit):

    outname  = plot_out + header + str(ccd) + '.png'
    filename = 'lres_ccd' + str(ccd) + '_merged.fits'
#
#--- extract data from data files in the list and combine them
#
    [atime, assoft, asoft, amed, ahard, aharder, ahardest] = accumulate_data(dlist, filename)

    if len(atime) > 0:
#
#--- if the plot is a long term, use the unit of year. otherwise, dom
#
        if xunit == 'year':
            xtime = convert_time(atime, format=2) 
        elif xunit == 'ydate':
            xtime = convert_time(atime, format=1) 
        else:
            xtime = convert_time(atime)
#
#--- create the full range and ccd 5, 6, and 7  data sets
#
        count_ccd = []
        for i in range(0, len(xtime)):
            dsum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
            count_ccd.append(dsum)

    return [xtime, count_ccd, assoft, asoft, amed, ahard, aharder, ahardest]

#---------------------------------------------------------------------------------------------------
#-- plot_data_sub: plotting data                                                                 ---
#---------------------------------------------------------------------------------------------------

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
    if xunit == 'year':
        xmin = int(xmin)
        xmax = int(xmax) + 2
    else:
        xdiff = xmax - xmin
        xmin -= 0.05 * xdiff
        xmax += 0.05 * xdiff
#
#--- now set y related quantities
#
    ySets = []
    ymin  = 0
    for data in data_list:
        ySets.append(data)

        ymax = 0
        if len(data) > 0:
            tmax = set_Ymax(data)
            if tmax > ymax:
                ymax = tmax
        else:
            ymax = 1

    if xunit == 'year':
        xname = 'Time (Year)'
    elif xunit == 'ydate':
        xname = 'Time (Year Date)'
    else:
        xname = 'DOM'

    yname = 'cnts/s'
#
#--- actual plotting is done here
#
    plot_multi_entries(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outname, psize=psize)

#---------------------------------------------------------------------------------------------------
#-- set_Ymax: find a plotting range                                                              ---
#---------------------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------------------
#-- collect_data_file_names: or a given period, create a list of directory names                 ---
#---------------------------------------------------------------------------------------------------

def collect_data_file_names(period, syear=2000, smonth=1, eyear=2000, emonth=12):

    """
    for a given period, create a list of directory names
    Input:  period   --- indicator of which peirod, "month", "quarter", "year", "lyear", "full", and "check'"
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
    out   = time.strftime('%Y:%m:%d', time.gmtime())
    atemp = re.split(':', out)
    year  = int(float(atemp[0]))
    mon   = int(float(atemp[1]))

    data_list = []

#
#--- find the last month 
#
    if period == 'month':
        mon -= 1
        if mon < 1:
            mon = 12
            year -= 1

        if mon < 10:
            cmon = '0' + str(mon)
        else: 
            cmon = str(mon)

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

            if month < 10:
                cmon = '0' + str(month)
            else: 
                cmon = str(month)

            dfile = data_dir + 'Data_' + str(lyear) + '_' + cmon
            data_list.append(dfile)
#
#--- find data for the last one year (ending the last month)
#
    elif period == 'year':
        
        cnt = 0
        if mon > 1:
            for i in range(1, mon):
                if i < 10:
                    cmon = '0' + str(i)
                else:
                    cmon = str(i)
                dfile = data_dir + 'Data_' + str(year) + '_' + cmon
                data_list.append(dfile)
                cnt += 1
        if cnt < 11:
            year -= 1
            for i in range(mon, 13):
                if i < 10:
                    cmon = '0' + str(i)
                else:
                    cmon = str(i)
                dfile = data_dir + 'Data_' + str(year) + '_' + cmon
                data_list.append(dfile)
#
#--- fill the list with the past year's data
#
    elif period == 'lyear':
        year -= 1
        for i in range(1, 13):
            if i < 10:
                cmon = '0' + str(i)
            else:
                cmon = str(i)
            dfile = data_dir + 'Data_' + str(year) + '_' + cmon
            data_list.append(dfile)
#
#--- fill the list with the entire data
#
    elif period == 'full':
        for iyear in range(2000, year+1):
            for i in range (1, 13):
                if i < 10:
                    cmon = '0' + str(i)
                else:
                    cmon = str(i)
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
                if i < 10:
                    cmon = '0' + str(i)
                else:
                    cmon = str(i)
                dfile = data_dir + 'Data_' + str(syear) + '_' + cmon
                data_list.append(dfile)

        elif syear < eyear:
            for iyear in range(syear, eyear+1):
                if iyear == syear:
                    for month in range(smonth, 13):
                        if i < 10:
                            cmon = '0' + str(i)
                        else:
                            cmon = str(i)
                        dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                        data_list.append(dfile)
                elif iyear == eyear:
                    for month in range(1, emonth+1):
                        if i < 10:
                            cmon = '0' + str(i)
                        else:
                            cmon = str(i)
                        dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                        data_list.append(dfile)
                else:
                    for month in range(1, 13):
                        if i < 10:
                            cmon = '0' + str(i)
                        else:
                            cmon = str(i)
                        dfile = data_dir + 'Data_' + str(iyear) + '_' + cmon
                        data_list.append(dfile)

    return data_list

#---------------------------------------------------------------------------------------------------
#-- read_fits_data: read out needed data from a given file                                       ---
#---------------------------------------------------------------------------------------------------

def read_fits_data(ifile):

    """
    read out needed data from a given file
    Input:  ifile    --- input file name
    Output: a list of lists of data: [time, ssoft, soft, med, hard, harder, hardest]
    """
    try:
        hdulist = pyfits.open(ifile)
        tbdata = hdulist[1].data
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

#---------------------------------------------------------------------------------------------------
#-- accumulate_data: combine the data in the given period                                        ---
#---------------------------------------------------------------------------------------------------

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

        if not  os.path.isfile(infile):
            infile = infile + '.gz'

        try:
            [time, ssoft, soft, med, hard, harder, hardest] = read_fits_data(infile)
            atime    = atime    + time
            assoft   = assoft   + ssoft
            asoft    = asoft    + soft
            amed     = amed     + med
            ahard    = ahard    + hard
            aharder  = aharder  + harder
            ahardest = ahardest + hardest
        except:
            pass

    return [atime, assoft, asoft, amed, ahard, aharder, ahardest]


#---------------------------------------------------------------------------------------------------
#-- convert_time: convert time format from seconds from 1998.1.1 to dom or fractional year       ---
#---------------------------------------------------------------------------------------------------

def convert_time(time_list, format  = 0):

    """
    convert time format from seconds from 1998.1.1 to dom or fractional year
    Input:  time    --- a list of time in seconds
            format  --- if 0, convert into dom. if 1, ydate,  otherwise, fractional year
    Output: timeconverted --- a list of conveted time
    """

    timeconverted = []
    for ent in time_list:
        out   = Chandra.Time.DateTime(ent).date
        atemp = re.split(':', out)
        year  = float(atemp[0])
        ydate = float(atemp[1]) 
        tpart = float(atemp[2]) / 24. + float(atemp[3]) / 1440. + float(atemp[4]) / 86400.
        if format == 0: 
            dom = mcf.ydate_to_dom(year, ydate)
            timeconverted.append(dom + tpart)
        elif format == 1:
            timeconverted.append(ydate + tpart)
        else:
            if mcf.is_leapyear(year):
                base = 366
            else:
                base = 365
            year += (ydate + tpart) /base

            timeconverted.append(year)
        
    return timeconverted

#-----------------------------------------------------------------------------------------------
#-- plot_multi_entries: plotting multiple data in a single panel                             ---
#-----------------------------------------------------------------------------------------------

def plot_multi_entries(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outname, yerror = 0,fsize = 9, psize = 2.0,lsize=0, resolution=100, linefit=0, connect=0):

    """
    This function plots multiple data in a single panel.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets:      a list of lists containing x-axis data
            ySets:      a list of lists containing y-axis data
            xname:      a name of x-axis
            yname:      a name of y-axis
            entLabels:  a list of the names of each data
            outname:    a name of plotting file
            yerror:     a list of lists of y error, if it is '0', no error bar, default = 0
            fsize:      font size, default = 9
            psize:      plotting point size, default = 2.0
            lsize:      fitted line width, default = 1
            resolution: plotting resolution in dpi
            linefit  --- if it is 1, fit a line estimated by robust method
            connect:    connected line size. if it is '0', no connected line

    Output: a png plot: out.png
    """

    colorList = ('green', 'blue', 'red', 'lime', 'line', 'yellow', 'maroon', 'black', 'fushia', 'olive')

    markerList = ('o',    '*',     '+',   '^',    's',    'D',       '1',      '2',     '3',      '4')
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

#
#---- set a panel
#
    ax = plt.subplot(111)
    ax.set_autoscale_on(False)      #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)        #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    tot = len(entLabels)
#
#--- start plotting each data set
#
    lnamList = []
    for i in range(0, tot):
        xdata  = xSets[i]
        ydata  = ySets[i]
        color  = colorList[i]
        marker = markerList[0]
        label  = entLabels[i]

        if tot > 1:
            lnam = 'p' + str(i)
            lnamList.append(lnam)
            exec('%s, = plt.plot(xdata, ydata, color="%s", lw =lsize , marker="%s", markersize=3, label=entLabels[i])' %(lnam, color, marker))

        else:
#
#--- if there is only one data set, ignore legend
#
            plt.plot(xdata, ydata, color=color, lw =connect , marker='o', markersize=psize)

            if yerror != 0:
                p, = plt.errorbar(xdata, ydata, yerr=yerror[i], lw = 0, elinewidth=1)

            if linefit > 0:
                (sint, slope,serror) = robust.robust_fit(xdata, ydata)
                start = sint + slope * xmin
                stop  = sint + slope * xmax
                plt.plot([xmin, xmax],[start,stop], color=color, lw =lsize )

#
#--- add legend
#
    if tot > 1:
        line = '['
        for ent in lnamList:
            if line == '[':
                line = line + ent
            else:
                line = line +', ' +  ent
        line = line + ']'

        leg = eval("legend(%s,  entLabels, prop=props)" % (line))
        leg.get_frame().set_alpha(0.5)

    ax.set_xlabel(xname, size=fsize)
    ax.set_ylabel(yname, size=fsize)


#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)



#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':
#
#--- if check is "check", you will be asked to input year and month
#
    check = 'normal'
    if len(sys.argv) == 2:
        check = sys.argv[1]
        check.strip()

    ccd_comb_plot(check)
