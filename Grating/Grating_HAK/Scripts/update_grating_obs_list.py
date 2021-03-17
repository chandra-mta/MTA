#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#           update_grating_obs_list.py: update grating observations lists                       #
#                              which generate grat index.html page                              #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Mar 09, 2021                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import random
import numpy
import time
#
#--- reading directory list
#
path = '/data/mta/Script/Grating/Grating_HAK/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import mta_common_functions     as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set a few global variables
#
month_list    = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
data_location = '/data/mta_www/mta_grat/Grating_Data/'
sot_directory = '/data/mta4/obs_ss/sot_ocat.out'

#----------------------------------------------------------------------------------------------
#-- update_grating_obs_list: update grating observations lists                               --
#----------------------------------------------------------------------------------------------

def update_grating_obs_list():
    """
    update grating observations lists
    Input:  none, but read from <data_location> and <sot_directory>
    Output: <web_dir>/Grating_Data/grating_list_year<year>html
            <web_dir>/Grating_Data/grating_list_past_six_month.html
    """
    obs_dict = get_obsdate()

    tyear = int(time.strftime('%Y', time.gmtime()))
    tmon  = int(time.strftime('%m', time.gmtime()))
    lyear = tyear + 1

    pyear = tyear
    pmon  = tmon - 6
    if pmon < 1:
        pmon  += 12
        pyear -= 1
#
#--- start checking from this year to backward
#
    acis_hetg_r = []
    acis_letg_r = []
    hrc_letg_r  = []

    for year in range(tyear, 1998, -1):
        ytemp = str(year)
        pyr = ytemp[2] + ytemp[3]

        acis_hetg   = []
        acis_letg   = []
        hrc_letg    = []
#
#--- if this is this year, start from this month to backward
#
        if year == tyear:
            smon = tmon
        else:
            smon = 12

        for  k in range(smon-1, -1, -1):
            if (year == tyear) and (k >tmon):
                continue

            if (year == 1999) and (k < 7):
                break

            tdir = data_dir + month_list[k] + pyr
            if os.path.isdir(tdir) and len(os.listdir(tdir)) > 0:
                cmd = 'ls ' + tdir + '/*/*_Sky_summary.html>' + zspace
                os.system(cmd)

            data = mcf.read_data_file(zspace, remove=1)

            if len(data) == 0:
                continue
#
#--- check whether to keep the data in recent list
#
            achk = 0
            if year > pyear:
                achk = 1
            elif year == pyear:
                if k >= pmon:
                    achk = 1
#
#--- classify which link goes to which category
#
            for ent in data:
                catg = check_category(ent)
                if catg == False:
                    continue

                if catg == 'acis_hetg':
                    acis_hetg.append(ent)
                    if achk == 1:
                        acis_hetg_r.append(ent)

                elif catg == 'acis_letg':
                    acis_letg.append(ent)
                    if achk == 1:
                        acis_letg_r.append(ent)

                else:
                    hrc_letg.append(ent)
                    if achk == 1:
                        hrc_letg_r.append(ent)
#
#--- write a html page for each year
#
        write_html_page(year, acis_hetg, acis_letg, hrc_letg, obs_dict)
#
#--- write a html page for the last 6 month
#
    write_html_page(0, acis_hetg_r, acis_letg_r, hrc_letg_r, obs_dict)

#------------------------------------------------------------------------------------
#-- check_category: check which category this observation                          --
#------------------------------------------------------------------------------------

def check_category(ifile):
    """
    check which category this observation
    input:  ifile   --- file name with data path (partial)
    output: catg    --- acis_hetg, acis_letg, hrc_letg
    """
    with open(ifile, 'r') as f:
        text = f.read()
#
#--- check the file contain the words "ACIS-S", "HRC", "HETG", or "LETG"
#
    chk1  = re.search('ACIS-S', text)  
    chk2  = re.search('HRC',    text)  
    chk3  = re.search('HETG',   text)  
    chk4  = re.search('LETG',   text)  

    if chk1 is not None:
        if chk3 is not None:
            catg = 'acis_hetg'
        else:
            catg = 'acis_letg'

    elif chk2 is not None:
        catg = 'hrc_letg'

    else:
        catg = False

    return catg

#------------------------------------------------------------------------------------
#-- write_html_page: wirte a html page for year grating observations               --
#------------------------------------------------------------------------------------

def write_html_page(year, acis_hetg, acis_letg, hrc_letg, obs_dict):
    """
    wirte a html page for year grating observations
    input:  year    --- year
            acis_hetg   --- a list of acis_hetg list
            acis_letg   --- a list of acis_letg list
            hrc_letg    --- a list of hrc_letg list
    output: <data_dir>/grating_list_year<year>.html
    """
#
#--- acis hetg data list tends to be long; devide into two lists
#
    [acis_hetg1, acis_hetg2] = devide_list_to_two(acis_hetg)
#
#--- match the length of lists; d_list = [acis_letg, acis_hetg1, acis_hetg2, hrc_letg]
#
    [d_list, tmax]  = match_lentgh([acis_letg, acis_hetg1, acis_hetg2, hrc_letg])
#
#--- write table lines
#
    if tmax > 0:
        line = ''
        for k in range(0, tmax):

            line = line + '<tr>\n'
            for m in range(0, len(d_list)):
                line = line + '\t<th>' + get_info(d_list[m][k],  obs_dict) + '</th>\n'

            line = line + '</tr>\n'
#
#--- if there is no data, say so
#
    else:
            line = '<tr><th colspan=3>No Grating Observations </th></tr>\n'

    lyear = int(time.strftime('%Y', time.gmtime())) + 1
    m = 0 
#
#--- if it is not a main page, adding link to the last six month page
#
    if year == 0:
        line2 = '<tr>\n'
    else:
        line2 = '<tr>\n<th colspan=10><a href="'
        line2 = line2 +  'grating_list_past_six_month.html'
        line2 = line2 + '">Last Six Months</a></th>\n</tr>\n'
        line2 = line2 + '<tr>\n'
#
#--- add all other year links, except the year of the page
#
    for k in range(1999, lyear):
        if k == year:
            line2 = line2 + '<th style="color:green;"><b>' + str(k) + '</b></th>\n'
        else:
            line2 = line2 + '<th><a href="grating_list_year' + str(k) + '.html">' 
            line2 = line2 + str(k) + '</a></th>\n'
        m += 1
        if m >= 10:
            line2 = line2 + '</tr>\n<tr>\n'
            m = 0

    if (m > 0) and (m < 10):
        for k  in range(m, 10):
            line2 = line2 + '<td>&#160;</td>'
        line2 = line2 + '</tr>\n'
#
#--- read the template for the html page
#
    t_file = house_keeping + 'grating_obs_template'
    with open(t_file, 'r') as f:
        text   = f.read()
#
#--- replace the year and the table entry
#
    if year == 0:
        yline =  "the Last Six Months"
        outfile = data_dir + '/grating_list_past_six_month.html'
    else:
        yline = "Year " + str(year)
        outfile = data_dir + '/grating_list_year' + str(year) + '.html'

    text   = text.replace('#YEAR#',   yline)
    text   = text.replace('#TABLE#',  line)
    text   = text.replace('#TABLE2#', line2)
#
#--- check whether this is the html page for the last 6 months
#
    with  open(outfile, 'w') as fo:
        fo.write(text)

#------------------------------------------------------------------------------------
#-- devide_list_to_two: devide a long list into two lists                          --
#------------------------------------------------------------------------------------

def devide_list_to_two(alist):
    """
    devide a long list into two lists
    input:  alist           --- a list
    output: alist1/alist2   --- two lists of about the same length
    """
    a_len = len(alist)
    
    if a_len > 3:
        half = int(0.5 * a_len)
        alist1 = alist[:half]
        alist2 = alist[half:]
    else:
        alist1 = alist
        alist2 = []

    return [alist1, alist2]

#------------------------------------------------------------------------------------
#-- match_lentgh: add empty value to match the length of lists                     --
#------------------------------------------------------------------------------------

def match_lentgh(list_d, add='&#160;'):
    """
    add empty value to match the length of lists 
    input:  list_d  --- a list of lists
            add     --- the value/string to add to fill the empty spot
    output: save    --- a list of lists of the same length
            tmax    --- the length of the each list
    """
    l_len = len(list_d)
#
#--- find max length of lists
#
    tmax = len(list_d[0])
    for k in range(1, l_len):
        val = len(list_d[k])
        if val > tmax:
            tmax = val

    save = []
#
#--- fill the empty part with  add
#
    for k in range(0, l_len):
        start = len(list_d[k])
        for m in range(start, tmax):
            list_d[k].append(add)

        save.append(list_d[k])

    return [save, tmax]

#------------------------------------------------------------------------------------
#-- get_info: create table cell display info                                      ---
#------------------------------------------------------------------------------------

def get_info(line, obs_dict):
    """
    create table cell display info
    input:  line        --- link to the html page
            obs_dict    --- a dictionary of obsid <---> observation time
    output: oline       --- a table cell display
    """
    if line == '&#160;':
       return line

    else:
        atemp = re.split('\/', line)
        try:
            obsid = int(atemp[-2])
        except:
            obsid = 'na'
#
#--- find observation time
#
        try:
            stime = obs_dict[obsid]
#
#--- if it cannot find, use the short one
#
        except:
            stime = atemp[-3]
#
#--- adjust the link path
#
        ltemp = re.split('Grating_Data', line)
        line  = 'https://cxc.cfa.harvard.edu/mta_days/mta_grat/Grating_Data/' + ltemp[1]
        oline = '<a href="'+  line + '" target="_parent">'
        oline = oline + 'Date: ' +  stime + '<br />' + 'Obsid: ' +  str(obsid) + '</a>'

        return oline

#------------------------------------------------------------------------------------
#-- get_obsdate: read sot database and make a list of obsids and observation dates --
#------------------------------------------------------------------------------------

def get_obsdate():
    """
    read sot database and make a list of obsids and its observation dates
    Input:  none, but read data from <sot_direcotry>
    Output: obs_dict ---    a dictionary of obsid <--> starting date
    """
#
#--- read sot data
#
    data = mcf.read_data_file(sot_directory)

    obsid_list = []
    start_date = []
    index_date = []
    obs_dict   = {}
    for ent in data:
        temp = re.split('\^', ent)
        obsid = temp[1]
#
#--- check the data are valid
#
        try:
            atemp = re.split('\s+', temp[13])
            mon   = mcf.change_month_format(atemp[0])
            date  = atemp[1]
            year  = atemp[2][2] + atemp[2][3]
        except:
            continue
#
#--- starting date in form of 05/23/14
#
        lmon  = mcf.add_leading_zero(mon)
        ldate = mcf.add_leading_zero(date)

        dline = lmon + '/' + ldate + '/' + year

        try:
            obs_dict[int(obsid)] = dline
        except:
            pass

    return obs_dict

#------------------------------------------------------------------------------------

if __name__ == '__main__':

    update_grating_obs_list()
