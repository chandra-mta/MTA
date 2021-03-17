#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       acis_sci_run_get_data.py:obtain data from MIT and update acis sci run   #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Mar 01, 2021                                               #
#                                                                               #
#################################################################################

import os
import sys
import re
import string
import random
import operator
import time
import Chandra.Time

path = '/data/mta/Script/ACIS/Acis_sci_run/house_keeping/dir_list_py_t'

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
import mta_common_functions     as mcf
import acis_sci_run_functions   as asrf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- a list of columns to extract
#
col_names = bin_data_dir + '/col_list2004'

#-----------------------------------------------------------------------------------------------
#---acis_sci_run_get_data: extracts mit data and updates acis science run data               ---
#-----------------------------------------------------------------------------------------------

def acis_sci_run_get_data(tyear=''):
    """
    this function is a driving fuction which extracts mit data 
    and updates acis science run data
    input:  tyear    --- the year in which we want to extract, process data
            data needed will be downloaded from mit site
    output: updated data tables in web_dir/Year<this_year>
        data_<year> --- this contains all data
        sub data sets are:
            te1_3_out           te3_3_out
            te5_5_out           cc2_3_out
            drop_<year>         drop5x5_<year>
            high_error_<year>   high_error5x5_<year>
            high_event_<year>   high_event5x5_<year>
            --- there are a few other files, but they are mostly empty and ignored.
    """
#
#---check whether "Working_dir" exists
#
    if os.path.isdir('./Working_dir'):
        cmd = 'rm -f ./Working_dir/*'
    else:
        cmd = 'mkdir -p ./Working_dir'
    os.system(cmd)
#
#--- set year of the data extraction if it is not given
#
    today   = time.strftime("%Y:%m:%d", time.gmtime())
    atemp   = re.split(':', today)
    year    = int(float(atemp[0]))
    month   = int(float(atemp[1]))
    mday    = int(float(atemp[2]))

    if tyear == '':
        nchk    = 0
        tyear   = year
    else:
        nchk    = 1
#
#--- setting the output directory
#
    cout_dir = 'Year' + str(tyear) + '/'
    oweb     = web_dir + cout_dir
    if not os.path.isdir(oweb):
        cmd = 'mkdir -p ' + oweb
        os.system(cmd)
#
#--- if the process asks to update of a specific year
#
    if nchk > 0:
        mit_data = get_mit_data(tyear)
        update_data_tables(tyear, mit_data)
#
#--- update data of the current year and possinbly the last year
#
    else:
        mit_data = get_mit_data(tyear)
#
#--- still working the last year's data
#
        if len(mit_data) == 0:
            mit_data = get_mit_data(tyear-1)
            update_data_tables(tyear-1, mit_data)
#
#--- the current year's data available
#
        else:
            update_data_tables(tyear, mit_data)
#
#--- make sure that the last year's data are completed
#
            if (month == 1) and (mday < 10):
                if check_year_data_complete(tyear-1) == False:
                    mit_data = get_mit_data(tyear-1)
                    update_data_tables(tyear-1, mit_data)

#-----------------------------------------------------------------------------------------------
#-- check_year_data_complete: check whether the database for the given year is filled till the end 
#-----------------------------------------------------------------------------------------------

def check_year_data_complete(tyear):
    """
    check whether the database for the given year is filled till the end
    input:  tyear   --- the year of the data to be examined
    output: True/False
    """
    name  = web_dir + 'Year' + str(tyear) + '/data' + str(tyear)
    data  = mcf.read_data_file(name)
    atemp = re.split('\s+', data[-1])
    btemp = re.split(':',   atemp[1])
    ldate = float(btemp[0])

    if mcf.is_leapyear(tyear):
        base = 366
    else:
        base = 365

    if ldate == base:
        return True
    else:
        return False

#-----------------------------------------------------------------------------------------------
#-- update_data_tables: update data tables of the given year                                  --
#-----------------------------------------------------------------------------------------------

def update_data_tables(tyear, mit_data):
    """
    update data tables of the given year
    input:  tyear   --- the year of the data
            mit_data    --- a list of data
    output: data_<year> --- this contains all data
            sub data sets are:
                te1_3_out           te3_3_out
                te5_5_out           cc2_3_out
                drop_<year>         drop5x5_<year>
                high_error_<year>   high_error5x5_<year>
                high_event_<year>   high_event5x5_<year>
                --- there are a few other files, but they are mostly empty and ignored.
    """
    cout_dir = 'Year' + str(tyear)
#
#--- write out mit_data to the output directory
#
    name     = web_dir + cout_dir + '/data' + str(tyear)
    with open(name, 'w') as fo:
        for ent in mit_data:
            fo.write(ent + '\n')
#
#--- separate data into each category
#
    separate_data(mit_data, cout_dir)
#
#--- check whether there are any high events
#
    chk_high_events(tyear)
#
#--- update long term data tables
#
    longTermTable(tyear)
#
#--- update all_data file
#
    update_all_data(tyear)

#-----------------------------------------------------------------------------------------------
#--- get_mit_data: extract data from mit sites                                                --
#-----------------------------------------------------------------------------------------------

def get_mit_data(tyear):
    """
    extract mit data for the given year
    input:  tyear --- the year of which you want to extract mit data
    output: mit_data with column entries of (example):
            22027   365:63412.545   ACIS-S  I5  Te5x5   F   20.1    810116  0   0.0 NONE    CLQtooAlt1
    """
#
#--- read column names --- this is the name of columns we need to save
#
    col_list = mcf.read_data_file(col_names)
#
#--- first find out the latest version of phase by reading main html page 
#--- here is the lnyx script to obtain web page data
#
    [phase_list, start_list, end_list]  = create_phase_list()
#
#--- select the phase list cover the tyear
#
    tstart = str(tyear) + ':001:00:00:00'
    tstart = Chandra.Time.DateTime(tstart).secs

    tstop  = str(tyear + 1) + ':001:00:00:00'
    tstop  = Chandra.Time.DateTime(tstop).secs

    p_list = []
    for k in range(0, len(phase_list)):
        try:
            if (end_list[k] >= tstart) and (start_list[k] < tstop):
                p_list.append(phase_list[k])
        except:
            continue

    plen = len(p_list)
    if plen == 0:
        return []

    mit_data = []
    for k in range(0, plen):
#
#--- extract data for the period
#
        out_data = download_mit_data(tyear, p_list[k])
#
#--- if there is no new data, stop the entire operation
#
        if len(out_data) == 0:
            continue
#
#--- extract specified column data
#
        out_data = extract_elements(out_data, col_list)
#
#--- the first in the list; need to check the data from the last year
#
        if k == 0:
            chk = 1
#
#--- the last in the list; need to check the data from the next year
#
        elif (plen > 1) and (k == plen -1):
            chk = 2
        else:
            chk = 0
#
#--- keep only data of the specified year
#
        out_data = clean_mit_data_list(out_data, chk)

        mit_data = mit_data + out_data

    return mit_data

#-----------------------------------------------------------------------------------------------
#-- clean_mit_data_list: remove the data lines which are not of the main year                 --
#-----------------------------------------------------------------------------------------------

def clean_mit_data_list(mit_data, chk):
    """
    remove the data lines which are not of the main year
    input:  mit_data    --- data list
            chk         --- indicator of which data set:1 --- first/ 2--- last
    output: mit_data    --- cleaned data list
    """
    clean_mit_data = []
    for ent in mit_data:
        atemp = re.split('\s+', ent)
        btemp = re.split(':',   atemp[1])
        try:
            ydate = float(btemp[0])
        except:
            continue
#
#--- the first set of the data usually contains a part from the last year
#
        if (chk == 1) and (ydate > 200):
            continue
#
#--- the last set of the data sometime contains a part from the next year
#
        elif chk == 2:
            if ydate < 100:
                break
            else:
                clean_mit_data.append(ent)

        else:
            clean_mit_data.append(ent)

    return clean_mit_data

#-----------------------------------------------------------------------------------------------
#-- create_phase_list: create a list of phase from the mit web site                           --
#-----------------------------------------------------------------------------------------------

def create_phase_list():
    """
    extract the phase numbers from mit site and creates a list
    input: none but read from MIT site: https://acisweb.mit.edu/asc/
    output: phase_list  --- a list of the phase numbers
            start_list  --- a list of the phase starting time in seconds from 1998.1.1
            end_list    --- a list of the phase ending time in seconds from 1998.1.1
    """
#
#--- using lynx, read the mit web page where shows phase list
#
    cmd = '/usr/bin/wget -O ' + zspace + ' https://acisweb.mit.edu/asc/' 
    os.system(cmd)
    data = mcf.read_data_file(zspace, remove=1)

    phase_list = []
    start_list = []
    end_list   = []
    chk = 0
    for ent in data:
        if chk == 0:
            mc  = re.search('nbsp;Phase', ent)
            if mc is not None:
                atemp = re.split('Phase', ent)
                btemp = re.split('\<',    atemp[1])
                val = float(btemp[0])
                phase_list.append(int(val))
                chk = 1
                continue
        elif chk == 1:
            atemp = re.split('<tt>', ent)
            btemp = re.split('\<', atemp[1])
            ltime = btemp[0]

            try:
                stime = asrf.convert_to_chandra_time(ltime, ifmt='%m/%d/%y')
                start_list.append(stime)
                chk = 2
                continue
            except:
                continue
        elif chk == 2:
            try:
                atemp = re.split('tt\>', ent)
                btemp = re.split('\<', atemp[1])
                ltime = btemp[0]
            except:
                end_list.append(6374591994)     #--- the latest period has an open ending
                chk = 0
                continue
            try:
                stime = asrf.convert_to_chandra_time(ltime, ifmt='%m/%d/%y')
                end_list.append(stime)
                if val == 1:
                    break
                chk = 0
                continue
            except:
                continue
#
#--- reverse all list to the oldest to newest
#
    phase_list = list(reversed(phase_list))
    start_list = list(reversed(start_list))
    end_list   = list(reversed(end_list))

    return [phase_list, start_list, end_list]

#-----------------------------------------------------------------------------------------------
#-- download_mit_data: for given time periods, extract data from mit site using their xs3 files    ----
#-----------------------------------------------------------------------------------------------

def download_mit_data(tyear, phase):
    """
    using the given phase interval, extreact science run data from mit site
    input: tyear        --- the year of the data extraction
           phase        --- the phase of the data set
           the data will be read from mit site (XS format)
                https://acisweb.mit.edu/asc/acisproc<phase>/acis<phase>.xs3
    output: new_data    ---  extracted data table
    """
    new_data = []
    ifile = 'https://acisweb.mit.edu/asc/acisproc' + str(phase) + '/acis' + str(phase) + '.xs3'
    cmd   = '/usr/bin/wget -O ./Working_dir/input_data ' + ifile
    os.system(cmd)

    cmd   = 'cp ./Working_dir/input_data ' + web_dir + 'Year' + str(tyear) + '/' + str(phase)
    os.system(cmd)
#
#--- extract a new part of the data
#
    data = mcf.read_data_file('./Working_dir/input_data')

    for ent in data:
        m1 = re.search('Multiple Choices',  ent)
        m2 = re.search('not found',         ent)
        m3 = re.search('Object not found!', ent)
        m4 = re.search('was not found',     ent)
        if m1 is not None:
            break

        if m2 is not None:
            break

        if m3 is not None:
            break

        if m4 is not None:
            break

        new_data.append(ent)

    return new_data

#-----------------------------------------------------------------------------------------------
#-- extract_elements: extract needed data from mit dataset                                  ----
#-----------------------------------------------------------------------------------------------

def extract_elements(new_data, col_list):
    """
    extract only data needed from the data extracted from mit site.
    input:   new_data --- data extreacted from MIT site
             col_list --- a list of column names which we want to extract from new_data

             new_data contains data in the following format (example)
            ......
             Cn@A2:f2,0|j3|F1:=1
             Cn@B2:f2,0|F1:=53956
             Cl@C2:F1:"HRC-S"
             Cl@D2:j3|F1:"NONE"
             Cl@E2:c5,0|j3|F1:"FEB0413a"
             Cl@F2:c5,0|F1:"Faint_Mode_I"
             Cn@G2:c5,0|f2,0|j3|F1:=0
             Cl@H2:j2|F1:"18028:032"
             Cl@I2:j3|F1:"41:08149.053"
             Cl@J2:j3|F1:"41:16442.880"
             Cn@K2:f2,1|F1:=8.3
             Cn@L2:f2,1|F1:=100.0
             Cl@M2:j3|F1:"I6"
            ......
    output:  new_data_save: data table only contains needed data in more usable format
    """
#
#--- initialized arrays
#
    c_dict = {}
    for colnam in col_list:
        c_dict[colnam] = []
#
#---- since the last data entry of the table is usually incomplate, we need to drop it
#
    max_read = len(new_data) -1
    ichk     = 0
#
#---- read data
#
    for ent in new_data:
        if ichk == max_read:                #---- check the entry until reaching the last entry
            break
        ichk += 1

        if ent[0] == 'C':
            btemp = re.split('\@', ent)
            ctemp = re.split('\:', btemp[1])
            dtemp = ctemp[0]
            seq    = ''
            pos_id = ''
            val    = 'NA'
            for letter in dtemp:
                try:
                    val = float(letter)
                    seq = seq + letter
                except:
#
#--- pos_id: entry position id: A.... BA
#
                    pos_id = pos_id + letter
#
#--- save data for only columns we need
#
            for comp in col_list:
                if pos_id.lower() == comp:
#
#---- time entries need a special care
#
                    if pos_id in ['I', 'J', 'i', 'j']:
                        gtemp =  re.split('\"', ent)
                        val   = gtemp[1]
                    else:
#
#---- none time element entries
#
                        m = re.search('=', ctemp[2])
                        if m is not None:
                            etemp = re.split('=', ctemp[2])
                            val   = etemp[1]
                        else:
                            ftemp = re.split('\"', ctemp[2])
                            val   = ftemp[1]
     
                    vname         = pos_id.lower()
                    p_list = c_dict[vname]
                    p_list.append(val)
                    c_dict[vname] =  p_list
                    break
#
#---- rearrange data
#
    tlen          = len(c_dict[col_list[0]])
    new_data_save = []
    for i in range(0, tlen):
        line = ''
        for colnam in col_list:
            try:
                add  = c_dict[colnam][i]
            except:
                add = ''

            if line == '':
                line = add
            else:
                line = line + '\t' +  str(add)

        new_data_save.append(line)

    return new_data_save

#-----------------------------------------------------------------------------------------------
#-- separate_data: separate data into sub groups and save them in the separate files         ---
#-----------------------------------------------------------------------------------------------

def separate_data(mit_data, current_dir):
    """
    this function separate the data into sub data sets
    input: mit_data     --- a list of data
           current_dir  --- the name of the directory containing the "file"
    output: sub data files (see below... <>_out, the data will be saved in current_dir
    """
#
#--- output file name list
#
    out  = ['te1_3_out', 'te3_3_out', 'te5_5_out', 'te_raw_out', 'te_hist_out', 'cc1_3_out',\
            'cc3_3_out', 'cc5_5_out', 'cc_raw_out', 'cc_hist_out']
#
#--- condition list
#
    clist = ['Te1x3', 'Te3x3', 'Te5x5', 'TeRaw', 'TeHist', 'Cc1x3', 'Cc3x3', 'Cc5x5', 'CcRaw', 'CcHist']

    fs = []
    fs = ['' for x in range(0, 10)]

    for ent in mit_data:
        col = re.split('\s+', ent)
#
#--- only ACIS data will be extracted
#
        if col[2] in ['ACIS-I', 'ACIS-S']:
            line = ent + '\n'
            for k in range(0, 10):
                if col[4] == clist[k]:
                    fs[k] = fs[k] + line
                    break
#
#--- write out the data
#
    for k in range(0, 10):
        if fs[k] != '':
            line = web_dir + current_dir + '/' + out[k]
            with open(line, 'w') as fo:
                fo.write(fs[k])

#-----------------------------------------------------------------------------------------------
#--- chk_high_events: control function to check high count/drop rate events                  ---
#-----------------------------------------------------------------------------------------------

def chk_high_events(year):
    """
    check high error rates / count rates /drop rates comparing to the given criteria and update 
    the files
    input: year         --- current year.  data are read from the directory Year<year>
    output: drop_<year>         drop5x5_<year>
            high_error_<year>   high_error5x5_<year>
            high_events_<year>  high_events5x5_<year>
    """
#
#--- te3x3 high drop rate
#
    etype    = 'drop'
    event    = 'te3_3'
    criteria = 3.0 
    dname    = 'drop rate(%)'
    asrf.checkEvent(web_dir, etype,  event, year,  criteria, dname)
#
#--- te5x5 high drop rate
#
    etype    = 'drop5x5'
    event    = 'te5_5'
    criteria = 3.0
    dname    = 'drop rate(%)'
    asrf.checkEvent(web_dir, etype,  event, year, criteria, dname)
#
#--- te3x3 high error rate
#
    etype    = 'high_error'
    event    = 'te3_3'
    criteria = 1.0 
    dname    = 'err/ksec    '
    asrf.checkEvent(web_dir, etype,  event, year, criteria, dname)
#
#--- te5x5 high error rate
#
    etype    = 'high_error5x5'
    event    = 'te5_5'
    criteria = 1.0 
    dname    = 'err/ksec    '
    asrf.checkEvent(web_dir, etype,  event, year, criteria, dname)
#
#--- te3x3 high event rate
#
    etype    = 'high_event'
    event    = 'te3_3'
    criteria = 180.0 
    dname    = 'avg # of events/sec'
    asrf.checkEvent(web_dir, etype,  event, year, criteria, dname)
#
#--- te5x5 high event rate
#
    etype    = 'high_event5x5'
    event    = 'te5_5'
    criteria = 180.0 
    dname    = 'avg # of events/sec'
    asrf.checkEvent(web_dir, etype,  event, year, criteria, dname)

#-----------------------------------------------------------------------------------------------
#-- longTermTable: control function to update long term data tables                          ---
#-----------------------------------------------------------------------------------------------

def longTermTable(year):
    """
    control function to update each data table file save in Year<year> directory
    Input: year ---- the year you want to update 

    Ouptput data file in Year<year> directory e.g. high_errr_<year> or te3_3_out
    """
#
#--- acis_sci_run_te3x3 drop rate
#
    event   = 'drop'
    dname   = 'drop rate(%)'
    asrf.updateLongTermTable(web_dir, event, year, dname)
#
#--- acis_sci_run_te5x5 drop rate
#
    event   = 'drop5x5'
    dname   = 'drop rate(%)'
    asrf.updateLongTermTable(web_dir, event, year, dname)
#
#--- acis_sci_run_err3x3
#
    event   = 'high_error'
    dname   = 'err/ksec    '
    asrf.updateLongTermTable(web_dir, event, year, dname)
#
#--- acis_sci_run_err5x5
#
    event   = 'high_error5x5'
    dname   = 'err/ksec    '
    asrf.updateLongTermTable(web_dir, event, year, dname)
#
#--- acis_sci_run_high_evnt3x3
#
    event   = 'high_event'
    dname   = 'avg # of events/sec'
    asrf.updateLongTermTable(web_dir, event, year, dname)
#
#--- acis_sci_run_high_evnt5x5
#
    event   = 'high_event5x5'
    dname   = 'avg # of events/sec'
    asrf.updateLongTermTable(web_dir, event, year, dname)
#
#--- te1x3
#
    event = 'Te1_3'
    asrf.updateLongTermTable2(web_dir, event, year)
#
#--- te3x3
#
    event = 'Te3_3'
    asrf.updateLongTermTable2(web_dir, event, year)
#
#--- te5x5
#
    event = 'Te5_5'
    asrf.updateLongTermTable2(web_dir, event, year)
#
#--- te_raw
#
    event = 'Te_raw'
    asrf.updateLongTermTable2(web_dir, event, year)
#
#--- cc3x3
#
    event = 'cc3_3'
    asrf.updateLongTermTable2(web_dir, event, year)

#-----------------------------------------------------------------------------------------------
#-- update_all_data: update a file "all_data" to current                                     ---
#-----------------------------------------------------------------------------------------------

def update_all_data(tyear):
    """
    this function updates a file "all_data" which contains all past data.
    input:  tyear    ---the year of the mit_data
    output: <web_dir>/all_data
    """
    odata = web_dir  + 'all_data'
    with open(odata, 'w') as fo:
        for year in range(1999, tyear+1):
            infile = web_dir + 'Year' + str(year) + '/data' + str(year)
            data   = mcf.read_data_file(infile)
            for ent in data:
                atemp = re.split('\s+', ent)
                date  = atemp[1]
                ldate = str(year) + ':' + date
                ent   = ent.replace(date, ldate)
                fo.write(ent + '\n')
#
#--- remove duplicated lines
#
    asrf.removeDuplicated(odata)

#--------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        year = int(float(sys.argv[1]))
    else:
        year = ''

    acis_sci_run_get_data( year)

