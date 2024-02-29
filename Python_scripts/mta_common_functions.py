#!/proj/sot/ska3/flight/bin/python

#############################################################################
#                                                                           #
#       mta_common_functions.py: colleciton of funtions used by mta         #
#                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                           #
#           last update: Oct 21, 2021                                       #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import random
import time
import math
import numpy
#import astropy.io.fits  as pyfits
from datetime import datetime
import Chandra.Time
from io import BytesIO
import codecs
import unittest
#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param ', shell='tcsh')

tail = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(tail)

house_keeping = '/data/mta/Script/Python3.10/MTA/'

#--------------------------------------------------------------------------
#-- read_data_file: read a data file and create a data list              --
#--------------------------------------------------------------------------

def read_data_file(ifile, remove=0, ctype='r'):
    """
    read a data file and create a data list
    input:  ifile   --- input file name
            remove  --- if > 0, remove the file after reading it
            ctype   --- reading type such as 'r' or 'b'
    output: data    --- a list of data
    """
#
#--- if a file specified does not exist, return an empty list
#
    if not os.path.isfile(ifile):
        return []

    try:
        with open(ifile, ctype) as f:
            data = [line.strip() for line in f.readlines()]
    except:
        with codecs.open(ifile, ctype, encoding='utf-8', errors='ignore') as f:
            data = [line.strip() for line in f.readlines()]
#
#--- if asked, remove the file after reading it
#
    if remove > 0:
        rm_files(ifile)

    return data

#--------------------------------------------------------------------------
#-- rm_files: remove a file of named file in a list                      --
#--------------------------------------------------------------------------

def rm_files(ifile):
    """
    remove a file of named file in a list
    input:  ifile   --- a file name or a list of file names to be removed
    output: none
    """
    mc = re.search('\*', ifile)
    if mc  is not None:
        cmd = 'rm -fr ' +  ifile
        os.system(cmd)

    else:
        if isinstance(ifile, (list, tuple)):
            ilist = ifile
        else:
            ilist = [ifile]
    
        for ent in ilist:
            if os.path.isfile(ent):
                cmd = 'rm -fr ' + ent
                os.system(cmd)

def rm_file(ifile):
    rm_files(ifile)

#--------------------------------------------------------------------------
#-- sort_list_with_other: order a list with the order of another sorted list 
#--------------------------------------------------------------------------

def sort_list_with_other(list1, list2, schoice=1):
    """
    order a list with the order of another sorted list
    input:  list1   --- a list
            list2   --- a list
            schoice --- which list to be used to order; default:fist
    output: list1, list2    --- sorted/reordered lists
    """
    if len(list1) != len(list2):
        return False

    if schoice == 1:
        list1, list2 = (list(t) for t in zip(*sorted(zip(list1, list2))))
    else:
        list2, list1 = (list(t) for t in zip(*sorted(zip(list2, list1))))

    return [list1, list2]

#--------------------------------------------------------------------------
#-- sort_multi_list_with_one: order all lists in a list by nth list order -
#--------------------------------------------------------------------------

def sort_multi_list_with_one(clists, col=0):
    """
    order all lists in a list by nth list sorted order
    input:  clist   --- a list of lists
            col     --- position of a list to be use for sorting
    output: save    --- a list of lists, sorted
    """

    array1 = numpy.array(clists[col])
    index  = numpy.argsort(array1)

    save   = []
    for ent in clists:
        save.append(list(numpy.array(ent)[index]))

    return save

#--------------------------------------------------------------------------
#-- is_leapyear: check whether the year is a leap year                   --
#--------------------------------------------------------------------------

def is_leapyear(year):
    """
    check whether the year is a leap year
    input:  year    --- year
    output: True/False
    """
    year = int(float(year))
    chk  = year % 4             #--- every 4 years:   leap year
    chk2 = year % 100           #--- but every 100 years: not leap year
    chk3 = year % 400           #--- except every 400 year: leap year

    val  = False
    if chk == 0:
        val = True
        if chk2 == 0:
            val = False
    if chk3 == 0:
        val = True

    return val

def isLeapYear(year):
    is_leapyear(year)
    
#--------------------------------------------------------------------------
#-- is_neumeric: checking the input is neumeric value                    --
#--------------------------------------------------------------------------

def is_neumeric(val):
    """
    checking the input is neumeric value
    input:  val --- input value
    output: True/False
    """

    try:
        var = float(val)
        return True
    except:
        return False

def chkNumeric(val):
    is_neumeric(val)

#--------------------------------------------------------------------------
#-- convert_date_format: convert date format                             --
#--------------------------------------------------------------------------

def convert_date_format(date, ifmt="%Y:%j:%H:%M:%S", ofmt="%Y-%m-%dT%H:%M:%S"):
    """
    convert date format
    input:  date    --- the original date
            ifmt    --- input date format.  default: %Y:%j:%H:%M:%S
                        if input is chandara time, it will ignore the input format
            ofmt    --- output date format. default: %Y-%m-%dT%H:%M:%S
    output: date    --- converted date
    """
#
#--- if it is chandra time, convert the date into '%Y:%j:%H:%M:%S'
#
    if is_neumeric(date) and (ifmt in ['%Y:%j:%H:%M:%S', 'chandra']):
        date    = Chandra.Time.DateTime(date).date
#
#--- chandra time give a dicimal part in the second; get rid of it
#
        atmp    = re.split('\.', date)
        date    = atmp[0]
        ifmt = '%Y:%j:%H:%M:%S'
#
#--- convert it to time struct
#
    out  = time.strptime(str(date),   ifmt)
#
#--- if output format is chandra time
#
    if ofmt.lower() == 'chandra':
        ofmt = '%Y:%j:%H:%M:%S'
        ochk    = 1
    else:
        ochk    = 0

    date = time.strftime(ofmt, out)
    if ochk == 1:
        date = Chandra.Time.DateTime(date).secs

    return date

#--------------------------------------------------------------------------
#-- ydate_to_dom: find dom for a given year and ydate                   ---
#--------------------------------------------------------------------------

def ydate_to_dom(year, ydate):
    """
    find dom for a given year and ydate
    input:  year    --- year
            ydate   --- ydate
    output: dom
    """
    year  = int(float(year))
    ydate = int(float(ydate))

    dom = ydate
    if year == 1999:
        dom -= 202

    elif year >= 2000:
#
#--- add adjust leap year from the last year. 2100 is not a leap year
#--- so we need to correct that
#
        add = int((year - 1997) / 4.0)
        if year == 2101:
            add -= 1
        dom = dom + 163 + (year - 2000) * 365 + add

    else: 
        dom = 0

    dom = int(dom)

    return dom

#--------------------------------------------------------------------------
#-- dom_to_ydate: find year and ydate from dom                           --
#--------------------------------------------------------------------------

def dom_to_ydate(dom):
    """
    find year and ydate from dom
    input:  dom --- day of mission
    output: year    --- year
            ydate   --- ydate
    """
    dom += 202
    year = 1999
    chk  = 0
    while chk == 0:
        if is_leapyear(year):
            base = 366
        else:
            base = 365

        dom -= base
        if dom < 0:
            ydate = dom + base
            chk   = 1
            break
        else:
            year += 1

    return (year, ydate)

#--------------------------------------------------------------------------
#-- chandratime_to_fraq_year: convert chandra time into a fractional year date format 
#--------------------------------------------------------------------------

def chandratime_to_fraq_year(ctime):
    """
    convert chandra time into a fractional year date format
    input:  ctime   --- time in seconds from 1998.1.1
    output: ytime   --- time in fractional year format
    """
    atime = convert_date_format(ctime, ofmt='%Y:%j:%H:%M:%S')
    btemp = re.split(':', atime)
    year  = float(btemp[0])
    ydate = float(btemp[1])
    hour  = float(btemp[2])
    mins  = float(btemp[3])
    sec   = float(btemp[4])

    if is_leapyear(year):
        base = 366.0
    else:
        base = 365.0

    ydate  = ydate + (hour/24.0 + mins/1440.0 + sec/86400.0)
    frac   = ydate/base
    ytime  = year + frac

    return ytime

#--------------------------------------------------------------------------
#-- chandratime_to_yday: convert chandra time into a day of year         --
#--------------------------------------------------------------------------

def chandratime_to_yday(ctime):
    """
    convert chandra time into a day of year
    input:  ctime   --- time in seconds from 1998.1.1
    output: ydate   --- a day of year (fractional)
    """

    atime = convert_date_format(ctime, ofmt='%Y:%j:%H:%M:%S')
    btemp = re.split(':', atime)
    year  = float(btemp[0])
    ydate = float(btemp[1])
    hour  = float(btemp[2])
    mins  = float(btemp[3])
    sec   = float(btemp[4])

    ydate  = ydate + (hour/24.0 + mins/1440.0 + sec/86400.0)


    return ydate


#--------------------------------------------------------------------------
#-- mk_empty_dir: empyty or create a named directory                     --
#--------------------------------------------------------------------------

def mk_empty_dir(name):
    """
    empty the existing directory. if it doesnot exist, create an empty directory
    Input:  name    --- the name of direcotry
    Output: <chk>   --- if it is created/emptyed, return 1 otherwise 0
    """
    try:
        if os.path.isdir(name):
            cmd = 'rm -rf ' + name
            os.system(cmd)

        cmd = 'mkdir ' + name
        os.system(cmd)
        return 1

    except:
        return 0

#--------------------------------------------------------------------------
#-- add_leading_zero: add leading 0 to digit                             --
#--------------------------------------------------------------------------

def add_leading_zero(val, dlen=2):
    """
    add leading 0 to digit
    input:  val     --- neumeric value or string value of neumeric
            dlen    --- length of digit
    output: val     --- adjusted value in string
    """
    try:
        val = int(val)
    except:
        return val

    val  = str(val)
    vlen = len(val)
    for k in range(vlen, dlen):
        val = '0' + val

    return val

#--------------------------------------------------------------------------
#-- add_tailing_zero: add '0' to the end to fill the length after a dicimal point
#--------------------------------------------------------------------------

def add_tailing_zero(val, digit):
    """
    add '0' to the end to fill the length after a dicimal point
    input:  val --- value
            digit   --- the number of decimal position
    output: val --- adjust value (str)
    """
    val   = str(val)
    atemp = re.split('\.', val)
    
    vlen  = len(atemp[1])
    diff  = digit - vlen
    if diff > 0:
        for k in range(0, diff):
            atemp[1] = atemp[1] + '0'
    
    val   = atemp[0] + '.' + atemp[1]
    
    return val

#--------------------------------------------------------------------------
#-- check_file_with_name: check files with the name with a part 'part' exist 
#--------------------------------------------------------------------------

def check_file_with_name(tdir, part=''):
    """
    check files with the name with a part 'part' exist in dir
    input:  tdir    --- a directory path or a full path with the full file name
            part    --- a part of the name of files which we want to check
    output: Ture/False
    """
    if part == '':
        if os.path.isfile(tdir):
            return True
        else:
            return False
    else:
        if tdir == './':
            if os.path.isfile(test):
                return True
            else:
                return False

        try:
            part = part.rstrip('\/')
            part = part.rstrip('*')
            part = part.rstrip('\\')
            if os.path.isdir(tdir):
                cmd = 'ls ' + tdir + '> ' + zspace
                os.system(cmd)

                f   = open(zspace, 'r')
                out = f.read()
                f.close()
                rm_files(zspace)
             
                mc  = re.search(part,  out)
                if mc is not None:
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

#--------------------------------------------------------------------------
#-- remove_duplicated_lines: remove duplicated lines from a file or a list 
#--------------------------------------------------------------------------

def remove_duplicated_lines(iname, chk=1, srt=1):
    """
    remove duplicated lines from a file or a list
    input:  iname   --- input file or a input list name
            chk     --- input is a list if 0, otherwise a file
            srt     --- if 1, sort requested
    output: if chk == 0:    return a list 
               chk >  0:    updated file

    """
    if (chk == 1) and (not os.path.isfile(iname)): 
        return []
    else:
        new  =  []
        if chk == 1:
            data = read_data_file(iname)
        else:
            data = iname

        if len(data) > 1:
            if srt > 0:
                data = sorted(data)

                first = data[0]
                new   = [first]
                for i in range(1, len(data)):
                    ichk = 0
                    for k in range(len(new)-1, -1, -1):
                        if data[i] == new[k]:
                            ichk = 1
                            break

                    if ichk == 0:
                        new.append(data[i])

                if chk == 1:
                    with open(iname, 'w') as fo:
                        for ent in new:
                            fo.write(ent + '\n')

                else:
                    return new
        else:
            if chk == 0:
                return data

def removeDuplicate(iname, chk = 1, srt=1):
    remove_duplicated_lines(iname, chk=1, srt=1)

    
#--------------------------------------------------------------------------
#-- change_month_format: cnvert month format between digit and three letter month 
#--------------------------------------------------------------------------

def change_month_format(month):
    """
    cnvert month format between digit and three letter month
    input:  month   --- either digit month or letter month
    oupupt: either digit month or letter month
    """
    m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',\
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
#--- check whether the input is digit
#
    try:
        var = int(float(month))
        if (var < 1) or (var > 12):
            return 'NA'
        else:
            return m_list[var-1]
#
#--- if not, return month #
#
    except:
        mon = 'NA'
        var = month.lower()
        for k in range(0, 12):
            if var == m_list[k].lower():
                return k+1

        return mon

#--------------------------------------------------------------------------
#-- today_date_display: get today's date in <mmm>-<dd>-<yyyy>           ---
#--------------------------------------------------------------------------

def today_date_display():
    """
    get today's date in <mmm>-<dd>-<yyyy> (e.g., Jan-01_2018)
    input:  none
    output:<mmm>-<dd>-<yyyy>
    """
    out= time.strftime('%Y:%m:%d', time.gmtime())
    atemp  = re.split(':', out)
    lmon   = change_month_format(atemp[1])

    current = lmon + '-' + atemp[2] + '-' + atemp[0]

    return current


#--------------------------------------------------------------------------
#-- today_date_display2 : get today's date in <mmm> <dd>, <yyyy>           ---
#--------------------------------------------------------------------------

def today_date_display2():
    """
    get today's date in <mmm>-<dd>-<yyyy> (e.g., Jan-01_2018)
    input:  none
    output:<mmm>-<dd>-<yyyy>
    """
    out= time.strftime('%Y:%m:%d', time.gmtime())
    atemp  = re.split(':', out)
    lmon   = change_month_format(atemp[1])

    current = lmon + ' ' + atemp[2] + ', ' + atemp[0]

    return current

#--------------------------------------------------------------------------
#-- today_date: return today's year, mon, and day                        --
#--------------------------------------------------------------------------

def today_date():
    """
    return today's year, mon, and day
    input: none
    output: [year, mon, day]
    """
    out = time.strftime('%Y:%m:%d', time.gmtime())
    atemp = re.split(':', out)
    year  = int(atemp[0])
    mon   = int(atemp[1])
    day   = int(atemp[2])

    return [year, mon, day]

#--------------------------------------------------------------------------
#-- separate_data_to_arrays: separate a table data into arrays of data    --
#--------------------------------------------------------------------------

def separate_data_to_arrays(data, separator='\s+', com_out=''):
    """
    separate a table data into arrays of data
    input:  data        --- a data table
            separator   --- what is the delimited charactor.default: '\s+'
            com_out     --- if this is provided, the beginning of the line 
                            marked with that won't be read in (e.g.  by '#')
    output: coldata     --- a list of lists of each column
    """
    atemp = re.split(separator, data[0])
    alen  = len(atemp)

    coldata = [[] for x in range(0, alen)]

    for ent in data:
        if ent == '':
            continue
        if (com_out != '') and (ent[0] == com_out):
            continue

        atemp = re.split(separator, ent)

        for j in range(0, alen):
            try:
                val = float(atemp[j])
            except:
                val = atemp[j]
            coldata[j].append(val)

    return coldata

#--------------------------------------------------------------------------
#-- run_arc5gl_process: un arc5gl process                                --
#--------------------------------------------------------------------------

def run_arc5gl_process(cline):
    """
    run arc5gl process
    input:  cline   --- command lines
    output: f_list  --- a list of fits (either extracted or browsed)
    *fits   --- if the command asked to extract; resulted fits files
    """
    with open(zspace, 'w') as fo:
        fo.write(cline)
    
    try:
        cmd = ' /proj/sot/ska/bin/arc5gl -user swolk -script ' + zspace + ' > ./zout'
        os.system(cmd)
    except:
        try:
            cmd  = ' /proj/axaf/simul/bin/arc5gl -user swolk -script ' + zspace + ' > ./zout'
            os.system(cmd)
        except:
            cmd1 = "/usr/bin/env PERL5LIB= "
            cmd2 = ' /proj/axaf/simul/bin/arc5gl -user swolk -script ' + zspace + ' > ./zout'
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)
    
    rm_files(zspace)
    
    out  = read_data_file('./zout', remove=1)
    save = []
    for ent in out:
        if ent == "":
            continue
        mc = re.search('Filename', ent)
        if mc is not None:
            continue
        mc = re.search('Retrieved', ent)
        if mc is not None:
            continue
        mc = re.search('---------------', ent)
        if mc is not None:
            continue
    
        atemp = re.split('\s+', ent)
        save.append(atemp[0])
    
    return save

#--------------------------------------------------------------------------
#-- run_arc5gl_process_user: un arc5gl process with a user option        --
#--------------------------------------------------------------------------

def run_arc5gl_process_user(cline, user='isobe'):
    """
    run arc5gl process with a user option
    input:  cline   --- command lines
            user    --- user option
    output: f_list  --- a list of fits (either extracted or browsed)
            *fits   --- if the command asked to extract; resulted fits files
    """
    with open(zspace, 'w') as fo:
        fo.write(cline)
    
    try:
        cmd = ' /proj/sot/ska/bin/arc5gl -user ' + user + ' -script ' + zspace + ' > ./zout'
        os.system(cmd)
    except:
        try:
            cmd  = ' /proj/axaf/simul/bin/arc5gl -user ' + user + ' -script ' + zspace + ' > ./zout'
            os.system(cmd)
        except:
            cmd1 = "/usr/bin/env PERL5LIB= "
            cmd2 = ' /proj/axaf/simul/bin/arc5gl -user ' + user + ' -script ' + zspace + ' > ./zout'
            cmd  = cmd1 + cmd2
            bash(cmd,  env=ascdsenv)
    
    rm_files(zspace)
    
    out  = read_data_file('./zout', remove=1)
    save = []
    for ent in out:
        if ent == "":
            continue
        mc = re.search('Filename', ent)
        if mc is not None:
            continue
        mc = re.search('Retrieved', ent)
        if mc is not None:
            continue
        mc = re.search('---------------', ent)
        if mc is not None:
            continue
    
        atemp = re.split('\s+', ent)
        save.append(atemp[0])
    
    return save

#--------------------------------------------------------------------------
#-- separate_data_into_col_data: separate a list of data lines into a list of lists 
#--------------------------------------------------------------------------

def separate_data_into_col_data(data, spliter = '\s+'):
    """
    separate a list of data lines into a list of lists of column data
    input:  data    --- data list
            spliter --- spliter of the line. default: \s+
    output: save    --- a list of lists of data
    """
    atemp = re.split(spliter, data[0])
    alen  = len(atemp)
    save  = [[] for x in range(0, alen)]   

    for ent in data:
        atemp = re.split(spliter, ent)
        for k in range(0, alen):
            try:
                val = float(atemp[k])
            except:
                val = atemp[k].strip()
     
            save[k].append(val)
     
    return save

#--------------------------------------------------------------------------
#-- remove_non_neumeric_values: remove all rows of lists in a list which correspond to non-neumeric
#--------------------------------------------------------------------------

def remove_non_neumeric_values(alist, pos):
    """
    remove all rows of lists in a list which correspond to non-neumeric
    entries in pos-th list.
    input:  alist   --- a list of lists
            pos     --- position of a list which contains non nuemeric values
    output: slist   --- a list of lists removed non-neumeric entries
    """
#
#--- get a list of which we want to find non-numeric entries
#
    tlist  = alist[pos]
    tlist  = genfromtxt3(tlist)
    tarray = numpy.array(tlist)
#
#--- create index to remove non-neumeric values
#
    oindex = ~numpy.isnan(tarray)
#
#--- apply the index to all lists
#
    slist  = []
    for ent in alist:
        tarray = numpy.array(ent)
#
#--- make sure that all entries are numeric not string
#
        nlist  = list(tarray[oindex])
        if isinstance(nlist[0], str):
            nlist = list(genfromtxt3(nlist))

        slist.append(nlist)

    return slist

#--------------------------------------------------------------------------
#-- genfromtxt3: genfromtxt python3 version --- correcting python 3 bug ---
#--------------------------------------------------------------------------

def genfromtxt3(alist):
    """
    genfromtxt python3 version --- correcting python 3 bug
    input:  alist   --- a list of string entries
    output: out     --- a list of numeric entries
    """

    out = numpy.array(alist)
    out = numpy. genfromtxt(map(lambda s:s.encode('utf8'), out))

    return out

#--------------------------------------------------------------------------
#--    TEST TEST TEST TESt TESt TEST TEST TEST TEST TESt TESt TEST      ---
#--------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):

    def test_is_leapyear(self):
        year = 2000
        self.assertTrue(is_leapyear(year))
        year = 2100
        self.assertFalse(is_leapyear(year))

#--------------------------------------------------------------------------

    def test_sort_list_with_other(self):

        list1 = ['z', 'v', 't', 'k']
        list2 = ['a', 'b', 'c', 'd']
        list1, list2 = sort_list_with_other(list1, list2)

        self.assertEqual(list2, ['d', 'c', 'b', 'a'])

#--------------------------------------------------------------------------

    def test_sort_multi_list_with_one(self):

        list1 = [4,3,2,1]
        list2 = [10, 9, 8, 7]
        list3 = ['z', 'v', 't', 'k']
        list4 = ['a', 'b', 'c', 'd']
        clists = [list1, list2, list3, list4]
        out   = sort_multi_list_with_one(clists, 0)

        self.assertEqual(out[3], ['d', 'c', 'b', 'a'])

#--------------------------------------------------------------------------

    def test_convert_date_format(self):

        date  = '2019:184:00:43:32'
        cdate = convert_date_format(date)
        self.assertEqual(cdate, '2019-07-03T00:43:32')

        cdate = convert_date_format(date, ofmt='%Y:%m:%d:%H:%M:%S')
        self.assertEqual(cdate, '2019:07:03:00:43:32')

        cdate = convert_date_format(date, ofmt="chandra")
        self.assertEqual(cdate, 678501881.184)

        cdate = convert_date_format(678501881.184)
        self.assertEqual(cdate, '2019-07-03T00:43:32')

        cdate = convert_date_format('20190626223528', ifmt='%Y%m%d%H%M%S', ofmt='%Y:%j:%H:%M:%S')
        print("I AM HERE Cdate: " + str(cdate))

#--------------------------------------------------------------------------

    def test_ydate_to_dom(self):

        year  = 1999
        ydate = 202
        out   = ydate_to_dom(year, ydate)
        self.assertEqual(out, 0)

        year  = 2012
        ydate = 1
        out   = ydate_to_dom(year, ydate)
        self.assertEqual(out, 4547)

        year  = 2019
        ydate = 202
        out   = ydate_to_dom(year, ydate)
        self.assertEqual(out, 7305)

#--------------------------------------------------------------------------

    def test_dom_to_ydate(self):

        dom = 7175
        [year, ydate] = dom_to_ydate(dom)
        line = str(year) + ':' + str(ydate)
        self.assertEqual(line, '2019:72')

#--------------------------------------------------------------------------

    def test_chandratime_to_fraq_year(self):

        ctime = 584150395
        fyear = chandratime_to_fraq_year(ctime)
        self.assertEqual(fyear, 2016.5136588620724)

#--------------------------------------------------------------------------

    def test_add_leading_zero(self):

        val = 2
        val = add_leading_zero(val)
        self.assertEqual(val, '02')

        val = 33
        val = add_leading_zero(val, dlen=3)
        self.assertEqual(val, '033')

        val = 33
        val = add_leading_zero(val)
        self.assertEqual(val, '33')

        val = '33'
        val = add_leading_zero(val, dlen=3)
        self.assertEqual(val, '033')

#--------------------------------------------------------------------------

    def test_remove_duplicated_lines(self):

        test = ['5,3,4', '1,2,3', '2,3,4', '1,2,3']
        out = remove_duplicated_lines(test, chk=0)
        chk = ['1,2,3', '2,3,4','5,3,4']
        self.assertEqual(out, chk)

#--------------------------------------------------------------------------

    def test_run_arc5gl_process(self):

        line = 'operation=browse\n'
        line = line + 'dataset=flight\n'
        line = line + 'detector=acis\n'
        line = line + 'level=1\n'
        line = line + 'filetype=evt1\n'
        line = line + 'tstart=2019-01-01T00:00:00\n'
        line = line + 'tstop=2019-01-05T00:00:00\n'
        line = line + 'go\n'
        
        fits = 'acisf22032_000N001_evt1.fits'
        out = run_arc5gl_process(line)
        if fits in out:
            self.assertEqual(fits, fits)

#--------------------------------------------------------------------------
    def test_separate_data_into_col_data(self):

        data = ['1  2   3   4', '5  6   7   8']

        out = separate_data_into_col_data(data, spliter='\s+')

        print("I AM HERE: " + str(out))

#--------------------------------------------------------------------------

    def test_remove_non_neumeric_values(self):

        in_list=   [[1,2,3,4], [2,'test',4,5],  [3,4,5,6]]
        out_list = [[1, 3, 4], [2.0, 4.0, 5.0], [3, 5, 6]]

        out = remove_non_neumeric_values(in_list, 1)
        self.assertEqual(out, out_list)

#--------------------------------------------------------------------------

if __name__ == '__main__':

    unittest.main()

