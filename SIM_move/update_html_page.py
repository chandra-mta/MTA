#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #  
#       update_html_page.py: update the main html page                                      #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 17, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import time
#
#--- reading directory list
#
path = '/data/mta/Script/SIM_move/Scripts/house_keeping/dir_list'

with  open(path, 'r') as f:
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
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf

detectors = ['ACIS-I','ACIS-S','HRC-I','HRC-S', 'All']

#-----------------------------------------------------------------------------------------
#-- update_html_page: update the summary table of the main html page                    --
#-----------------------------------------------------------------------------------------

def update_html_page():
    """
    update the summary table of the main html page
    input: none but read from <data_dir>/avg_sim_step_size and <data_dir>/avg_sim_move_time
    output:<web_dir>/sim_monitoring.html
    """
    dfile1 = data_dir + 'avg_sim_step_size'
    data1  = mcf.read_data_file(dfile1)
    s_list = []
    for ent in data1:
        atemp = re.split('\s+', ent)
        s_list.append(atemp)

    dfile2 = data_dir + 'avg_sim_move_time'
    data2  = mcf.read_data_file(dfile2)
    m_list = []
    for ent in data2:
        atemp = re.split('\s+', ent)
        m_list.append(atemp)

    line = "<table border=1 cellpadding=1>\n"
    line = line + '<tr><th>From</th><th>To</th><th># Obs</th>'
    line = line + '<th>Time (sec)/ Step</th><th>Average Time</th></tr>\n'
    for k in range(0, 12):
        line = line + '<tr>'
        line = line + '<th>' +  detectors[int(s_list[k][0])] + '</th>'
        line = line + '<th>' +  detectors[int(s_list[k][1])] + '</th>'
        line = line + '<td style="text-align:right">'  +  str(s_list[k][2]) + '</td>'
        line = line + '<td style="text-align:center">' +  str(s_list[k][3]) + '</td>'
        line = line + '<td style="text-align:center">' +  str(m_list[k][2]) + '+/-' 
        line = line + str(m_list[k][3]) + '</td>'
        line = line + '</tr>\n'

    line = line + '</table>\n'


    tfile = house_keeping + 'template.html'
    with open(tfile, 'r') as f:
        out = f.read()

    out = out.replace('#SUMMARY_TABLE#', line)

    ofile = web_dir + 'sim_monitoring.html'
    with open(ofile, 'w') as fo:
        fo.write(out)

#-----------------------------------------------------------------------------------------

if __name__ == "__main__":

    update_html_page()


