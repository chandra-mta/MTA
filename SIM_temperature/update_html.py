#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#       update_html.py: updating html pages                                                 #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Jul 19, 2023                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import time
import operator
import math
import getpass
import glob

#
#--- reading directory list
#
path = '/data/mta/Script/SIM/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append("/data/mta4/Script/Python3.10/MTA/")
#
#--- import several functions
#
import mta_common_functions   as mcf    #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------
#-- update_html: check whether the update is needed and if so, run the update        ---
#---------------------------------------------------------------------------------------

def update_html(update):
    """
    check whether the update is needed and if so, run the update
    input:  update  --- if it is 1, run the update without chekcing the file exist or not
    output: none, but updated html pages (in <web_dir>)
    """
#
#--- find today's date
#
    today = time.localtime()
    year  = today.tm_year
#
#--- if update is asked, just run the update
#
    if update > 0:
        run_update(year)
#
#--- otherwise, find the last update, and if needed, run the update
#
    else:
        out = ' '.join(glob.glob(f"{web_dir}*.html"))
#
#--- checking the file existance (looking for year in the file name)
#
        mc    = re.search(str(year), out)

        if mc is None:
            run_update(year)
            

#---------------------------------------------------------------------------------------
#-- run_update: update all html pages and add a new one for the year, if needed      ---
#---------------------------------------------------------------------------------------

def run_update(year):
    """
    update all html pages and add a new one for the year, if needed
    input:  year    --- this year
    output: none but updated html pages and a new one for this year (in <web_dir>)
    """

    ifile = house_keeping + 'html_template'
    with open(ifile, 'r') as f:
        data = f.read()
#
#--- full range page
#
    line = '<li>\n'
    line = line + '<span style="padding-right:15px;color:red;font-size:105%">\n'
    line = line + 'Full Range \n'
    line = line + '</span>\n'
    line = line + '</li>\n'

    for lyear in range(1999, year+1):
        line = line + '<li><a href="./sim_' + str(lyear) + '.html">' + str(lyear) + '</a></li>\n'

    out = data.replace('#YEARLIST#', line)
    out = out.replace('#YEAR#', 'fullrange')
    
    ofile = web_dir + 'fullrange.html'
    with open(ofile, 'w') as fo:
        fo.write(out)
#
#--- each year page
#
    for lyear in range(1999, year+1):
        line = '<li>\n'
        line = line + '<span style="padding-right:15px">\n'
        line = line + '<a href="./fullrange.html">Full Range</a>\n'
        line = line + '</span>\n'
        line = line + '</li>\n'

        for eyear in range(1999, year+1):
            if eyear == lyear:
                line = line + '<span style="color:red;font-size:105%">\n'
                line = line + str(eyear) + '\n'
                line = line + '</span>\n'
                line = line + '</li>\n'
            else:
                line = line + '<li><a href="./sim_' + str(eyear) + '.html">' + str(eyear) + '</a></li>\n'

        out = data.replace('#YEARLIST#', line)
        out = out.replace('#YEAR#', str(lyear))
    
        ifile = web_dir + 'sim_' + str(lyear) + '.html'
        with  open(ifile, 'w') as fo:
            fo.write(out)

#---------------------------------------------------------------------------------------
 
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

    if len(sys.argv) == 2:
        update = 1
    else:
        update = 0

    update_html(update)
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp{user}/{name}.lock")