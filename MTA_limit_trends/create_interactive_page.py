#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################    
#                                                                                   #
#       create_interactive_page.py: create interactive html page for a given msid   #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Feb 03, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys

#
#--- set python environment if it is not set yet
#
if 'PYTHONPATH' not in os.environ:
        os.environ['SAK']        = "/proj/sot/ska"
        os.environ['PYTHONPATH'] = "/data/mta/Script/Python3.8/envs/ska3-shiny/lib/python3.8/site-packages:/data/mta/Script/Python3.8/lib/python3.8/site-packages"
        try:
            os.execv(sys.argv[0], sys.argv)
        except Exception:
            print('Failed re-exec:', exc)
            sys.exit(1)
import re
import string
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
#
#--- interactive plotting module
#
import plotly.express       as px
import plotly.graph_objects as go
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import run_fetch                as rf
import mta_common_functions     as mcf  #---- contains other functions commonly used in MTA scripts
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
import read_limit_table         as rlt  #---- read limit table and craete msid<--->limit dict
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

css = """
    p{
        text-align:left;
    }
"""
#
#---  get dictionaries of msid<-->unit and msid<-->description
#
[udict, ddict] = ecf.read_unit_list()

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
#--- a list of those with sub groups
#
sub_list_file  = house_keeping + 'sub_group_list'
sub_group_list = mcf.read_data_file(sub_list_file)

#-------------------------------------------------------------------------------------------
#-- create_interactive_page: update all msid listed in msid_list                                 --
#-------------------------------------------------------------------------------------------

def create_interactive_page(msid, group, mtype, start, stop, step):
    """
    create an interactive html page for a given msid
    input:  msid    --- msid
            group   --- group name
            mtype   --- mid, mde, min, or max
            start   --- start time
            stop    --- stop time
            step    --- bin size in seconds
    """
    start = ecf.check_time_format(start)
    stop  = ecf.check_time_format(stop)
#
#--- create msid <---> unit dictionary
#
    [udict, ddict] = ecf.read_unit_list()
#
#--- read mta database
#
    mta_db = ecf.read_mta_database()
#
#--- read mta msid <---> sql msid conversion list
#
    mta_cross = ecf.read_cross_check_table()
#
#--- get limit data table for the msid
#
    try:
        uck   = udict[msid]
        if uck.lower() == 'k':
            tchk = 1
        else:
            tchk  = ecf.convert_unit_indicator(uchk)
    except:
        tchk  = 0

    glim  = make_glim(msid)
#
#--- extract data from archive
#
    chk = 0
    try:
        [ttime, tdata] = rf.get_data(msid, start, stop)
    except:
#
#--- if no data in archive, try mta local database
#
        try:
            [ttime, tdata] = get_mta_fits_data(msid, group, start, stop)
#
#--- if it is also failed, return the empty data set
#
        except:
            chk = 1
            ttime = []
            tdata = []
#
#--- only short_p can change step size (by setting "step")
#
    if chk == 0:
        data_p = process_day_data(msid, ttime, tdata, glim,  step=step)
    else:
        data_p = 'na'
#
#--- create interactive html page
#
    create_html_page(msid, group, data_p, mtype, step)

#----------------------------------------------------------------------------------------
#-- create_html_page: create indivisual html pages for all msids in database           --
#----------------------------------------------------------------------------------------

def create_html_page(msid, group,  data_p, mtype, bin_size):
    """
    """
    try: 
        unit    = udict[msid]
        descrip = ddict[msid]
    except:
        unit    = ''
        descrip = ''
#
#--- pdata is two dim array of data (see read_data for details). flist is sub category 
#--- of each data set
#
    if data_p == 'na':
        pout  = '<h1 style="padding-top:40px;padding-bottom:40px;">NO DATA FOUND</h1>\n'

    else:
        [pdata, byear] = read_msid_data_full(data_p, msid)
#
#--- create the plot
#
        create_trend_plots(msid, group, pdata, byear, unit, 'week', mtype)

#--------------------------------------------------------------------------------
#-- create_trend_plots: create interactive trend plot                         ---
#--------------------------------------------------------------------------------

def create_trend_plots(msid, group, pdata, byear,  unit, ltype, mtype):
    """
    create static and interactive trend plot
    input:  msid    --- msid
            group   --- the gruop name to which msid belogs
            pdata   --- a list of arrays of data; see read_data for details
            year    --- a base year for the short term plot
            unit    --- unit of msid
            ltype   --- 'short' or 'long'           --- period length indicator
            mtype   --- 'mid', 'med', 'min', or 'max'      --- data type indicator
    output: pout    --- plot in html format
    """
    if not (len(pdata) > 0 and len(pdata[0]) > 0):
        print(msid + ': empty data file')
        return na

    if len(pdata[0]) < 10:
        return False
#
#--- get a data position of mtype data in pdata 
#
    [pos, cname]    = select_data_position(mtype)
#
#--- column name
#
    xname    = 'Time ' 
    if ltype == 'long':
        xname = xname + ' (Year)'
    else:
        xname = xname + ' (Ydate Year: ' + str(byear) + ')'

    mname    = msid.upper()
    if unit != '':
#
#--- special treatment for temp unit "F"
#
        if unit == 'F':
            unit = 'K'
        mname = mname + ' (' + unit + ')'
        if mtype == 'mid':
            mnam = ': Mean'
        elif mtype == 'med':
            mnam = ': Median'
        elif mtype == 'min':
            mnam = ': Minimum'
        elif mtype == 'max':
            mnam = ': Maximum'
        else:
            mnam = ''

        mname = mname + ' ' + mnam

    colnames = ['Time', '# of Data',  'Mean', 'Median', 'Sadnard Deviation', \
                'Min', 'Max', '% of Lower Yellow Violation', \
                '% of Upper Yellow Violation', '% of Lower Red Violation',\
                '% of Upper Red Violation', 'Lower Yellow Limit', \
                'Upper Yellow Limit', 'Lower Red Limit', 'Upper Red Limit']
#
#--- set data frame
#
    p_dict= {}
    for k in range(0, 2):
        p_dict[colnames[k]] = pdata[k]
    for k in range(2, 15):
        p_dict[colnames[k]] = pdata[k+2]

    p_dict[colnames[0]] = shorten_digit(p_dict[colnames[0]])
    for k in range(2, 7):
        p_dict[colnames[k]] = shorten_digit(p_dict[colnames[k]])
#
#--- get a data position of mtype data in pdata 
#
    [pos, cname]    = select_data_position(mtype)
#
#--- set plotting ranges
#
    [xmin, xmax, xpos] = set_x_plot_range(pdata[0], ltype)
    xchk = xmax - xmin
#
#--- set warning area range lists
#
    [ymin, ymax, ypos] = set_y_plot_range(pdata[0], pdata[pos], ltype)

    [time_save, rb1_save, rb2_save, yb2_save, yt1_save, yt2_save, rt2_save] \
                  = set_warning_area(msid, xmin, xmax, ymin, ymax, byear)


    fig= px.scatter(p_dict, x=colnames[0], y=colnames[pos-2], hover_data=colnames,\
                    labels={colnames[0]:xname, colnames[pos-2]:mname} )
    fig.update_layout(yaxis_range=[ymin,ymax])
#
#---- bottom warning area
#
    fig.add_trace(go.Scatter(x=time_save, y=rb1_save, fill = None,\
                  opacity=0.3,  mode='lines'))

    fig.add_trace(go.Scatter(x=time_save, y=rb2_save, fill='tonexty',\
                  opacity=0.3, mode='none', fillcolor='rgba(255,0,0,0.3)'))

    fig.add_trace(go.Scatter(x=time_save, y=yb2_save, fill='tonexty',\
                  opacity=0.3, mode='none', fillcolor='rgba(255,255,0,0.3)'))
#
#--- top warning area
#
    fig.add_trace(go.Scatter(x=time_save, y=yt1_save, fill = 'tonexty',\
                  opacity=0.0,  mode='none', fillcolor='rgba(255,255,0,0.0)'))

    fig.add_trace(go.Scatter(x=time_save, y=yt2_save, fill='tonexty', \
                  opacity=0.3, mode='none', fillcolor='rgba(255,255,0,0.3)'))

    fig.add_trace(go.Scatter(x=time_save, y=rt2_save, fill='tonexty',\
                  opacity=0.3, mode='none', fillcolor='rgba(255,0,0,0.3)'))


    fig.update_layout(yaxis=dict(range=[ymin, ymax]))
    fig.layout.update(showlegend=False)

    hname = web_dir + 'Interactive/' + msid + '_inter_avg.html'
    fig.write_html(hname)

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
#-- set_warning_area: set yellow and red violation zones                         --
#----------------------------------------------------------------------------------

def set_warning_area_xxx(pdata, xmin, xmax, ymin, ymax):
    """
    set yellow and red violation zones
    input:  pdata   --- a two dimensional array of data (see read_data)
            xmin    --- xmin
            xmax    --- xmax
            ymin    --- ymin
            ymax    --- ymax
    output: a list of lists:
                    time_save   --- time list
                    rb1_save    --- lower boundary of the bottom red area
                    rb2_save    --- top   boundary of the bottom red area
                    yb1_save    --- lower boundary of the bottom yellow area
                    yb2_save    --- top   boundary of the bottom yellow area
                    yt1_save    --- lower boundary of the top yellow area
                    yt2_save    --- top   boundary of the top yellow area
                    rt1_save    --- lower boundary of the top red area
                    rt2_save    --- top   boundary of the top red area
    """

    l_len = len(pdata[0]) + 2
#
#--- filling up the beginning of the plot to the end of the plot
#
    aa        = numpy.array([xmin])
    bb        = numpy.array([xmax])
    time_save = three_array_add(aa, pdata[0], bb)

    if pdata[13][-1] < ymin:
        brbnd = pdata[13][-1]
    else:
        brbnd = ymin

    if pdata[16][-1] > ymax:
        trbnd = pdata[13][-1]
    else:
        trbnd = ymax

    brbnd = 0.0
    if brbnd > ymin:
        brbnd = ymin

    trbnd = 9e9
    if trbnd < ymax:
        trbnd = ymax

    rb1_save  = [brbnd] * l_len
    rb2_save  = adjust_lim_list(pdata[15])
    yb1_save  = rb2_save
    yb2_save  = adjust_lim_list(pdata[13])

    yt1_save  = adjust_lim_list(pdata[14])
    yt2_save  = adjust_lim_list(pdata[16])
    rt1_save  = yt2_save
    rt2_save  = [trbnd] *l_len

    return [time_save, rb1_save, rb2_save, yb1_save, yb2_save, \
            yt1_save, yt2_save, rt1_save, rt2_save]

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

def read_msid_data_full(data_p, msid):
    """
    read the data of msid
    input:  data_p  --- a list of lists of data
            msid    --- msid
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

    today  = ecf.find_current_stime()

    dtime  =  data_p[0]
    dnum   =  data_p[1]
    avg    =  data_p[2]
    med    =  data_p[3]
    std    =  data_p[4]
    dmin   =  data_p[5]
    dmax   =  data_p[6]
    ylow   =  data_p[7]
    ytop   =  data_p[8]
    rlow   =  data_p[9]
    rtop   =  data_p[10]
    yl_lim =  data_p[11]
    yu_lim =  data_p[12]
    rl_lim =  data_p[13]
    ru_lim =  data_p[14]

    skp    = 3
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
    out   = Chandra.Time.DateTime(dtime[2]).date
    atemp = re.split(':', out)
    byear = int(float(atemp[0]))
    xtime = []
    for k in range(0, len(dtime)):

        yday = chandratime_to_yday(dtime[k], byear)
        xtime.append(yday)

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
        xmin  = 1999
        xmax  = ecf.current_time() + 1
        xmax  = int(xmax)

    elif ltype == 'five':
        xmax  = ecf.current_time() + 1
        xmax  = "%4.1f" % round(xmax, 1)
        xmax  = int(float(xmax))
        xmin  = xmax - 6.0
        xmin  = "%4d" % round(xmin, 1)
        xmin  = int(float(xmin))

    elif ltype == 'short':
        xmax  = max(x)
        xmax  = "%4.1f" % round(xmax, 1)
        xmax  = int(float(xmax))
        xmin  = xmax - 90.0
        xmin  = "%4d" % round(xmin, 1)
        xmin  = int(float(xmin))
        xmax += 10

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
        udata = []
        for k in range(0, len(x)):
            if y[k] in [-999, -998,-99, 99, 998, 999]:
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
    test  = udata

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
        pos   = 4
        cname = 'Mean'

    elif mtype == 'med':
        pos = 5
        cname  = 'Median'
    elif mtype == 'min':
        pos    = 7
        cname  = 'Min'
    elif mtype == 'max':
        pos = 8
        cname  = 'Max'

    return [pos, cname]

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

#-------------------------------------------------------------------------------------------
#-- process_day_data: extract data from the archive and compute the stats           ---
#-------------------------------------------------------------------------------------------

def process_day_data(msid, time, data, glim, step = 3600.0):
    """
    extract data from the archive and compute the stats
    input:  msid    --- msid of the data
            time    --- array of time
            data    --- array of data
            glim    --- a list of limit tables
            step    --- interval of the data. defalut: 3600 sec
    output: a list of lists which contain:
                btime   --- a list of time in sec from 1998.1.1
                bdata   --- a list of the  mean of each interval
                bmed    --- a list of the median of each interval
                bstd    --- a list of the std of each interval
                bmin    --- a list of the min of each interval
                bmax    --- a list of the max of each interval
                byl     --- a list of the rate of yellow lower violation
                byu     --- a list of the rate of yellow upper violation
                brl     --- a list of the rate of red lower violation
                bru     --- a list of the rate of red upper violation
                bcnt    --- a list of the total data counts
                byl     --- a list of the lower yellow limits
                byu     --- a list of the upper yellow limits
                brl     --- a list of the lower red limits
                bru     --- a list of the upper red limits
    """
    btime = []
    bdata = []
    bmed  = []
    bstd  = []
    bmin  = []
    bmax  = []
    byl   = []
    byu   = []
    brl   = []
    bru   = []
    bcnt  = []
    vsave = []
#
#--- extract data from archive
#
    try:
        data  = numpy.array(data)
        dtime = numpy.array(time)
#
#--- remove all "nan" data
#
        mask  = ~(numpy.isnan(data))
        data  = data[mask]
        dtime = dtime[mask]
#
#--- there are glitch values much larger than the real value; remove them
#
        mask  = [data < 9e6]
        data  = data[mask]
        dtime = dtime[mask]
#
#--- devide the data into a 'step' size
#
        spos  = 0
        chk   = 1
        send  = dtime[spos]  + step
        dlen  = len(dtime)

        for k in range(0, dlen):

            if dtime[k] < send:
                chk = 0
                continue
            else:
                rdata = data[spos:k]
                avg   = rdata.mean()
                if len(rdata) < 1:
                    med   = 0.0
                else:
                    med   = numpy.median(rdata)
                sig   = rdata.std()
                amin  = rdata.min()
                amax  = rdata.max()
                stime = dtime[spos + int(0.5 * (k-spos))]
                vlimits = find_violation_range(glim, stime)
                [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)

                btime.append(stime)
                bdata.append(avg)
                bmed.append(med)
                bstd.append(sig)
                bmin.append(amin)
                bmax.append(amax)
                byl.append(yl)
                byu.append(yu)
                brl.append(rl)
                bru.append(ru)
                bcnt.append(tot)
                vsave.append(vlimits)

                spos = k
                send = dtime[k] + step
                chk  = 1
#
#--- check whether there are any left over; if so add it to the data lists
#
        if chk == 0:
            rdata = data[spos:dlen]
            if len(rdata) < 1:
                avg = 0.0
                med = 0.0
            else:
                avg   = rdata.mean()
                med   = numpy.median(rdata)
            sig   = rdata.std()
            amin  = rdata.min()
            amax  = rdata.max()
            stime = dtime[spos + int(0.5 * (k-spos))]
            vlimits = find_violation_range(glim, stime)
            [yl, yu, rl, ru, tot] = find_violation_rate(rdata, vlimits)

            btime.append(dtime[spos + int(0.5 * (k-spos))])
            bdata.append(avg)
            bmed.append(med)
            bstd.append(sig)
            bmin.append(amin)
            bmax.append(amax)
            byl.append(yl)
            byu.append(yu)
            brl.append(rl)
            bru.append(ru)
            bcnt.append(tot)
            vsave.append(vlimits)

        #out = [btime, bdata, bmed, bstd, bmin, bmax, byl, byu, brl, bru, bcnt]
        out = [btime, bcnt,  bdata, bmed, bstd, bmin, bmax, byl, byu, brl, bru]
#
#--- adding limits to the table
#
        vtemp   = [[], [], [], []]
        for k in range(0, len(vsave)):
            for m in range(0, 4):
                vtemp[m].append(vsave[k][m])
        out = out + vtemp
    
    except:
        ftime = 0
        fdata = 0
        fmed  = 0
        fstd  = 0
        fmin  = 0
        fmax  = 0
        ylow  = 0
        yupper= 0
        rlow  = 0
        rupper= 0
        tcnt  = 0

        vlimits = [-9.0e9, -9.0e9, 9.0e9, 9.0e9]
        #out     = [ftime, fdata, fmed, fstd, fmin, fmax, ylow, yupper, rlow, rupper, tcnt]
        out     = [ftime, tcnt,  fdata, fmed, fstd, fmin, fmax, ylow, yupper, rlow, rupper]
        out     = out + vlimits

    return out

#-------------------------------------------------------------------------------------------
#-- find_violation_range: set violation range                                             --
#-------------------------------------------------------------------------------------------

def find_violation_range(glim, time):
    """
    set violation range
    input:  glim    --- a list of lists of violation set [start, stop, yl, yu, rl, ru]
            time    --- time of the violation check
    output: vlimit  --- a four element list of [yl, yu, rl, ru]
    """

    vlimit = [-9.0e9, -9.0e9, 9.0e9, 9.0e9]

    for lim_set in glim:
        start = float(lim_set[0])
        stop  = float(lim_set[1])
        if (time >= start) and (time < stop):
            vlimit = [lim_set[2], lim_set[3], lim_set[4], lim_set[5]]

    return vlimit

#-------------------------------------------------------------------------------------------
#-- find_violation_rate: find rate of yellow, red violations in both lower and upper limits 
#-------------------------------------------------------------------------------------------

def find_violation_rate(carray, limits):
    """
    find rate of yellow, red violations in both lower and upper limits
    input:  carray  --- numpy array of the data
            limits  --- a list of limit [yellow lower, yellow upper, red lower, red upper]
    output: [yl, yu, rl, ru, tot]:  rate of yellow lower
                                    rate of yellow upper
                                    rate of red lower
                                    rate of red upper
                                    totla number of the data
    """
    tot  = len(carray)
    ftot = float(tot)

    yl  = find_num_of_elements(carray, limits[0], side=0)
    yu  = find_num_of_elements(carray, limits[1], side=1)
    rl  = find_num_of_elements(carray, limits[2], side=0)
    ru  = find_num_of_elements(carray, limits[3], side=1)
    yl -= rl
    yu -= ru
#
#--- compute the violation is how many percent of the data
#
    fdiv = ftot /100
    yl =  yl/fdiv
    yu =  yu/fdiv
    rl =  rl/fdiv
    ru =  ru/fdiv

    return [yl, yu, rl, ru, tot]

#-------------------------------------------------------------------------------------------
#-- find_num_of_elements: find the numbers of elements above or lower than limit 
#-------------------------------------------------------------------------------------------

def find_num_of_elements(carray, lim, side=0):
    """
    find the numbers of elements above or lower than limit comparing to the total data #
    input:  carray  --- numpy array of the data
            lim     --- the limit value
            side    --- lower:0 or upper:1 limit
    output: cnt     --- the numbers of the values beyond the limit
    """
#
#--- assume that the huge limit value means that there is no limit
#
    if abs(lim) > 1e6:
        return 0


    if side == 0:
        out = numpy.where(carray < lim)
    else:
        out = numpy.where(carray > lim)

    try:
        cnt = len(out[0])
    except:
        cnt = 0

    return cnt 

#--------------------------------------------------------------------------------
#-- get_mta_fits_data: fetch data from mta local database                      --
#--------------------------------------------------------------------------------

def get_mta_fits_data(msid, group, start, stop):
    """
    fetch data from mta local database
    input:  msid    --- msid
            start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: time    --- time in second from 1998.1.1 for the given period
            vals    --- vals of msid for the given period
    """
#
#--- find a parent group name
#
    pgroup  = 'Comp_save/'
    mc1     = re.search('Deahk', group)
    mc2     = re.search('Grad',  group)
    if mc1 is not None:
        pgroup = 'Deahk_save/'
    elif mc2 is not None:
        pgroup = 'Grad_save/'
#
#--- find which year(s) the requested period falls
#
    date  = Chandra.Time.DateTime(start)
    byear = int(float(date.year))
    date  = Chandra.Time.DateTime(stop)
    eyear = int(float(date.year))
    
    chk   = 0
    for year in range(byear, eyear+1):
        fits = deposit_dir + pgroup + group + '/' + msid + '_full_data_' + str(year) + '.fits'
        if not os.path.isfile(fits):
            fits = deposit_dir + pgroup + group + '/' + msid + '_full_data_' + str(year) + '.fits.gz'
            if not os.path.isfile(fits):
                continue
#
#--- extract the data for the given period
#
        f = pyfits.open(fits)
        data  = f[1].data
        f.close()
        if chk == 0:
            time = data['time']
            vals = data[msid]
            ext  = [(time > start) & (time < stop)]
            time = time[ext]
            vals = vals[ext]
            chk  = 1
        else:
            tmp1 = data['time']
            tmp2 = data[msid]
            ext  = [(tmp1 > start) & (tmp1 < stop)]
            tmp1 = tmp1[ext]
            tmp2 = tmp2[ext]
            time = numpy.append(time, tmp1)
            vals = numpy.append(vals, tmp2)
     
    if chk > 0:
        return [time, vals]
    else:
#
#--- if no data, return False
#
        return False

#------------------------------------------------------------------------------------
#-- shorten_digit: clean up the value so that it show only a few digits            --
#------------------------------------------------------------------------------------

def shorten_digit(alist):
    """
    clean up the value so that it show only a few digits
    input:  alist   --- a list of data
    output: olist   --- a list of data cleaned
    """

    olist = []
    for ent in alist:
        out = '%2.3e' % ent
        val = float(out)
        if val > 1000 or val < 0.001:
            val = out
        else:
            val = str(val)

        olist.append(val)

    return olist

#------------------------------------------------------------------------------------
#-- set_warning_area: create warning area for plotting                             --
#------------------------------------------------------------------------------------

def set_warning_area(msid, xmin, xmax, ymin, ymax, byear):
    """
    create warning area for plotting
    input:  msid    --- msid
            xmin    --- min x
            xmax    --- max x
            ymin    --- min y
            ymax    --- max y
            byear   --- the base year
    output: t_save  --- a list of starting and stopping times in ydate
            bt_lim  --- a list of bottom; usually 0, but can be ymin
            lr_lim  --- a list of lower red limit
            ly_lim  --- a list of lower yellow limit
            uy_lim  --- a list of upper yellow limit
            ur_lim  --- a list of upper red limit
            tp_lim  --- a list of top: usually 9e10, but can be ymax

    """
    msid = msid.lower()

    [limit_dict, cnd_dict] = rlt.get_limit_table()
    
    bval = 0.
    if bval > ymin:
        bval = ymin

    tval = 9e9
    if tval < ymax:
        tval = ymax

    try:
        out      = limit_dict[msid]
        cnd_msid = cnd_dict[msid]

        t_save = []
        bt_lim = []
        lr_lim = []
        ly_lim = []
        uy_lim = []
        ur_lim = []
        tp_lim = []
        chk = 0
        dlen = len(out)
        for ent in out:
            try:
                lim_list = ent[3]['none']
            except:
                continue
#
            x1 = chandratime_to_yday(ent[0], byear)
            x2 = chandratime_to_yday(ent[1] -1.0, byear)
            if x2 < xmin:
                continue

            if x1 < xmin:
                x1 = xmin

            if x1 < xmax and x2 >= xmax:
                x2 = xmax
                chk = 1

            t_save.append(x1)
            t_save.append(x2)

            for k in range(0, 2):
                bt_lim.append(bval)
                ly_lim.append(lim_list[0])
                uy_lim.append(lim_list[1])
                lr_lim.append(lim_list[2])
                ur_lim.append(lim_list[3])
                tp_lim.append(tval)
        

            if chk == 1:
                break
        
    except:
        t_save = [xmin, xmax]
        bt_lim = [-9e10, -9e10]
        lr_lim = [-9e10, -9e10]
        ly_lim = [-9e10, -9e10]
        uy_lim = [9e10,   9e10]
        ur_lim = [9e10,   9e10]
        tp_lim = [9e10,   9e10]

    return [t_save, bt_lim, lr_lim, ly_lim, uy_lim, ur_lim, tp_lim]

#------------------------------------------------------------------------------------
#-- make_glim: create limit list in glim format                                    --
#------------------------------------------------------------------------------------

def make_glim(msid):
    """
    create limit list in glim format
    input:  msid    --- msid
    output: glim    --- a list of list of [<start time> <stop time> <lower yellow> <upper yellow>
                                            <lower red> <upper red>]
                        time is in seconds from 1998.1.1
    """
    msid = msid.lower()
    [limit_dict, cnd_dict] = rlt.get_limit_table()
    out      = limit_dict[msid]
    glim     = []
    for ent in out:
        try:
            lim_list = ent[3]['none']
        except:
            continue
        temp = [ent[0], ent[1], lim_list[0], lim_list[1], lim_list[2], lim_list[3]]

        glim.append(temp)

    if len(glim) == 0:
        glim = [[0,  3218831995, -9e6, 9e6, -9e6, 9e6]]

    return glim

#------------------------------------------------------------------------------------
#-- chandratime_to_yday: convert chandra time into ydate from the 001 day of byear  -
#------------------------------------------------------------------------------------

def chandratime_to_yday(ctime, byear):
    """
    convert chandra time into ydate from the 001 day of byear
    input:  ctime   --- chandra time; seconds from 1998.1.1
            byear   --- the base year
    output: ydate   --- ydate from 001 day of byear
    """

    out = Chandra.Time.DateTime(ctime).date
    atemp = re.split(':', out)
    year  = int(float(atemp[0]))
    ydate = float(atemp[1])
    hh    = float(atemp[2])
    mm    = float(atemp[3])
    ss    = float(atemp[4])

    ydate+= hh /24.0 + mm/1440.0 + ss /86400.0


    if year < byear:
        for tyear in range(year, byear):
            if mcf.is_leapyear(tyear):
                base = 366
            else:
                base = 365

            ydate -= base

    elif year > byear:
        for tyear in range(byear, year):
            if mcf.is_leapyear(tyear):
                base = 366
            else:
                base = 365

            ydate += base

    return ydate

#------------------------------------------------------------------------------------

if __name__ == "__main__":

#        msid   = '1cbat'
#        group  = 'Acistemp'
#        tstart = '2019:001:00:00:00'
#        tstop  = '2019:002:00:00:00'
#        step   = 300.0
#        create_interactive_page(msid, group, tstart, tstop, step)

#        msid   = 'hstrtgrd1'
#        group  = 'Gradhstrut'
#        tstart = '2019:001:00:00:00'
#        tstop  = '2019:002:00:00:00'
#        step   = 300.0
#        create_interactive_page(msid, group, tstart, tstop, step)

    if len(sys.argv) ==  5:
        msid   = sys.argv[1]
        group  = sys.argv[2]
        tstart = sys.argv[3]
        tstop  = sys.argv[4]
        mtype  = 'mid'
        step   = 300.0

        create_interactive_page(msid, group, mtype, tstart, tstop, step)

    elif len(sys.argv) == 6:
        msid   = sys.argv[1]
        group  = sys.argv[2]
        mtype  = sys.argv[3]
        tstart = sys.argv[4]
        tstop  = sys.argv[5]
        step   = int(float(sys.argv[5]))

        create_interactive_page(msid, group, mtype, tstart, tstop, step)

    elif len(sys.argv) == 7:
        msid   = sys.argv[1]
        group  = sys.argv[2]
        mtype  = sys.argv[3]
        tstart = sys.argv[4]
        tstop  = sys.argv[5]
        step   = int(float(sys.argv[6]))
        
        create_interactive_page(msid, group, mtype, tstart, tstop, step)

    else:
        print("Usage: create_interactive_page.py <msid> <group> <mtype> <start> <stop> <bin size> ")
