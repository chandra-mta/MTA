#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################
#                                                                               #
#       sci_run_print_html.py: print out html pagess                            #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Mar 09, 2021                                       #
#                                                                               #
#################################################################################

import math
import re
import sys
import os
import string
import time
import Chandra.Time
#
#--- reading directory list
#
path = '/data/mta/Script/Interrupt/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- mta common functions
#
import mta_common_functions             as mcf
#
#--- Science Run Interrupt related funcions shared
#
import interrupt_suppl_functions        as itrf

#---------------------------------------------------------------------------------------------
#---  print_each_html_control: html page printing control                                  ---
#---------------------------------------------------------------------------------------------

def print_each_html_control(ifile = 'NA'):

    """
    html page printing control function. 
    input:  ifile    --- the name of the file containing event information
            we also need "./acis_list" which contains a list of acis gif names
            example: 20170907::2017-248:2017-249:2017-250:2017-251
    output: <main_dir>/rad_interrupt.html       if file == 'NA"
            <html_dir>/<evnet>.html
    """
    if ifile != 'NA':
        data = mcf.read_data_file(ifile)
#
#--- first pint indivisula html pages
#
        for ent in data:
                atemp = re.split('\s+', ent)
        
                event = atemp[0]
                start = atemp[1]
                stop  = atemp[2]
                gap   = atemp[3]
                itype = atemp[4]
        
                print_each_html(event, start, stop, gap, itype)
    else:
#
#--- print top pages, auto, manual, hardness, and time ordered
#
        print_sub_html()
#
#---- change permission/owner group of pages
#
    cmd = 'chmod 775 '       + web_dir  + '/*'
    os.system(cmd)
    cmd = 'chgrp mtagroup  ' + web_dir  + '/*'
    os.system(cmd)

    cmd = 'chmod 775 '       + html_dir + '/*'
    os.system(cmd)
    cmd = 'chgrp mtagroup  ' + html_dir + '/*'
    os.system(cmd)

#---------------------------------------------------------------------------------------------
#--- print_each_html: print out indivisual html page                                       ---
#---------------------------------------------------------------------------------------------

def print_each_html(event, start, stop, gap, stop_type):
    """
    create indivisual event html page. 
    input:  event       ---   event name
            start       --- start time
            stop        --- stop time
            gap         --- aount of interrution in sec
            stop_type    --- auto/manual
            example: 20031202  2003:12:02:17:31  2003:12:04:14:27  139.8   auto

            we also need "./acis_list" which contains a list of acis gif names
            example: 20170907::2017-248:2017-249:2017-250:2017-251
    output: html pages
    """
#
#--- modify date formats
#   
    [year1, ydate1] = itrf.dtime_to_ydate(start)
    [year2, ydate2] = itrf.dtime_to_ydate(stop)
#
#--- find plotting range
#
    (pyear_start, period_start, pyear_stop, period_stop, plot_year_start,\
     plot_start, plot_year_stop, plot_stop, pannel_num)  \
                            = itrf.find_collection_period(year1, ydate1, year2, ydate2)
#
#--- check whether we need multiple pannels
#
    pannel_num  = int((plot_stop - plot_start) / 5)
#
#--- choose a template
#
    if year1 < 2011:
        ifile = house_keeping + 'Templates/sub_html_template'

    elif year1 < 2014:
        ifile = house_keeping + 'Templates/sub_html_template_2011'

    elif year1 < 2017:
        ifile = house_keeping + 'Templates/sub_html_template_2014'

    elif year1 < 2020:
        ifile = house_keeping + 'Templates/sub_html_template_2017'

    else:
        ifile = house_keeping + 'Templates/sub_html_template_2020'
#
#--- read the template and start substituting 
#
    data = open(ifile).read()

    data = re.sub('#header_title#',  event,     data)
    data = re.sub('#main_title#',    event,     data)
    data = re.sub('#sci_run_stop#',  start,     data)
    data = re.sub('#sci_run_start#', stop,      data)
    data = re.sub('#interruption#',  gap,       data)
    data = re.sub('#trigger#',       stop_type, data)

    noteN = event + '.txt'
    data = re.sub('#note_name#',     noteN,  data)
#
#--- ACE (NOAA) radiation data
#
    aceData = event + '_dat.txt'
    data = re.sub('#ace_data#',     aceData, data)

    ifile = stat_dir + event + '_ace_stat'
    try:
        stat = open(ifile).read()
        data = re.sub('#ace_table#',    stat,    data)
    
        line =  event + '.png"'
        for i in range(2, pannel_num+1):
            padd = ' alt="main plot" style="width:100%">\n<br />\n<img src = "../Main_plot/' 
            padd = padd + event + '_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#ace_plot#', line , data)
    except:
        pass
#
#---EPHIN/HRC data
#
    ephData = event + '_eph.txt'
    data = re.sub('#eph_data#', ephData, data)

    ifile = stat_dir + event + '_ephin_stat'
    try:
        stat = open(ifile).read()
        data = re.sub('#eph_table#',    stat,    data)
    
        line =  event + '_eph.png"'
        for i in range(2, pannel_num+1):
            padd = ' alt="eph plot" style="width:100%">\n<br />\n<img src = "../Ephin_plot/' 
            padd = padd + event + '_eph_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#eph_plot#', line , data)
    except:
        pass
#
#---GOES data
#
    goesData = event + '_goes.txt'
    data = re.sub('#goes_data#', goesData, data)

    ifile = stat_dir + event + '_goes_stat'
    try:
        stat = open(ifile).read()
        data = re.sub('#goes_table#',    stat,    data)
    
        line =  event + '_goes.png"'
        for i in range(2, pannel_num+1):
            padd = ' alt="goes plot" style="width:100%"> \n<br />\n<img src = "../GOES_plot/' 
            padd = padd + event + '_goes_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#goes_plot#', line , data)
    
        if year1 >= 2011 and year1 < 2020:
            data = re.sub('GOES-11', 'GOES-15', data)
        elif year1 >= 2020:
            data = re.sub('GOES-11', 'GOES-R', data)

    except:
        pass
#
#---XMM data
#
    xmmData = event + '_xmm.txt'
    data = re.sub('#xmm_data#', xmmData, data)

    ifile = stat_dir + event + '_xmm_stat'
    try:
        stat = open(ifile).read()
        data = re.sub('#xmm_table#',    stat,    data)
    
        line =  event + '_xmm.png"'
        for i in range(2, pannel_num+1):
            padd = ' alt="xmm plot" style="width:100%"> \n<br />\n<img src = "../XMM_plot/' 
            padd = padd + event + '_xmm_pt' + str(i) + '.png '
            line = line + padd
    
        data = re.sub('#xmm_plot#', line , data)
    except:
        pass
#
#--- ACIS
#
    alist = mcf.read_data_file('./acis_list')
    if len(alist) == 0:
        print("ACIS plot data list: './acis_list' does not exist. Stopping the process!")
        exit(1)

    achk = 0
    for ent in alist:
        mc = re.search(event, ent)
        if mc is not None:
            atemp = re.split('::', ent)
            blist = re.split(':', atemp[1])
            achk = 1
            break
    if achk > 0:
        k = 0
        aline = ''
        for ent in blist:
            aline = aline + "<img src='http://acisweb.mit.edu/asc/txgif/gifs/"
            aline = aline + ent + ".gif' style='width:45%; padding-bottom:30px;'>\n"
            k += 1
            if k % 2 == 0:
                aline = aline + '<br />\n'
    
        data = re.sub('#acis_plot#', aline, data)
    else:
        data = re.sub('#acis_plot#', '', data)
#
#--- print the page
#
    ofile = web_dir + 'Html_dir/' + event + '.html'
    with open(ofile, 'w') as fo:
        fo.write(data)

#----------------------------------------------------------------------------------------
#--- print_each_pannel: create each event pannel for the top html pages                 ---
#----------------------------------------------------------------------------------------

def print_each_pannel(event, start, stop, gap, stop_type):
    """
    create each event pannel for the top html pages. 
    input:  event       ---   event name
            start       --- start time
            stop        --- stop time
            gap         --- aount of interrution in sec
            stop_type    --- auto/manual
            out         --- the name of the output file
    output: line        --- part crated
    """
    atemp = re.split(':', start)
    tyear = float(atemp[0])

    line = '<li style="text-align:left;font-weight:bold;padding-bottom:20px">\n'
    line = line + '<table style="border-width:0px"><tr>\n'
    line = line + '<td>Science Run Stop: </td><td> ' 
    line = line + start + '</td><td>Start:  </td><td>' + stop + '</td>'
    line = line + '<td>Interruption: </td><td> %4.1f ks</td><td>%s</td>\n' %(float(gap), stop_type)
    line = line + '</tr></table>\n'

    address = html_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '.html"><img src="./Intro_plot/' 
    line = line + event + '_intro.png" alt="intro plot" style="width:100%;height:20%"></a>\n'

    address = wdata_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '_dat.txt"> ACE RTSW EPAM Data </a>\n'

    if tyear < 2014:
        line = line + '<a href="' + address + event + '_eph.txt"> Ephin Data </a>\n'
    else:
        line = line + '<a href="' + address + event + '_eph.txt"> HRC Data </a>\n'

    line = line + '<a href="' + address + event + '_goes.txt"> GOES Data </a>\n'
    if tyear >= 2017:
        line = line + '<a href="' + address + event + '_xmm.txt"> XMM Data </a>\n'

    address = note_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '.txt"> Note </a>\n'

    address = html_dir.replace('/data/mta_www/', '/mta_days/')
    line = line + '<a href="' + address + event + '.html"> Plots </a>\n'

    line = line + '<br />\n'
    line = line + '<div style="padding-bottom:10px">\n</div>\n'
    line = line + '</li>\n'

    return line

#----------------------------------------------------------------------------------------
#--- print_sub_html: create auto/manual/hardness/time ordered html pages                ---
#----------------------------------------------------------------------------------------

def print_sub_html():

    """
    create auto/manual/hardness/time ordered html page. 
    input: none, but data are read from house_keeping and stat_dir 
    output: auto_shut.html etc
    """
#
#--- read the list of the interruptions
#
    ifile       = data_dir + 'all_data'
    timeOrdered = mcf.read_data_file(ifile)

    auto_list      = []
    manual_list    = []
    hardness_list  = []
#
#--- create list of auto, manual, and hardness ordered list. time ordered list 
#--- is the same as the original one
#
    [auto_list, manual_list, hardness_list] = create_ordered_list(timeOrdered)
#
#--- print out each html page
#
    for ptype in ('auto_shut', 'manual_shut', 'hardness_order', 'time_order'):
#
#--- read the template for the top part of the html page
#
        line = house_keeping + 'Templates/main_html_page_header_template'
        data = open(line).read()
#
#---- find today's date so that we can put "updated time in the web page
#
        today = time.strftime('%Y-%m-%d', time.gmtime())
        data  = re.sub("#DATE#", today, data)
        oline = data

        oline = oline + '<table style="border-width:0px">\n'
        oline = oline + '<tr><td>\n'

        if ptype == 'auto_shut':
            oline = oline + auto_html()
            inList = auto_list

        elif ptype == 'manual_shut':
            oline = oline + manula_html()
            inList = manual_list

        elif ptype == 'hardness_order':
            oline = oline + hardness_html()
            inList = hardness_list

        else:
            oline = oline + time_order_html()
            inList = timeOrdered

        oline = oline + '</table>\n'
        oline = oline + '<ul>\n'
#
#--- now create each event pannel
#
        for ent in inList:
            atemp    = re.split('\s+|\t+', ent)
            event    = atemp[0]
            start    = atemp[1]
            stop     = atemp[2]
            gap      = atemp[3]
            stop_type = atemp[4]

            oline = oline + print_each_pannel(event, start, stop, gap, stop_type)

        oline = oline + '</ul>\n'
        oline = oline + '</body>'
        oline = oline + '</html>'

        fout = web_dir + ptype +'.html'
        with open(fout, 'w') as fo:
            fo.write(oline)

#---------------------------------------------------------------------------------------
#--- auto_html: print a header line for auto shutdown case                            ---
#---------------------------------------------------------------------------------------

def auto_html():

    line = '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------
#--- manula_html: print a header line for manual shotdown case                        ---
#---------------------------------------------------------------------------------------

def manula_html():

    line = '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------
#--- hardness_html: print a header line for hardness ordered case                    ---
#---------------------------------------------------------------------------------------

def hardness_html():

    line = '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------
#--- time_order_html: print a header line for time ordered case                      ---
#---------------------------------------------------------------------------------------

def time_order_html():

    line = '<em class="lime" style="font-weight:bold;font-size:120%">\n'
#    line = line + '<a href="time_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Time Ordered List</em>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="auto_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Auto Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="manual_shut.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Manually Shutdown List</a>\n'
    line = line + '</td><td>\n'
    line = line + '<a href="hardness_order.html" style="font-weight:bold;font-size:120%">\n'
    line = line + 'Hardness Ordered List</a>\n'
    line = line + '</td><td>\n'

    return line

#---------------------------------------------------------------------------------------
#--- create_ordered_list: create lists of auto/manual shut down and harness ordered list
#---------------------------------------------------------------------------------------

def create_ordered_list(data):
    """
    create lists of auto, manual, and hardness ordered events. 
    input:  data        --- e.g.: 20031202  2003:12:02:17:31 2003:12:04:14:27 139.8  auto
    output: auto_list       --- a list of auto shutdown
            manual_list     --- a list of manual shutdown
            hardness_list   --- a list of events sorted by hardness
    """
    auto_list     = []
    manual_list   = []
    hardness_list = []

    hardList      = []

    for ent in data:
#
#--- extract auto and manual entries
#
        m = re.search('auto',   ent)
        n = re.search('manual', ent)
        if m is not None:
            auto_list.append(ent)
        elif n is not None:
            manual_list.append(ent)
#
#--- hardness list bit more effort. find p47/p1060 value from stat file
#
        atemp    = re.split('\s+|\t+', ent)
        statData = stat_dir + atemp[0] + '_ace_stat'
        sdata    = mcf.read_data_file(statData)

        if len(sdata) == 0:
            continue

        for line in sdata:
            m = re.search('p47/p1060', line)
            if m is not None:
                btemp = re.split('\s+|\t+', line)
                hardList.append(btemp[2])
#
#--- zip the hardness list and the original list so that we can sort them by hardness
#
    tempList = zip(hardList, data)
    tempList = sorted(tempList)
#
#--- extract original data sorted by the hardness
#
    for ent in tempList:
        hardness_list.append(ent[1])

    return [auto_list, manual_list, hardness_list]

#---------------------------------------------------------------------------------------------

if __name__ == '__main__':
#
#---- plotting the data and create html pages
#
    if len(sys.argv) > 1:
        ifile = sys.argv[1]
    else:
        ifile = input('Please put the intrrupt timing list (if "NA", print all top level html pages: ')
    print_each_html_control(ifile)

