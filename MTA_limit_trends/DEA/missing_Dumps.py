#!/proj/sot/ska3/flight/bin/python

#In the event of the GOT Dumps data archive missing/deleting data which hasn't been processed into deahk rdb files,
#this script will calculate and donwload the missing Dumps_EM data into the Exc directory.
#This script is to repairing missing data, not for typical running.

import sys, os
from Chandra.Time import DateTime
import re
import subprocess
import numpy

sys.path.append("/data/mta4/Script/Python3.10/MTA")
import mta_common_functions as mcf


dea_dir = "/data/mta4/testDEA/Scripts/DEA/"
repository = "/data/mta4/testDEA/Scripts/DEA/RDB/"

#list of files which should be checked timewise for repair. If another break occurs, change these files to reflect the more recently generated rdb files
"""
ifiles = ["/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_elec_short.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_elec_week2021.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_elec_week.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_temp_short.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_temp_week2021.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_temp_week.rdb"]

ifiles = ["/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_elec_short.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_elec_week2021.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_temp_short.rdb",\
         "/data/mta/Script/MTA_limit_trends/Scripts/DEA/RDB/deahk_temp_week2021.rdb"]
"""

ifiles = ["/data/mta4/testDEA/Scripts/DEA/RDB/deahk_elec_short.rdb",\
         "/data/mta4/testDEA/Scripts/DEA/RDB/deahk_elec_week2021.rdb",\
         "/data/mta4/testDEA/Scripts/DEA/RDB/deahk_temp_short.rdb",\
         "/data/mta4/testDEA/Scripts/DEA/RDB/deahk_temp_week2021.rdb"]


def tail(f, n=10):
    proc = subprocess.Popen(['tail', '-n', str(n), f], stdout=subprocess.PIPE)
    lines = list(proc.stdout.readlines())
    lines = [x.decode() for x in lines]
    if len(lines) == 1:
        return lines[0]
    else:
        return lines

#---------------------
#-- smart_append: appends a processed data file into an existing data set without repeating time entries.
#-- Note: Designed for this projects rdb files where time is recorded as the frist tesxt entry in each line. does not work in general.
#-----------------------
def smart_append(file, append):
    endtime = float(tail(file,n=1).strip().split()[0])
    with open(append,'r') as f:
        data = f.readlines()
    data = [x.strip() for x in data if x.strip() != ''] #cleanup step in case appending file contains unnecessary extra spacing
    chk = 0
    for i in range(len(data)):
        if float(data[i].split()[0]) > endtime:
            chk = 1
            break
    if chk == 1:
        data = data[i:]
    else:
        data = []
    appendstring = "\n".join(data)
    with open(file,'a+') as f:
        f.write(appendstring)


def start_stop_period(year, yday, range):
    """
    convert year and yday to the mm/dd/yy, 00:00:00 format
    input:  year    --- year
            yday    --- yday
    output: [start, stop]   --- in the format of mm/dd/yy, 00:00:00 
    """
    yday = int(yday)
    startday = str(year) + ':' + mcf.add_leading_zero(yday, 3)
    endday = str(year) + ':' + mcf.add_leading_zero(yday+range, 3)
    start = startday + ':00:00:00'
    stop  = endday+ ':23:59:59'

    return [start, stop]


def run_arc5gl(ctime):
    (year, yday) = DateTime(ctime).date.split(':')[:2]

#
#--- covert date foramt to  mm/dd/yy, 00:00:00
#
    #calculate in batches of 10 days.
    range = 10
    [start, stop] = start_stop_period(year, yday, range)
    
#
#--- write arc5gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset =flight\n'
    line = line + 'detector=telem\n'
    line = line + 'level =raw\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'

#
#--- extract data
#
    out  = mcf.run_arc5gl_process(line)

    return out



#------------------------------------------------------------------------------------
#-- run_dea_perl: run perl scripts to extract data from dump data                  --
#------------------------------------------------------------------------------------

def run_dea_perl(dlist):
    """
    run perl scripts to extract data from dump data
    input:  dlist   --- a list of dump data file names
    output: <repository>/deahk_<temp/elec>.rdb
    """

    for ifile in dlist:
        atemp = re.split('\/', ifile)
        btemp = re.split('_', atemp[-1])
        year  = str(btemp[0])
#
#--- following is Peter Ford script to extract data from dump data
#
        cmd = '/bin/gzip -dc ' + ifile + ' | ' + dea_dir + 'getnrt -O  | ' + dea_dir + 'deahk.pl'
        os.system(cmd)

        cmd = dea_dir + 'out2in.pl deahk_temp.tmp deahk_temp_in.tmp ' + year
        os.system(cmd)

        cmd = dea_dir + 'out2in.pl deahk_temp.tmp deahk_elec_in.tmp ' + year
        os.system(cmd)
#
#--- 5 min resolution
#
        cmd  = dea_dir + 'average1.pl -i deahk_temp_in.tmp -o deahk_temp.rdb'
        os.system(cmd)
        """
        cmd  = 'cat deahk_temp.rdb >> ' + repository + 'deahk_temp_week' + year + '.rdb'
        os.system(cmd)
        """
        smart_append(f"{repository}/deahk_temp_week{year}.rdb","deahk_temp.rdb")

        cmd  = dea_dir + 'average1.pl -i deahk_elec_in.tmp -o deahk_elec.rdb'
        os.system(cmd)
        """
        cmd  = 'cat deahk_elec.rdb >> ' + repository + 'deahk_elec_week' + year + '.rdb'
        os.system(cmd)
        """
        smart_append(f"{repository}/deahk_elec_week{year}.rdb","deahk_elec.rdb")
#
#--- one hour resolution
#
        cmd  = dea_dir + 'average2.pl -i deahk_temp_in.tmp -o deahk_temp.rdb'
        os.system(cmd)
        """
        cmd  = 'cat deahk_temp.rdb >> ' + repository + 'deahk_temp_short.rdb'
        os.system(cmd)
        """
        smart_append(f"{repository}/deahk_temp_short.rdb","deahk_temp.rdb")

        cmd  = dea_dir + 'average2.pl -i deahk_elec_in.tmp -o deahk_elec.rdb'
        os.system(cmd)
        """
        cmd  = 'cat deahk_elec.rdb >> ' + repository + 'deahk_elec_short.rdb'
        os.system(cmd)
        """
        smart_append(f"{repository}/deahk_elec_short.rdb","deahk_elec.rdb")
#
#--- clean up
#
        #cmd  = 'rm -rf deahk_*.tmp deahk_*.rdb '
        cmd  = 'rm -rf deahk_*.tmp deahk_*.rdb'
        os.system(cmd)
#
#--- cleanup for Dump files
#
    cmd = 'rm -rf *Dump_EM* *Merge_EM*'
    os.system(cmd)

def find_last_time(ifiles):
    lasttime = []
    for file in ifiles:
        ending = tail(file,1)
        time = ending.strip().split()[0]
        lasttime.append(time)
        #print(f"file:{file}")
        #print(f"time: {time}")
        #print(DateTime(time).date)
    min = float(lasttime[0])
    loc = 0
    for i in range(len(lasttime)):
        if float(lasttime[i]) < min:
            min = float(lasttime[i])
            loc = i
    #print(f"smallest: {ifiles[loc]}, {lasttime[loc]}")
    return min

if __name__=="__main__":
    time = find_last_time(ifiles)
    dlist = run_arc5gl(time)

    run_dea_perl(dlist)
    with open('record.txt','w+') as f:
            f.write("\n".join(dlist))