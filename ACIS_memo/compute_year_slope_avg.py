#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       acis_cti_plot.py: plotting cti trends                                                   #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               Last update: Jan 27, 2015                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

#
#--- check whether this is a test case
#
comp_test = 'live'
if len(sys.argv) == 2:
    if sys.argv[1] == 'test':   #---- test case
        comp_test = 'test'
    elif sys.argv[1] == 'live': #---- automated read in
        comp_test = 'live'
    else:
        comp_test = sys.argv[1].strip() #---- input data name
#
#--- reading directory list
#
if comp_test == 'test' or comp_test == 'test2':
    path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py_test'
else:
    path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import robust_linear        as robust     #---- robust linear fit

from kapteyn import kmpfit
#import kmpfit_chauvenet     as chauv
#
#--- temp writing file name
#
rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)
#--- today date to set plotting range
#
today_time = tcnv.currentTime()
txmax      = today_time[0] + 1.5
#
#--- fitting line division date
#
img_div = 2011
spc_div = 2011
bks_div = 2009

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def run_for_year(year):

    base  = 3600. * 24. * 365
    lyear = str(year)
    head  = '/data/mta/Script/ACIS/CTI/Data/Det_Data_adjust/mn_ccd'
    head2 = '/data/mta/Script/ACIS/CTI/Data/Data_adjust/mn_ccd'

    ssave = []
    esave = []
    asave = []
    for k in range(0, 10):
        if k ==5 or k == 7:
            ccd = head2 + str(k)
        else:
            ccd  = head + str(k)

        f    = open(ccd, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

        time = []
        vals = []
        for ent in data:
            atemp = re.split('\s+', ent)
            btemp = re.split('-',   atemp[0])

            if btemp[0] == lyear:
                ctemp = re.split('\+\-', atemp[1])
                q0    = float(ctemp[0])

                ctemp = re.split('\+\-', atemp[2])
                q1    = float(ctemp[0])

                ctemp = re.split('\+\-', atemp[3])
                q2    = float(ctemp[0])

                ctemp = re.split('\+\-', atemp[4])
                q3    = float(ctemp[0])

                if q0 < 0.0: 
                    continue

                avg = 0.25 * ( q0 + q1 + q2 + q3)
                time.append(float(atemp[-2])/ base )
                vals.append(q0)

        [intc, slope, ierr, serr] = linear_fit(time, vals, 100)
        mval = numpy.mean(vals)
        lslope = "%4.3f" % round(slope * 1e1, 3)
        lerr   = "%4.3f" % round(serr  * 1e1, 3)
        lavg   = "%4.3f" % round(mval, 3)
        ssave.append(lslope)
        esave.append(lerr)
        asave.append(lavg)


    line = '<tr>\n'
    for k in range(0, 10):
        line =  line + '<td>' + ssave[k] + '<br />+/-' + esave[k] + '</td>\n' 

    line = line + '</tr>'

    print line
    print '\n\n'

    line = '<tr>\n'
    for k in range(0, 10):
        line =  line + '<td>' + asave[k] + '</td>\n' 

    line = line + '</tr>'

    print line

                


#---------------------------------------------------------------------------------------------------
#-- linear_fit: linear fitting function with 99999 error removal                                 ---
#---------------------------------------------------------------------------------------------------

def linear_fit(x, y, iter):

    """
    linear fitting function with -99999 error removal 
    Input:  x   --- independent variable array
            y   --- dependent variable array
            iter --- number of iteration to computer slope error
    Output: intc --- intercept
    slope--- slope
    """

#
#--- first remove error entries
#
    sum  = 0 
    sum2 = 0
    tot  = 0
    for i in range(0, len(y)):
        if y[i] > 0:
            sum  += y[i]
            sum2 += y[i] *y[i]
            tot  += 1
    if tot > 0:
        avg = sum / tot
        sig = math.sqrt(sum2/tot - avg * avg)
    else: 
        avg = 3.0

    lower =  0.0
    upper = avg + 2.0
    xn = []
    yn = []

    for i in range(0, len(x)):
#        if (y[i] > 0) and (y[i] < yupper):            #--- removing -99999/9999 error
        if (y[i] > lower) and (y[i] < upper):
            xn.append(x[i])
            yn.append(y[i])

    if len(yn) > 10:
        [intc, slope, serr] = robust.robust_fit(xn, yn, iter=iter)
#        [intc, slope, serr] = robust.robust_fit(xn, yn, iter=1)
    else:
        [intc, slope, serr] = [0, 0, 0]
#
#--- modify array to numpy array
#
#    d = numpy.array(xn)
#    v = numpy.array(yn)
#
#--- kmpfit
#
#    param = [0, 1]
#    fitobj = kmpfit.Fitter(residuals=residuals, data=(d,v))
#    fitobj.fit(params0=param)
#
#    [intc, slope] = fitobj.params
#    [ierr, serr]  = fitobj.stderr

#
#--- chauvenet exclusion of outlyers and linear fit
#
#    [intc, slope, ierr, serr] = chauv.run_chauvenet(d,v)

    return [intc, slope, 0.0, serr]


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def model(p, x):
    a, b = p
    y = a + b * x
    return y

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def residuals(p, data):

    x, y = data

    return  y - model(p, x)


#---------------------------------------------------------------------------------------------------
#-- convTimeFullColumn: convert time format to fractional year for the entire array              ---
#---------------------------------------------------------------------------------------------------

def convTimeFullColumn(time_list):

    """
    convert time format to fractional year for the entire array
    Input:  time_list   --- a list of time 
    Output: converted   --- a list of tine in dom
    """

    converted = []
    for ent in time_list:
        time  = tcnv.dateFormatConAll(ent)
        year  = time[0]
        ydate = time[6]
        chk   = 4.0 * int(0.25 * year)
        if year == chk:
            base = 366
        else:
            base = 365
        yf = year + ydate / base
        converted.append(yf)    

    return converted

#---------------------------------------------------------------------------------------------------
#-- separateErrPart: separate  the error part of each entry of the data array                    ---
#---------------------------------------------------------------------------------------------------

def separateErrPart(data):

    """
    drop the error part of each entry of the data array
    Input:  data    --- data array
    Ouptput:cleane  --- data array without error part
            err     --- data array of error
    """

    cleaned = []
    err     = []
    for ent in data:
        atemp = re.split('\+\-', ent)
        cleaned.append(float(atemp[0]))
        err.append(float(atemp[1]))

    return [cleaned,err]

#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, ydiv,  yErrs = [], intList = [], slopeList = [], intList2 = [], slopeList2 = []):

    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            yMinSets: a list of ymin 
            yMaxSets: a list of ymax
            entLabels: a list of the names of each data

    Output: a png plot: out.png
    """

#
#--- set line color list
#
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(ySets)
#
#--- start plotting each data
#
    for i in range(0, len(entLabels)):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec "ax%s = plt.subplot(%s)"       % (str(i), line)
        exec "ax%s.set_autoscale_on(False)" % (str(i))      #---- these three may not be needed for the new pylab, but 
        exec "ax%s.set_xbound(xmin,xmax)"   % (str(i))      #---- they are necessary for the older version to set

        exec "ax%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (str(i))
        exec "ax%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (str(i))

        xdata  = xSets[i]
        ydata  = ySets[i]

        echk   = 0
        if len(yErrs) > 0:
            yerr = yErrs[i]
            echk = 1
        pchk   = 0
        if len(intList) > 0:
            intc    = intList[i] 
            slope   = slopeList[i]
            pstart  = intc + slope * xmin
            pstop   = intc + slope * xmax 
            pchk    = 1
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=3.0, lw =0)
        if echk > 0:
#            p, = plt.errorbar(xdata, ydata, yerr=yerr,  marker='.', markersize=1.5, lw =0)
            plt.errorbar(xdata, ydata, yerr=yerr,color=colorList[i],  markersize=3.0, fmt='.')
        if pchk > 0:
            plt.plot([xmin,xmax], [pstart, pstop],   colorList[i], lw=1)

#
#--- add legend
#
        ltext = entLabels[i] + ' / Slope (CTI/Year): ' + str(round(slopeList[i] * 1.0e2, 3)) + ' x 10**-2   '
#        ltext = ltext + str(round(slopeList2[i] * 1.0e2, 3)) + ' x 10**-2 '
        leg = legend([p],  [ltext], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec "ax%s.set_ylabel(yname, size=8)" % (str(i))

#
#--- add x ticks label only on the last panel
#
###    for i in range(0, tot):

        if i != tot-1: 
            exec "line = ax%s.get_xticklabels()" % (str(i))
            for label in  line:
                label.set_visible(False)
        else:
            pass

    xlabel(xname)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig('out.png', format='png', dpi=100)


#---------------------------------------------------------------------------------------------------
#-- update_cti_page: update cti web page                                                         ---
#---------------------------------------------------------------------------------------------------

def update_cti_page():

    """
    update cti web page
    Input:  None but use <house_keeping>/cti_page_template
    Output: <web_page>/cti_page.html
    """

    ctime = tcnv.currentTime("Display")

    file  = house_keeping + 'cti_page_template'
    html  = open(file, 'r').read()

    html  = html.replace('#DATE#', ctime)

    out   = web_dir + 'cti_page.html'
    fo    = open(out, 'w')
    fo.write(html)
    fo.close()

#--------------------------------------------------------------------

if __name__== "__main__":

    if len(sys.argv) > 1:
        year = sys.argv[1]
        year.strip()

        run_for_year(year)
    else:
        print "Provide year"

