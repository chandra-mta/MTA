#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       create_monthly.py   create monthly report                                       #
#                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                       #
#           last update: Oct 07, 2022                                                   #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import math
import time
import Chandra.Time
import numpy
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release', shell='tcsh')

#path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'
#f    = open(path, 'r')
#data = [line.strip() for line in f.readlines()]
#f.close()
#
#for ent in data:
#    atemp = re.split(':', ent)
#    var  = atemp[1].strip()
#    line = atemp[0].strip()
#    exec "%s = %s" %(var, line)
#
#--- append path to a private folder
#
mta_dir = '/data/mta/Script/Python3.8/MTA/'
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf

#
#--- Recieve Admin email list from sys args
#
ADMIN = ['mtadude@cfa.harvard.edu']
for i in range(1,len(sys.argv)):
    if sys.argv[i][:6] == 'email=':
        ADMIN.append(sys.argv[i][6:])

#-----------------------------------------------------------------------------------
#-- create_monthly: create monthly report                                         --
#-----------------------------------------------------------------------------------

def create_monthly(year='', mon=''):
    """
    create monthly report
    input:  year    --- year; if it is "", the year of the last month will be used
            mon     --- month;if it is "", the month value of the last month is used
    output: monthly report in /data/mta4/www/REPORTS/MONTLHY/<yyyy><MMM>/
    """
#
#--- if year and month are not given, use the last month's month and year value
#
    if year == '':
#
#--- find today's date
#
        out   = time.strftime("%Y:%m:%d", time.gmtime())
        ltime = re.split(':', out)
        year  = int(float(ltime[0]))
        lyear = str(year)                           #--- '2016'
#
#--- set the last month's month and year
#
        mon   = int(float(ltime[1])) -1 

        if mon < 1:
            mon   = 12
            year -= 1
            lyear = str(year)                           #--- '2016'

    cmon   = str(mon)
    if mon < 10:
        cmon = '0' + cmon                           #--- e.g. 03 or 11

    lmon   = mcf.change_month_format(mon)           #--- e.g. Mar or Nov

    lmonyr = lmon.lower() + lyear[2] + lyear[3]     #--- e.g. jan16
    lm_y   = cmon + '_' + lyear                     #--- e.g. 03_2016
#
#--- set output directory
#
    odir  = '/data/mta4/www/REPORTS/MONTHLY/' + str(year) + lmon.upper()

    cmd = 'mkdir ' + odir
    os.system(cmd)

    odir  =  odir + '/'
#
#--- set month interval depending on leap year or not
#
    if mcf.is_leapyear(year):
        sdate = ['001', '032', '060', '091', '121', '152', '182', '213', '244', '274', '305', '335']
        edate = ['032', '060', '091', '121', '152', '182', '213', '244', '274', '305', '335', '001']
    else:
        sdate = ['001', '032', '061', '092', '122', '153', '183', '214', '245', '275', '306', '336']
        edate = ['032', '061', '092', '122', '153', '183', '214', '245', '275', '306', '336', '001']
#
#--- set start and stop time of the month in <yyyy>:<ddd>:00:00:00 format
#
    tstart = str(year) + ':' + sdate[mon-1] + ':00:00:00' 

    eyear  = year
    if mon == 12:
        eyear = year + 1
    tstop  = str(eyear) + ':' + edate[mon-1] + ':00:00:00' 
#
#--- create CTI plots
#
    os.system("cd /data/mta/Script/Month/CTI/;    monthly_report_cti_avg_plots_two_section.py")
#
#--- create Focal Plane temperature plots
#
    os.system("cd /data/mta/Script/Month/FOCAL/;  run_all_focal_scripts")
#
#--- create ACIS SIB plots
#
    os.system("cd /data/mta/Script/Month/SIB/;    sib_monthly_report_plot.py")
#
#--- create SIM movement plots
#
    os.system("cd /data/mta/Script/Month/SIM/;    create_monthly_sim_plots")
#
#--- copy the created plots to the report directory
#
    cmd = "cp /data/mta/Script/Month/CTI/Plots/*png "       + odir 
    os.system(cmd)
    cmd = "cp -rf /data/mta/Script/Month/CTI/Data "         + odir 
    os.system(cmd)
    cmd = "cp /data/mta/Script/Month/FOCAL/*png "           + odir 
    os.system(cmd)
    cmd = "cp /data/mta/Script/Month/FOCAL/Plots/*png "     + odir 
    os.system(cmd)
    cmd = "cp /data/mta_www/mta_bad_pixel/Plots/hist_ccd_plot_front_side.png " + odir 
    os.system(cmd)
    cmd = "cp /data/mta_www/mta_bad_pixel/Plots/hist_plot_ccd5.png " + odir 
    os.system(cmd)
    cmd = "cp /data/mta/Script/Month/SIB/*png "                      + odir 
    os.system(cmd)
    cmd = "cp /data/mta/www/mta_max_exp/Images/hrc_max_exp.gif "     + odir 
    os.system(cmd)
    cmd = "cp /data/mta_www/mta_grat/Focus/Plots/acis_hetg_streak_lrf_focus.png " + odir 
    os.system(cmd)
    cmd = "cp /data/mta_www/mta_grat/Focus/Plots/acis_hetg_ax_lrf_focus.png "     + odir 
    os.system(cmd)
    cmd = "cp /data/mta/Script/Month/SIM/*.png "                     + odir 
    os.system(cmd)
    cmd = "cp /data/mta4/www/RADIATION_new/ACIS_Rad/Plots/rad_cnts_" + lmonyr + ".png "    + odir 
    os.system(cmd)
    cmd = "cp /data/mta4/www/DAILY/mta_pcad/IRU/Plots_new/" + lyear + '/' +  lmonyr + "_bias.png " + odir 
    os.system(cmd)
    cmd = "cp /data/mta/www/mta_max_exp/Images/hrc_max_exp.gif "           + odir 
    os.system(cmd)
    cmd = 'cp /data/mta4/www/RADIATION_new/ACIS_Rad/Plots/rad_use_' + lmonyr + '.png ' + odir
    os.system(cmd)
#
#--- move the plots to past plot saving directories
#
    os.system("mv -f /data/mta/Script/Month/FOCAL/Plots/*gif /data/mta/Script/Month/FOCAL/Plots/Past/.")
    os.system("mv -f /data/mta/Script/Month/SIB/*png /data/mta/Script/Month/SIB/Plots/.")
#
#--- sun spot cycle download
#
    cmd = 'wget -q -O'+ odir + '/solar-cycle-sunspot-number.gif  http://services.swpc.noaa.gov/images/solar-cycle-sunspot-number.gif'
    os.system(cmd)
#
#--- now copy  month depend plot files and set the template file for the month
#
    if mon == 1 or mon == 7:
        cmd = "cp /data/mta_www/mta_sib/Plots/Plot_long_term/full_plot_ccd3.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sib/Plots/Plot_long_term/full_plot_ccd5.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sib/Plots/Plot_long_term/full_plot_ccd7.png " + odir
        os.system(cmd)

        cmd = "cp /data/mta_www/mta_acis_sci_run/Corner_pix/Plots/I3_all_norm_cent.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_acis_sci_run/Corner_pix/Plots/S3_all_norm_cent.png " + odir
        os.system(cmd)

        cmd = "cp /data/mta_www/mta_bias_bkg/Plots/Overclock/ccd2.png " + odir + 'ccd2_oc.png'
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_bias_bkg/Plots/Sub/ccd2.png       " + odir + 'ccd2_sub.png'
        os.system(cmd)

        cmd = "cp /data/mta4/www/DAILY/mta_pcad/ACA/Plots/acis_1_full.png   " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_pcad/ACA/Plots/acis_6_full.png   " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_pcad/ACA/Plots/hrc_i_1_full.png  " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_pcad/ACA/Plots/hrc_s_1_full.png  " + odir
        os.system(cmd)

        ifile = '/data/mta/Script/Month/Scripts/Templates/MONTHLY1.html'             #--- template file name

    elif mon == 2 or mon == 8:
        cmd = "cp /data/mta4/www/DAILY/mta_src/ACIS-I_d_tyear10_psf.gif " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_xy.gif           " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_d_rnd.gif        " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_t_rnd.gif        " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_d_ravg.gif       " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_t_ravg.gif       " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_d_snr.gif        " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_t_snr.gif        " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_rot.gif          " + odir
        os.system(cmd)
        cmd = "cp /data/mta4/www/DAILY/mta_src/tot_all_t_rot.gif        " + odir
        os.system(cmd)

        cmd = "cp /data/mta_www/mta_aiming/Fig_save/acis_point_err.gif  " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_aiming/Fig_save/hrc_i_point_err.gif " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_aiming/Fig_save/hrc_s_point_err.gif " + odir
        os.system(cmd)

        cmd = "cp -r /data/mta4/www/DAILY/mta_src/Plots " + odir + 'HRMA_Plots'
        os.system(cmd)

        ifile = '/data/mta/Script/Month/Scripts/Templates/MONTHLY2.html'

    elif mon == 3 or mon == 9:
        cmd = "cp /data/mta_www/mta_acis_sci_run/Events_rej/Plots/ccd3_cti.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_acis_sci_run/Events_rej/Plots/ccd3_sci.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_acis_sci_run/Events_rej/Plots/ccd7_cti.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_acis_sci_run/Events_rej/Plots/ccd7_sci.png " + odir
        os.system(cmd)

        cmd = "cp /data/mta/www/mta_acis_gain/Plots/gain_plot_ccd3.png   " + odir
        os.system(cmd)
        cmd = "cp /data/mta/www/mta_acis_gain/Plots/offset_plot_ccd3.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta/www/mta_acis_gain/Plots/gain_plot_ccd5.png   " + odir
        os.system(cmd)
        cmd = "cp /data/mta/www/mta_acis_gain/Plots/offset_plot_ccd5.png " + odir
        os.system(cmd)

        ifile = '/data/mta/Script/Month/Scripts/Templates/MONTHLY3.html'

    elif mon == 4 or mon == 10:
        #cmd = "cp /data/mta_www/mta_grat/EdE/heg_all.gif  " + odir
        #os.system(cmd)
        #cmd = "cp /data/mta_www/mta_grat/EdE/meg_all.gif  " + odir
        #os.system(cmd)
        #cmd = "cp /data/mta_www/mta_grat/EdE/leg_all.gif  " + odir
        #os.system(cmd)
#
#--- this part should be rewritten after year 2019
#
        cmd = "cp /data/mta_www/mta_grat/EdE/Plots/*_2019.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sim_twist/Plots/twist_plot.png " + odir
        os.system(cmd)

        ifile = '/data/mta/Script/Month/Scripts/Templates/MONTHLY4.html'

    elif mon == 5 or mon == 11:
        cmd = "cp /data/mta_www/mta_sib/Plots/Plot_long_term/full_plot_ccd3.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sib/Plots/Plot_long_term/full_plot_ccd5.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sib/Plots/Plot_long_term/full_plot_ccd7.png " + odir
        os.system(cmd)

        cmd = "cp /data/mta_www/mta_acis_hist/Html_pages/acis_hist_cccd3_high_pos.html   " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_acis_hist/Html_pages/acis_hist_cccd3_high_width.html " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_acis_hist/Html_pages/acis_hist_cccd3_high_cnt.html   " + odir
        os.system(cmd)

        ifile = '/data/mta/Script/Month/Scripts/Templates/MONTHLY5.html'

    elif mon == 6 or mon == 12:
        cmd = "cp /data/mta_www/mta_sim_twist/Plots/I-1.png   " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sim_twist/Plots/S-2.png   " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sim_twist/Plots/H-I-2.png " + odir
        os.system(cmd)
        cmd = "cp /data/mta_www/mta_sim_twist/Plots/H-S-2.png " + odir
        os.system(cmd)

        ifile = '/data/mta/Script/Month/Scripts/Templates/MONTHLY6.html'
#
#--- create clean acis and hrc exposure maps using ds9
#
    #run_exposure_maps(lyear, cmon)

    send_email_to_admin()

#--------------------------------------------------
#--- read the template and substitute the contents 
#--------------------------------------------------

    with  open(ifile, 'r') as fx:
        text = fx.read()
#
#--- substitute values
#
    fmonth_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    fmon = fmonth_list[mon-1]             
    text = text.replace('#Month#', fmon)        #--- full month name e.g. May
    text = text.replace('#YEAR#',  lyear)       #--- full year nane  e.g. 2016

    text = text.replace('#SMON#', lmon)         #--- short month, e.g. Jan
    text = text.replace('#LSMON#', lmon.lower())#--- short lower month, e.g. jan
    text = text.replace('#USMON#', lmon.upper())#--- short upper month, e.g. JAN 

    line = 'rad_use_' + lmonyr + '.png'
    text = text.replace('#RADUSE#', line)       #--- e.g., rad_use_oct16.png

    line = cmon + '_' + lyear
    text = text.replace('#LMONYR#', line)       #--- mon_year e.g. 07_2016

    line = lmonyr.upper()
    text = text.replace('#UMONYR#', line)       #--- e.g., OCT16
#
#--- acis exposure tables
#
    os.system("cd /data/mta/Script/Exposure/Exc/; /data/mta/Script/Exposure/Scripts/ACIS_Scripts/acis_dose_monthly_report.py")

    line = '/data/mta/Script/Exposure/Exc/monthly_diff_' +  cmon + '_' + lyear
    with  open(line, 'r') as f:
        dout = f.read()
    
    text = text.replace('#ACISMON#', dout)       #--- acis monthly dose

    line = '/data/mta/Script/Exposure/Exc/monthly_acc_' +  cmon + '_' + lyear
    with open(line, 'r') as f:
        dout = f.read()
    
    text = text.replace('#ACISCMON#', dout)     #--- acis cumulative dose
#
#--- last 12 months exposure maps
#
    byear = year -1
    text  = past_data_entry(1, 0, mon, byear, text)
    text  = past_data_entry(2, 3, mon, byear, text)
    text  = past_data_entry(3, 6, mon, byear, text)
    text  = past_data_entry(4, 9, mon, byear, text)
#
#---- acis focal
#
    data  = mcf.read_data_file('/data/mta/Script/Month/FOCAL/Plots/month_avg')

    atemp = re.split(':', data[0])
    btemp = re.split('\+\/\-', atemp[1])
    ft    = round(float(btemp[0]), 2)
    ferr  = round(float(btemp[1]), 2)

    text  = text.replace('#FT#',   str(ft))
    text  = text.replace('#FERR#', str(ferr))

    atemp = re.split(':', data[1])
    btemp = re.split('\+\/\-', atemp[1])
    fw    = round(float(btemp[0]), 2)
    werr  = round(float(btemp[1]), 2)

    text  = text.replace('#FW#',   str(fw))
    text  = text.replace('#WERR#', str(werr))

    line = 'erad_' + lmonyr + '.gif'                #--- erand_nov16.gif
    text = text.replace('#ERAND#', line)
#
#--- acis sib
#
    yearmon = str(year) +'_' + cmon
    text = text.replace('#YEARMON#', yearmon)       #--- e.g. 2015_03
#
#--- hrc i monthly dose
#
    line = hrc_monthly_report('HRCI', cmon, lmon,  lyear)    
    text = text.replace('#HRCIDOSE#', line)        #--- HRC I DIFF 
#
#--- hrc cumulative
#
    line = hrc_cumulative_report('HRCI', cmon, lmon,  lyear)
    text = text.replace('#CHRCIDOSE#', line)       #--- HRC I Cumulative
#
#--- hrc s monthly dose
#
    line = hrc_monthly_report('HRCS', cmon, lmon,  lyear)    
    text = text.replace('#HRCSDOSE#', line)        #--- HRC S DIFF 
#
#--- hrc cumulative
#
    line = hrc_cumulative_report('HRCS', cmon, lmon,  lyear)
    text = text.replace('#CHRCSDOSE#', line)       #--- HRC S Cumulative
#
#--- IRU
#
    text = text.replace("#SMONYR#", lmonyr)        #--- e.g., nov16
#
#--- envelope trending
#
    line = get_envelope_trending(mon, odir)
    text = text.replace("#ENVTREND#", line)
#
#--- critical trends which are reported on Mar, Jun, Sep, and Dec
#
    if mon in [3, 6, 9, 12]:
        text = run_critical_trend(text)
#
#--- Monthly Trend Reports
#
    text = run_month_trend(mon, text)
#
#--- last index
#
    line = create_index(year, mon)
    text = text.replace('#YINDEX#', line)
#
#--- finally print out the report
#
    ofile = odir + "MONTHLY.html"
    with open(ofile, 'w') as fo:
        fo.write(text)
#
#--- chnage permission and owners
#
    cmd = 'chmod 755 ' + odir + '/*'
    os.system(cmd)

    cmd = 'chgrp -R mtagroup ' + odir + '/*'
    os.system(cmd)

#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------
    
def past_data_entry(setno, mpos, mon, byear, text):
    """
    update the text for the given past month date
    input:  setno   --- indicator of which entry
            mpos    --- which step from the oldest month to indicate
                        the month
            byear   --- the last year
            text    --- the text which will be updated
    output: text    --- the text updated
    """
    chk   = 0
    test  = mon + mpos
    if test > 12:
        test -= 12
        if chk == 0:
            byear += 1

    ctest = str(test)
    if test < 10:
        ctest = '0' + ctest

    line  = ctest + '_' + str(byear)

    mset  = '#MSET'  + str(setno) + '#'
    yset  = '#YSET'  + str(setno) + '#'
    myset = '#MYSET' + str(setno) + '#'

    text  = text.replace(mset,  mcf.change_month_format(test))
    text  = text.replace(yset,  str(byear))
    text  = text.replace(myset, line)

    return text

#-----------------------------------------------------------------
#-- hrc_monthly_report: create hrc month long exposure data input 
#-----------------------------------------------------------------

def hrc_monthly_report(hrc, cmon, lmon, lyear):
    """
    create hrc month long exposure data input
    input:  hrc     --- hrc indicator either HRCI or HRCS
            cmon    --- str(<month>)
            lmon    --- month in word (e.g. Jan)
            lyear   --- str(<year>)
    output: line    --- created text to be substitute
    """

#
#--- hrc s monthly dose
#
    line = '/data/mta/www/mta_max_exp/Data/' + hrc.lower() + '_dff_out'
    data = mcf.read_data_file(line)
    
    test = data[-1]
    mc   = re.search('NA', test)
#
#--- for the case, there is no HRC observations
#
    if mc is not None:
        line = "<li>" + lmon + " " + hrc.upper() + " dose fits image - no observations</li><br />\n"
        line = line + "<pre style='padding-left:30px; padding-bottom:30px'> \n"
        line = line + "No Data   \n </pre>\n"
#
#--- for the case, there are HRC S observations
#
    else:
        monyear = cmon + '_' + lyear
        line = "<li><a href='/mta_days/mta_max_exp/Month_hrc/" + hrc.upper() +"_" + monyear + ".fits.gz'> \n"
        line = line + "<strong>" + lmon + " " + hrc.upper() + " Dose</strong> in fits   \n"
        line = line + "</a></li>\n\n"

        line = line + "<div style='float:left; width:15%'> \n"
        line = line +"<table border=0 style='padding-right:1px;padding-left:1px;background-color:white'><tr><th>\n"
        line = line + "<a href =\"javascript:WindowOpener2('/mta_days/mta_max_exp/Images/" + hrc.upper() +"_" + monyear + ".png')\">\n"
        line = line + "<img src='https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/" + hrc.upper() +"_" + monyear + ".png'  width='70' height='70' />\n"
        line = line + "</th></tr></table>\n"
        line = line + "</a> </div>\n"

        line = line + "<pre style='padding-left:30px; padding-bottom:30px'>\n"
        line = line + "IMAGE                NPIX      MEAN    STDDEV      MIN       MAX\n"
        atemp = re.split('\s+', test)
        a1   = '%.3f ' % round(float(atemp[2]), 3)
        a2   = '%.3f ' % round(float(atemp[3]), 3)
        a3   = '%.3f ' % round(float(atemp[4]), 3)
        a4   = '%.3f ' % round(float(atemp[6]), 3)
        line = line + hrc.upper() + "_" + monyear + ".fits  16777216\t"+ a1 +'\t'+ a2 + '\t' + a3 + '\t' + a4 + "\n"
        line = line + "</pre>\n"

    return line    

#-----------------------------------------------------------------
#-- hrc_cumulative_report: create hrc cumulative exposure data input 
#-----------------------------------------------------------------

def hrc_cumulative_report(hrc, cmon, lmon, lyear):
    """
    create hrc cumulative exposure data input
    input:  hrc     --- hrc indicator either HRCI or HRCS
            cmon    --- str(<month>)
            lmon    --- month in word (e.g. Jan)
            lyear   --- str(<year>)
    output: line    --- created text to be substitute
    """

    monyear = cmon + '_' + lyear

    line = '/data/mta/www/mta_max_exp/Data/'+ hrc.lower() + '_acc_out'
    data = mcf.read_data_file(line)
    
    test = data[-1]
    atemp = re.split('\s+', test)

    line = "<li><a href=\"/mta_days/mta_max_exp/Cumulative_hrc/" + hrc.upper() + "_08_1999_"+monyear + ".fits.gz\"> \n"
    line = line + "<strong>AUG 1999 - " + lmon + ' ' + lyear + " " +  hrc.upper() +"  Dose</strong> in fits</a></li> \n"

    line = line + "<div style='float:left; width:15%'>\n"
    line = line + "<a href =\"javascript:WindowOpener2('/mta_days/mta_max_exp/Images/"+ hrc.upper() + "_08_1999_" + monyear + ".png')\">\n"
    line = line + "<img src='https://cxc.cfa.harvard.edu/mta_days/mta_max_exp/Images/" + hrc.upper() + "_08_1999_" + monyear + ".png'  width='70' height='70' />\n"
    line = line + "</a> </div>\n"
    line = line + "<pre style='padding-left:30px; padding-bottom:30px'>\n"
    line = line + "IMAGE                       NPIX      MEAN    STDDEV      MIN       MAX\n"
    try:
        a1   = '%.3f ' % round(float(atemp[2]), 3)
    except:
        a1   = 'na'
    try:
        a2   = '%.3f ' % round(float(atemp[3]), 3)
    except:
        a2   = 'na'
    try:
        a3   = '%.3f ' % round(float(atemp[4]), 3)
    except:
        a3   = 'na'
    try:
        a4   = '%.3f ' % round(float(atemp[6]), 3)
    except:
        a4   = 'na'

    line = line  + hrc.upper() + "_08_1999_" + monyear + ".fits  16777216\t"+ a1 +'\t'+ a2 + '\t' + a3 + '\t' + a4 + "\n"
    line = line + "</pre> \n"

    return line

#-----------------------------------------------------------------
#-- run_critical_trend: create critical trend input             --
#-----------------------------------------------------------------

def run_critical_trend(text):
    """
    create critical trend input
    input   text    --- text
    output  text    --- updated text
    """
#
#--- critical trends which are reported on Mar, Jun, Sep, and Dec
#
    #namlist = ['1PDEAAT', '1PIN1AT']
    namlist = ['1PDEAAT',]
    line    = trend_data_extract('acistemp', namlist, part='max')
    text = text.replace("#CRITACIS#", line)

    namlist = ['OBAAVG']
    line    = trend_data_extract('compgradkodak', namlist, part='max')
    text = text.replace("#CRITOBA#", line)

    namlist = ['TEIO', 'TEPHIN']
    line    = trend_data_extract('ephtv', namlist, part='max')
    text = text.replace("#CRITEPHIN#", line)

    namlist = ['TCYLFMZM', 'TCYLFMZP']
    line    = trend_data_extract('sc_main_temp', namlist, part='max')
    text = text.replace("#CRITSCM#", line)

    namlist = ['TFSSBKT1', 'TFSSBKT2', 'TSCTSF1', 'TSCTSF6']
    line    = trend_data_extract('sc_anc_temp', namlist, part='max')
    text = text.replace("#CRITTSC#", line)

    namlist = ['PM1THV1T', 'PM2THV1T', 'PM1THV2T', 'PM2THV2T', 'PLINE02T', 'PLINE03T', 'PLINE04T']
    line    = trend_data_extract('mups', namlist, part='max')
    text = text.replace("#CRITMUPS#", line)

    return text

#-----------------------------------------------------------------
#-- run_month_trend: create trending input and update the text   -
#-----------------------------------------------------------------

def run_month_trend(mon, text):
    """
    create trending input and update the text
    input:  mon     --- month
            text    --- text
    output: text    --- updated text
    """
#
#--- Monthly Trend Reports
#
    if mon == 1 or mon == 7:

        namlist = ['1CBAT', '1CRAT', '1CRBT', '1DACTBT', '1DEAMZT', '1DPAMYT', '1DPAMZT', '1OAHAT', '1OAHBT', '1PDEAAT', '1PDEABT', '1WRAT', '1WRBT']
        line    = trend_data_extract('acistemp', namlist)
        text = text.replace("#TREND_ACISTEMP#", line)

        namlist = ['1DAHBCU', '1DAHBVO', '1DAHHBVO', '1DE28BVO', '1DEICBCU', '1DEN0BVO', '1DEN1BVO', '1DEP0BVO', '1DEP1BVO', '1DEP2BVO', '1DEP3BVO', '1DP28BVO', '1DPICBCU', '1DPP0BVO']
        line    = trend_data_extract('aciselecb', namlist)
        text = text.replace("#TREND_ACISELEC#", line)

        #namlist = ['5EIOT', '5EPHINT', 'HKEBOXTEMP', 'HKN6I', 'HKN6V', 'HKP27I', 'HKP27V', 'HKP5I', 'HKP5V', 'HKP6I', 'HKP6V', 'TEIO', 'TEPHIN']
        namlist = ['5EIOT', '5EPHINT', 'HKEBOXTEMP', 'TEIO', 'TEPHIN']
        line    = trend_data_extract('ephtv', namlist)
        text = text.replace("#TREND_EPHTV#", line)

    elif mon == 2 or mon == 8:

        namlist = ['2CEAHVPT', '2CHTRPZT', '2CONDMXT', '2DCENTRT', '2DTSTATT', '2FHTRMZT', '2FRADPYT', '2PMT1T', '2PMT2T', '2UVLSPXT']
        line    = trend_data_extract('hrctemp', namlist)
        text = text.replace("#TREND_HRCTEMP#", line)

        #namlist = ['FE00ATM', 'FEPRATM', 'IMHVATM', 'IMINATM', 'LVPLATM', 'PRBSCR', 'PRBSVL', 'SMTRATM', 'SPHVATM', 'SPINATM']
        namlist = ['2FE00ATM', '2FEPRATM', '2IMHVATM', '2IMINATM', '2LVPLATM', '2PRBSCR', '2PRBSVL', '2SMTRATM', '2SPHVATM', '2SPINATM']
        line    = trend_data_extract('hrchk', namlist)
        text = text.replace("#TREND_HRCHK#", line)

        namlist = ['AACCCDPT', 'AACCCDRT', 'AACH1T', 'AACH2T']
        line    = trend_data_extract('pcadtemp', namlist)
        text = text.replace("#TREND_PCADTEMP#", line)

    elif mon == 3 or mon == 9:

        namlist = ['OHRTHR27', 'OHRTHR42', 'OHRTHR43', 'OOBAGRD3', 'OOBAGRD6']
        line    = trend_data_extract('pcadftsgrad', namlist)
        text = text.replace("#TREND_PCAD#", line)

        namlist = ['3BTU_BPT', '3TSMXCET', '3TSMXSPT', 'BOXTEMP', 'FAMTRTEMP', 'FLEXATEMP', 'PSUTEMP', 'TSCMTRTEMP']
        line    = trend_data_extract('simtemp', namlist)
        text = text.replace("#TREND_SIMTEMP#", line)

        namlist = ['AGRNDADC', 'FATABADC','N15VADC', 'P15VADC','P5VADC','TSCTABADC']
        line    = trend_data_extract('simelec', namlist)
        text = text.replace("#TREND_SIMELEC#", line)

    elif mon == 4 or mon == 10:

        namlist = ['EB2CI', 'EB2DI', 'EB2V', 'ECNV1V', 'ECNV2V', 'ECNV3V']
        line    = trend_data_extract('epsbatt', namlist)
        text = text.replace("#TREND_EPSBATT#", line)

        namlist = ['ELBI', 'ELBV', 'OHRMAPWR', 'OOBAPWR']
        line    = trend_data_extract('spcelec', namlist)
        text = text.replace("#TREND_SPCELEC#", line)

        namlist = ['OOBTHR04', 'OOBTHR12', 'OOBTHR26', 'OOBTHR38', 'OOBTHR44', 'OOBTHR50']
        line    = trend_data_extract('obaheaters', namlist)
        text = text.replace("#TREND_OBAHEAT#", line)

    elif mon == 5 or mon == 11:

        namlist = ['OHRTHR03', 'OHRTHR09', 'OHRTHR17', 'OHRTHR24', 'OHRTHR38', 'OHRTHR52']
        line    = trend_data_extract('hrmaheaters', namlist)
        text = text.replace("#TREND_HRMAHEAT#", line)

        namlist = ['4RT568T', '4RT569T','4RT570T', '4RT575T', '4RT576T', '4RT578T']
        line    = trend_data_extract('hrmatherm', namlist)
        text = text.replace("#TREND_HRMATHERM#", line)

        namlist = ['PM1THV1T', 'PLINE02T', 'PLINE03T', 'PLINE04T']
        line    = trend_data_extract('mups', namlist)
        text = text.replace("#TREND_MUPS#", line)

    elif mon == 6 or mon == 12:

        namlist = ['4RT584T', '4RT585T', '4RT586T', '4RT587T', '4RT597T', '4RT598T']
        line    = trend_data_extract('hrmastruts', namlist)
        text = text.replace("#TREND_HRMAST#", line)

        namlist = ['4RT705T', '4RT706T', '4RT707T', '4RT708T', '4RT709T', '4RT710T']
        line    = trend_data_extract('obfwdbulkhead', namlist)
        text = text.replace("#TREND_OBFWRD#", line)

        namlist = ['4RT568T', '4RT569T', '4RT570T', '4RT575T', '4RT576T', '4RT578T']
        line    = trend_data_extract('hrmatherm', namlist)
        text = text.replace("#TREND_HRMATHERM#", line)

    return text        

#-----------------------------------------------------------------
#-- create_index: create index for the past report              --
#-----------------------------------------------------------------

def create_index(year, mon):
    """
    create index for the past report
    input:  year    --- year
            mon     --- month
    output: line    --- a text to be substituted
    """

    line = ''
    for xyear in range(year, 1999, -1):
        line = line + '<tr>\n<td>' + str(xyear) + '</td>'
        for xmonth in range(1, 13):
            if (xyear == year) and (xmonth >= mon):
                line = line + '<td>&#160</td>\n'
            else:
                stmon  = mcf.change_month_format(xmonth)
                ltmon  = stmon.upper()
                tyear  = str(xyear)
                line = line + '<td><a href="/mta/REPORTS/MONTHLY/' 
                line = line + tyear + ltmon + '/MONTHLY.html">' + stmon + '</a></td>\n'
        line = line + '</tr>\n\n'

    return line 

#-----------------------------------------------------------------
#-- trend_data_extract: find trend entries for given msids    --
#-----------------------------------------------------------------

def trend_data_extract(group, msid_list, part=''):
    """
    find trend entries for given msids
    input:  group       --- a html file name without .html part
            msid_list   --- a list of name of msids
            part        --- if 'max', extract full range max trend
    output: hline       --- a text line containing all masids information
    """

    group = group.lower()
    cgroup = group.capitalize()

    line = '/data/mta4/www/MSID_Trends/' + cgroup + '/' + group  + '_mid_static_short_main.html'
    data = mcf.read_data_file(line)

    #ifile = '/data/mta4/www/MSID_Trends/' + cgroup + '/' + group + '_mid_static_short_main.html'
    #hgrp  = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + cgroup + '/' + group + '_mid_static_short_main.html'

    hline = ''
    for msid in msid_list:
        msid = msid.lower()
        for m in range(0, len(data)):
            ent = data[m]
            mc = re.search(msid, ent)
            if mc is None:
                continue

            html  = 'https://cxc.cfa.harvard.edu/mta/MSID_Trends/' + cgroup + '/'
            if part == 'max':
                html  = html + msid.capitalize()  + '/' + msid + '_max_static_long_plot.html'
            else:
                html  = html + msid.capitalize()  + '/' + msid + '_mid_static_short_plot.html'

            hline = hline + '<tr><th><a href="javascript:WindowOpener3(\''+  html 
#
#--- check multi row entries
#
            mc = re.search('rowspan', ent)
            if mc is not None:
                ctemp = re.split('>', ent)
                dtemp = re.split('rowspan=', ctemp[0])
                rowno = int(float(dtemp[1]))
                hline = hline +  html + '\')" rowspan=' + str(rowno) + '>' + msid + '</th>'
                for n in range(0, rowno):
                    line  = data[m+2*n]
#
#--- first line has a bit more info than the following lines
#
                    if n == 0:
                        atemp = re.split('</th>', line)
                        btemp = re.split('<th ',  atemp[1])
                        hline = hline + btemp[0] + '</tr>\n'
#
#--- other lines
#
                    else:
                        atemp = re.split('<th ', line)
                        hline = hline + '<td>&#160;</td>' +  atemp[0] + '</tr>\n'
#
#--- single row entry case
#
            else:

                hline = hline + '\')">' + msid + '</th>'
                atemp = re.split('</th>', ent)
                btemp = re.split('"',  atemp[0])
                btemp = re.split('<th', atemp[2])
                hline = hline + '<td>&#160;</td>' +  btemp[0] + '</tr>\n'

            break

    return hline

#-----------------------------------------------------------------------------------
#-- get_envelope_trending: get envelope trending which predicting a near future violation 
#-----------------------------------------------------------------------------------

def get_envelope_trending(mon, odir):
    """
    get envelope trending which predicting a near future violation
    input: read from /data/mta_www/mta_envelope_trending/envelope_main.html
           mon  --- month value
    output: selected envelope trending plot html files; they are also modified
    """

    data = mcf.read_data_file('/data/mta_www/mta_envelope_trending/envelope_main.html')
#
#--- extract name and html address of possible near future violation cases
#
    html_list = []
    name_list = []
    chk  = 0
    for ent in data:
        mc = re.search('Predicted Near Future Violations', ent)
        if mc is not None:
            chk = 1
        
        if chk == 0:
            continue
        mc = re.search('Yellow Violations', ent)
        if mc is not None:
            break

        mc = re.search('https://cxc.cfa.harvard.edu/mta_days/mta_envelope_trending/', ent)
        if mc is not None:
            atemp = re.split('Htmls\/', ent)
            btemp = re.split('\"', atemp[1])
            html_list.append(btemp[0])
            atemp = re.split('html\">', ent)
            btemp = re.split('<', atemp[1])
            name_list.append(btemp[0])

    if mon > 6:
        mon -= 6
#
#--- choose about 1/6 of the near future violation files for display for this monthly report
#
    cnt = len(name_list)
    val = int(cnt / 6)

    start = val * (mon -1)
    stop  = val * mon + 1
    selected_name = name_list[start:stop]
    selected_html = html_list[start:stop]
#
#---  copy the file we need
#
    oline = ''
    for i in range(0, len(selected_name)):
        oline = oline + '<li><a href="./' + selected_html[i] + '" target="blank">' + selected_name[i] + '</a></li>'
        cmd  = 'cp /data/mta/www/mta_envelope_trending/Htmls/' + selected_html[i] + ' ' + odir 
        os.system(cmd)
#
#--- remove the part we don't need for the monthly report
#
        ifile = odir + selected_html[i]
        data  = mcf.read_data_file(ifile)

        with open(ifile, 'w') as fo:
            for ent in data:
                mc = re.search('<\/script><ul><li', ent)
                if mc is not None:
                    fo.write('</script>\n')
                    break
                fo.write(ent)
                fo.write('\n')


    return oline

#-----------------------------------------------------------------------------------
#-- run_exposure_maps: run through ACIS and HRC does fits files to create mpas   ---
#-----------------------------------------------------------------------------------

def run_exposure_maps(lyear, cmon):
    """
    run through ACIS and HRC does fits files to create mpas
    input:  lyear   --- "<year>"
            cmon    --- "<month>"
    output: png files in /data/mta_www/mta_max_exp/Images/
                        e.g., ACIS_<mon>_<year>.png
                              HRCI_08_1999_<mon>_<year>.png
    """

    ifile = '/data/mta_www/mta_max_exp/Cumulative/ACIS_07_1999_' + cmon + '_' + lyear

    for tail in ['', '_i2', '_i3', '_s2', '_s3']:
        fits  = ifile + tail + '.fits*'
        create_exposure_map(fits)


    ifile = '/data/mta_www/mta_max_exp/Month/ACIS_' + cmon + '_' + lyear

    for tail in ['', '_i2', '_i3', '_s2', '_s3']:
        fits  = ifile + tail + '.fits*'
        create_exposure_map(fits)

    fits = '/data/mta_www/mta_max_exp/Cumulative_hrc/HRCI_08_1999_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)
    fits = '/data/mta_www/mta_max_exp/Cumulative_hrc/HRCS_08_1999_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)


    fits = '/data/mta_www/mta_max_exp/Month_hrc/HRCI_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)

    fits = '/data/mta_www/mta_max_exp/Month_hrc/HRCS_' + cmon + '_' + lyear + '.fits*'
    create_exposure_map(fits)

    os.system('mv -f /data/mta_www/mta_max_exp/Cumulative/*png     /data/mta_www/mta_max_exp/Images/.')
    os.system('mv -f /data/mta_www/mta_max_exp/Month/*png          /data/mta_www/mta_max_exp/Images/.')
    os.system('mv -f /data/mta_www/mta_max_exp/Cumulative_hrc/*png /data/mta_www/mta_max_exp/Images/.')
    os.system('mv -f /data/mta_www/mta_max_exp/Month_hrc/*png      /data/mta_www/mta_max_exp/Images/.')

#-----------------------------------------------------------------------------------
#-- create_exposure_map: create an exposure map from a fits file using ds9        --
#-----------------------------------------------------------------------------------

def create_exposure_map(fits):
    """
    create an exposure map from a fits file using ds9
    input:  fits    --- fits file name
    output: out     --- png file
    """

    atemp = re.split('fits', fits)
    out   = atemp[0] + 'png'
    cmd   = 'ds9 ' + fits + '  -zoom to fit -scale histequ -cmap Heat -export png ' + out + ' -quit'

    try:
        bash(cmd,  env=ascdsenv)
    except:
        pass

#----------------------------------------------------------------------------------
#-- send_email_to_admin: send out a notification email to admin                  --
#----------------------------------------------------------------------------------

def send_email_to_admin():
    """
    send out a notification email to admin
    input:  none
    output: email to admin
    """
    out   = Chandra.Time.DateTime().date
    atemp = re.split('\.', out)
    ctime = time.strftime('%Y-%m', time.strptime(atemp[0], '%Y:%j:%H:%M:%S'))
    btemp = re.split('-', ctime)
    year  = btemp[0]
    mon   = int(float(btemp[1]))
    mon = mon - 1 #Pulls current month, report is for previous month.
    if (mon == 0):#If current month is Jan, then monthly report records Dec of previous year.
       year = int(float(year))
       year = year - 1
       mon = 12

    mon   = mcf.change_month_format(mon).upper()

    line = 'Monthly Report is created. Please create exposure maps and copy solar cycle plots.\n '
    line = line + 'https://cxc.harvard.edu/mta/REPORTS/MONTHLY/'
    line = line + str(year) + str(mon) + '/MONTHLY.html\n\n'
    line = line + "Don't forget to edit index file: /data/mta4/www/REPORTS/MONTHLY/index.html.\n"
    
    cmd = f'echo "{line}" | mailx -s "Subject: Monthly Report for {str(mon)} Created" {" ".join(ADMIN)}'
    os.system(cmd)

#-----------------------------------------------------------------

if __name__ == "__main__":

    if (len(sys.argv) >= 3 and sys.argv[1][:6] != 'email=' and sys.argv[2][:6] != 'email='):
        year = sys.argv[1]
        year = int(float(year))
        mon  = sys.argv[2]
        mon  = int(float(mon))
    else:
        year = ''
        mon  = ''

    create_monthly(year, mon)

