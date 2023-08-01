#!/proj/sot/ska3/flight/bin/python

#######################################################################################
#                                                                                     #
#       create_html_page.py: create indivisual html pages for all msids in database   #
#                                                                                     #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                 #
#                                                                                     #
#           last update: Feb 01, 2021                                                 #
#                                                                                     #
#######################################################################################

import sys
import os
import string
import re
import numpy
import getopt
import os.path
import time
import astropy.io.fits  as pyfits
import argparse
import getpass
import glob
#
#--- read argv
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append("/data/mta4/Script/Python3.10/MTA")
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import create_html_suppl        as chs  #---- supplemental functions to crate html page
#
#--- set a temporary file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- other settings
#
na     = 'na'
#
#--- read category data
#
cfile         = house_keeping + 'sub_html_list_all'
category_list = mcf.read_data_file(cfile)
#
#---  get dictionaries of msid<-->unit and msid<-->description
#
[udict, ddict] = ecf.read_unit_list()
#
#---  a list of groups excluded from interactive page creation
#
efile = house_keeping + 'exclude_from_interactive'
eout  = mcf.read_data_file(efile)
exclude_from_interactive = []
for ent in eout:
    atemp = re.split('\s+', ent)
    exclude_from_interactive.append(atemp[0])
#
#--- the top web page address
#
web_address = 'https://' + web_address
#
#--- alias dictionary
#
afile  = house_keeping + 'msid_alias'
data   = mcf.read_data_file(afile)
alias  = {}
alias2 = {}
for ent in data:
    atemp = re.split('\s+', ent)
    alias[atemp[0]]  = atemp[1]
    alias2[atemp[1]] = atemp[0]

#------------------------------------------------------------------------------------
#-- create_html_page: create indivisual html pages for all msids in database       --
#------------------------------------------------------------------------------------
"""
def create_html_page(msid_list='', ds='all', ms='all'):
"""
def create_html_page(msid_list=None, ds=None, ms=None):
    """
    create indivisual html pages for all msids in database
    input:  msid_list   --- a name of msid_list to be run. if "", 
                            <house_keeping>/msid_list is used
            ds          --- data set name. if 'all', ['week', 'short', 'year', 'five', 'long'] is used.
            ms          --- category name. if 'all', ['mid', 'min', max'] is used.
    output: <web_dir>/<msid>_plot.html etc
    """
#
#--- read mta created msids
#
    ifile = house_keeping + 'msid_grad_comp'
    out   = mcf.read_data_file(ifile)
    mta_msids = []
    for ent in out:
        atemp = re.split('\s+', ent)
        mta_msids.append(atemp[0])
#
#--- set which data set to run
#
    if ds == None:
        data_sets = ['week', 'short', 'year', 'five', 'long']
    else:
        data_sets = ds
    """
    if ds == 'all':
        data_sets = ['week', 'short', 'long']
    else:
        data_sets = [ds]
    """
#
#--- set which category of plots to create
#
    if ms == None:
        cat_sets = ['mid', 'min', 'max']
    else:
        cat_sets = ms
    """
    if ms == 'all':
        cat_sets = ['mid', 'min', 'max']
    else:
        cat_sets = [ms]
    """

    print('Data sets: '  + str(data_sets) + ' : ' + 'Category: ' + str(cat_sets))
#
#--- clean out future estimate direcotry
#
    cmd = 'rm -rf ' + web_dir + 'Future/* 2>/dev/null'
    os.system(cmd)
#
#--- get a list of msids (and the group name)
#
    """
    if msid_list == "":
        mfile = house_keeping + 'msid_list'
    else:
        mfile = house_keeping + msid_list

        if not os.path.isfile(mfile):
            mfile = house_keeping + 'msid_list'
    """
    if msid_list == None:
        mfile= house_keeping + 'msid_list_all'
    else:
        mfile = house_keeping + msid_list

    data  = mcf.read_data_file(mfile)

    msid_list  = []
    group_list = []
    gchk       = ''
    g_dict     = {}
    m_save     = []

    for out in data:
        if out[0] == '#':
            continue

        try:
            [msid, group] = re.split('\s+',  out)
        except:
            atemp = re.split('\s+', out)
            msid  = atemp[0]
            group = atemp[1]

        msid_list.append(msid)
        group_list.append(group)

        if gchk == "":
            gchk = group
            m_save.append(msid)

        elif gchk != group:
            g_dict[gchk] = m_save
            m_save = [msid]
            gchk   = group

        else:
            m_save.append(msid)

    if len(m_save) > 0:
        g_dict[group] = m_save

    for k in range(0, len(msid_list)):
        msid  = msid_list[k]
        group = group_list[k]

        print('Processing: ' + msid + ' of ' + group)
#
#--- try to find the unit of the msid
#
        try: 
            unit    = udict[msid]
            descrip = ddict[msid]
        except:
            unit    = ''
            descrip = ''
#
#--- check whether the output directries exist; p_dir is the directory to save png files
#
        [p_dir, p_dir2]  = check_directories(msid, group)
#
#--- check which plot files in the directory
#
        """
        for dtype in ['week', 'short', 'year', 'five', 'long']:
            for mtype in ['mid', 'min', 'max']:
        """
        for dtype in data_sets:
            for mtype in cat_sets:
                hpart = p_dir + msid + '_' + dtype + '_'  + mtype
                """
                cmd = 'ls ' +  hpart + '*.png > ' + zspace + ' 2>&1'
                os.system(cmd)
                data = mcf.read_data_file(zspace, remove=1)
                """
                data = glob.glob(f"{hpart}*.png")

                trend_list = []
                dev_list   = []
#
#--- if there is no plot, just copy no_data.png
#
                if len(data) < 1:
                    hfile = hpart + '.png'
                    cmd = 'cp ' + house_keeping + 'no_data.png ' + hfile
                    ##os.system(cmd)
                    trend_list.append(hfile.replace(p_dir, p_dir2))

                    hfile = hpart + '_dev.png'
                    cmd = 'cp ' + house_keeping + 'no_data.png ' + hfile
                    ##os.system(cmd)
                    dev_list.append(hfile.replace(p_dir, p_dir2))
#
#--- otherwise, find all "states" data for this set of the plots
#
                else:
                    for ent in data:
                        mc = re.search('_dev.png', ent)
                        if mc is not None:
                            dev_list.append(ent.replace(p_dir, p_dir2))
                        else:
                            trend_list.append(ent.replace(p_dir, p_dir2))
#
#--- create html page; g_dict contains a list of msids of that group

                create_plot_html_page(msid, g_dict[group], group, descrip,\
                                          trend_list, dev_list,  dtype, mtype, mta_msids)

#------------------------------------------------------------------------------------
#-- check_directories: check the existances of directories. if not, create them   ---
#------------------------------------------------------------------------------------

def check_directories(msid, group):
    """
    check the existances of directories. if not, create them
    input:  msid    --- msid
            group   --- group name
    output: p_dir   --- directries created if there were not before
            p_dir2  --- wed address to the directory
            
    """
    p_dir  = web_dir + group + '/'
    p_dir2 = web_address + group + '/'
    cmd = 'mkdir -p ' + p_dir
    os.system(cmd)

    p_dir  = p_dir  + msid.capitalize() + '/'
    p_dir2 = p_dir2 + msid.capitalize() + '/'
    cmd = 'mkdir -p ' + p_dir
    os.system(cmd)

    p_dir  = p_dir  + 'Plots/'
    p_dir2 = p_dir2 + 'Plots/'
    cmd = 'mkdir -p ' + p_dir
    os.system(cmd)

    return [p_dir, p_dir2]

#----------------------------------------------------------------------------------
#-- create_plot_html_page: create a html page to display the trend plot          --
#----------------------------------------------------------------------------------

def create_plot_html_page(msid, msid_list, group, descrip, trend_list, dev_list, dtype, mtype, mta_msids):
    """
    create a html page to display the trend plot
    input:  msid        --- msid
            msid_list   --- the list of msids in the group
            group       --- group name to which msid belongs
            descrip     --- description of the msid
            trend_list  --- a list of trend plot files
            dev_list    --- a list of deviation plot files
            dtype       --- data type, week, short, year, five, or long
            mtype       --- data type, mid, min, max
            mta_msids   --- a list of mta created msids
    output: plot <web_dir>/<msid>_plot.html
    """
#
#--- read javascript file
#
    jscript = chs.read_template('java_script_deposit')
#
#--- set web page names including link back pages
#
    [tweb, hname, other, other_list] = set_link_htmls(group, msid, dtype, mtype)
#
#--- pop up limit table web address
#
    file_name = web_address + group +  '/Limit_table/' + msid + '_limit_table.html'
#
#--- start creating html page
#
    repl = [["#MSID#",  msid.upper()], ["#JAVASCRIPT#", jscript], ["#STYLE#", '']]
    out = chs.read_template('html_head', repl )

    out = out + '<div style="float:right;padding-right:50px;">'
    out = out + '<a href="' + tweb + '" '
    out = out + 'style="text-align:right"><b>Back to ' + group + ' Page</b></a><br />\n'
    out = out + '<b><a href = "' + web_address + 'mta_trending_main.html">Back To Top</a><br />\n'
#
#--- interactive/static page link back
#
    out = out + '<a href="'  + other  + '" style="text-align:right">'
    out = out + '</a><br />\n'
    out = out + '<b><a href="javascript:popitup(\'' + web_address 
    out = out + '/how_to_create_plots.html\')" style="text-align:right">'
    out = out + 'How the Plots Are Created</a></b><br />\n'
#
#--- prev and next msid
#
    out = out + make_msid_link(msid, msid_list, group,  dtype, mtype)

    out = out + '</div>\n'
#
#--- title of the page 
#
    out = out + set_title(msid, descrip, dtype, mtype)
#
#--- popup limit table link
#
    out = out + '<div style="paddng-top:10px"><h3>'
    out = out + 'Open <a href="javascript:popitup(\'' + file_name + '\')" '
    out = out + 'style="text-align:right">Limit Table</a>.'
    out = out + '</h3>\n'
    out = out + '</div>\n'
#
#--- link to the other type of length plots
#
    out = out + create_period_link(other_list, msid, dtype, mtype)

    for plotname in trend_list:
        out = out + '<img src="' + plotname + '" width=80%>'
        out = out + '<br />\n'
#
#--- msid is mta created one, don't put the interactive page link
#
    if msid in mta_msids:
        out = out + '<br><br>\n'
    else:
        phpfile  = web_address + "Interactive/msid_data_interactive.php"
        int_note = web_address + 'interactive_note.html'
    
        out = out + '<div style="padding-bottom:10px;font-size:90%;">\n';
        if msid.lower() in exclude_from_interactive:
            out = out + '<h3>This Data Set Cannot Produce an Interactive Plot</h3>\n'
        else:
            out = out + '<h3>Create an Interactive Plot ('
            out = out + '<a href="javascript:popitup(\'' + int_note + '\')" '
            out = out + 'style="text-align:right">Usage Note</a>'
            out = out + ')</h3>\n'
            out = out + '<form method="post" action=' + phpfile + '>\n'
            out = out + '<b>Starting Time:</b> <input type="text" name="tstart"  size=20>\n'
            out = out + '<b>Stopping Time:</b> <input type="text" name="tstop"  size=20>\n'
            out = out + '<b>Bin Size:</b>      <input type="text" name="binsize"  '
            out = out + 'value=300.0 size=10>\n '
    
            out = out + '<b>Data Type:</b>\n '
            out = out + '<select id="mstype", name="mstype">\n'
            if mtype == 'mid':
                out = out + '   <option value="mid" selected>Mean</option>\n'
            else:
                out = out + '   <option value="mid">Mean</option>\n'
    
            out = out + '   <option value="med">Median</option>\n'
            if mtype == 'min':
                out = out + '   <option value="min" selected>Minimum</option>\n'
            else:
                out = out + '   <option value="min">Minimum</option>\n'
            if mtype == 'max':
                out = out + '   <option value="max" selected>Maximum</option>\n'
            else:
                out = out + '   <option value="max">Maximum</option>\n'
            out = out + '</select>\n'

        out = out + '<input type="hidden" name="dtype" value="' + dtype + '">\n'
        out = out + '<input type="hidden" name="mtype" value="' + mtype + '">\n'
        out = out + '<input type="hidden" name="msid"  value="' + msid  + '">\n'
        out = out + '<input type="hidden" name="group" value="' + group + '">\n'
    
        out = out + '</br><span style="text-align:right;"><input type=submit '
        out = out + 'name="submit" value="Submit"></span>\n'
        out = out + '<br />\n'
        out = out + '</form>\n'
    out = out + '</div>\n'
#
#--- add the derivative plot
#
    out = out + '<h3>Derivative Plot</h3>\n'
    for ent in dev_list:
        out = out + '<img src="' + ent + '" width=80%>'
        out = out + '<br />'
#
#--- add the link to other plots in a table format
#
    [lout, gname] = get_group_names(msid, group,  dtype, mtype)
    if lout != '':
        out = out + '<h3>Other msids in this group: ' + gname + '</h3>'
        out = out + lout
#
#--- close html page
#
    date = mcf.today_date_display2()
    out  = out + chs.read_template('html_close', repl=[['#TODAY#', date]])
#
#--- write out the html data
#
    with open(hname, 'w') as fo:
        fo.write(out)

#----------------------------------------------------------------------------------
#-- set_link_htmls: create the main html name and other link back html names     --
#----------------------------------------------------------------------------------

def set_link_htmls(group, msid, dtype, mtype):
    """
    create the main html name and other link back html names
    input:  group   --- group name
            msid    --- msid
            dtype   --- data type: week, short, year, five, long
            mtype   --- data type: mid, min, max
    output: tweb    --- top web page link
            hname   --- main html name
            other   --- counter part of hname (static/interactive)
            other_list  --- a list of other html page links
    """
    insert1 = '_static'
    insert2 = '_inter'
#
#--- check whether the directories exist
#
    odir   = web_dir + group
    o_dir  = odir  + '/' + msid.capitalize() + '/'
    cmd    = 'mkdir -p ' + o_dir
    os.system(cmd)

    odir2  = web_address + group
    o_dir2 = odir2  + '/' + msid.capitalize() + '/'
#
#--- top web page name to back to
#
    if group.lower() == 'ephkey_l1':
        tgroup = 'compephkey'
    else:
        tgroup = group.lower()

    tweb = web_address + group.capitalize() + '/' + tgroup.lower()  + '_' + mtype
    tweb = tweb + insert1 + '_' + dtype + '_main.html'
#
#--- other html pages
#
    hname  = o_dir  + msid + '_' + mtype + insert1 + '_' + dtype + '_plot.html'
    other  = o_dir  + msid + '_' + mtype + insert2 + '_' + dtype + '_plot.html'
    other_list = []

    for ctype in ['week', 'short', 'year', 'five', 'long']:

        if ctype != dtype:
            ohtml = o_dir2  + msid + '_' + mtype + insert1 + '_' + ctype + '_plot.html'
            other_list.append(ohtml)

    return [tweb, hname, other, other_list]

#----------------------------------------------------------------------------------
#-- set_title: create the title of the page                                      --
#----------------------------------------------------------------------------------

def set_title(msid, descrip, dtype, mtype):
    """
    create the title of the page
    input:  msid    --- msid
            descrip --- description of this msid
            dtype   --- week, short, year, five, long
            mtype   --- mid, min, max
    output: out     --- the title of the page
    """
    out = '<h2>'

    if descrip == '':
        out = out + msid.upper()
    else:
        out = out + msid.upper() + ' (' + descrip.upper() + ')' 

    out = out + '<br /> Static Version: '

    if mtype == 'min':
        out = out + 'Min  ---'
    elif mtype == 'max':
        out = out + 'Max  ---'
    else:
        out = out + 'Mean ---'

    if dtype == 'week':
        out = out + 'One Week Plot\n'
    elif dtype == 'short':
        out = out + 'Last Three Month Plot\n'
    elif dtype == 'year':
        out = out + 'Last One Year Plot\n'
    elif dtype == 'five':
        out = out + 'Last Five Year Plot\n'
    else:
        out = out + 'Full Range Plot\n'

    out = out + '</h2>\n'

    return out

#----------------------------------------------------------------------------------
#-- make_msid_link: create links to the previous and the next msid               --
#----------------------------------------------------------------------------------

def make_msid_link(msid, msid_list, group,  dtype, mtype):
    """
    create links to the previous and the next msid
    input:  msid        --- msid
            msid_list   --- a list of msid in the group
            group       --- a group name
            dtype       --- week, short, year, five, long
            mytpe       --- mid, min, max
    output: line        --- links in html format
    """
    ltot = len(msid_list)
    if ltot == 0:
        return ''
#
#--- find the position of the msid in the list
#
    pos = 0
    for k in range(0, ltot):
        if msid_list[k] == msid:
            pos = k
            break

    main_msid = '<span style="color:green;">' + msid + '</span>\n'
#
#--- create the link to the previous msid
#
    try:
        if pos-1 < 0:
            pline = ''
        else:
            prev  = msid_list[pos-1]
            plink = web_address + group + '/' + prev.capitalize() + '/' + prev
            plink = plink + '_' + mtype + '_static_' + dtype + '_plot.html'
            pline = '<a href="' + plink + '">' + prev + '</a> &lt;&lt;  '
    except:
        pline = ''
#
#--- create the link to the next msid
#
    try:
        if pos+1 > ltot:
            nline = ''
        else:
            if pos == 0:
                next = msid_list[1]
            else:
                next = msid_list[pos+1]

            nlink = web_address + group + '/' + next.capitalize() + '/' + next 
            nlink = nlink + '_' + mtype + '_static_' + dtype + '_plot.html'
            nline = '  &gt;&gt; <a href="' + nlink + '">' + next + '</a>\n' 
    except:
        nline = ''
#
#--- now create the html code
#
    line = '<h3 style="float:right;text-align:right;font-size:90%;">\n'

    if pos == 0:
        line = line +  main_msid +  nline

    elif pos == ltot-1:
        line = line + pline + main_msid

    else:
        line = line + pline + main_msid +  nline

    line = line + '</h3>\n'

    return line

#----------------------------------------------------------------------------------
#-- create_period_link: create a table to list links to  different period length plots 
#----------------------------------------------------------------------------------

def create_period_link(other_list, msid, dtype, mtype):
    """
    create a table to list links to  different period length plots
    input:  ohter_list  --- a list of path to the other html page
            msid        --- msid
            dtype       --- data type: week, short, year, five, long
            mtype       --- mid, min, or max
    output: out         --- html code of the table
    """
    out = ''
    out = out + '<table border=1 cellspacing=2>\n'
    out = out + '<tr>\n'

    for ent in ['week', 'short', 'year', 'five', 'long']:
        chk = 0
        for elink in other_list:
            mc = re.search(ent, elink)
            if mc is not None:
                chk = 1
                break

        if ent == 'week':
            name = 'One Week Plot'
        elif ent == 'short':
            name = 'Three Month Plot'
        elif ent == 'year':
            name = 'One year Plot'
        elif ent == 'five':
            name = 'Five Year Plot'
        elif ent == 'long':
            name = 'Full Range'
        else:
            continue

        if chk == 1:
            out = out + '<td style="text-align:center;width:20%;white-space:nowrap;">'
            out = out + '<a href="' + elink + '">' + name + '</a></td>\n'
        else:

            out = out + '<td style="text-align:center;width:20%;">'
            out = out + '<b style="color:green;white-space:nowrap;">' 
            out = out + name + '</b></td>\n'
        llink = elink
#
#--- create links to mid, min, or max of the same dtype
#
    atemp = re.split('\/', llink)
    lpath = ''
    for ent in atemp[:-1]:
        lpath = lpath + ent + '/'

    for ent in['min', 'mid', 'max']:
        chk = 0
        if ent == mtype:
            chk = 1

        if ent == 'mid':
            name = 'Mean'
        elif ent == 'min':
            name = 'Min'
        elif ent == 'max':
            name = 'Max'
        if chk == 0:
            llink = lpath + msid + '_' + ent + '_static_' + dtype + '_plot.html'
            part  = '<a href="' + llink + '">' + name + '</a>'
        else:
            part  = '<span style="color:green;">' + name +  '</span>'

        out = out + '<td style="text-align:center;width:20%;white-space:nowrap;">'
        out = out + part  + '</td>\n'

    out = out + '</tr>\n'
    out = out + '</table>\n'
    out = out + '<div style="padding-bottom:15px;"></div>\n';

    return out

#----------------------------------------------------------------------------------
#-- get_group_names: create a table with links to other msids in the same group  --
#----------------------------------------------------------------------------------

def get_group_names(msid, group, dtype, mtype):
    """
    create a table with links to other msids in the same group
    input:  msid    --- msid
            group   --- group name
            dtype   --- week, short, year, five, long
            mtype   --- mid, min, max
    output: line    --- a link list in html table format
    """
#
#--- find which group this msid belongs to and then find all other msids in this group
#
    [group_id, group_list] = find_group_names(msid)
#
#--- create the table fo these msids with links to the plots
#
    nrow  = 0
    k     = 0
    if len(group) > 0:
        cname = group.capitalize()
        gname = '<a href="' + web_address + group.capitalize() + '/'  
        gname = gname + group.lower() + '_' + mtype + '_static_'
        gname = gname +  dtype   + '_main.html">' + group.upper() + '</a>'

        line = '<table border=1 cellpadding=3>\n'
        for ent in group_list:
#
#--- make the main msid not clickable
#
            tchk = 0
            ctemp = re.split('_plot.html', ent)
            if ctemp[0] == msid:
                tchk = 1

            ment  = ctemp[0]                #--- msid of the targeted link

            if k == 0:
                line = line + '<tr>'
#
#--- create link html address
#
            pname = ment + '_' + mtype + '_static_' + dtype + '_plot.html'

            line = line + '<td style="text-align:center">'
            if tchk == 1:
                line = line + '<b style="color:green;">' + msid + '</b></td>\n'
            else:
                line = line + '<a href="' + web_address  + cname + '/' 
                line = line + ment.capitalize() +  '/' + pname + '">' 
                line = line + ctemp[0] + '</a></td>\n'
#
#--- 10 entries per row
#
            if k >= 11:
                line = line + '</tr>\n'
                k    = 0
                nrow = 1
            else:
                k += 1
#
#--- filling up the empty cells
#
        chk = 0
        if (nrow > 0) and (k > 0):
            for m in range(k, 12):
                line = line + '<td>&#160;</td>\n'
                chk = 1
        else:
            chk = 1

        if chk == 1:
            line = line + '</tr>\n'
            line = line + '</table>\n'

    else:
        gname = ''
        line = ''

    return [line, gname]

#----------------------------------------------------------------------------------
#-- find_group_name: return a list of msids which belongs to the group with the given msid
#----------------------------------------------------------------------------------

def find_group_names(msid):
    """
    return a list of msids which belongs to the group with the given msid
    input:  msid        --- misd 
    output: group_id    --- a group name
            group_list  --- a list of msids belong to the group
    """
    group_id    = 'na'
    group_list = []

    test       = msid + '_plot.html'

    for ent in category_list:
        mc = re.search(test, ent)

        if mc is not None:
            atemp      = re.split('::', ent)
            group_id   = atemp[0].lower()
            group_list = re.split(':',  atemp[1])

            if test in group_list:
                break
            else:
                group_id   = 'na'
                group_list = []
                continue

    return [group_id, group_list]

#------------------------------------------------------------------------------------

if __name__ == '__main__':
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")

    parser = argparse.ArgumentParser()

    parser.add_argument('-p','--period',help='Process specific time length. If empty defaults to all.', \
                        action="extend",nargs='*',type=str, choices=['week', 'short', 'year', 'five', 'long'])
    parser.add_argument('-c','--category',help='Choose category of values to show in plot. If empty defaults to all.', \
                        action="extend",nargs='*',type=str, choices=["mid","min",'max"'])
    parser.add_argument("-m","--msid_list",help="File name of msid list to use from housekeeping. Defaults to msid_list_all",type=str)

    args = parser.parse_args()
    create_html_page(args.msid_list,ds=args.period,ms=args.category)


#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")
