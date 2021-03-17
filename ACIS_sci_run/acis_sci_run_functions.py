#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       acis_sci_run_functions.py: collection of functions used by acis sci run #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Feb 26, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import time
import Chandra.Time

path = '/data/mta/Script/ACIS/Acis_sci_run/house_keeping/dir_list_py_t'
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

http_dir = 'https://cxc.cfa.harvard.edu/mta_days/mta_acis_sci_run/'
#
#--- NOTE:
#--- because we need to run test, web_dir read from dir_list_py cannot be used. instead
#--- we are passing from the main script's web_dir to local html_dir variable. (Apr 26, 2013)
#

#-----------------------------------------------------------------------------------------------
#--- removeDuplicated: remove duplicated entries                                             ---
#-----------------------------------------------------------------------------------------------

def removeDuplicated(ifile):
    """
    remove duplicated rows from the file
    Input:      file --- a file name of the data

    Output:     file --- cleaned up data
    """

    data = mcf.read_data_file(ifile)

    if len(data) > 0:
        first = data.pop(0)
        new   = [first]
    
        for ent in data:
            chk = 0
            for comp in new:
                if ent == comp:
                    chk = 1
                    break
            if chk == 0:
                new.append(ent)
    
#
#--- now print out the cleaned up data 
#
        with open(ifile, 'w') as f:
            for ent in new:
                line = ent + '\n'
                f.write(line)

#-----------------------------------------------------------------------------------------------
#--- acis_sci_run_print_html: update html pages                                               --
#-----------------------------------------------------------------------------------------------

def acis_sci_run_print_html(html_dir, pyear, pmonth, pday):
    """
    update three html pages according for the year (pyear)
    Input: html_dir --- web directory path
           pyear  --- the year you want to update the html pages
           pmonth --- current month
           pday   --- current month date
    Output: science_run.html
            science_run<year>.html
    """
#
#--- set substitution values
#
    pyear  = int(pyear)
    cpmon  = mcf.add_leading_zero(int(float(pmonth)))
    cpday  = mcf.add_leading_zero(int(float(pday)))
    update = str(pyear) + '-' + str(cpmon) + '-' + str(cpday)
    ydate  = int(float(time.strftime("%j", time.strptime(update, '%Y-%m-%d'))))
#
#--- make a link table
#
    ylist = ''
    j     = 0
    for ryear in range(1999, pyear+1):
        ylist = ylist + '<td><a href='  + http_dir   + '/Year' + str(ryear) 
        ylist = ylist + '/science_run'  + str(ryear) + '.html>'
        ylist = ylist + '<strong>Year ' + str(ryear) + '</strong></a><br /><td />\n'
#
#--- every 6 years, break a row
#
        if j == 5:
            j = 0
            ylist = ylist + '</tr><tr>\n'
        else:
            j += 1
#
#---- update the main html page
#
    template = house_keeping + 'science_run.html'
    outfile  = html_dir      + 'science_run.html'

    print_html_page(template, update, pyear, ylist, outfile)
#
#--- update sub directory html pages
#
    ystop = pyear + 1
    for syear in range(1999, ystop):
        template = house_keeping + 'sub_year.html'
        outfile  = html_dir + 'Year' + str(syear) + '/science_run' + str(syear) + '.html'

        if syear == pyear:
            ldate = update
        else:
            ldate = str(syear) + '-12-31'

        print_html_page(template, ldate, syear, ylist, outfile)

#-----------------------------------------------------------------------------------------------
#-- print_html_page: read template and update the html page                                   --
#-----------------------------------------------------------------------------------------------

def print_html_page(template, update, syear, ylist, outfile):
    """
    read template and update the html page
    input:  template    --- the template file name
            update      --- udated date
            syeare      --- year
            ylist       --- html table containing links to sub directories
            outfile     --- html file name
    output: outfile
    """
    f     = open(template, 'r')
    hfile = f.read()
    f.close()

    temp0 = hfile.replace('#UPDATE#', update)
    temp1 = temp0.replace('#YEAR#',   str(syear))
    temp2 = temp1.replace('#YLIST#',  str(ylist))

    with open(outfile, 'w') as f:
        f.write(temp2)

#-----------------------------------------------------------------------------------------------
#--- checkEvent: check high event/error/drop cases, and send out a warning message if needed ---
#-----------------------------------------------------------------------------------------------

def checkEvent(html_dir, etype, event, year, criteria, dname):
    """
    check high event/error/drop cases, and send out a warning message if needed
    input: html_dir --- web directory path
           etype    --- type of error  e.g. drop for  Te3_3
           event    --- event name     e.g. Te3_3
           criteria --- cut off        e.g. 3.0 for Te3_3
           dname    --- table name     e.g. drop rate(%)

    output: ofile --- updated with newly found violation
    """
#
#----- read the main table and file new entries
#
    ifile = html_dir + 'Year' + str(year) + '/' + event + '_out'
    cdata = mcf.read_data_file(ifile)
#
#----- check data type: drop rate, high error, and high event
#
    mchk     = re.search('drop',  etype)
    mchk2    = re.search('error', etype)
    new_list = []
    sline    = ''
    for ent in cdata:
        atemp = re.split('\s+', ent)
#
#--- if the case is "drop" rate, the pass the data as it is
#
        if mchk is not None:
            try:
                cval = float(atemp[9])                  #--- drop rate
            except:
                continue
#
#--- otherwise normalize the data
#
        else:
            cval = 0
            try:
                val6  = float(atemp[6])
                if val6 > 0:
                    if mchk2 is not None:
                        cval = float(atemp[8])/val6     #--- high error
                    else:
                        cval = float(atemp[7])/val6     #--- high count
            except:
                continue
#
#--- here is the selection criteria
#
        if cval > criteria:
            cval = round(cval, 3)
#
#--- limit length of description to 20 letters
#
            alen  = len(atemp[11])
            if alen < 20:
                dline = atemp[11]
                for i in range(alen, 20):
                    dline = dline + ' '
            else:
                dline = '' 
                for i in range(0, 20):
                    dline = dline + atemp[11][i]

#
#--- some foramtting adjustments
#
            if len(atemp[0]) < 4:
                sp = '\t\t'
            else:
                sp = '\t'
            if len(atemp[1]) < 12:
                sp2 = '\t\t\t'
            else:
                sp2 = '\t\t'
            tlen = len(atemp[6])
            lval  = atemp[6]
            for k in range(tlen,4):
                lval = ' ' + lval

            line  = atemp[0]          + sp   + dline     + '\t' + atemp[1] + sp2
            line  = line  + lval      + '\t' + atemp[2]  + '\t' + atemp[3] + '\t\t'
            line  = line  + atemp[10] + '\t' + str(cval) + '\n'

            sline = sline + line
            new_list.append(line)
#
#--- print out the table
#
    aline = 'obsid   target                  start time      int time    inst    '
    aline = aline + 'ccd     grat    ' + dname + '\n'
    aline = aline + '-------------------------------------------------------------'
    aline = aline + '----------------------------------------------\n'
    aline = aline + sline

    ofile = web_dir + 'Year' + str(year) + '/'+ etype + '_' + str(year)
    with open(ofile, 'w') as fo:
        fo.write(aline)

    return new_list

#-----------------------------------------------------------------------------------------------
#-- updateLongTermTable: update a long term violation tables                                 ---
#-----------------------------------------------------------------------------------------------

def updateLongTermTable(html_dir, event, this_year, dname):
    """
    updates long term violation tables
    Input:   html_dir --- web directory path
             events  --- name of events such as drop (te3_3)
             this_year --- the latest year
             dname     --- column name to use

    Output:
            violation table file named "event"
    """
    line = ''
    ytop = int(this_year) + 1
    for  year in range(1999, ytop):
        #line  = line +  '\nYear' + str(year) + '\n'

        fname = html_dir + 'Year' + str(year) + '/' + event.lower() + '_' + str(year)
        data  = mcf.read_data_file(fname)

        for ent in data:
            atemp = re.split('\s+', ent)
            try:
                val = float(atemp[0])
                otime = atemp[2]
                ntime = str(year) + ':' + otime
                ent   = ent.replace(otime, ntime)
                line = line + ent + '\n'
            except:
                pass
#
#--- write out the talbe
#
    hline  = 'obsid   target                  start time  int time        inst    ccd     grat    ' + dname + '\n'
    hline  = hline + '-----------------------------------------------------------------------------------------------------------\n'

    line   = hline + line
    oname  = html_dir + 'Long_term/' + event.lower()
    with open(oname, 'w') as fo:
        fo.write(line)


#-----------------------------------------------------------------------------------------------
#-- updateLongTermTable2: update long term sub data tables                                   ---
#-----------------------------------------------------------------------------------------------

def updateLongTermTable2(html_dir, event, this_year):
    """
    update long term sub data tables
    Input:   html_dir    web directory path
             event    name of the event  such as te3_3
             this_year    the latest year
    Output:  sub data file suchas te3_3_out
    """

    line = ''
    ytop = int(this_year) + 1
    for  year in range(1999, ytop):
#
#--- check leap year
#
        if mcf.is_leapyear(year):
            base = 366.0
        else:
            base = 365.0
#
#--- read each year's data
#
        fname = html_dir + 'Year' + str(year) + '/' + event.lower() + '_out'
        data  = mcf.read_data_file(fname)
        if len(data) == 0:
            continue

        for ent in data:
            atemp = re.split('\t+|\s+', ent)
            try:
                val   = float(atemp[0])
                btemp = re.split(':', atemp[1])
#
#--- convert time to year date to fractional year
#
                time  = float(year) + (float(btemp[0]) + float(btemp[1])/ 86400.0 ) / base
                time  = round(time, 3)
                dlen  = len(atemp)
                dlst  = dlen -1

                for j in range(0, dlen):
                    if j == 1:
                        line = line + str(time) + '\t'
                    elif j == dlst:
                        line = line + atemp[j]  + '\n'
                    else:
                        line = line + atemp[j]  + '\t'
            except:
                pass

    oname = html_dir + 'Long_term/' + event.lower() + '_out'
    with open(oname, 'w') as fo:
        fo.write(line)

#-----------------------------------------------------------------------------------------------
#-- chkNewHigh: sending out email to warn that there are value violatioins                  ----
#-----------------------------------------------------------------------------------------------

def chkNewHigh(old_list, new_list, event, dname):
    """
    sending out email to warn that there are value violatioins 
    Input: old_list:   old violation table
           new_list:   new violation table
           event:      event name
           dname:      column name to be used
    """
    wchk = 0
#
#--- compare old and new list and if there are new entries, save them in "alart"
#
    alart = []
    for ent in new_list:
        chk = 0
        ntemp  = re.split('\t+|\s+', ent)
        for comp in old_list:
            otemp = re.split('\t+|\s+', comp)
            if(ent == comp) or (ntemp[0] == otemp[0]):
                chk = 1
                break
        if chk == 0:
            alart.append(ent)
            wchk += 1
#
#--- if there is violations, send out email
#
    if wchk > 0:
        line = 'ACIS Science Run issued the following warning(s)\n\n'
        line = line + "The following observation has a " + event + "Rate in today's science run\n\n"
        line = line + 'obsid   target                  start time  int time        '
        line = line + 'inst    ccd     grat    ' + dname + '\n'
        line = line + '------------------------------------------------------------'
        line = line + '-------------------------------------------\n'
        for ent in alart:
            line = line + ent + '\n'

        line = line + '\nPlese check: https://cxc.cfa.harvard.edu/mta_days/mta_acis_sci_run/'
        line = line + 'science_run.html\n'
        line = line + '\n or MIT ACIS Site: https://acisweb.mit.edu/asc/\n'

        with open(zspace, 'w') as f:
            f.wirte(line)

        cmd = 'cat ' + zspace + '|mailx -s \"Subject: ACIS Science Run Alert<>' 
        cmd = cmd    + event  + 'Rate" isobe\@head.cfa.harvard.edu'
#        cmd = 'cat ' + zspace + '|mailx -s \"Subject: ACIS Science Run Alert<>' 
#        cmd = cmd    + event  + 'Rate" isobe\@head.cfa.harvard.edu  '
#        cmd = cmd    + swolk\@head.cfa.harvard.edu acisdude\@head.cfa.harvard.edu"'

        os.system(cmd)
    
        mcf.rm_files(zspace)

#-----------------------------------------------------------------------------------------------
#-- convert_to_chandra_time: convert time into Chandra Time                                   --
#-----------------------------------------------------------------------------------------------

def convert_to_chandra_time(dtime, ifmt='%Y:%m:%d:%H:%M:%S'):
    """
    convert time into Chandra Time
    input:  dtime   --- original time in ifmt 
            ifmt    --- time format
    output: stime   --- seconds from 1998.1.1
    """
    out   = time.strftime("%Y:%j:%H:%M:%S", time.strptime(dtime, ifmt))
    stime = int(Chandra.Time.DateTime(out).secs)

    return stime
