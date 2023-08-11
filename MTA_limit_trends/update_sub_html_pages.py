#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#   update_sub_html_pages.py: creates html pages for different categories of msids      #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Feb 01, 2021                                               #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import math
import numpy
import unittest
import time
from datetime import datetime
from time import gmtime, strftime, localtime
import getpass
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append("/data/mta4/Script/Python3.10/MTA")
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
import create_html_suppl        as chs  #---- collecitons of functions to create html pages

web_address  =  'https://' + web_address
#
#--- a list of thoese with sub groups
#
sub_list_file  = house_keeping + 'sub_group_list'
sub_group_list = mcf.read_data_file(sub_list_file)

#----------------------------------------------------------------------------------
#-- create_sub_html: creates html pages for different categories of msids        --
#----------------------------------------------------------------------------------

def create_sub_html():
    """
    creates html pages for different categories of msids
    input:  none, but read from <house_keeping>/msid_list_all
            read from <house_keeping>/sub_html_list_*
    output: <web_dir>/Htmls/<category>_main.html
    """
#
#--- get today's date in fractional year
#
    sec1998 = ecf.find_current_stime()
    ytime   = ecf.stime_to_frac_year(sec1998)
#
#--- create dictionary of unit and dictionary of descriptions for msid
#
    [udict, ddict] = ecf.read_unit_list()

#
#--- create category list and a dictionary of catg <--> [msid list]
#
    lfile = house_keeping + 'msid_list_all'
    data  = mcf.read_data_file(lfile)

    catg_dict = {}
    catg_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0].strip()
        catg  = atemp[1].strip()
        try:
            out = catg_dict[catg]
            out = out + [msid]
            catg_dict[catg] = out
        except:
            catg_dict[catg] = [msid]
            catg_list.append(catg)
#
#--- just in a case there is not directory for the page, create it
#
            dchk  = web_dir + catg
            if not os.path.isdir(dchk):
                cmd = 'mkdir ' + dchk
                os.system(cmd)
#
#--- create each dtype, mtype and category web page
#
    for dtype  in ['week','short', 'year', 'five', 'long']:
        for mtype in ['mid', 'min', 'max']:
            for catg in catg_list:
                create_html(catg, catg_dict[catg], ytime, udict, ddict, dtype, mtype)

#----------------------------------------------------------------------------------
#-- create_html: create a html page for category <catg>                         ---
#----------------------------------------------------------------------------------

def create_html(catg, msid_list, ytime, udict, ddict, dtype, mtype, ptype='static'):
    """
    create a html page for category <catg>
    input:  catg    --- category of the msids
            msid_list  --- a list of msids of the category
            ytime   --- current time
            udict   --- a dictionary of unit: <msid> <---> <unit>
            ddict   --- a dictionary of description: <msid> <---> <description>
            dtype   --- date length: week, short, year, five, long
            mtype   --- data type: mid, min, max
    output: <catg>_main.html
    """
#
#--- create links to other pages
#
    line = '<!DOCTYPE html>\n<html>\n<head>\n\t<title>Envelope Trending  Plots: ' 
    line = line + catg.upper() + '</title>\n'
    line = line + '</head>\n<body style="width:95%;margin-left:10px; margin-right;'
    line = line + '10px;background-color:#FAEBD7;'
    line = line + 'font-family:Georgia, "Times New Roman", Times, serif">\n\n'

    line = line + '<div style="float:right;padding-right:50px;font-size:120%">\n'
    line = line + '<a href="../mta_trending_main.html" '
    line = line + 'style="float:right;padding-right:50px;font-size:80%">'
    line = line + '<b>Back to Top</b></a><br />\n'

    line = line + '</div>\n'

    line = line + '<h3 style="padding-bottom:0px">' + catg.upper() + ' '

    if ptype == 'static':
        line = line + '<br /> Static Version: '
    else:
        line = line + '<br /> Interactive Version: '

    if mtype == 'min':
        line = line +  ' Min --- '
    elif mtype == 'max':
        line = line +  ' Max --- '
    else:
        line = line +  ' Mean --- ' 

    if dtype == 'week':
        line = line +  ' One Week '
    elif dtype == 'short':
        line = line +  ' Last Three Months '
    elif dtype == 'year':
        line = line +  ' Last One Years '
    elif dtype == 'five':
        line = line +  ' Last Five years '
    else:
        line = line +  ' Full Range '

    line = line + '</h3>\n'
#
#--- link to the other plot category
#
    line = line + create_link_names(catg, dtype, mtype, ptype)

    line = line + '<p style="margin-left:35px; margin-right:35px;">'
    line = line + '<em><b>Delta/Yr</b></em> below is a slope of the linear fitting '
    line = line + 'over the data of the period. '
    line = line + '<em><b>Delta/Yr/Yr</b></em> is a slope of the liner fitting '
    line = line + 'over the devivative data of the period. <em><b>Slope</b></em> '
    line = line + 'listed on a linked plot is the slope computed on '
    line = line + 'the last few periods of the  data to show the direction of the trend, '
    line = line + 'and different from that of Delta/Yr.</p>'
    line = line + '<div style="padding-bottom:30px;"></div>'

    line = line + '<div style="text-align:center">\n\n'
    line = line + '<table border=1 cellspacing=2 style="margin-left:auto;margin-right:auto;'
    line = line + 'text-align:center;">\n'
    line = line + '<th>MSID</th><th>&#160;</th><th>Mean</th><th>RMS</th><th>Delta/Yr</th><th>Delta/Yr/Yr</th>'
    line = line + '<th>Unit</th><th>Description</th><th>Limit Violation</th>\n'
#
#--- create a table with one row for each msid
#
    violation_save = []
    for msid in msid_list:
#
#--- check whether plot html file exist
#
        cfile = check_plot_existance(msid, catg, dtype, mtype, ptype)
        if cfile == False:
            continue

        [states, fit_dict] = extract_data(catg, msid, dtype, mtype)
        slen   = len(states)
        try:
            unit  = udict[msid]
            discp = ddict[msid]
#
#--- convert all F and most C temperature to K, exception: if the uint is "C", leave as it is
#
            if unit == 'DEGF':
                unit = 'K'
            elif unit == 'DEGC':
                if msid[:-2].lower() != 'tc':
                    unit = 'K'
        except:
            unit  = '---'
            discp = msid

        xfile = cfile.replace('www\/','')
        ctemp = re.split('\/', cfile)
        xfile = ctemp[-2] + '/' + ctemp[-1]
#
#--- for the case there are more than one state
#
        if slen > 1:
            line = line + '<tr>\n'  
            line = line + '<th rowspan=' + str(slen) + '>'
            line = line + '<a href="'+ xfile + '">' + msid + '</a></th>'

            for k in range(0, slen):
                state = states[k]
                fit_save = fit_dict[state]
                [avg,  std]    = set_avg_std(fit_save[0], fit_save[1])
                [fline, dline] = set_slope_lines(fit_save[2], fit_save[3], \
                                                 fit_save[4], fit_save[5])
#
#--- check violation status; if it is 'na', there is no data
#
                [vnote, color] = create_status(msid, dtype, mtype, state, catg, ytime)
                if color != 'black':
                    violation_save.append([msid, vnote])

                if slen == 1 and state == 'none':
                    state = '&#160;'

                line = line + '<td>' + state    + '</td>'
                line = line + '<td>' + str(avg) + '</td>' 
                line = line + '<td>' + str(std) + '</td>'
                line = line + '<td>' + fline    + '</td>'
                line = line + '<td>' + dline    + '</td>'

                if k == 0:
                    line = line + '<td rowspan=' + str(slen) + '>' + unit  + '</td>'
                    line = line + '<td rowspan=' + str(slen) + '>' + discp + '</td>'

                line = line + '<th style="font-size:90%;color:' + color + ';padding-left:10px;'
                line = line + 'padding-right:10px">' + vnote + '</th>\n</tr>\n'
#
#--- for the case there is only one state
#
        else:
            fit_save = fit_dict[states[0]]
            [avg,  std]    = set_avg_std(fit_save[0], fit_save[1])
            [fline, dline] = set_slope_lines(fit_save[2], fit_save[3], \
                                             fit_save[4], fit_save[5])
            [vnote, color] = create_status(msid, dtype, mtype, 'none', catg, ytime)
            if color != 'black':
                violation_save.append([msid, vnote])

            line = line + '<tr>\n<th><a href="'+ xfile  +  '">' + msid +'</a></th>'
            line = line + '<th>&#160;</th><td>' + str(avg) + '</td><td>' 
            line = line + str(std) + '</td><td>' + fline + '</td>'
            line = line + '<td>' + dline + '</td><td>' + unit +'</td><td>' + discp + '</td>'
            line = line + '<th style="font-size:90%;color:' + color + ';padding-left:10px;'
            line = line + 'padding-right:10px">' + vnote + '</th>\n</tr>\n'

    line = line + '</table>\n'

    line = line + '</div>\n'

    out    = mcf.today_date_display2()
    fout = chs.read_template('html_close', repl=[['#TODAY#', out]])
    
    line = line +  fout
#
#--- category html has the tail of "_main.html"
#
    try:
        name = create_out_name(catg, dtype, mtype, ptype)
        with  open(name, 'w') as fo:
            fo.write(line)
    except:
        pass
#
#--- update violation file; this will be used by the top html page
#
    if mtype == 'mid':
        vout = web_dir + catg + '/violations'
        if len(violation_save) ==  0:
            mcf.rm_files(vout)
        else:
            line = ''
            for ent in violation_save:
                if len(ent[0]) < 8:
                    line = line + ent[0] + '\t\t' + ent[1] + '\n'
                else:
                    line = line + ent[0] + '\t'   + ent[1] + '\n'
    
            with open(vout, 'w') as fo:
                fo.write(line)
        
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def set_slope_lines(b, d, db, dd):

    b  = float(b)
    d  = abs(float(d))
    db = float(db)
    dd = abs(float(dd))
    if (abs(b) > 100) or (abs(b) < 0.001):
        fline = ecf.modify_slope_dicimal(abs(b), abs(d))
        if b < 0:
            fline = '-' + fline
    else:
        fline = '%3.2f +/- %3.2f' % (round(b, 2), round(d, 2))

    fline = check_na_std(fline)

    if (abs(db) > 100) or (abs(db) < 0.001):
        dline = ecf.modify_slope_dicimal(abs(db), abs(dd))
        if db < 0:
            dline = '-' + dline
    else:
        dline = '%3.2f +/- %3.2f' % (round(db, 2), round(dd, 2))

    dline = check_na_std(dline)

    return [fline, dline]

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def set_avg_std(avg, std):
    avg = float(avg)
    std = float(std)
    if abs(avg) > 1000 or abs(avg) < 0.001:
        avg = '%3.3e' % avg
    else:
        avg = '%3.3f' % avg

    if abs(std) > 1000 or abs(std) < 0.001:
        std = '%3.3e' % std
    else:
        std = '%3.3f' % std

    return [avg, std]

        
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def check_na_std(line):

    mc1 = re.search('999',  line)
    mc2 = re.search('99.9', line)
    mc3 = re.search('9.99', line)

    if (mc1 is not None) or (mc2 is not None) or (mc3 is not None):

        atemp = re.split('\+\/\-', line)
        mc2 = re.search('\)', atemp[1])
        if mc2 is not None:
            btemp = re.split('\)', atemp[1])

            line = atemp[0] + '+/-na)' + btemp[1]
        else:
            line = atemp[0] + '+/-na'

    return line

#----------------------------------------------------------------------------------
#-- read fitting results: read fitting results                                   --
#----------------------------------------------------------------------------------

def extract_data(catg, msid, dtype, mtype):
    """
    read fitting results
    input:  catg    --- category of the msids
            msid    --- msid
            dtype   --- data length: week, short, year, five, long
            mtype   --- min, max, med
    output: states  --- a list of possible state
            fit_dict--- a dictionary of states <---> [a, b, d, avg, std, da, db, dd], 
                                                      fitting results and their errors
    """
    sfile = web_dir + catg + '/' + msid.capitalize() + '/Plots/' + msid + '_fit_results'
    #print("Processing: " + sfile)
    print("Processing: " + msid)
    sdata = mcf.read_data_file(sfile)

    states   = []
    fit_dict = {}
    chk = 0
    for ent in sdata:
        atemp = re.split('#', ent)
        btemp = re.split(':', atemp[0])
        if btemp[0] == dtype and btemp[1] == mtype:
            state = btemp[2]
            states.append(state)
            ctemp = re.split(':', atemp[1])
            avg   = ctemp[0]
            std   = ctemp[1]
            b     = ctemp[2]
            d     = ctemp[3]
            da    = ctemp[4]
            db    = ctemp[5]
            dd    = ctemp[6]
            fit_dict[state] = [b, d, avg, std, db, dd]
            chk   = 1
    if chk == 0:
        states.append('none')
        fit_dict['none'] = [0, 0, 0, 0, 0, 0]

    return [states, fit_dict]

#----------------------------------------------------------------------------------
#-- create_out_name: create html page name for given condition                   --
#----------------------------------------------------------------------------------

def create_out_name(catg, dtype, mtype, ptype):
    """
    create html page name for given condition
    input:  catg    --- category of the msids
            dtype   --- data length: week, year, five or long
            mtype   --- min, max, med
            ptype   --- static or inter (interactive)
    output: name    --- html page name (with a full path)
    """
    if ptype == 'static':
        ppart = '_static_'
    else:
        ppart = '_inter_'

    name = web_dir + catg + '/' +  catg.lower() + '_' + mtype + ppart  + dtype +  '_main.html'

    return name

#----------------------------------------------------------------------------------
#-- create_link_names: create html page link code for given condition            --
#----------------------------------------------------------------------------------

def create_link_names(catg, dtype, mtype, ptype):
    """
    create html page link code for given condition
    input:  catg    --- category of the msids
            dtype   --- data length: week, year, five or long
            mtype   --- min, max, med
            ptype   --- static or inter (interactive)
    output: line    --- html link code
    """
    link     = []
    discript = []

    for dtype_t in ('week', 'short', 'year', 'five', 'long'):
        if dtype == dtype_t:
            this = ''
        else:
            this = create_out_name(catg, dtype_t, mtype, ptype)

        if dtype_t == 'week':
            text = 'One Week'
        elif dtype_t == 'short':
            text = 'Three Month '
        elif dtype_t == 'year':
            text = 'One Year'
        elif dtype_t == 'five':
            text = 'Five Year'
        else:
            text = 'Full Range'

        link.append(this)
        discript.append(text)

    for mtype_t in ('min', 'mid', 'max'):
        if mtype == mtype_t:
            this = ''
        else:
            this = create_out_name(catg, dtype, mtype_t, ptype)

        if mtype_t == 'max':
            text = 'Max'
        elif mtype_t == 'min':
            text = 'Min'
        else:
            text = 'Mean'
        link.append(this)
        discript.append(text)

    for ptype_t in ('static', 'inter'):
        if ptype == ptype_t:
                continue

        this = create_out_name(catg, dtype, mtype, ptype_t)

    line = '<table border=1 cellpadding=2><tr>\n'
    for k in range(0, len(link)):
        if link[k] == '':
            line = line + '<th style="color:green;">' +  discript[k] + '</th>\n'
        else:
            slink = link[k].replace(web_dir, '\.\/mta\/MSID_Trends\/')
            line  = line + '<th><a href="' + slink + '">' + discript[k] + '</a></th>\n'

    line = line + '</tr>\n</table>\n'
    line = line + '<div style="padding-bottom:10px;"></div>'

    return line

#----------------------------------------------------------------------------------
#-- check_plot_existance: check whether a html file exist for the given msid and/or interactive plot exists
#----------------------------------------------------------------------------------

def check_plot_existance(msid, catg, dtype, mtype, ptype):
    """
    check whether a html file exist for the given msid and/or interactive plot exists
    input:  msid    --- msid
            dtype   --- week, short, year, five, long
            mtyp    --- mid, min, max
            ptype   --- static or inter
    output: True/False
    """
    if ptype == 'static':
        ppart = '_static_'
    else:
        ppart = '_inter_'

    cfile = web_dir + catg  + '/' + msid.capitalize() + '/' +  msid  + '_' + mtype
    cfile = cfile   + ppart + dtype +  '_plot.html'

    if os.path.isfile(cfile):
        return cfile
    else:
        return False

#----------------------------------------------------------------------------------
#-- create_status: check the status of the msid and return an appropriate comment -
#----------------------------------------------------------------------------------

def create_status(msid, dtype, mtype, state, group,  ytime):
    """
    check the status of the msid and return an appropriate comment
    input:  msid    --- msid
            dtype   --- data type week, short, year, five, long
            mtype   --- mid, min, max
            group   --- group name
            ytime   --- current time
    output: [<comment>, <font color>]
    """
    ftime = ytime + 2
#
#--- read violation status of the msid
#
    if group in sub_group_list:
        tmsid = msid + '_' + group.lower()
    else:
        tmsid = msid

    try:
        out   = ved.read_v_estimate(tmsid, dtype, mtype, state)
    except:
        out   = []

#
#--- if there is no data, tell so and return
#
    if len(out) < 4:
        return ["No Violation Check", 'black']
#
#--- if all entries are "0", no violation
#
    chk = 0
    for k in range(0, 4):
        if out[k] != 0.0:
            chk =1
            break

    if chk == 0:
        return ["No Violation", 'black']
#
#--- if there are violation, create the description and choose a color for it
#
    else:
        line  = ''
        line0 = ''
        line1 = ''
        line2 = ''
        line3 = ''
        color = 'black'
        if out[0] != 0:
            if out[0] < ytime:
                line0 = 'Already Lower Yellow Violation'
                color = '#FF8C00'
            elif out[0] < ftime:
                line0 = "Yellow Lower Violation: " + clean_the_input(out[0])
                color = '#FF8C00'

        if out[1] != 0:
            if out[1] < ytime:
                line1 = 'Already Upper Yellow Violation'
                color = '#FF8C00'
            elif out[1] < ftime:
                line1 = "Yellow Upper Violation: " + clean_the_input(out[1])
                color = '#FF8C00'

        if out[2] != 0:
            if out[2] < ytime:
                line2 = 'Already Lower Red Violation'
                color = 'red'
            elif out[2] < ftime:
                line2 = "Red Lower Violation: " + clean_the_input(out[2])
                color = 'red'

        if out[3] != 0:
            if out[3] < ytime:
                line3 = 'Already Upper Red Violation'
                color = 'red'
            elif out[3] < ftime:
                line3 = "Red Upper Violation: " + clean_the_input(out[3])
                color = 'red'

        if line2 != '':
            line =  line2
            color = 'red'
        else:
            if line0 != '':
                line = line0
                color = '#FF8C00'


        if line3 != '':
            if line != '':
                line = line + '<br />' + line3
                color = 'red'
            else:
                line = line3
                color = 'red'
        else:
            if line1 != '':
                if line != '':
                    line = line + '<br />' + line1
                    if color == 'black':
                        color = '#FF8C00'
                else:
                    line = line1
                    color = '#FF8C00'

        if line == '':
            line = "No Violation"

        return [line, color]

#----------------------------------------------------------------------------------
#-- clean_the_input: check the input is numeric and if so, round to two decimal   -
#----------------------------------------------------------------------------------

def clean_the_input(line):
    """
    check the input is numeric and if so, round to two decimal
    input:  line    --- input quantity
    output: line    --- if it is a numeric value, a value of two decimal, 
                        otherwise, just return the value as it was
    """

    try:
        chk = float(line)
        line = str(ecf.round_up(float(line)))
    except:
        pass

    return line
        
#---------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")

    create_sub_html()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")