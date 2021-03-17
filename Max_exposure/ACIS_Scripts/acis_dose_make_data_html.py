#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       acis_dose_make_data_html.py: create html pages for ACIS CCDs                    #
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
#--- append path to a privte folder
#
sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions as mcf
import exposureFunctions    as expf

#----------------------------------------------------------------------------------------
#--- acis_dose_make_data_html: read hrc database, and plot history of exposure        ---
#----------------------------------------------------------------------------------------

def acis_dose_make_data_html(indir = 'NA', outdir = 'NA'):
    """
    read data and create html pages
    input:  indir   --- input data directory
            outdir  --- html directory
    """
#
#--- setting indir and outdir if not given
#
    if indir   == 'NA':
        indir   = data_out

    if outdir  == 'NA':
        outdir  = data_out
#
#--- read data
#
    for ccd in ('i_2', 'i_3', 's_2', 's_3'):
        for sec in range(0, 4):

            inst  = ccd + '_n_' + str(sec)
            data  = expf.readExpData(indir, inst)
#
#--- write html page
#
            outfile = outdir + inst + '.html'
            write_html(ccd, sec, data, outfile)
#
#--- update top html page (this is done in HRC)
#
#    line = house_keeping + 'exposure.html'
#    with open(line, 'r') as f:
#        data = f.read()
#
#    now   = time.strftime("%m %d %Y", time.gmtime())
#    [syear, smon, day] = mcf.today_date()
#    smon -= 1
#
#    if smon < 1:
#        smon   = 12
#        syear -= 1
#    lyear = str(syear)
#    lmon  = mcf.add_leading_zero(smon)
#
#    data  = data.replace("#DATE#",  now)
#    data  = data.replace("#YEAR#", lyear)
#    data  = data.replace("#MON#",  lmon)
#
#    ofile = web_dir + 'exposure.html'
#    with open(ofile, 'w') as fo:
#        fo.write(data)
#
#--- update plot page htmls
#
    update_plt_html_date()

#----------------------------------------------------------------------------------------
#--    write_html: write a html page                                                   --
#----------------------------------------------------------------------------------------

def write_html(ccd, sec, data, outfile):
    """
    write a html page:
    input:  ccd     --- ccd; e.g., i2, s3
            sec     --- section 0 - 3
            data    --- a list of lists of data
                        date, year,month,mean_acc,std_acc,min_acc,min_apos,  
                        max_acc,max_apos,m10_acc,  m10_apos,mean_dff,std_dff,
                        min_dff, min_dpos,max_dff,max_dpos,m10_dff,m10_dpos
            outfile --- output file name
    output: outfile
    """
#
#--- open the list of lists
#
    [date, year,month,mean_acc,std_acc,min_acc,min_apos,\
     max_acc,max_apos, asig1, asig2, asig3, mean_dff,std_dff,\
     min_dff, min_dpos,max_dff,max_dpos,dsig1, dsig2, dsig3] = data
#
#--- today's date
#
    [lyear, lmon, lday] = mcf.today_date()
#
#--- start writing a html page
#
    sline = '<!DOCTYPE html>\n'
    sline = sline + '<html>\n'
    sline = sline + '<head>\n'
    sline = sline + '<title>ACIS ' + ccd.upper() + ' Section ' 
    sline = sline + str(sec) + ' History Data</title>\n'
    sline = sline + "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />"
#
#--- css style sheet
#
    sline = sline + '<style type="text/css">\n'
    sline = sline + 'body{background-color:#FFEBCD;}\n'
    sline = sline + 'table{text-align:center;margin-left:auto;margin-right:'
    sline = sline + 'auto;border-style:solid;border-spacing:8px;border-width:'
    sline = sline + '2px;border-collapse:separate}\n'
    sline = sline + 'td {text-align:center}\n'
    sline = sline + 'a:link {color:green;}\n'
    sline = sline + 'a:visited {color:red;}\n'
    sline = sline + '</style>\n'

    sline = sline + '</head>\n'

    sline = sline + '<body> \n'

#    sline = sline + '<br /><h3> Last Update: ' 
#    sline = sline + mcf.add_leading_zero(lmon) + '/'
#    sline = sline + mcf.add_leading_zero(lday) + '/'
#    sline = sline + str(lyear) + '</h3>\n'
    sline = sline + '<table border=1>\n'

    sline = sline + header_write() + '\n'

    for i in range(0, len(year)):
        sline = sline + '<tr>\n'

        sline = sline + '<td>' + str(year[i])     + '</td>\t'
        sline = sline + '<td>' + str(month[i])    + '</td>\t'
        sline = sline + '<td>' + str(mean_dff[i]) + '</td>\t'
        sline = sline + '<td>' + str(std_dff[i])  + '</td>\t'
        sline = sline + '<td>' + str(min_dff[i])  + '</td>\t'
        sline = sline + '<td>' + str(min_dpos[i]) + '</td>\t'
        sline = sline + '<td>' + str(max_dff[i])  + '</td>\t'
        sline = sline + '<td>' + str(max_dpos[i]) + '</td>\t'
        sline = sline + '<td>' + str(dsig1[i])    + '</td>\t'
        sline = sline + '<td>' + str(dsig2[i])    + '</td>\t'
        sline = sline + '<td>' + str(dsig3[i])    + '</td>\t'

        syear = str(int(year[i]))
        smon  = mcf.add_leading_zero(month[i])
        lccd  = ccd.replace('_', '')
        ifile = 'ACIS_' + smon + '_' + syear + '_' + lccd 

        sline = sline + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Month/' 
        sline = sline + ifile + '.fits.gz">fits</a></td>\n'
        sline = sline + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/' 
        sline = sline + ifile + '.png">map</a></td>\n\n'

        sline = sline + '<td>' + str(mean_acc[i]) + '</td>\t'
        sline = sline + '<td>' + str(std_acc[i])  + '</td>\t'
        sline = sline + '<td>' + str(min_acc[i])  + '</td>\t'
        sline = sline + '<td>' + str(min_apos[i]) + '</td>\t'
        sline = sline + '<td>' + str(max_acc[i])  + '</td>\t'
        sline = sline + '<td>' + str(max_apos[i]) + '</td>\t'
        sline = sline + '<td>' + str(asig1[i])    + '</td>\t'
        sline = sline + '<td>' + str(asig2[i])    + '</td>\t'
        sline = sline + '<td>' + str(asig3[i])    + '</td>\n'

        ifile = 'ACIS_07_1999_' + smon + '_' + syear + '_' + lccd 
        sline = sline + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Cumulative/' 
        sline = sline + ifile + '.fits.gz">fits</a></td>\n'
        sline = sline + '<td><a href="https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/' 
        sline = sline + ifile + '.png">map</a></td>'

        sline = sline + '</tr>\n\n'
#
#--- put header every new year so that we can read data easier
#
        if month[i] % 12 == 0 and i != (len(year)-1):
            sline = sline + header_write() + '\n'

    sline = sline + '</table>\n\n'
    sline = sline + '<br /><br /><hr /><br />\n'

    sline = sline + '<br /><strong style="font-size:105%;float:right">Last Update: ' 
    sline = sline + mcf.add_leading_zero(lmon) + '/' 
    sline = sline + mcf.add_leading_zero(lday) + '/' 
    sline = sline + str(lyear) + '</strong>\n'

    sline = sline + '<p>If you have any questions about this page, contact '
    sline = sline + '<a href="mailto:isobe@haed.cfa.harvad.edu">'
    sline = sline + 'isobe@haed.cfa.harvad.edu.</a></p>\n'

    sline = sline + '</body>\n'
    sline = sline + '</html>\n'

    with open(outfile, 'w') as fo:
        fo.write(sline)

#------------------------------------------------------------------------
#-- header_write: writing header part of html                         ---
#------------------------------------------------------------------------

def header_write():    
    """
    writing a header part of html
    input:   none
    output: header line
    """
    sline = ''
    sline = sline + '<tr style="color:blue">\n'
    sline = sline + '<td>&#160;</td><td>&#160;</td>\n'
    sline = sline + '<td colspan=11>Monthly</td>\n'
    sline = sline + '<td colspan=11>Cumulative</td>\n'
    sline = sline + '</tr><tr>\n'

    sline = sline + '<th>Year</th>\n'
    sline = sline + '<th>Month</th>\n'
    sline = sline + '<th>Mean</th>\n'
    sline = sline + '<th>SD</th>\n'
    sline = sline + '<th>Min</th>\n'
    sline = sline + '<th>Min Position</th>\n'
    sline = sline + '<th>Max</th>\n'
    sline = sline + '<th>Max Position</th>\n'
    sline = sline + '<th>68% Level</th>\n'
    sline = sline + '<th>95% Level</th>\n'
    sline = sline + '<th>99.7% Level</th>\n'
    sline = sline + '<th>Data</th>\n'
    sline = sline + '<th>Map</th>\n'

    sline = sline + '<th>Mean</th>\n'
    sline = sline + '<th>SD</th>\n'
    sline = sline + '<th>Min</th>\n'
    sline = sline + '<th>Min Position</th>\n'
    sline = sline + '<th>Max</th>\n'
    sline = sline + '<th>Max Position</th>\n'
    sline = sline + '<th>68% Level</th>\n'
    sline = sline + '<th>95% Level</th>\n'
    sline = sline + '<th>99.7% Level</th>\n'
    sline = sline + '<th>Data</th>\n'
    sline = sline + '<th>Map</th>\n'
    sline = sline + '</tr>\n'

    return sline

#------------------------------------------------------------------------
#-- update_plt_html_date: update html pages for plots; just replacing date
#------------------------------------------------------------------------

def update_plt_html_date():
    """
    update html pages for plots; just replacing date
    no input, but get the list from plot_dir
    """
    [lyear, lmon, lday] = mcf.today_date()
    date  =  mcf.add_leading_zero(lmon) + '/' 
    date  = date + mcf.add_leading_zero(lday) + '/' + str(lyear)

    cmd  = 'ls ' + plot_dir  + '/*html>./ztemp' 
    os.system(cmd)
    data = mcf.read_data_file('./ztemp', remove=1)

    for ent in data:
        hdat = mcf.read_data_file(ent)

        sline = ''
        for oline in hdat:
            m = re.search('Last Update', oline)
            if m is not None:
                sline = sline + 'Last Update: ' +  date + '\n'
            else:
                sline = sline + oline + '\n'

        with open(ent, 'w') as fo:
             fo.write(sline)

#------------------------------------------------------------------------

if __name__ == '__main__':

    acis_dose_make_data_html(indir = 'NA', outdir = 'NA')
