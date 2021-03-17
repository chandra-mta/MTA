#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#           update_aca_html_pages.py: update all aca html pages                             #
#                                                                                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 23, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import time
import random
import Chandra.Time
import numpy
import astropy.io.fits  as pyfits
#
#--- reading directory list
#
path = '/data/mta/Script/ACA/Scripts/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

#
#--- append a path to a private folder to python directory
#
sys.path.append(mta_dir)

import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

dmon1 = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334] 
dmon2 = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335] 
inst_list = ['ACIS-1',  'ACIS-2',  'ACIS-3',  'ACIS-4', 'ACIS-5', 'ACIS-6', \
             'HRC-I-1', 'HRC-I-2', 'HRC-I-3', 'HRC-I-4', \
             'HRC-S-1', 'HRC-S-2', 'HRC-S-3', 'HRC-S-4']
slot_list = ['slot good','marginal', 'bad', 'type', 'name', 'rms_ra_err', 'rms_dec_err',\
             'rms_delta_mag,' 'number', 'avg_angynea', 'avg_angznea', 'number_nea', 'mta_status']

mon_list  = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

#-----------------------------------------------------------------------------------
#-- create_sub_html_page: read the old html page and create new sub aca subpage   --
#-----------------------------------------------------------------------------------

def create_sub_html_page(ifile= ''):
    """
    read the old html page and create new sub aca subpage
    input:  ifile   --- old html page, if not given, read from /Temp_comp_area/acatrd.html
    output: <web_dir>/<MMM><yy>/acatrd.html. plots are also copied to that directory
    """
    ichk = 0
    if ifile == '':
        ifile       = exc_dir + '/Temp_comp_area/acatrd.html'
        ichk = 1
#
#--- create the data lists from the old formatted html page
#
    data, tsave = extract_date_from_old_html(ifile)
#
#--- create a new table
#
    htable      =  create_html_table(data)
#
#--- find the year and month of the data created
#
    out         = Chandra.Time.DateTime(0.5 * (tsave[0] + tsave[1])).date
    atemp       = re.split('\.', out)
    out         = time.strftime('%Y:%m:%d', time.strptime(atemp[0], '%Y:%j:%H:%M:%S'))
    atemp       = re.split(':', out)
    year        = atemp[0]
    mon         = atemp[1]
    dyear       = int(float(year))
    dmon        = int(float(mon))
    lmon        = mcf.change_month_format(mon)
#
#--- read the template 
#
    tfile = house_keeping + 'Template/sub_page'
    with open(tfile, 'r') as f:
        template = f.read()
#
#--- substitute the values
#
    template = template.replace('#YEAR#',   year)
    template = template.replace('#MON#',    lmon)
    template = template.replace('#TABLE#',  htable)
#
#--- substitute magnitude slope and std values
#
    ifile    = data_dir + 'monthly_mag_stats'
    template = substitue_mag_stat(template, ifile, dyear, dmon)
#
#--- substitute slot slope and std values
#
    ifile    = data_dir + 'diff_mtatr_month_slope'
    template = substitue_slot_stat(template, ifile, dyear, dmon, 'POS')
    
    ifile    = data_dir + 'diff_mtatr_month_slope'
    template = substitue_slot_stat(template, ifile, dyear, dmon, 'DIFF')

    ifile    = data_dir + 'acacent_mtatr_month_slope'
    template = substitue_slot_stat(template, ifile, dyear, dmon, 'ANGY')
    template = substitue_slot_stat(template, ifile, dyear, dmon, 'ANGZ', col_start=10)
#
#--- substitute slot tables
#
    gtable   = make_slot_star_table(dyear, dmon, 'guide_gsst')
    template = template.replace('#GUIDE_LOOK#', gtable)

    ftable   = make_slot_star_table(dyear, dmon, 'fid_gsst')
    template = template.replace('#FID_LOOK#',   ftable)

    mtable   = make_slot_star_table(dyear, dmon, 'monitor_gsst')
    template = template.replace('#MON_LOOK#',   mtable)
#
#--- check the output directory and if it does not exist, create
#
    odir = web_dir + lmon.upper() + year[2] + year[3] + '/'
    if not os.path.isdir(odir):
        cmd = 'mkdir -p ' + odir
        os.system(cmd)
#
#--- write the new html page
#
    ofile = odir + 'acatrd.html'

    with open(ofile, 'w') as fo:
        fo.write(template)

#-----------------------------------------------------------------------------------
#-- extract_date_from_old_html: read the original html page created by flt_run_pipe 
#-----------------------------------------------------------------------------------

def extract_date_from_old_html(ifile):
    """
    read the original html page created by flt_run_pipe
    input:  ifile   --- original html file
    output: save    --- a list of lists of data
            tsave   --- a list of stating and stopping time in seconds from 1998.1.1
    """
    data  = mcf.read_data_file(ifile)
#
#--- save the reading in a matirx; initialize with 0.0
#
    save  = []
    tsave = []
    for k in range(0, 14):
        alist = []
        for m in range(0, 7):
            alist.append(0.0)

        save.append(alist)
#
#--- find the section of each instrument by looking for the instrument name
#
    dchk = 0
    for ent in data:
#
#--- checking starting and stopping time
#
        if dchk < 2:
            dmc = re.search('Seconds since', ent)
            if dmc is not None:
                atemp = re.split('\s+', ent)
                stime = float(atemp[0])
                tsave.append(stime)
                dchk += 1

        for n in range(0, 14):
            mc  = re.search(inst_list[n],  ent)
            if mc is not None:
                k = n
                m = 0
                break
#
#--- assume that the value appears without any html coding around
#
        if mcf.is_neumeric(ent):
            if m < 7:
                save[k][m] = float(ent)
                m += 1

    return save, tsave

#-------------------------------------------------------------------------------------------
#-- create_html_table: create html data table from a data file                            --
#-------------------------------------------------------------------------------------------

def create_html_table(data):
    """
    create html data table from a data file
    input:  data    --- a list of lists of data
    output: line    --- a html table 
    """
    line = '<table border=1 cellpadding=2 style="margin-left:auto;margin-right:auto;text-align:center;">\n'
    line = line + '<tr><td rowspan=2 style="padding-left:10px;padding-right:10px;">ID</td>'
    line = line + '<td rowspan=2>ID String</td>'
    line = line + '<td colspan=3>Magnitude</td><td colspan=3>Data Quality (%)</td>'
    line = line + '<td rowspan=2>Total Data</td></tr>\n'
    line = line + '<td>Average</td><td style="padding-left:10px;padding-right:10px;">Min</td>'
    line = line + '<td style="padding-left:10px;padding-right:10px;">Max</td>'
    line = line + '<td>Good</td><td>Marginal</td><td>Bad</td></tr>\n'

    for k in range(0, len(inst_list)):
        inum   = k + 1
        stitle = 'Average Magnitude for Fid ' + str(inum)

        line = line + '<td>' + str(inum)            + '</td>\n'

        line = line + '<td>'
        line = line + '<a href="javascript:WindowOpener(\''
        line = line + 'Plots/MAG_I_AVG_' + str(inum) + '.png\',\'' 
        line = line + stitle + '\')">' + inst_list[k] + '</a>'
        line = line + '</td>\n'

        line = line + '<td>' + '%2.3f' % data[k][4] + '</td>\n'
        line = line + '<td>' + '%2.3f' % data[k][5] + '</td>\n'
        line = line + '<td>' + '%2.3f' % data[k][6] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][0] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][1] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][2] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][3] + '</td>\n'
        line = line + '</tr>\n'

    line = line + '</table>\n'

    return line

#-------------------------------------------------------------------------------------------
#-- update_aca_index_page: update aca index page                                          --
#-------------------------------------------------------------------------------------------

def update_aca_index_page():
    """
    update aca index page
    input:  none, but use Template/index_template
    output: <out_path>/index.html
    """
    tfile = bin_dir  + '/house_keeping/Template/index_template'
    with open(tfile, 'r') as f:
        page  = f.read()
#
#--- magnitude slope, std 
#
    dfile = 'full_mag_stats'
    colno = 14
    head  = 'MAG'
    page  = substitue_idx_page(page, dfile, colno, head)

    dfile = 'recent_mag_stats'
    colno = 14
    head  = 'RMAG'
    page  = substitue_idx_page(page, dfile, colno, head)
#
#--- slot slope, std
#
    dfile = 'pos_err_mtatr_full_slope'
    colno = 8
    head  = 'POS'
    page  = substitue_idx_page(page, dfile, colno, head)
    dfile = 'pos_err_mtatr_recent_slope'
    colno = 8
    head  = 'RPOS'
    page  = substitue_idx_page(page, dfile, colno, head)

    dfile = 'diff_mtatr_full_slope'
    colno = 8
    head  = 'DIFF'
    page  = substitue_idx_page(page, dfile, colno, head)
    dfile = 'diff_mtatr_recent_slope'
    colno = 8
    head  = 'RDIFF'
    page  = substitue_idx_page(page, dfile, colno, head)

    dfile = 'acacent_mtatr_full_slope'
    colno = 8
    head  = 'ANGY'
    page  = substitue_idx_page(page, dfile, colno, head)
    dfile = 'acacent_mtatr_recent_slope'
    colno = 8
    head  = 'RANGY'
    page  = substitue_idx_page(page, dfile, colno, head)

    dfile = 'acacent2_mtatr_full_slope'
    colno = 8
    head  = 'ANGZ'
    page  = substitue_idx_page(page, dfile, colno, head)
    dfile = 'acacent2_mtatr_recent_slope'
    colno = 8
    head  = 'RANGZ'
    page  = substitue_idx_page(page, dfile, colno, head)
#
#--- create sub page link table; table runs from the most recent year to  year 1999 
#
    out   = time.strftime("%Y:%m", time.gmtime())
    atemp = re.split(':', out)
    lyear = int(float(atemp[0]))
    lmon  = int(float(atemp[1]))

    line  = ''
    for  year in range(lyear, 1998, -1):
        syear = str(year)
        syr   = syear[2] + syear[3]

        line  = line + '<tr>\n<th><a href="./aca_trend_year' + str(year) + '.html">'
        line  = line + str(year) + '</th>\n'

        for mon in range(1, 13):
            if (year == lyear) and (mon > lmon):
                cell = '<td>&#160;</td>\n'

            elif (year == 1999) and (mon < 8):
                cell = '<td>&#160;</td>\n'

            else:
                cell = '<td><a href="./'  +  mon_list[mon-1] + syr
                cell = cell + '/acatrd.html">' +  mon_list[mon-1] + syr   + '</a></td>\n'
            line = line + cell

        line  = line + '</tr>\n'

    page  = page.replace('#TABLE#', line)

    ofile = web_dir  + 'index.html'
    with open(ofile, 'w') as fo:
        fo.write(page)

#-----------------------------------------------------------------------------------
#-- substitue_idx_page: substitute slope and std values to index.html page template 
#-----------------------------------------------------------------------------------

def substitue_idx_page(page, dfile, col_no, head, cstart=0):
    """
    substitute slope and std values to index.html page template
    input:  page    --- tempalte string
            dfile   --- data file name (without the path)
            col_no  --- numbers of column in the data 
            head    --- header of the substituion string
            cstart  --- from where to start the data reading. defalut: 0
    output: page    --- updated template string
    """
#
#--- data has only one line data with col_no entries
#--- first half lists slopes and the last half lists std
#
    ifile = data_dir + dfile
    data  = mcf.read_data_file(ifile)
    atemp = re.split('\s+', data[0])
    for k in range(0, col_no):
        m = k + cstart
        try:
            slope    = atemp[m]
        except:
            slope    = 'nan'
        try:
            std      = atemp[m+col_no]
        except: 
            std      = 'nan'
        slp_name = '#' + head.upper() + '_SLP' + str(k) + '#'
        std_name = '#' + head.upper() + '_STD' + str(k) + '#'
        page     = page.replace(slp_name, slope)
        page     = page.replace(std_name, std)

    return page


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def update_one_year_pages(iyear=''):
    """
    upate yearly html page
    input:  year    --- year. if it is not given, update all years
    output: <web_dir>/aca_trend_year<yyyy>.html
    """
#
#--- find the current year and month 
#
    out   = time.strftime('%Y:%m:%d', time.gmtime())
    atemp = re.split(':', out)
    this_year  = int(float(atemp[0]))
    this_month = int(float(atemp[1]))
    this_day   = int(float(atemp[2]))
    if this_day < 5:
        this_month -= 1
        if this_month < 1:
            this_month = 12
            this_year -= 1
#
#--- set the year interval to create the pages
#
    if iyear == '':
        syear = 1999
        eyear = this_year + 1
    else:
        syear = iyear
        eyear = iyear + 1

    for year in range(syear, eyear):
        lyear = str(year)
        syear = lyear[2] + lyear[3]

        tfile = house_keeping + 'Template/one_year_template'
        with open(tfile, 'r') as f:
            template = f.read()

        template = template.replace('#YEAR#',  lyear)
        template = template.replace('#SYEAR#', syear)
#
#--- substitue slope and std of magnitude data
#
        dfile = 'yearly_mag_stats'
        template = substitue_year_page(template, dfile, year, 14, 'MAG')
#
#--- substitute slope and std of pos_err
#
        dfile = 'pos_err_mtatr_year_slope'
        template = substitue_year_page(template, dfile, year, 8, 'POS')
#
#--- substitue slope and std of magnitue difference
#
        dfile = 'diff_mtatr_year_slope'
        template = substitue_year_page(template, dfile, year, 8, 'DIFF')
#
#--- substitute slope and std of angy
#
        dfile = 'acacent_mtatr_year_slope'
        template = substitue_year_page(template, dfile, year, 8, 'ANGY')
#
#--- subsititute  slope and std of angz
#
        dfile = 'acacent2_mtatr_year_slope'
        template = substitue_year_page(template, dfile, year, 8, 'ANGZ')

#
#--- create a table to link to the each month of this year
#
        if year == 1999:
            smon = 8
            emon = 12
        elif year == this_year:
            smon = 1
            emon = this_month
        else:
            smon = 1
            emon = 12
        line = '<table border=1 cellspacing=2 cellpadding=2>\n'
        line = line + '<tr>\n'
        for mon in range(1, 13):
            lmon =  mcf.change_month_format(mon).upper()
            if mon < smon:
                line = line + '<td>' + lmon + '</td>\n'
            elif mon > emon:
                line = line + '<td>' + lmon + '</td>\n'
            else:
                line = line + '<td><a href="./' + lmon + syear
                line = line + '/acatrd.html">' + lmon + '</a>\n'

        line = line + '</table>\n'

        template = template.replace('#LTABLE#', line)
#
#--- update the html page
#
        outname = web_dir + 'aca_trend_year' + str(year) + '.html'
        with open(outname, 'w') as fo:
            fo.write(template)


#-----------------------------------------------------------------------------------
#-- substitue_year_page: substitue slope and std on one year pag                  --
#-----------------------------------------------------------------------------------

def substitue_year_page(page, dfile, year, col_no, head, cstart=1):
    """
    substitue slope and std on one year page
    input:  page    --- template
            dfile   --- data file
            year    --- the year of the page created
            col_no  --- numuber of data column
            head    --- header of substition string
            cstart  --- starting column
    output: page    --- updated tempalte
    """
    ifile = data_dir + dfile
    data  = mcf.read_data_file(ifile)
    for ent in data:
        atemp = re.split('\s+', ent)
        if float(atemp[0]) == year:
            for k in range(0, col_no):
                m = k + cstart
                slope    = atemp[m]
                std      = atemp[m+col_no]
                slp_name = '#' + head.upper() + '_SLP' + str(k) + '#'
                std_name = '#' + head.upper() + '_STD' + str(k) + '#'
                page     = page.replace(slp_name, slope)
                page     = page.replace(std_name, std)
            break
        
    return page

#-----------------------------------------------------------------------------------
#-- substitue_slot_stat: substitute slope and std of magnitue tables of monthly page
#-----------------------------------------------------------------------------------

def substitue_slot_stat(template, ifile,  dyear, dmon, sname, col_start=2):
    """
    substitute slope and std of magnitue tables of monthly page
    input:  template    --- template
            ifile       --- input file name
            dyear       --- year of the page
            dmon        --- month of the page
            sname       --- header of the substition string
            col_starts  --- starting column postion
    output: template    --- updated template
    """
    data  = mcf.read_data_file(ifile)
    for ent in data:
        atemp = re.split('\s+', ent)
        btemp = re.split(':', atemp[1])
        year  = int(float(btemp[0]))
        mon   = int(float(btemp[1]))
        if year == dyear and mon == dmon:
            for k in range(0, 8):
                slope = atemp[k+ col_start]
                if slope == '-999.0':
                    slope = 'nan'

                std   = atemp[k+ col_start + 8]
                if std == '-999.0':
                    std   = 'nan'

                slope_name = '#' + sname + '_SLP' + str(k) + '#'
                std_name   = '#' + sname + '_STD' + str(k) + '#'
                template   = template.replace(slope_name,  slope)
                template   = template.replace(std_name,    std)
            break

    return template

#-----------------------------------------------------------------------------------
#-- substitue_mag_stat: substitute slope and std of slot tables of monthly page   --
#-----------------------------------------------------------------------------------

def  substitue_mag_stat(template, ifile, dyear, dmon):
    """
    substitute slope and std of slot tables of monthly page
    input:  template    --- template
            ifile       --- input file name
            dyear       --- year of the page
            dmon        --- month of the page
    output: template    --- updated template
    """
    data = mcf.read_data_file(ifile)
    for ent in data:
        atemp = re.split('\s+', ent)
        btemp = re.split(':', atemp[0])
        year  = int(float(btemp[0]))
        mon   = int(float(btemp[1]))
        if year == dyear and mon == dmon:
            for k in range(1, 15):
                slope = atemp[k]
                if slope == '-999.0':
                    slope = 'nan'
                std   = atemp[k+14]
                if std == '-999.0':
                    std   = 'nan'

                slope_name = '#MAG_SLP' + str(k) + '#'
                std_name   = '#MAG_STD' + str(k) + '#'
                template   = template.replace(slope_name, slope)
                template   = template.replace(std_name,   std)
            break

    return template

#-----------------------------------------------------------------------------------
#-- make_slot_star_table: create a slot data table for the monthly html page      --
#-----------------------------------------------------------------------------------

def make_slot_star_table(dyear, dmon, tail):
    """
    create a slot data table for the monthly html page
    input:  dyear   --- year
            dmon    --- month
            tail    --- a part of fits file name used to find the file
    output:  line   --- a html table string
    """
#
#--- find data fits file
#
    lyear = str(dyear)
    ddir  = data_dir + 'Fits_data/' + mcf.change_month_format(dmon).upper() + lyear[2] + lyear[3] + '/'
    cmd   = 'ls ' + ddir + '*_' + tail + '.fits.gz > ' + zspace
    os.system(cmd)
#
#--- if there is no data fits file, say so
#
    out   = mcf.read_data_file(zspace, remove=1)
    if len(out) == 0:
        return '<h3>No Slot Data</h3>'
#
#--- read the data fits file
#
    fits  = out[0].strip()
    fout  = pyfits.open(fits)
    fdata = fout[1].data
    fout.close()
#
#--- extract each column data
#
    good     = fdata['good']
    marginal = fdata['marginal']
    bad      = fdata['bad']
    ra_rms   = fdata['rms_ra_err']
    dec_rms  = fdata['rms_dec_err']
    mag_rms  = fdata['rms_delta_mag']
    angy     = fdata['avg_angynea']
    angz     = fdata['avg_angznea']
    nums     = fdata['number']
    num_nea  = fdata['number_nea']
#
#--- create slot data html data table
#
    line  = '<table border=1 cellpadding=3>\n'
    line  = line + '<tr>\n'
    line  = line + '<th>slot</th><th>rms_ra_err (deg)</th><th>rms_dec_err (deg)</th>\n'
    line  = line + '<th>rms_delta_mag (marcsec)</th><th>number</th>\n'
    line  = line + '<th>avg_angynea (arcsec)</th><th>avg_angznea (arcsec)</th>\n'
    line  = line + '<th>number_nea</th>\n'
    line  = line + '<th>good</th><th>marginal</th><th>bad</th>\n'
    line  = line + '</tr>\n'

    for k in range(0, 8):
        line = line + '<tr>\n'
        line = line + '<th>' + str(k) + '</th>'
        line = line + '<td>%2.3e</td>' % ra_rms[k]
        line = line + '<td>%2.3e</td>' % dec_rms[k]
        line = line + '<td>%2.3e</td>' % mag_rms[k]
        line = line + '<td>%4d</td>'   % nums[k]
        line = line + '<td>%2.3e</td>' % angy[k]
        line = line + '<td>%2.3e</td>' % angz[k]
        line = line + '<td>%4d</td>'   % num_nea[k]
        line = line + '<td>%2.2f</td>' % good[k]
        line = line + '<td>%2.2f</td>' % marginal[k]
        line = line + '<td>%2.2f</td>' % bad[k]
        line = line + '</tr>\n'

    line = line + '<tr>\n'
    line = line + '<th>AVG</th>'
    line = line + '<td>%2.3e</td>' % numpy.mean(ra_rms)
    line = line + '<td>%2.3e</td>' % numpy.mean(dec_rms)
    line = line + '<td>%2.3e</td>' % numpy.mean(mag_rms)
    line = line + '<td>%4d</td>'   % numpy.mean(nums)
    line = line + '<td>%2.3e</td>' % numpy.mean(angy)
    line = line + '<td>%2.3e</td>' % numpy.mean(angz)
    line = line + '<td>%4d</td>'   % numpy.mean(num_nea)
    line = line + '<td>%2.2f</td>' % numpy.mean(good)
    line = line + '<td>%2.2f</td>' % numpy.mean(marginal)
    line = line + '<td>%2.2f</td>' % numpy.mean(bad)
    line = line + '</tr>\n'

    line = line + '</table>'

    return line

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    create_sub_html_page()
    update_one_year_pages()
    update_aca_index_page()

#    for year in range(1999, 2022):
#        for month in range(1, 13):
#            if year == 1999 and month < 8:
#                continue
#            if year == 2021 and month > 3:
#                break
#            lyear = str(year)
#            syear = lyear[2] + lyear[3]
#            lmon  = mcf.change_month_format(month).upper()
#            print(lyear + '   ' + lmon)
#
#            ifile = '/data/mta4/www/DAILY/mta_pcad/ACA/' + lmon + syear + '/acatrd.html'
#            if os.path.isfile(ifile):
#                create_sub_html_page(ifile)
#            else:
#                with open('./missing_file', 'a') as fo:
#                    line = lyear + '   ' + lmon + '\n'
#                    fo.write(line)
