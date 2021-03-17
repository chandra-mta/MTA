#!/usr/bin/env /proj/sot/ska/bin/python
import os
import sys
import re
import string
import random
import operator
import math
import numpy
import unittest

mta_dir = '/data/mta/Script/Python_script2.7/'
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA script

month_list1 = [31, 28, 31, 30, 31, 30, 31, 31, 30 , 31, 30, 31]
month_list2 = [31, 29, 31, 30, 31, 30, 31, 31, 30 , 31, 30, 31]

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def print_month_list():

    [year, mon, day, hours, min, sec, weekday, yday, dst] = tcnv.currentTime()

    line  = 'Sep99 41 71\n'
    begin = 71
    for iyear in range(1999, year+1):

        if tcnv.isLeapYear(iyear) == 1:
            month_list = month_list2
        else:
            month_list = month_list1

        lyear = str(iyear)
        syear = lyear[2] + lyear[3]
        for month in range(1, 13):
            if iyear == 1999 and  month < 10:
                continue
            if iyear == year and month > mon:
                break

            lmon = tcnv.changeMonthFormat(month)
            time = lmon + syear

            daynum = month_list[month-1]
            end    = daynum + begin
            
            line   = line + time + ' ' + str(begin) + ' ' + str(end) + '\n'
            begin  = end

    fo = open('/data/mta_www/mta_sim/Scripts/SIM_move/Outputs/months', 'w')
    fo.write(line)
    fo.close()
            
#--------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    print_month_list()

