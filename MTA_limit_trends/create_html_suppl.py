#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#######################################################################################
#                                                                                     #
#       create_html_suppl.py:   collecitons of functions to create html pages         #
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
import math
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- read argv
#
try:
    option, remainder = getopt.getopt(sys.argv[1:],'t',['test'])
except getopt.GetoptError as err:
     print(str(err))
     sys.exit(2)

path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(mta_dir)
sys.path.append(bin_dir)

import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import violation_estimate_data  as ved  #---- save violation estimated times in sqlite database v_table
import find_moving_average      as fma  #---- moving average 
import find_moving_average_bk   as fmab #---- moving average (backword fitting version)
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
#--- set several values used in the plots
#
color_table  = ['blue', 'red', '#FFA500']
marker_table = ['s',   '*',    '^',     'o']
marker_size  = [50,    80,     70,      50]

css = """
    p{
        text-align:left;
    }
"""
#
#---  get dictionaries of msid<-->unit and msid<-->description
#
[udict, ddict] = ecf.read_unit_list()
#
#---  a list of groups excluded from interactive page creation
#
efile = house_keeping + 'exclude_from_interactive'
exclude_from_interactive = mcf.read_data_file(efile)
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
#
#--- a list of thoese with sub groups
#
sub_list_file  = house_keeping + 'sub_group_list'
sub_group_list = mcf.read_data_file(sub_list_file)

#----------------------------------------------------------------------------------
#-- drop_suffix: drop suffix of msid (eps. those of HRC msids)                   --
#----------------------------------------------------------------------------------

def drop_suffix(msid):
    """
    hrc has 4 different categories (all, hrc i, hrc s, off); use the same limit range
    input:  msid    --- msid
    output: pmsid   --- msid without suffix
    """
    pmsid  =  msid.replace('_i^',   '')
    pmsid  = pmsid.replace('_s^',   '')
    pmsid  = pmsid.replace('_off^', '')

    return pmsid

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def est_two_point_slope(x, y):
    try:
        [a, b] = get_int_slope_supl([x[-2], x[-1]], [y[-2], y[-1]])
        return [a, b]
    except:
        return [0, 0]


#----------------------------------------------------------------------------------
#-- compute_dy_dx: compute dy/dt for the specified period                       ---
#----------------------------------------------------------------------------------

def compute_dy_dx(x, y, ltype):
    """
    compute dy/dt for the specified period
    input:  x   --- a list of x values
            y   --- a list of y values
            ltype   --- week, short, one, five, long
    output: a       --- intercept
            b       --- slope
            d       --- slope error
            avg     --- mean of the data given (y list)
            std     --- std of the data given (y list)
    """

    if ltype   == 'week':
        cut = 4.0               #--- in days
    elif ltype == 'short':
        cut = 45.0              #--- in days
    elif ltype == 'one':
        cut =  90.0             #--- in days
    elif ltype == 'five':
        cut = 2.0               #--- in years
    else:
        cut = 3.0               #--- in years

    xd = []
    yd = []
#
#--- select out the data backward
#
    for k in range(len(x)-1, 0, -1):
        if x[k] < cut:
            break
        xd.append(x[k])
        yd.append(y[k])

    try:
        [a, b, d ] = rbl.robust_fit(xd, yd)
#
#--- cheating but a quick way to add the slope error.
#
        [x, x, d ] = least_sq(xd, yd, remove=98)        
    except:
        [a, b, d ] = least_sq(xd, yd, remove=98)

    if len(yd) > 0:
        yarray = numpy.array(yd)
        avg    = numpy.mean(yarray)
        std    = numpy.std(yarray)
    else:
        avg    = 0.0
        std    = 0.0


    if abs(a) < 0.001:
        a   = '%3.3e' % (a)
    else:
        a   = '%3.3f' % round(a, 3)

    if abs(b) < 0.001:
        b   = '%3.3e' % (b)
        d   = '%3.3e' % (d)
    else:
        b   = '%3.3f' % round(b, 3)
        d   = '%3.3f' % round(d, 3)

    if abs(avg) < 0.001:
        avg = '%3.3e' % (avg)
        std = '%3.3e' % (std)
    else:
        avg = '%3.3f' % round(avg, 3)
        std = '%3.3f' % round(std, 3)

    return [a, b, d, avg, std ]


#----------------------------------------------------------------------------------
#-- violation_notification: create violation notification                 --
#----------------------------------------------------------------------------------

def violation_notification(msid, group,  pdata, xmax, ltype,  min_a,  min_b, max_a, max_b, tmax, vupdate):
    """
    create violation notification
    input:  msid    --- msid
            group   --- group name
            pdata   --- a two dimensional array of data
            xmax    --- x max
            min_a   --- intercept of the lower predictive line
            min_b   --- slope of the lower predictive line
            max_a   --- intercept of the upper predictive line
            max_b   --- slope of the upper predictive line
            tmax    --- prediction ending point in time
            vupdate --- indicator of whether to update violation database in <house_keeping>; 1: update
    output: wline   --- lower violation description (can be empty)
            wline2  --- upper violation description (can be empty0
            pchk_l  --- indicator of whether there is lower violation (if 1)
            pchk_u  --- indicator of whether there is upper violation (if 1)
            gchk    --- whether notificaiton returned 1:yes
    """
#
#--- create violation notification
#
    wline  = ''
    wline2 = ''

    chk    = 3.0 * set_period(ltype)
    chk    = 1.e6
#
#--- updating violation notice sql database in <house_keeping>
#
    if xmax - tmax > chk: 
        vtdata = [0, 0, 0, 0]
        if vupdate > 0:
            if group in sub_group_list:
                tmsid = msid + '_' + group.lower()
            else:
                tmsid = msid

            ved.incert_data(tmsid, vtdata)
        pchk_l = 0
        pchk_u = 0
        gchk   = -1 
    elif (abs(min_b) == 999)  or (abs(max_b) == 999):
        vtdata = [0, 0, 0, 0]
        if vupdate > 0:
            if group in sub_group_list:
                tmsid = msid + '_' + group.lower()
            else:
                tmsid = msid

            ved.incert_data(tmsid, vtdata)
        pchk_l = 0
        pchk_u = 0
        gchk   = 0
    else:
        [wline, wline2, pchk_l, pchk_u]\
            = create_violation_notification(msid, group, pdata,\
                        min_a, min_b, max_a, max_b, tmax, vupdate)
        gchk  = 1

    return [wline, wline2, pchk_l, pchk_u, gchk]

#----------------------------------------------------------------------------------
#-- set_axes_label: set axes labels                                              --
#----------------------------------------------------------------------------------

def set_axes_label(msid, unit, ltype, byear):
    """
    set axes labels
    input:  msid    --- msid
            unit    --- unit
            ltype   --- short or long type plot indicator
            byear   --- the year of the short plot
    output: xlabel  --- x axis label
            ylabel  --- y axis label
    """

    if ltype in ['five', 'long']:
        xlabel = 'Time (year)'
    else:
        xlabel = 'Time (yday of ' + str(int(byear)) + ')'

    if unit != '':
        if unit in ('DEGF', 'DEGC'):
            unit = 'K'
        ylabel = msid + ' (' + unit + ')'
    else:
        ylabel = msid

    return [xlabel, ylabel]

#----------------------------------------------------------------------------------
#-- save_plot_html: save a html formated plot in a file                          --
#----------------------------------------------------------------------------------

def save_plot_html(msid, fig, ltype, mtype, tail):
    """
    save a html formated plot in a file
    input:  msid    --- msid
            fig     --- matplot format plot information
            tail    --- sufix to put on the file name
    output: oname   --- a file saving the plot: <web_dir>/Future/<msid>_<tail>
    """

    fig.set_size_inches(8.0, 5.8)
    fig.tight_layout()
    sout =  mpld3.fig_to_html(fig)

    oname = web_dir + 'Future/' + msid + '_'  + ltype + '_' + mtype + '_' + tail

    with open(oname, 'w') as fo:
        fo.write(sout)

#----------------------------------------------------------------------------------
#-- create_violation_notification: check violation and create notification       --
#----------------------------------------------------------------------------------

def create_violation_notification(msid, group,  pdata, min_a, min_b, max_a, max_b, tmax, vupdate):
    """
    check violation and create notification
    input:  msid    --- msid
            group   --- group
            pdata   --- a two dimensional array  of data (see "read_data" for details)
            min_a   --- intercept value of the lower envelope prediction
            min_b   --- slope value of the lower envelope prediction
            max_a   --- intercept value of the upper envelope prediction
            max_b   --- slope value of the upper envelope prediction
            tmax    --- prediction ending point in time
            vupdate --- indicator of whether to update violation database 
                        in <house_keeping>; 1: update
    output: line    --- lower violation description (can be empty)
            line2   --- upper violation description (can be empty0
            pchk_l  --- indicator of whether there is lower violation (if 1)
            pchk_u  --- indicator of whether there is upper violation (if 1)
    """
#
#--- predict violation
#
    line   = ''
    line2  = ''
    yl_time = 0.0
    yt_time = 0.0
    rl_time = 0.0
    rt_time = 0.0
    pchk_l  = 0
    pchk_u  = 0
#
#--- check lower violations
#
    if (min_a != 0) or (min_b != 0):
        vlimit = pdata[15][-2]
        if abs(vlimit) > 6e6:
            pass
        else:
            vtime1 = predict_violation(min_a, min_b, tmax, vlimit, side = 0)
            if vtime1 == tmax:
                line = 'The data are already in Red Lower Violation'
                rl_time = -1.0
            else:
                vlimit = pdata[13][-2]
                vtime2 = predict_violation(min_a, min_b, tmax, vlimit, side = 0)
     
                if vtime2 == tmax:
                    line = 'The data are already in Yellow Lower Violation'
                    yl_time = -1.0
     
                elif (vtime2 > 0) and (vtime2 < tmax + 5):
                    line   = 'The data may violate the lower yellow limit at Year: ' 
                    line   = line + str(ecf.round_up(vtime2))
                    yl_time = vtime2
                    pchk_l  = 1
#
#--- check upper violations
#

    if (max_a != 0) or (max_b != 0):
        vlimit = pdata[16][-2]
        if abs(vlimit) > 6e6:
            pass
        else:
            vtime1 = predict_violation(max_a, max_b, tmax, vlimit, side = 1)
            if vtime1 == tmax:
                if line == '':
                    line  = 'The data are already in Red Upper Violation'
                    line2 = ''
                else:
                    line2 = 'The data are already in Red Upper Violation'
     
                rt_time = -1.0
            else:
                vlimit = pdata[14][-2]
                vtime2 = predict_violation(max_a, max_b, tmax, vlimit, side = 1)
                if (vtime2 > 0) and (vtime2 < tmax + 5):
                    if line == '':
                        if vtime2 == tmax:
                            line = 'The data are already in Yellow Upper Violation'
                            yt_time = -1.0
                        else:
                            line   = 'The data may violate the upper yellow limit at Year: ' 
                            line   = line + str(ecf.round_up(vtime2))
                            line2  = ''
                            yt_time = vtime2
                            pchk_u  = 1
                    else:
                        if vtime2 == tmax:
                            line2 = 'The data are already in Yellow Upper Violation'
                            yt_time = -1.0
                        else:
                            line2  = 'The data may violate the upper yellow limit  at Year: ' 
                            line2  = line2 + str(ecf.round_up(vtime2))
                            yt_time = vtime2
                            pchk_u  = 1
#
#-- update violation time estimate database
#
    if vupdate == 1:
        vtdata = [yl_time, yt_time, rl_time, rt_time]
        if group in sub_group_list:
            tmsid = msid + '_' + group.lower()
        else:
            tmsid = msid

        ved.incert_data(tmsid, vtdata)

    return [line, line2, pchk_l, pchk_u]


#----------------------------------------------------------------------------------
#-- create_label_html: creating a information label of the each data point       --
#----------------------------------------------------------------------------------

def create_label_html(indata, msid, unit, ltype):
    """
    creating a information label of the each data point
    input:  indata  --- full data table
            msid    --- msid
            unit    --- unit 
            ltype   --- short or long term plot
    output: hlist   --- a list of lines
    """
#
#--- open up the data
#
    [ftime, dnum, start, stop, avg, med, std, dmin, dmax, ylow, ytop,  \
                        rlow, rtop, yl_lim, yu_lim, rl_lim, ru_lim] =indata

    hlist = []
    for k in range(0, len(start)):

        if ltype == 'long':
            ptime = compute_yday(ftime[k])
        else:
            ptime = "%3.2f" % round(ftime[k], 2)

        line = '<table border=1 cellpadding=2 style="text-align:center;background-color:yellow;">'

        tdline = '<td style="text-align:center;">'

        line = line + '<tr><th>Time</th>'
        line = line + tdline + ptime          + '</td></tr>'

        line = line + '<tr><th># of Data </th>'
        line = line + tdline + str(dnum[k])   + '</td></tr>'

        line = line + '<tr><th>Average   </th>'
        line = line + tdline + str(avg[k])    + '</td></tr>'

        line = line + '<tr><th>Median    </th>'
        line = line + tdline + str(med[k])    + '</td></tr>'

        line = line + '<tr><th>Sandard Deviation </th>'
        line = line + tdline + str(std[k])    + '</td></tr>'

        line = line + '<tr><th>Min       </th>'
        line = line + tdline + str(dmin[k])   + '</td></tr>'

        line = line + '<tr><th>Max       </th>'
        line = line + tdline + str(dmax[k])   + '</td></tr>'

        line = line + '<tr><th>% of Lower Yellow Violation </th>'
        line = line + tdline + str(ctop(ylow[k]))   + '%</td></tr>'

        line = line + '<tr><th>% of Upper Yellow Violation </th>'
        line = line + tdline + str(ctop(ytop[k]))   + '%</td></tr>'

        line = line + '<tr><th>% of Lower Red Violation    </th>'
        line = line + tdline + str(ctop(rlow[k]))   + '%</td></tr>'

        line = line + '<tr><th>% of Upper Red Violation    </th>'
        line = line + tdline + str(ctop(rtop[k]))   + '%</td></tr>'

        line = line + '<tr><th>Lower Yellow Limit </th>'
        line = line + tdline + str(yl_lim[k]) + '</td></tr>'

        line = line + '<tr><th>Upper Yellow Limit </th>'
        line = line + tdline + str(yu_lim[k]) + '</td></tr>'

        line = line + '<tr><th>Lower Red Limit    </th>'
        line = line + tdline + str(rl_lim[k]) + '</td></tr>'

        line = line + '<tr><th>Upper Red Limit    </th>'
        line = line + tdline + str(ru_lim[k]) + '</td></tr>'

        line = line + '</table>'
        line = line + '<div style="padding-bottom:10px;"></div>'

        hlist.append(line)
        
    return hlist

#----------------------------------------------------------------------------------
#-- compute_yday: convert fractional year to <year>-<ydate> format               --
#----------------------------------------------------------------------------------

def compute_yday(ltime):
    """
    convert fractional year to <year>-<ydate> format
    input:  ltime   --- fractional year
    output: ptime   --- <year>-<ydate>
    """

    year = int(ltime)
    if mcf.is_leapyear(year):
        base = 366
    else:
        base = 365

    yday = int((ltime - year) * base)
    lday = str(yday)
    lday = mcf.add_leading_zero(lday, dlen=3)

    ptime = str(year) + '-' + lday

    return ptime

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def ctop(val):

    out = "%2.1f" % round(100 * val, 1)

    return out

#----------------------------------------------------------------------------------
#-- adjust_lim_list: adjust the limit area so that it covers xmin to xmax        --
#----------------------------------------------------------------------------------

def adjust_lim_list(alist):
    """
    adjust the limit area so that it covers xmin to xmax
    input:  alist   --- data list
    output: slist   --- adjusted list
    """
#
#--- some data has open limit at beginning; fill them
#
    val = alist[0]
    pos = 0
    for k in range(0, len(alist)):
        if abs(alist[k]) >= 9e6:
            continue
        if abs(alist[k]) == 999:
            continue
        if abs(alist[k]) == 998:
            continue
        val = alist[k]
        pos = k
        break

    if pos > 0:
        for k in range(0, pos+1):
            alist[k] = val
#
#--- make sure that the area covers from xmin to xmax
#
    aa    = numpy.array([val])
    bb    = numpy.array([alist[-1]])
    slist = three_array_add(aa, alist, bb)
#
#--- special adjustment for the no limit cases
#
    alist = list(slist)
    slist = []
    for ent in alist:
        if abs(ent) >= 9e6:
            slist.append(ent/abs(ent) * 9e12)
        elif abs(int(ent)) in [998,999]:
            slist.append(ent/abs(ent) * 9e12)
        else:
            slist.append(ent)
    slist = numpy.array(slist)

    return slist

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def three_array_add(a1, a2, a3):

    slist = numpy.concatenate((a1, a2))
    slist = numpy.concatenate((slist, a3))

    return slist

#----------------------------------------------------------------------------------
#-- read_msid_data_full: read the data of msid                                       ---
#----------------------------------------------------------------------------------

def read_msid_data_full(dfile, msid,  ltype, ptype='static'):
    """
    read the data of msid
    input:  dfile   --- data file name
            msid    --- msid
            ltype   --- data type: week, short, one, five, long
    output: pdata   --- a two dimensional array of data
                        xtime  = pdata[0]
                        dnum   = pdata[1]
                        start  = pdata[2]
                        stop   = pdata[3]
                        avg    = pdata[4]
                        med    = pdata[5]
                        std    = pdata[6]
                        dmin   = pdata[7]
                        dmax   = pdata[8]
                        ylow   = pdata[9]
                        ytop   = pdata[10]
                        rlow   = pdata[11]
                        rtop   = pdata[12]
                        yl_lim = pdata[13]
                        yu_lim = pdata[14]
                        rl_lim = pdata[15]
                        ru_lim = pdata[16]
                        pcolor = pdata[17] --- 0, 1, or 2: see color_table at beginning
            byear   --- base year for short term plot
    """
#
#--- compaciscent needs a special treatment
#
    mc = re.search('tc$', msid)
    if mc is not None:
        msid  = msid.replace('tc', 't')
        dfile = dfile.replace('tc_', 't_')

    today = ecf.find_current_stime()
    if ltype == 'week':
        cut = today - 7 * 86400
    elif ltype == 'short':
        #cut = today - 95 * 86400
        cut = today - 366 * 86400
    elif ltype == 'one':
        cut = today - 366 * 86400
    elif ltype == 'five':
        cut = today - 5 * 366 * 86400
    else:
        cut = 0

    if ptype == 'inter':
        cut = 0

    f    = pyfits.open(dfile)
    data = f[1].data
    f.close()

    if len(data) == 0:
        return na

    if cut > 0:
        mask = data['time'] > cut
        data = data[mask]

    dtime  = data['time']

    dnum   = data['dcount']
    avg    = data[msid]
    med    = data['med']
    std    = data['std']
    dmin   = data['min']
    dmax   = data['max']
    ylow   = data['ylower']
    ytop   = data['yupper']
    rlow   = data['rlower']
    rtop   = data['rupper']
    yl_lim = data['ylimlower']
    yu_lim = data['ylimupper']
    rl_lim = data['rlimlower']
    ru_lim = data['rlimupper']

    if ltype == 'week':
        skp = 3
    elif ltype in ['short', 'one']:
        skp =  10
    else:
        skp = 5

    if skp > 1:
        dtime  = dtime[0::skp]
        dnum   = dnum[0::skp]
        avg    = avg[0::skp]
        med    = med[0::skp]
        std    = std[0::skp]
        dmin   = dmin[0::skp]
        dmax   = dmax[0::skp]
        ylow   = ylow[0::skp]
        ytop   = ytop[0::skp]
        rlow   = rlow[0::skp]
        rtop   = rtop[0::skp]
        yl_lim = yl_lim[0::skp]
        yu_lim = yu_lim[0::skp]
        rl_lim = rl_lim[0::skp]
        ru_lim = ru_lim[0::skp]
#
    byear = 1999
    xtime = []
    for k in range(0, len(dtime)):
        if ltype in ['week', 'short', 'one']:
            yday = mcf.chandratime_to_yday(dtime[k])
            year = int(float(mcf.convert_date_format(dtime[k], ifmt='chandra', ofmt='%Y')))
            if k == 0:
                byear = year
            else:
                if year > byear:
                    if mcf.is_leapyear(year):
                        base = 366
                    else:
                        base = 365
                    yday += base 

            xtime.append(yday)
        else:
            fyear = mcf.chandratime_to_fraq_year(dtime[k])
            xtime.append(fyear)

    start  = []
    stop   = []
    pcolor = []
    rm_id  = []

    for k in range(0, len(xtime)):
        if k > 0:
            tstart = 0.5 * ( float(xtime[k-1] + float(xtime[k])))
            tstop  = float(xtime[k]) + 0.5 * (float(xtime[k]) -  float(xtime[k-1]))
        else:
            tstart = float(xtime[k]) - 0.5 * (float(xtime[k+1]) -  float(xtime[k]))
            tstop  = float(xtime[k]) + 0.5 * (float(xtime[k+1]) -  float(xtime[k]))
        start.append(tstart)
        stop.append(tstop)

        if abs(yl_lim[k]) > 6e6:
            pcolor.append(0)

        else:
            if (avg[k] not in [998, 999])     and ((avg[k] > ru_lim[k]) or (rtop[k] > 0.7)):
                pcolor.append(1)

            elif (avg[k] not in [-999, -998]) and ((avg[k] < rl_lim[k]) or (rlow[k] > 0.7)):
                pcolor.append(1)

            elif (avg[k] not in  [998, 999])  and ((avg[k] > yu_lim[k]) or (ytop[k] > 0.7)): 
                pcolor.append(2)

            elif (avg[k] not in [-999, -998]) and ((avg[k] < yl_lim[k]) or (ylow[k] > 0.7)):
                pcolor.append(2)

            else:
                pcolor.append(0)
        if dmax[k] > 9.0e8 or dmin[k] < -9.0e8:
            rm_id.append(k)

#
#--- if the avg is totally flat, the plot wil bust; so change tiny bit at the last entry
#
    if len(avg) > 0:
        test = numpy.std(avg)
    else:
        test = 0

    if test == 0:
        alen = len(avg) - 1
        avg[alen] = avg[alen] * 1.0001
        
    pcolor = numpy.array(pcolor)

    plist  = [xtime, dnum,  start, stop, avg, med, std,  \
                dmin, dmax, ylow, ytop, rlow, rtop, yl_lim, yu_lim, rl_lim, ru_lim, pcolor]
#
#--- if there is extremely large values, drop them
#
    rm_rate = float(len(rm_id)) / float(len(xtime))
    if rm_rate < 0.1:
        plist = remove_extreme(plist, rm_id)
#
#--- convert into numpy array then all to float entry
#
    pdata  = numpy.array(plist)
    pdata  = pdata.astype(float)

    return [pdata, byear]

#----------------------------------------------------------------------------------
#-- remove_extreme: remove the elements of the lists by given indecies           --
#----------------------------------------------------------------------------------

def remove_extreme(plist, rm_id):
    """
    remove the elements of the lists by given indecies
    input:  plist   --- a list of lists
            rm_id   --- a list of indecies to be removed
    output: u_lsit  --- a list of updated lists
    """

    u_list = []
    for alist in plist:
        new_a = numpy.delete(numpy.array(alist), rm_id)
        u_list.append(new_a)


    return u_list

#----------------------------------------------------------------------------------
#-- convert_stime_into_year: convert time in seconds from 1998.1.1 to fractional year 
#----------------------------------------------------------------------------------

def convert_stime_into_year(stime):
    """
    convert time in seconds from 1998.1.1 to fractional year
    input:  stime   --- time in seconds from 1998.1.1
    output: ytime   --- time in fractional year
            year    --- year 
            base    --- the number of the days in that year, either 365 or 366
    """

    date = Chandra.Time.DateTime(stime)

    year = float(date.year)
    yday = float(date.yday)
    hrs  = float(date.hour)
    mins = float(date.min)
    secs = float(date.sec)

    if mcf.is_leapyear(year):
        base = 366
    else:
        base = 365

    ytime = year + (yday + hrs / 24.0 + mins / 1440.0 + secs / 86400.0) / base

    return [ytime, year, base]

#----------------------------------------------------------------------------------
#-- set_x_range: find plotting x range                                          ---
#----------------------------------------------------------------------------------

def set_x_plot_range(x, ltype):
    """
    setting x plotting range
    input:  x       --- a list of x values
            ltype   --- data type; week, short, one, five, long
    output: xmin    --- xmin
            xmax    --- xmax
            xpos    --- x position of the text to be placed
    """

    if ltype  == 'long':
        xmin  = 2000
        xmax  = ecf.current_time() + 3
        xmax  = int(xmax)

    elif ltype == 'five':
        xmax  = ecf.current_time() + 1
        xmax  = "%4.1f" % round(xmax, 1)
        xmax  = int(float(xmax))
        xmin  = xmax - 6.0
        xmin  = "%4d" % round(xmin, 1)
        xmin  = int(float(xmin))

    elif ltype == 'year':
        xmax  = max(x)
        xmax  = "%4.1f" % round(xmax, 1)
        xmax  = int(float(xmax)) + 30
        xmin  = xmax - 396

    elif ltype == 'short':
        xmax  = max(x)
        xmax  = "%4.1f" % round(xmax, 1)
        xmax  = int(float(xmax)) + 10
        xmin  = xmax - 100

    else:
        xmin  = min(x)
        xmax  = max(x)
        xdff  = xmax - xmin
        xmin -= 0.01 * xdff
        xmax += 0.06 * xdff
        xmin  = 0.1 * (int(10*xmin) -1)
        xmax  = 0.1 * (int(10*xmax) +1)

    xdiff = xmax - xmin
    xpos  = xmin + 0.05 * xdiff
    if ltype =='':
        xpos  = xmax - 0.1 * xdiff

    return [xmin, xmax, xpos]

#----------------------------------------------------------------------------------
#-- set_y_plot_range: find plotting y range                                     ---
#----------------------------------------------------------------------------------

def set_y_plot_range(x, y=[], ltype=''):
    """
    find plotting y range
    input:  x       --- a list of y if only one array is given; otherwise a list of x
            y       --- a list of y data if it is given
            ltype   --- week, short, one, five, long
    output: [ymin, ymax, ypos]
    """
    if y != []:
#
#--- remove all dummy values and the values outside of the range
#
        bound  = max(x) - set_x_bound(ltype)
    
        udata = []
        for k in range(0, len(x)):
            if x[k] < bound:
                continue
    
            elif y[k] in [-999, -998,-99, 99, 998, 999]:
                continue
    
            else:
                udata.append(y[k])
    else:
        udata = []
        for k in range(0, len(x)):
            if x[k] in [-999, -998,-99, 99, 998, 999]:
                continue
            else:
                udata.append(x[k])
#
#--- remove possible extreme outlayers from both ends before getting min and max
#
    udata.sort()

    lcnt  = len(udata)
    p     = int(0.02 * lcnt)
    test  = udata[p:lcnt-p]

    ymin  = min(test)
    ymax  = max(test)
    if ymin == ymax:
        ymax = ymin + 0.5
        ymin = ymin - 0.5
    else:
        ydiff = ymax - ymin 
        ymin -= 0.2 * ydiff
        ymax += 0.2 * ydiff

    ydiff = ymax - ymin
    ypos  = ymax - 0.1 * ydiff

    return  [ymin, ymax, ypos]

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def set_x_bound(ltype):

    if ltype == 'week':
        bound = 8.0
    elif ltype == 'short':
        bound = 100.0
    elif ltype == 'one':
        bound = 370.0
    elif ltype == 'five':
        bound = 5.5
    else:
        bound = 100.

    return bound

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def select_data_position(mtype):

    if mtype == 'mid':
        pos = 4
    elif mtype == 'min':
        pos = 7
    elif mtype == 'max':
        pos = 8

    return pos

#----------------------------------------------------------------------------------
#-- predict_trend: create moving average of envelope around the average data      -
#----------------------------------------------------------------------------------

def predict_trend(xtime, yset, ltype, mtype):
    """
    create moving average of envelope around the average data
    input:  xtime   --- time in seconds from 1998.1.1
            yset    --- y data set from the following:
                        pdata   --- a two dimensional arry of data.
                        xtime  = pdata[0]
                        dnum   = pdata[1]
                        start  = pdata[2]
                        stop   = pdata[3]
                        avg    = pdata[4]
                        med    = pdata[5]
                        std    = pdata[6]
                        dmin   = pdata[7]
                        dmax   = pdata[8]
                        ylow   = pdata[9]
                        ytop   = pdata[10]
                        rlow   = pdata[11]
                        rtop   = pdata[12]
                        yl_lim = pdata[13]
                        yu_lim = pdata[14]
                        rl_lim = pdata[15]
                        ru_lim = pdata[16]
                        pcolor = pdata[17]
            ltype   --- long or short
            mtype   --- mid, min, or max
    output: tlim    --- prediction starting point in time
            tmax    --- prediction ending point in time
            min_a   --- intercept of the bottom prediciton line
            min_b   --- slope of the bottom prediction line
            max_a   --- intercept of the top prediction line
            max-b   --- slope of the top prediction line
            xcent   --- a list of x value for moving average
            y_avg   --- a list of moving average of  center value
            y_min   --- a list of moving averages of y min envelop
            y_max   --- a list of moving averages of y max envelop
    """
#
#--- pdata[0] is time and pdata[5] is med, pdata[6] is std
#
    dlen   = len(xtime)
    tmax   = max(xtime)

    period = set_period(ltype)
    if ltype == 'week':
        period *=2

    tlim   = tmax - period
#
#--- center envelope
#
    [x, y]     = select_y_data_range(xtime, yset, period, top=2)
    [xmc, ymc] = get_moving_average_fit(x, y, period)
#
#--- bottom envelope
#
    [xbot, ybot] = select_y_data_range(xtime, yset, period, top=0)
    [xmb, ymb]   = get_moving_average_fit(xbot, ybot, period)
#
#--- top envelope
#
    [xtop, ytop] = select_y_data_range(xtime, yset, period, top=1)
    [xmt, ymt]   = get_moving_average_fit(xtop, ytop, period)

    if len(xmb) == 0:
        ymb = ymc
    elif len(xmb) < len(xmc):
        [xmb, ymb] = adjust_entry(xmc, xmb, ymb)

    if len(xmt) == 0:
        ymt = ymc
    elif len(xmt) < len(xmc):
        [xmt, ymt] = adjust_entry(xmc, xmt, ymt)
#
#--- estimate intercept and slope from the last two data points
#
    try:
        [min_a, min_b, min_d] = get_int_slope(xbot, ybot, [xmb[-2], xmb[-1]], [ymb[-2], ymb[-1]], period)
    except:
        [min_a, min_b, min_d] = [0,0,0]
    try:
        [cnt_a, cnt_b, cnt_d] = get_int_slope(x,    y,    [x[-2],   x[-1]],   [y[-2],   y[-1]],   period, two=0)
    except:
        [cnt_a, cnt_b, cnt_d] = [0,0,0]
    try:
        [max_a, max_b, max_d] = get_int_slope(xtop, ytop, [xmt[-2], xmt[-1]], [ymt[-2], ymt[-1]], period)
    except:
        [max_a, max_b, max_d] = [0,0,0]

#
#---- adjust length of lists
#
    xlen  = len(xmc)
    yblen = len(ymb)
    ytlen = len(ymt)

    if xlen < yblen:
        ymb = ymb[:xlen]
    elif xlen > yblen:
        diff  = xlen - yblen
        for k in range(0, diff):
            ymb.append(ymb[-1])

    if xlen < ytlen:
        ymt = ymt[:xlen]
    elif xlen > ytlen:
        diff  = xlen - ytlen
        for k in range(0, diff):
            ymt.append(ymt[-1])

    return [tlim, tmax, cnt_a, cnt_b, cnt_d,  min_a, min_b, min_d, max_a, max_b,max_d, xmc, ymc, ymb, ymt]

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def adjust_entry(xc, x, y):

    diff = len(xc) - len(x)
    if xc[0] < x[0]:
        yval = y[0]
        temp = []
        for k in range(0, diff):
            temp.append(yval)

        y = temp + y

    else:
        yval = y[-1]
        temp = []
        for k in range(0, diff):
            temp.append(yval)

        y =  y + temp

    return [xc, y]


#----------------------------------------------------------------------------------
#-- set_period: assign numeric step interval for the given time interval indicator 
#----------------------------------------------------------------------------------

def set_period(ltype):
    """
    assign numeric step interval for the given time interval indicator
    input:  ltype   --- week, short, one, finve, long
    output: period  --- numeric step value for the ltype
    """

    if ltype ==  'long':
        period = 1.0            #--- a year interval
    elif ltype == 'five':
        period = 1.0            #--- a half year interval
    elif ltype == 'week':
        period = 1.0            #--- a day interval
    elif ltype == 'year':       
        period = 30.0           #--- 30 day interval
    else:
        period = 10.0           #--- 10 day interval

    return period

#----------------------------------------------------------------------------------
#-- get_moving_average_fit: get moving average                                   --
#----------------------------------------------------------------------------------

def get_moving_average_fit(x, y, period):
    """
    get moving average 
    input:  x       --- a list of x values
            y       --- a list of y values
            period  --- a period of the step
    output: [tx1, tx2]  --- a list of lists of x and y values of moving average
    """
#
#--- first find moving average forward, then find moving average backward from the end
#
    try:
        out1 = fma.find_moving_average(x,  y, period , 0)
    except:
        out1 = [[],[]]
    try:
        out2 = fmab.find_moving_average(x, y, period , 0)
    except:
        out2 = [[],[]]
#
#--- combined two of them so that fill all the way
#
    tx1 = out1[0]
    ty1 = out1[1]

    tx2 = out2[0]
    ty2 = out2[1]

    tx3 = []
    ty3 = []
    for k in range(0, len(tx2)):
        if tx2[k] > tx1[-1]:
            tx3.append(tx2[k])
            ty3.append(ty2[k])

    tx1 = tx1 + tx3
    ty1 = ty1 + ty3

    return [tx1, ty1]

#----------------------------------------------------------------------------------
#-- select_y_data_range: select data based on middle, top 25%, or bottom 25% area -
#----------------------------------------------------------------------------------

def select_y_data_range(xtime, yval, period, top=1):
    """
    select data based on middle, top 25%, or bottom 25% area 
    input:  xtime   --- a list of x values
            yval    --- a list of y values
            period  --- a compartment size
            top     --- position of the selction: 0: bottom 25%, 1: top 25%, other middle 96%
    output: xadjust --- a list of x data in the selected range
            yadjust --- a list of y data in the selected range
    """
#
#--- set percentaile limit values
#
    if top == 0:
        p1 = 2
        p2 = 25
    elif top == 1:
        p1 = 75
        p2 = 98
    else:
        p1 = 2
        p2 = 98

    xt   = numpy.array(xtime)
    yt   = numpy.array(yval)
    aind = xt.argsort()
    xt   = xt[aind[::]]
    yt   = yt[aind[::]]
    xadjust = []
    yadjust = []
#
#--- set step size and numbers of periods: select the data span to 20% of the period given 
#--- so that the bottom and top spans do not change much during the data selection period
#
    step  = 0.2 * period
    start = xt[0]
    stop  = xt[-1]
    snum  = int((stop - start) / step) + 1

    begin = 0
    for k in range(0, snum):
#
#--- select the data in that period
#
        xs = []
        ys = []
        sn = 0
        lstop = (k+1) * step + start
        for m in range(begin, len(xt)):
            if xt[m] > lstop:
                break
            else:
                xs.append(xt[m])
                ys.append(yt[m])
                sn += 1

        if len(xs) < 1:
            continue
#
#--- reset the starting spot for the next round
#
        begin += sn
#
#--- find given percentaile range
#
        try:
            limb = percentile(ys, p1)
            limt = percentile(ys, p2)
            if limb == None or limt == None:
                limb = min(ys)
                limt = max(ys)
        except:
            limb = min(ys)
            limt = max(ys)
        lavg = 0.5 * (limb + limt)

        for n in range(0, len(xs)):
#
#--- if the data is in the range, use the value
#
            if (ys[n] >= limb) and (ys[n] <= limt):
                xadjust.append(xs[n])
                yadjust.append(ys[n])
#
#--- if not, use the average
#
            else:
                xadjust.append(xs[n])
                yadjust.append(lavg)

    return [xadjust, yadjust]

#----------------------------------------------------------------------------------
#-- percentile: extract the value for the given percentale value                 --
#----------------------------------------------------------------------------------

def percentile(v_list, percent, key=lambda x:x):
    """
    extract the value for the given percentale value
    input:  v_list  --- a list of the data
            percent --- a percentile position (e.t. 75 for 75% percentile)
    output: the vaule at the percentile position
    """
    if len(v_list) < 1:
        return 0.0
#
#-- if it is asking 50% point
#
    if percent == 50:
        return numpy.median(numpy.array(v_list))
#
#--- otherwise, do other checking
#
    v_list.sort()

    if isinstance(v_list, list):
        return None

    k = (len(v_list)-1) * (percent/100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(v_list[int(k)])

    d0 = key(v_list[int(f)]) * (c-k)
    d1 = key(v_list[int(c)]) * (k-f)
    return d0 + d1

#----------------------------------------------------------------------------------
#-- create_secondary_bound: create boundray around the data based on med value   --
#----------------------------------------------------------------------------------

def create_secondary_bound(m_list, b_list, loc=0):
    """
    create boundray around the data based on med value
    this is used only when the main moving average boundary failed to be created
    input:  m_list  --- a list of main data
            b_list  --- a list of boundary data (either min or max data list)
            loc:    --- whether is this bottom or top boundary 0: lower or 1: upper
    output: e_list  --- a list of estimated values
    """
    if len(b_list) < 1:
        return []
    else:
        med = numpy.median(numpy.array(b_list))
        sign = 1.0
        if loc == 0:
            sign = -1.0
        e_list = []
        for ent in m_list:
            val = ent + sign * med
            e_list.append(val)
    
        return e_list

#----------------------------------------------------------------------------------
#-- get_int_slope: estimate a + b * x line  with a robust method               ----
#----------------------------------------------------------------------------------

def get_int_slope(x, y, xl, yl, period, two=1):
    """
    estimate a + b * x line  with a robust method and then compare with a
    simple two point estimate and choose a shallower slope fitting
    input:  x       --- a list of x values
            y       --- a list of y values
            xl      --- a secondary list of x value
            yl      --- a seocndary list of y value
    output: a       --- intercept
            b       --- slope
    """
#
#--- choose the data only in the last one year or 10 day (for short)
#
    if not  isinstance(x, numpy.ndarray):
        x = numpy.array(x)      #---- CHECK WHY THESE ARE NOT ARRAY!!!!!!
        y = numpy.array(y)

    bound = max(x) - period
    index = numpy.where(x > bound)
    xtemp = x[index]
    ytemp = y[index]
#
#--- limit data in well inside of the good data
#
    [xsave, ysave] = select_data_with_y_sigma(xtemp, ytemp, 3.5)
#
#--- if there are not enough data, give up the fitting
#
    if len(xsave) < 3:
        return [999, 999, 999]
    try:
#
#--- fit least sq straight line
#
        try:
            [a, b, dx]  = rbl.robust_fit(xsave, ysave)
            [ax, bx, d] = least_sq(xsave, ysave)
        except:
            [a, b, d] = least_sq(xsave, ysave)
#
#--- two point fit
#
        [al, bl]  = get_int_slope_supl(xl, yl)
#
#--- choose a shallower slope fit
#

        if two > 0:
            if abs(bl) < abs(b):
                a = al
                b = bl
    except:
        a = 999
        b = 999
        d = 999

    return [a, b, d]

#----------------------------------------------------------------------------------
#-- select_data_with_y_cond: select data within sval signma in y direction       --
#----------------------------------------------------------------------------------

def select_data_with_y_sigma(x, y, sval):
    """
    select data within sval signma in y direction
    input   x       --- a array of x values
            y       --- a array of y values
            sval    --- sigma value to be covered
    output: [xo, yo]    --- a list of arrays of data in the boundaries
    """
    if len(x) > 0:
        avg = numpy.mean(y)
        std = numpy.std(y)
        yb  = avg - sval * std
        yt  = avg + sval * std
    
        index = numpy.where(y > yb)
        xs    = x[index]
        ys    = y[index]
    
        index = numpy.where(ys < yt)
        xo    = xs[index]
        yo    = ys[index]
    else:
        xo    = x
        yo    = y

    return [xo, yo]


#----------------------------------------------------------------------------------
#-- get_int_slope: estimate a + b * x line from the last two data points         --
#----------------------------------------------------------------------------------

def get_int_slope_supl(x, y):
    """
    estimate a + b * x line from the last two data points
    input:  x       --- a list of x values
            y       --- a list of y values
    output: icept   --- intercept
            slope   --- slope
    """

    k  = len(x)
    k1 = k -1
    k2 = k -2
    while x[k1] == x[k2]:
        k2 -= 1
        if k2 < 0:
            return [0, 0]

    try:
        slope = (y[k1] - y[k2]) / (x[k1] - x[k2])
        icept = y[k1] - slope * x[k1]

        return [icept, slope]
    except:
        return [999,999]

#---------------------------------------------------------------------------------------------------
#-- least_sq: compute a linear fit parameters using least sq method  ---
#---------------------------------------------------------------------------------------------------

def least_sq(xval, yval, ecomp = 1, remove=100):

    """
    compute a linear fit parameters using least sq method
    Input:  xval    --- a list of independent variable
            yval    --- a list of dependent variable
            ecomp   --- indicator whether to compute the slope error; 0: no, >0: yes
            remove  --- when you want to remove the outlayers, set this value lower than 100 (%)
    Output: aa      --- intersect
            bb      --- slope
            be      --- slope error
    """
    if remove < 100:
        [xval, yval] = remove_extreme_vals(xval, yval, p=remove)
    
    itot= len(xval)
    tot = float(itot)
    sx  = 0.0
    sy  = 0.0
    sxy = 0.0
    sxx = 0.0
    syy = 0.0
    
    for j in range(0, itot):
        sx  += xval[j]
        sy  += yval[j]
        sxy += xval[j] * yval[j]
        sxx += xval[j] * xval[j]
        syy += yval[j] * yval[j]
    
    delta = tot * sxx - sx * sx
    if delta == 0:
        return [0.0, 0.0, 0.0]
    else:
        try:
            aa = (sxx * sy  - sx * sxy) / delta
        except:
            aa = 0.0
        try:
            bb = (tot * sxy - sx * sy)  / delta
        except:
            bb = 0.0

        be = 0.0
    
        if ecomp > 0:
            if tot - 2 < 1:
                bb = 999.
            else:
                try:
                    ss = (syy + tot*aa*aa + bb*bb*sxx - 2.0 *(aa*sy - aa*bb*sx + bb*sxy)) /(tot - 2.0)
                    be = math.sqrt(tot * ss / delta)
                except:
                    be = 999.
     
        return (aa, bb, be)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def remove_extreme_vals(x, y, p=98):
    """
    remove outlayers
    input:  x   --- x values
    y   --- y values
    p   --- how much include in the data in percentage; e.g.98-- remove top and bottom 1%
    """
    if len(x) < 10:
        return [x, y]
    
    xa = numpy.array(x)
    ya = numpy.array(y)
    
    cut= 100 - p
    bcut   =  0.5 * cut
    tcut   = p + bcut
    blim   = numpy.percentile(ya, bcut)
    tlim   = numpy.percentile(ya, tcut)
    select = [(ya > blim) & (ya < tlim)]
    
    xo = list(xa[select])
    yo = list(ya[select])
    
    return [xo, yo]


#----------------------------------------------------------------------------------
#-- predict_violation: predict possible limti violations                         --
#----------------------------------------------------------------------------------

def predict_violation(a, b, current, vlimit, side = 1):
    """
    predict possible limti violations
    input:  a       --- intercept of the predicted line
            b       --- slope of the predicted line
            current --- the current value
            vlimit  --- limit value
            side    --- lower (0) or upper (1) limit
    output: rtime   --- estimated violation time. if no violation return 0
    """
    if b == 999:
        return 0

    vlimit = float(vlimit)

    rtime  = 0
    now      = a + b * current
    if side > 0:
        if now > vlimit:
            rtime = current
    else:
        if now < vlimit:
            rtime = current

    if rtime == 0:
#
#--- if the slope is too steep, something is not right; so ignore the future estimation
#
        if  (b == 0) or (b == 999):
            rtime = 0
        else:
            estimate = (vlimit - a) / b
            if estimate > current:
                rtime = estimate
            else:
                rtime = 0

    return rtime

#----------------------------------------------------------------------------------
#-- check_dir_exist: chek whether the directory exists, and if not, create one    -
#----------------------------------------------------------------------------------

def check_dir_exist(tdir):
    """
    chek whether the directory exists, and if not, create one
    input:  tdir    --- directory name
    output: tdir    --- created directory
    """
    if not os.path.isdir(tdir):
        cmd = 'mkdir ' + tdir
        os.system(cmd)

#----------------------------------------------------------------------------------
#-- read_template: read template                                                 --
#----------------------------------------------------------------------------------

def read_template(fname, repl=[]):
    """
    read template
    input:  fname   --- template file name
            repl    --- a list of lists:[<tag to be replaced>, <replacing value>]
    output: out     --- template read
    """
    infile = house_keeping + 'Templates/' + fname
    with  open(infile, 'r') as f:
        out    = f.read()
#
#--- if substitue strings are given, replace them before return
#
    if len(repl) > 0:
        for rset in repl:
            out = out.replace(rset[0], rset[1])

    return out

#----------------------------------------------------------------------------------
#-- set_req: setting the input arguments                                         --
#----------------------------------------------------------------------------------

def set_req(argv):
    """
    setting the input arguments 
    input:  argv    --- input from the argv line
    output: r_dict  --- a dictionry containing argument keys and values
    """

    keys = ['qtype', 'msid_list', 'ds', 'ms']
    vals = ['inter', 'msid_list', 'all', 'all']
    r_dict = dict(zip(keys, vals))

    for k in range(1, len(argv)):
        atemp = re.split('=', argv[k])
        r_dict[atemp[0]] = atemp[1]

    return r_dict
        
#----------------------------------------------------------------------------------
#-- create_limit_table: create a limit table for msid                            --
#----------------------------------------------------------------------------------

def create_limit_table(msid, group,  unit,  xmin, xmax):
    """
    create a limit table for msid
    input:  msid    --- msid
            unit    --- unit
            xmin    --- xmin
            xmax    --- xmax
    output: <web_dir>/Limit_table/<msid>_limit_table.html
    """
#
#--- read limit data
#
    pmsid  = drop_suffix(msid)
    l_list = ecf.set_limit_list(pmsid)
#
#--- read header part
#
    title  = msid + ' limit table'
    repl   = [["#MSID#",  title], ["#JAVASCRIPT#", ''], ["#STYLE#", ""]]
    line   = read_template('html_head', repl )
#
#--- except a few, all temperatures are in K
#
    if unit == 'DEGF':
        tline = msid.upper() + ' (K)'
    elif unit == 'DEGC':
        tline = msid.upper() + ' (K)'
    elif unit == '':
        tline = msid.upper()
    else:
        tline = msid.upper() + ' (' + unit + ')'

    bgline = '<th style="background-color:'

    line = line + '<h2>' + tline + '</h2>\n'
    line = line + '<table border=1 cellpadding=2>\n'
    line = line + '<tr><th>Start Time</th>\n'
    line = line + '<th>Stop Time</th>\n'
    line = line + bgline + 'yellow">Yellow Lower</th>\n'
    line = line + bgline + 'yellow">Yellow Upper</th>\n'
    line = line + bgline + 'red">Red Lower</th>\n'
    line = line + bgline + 'red">Red Upper</th>\n'
    line = line + '</tr>\n'

    for k in range(0, len(l_list)):
        alist = l_list[k]

        [astart, byear, base] = convert_stime_into_year(float(alist[0]))
        [astop,  byear, base] = convert_stime_into_year(float(alist[1]))
#
#--- there are often the data with <start>=<stop>, drop them
#
        if astart == astop:
            continue

        astart  = float('%4.2f' % (round(astart,2)))
        astop   = float('%4.2f' % (round(astop, 2)))

        if k == 0:
            if astart > xmin:
                astart = '---'

        if k == (len(l_list) -1):
            astop = "---"
#
#---    alist: ymin, ymax, rmin, rmax in position of 2 to 5
#
        tlist   = [astart, astop] + alist[2:6]
#
#--- create each row
#
        line = line + '<tr>\n'

        for tval in  tlist:
            line = line + '<td style="text-align:center;">' + str(tval) + '</td>\n'

        line = line + '</tr>\n'

    line = line + '</table>\n'
    line = line + '</body>\n</html>\n'

    o_dir = web_dir + group + '/'
    check_dir_exist(o_dir)
    o_dir = o_dir + 'Limit_table/'
    check_dir_exist(o_dir)

    file_name = o_dir + msid + '_limit_table.html'
    with  open(file_name, 'w') as fo:
        fo.write(line)

#------------------------------------------------------------------------------------
#-- update_fit_result_file: update fitting line result file for the give type  --
#------------------------------------------------------------------------------------

def update_fit_result_file(otype, mtype, rfile, result):
    """
    update fitting line result file for the give type
    input:  otype   --- length of the data type (week, short, one, five, long)
            mtype   --- data type (mid, min, max)
            rfile   --- the result file name
            result  --- the new fitted result
    output: rfile   --- updated result file
    """
#
#--- read the saved results
#
    try:
        out  = mcf.read_data_file(rfile)
        out  = list(set(out))
    except:
        out  = []
#
#--- find the line with the same type and replace it with the new result
#
    save = []
    chk  = 0
    for ent in out:
        test = otype + ':' + mtype
#
#--- remove the following few lines after cleaning finishes (Jan 17, 2018)
#
        mc = re.search(test, ent)
        if (ent.startswith('w:')) or  (ent.startswith('e:')) or (ent.startswith('k:')):
            continue
    
        if mc is not None:
            save.append(result)
            chk = 1
        else:
            if ent == "" or ent == '\s+':
                continue
            save.append(ent)
    
    if chk == 0:
        save.append(result)
#
#--- update the file
#
    sline = ''
    for ent in save:
        if ent == '':
            continue
        sline = sline + str(ent) + '\n'
    
    with open(rfile, 'w') as fo:
        fo.write(sline)

