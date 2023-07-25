#!/proj/sot/ska3/flight/bin/python

import sys
import os

sys.path.append("/data/mta4/Script/Python3.10/MTA")
import mta_common_functions as mcf

#---------------------------------------------------------------------------------------
#-- run_arc5gl: extract data from archive using arc5gl                                --
#---------------------------------------------------------------------------------------

def run_arc5gl(start, stop):
    """
    extract data from archive using arc5gl
    input:  start   --- starting time in the format of mm/dd/yy,hh/mm/ss. hh/mm/ss is optional
            stop    --- stoping time
    output: extracted data set
    """
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

def start_stop_period(year, yday):
    """
    convert year and yday to the mm/dd/yy, 00:00:00 format
    input:  year    --- year
            yday    --- yday
    output: [start, stop]   --- in the format of mm/dd/yy, 00:00:00 
    """
    today = str(year) + ':' + mcf.add_leading_zero(yday, 3)
    start = today + ':00:00:00'
    stop  = today + ':23:59:59'

    return [start, stop]


def set_date_period(year,sdate,edate):
    dperiod = []
    for yday in range(sdate, edate+1):
        dperiod.append([year, yday])
    return dperiod

year = 2023
yday = 180

sdate = 100
edate = 150

tperiod = set_date_period(year,sdate,edate)

count = 0
rm_len = 14
"""
for i in range(len(tperiod)):
    print(f"Step: {i}, tperiod:{tperiod[i]}")
    print(f"Count:{count}")
    if count == rm_len:
        count = 0
        print("running remove command")
    else:
        count +=1
print(f"running final removal")
"""

#"""
[sdate,edate] = start_stop_period(year,yday)

print(f"sdate:{sdate}")
print(f"edate:{edate}")

out = run_arc5gl(sdate,edate)
print(out)
#"""