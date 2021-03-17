#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#   process_data_for_the_month.py: extract and process aca data for the given year/month    #
#                                                                                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 22, 2021                                                       #
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
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
ascdsenv['MTA_REPORT_DIR'] = '/data/mta/Script/ACA/Exc/Temp_comp_area/'
ascdsenv['PATH'] = '/bin:/usr/bin:/home/ascds/DS.release/bin:/usr/local/bin:/opt/local/bin:$PATH'
#
#--- reading directory list
#
path = '/data/mta/Script/ACA/Scripts/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
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

inst_list = ['ACIS-1', 'ACIS-2', 'ACIS-3', 'ACIS-4', 'ACIS-5', 'ACIS-6', \
             'HRC-I-1', 'HRC-I-2', 'HRC-I-3', 'HRC-I-4', \
             'HRC-S-1', 'HRC-S-2', 'HRC-S-3', 'HRC-S-4']


#-----------------------------------------------------------------------------------
#-- process_data_for_the_month: analysis ACA trending data for the given month    --
#-----------------------------------------------------------------------------------

def process_data_for_the_month(year, month):
    """
    analysis ACA trending data for the given month
    input:  year    --- year
            month   --- month
    output: <web_dir>/<MMM><yy>/acatrd.html
            <web_dir>/<MMM><yy>/Plots/*.png
    """
    if year == '':
        out = time.strftime('%Y:%m:%d', time.gmtime())
        atemp = re.split(':', out)
        year  = int(float(atemp[0]))
        month = int(float(atemp[1]))
        mday  = int(float(atemp[2]))
#
#--- if the date is in the firt 4 days of the month, update the last month
#
        if mday < 5:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
#
#--- extract fits data from archive
#
    extract_data(year, month)
#
#--- run mta pipe to create an html page in the older format and plots
#
    chk = run_flt_pipe(year, month)
#
#--- a crate the new html pages
#
    if chk:
        create_sub_hrma_page(year, month)
        read_mag_data_list()
        move_fits_files(year, month)
        return True
    else:
        print("Data Analysis Failed!!")
        failed_case_fill(year, month)
        move_fits_files(year, month)
        return False

#-----------------------------------------------------------------------------------
#-- move_fits_files:  move fits data files created by the pipe process to data directory
#-----------------------------------------------------------------------------------

def move_fits_files(year, month):
    """
    move fits data files created by the pipe process to data directory
    input:  year    --- year    
            month   --- month
    outout: <data_dir>/Fits_save/<MMM><yy>/*fits.gz
    """
    lyear = str(year)

    sdir = data_dir + 'Fits_data/' + mcf.change_month_format(month).upper() + lyear[2] + lyear[3] + '/'
    if  not os.path.isdir(sdir):
        cmd = 'mkdir -p ' + sdir
        os.system(cmd)

    cmd = 'mv -f ' + exc_dir + 'Temp_comp_area/*fits* ' + sdir
    os.system(cmd)
    cmd = 'gzip -f ' + sdir + '/*fits'
    os.system(cmd)        

#-----------------------------------------------------------------------------------
#--- extract_data: extract needed data for the given year/month                   --
#-----------------------------------------------------------------------------------

def extract_data(year, month):
    """
    extract needed data for the given year/month
    input:  year    --- year
            month   --- month
    output: <exc_dir>/<fits data>
    """
    if mcf.is_leapyear(year):
        mlist = dmon2
    else:
        mlist = dmon1

    yday1 = mlist[month-1] + 1
    year2 = year

    if month == 12:
        yday2 = 1
        year2 += 1
    else:
        yday2 = mlist[month] + 1

    cyday1 = mcf.add_leading_zero(yday1, 3)
    cyday2 = mcf.add_leading_zero(yday2, 3)

    tstart = str(year)  + ':' + cyday1 + ':00:00:00'
    tstop  = str(year2) + ':' + cyday2 + ':00:00:00'


    fits_dir = exc_dir + 'Fits_save/'
    if not os.path.isdir(fits_dir):
        cmd = 'mkdir '  + fits_dir
    else:
        cmd = 'rm -f '  + fits_dir + '/*fits*'
    os.system(cmd)

    out1 = run_arc5gl('retrieve', 'pcad', 'aca', '1', 'acacent',  tstart, tstop, fits_dir)
    out2 = run_arc5gl('retrieve', 'pcad', 'aca', '1', 'gsprops',  tstart, tstop, fits_dir)
    out3 = run_arc5gl('retrieve', 'pcad', 'aca', '1', 'fidprops', tstart, tstop, fits_dir)

#-----------------------------------------------------------------------------------
#-- run_arc5gl: extract data from archive using arc5gl                           ---
#-----------------------------------------------------------------------------------

def run_arc5gl(operation, detector, subdetector, level, filetype, tstart, tstop, fits_dir):
    """
    extract data from archive using arc5gl
    input:  operation   --- retrive/browse
            detector    --- detector
            subdetector --- sub detector name; defalut: '' (none)
            level       --- level
            filetype    --- filetype
            tstart      --- starting time
            tstop       --- stopping time
    ouptut: extracted fits file
            data        --- a list of fits file extracted
    """
    line = 'operation=' + str(operation) + '\n'
    line = line + 'dataset=flight\n'
    line = line + 'detector=' + str(detector) + '\n'
    if subdetector != "":
        line = line + 'subdetector=' + str(subdetector) + '\n'
    line = line + 'level='    + str(level) + '\n'
    line = line + 'filetype=' + str(filetype) + '\n'
    line = line + 'tstart='   + str(tstart)   + '\n'
    line = line + 'tstop='    + str(tstop)    + '\n'
    line = line + 'go\n'

    with open(zspace, 'w') as fo:
        fo.write(line)

    try:
        cmd = 'cd ' + fits_dir + '; /proj/sot/ska/bin/arc5gl    -user isobe -script ' 
        cmd = cmd   + zspace   + '> ./ztemp_out'
        os.system(cmd)
    except:
        cmd = 'cd ' + fits_dir + '; /proj/axaf/simul/bin/arc5gl -user isobe -script ' 
        cmd = cmd   ++ zspace  + '> ./ztemp_out'
        os.system(cmd)

    mcf.rm_file(zspace)
    
    lfile = exc_dir + './ztemp_out'
    data  = mcf.read_data_file(lfile, remove=1)

    data = data[2:]

    return data

#-------------------------------------------------------------------------------------------
#-- run_flt_pipe:  run mta pipe process                                                   --
#-------------------------------------------------------------------------------------------

def run_flt_pipe(year, month):
    """
    run mta pipe process
    iput:   year    --- year
            month   --- month
    output: <exc_dir>/Temp_comp_area/* --- acatrd.html and MGA_I_AVG*.png etc
    """

    datadir = exc_dir + '/Fits_save/'
    workdir = exc_dir + '/Temp_comp_area/'
#
#--- empty out workdir
#
    if len(os.listdir(workdir)) > 0:
        cmd     = 'rm -rf ' + workdir + '*'
        os.system(cmd)
#
#--- set root name
#
    lmon    = mcf.change_month_format(month).lower()
    lyear   = str(year)
    root    = lmon + lyear[2] + lyear[3]        #--- <mmm><yy>
#
#--- create input information files for flt_run_pipe
#
    cmd  = 'rm -rf ' + datadir + '*.lis'
    os.system(cmd)

    cmd  = 'ls ' + datadir + '/*acen* > '  + datadir + '/' + root + '_ACACENT.lis'
    os.system(cmd)
    cmd  = 'ls ' + datadir + '/*fidpr* > ' + datadir + '/' + root + '_FIDPROPS.lis'
    os.system(cmd)
    cmd  = 'ls ' + datadir + '/*gspr* > '  + datadir + '/' + root + '_GSPROPS.lis'
    os.system(cmd)
#
#--- run the pipe
#
    pipe_cmd1 = '/usr/bin/env PERL5LIB= '

    pipe_cmd2 = 'pset mta_trend_aca verbose=5; pset mta_trend_aca clean_outdir=0; flt_run_pipe -i ' + datadir + ' -o ' + workdir + ' -r ' + root 
    pipe_cmd2 = pipe_cmd2 + ' -t mta_trend_aca.ped 2>/dev/null'

    pipe_cmd  = pipe_cmd1 + pipe_cmd2

    try:
        bash(pipe_cmd, env=ascdsenv, logfile=open('log.txt', 'w'))
        return True
    except:
        return False


#-----------------------------------------------------------------------------------
#-- create_sub_hrma_page: read the old html file, create a html page and update data files 
#-----------------------------------------------------------------------------------

def create_sub_hrma_page(year, month, ifile= ''):
    """
    read the old html file, create a html page and update data files
    input:  year    --- year
            month   --- month
            ifile   --- input html file; if it is not given read from exc_dir
    output: <web_dir>/<MMM><yy>/acatrd.html
            <web_dir>/<MMM><yy>/Plots/*.png
    """

    if ifile == '':
        ifile       = exc_dir + '/Temp_comp_area/acatrd.html'
#
#--- create the data lists from the old formatted html page
#
    data, tsave = extract_date_from_old_html(ifile, year, month)
#
#--- create a new table
#
    htable  =  create_html_table(data)
    lyear   = str(year)
    lmon    = mcf.change_month_format(month)
#
#--- read the template 
#
    tfile = house_keeping + 'Template/sub_page'
    with open(tfile, 'r') as f:
        template = f.read()
#
#--- substitute the values
#
    template = template.replace('#YEAR#',   lyear)
    template = template.replace('#MON#',    lmon)
    template = template.replace('#TABLE#',  htable)
#
#--- check the output directory and if it does not exist, create
#
    odir = web_dir + lmon.upper() + lyear[2] + lyear[3] + '/'
    if not os.path.isdir(odir):
        cmd = 'mkdir -p ' + odir
        os.system(cmd)
#
#--- write the new html page
#
    ofile = odir + 'acatrd.html'

    with open(ofile, 'w') as fo:
        fo.write(template)
#
#--- create plot saving directory
#
    pdir = odir + 'Plots'
    cmd  = 'mkdir -p ' + pdir
    os.system(cmd)
#
#--- move all needed plot files
#
    cmd  = 'mv -f ' + exc_dir + '/Temp_comp_area/*png ' + pdir + '/.'
    os.system(cmd)


#-----------------------------------------------------------------------------------
#-- extract_date_from_old_html: read the old html file and extract the data needed -
#-----------------------------------------------------------------------------------

def extract_date_from_old_html(ifile, year, month):
    """
    read the old html file and extract the data needed
    input:  ifile   --- the html file in the old format (output from run_pipe)
            year    --- year
            month   --- month
    ouput:  save    --- a list of lists of data
                        columns are:
                            * percentage of good quality data
                            * percentage of marginal quality data
                            * percentage of bad quality data
                            * number of the data points
                            * average magnitude
                            * minimum magnitude
                            * maximum magnitude
            tsave   --- a list of start and stop time in seconds from 1998.1.1
    """
#
#--- read the original html page created by flt_run_pipe
#
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

#    for k in range(0, 14):
#        print(str(save[k]))

    create_data_table(save, year, month)

    return save, tsave

#-------------------------------------------------------------------------------------------
#-- create_data_table: create data table                                                  --
#-------------------------------------------------------------------------------------------

def create_data_table(save, year, month):
    """
    create data table
    input:  save    --- a list of lists of data
            tsave   --- a list of start and stop time in seconds from 1998.1.1
    output: <data_dir>/<inst>_<#>
    """
    out   = str(year) + ':' +  mcf.add_leading_zero(month) + ':15'
    out   = time.strftime('%Y:%j:00:00:00', time.strptime(out, '%Y:%m:%d'))
    stime = int(Chandra.Time.DateTime(out).secs)

    for k in range(0, len(inst_list)):
        inst = inst_list[k].lower()
        inst = inst.replace('-', '_')
        out  = data_dir + inst
     
        line = str(stime )+ '\t'
        line = line + str(year)  + ':'+ mcf.add_leading_zero(month)  + '\t'
        if  save[k][4] < 0:
            line = line + '-999\t'
        else:
            line = line + '%2.3f\t' % save[k][4]
        if  save[k][5] < 0:
            line = line + '-999\t'
        else:
            line = line + '%2.3f\t' % save[k][5]
        if  save[k][6] < 0:
            line = line + '-999\t'
        else:
            line = line + '%2.3f\t' % save[k][6]

        line = line + '%3d\t'   % save[k][0]
        line = line + '%3d\t'   % save[k][1]
        line = line + '%3d\t'   % save[k][2]
        line = line + '%3d\n'   % save[k][3]
     
        with open(out, 'a') as fo:
            fo.write(line)

        clean_up_file(out)


#-------------------------------------------------------------------------------------------
#-- create_html_table: create a html table from the given data                            --
#-------------------------------------------------------------------------------------------

def create_html_table(data):
    """
    create a html table from the given data
    input:  data    --- a list of lists of data
    output: line    --- a table in html format
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

        if data[k][4] < 0:
            line = line + '<td>-999</td>\n'
        else:
            line = line + '<td>' + '%2.3f' % data[k][4] + '</td>\n'

        if data[k][5] < 0:
            line = line + '<td>-999</td>\n'
        else:
            line = line + '<td>' + '%2.3f' % data[k][5] + '</td>\n'

        if data[k][6] < 0:
            line = line + '<td>-999</td>\n'
        else:
            line = line + '<td>' + '%2.3f' % data[k][6] + '</td>\n'

        line = line + '<td>' + '%3d'   % data[k][0] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][1] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][2] + '</td>\n'
        line = line + '<td>' + '%3d'   % data[k][3] + '</td>\n'
        line = line + '</tr>\n'

    line = line + '</table>\n'

    return line

#-----------------------------------------------------------------------------------
#-- failed_case_fill: for the case data analysis failed, fill the page with null data 
#-----------------------------------------------------------------------------------

def failed_case_fill(year, month):
    """
    for the case data analysis failed, fill the page with null data
    input:  year    --- year
            month   --- month
    output: <web_dir>/<MMM><yy>/acatrd.html         --- all zero data
            <web_dir>/<MMM><yy>/MAG_I_AVG*.png      --- blank plot
    """
#
#--- create null data set
#
    alist = [0, 0, 0, 0, -999, -999, -999]
    data  = []
    for k in range(0, len(inst_list)):
        data.append(alist)
#
#--- update data file with 0 data
#
    create_data_table(data, year, month)
#
#--- craete acatrd.html page with null data
#
    lmon   = mcf.change_month_format(month)
#
#--- create a new table
#
    htable =  create_html_table(data)
#
#--- read the template 
#
    tfile = house_keeping + 'Template/sub_page'
    with open(tfile, 'r') as f:
        template = f.read()
#
#--- substitute the values
#
    year     = str(year)
    fnotice  = year + ' --- <span style="color:red;">Data Analysis Failed</span>'
    template = template.replace('#YEAR#',   fnotice)
    template = template.replace('#MON#',    lmon)
    template = template.replace('#TABLE#',  htable)
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
#
#--- create plot saving directory
#
    pdir = odir + 'Plots'
    cmd  = 'mkdir -p ' + pdir
    os.system(cmd)
#
#--- copy no_plot.png to the plots dir for all MAG_I_AVG*.png
#
    for k in range(1, 15):
        cmd  = 'cp -f ' + house_keeping + 'no_data.png '  
        cmd  = cmd + pdir + '/MAG_I_AVG_' + str(k) + '.png' 
        os.system(cmd)
#
#--- move fits data
#
    fdir = odir + 'Data/'
    cmd  = 'mkdir -p ' + fdir
    os.system(cmd)

    cmd = 'mv -f /data/mta/Script/ACA/Exc/Fits_save/*.gz ' + fdir + '/.'
    os.system(cmd)

#-----------------------------------------------------------------------------------
#-- read_mag_data_list: read full magnitude data                                  --
#-----------------------------------------------------------------------------------

def read_mag_data_list():
    """
    read full magnitude data
    input:  <exc_dir>/Temp_comp_area//pcadf*1_mag_i_avg_mtatr.fits
    output: <data_dir>/mag_i_avg_<#>
    """
    cmd  =  'ls ' + exc_dir + 'Temp_comp_area/pcadf*1_mag_i_avg_mtatr.fits > ' + zspace
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)
    if len(data) > 0:
        fits = data[0].strip()
    else:
        return False

    fout  = pyfits.open(fits)
    fdata = fout[1].data
    fout.close()

    try:
        tarray = fdata['time']
    except:
        return False

    if len(tarray) == 0:
        return False

    for k in range(1, 15):

        col   = 'mag_i_avg_' + str(k)
        oname = data_dir + col
        out   = fdata[col]
        idx   = ~numpy.isnan(out)
        cdata = out[idx]
        tdata = tarray[idx]
#
#--- find out the last entry time
#
        xdata = mcf.read_data_file(oname)
        if len(xdata) > 0:
            atemp = re.split('\s+', xdata[-1])
            cut   = float(atemp[0])
        else:
            cut   = 0.0

        line  = ''
        for k in range(0, len(cdata)):
            tval = int(tdata[k])
            if tval > cut:
                line = line + str(tval) + '\t' + '%2.4f\n' % cdata[k]

        with open(oname, 'a') as fo:
            fo.write(line)
#
#--- clean up the data file
#
        clean_up_file(oname)

#-----------------------------------------------------------------------------------
#-- clean_up_file: sort, the data and remove duplicate                            --
#-----------------------------------------------------------------------------------

def clean_up_file(ifile, col=0):
    """
    sort, the data and remove duplicate. if duplcated, a newer data is used
    input:  ifile   --- input file name with full path
    col --- col # to be used for sorting
    output: ifile   --- cleaned up data file
    """
    t_list = []
    s_dict = {}
    data   = mcf.read_data_file(ifile)
    for ent in data:
        atemp = re.split('\s+', ent)
        tval  = float(atemp[col])
        t_list.append(tval)
        s_dict[tval] = ent
    
    tset   = set(t_list)
    t_list = sorted(list(tset))
    
    line   = ""
    for tval in t_list:
        line = line + s_dict[tval] + '\n'
    
    with open(ifile, 'w') as fo:
        fo.write(line)


#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 2:
        year  = int(float(sys.argv[1]))
        month = int(float(sys.argv[2]))
    else:
        year  = ''
        month = ''

    process_data_for_the_month(year, month)
