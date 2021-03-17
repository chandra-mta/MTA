#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#       mta_script_sub_functions.py: a colleciton of functions to create mta software/script list       #
#                                                                                                       #
#           author: t. isobe (tisobecfa.harvard.edu)                                                    #
#                                                                                                       #
#           last updated:   Jun 02, 2017                                                                #
#                                                                                                       #
#########################################################################################################

import sys
import os
import string
import re
import cgi
import time
import random

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)
#
#--- import a local function
#
sys.path.append("/data/mta/Script/Python_script2.7/")
import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#
#--- setting a couple of parameters
#
header = 'Content-Type: text/html\n\n'

thtml  = 'https://cxc.cfa.harvard.edu/mta_days/mta_script_list'
flev   = '/data/mta/www/mta_script_list'

#-------------------------------------------------------------------------------------------------------
#-- print_main_page: print mta group managed software/script page---------------------------------------
#-------------------------------------------------------------------------------------------------------

def print_main_page():
    """
    print mta group managed software/script page

    """
    data = find_entries('Realtime')
    [rt_text_line, rt_hname, rt_note_save]          = print_link('Realtime',  data)

    data = find_entries('Spacecraft')
    [sc_text_line, sc_hname, sc_note_save]          = print_link('Spacecraft', data)

    data = find_entries('MTA')
    [mta_text_line, mta_hname, mta_note_save]       = print_link('MTA',   data)

    data = find_entries('USINT')
    [usint_text_line, usint_hname, usint_note_save] = print_link('USINT', data)

    data = find_entries('HRC')
    [hrc_text_line, hrct_hname, hrc_note_save] = print_link('HRC', data)
#
#-- print header part of the page 
#

    print header

    print "<html> "

    print "<head> "
    print "<link rel='stylesheet' type='text/css' href='https://cxc.cfa.harvard.edu/mta_days/mta_script_list/house_keeping/style_sheet.css' /> "
    print "<style> "
    print "    td{padding:5px} "
    print "    th{padding:5px text-align:center} "
    print "    span{padding-left:10px} "
    print "</style> "

    print "<title>MTA Group Managed Software/Script List</title> "

    print "<script  src='https://cxc.cfa.harvard.edu/mta_days/mta_script_list/house_keeping/j_module.js'> </script> "

    print "</head> "

#
#-- main part starts here
#

    print "<body> "

    print "<h2 style='background-color:bluecolor:#FAEBD7margin-right:40px'> "
    print "<u>MTA Group Managed  Sofware/Script List</u> "
    print "</h2> "
    print "<div style='padding-bottom:10px'> "
    print "</div> "
#
#--- link to sot job list
#
    print "<p style='padding-bottom:10px'><b>If you like to see a quick reference of SOT jobs, please go to: "
    print "<a href='https://cxc.cfa.harvard.edu/mta/REPORTS/sot_jobs.html' target='blank'>Chandra SOT Job  Page</a>."
    print "</b></p>"

#
#-- print out "Note" if there are some notes
#
    print "<h3><u>Current Concerns</u></h3>"
    if len(rt_hname) == 0 and  len(sc_hname) == 0 and len(mta_hname) == 0 and len(usint_hname) == 0:
        print "<p>None<p>"
    else:
        print "<table border = 1 cell-padding=2>"

        print_note(rt_hname,    rt_note_save,   'rt') 
        print_note(sc_hname,    sc_note_save,   'sc') 
        print_note(mta_hname,   mta_note_save,  'mta') 
        print_note(usint_hname, usint_note_save,'usint') 

        print "</table>";


    print "<div style='padding-bottom:20px'> "
    print "</div> "
    print "<hr /> "
    print "<div style='padding-top:10px'> "
    print "</div> "

#-------------------------------------------------------------------------------------------------------#
#--                            Special Notes                                                          --#
#-------------------------------------------------------------------------------------------------------#

    print "<h3>Notes</h3>"
    print "<ul>"
    print "<li>"
    print "If a title in the following seciton is hilighted by <span style='color:red'>RED</span>,"
    print "this task must be updated by following the steps described in: "
    print "<a href='https://github.com/taldcroft/workflow/blob/master/README.md'>Git/github workflow</a>."
    print "Example steps are shown in: <span style='color:green'>TBA-will be written by BS </span>."
    print "</li>"
    print "</ul><ul>"
    print "<li>"
    print "All CUS Mail related functions were terminated their operation in Spring of 2015."
    print "</li>"
    print "</ul>"

    print "<div style='padding-bottom:20px'> "
    print "</div> "
    print "<hr /> "
    print "<div style='padding-top:20px'> "
    print "</div> "


#-------------------------------------------------------------------------------------------------------#
#--                       Chandra Real Time Related Scripts                                           --#
#-------------------------------------------------------------------------------------------------------#

    print "<h3>Chandra Real Time Related Scripts</h3> "

    print rt_text_line

    print "<div style='padding-top:20px'> "
    print "</div> "
    print "<hr /> "
    print "<div style='padding-top:20px'> "
    print "</div> "



#-------------------------------------------------------------------------------------------------------#
#--                        Other  Spacecraft related scripts                                          --#
#-------------------------------------------------------------------------------------------------------#

    print "<h3>Other Spacecraft Related Scripts</h3> "

    print sc_text_line

    print "<div style='padding-top:20px'> "
    print "</div> "
    print "<hr /> "
    print "<div style='padding-top:20px'> "
    print "</div> "


#-------------------------------------------------------------------------------------------------------#
#--                                MTA related scripts                                                --#
#-------------------------------------------------------------------------------------------------------#


    print "<h3>MTA Related Scripts</h3> "

    print mta_text_line

    print "<div style='padding-top:20px'> "
    print "</div> "
    print "<hr /> "

#-------------------------------------------------------------------------------------------------------#
#--                               USINT related scripts                                               --#
#-------------------------------------------------------------------------------------------------------#


    print "<h3>USINT Related Scripts</h3> "

    print usint_text_line

    print "<div style='padding-top:20px'> "
    print "</div> "
    print "<hr /> "



#-------------------------------------------------------------------------------------------------------#
#--                               HRC related scripts                                                 --#
#-------------------------------------------------------------------------------------------------------#


    print "<h3>HRC Related Scripts</h3> "

    print hrc_text_line

    print "<div style='padding-top:20px'> "
    print "</div> "
    print "<hr /> "


#
#--- closing part
#

    print "<p> "
    print "If you have questions about this page, email to <a href='mailto:tisobe@cfa.harvard.edu'>tisobe@cfa.harvard.edu</a> "
    print "</p> "
    
    print "</body> "
    print "</html> "


#----------------------------------------------------------------------------------------------
#-- find_entries: create list of fies/directory under the "dir"                             ---
#----------------------------------------------------------------------------------------------

def find_entries(dir):
    """
    create list of fies/directory under the "dir"
    ipnt:   dir     --- directory name under /data/mta/www/mta_script_list/
    output: data    --- a list of files and directories
    """

    try:
        cmd  = 'ls -d /data/mta/www/mta_script_list/' + dir + '/* >' + zspace
        os.system(cmd)
        f    = open(zspace, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        mcf.rm_file(zspace)
    except:
        data = []

    if len(data) > 0:
        cleaned = []
        for ent in data:
            mc = re.search('\~', ent)
            if mc is not None:
                continue
            else:
                cleaned.append(ent)
        data = cleaned

    return data

#----------------------------------------------------------------------------------------------
#-- print_link: separate html pages to top and sub directories and print the links          ---
#----------------------------------------------------------------------------------------------

def print_link(uname, indata):

    html_list = []                    #--- save the top level html page names
    dir_name  = []                    #--- save the sub directory names
    note_html = []                    #--- save the name of the html which has note
    note_save = []                    #--- save note cotents
    save_line = ''

    for ent in indata:
#
#--- top level html pages
#
        div   = uname + '/'
        atemp = re.split(div, ent)
        mc    = re.search('.html', ent)
        if mc is not None:
            html_list.append(atemp[1])
        else:
#
#--- create holders for sub directory html pages
#
            if os.path.isdir(ent):
                dir   = atemp[1]
                mc = re.search('Temp', dir)
                if mc is None:
                    dir = dir.replace('\/', '')
                    dir_name.append(dir)

#--- printing top level html page links
#
    if len(html_list) > 0:
        alist = []
        tlist = []
        save_line = save_line + "<ul>"
        for ent in html_list:
            mc = re.search('_template', ent)
            if mc is not None:
                continue

            shtml = thtml + '/' + uname + '/' + ent                  #--- web address
            efile = flev  + '/' + uname + '/' + ent                  #--- physical location

            [line, note, stime] = print_link_sub(shtml, efile)
            alist.append(line)
            tlist.append(stime)
            #save_line = save_line + line

            if note != '' and  note != '\s|\s+':
                note_html.append(shtml)
                note_save.append(note)
        
        myset = set(tlist)
        mlist = list(myset)
        slist = sorted(mlist)
        slist.reverse()
        for ent in slist:
            for m in range(0, len(alist)):
                if ent == tlist[m]:
                    save_line = save_line + str(alist[m])

        save_line = save_line + "</ul>"
#
#--- get sub level html pages
#
    for  dir in dir_name: 
        dh_list = []
        sub_dir =  uname + '/' + dir
        data    =  find_entries(sub_dir)

        div = dir + '/'
        for line in data:
            mc   = re.search('\~$', line)
            if mc is not None:
                continue

            mc   = re.search('.html$', line)
            if mc is not None:
                btemp = re.split(div, line)
                dh_list.append(btemp[1])
#
#--- print sub level html page links
#
#
#--- create the title of the sub directory entries
#
        name  = dir
        name  = name.replace('_', ' ')
        dname = uname + '/' + dir
#
#--- check the directory actually has any entries
#
        if len(dh_list) > 0:
            alist = []
            tlist = []

            save_line = save_line +  "<h3>" + name + "</h3>"
            save_line = save_line +  "<ul>"
            for ent  in dh_list:
                shtml = thtml + '/' + uname + '/' + dir + '/' + ent
                efile = flev  + '/' + uname + '/' + dir + '/' + ent

                [line, note, stime] = print_link_sub(shtml, efile)
                alist.append(line) 
                tlist.append(stime)
                #save_line = save_line + line
                if note != ''and  note != '\s|\s+':
                    note_html.append(shtml)
                    note_save.append(note)
            
            myset = set(tlist)
            mlist = list(myset)
            slist = sorted(mlist)
            slist.reverse()
            for ent in slist:
                for m in range(0, len(alist)):
                    if ent == tlist[m]:
                        save_line = save_line + str(alist[m])


            save_line = save_line + "</ul>"

    return [save_line, note_html, note_save]

#----------------------------------------------------------------------------------------------
#-- print out each html link                                                                ---
#----------------------------------------------------------------------------------------------

def print_link_sub(shtml, efile):
#
#   input: shtml    --- a full html address of the page
#          efile    --- a full physical address of the file
#

#
#--- find the title of the html page it assumes that of between <title> tags
#
    f    = open(efile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    note_save = []
    save_line = ''
    nchk      = 0
    for line in data:
        mc  = re.search('<title>', line)
        if mc is not None:
            atemp = re.split('<title>', line)
            btemp = re.split('<\\title>', atemp[1])
            title = btemp[0]
#
#--- find whether there is any "Note" in this page
#
        mc  = re.search('<h3>Note</h3>', line)
        mc2 = re.search('<!--', line)
        if mc is not None:
            nchk = 1
        elif mc2 is not None:
            continue
        elif nchk == 1:
            mc = re.search('<p>', line)
            if mc is not None:
                nchk = 2
        elif nchk == 2:
            mc = re.search('<\/p>', line)
            if mc is not None:
                break
            note_save.append(line)


    save_line = save_line +  "<li><a href='" + shtml + "'>" + title + "</a>"
#
#--- find the last updated date
#
    atemp = re.split('\s+', time.ctime(os.path.getmtime(efile)))
    mtime = atemp[1] + ' ' + atemp[2] + ', ' + atemp[4]
    mon   = tcnv.changeMonthFormat(atemp[1])
    day   = int(float(atemp[2]))
    year  = int(float(atemp[4]))
    stime = tcnv.convertDateToTime2(year, mon, day)

    save_line = save_line +  "<span style='padding-left:20pxfont-size:90%'>(Last Update: " + mtime + ")</span></li>"
#
#----returning "Note"
#
    note = ''
    if len(note_save) > 0:
        for ent in note_save:
            ent = ent.strip()
            test = ent.replace('\s|\t|\n',"")
            if ent != "None" and ent != "NONE" and ent != "NA" and ent !='na' and ent != '':
                note = note +  ' ' + ent

    return [save_line, note, stime]

#-------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------#

def print_note(hname, note, user):

    for i in range(0, len(hname)):
        atemp = re.split('\/', hname[i])
        btemp = re.split('_', atemp[-1])
        out   = btemp[1]
        for k in range(2, len(btemp)):
            out =  out +'_' + btemp[k]

        out   = out.replace('.html', '')
        print "<tr><th>" + user.upper() + "</th><th><a href='" + hname[i] +"'>" + out + "</a></th><td>" + note[i] + "</td></tr>"



#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    print_main_page()
