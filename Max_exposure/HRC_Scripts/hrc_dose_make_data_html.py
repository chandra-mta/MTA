#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       hrc_dose_make_data_html.py:   create  html data pages for a report              #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 09, 2021                                                       #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
#
#--- reading directory list
#
path = '/data/mta/Script/Exposure/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a privte folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions as mcf
import exposureFunctions    as expf

#--------------------------------------------------------------------------------------------
#--- hrc_dose_plot_exposure_stat: read hrc database, and plot history of exposure         ---
#--------------------------------------------------------------------------------------------

def hrc_dose_make_data_html(indir = 'NA', outdir = 'NA'):
    """
    read hrc database, and create html page: 
    input:  indir   --- data directory
            outdir  --- output direcotry
    """
    if indir   == 'NA':
        indir   = data_out

    if outdir  == 'NA':
        outdir  = data_out

    for hrc in ('hrci', 'hrcs'):
#
#--- just in a case, clear up the files before reading them
#
        expf.clean_data(indir)
#
#--- read HRC histrical data
#
        data = expf.readExpData(indir, hrc)
#
#--- create a HTML page to display histrical data
#
        print_html_page(indir, outdir, hrc, data)

#--------------------------------------------------------------------------------
#--  print_html_page: create HTML page to display HRC historical data        ----
#--------------------------------------------------------------------------------

def print_html_page(indir, outdir, hrc, data):
    """
    create HTML page to display HRC historical data.
    input:  indir   --- input dir
            outdir  --- output dir
            hrc     --- hrc
            data    --- a list of lists of data 
    output: <outdir>/<hrc>.html
    """
#
#--- open the data ; except the first three, all others are lists of data
#
    (date, year, month, mean_acc, std_acc, min_acc, min_apos, \
     max_acc, max_apos, asig1, asig2, asig3, mean_dff, std_dff,\
     min_dff, min_dpos, max_dff, max_dpos, dsig1, dsig2, dsig3)  = data

    outdir = outdir + '/' + hrc + '.html'
#
#--- start writing the html page
#
    line = '<!DOCTYPE html>\n'
    line = line + '<html>\n'
    line = line + '<head>\n'

    line = line + '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'

    line = line + '<style  type="text/css">\n'
    line = line + 'body{background-color:#FFEBCD;}\n'
    line = line + 'table{text-align:center;margin-left:auto;margin-right:auto;'
    line = line + 'border-style:solid;border-spacing:8px;border-width:2px;'
    line = line + 'border-collapse:separate}\n'
    line = line + 'a:link {color:green;}\n'
    line = line + 'a:visited {color:red;}\n'
    line = line + 'td{text-align:center;padding:8px}\n'
    line = line + '</style>\n'

    if hrc == 'hrci':
        hname = 'HRC I'
        wname = 'HRCI'
    else:
        hname = 'HRC S'
        wname = 'HRCS'

    line = line + '<title>' + hname + ' History Data</title>\n'
    line = line + '</head>\n'

    line = line + '<body>\n'
    line = line + '<h2 style="text-align:center">Data: ' + hname + '</h2>\n'

    line = line + '<div style="padding-bottom:30px">\n'
    line = line + '<table border=1>\n'
    line = line + '<tr><th>&#160;</th><th>&#160;</th><th colspan=11>'
    line = line + 'Monthly</th><th colspan=11>Cumulative</th></tr>\n'
    line = line + '<tr style="color:blue"><th>Year</th><th>Month</th>\n'
    line = line + '<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th>\n'
    line = line + '<th>Max</th><th>Max Position</th><th>68% Level</th>'
    line = line + '<th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th>\n'
    line = line + '<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th>'
    line = line + '<th>Max</th><th>Max Position</th><th>68% Level</th>'
    line = line + '<th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th></tr>\n'

    for i in range(0, len(date)):

        smonth = mcf.add_leading_zero(month[i])
        cmonth = mcf.change_month_format(month[i])
        syear  = str(int(year[i]))
#
#--- monthly HRC dose data
#
        if mean_dff[i] == 0 and std_dff[i] == 0:
#
#--- for the case there is no data for this month
#
            line = line + '<tr><td>%d</td><td>%d</td>' % (year[i], month[i])
            line = line + '<td>NA</td><td>NA</td><td>NA</td><td>NA</td><td>NA</td><td>NA</td>\n'
            line = line + '<td>NA</td><td>NA</td><td>NA</td><td>No Data</td><td>No Image</td>\n'
            #line = line + '</tr>\n'
        else:
            line = line + '<tr>'
            line = line + '<td>%d</td>'         % year[i]
            line = line + '<td>%d</td>'         % month[i]
            line = line + '<td>%4.4f</td>'      % mean_dff[i]
            line = line + '<td>%4.4f</td>'      % std_dff[i]
            line = line + '<td>%4.1f</td>'      % min_dff[i]
            line = line + '<td>%s</td>'         % min_dpos[i]
            line = line + '<td>%4.1f</td>'      % max_dff[i]
            line = line + '<td>%s</td>'         % max_dpos[i]
            line = line + '<td>%4.1f</td>'      % dsig1[i]
            line = line + '<td>%s</td>'         % dsig2[i]
            line = line + '<td>%4.1f</td>\n'    % dsig3[i]

            line = line + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Month_hrc/' 
            line = line + wname + '_' + smonth + '_' + syear + '.fits.gz' 
            line = line + '">fits</a></td>\n'
            line = line + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/' 
            line = line + wname + '_' + smonth + '_' + syear + '.png' 
            line = line + '">map</a></td>\n'
#
#---- cumulative HRC dose data
#
        line = line + '<td>%4.4f</td>'      % mean_acc[i]
        line = line + '<td>%4.4f</td>'      % std_acc[i]
        line = line + '<td>%4.1f</td>'      % min_acc[i]
        line = line + '<td>%s</td>'         % min_apos[i]
        line = line + '<td>%4.1f</td>'      % max_acc[i]
        line = line + '<td>%s</td>'         % max_apos[i]
        line = line + '<td>%4.1f</td>'      % asig1[i]
        line = line + '<td>%s</td>'         % asig2[i]
        line = line + '<td>%4.1f</td>\n'    % asig3[i]

        line = line + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Cumulative_hrc/' 
        line = line + wname + '_08_1999_' + smonth + '_' + syear + '.fits.gz' 
        line = line + '">fits</a></td>\n'
        line = line + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/' 
        line = line + wname + '_08_1999_' + smonth + '_' + syear + '.png' 
        line = line + '">map</a></td>\n'
        line = line + '</tr>\n\n'
#
#--- put header every new year so that we can read data easier
#
        if month[i] % 12 == 0 and i != (len(date)-1):
            line = line + '\n<tr style="color:blue"><th>Year</th><th>Month</th>'
            line = line + '<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th>'
            line = line + '<th>Max</th><th>Max Position</th><th>68% Level</th>'
            line = line + '<th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th>\n'
            line = line + '<th>Mean</th><th>SD</th><th>Min</th><th>Min Position</th>'
            line = line + '<th>Max</th><th>Max Position</th><th>68% Level</th>'
            line = line + '<th>95% Level</th><th>99.7% Level</th><th>Data</th><th>Map</th></tr>\n\n'

    line = line + '</table>\n\n'
    line = line + "</div>\n"
    line = line + '<hr />\n'
#
#--- set current date
#
    [tyear, tmon, tday] = mcf.today_date()

    lmon = mcf.add_leading_zero(tmon)
    lday = mcf.add_leading_zero(tday)

    line = line + '<p style="padding-top:10px;padding-bottom:10px">'
    line = line + '<strong style="font-size:105%;float:right">Last Update: ' 
    line = line + lmon + '/' + lday + '/' + str(tyear) + '</strong></p>\n'

    line = line + '<p>If you have any questions about this page, contact '
    line = line + ' <a href="mailto:isobe@haed.cfa.harvad.edu">isobe@haed.cfa.harvad.edu.</a></p>\n'
    line = line + '</body>\n'
    line = line + '</html>\n'

    with open(outdir, 'w') as fo:
        fo.write(line)

#--------------------------------------------------------------------------------
#-- update_main_html: update main html page                                   ---
#--------------------------------------------------------------------------------

def update_main_html():
    """
    update main html page
    input: none but read a template from <house_keeping>
    output: <web_dir>/expousre.html
    """
    [tyear, mon, day] = mcf.today_date() 
    today             = mcf.change_month_format(mon)
    today             = today + ' '  + mcf.add_leading_zero(day) 
    today             = today + ', ' + str(tyear)

    syear = tyear
    smon  = mon -1
    if smon < 1:
        smon  = 12
        syear = tyear -1

    lyear = str(syear)
    lmon  = mcf.add_leading_zero(smon)
    line  = lmon + '_' + lyear

    aline = mcf.change_month_format(smon) + ' ' + lyear

    ifile = house_keeping + 'template'
    with open(ifile, 'r') as f:
        data = f.read()

    data  = data.replace('#ODATE#', line)
    data  = data.replace('#DATE#',  aline)
    data  = data.replace('#TODAY#', today)

    ifile = web_dir + 'exposure.html'
    with open(ifile, 'w') as fo:
        fo.write(data)

#--------------------------------------------------------------------------------

if __name__ == '__main__':

    hrc_dose_make_data_html()
    update_main_html()
