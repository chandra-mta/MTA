#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       ccd_comb_plot.py: read data and create SIB plots                                    #
#                           monthly, quorterly, one year, and last year                     #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               Last Update: Apr 2, 2014                                                    #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import pyfits
import numpy

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
    path = '/data/mta/Script/ACIS/SIB/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- check whether this is run for lev2
#
level = 1
if len(sys.argv) == 2:
    if sys.argv[1] == 'lev2':
        data_dir = data_dir2
        web_dir  = web_dir + 'Lev2/'
        level = 2

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
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
nameList = ['Super Soft Photons', 'Soft Photons', 'Moderate Energy Photons', 'Hard Photons', 'Very Hard Photons', 'Beyond 10 keV']

#---------------------------------------------------------------------------------------------------
#-- ccd_comb_plot: a control script to create plots                                              ---
#---------------------------------------------------------------------------------------------------

def ccd_comb_plot(choice, syear = 2000, smonth = 1, eyear = 2000, emonth = 1, header = 'plot_ccd'):

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
#--- find today's date, and set a few thing needed to set output directory and file name
#
    if choice != 'check':
        [year, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()

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
#--- normal monthly operation
#
    if choice == 'normal':
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
#
#--- special case which we need to specify periods
#
    elif choice == 'check':
    
        dlist  = collect_data_file_names('check', syear, smonth, eyear, emonth)
        plot_out = web_dir + '/Plot/'
        check_and_create_dir(plot_out)
#        header   = 'plot_special_ccd'
        plot_data(dlist, plot_out, header, yr=syear, mo=smonth)
#
#--- extra...
#
    else:
        for year in range(2000, 2014):

            dlist  = collect_data_file_names('check', year, 1, year, 12)
            plot_out = web_dir + '/Plots/Plot_' + str(year) + '/'
            check_and_create_dir(plot_out)
            header = 'one_year_plot_ccd'
            plot_data(dlist, plot_out, header, yr = str(year))

            for month in range(1, 13):
                print " Processing: " + str(year) + ' / ' + str(month)
                smonth = str(month)
                if month < 10:
                    smonth = '0' + smonth
    
                dlist = collect_data_file_names('check', year, month, year, month)
                plot_out = web_dir + '/Plots/Plot_' + str(year) + '_' + smonth +  '/'
                check_and_create_dir(plot_out)
                header = 'month_plot_ccd'
                plot_data(dlist, plot_out, header, yr=str(year), mo=smonth, psize=2.5)
     
#---------------------------------------------------------------------------------------------------
#-- check_and_create_dir: check whether a directory exist, if not, create one                    ---
#---------------------------------------------------------------------------------------------------

def check_and_create_dir(dir):

    """
    check whether a directory exist, if not, create one
    Input:      dir --- directory name
    Output:     directory created if it was not there.
    """

    chk = mcf.chkFile(dir)
    if chk == 0:
        cmd = 'mkdir ' + dir
        os.system(cmd)

#---------------------------------------------------------------------------------------------------
#-- define_x_range: set time plotting range                                                      ---
#---------------------------------------------------------------------------------------------------

def define_x_range(dlist, xunit=''):

    """
    set time plotting range
    Input:  dlist       --- list of data files (e.g., Data_2012_09)
    Output: start       --- starting time in either DOM or fractional year
            end         --- ending time in either DOM or fractional year
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

    start  = tcnv.findDOM(year,  month,  1, 0, 0, 0)
    end    = tcnv.findDOM(nyear, nmonth, 1, 0, 0, 0)   
#
#--- if it is a long term, unit is in year
#
    if xunit == 'year':
        [syear, sydate] = tcnv.DOMtoYdate(start)
        chk = 4.0 * int(0.25 * syear)
        if chk == syear:
            base = 366
        else:
            base = 365
        start = syear + sydate/base
        [eyear, eydate] = tcnv.DOMtoYdate(end)
        chk = 4.0 * int(0.25 * eyear)
        if chk == eyear:
            base = 366
        else:
            base = 365
        end   = eyear + eydate/base

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
#--- if the plot is a long term, use the unit of year. otherwise, dom
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
                sum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                count_full.append(sum)
                ydata.append(sum)

            if ccd == 5:
                time_ccd5 = xtime
                for i in range(0, len(xtime)):
                    sum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                    count_ccd5.append(sum)
            if ccd == 6:
                time_ccd6 = xtime
                for i in range(0, len(xtime)):
                    sum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                    count_ccd6.append(sum)
            if ccd == 7:
                time_ccd7 = xtime
                for i in range(0, len(xtime)):
                    sum = assoft[i] + asoft[i] + amed[i] + ahard[i] + aharder[i] + ahardest[i]
                    count_ccd7.append(sum)
#
#--- prepare for the indivisual plot
#
            xsets = []
            for i in range(0, 6):
                xsets.append(xtime)
            data_list = (assoft, asoft, amed, ahard, aharder, ahardest)
#
#--- plottting data
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


#---------------------------------------------------------------------------------------------------
#-- add_html_page: update/add html page to Plot directory                                        ---
#---------------------------------------------------------------------------------------------------

def add_html_page(ptype, plot_out,  yr, mo):

    """
    update/add html page to Plot directory
    Input:  ptype       --- indiecator of which html page to be updated
            plot_out    --- a directory where the html page is updated/created
            yr          --- a year of the file
            mo          --- a month of the file
    Output: either month.html or year.hmtl in an appropriate directory
    """

    current = tcnv.currentTime(format='Display')
    lmon    = ''

    if ptype == 'month':
        ofile  = plot_out + 'month.html'
        lmon   = tcnv.changeMonthFormat(int(mo))
        if level == 2:
            file = house_keeping + 'month2.html'
        else:
            file = house_keeping + 'month.html'

    elif ptype == 'year':
        ofile  = plot_out + 'year.html'
        if level == 2:
            file = house_keeping + 'year2.html'
        else:
            file = house_keeping + 'year.html'

    text = open(file, 'r').read()
    text = text.replace('#YEAR#',  str(yr))
    text = text.replace('#MONTH#', str(lmon))
    text = text.replace('#DATE#',  str(current))
    
    f     = open(ofile, 'w')
    f.write(text)
    f.close()

#---------------------------------------------------------------------------------------------------
#-- change_outname_comb: change file name to "comb" form                                         ---
#---------------------------------------------------------------------------------------------------

def change_outname_comb(header, plot_out, ccd):

    """
    change file name to "comb" form
    Input:  header      --- original header form
            plot_out    --- output directory name
            ccd         --- ccd #
    Output: outname     --- <plot_out>_<modified header>_ccd<ccd#>.png
    """

    print "I AM HERE: " + str(header)
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
     
    try:
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
            xname = 'Time (DOM)'
        yname = 'cnts/s'
#
#--- actual plotting is done here
#
        plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, outname, psize=psize)
    except:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + outname
        os.system(cmd)

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
    [year, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()

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
#-- read_data_file: read out needed data from a given file                                       ---
#---------------------------------------------------------------------------------------------------

def read_data_file(file):

    """
    read out needed data from a given file
    Input:  file    --- input file name
    Output: a list of lists of data: [time, ssoft, soft, med, hard, harder, hardest]
    """

    try:
        hdulist = pyfits.open(file)
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

def accumulate_data(inlist, file):

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
        infile = dname + '/' + file

        chk = mcf.chkFile(infile)
        if chk == 0:
            infile = infile + '.gz'

        try:
            [time, ssoft, soft, med, hard, harder, hardest] = read_data_file(infile)
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

def convert_time(time, format  = 0):

    """
    convert time format from seconds from 1998.1.1 to dom or fractional year
    Input:  time    --- a list of time in seconds
            format  --- if 0, convert into dom, otherwise, fractional year
    Output: timeconverted --- a list of conveted time
    """

    timeconverted = []
    for ent in time:
        stime = tcnv.convertCtimeToYdate(ent)
        atime = tcnv.dateFormatConAll(stime)

        if format == 0: 
            timeconverted.append(float(atime[7]))
        else:
            year  = float(atime[0])
            ydate = float(atime[6])
            chk   = 4.0 *  int(0.25 * year)
            if chk == year:
                base = 366
            else:
                base = 365
            year += ydate /base

            timeconverted.append(year)
        
    return timeconverted

#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, outname, psize=1.0):

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
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
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

        exec "%s = plt.subplot(%s)"       % (axNam, line)
        exec "%s.set_autoscale_on(False)" % (axNam)      #---- these three may not be needed for the new pylab, but 
        exec "%s.set_xbound(xmin,xmax)"   % (axNam)      #---- they are necessary for the older version to set

        exec "%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam)
        exec "%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam)

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

        exec "%s.set_ylabel(yname, size=8)" % (axNam)

#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            exec "line = %s.get_xticklabels()" % (ax)
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
    plt.savefig(outname, format='png', dpi=100)


#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':
    ccd_comb_plot('normal')
#    ccd_comb_plot('other')
#    ccd_comb_plot('check', syear=2019, smonth=2, eyear=2019, emonth=2, header='month_plot_ccd')


