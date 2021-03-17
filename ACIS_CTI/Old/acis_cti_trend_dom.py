#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       acis_cti_trend_dom.py: computing trend line with dom                                    #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               Last update: Jun 16, 2014                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import numpy
import math

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
#
#--- set several lists
#

dir_set  = ['Data2000', 'Data119', 'Data7000', 'Data_adjust', 'Data_cat_adjust']
det_set  = ['Det_Data2000', 'Det_Data119', 'Det_Data7000', 'Det_Data_adjust', 'Det_Data_cat_adjust']
out_set  = ['Plot2000', 'Plot119', 'Plot7000', 'Plot_adjust', 'Plot_cat_adjust']
dout_set = ['Det_Plot2000', 'Det_Plot119', 'Det_Plot7000', 'Det_Plot_adjust', 'Det_Plot_cat_adjust']


elm_set  = ['al', 'mn', 'ti']


#---------------------------------------------------------------------------------------------------
#-- fit_line_with_dom: plot indivisual CCD CTI trends and combined CTI trends for all different cases    --
#---------------------------------------------------------------------------------------------------

def fit_line_with_dom(indirs, outdirs, allccd = 1):

    """
    plot indivisual CCD CTI trends and combined CTI trends for all different cases 
    Input:  indirs  --- a list of directories which contain data
            outdirs --- a list of directories which the plots will be deposted
            allccd  --- if it is 1, the funciton processes all ccd, if it is 0, detrended ccd only
    Output: plots such as <elm>_ccd<ccd#>_plot.png, imaging_<elm>_plot.png, etc 
            fitting_result  --- a file contains a table of fitted parameters
            combined data sets  such as imging_<elm>_comb, spectral_<elm>_comb etc saved in data_dir/<indir>
    """

    if allccd == 0:                                         #--- detrended data case
         ccd_list = [0, 1, 2, 3, 4, 6, 8, 9]
    else:
         ccd_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]          #---- normal case

    xname    = 'Time (Year)'
    yname    = '(S/I)x10**4'

    for k in range(0, len(indirs)):
        dir  = indirs[k]
#        file = data_dir + dir + '/fitting_result'
        file = web_dir + outdirs[k] + '/fitting_result_dom'
        fo   = open(file, 'w')

        for elm in elm_set:
            uelm = elm
            uelm.lower()
            line = '\n\n' + uelm + ' K alpha' + '\n'
            fo.write(line)
#
#--- write a table head
#
            fo.write('----------\n')
            fo.write('CCD     Quad0                           Quad1                           Quad2                           Quad3\n')
            fo.write('        Slope           Sigma           Slope           Sigma           Slope           Sigma           Slope           Sigma\n\n')

#
#--- read each ccd data set
#
            for ccd in ccd_list:

                file = data_dir +  dir + '/' +  elm + '_ccd' + str(ccd)
                f    = open(file, 'r')
                data = [line.strip() for line in f.readlines()]
                f.close()
#
#--- fit a line and get intercepts and slopes: they are save in a list form
#
                (xSets, ySets, yErrs) = rearrangeData(data)
                (intList, slopeList, serrList)    = fitLines(xSets,  ySets)

                line = str(ccd) + '\t'
                fo.write(line)

                entLabels = []
                for i in range(0, 4):
#
#--- create a title label for plot
#
                    line   = 'CCD' + str(ccd) + ': Node' + str(i) 
                    entLabels.append(line)
#
#--- print out the slope and the error for each quad
#
                    line = "%3e\t%3e\t" % (slopeList[i], serrList[i])
                    fo.write(line)

                fo.write('\n')
#
#--- create combined plots (image ccd, spec ccd, backside ccds)
#
            sccd_list = [0, 1, 2, 3]
            (newX, newY, newE, intc, slope, serr) = compute_fitting(elm, sccd_list, 'imaging', indirs[k], outdirs[k])
            fo.write('ACIS-I Average: ')
            line = "%3e\t%3e\n" % (slope, serr)
            fo.write(line)

            sccd_list = [4, 6, 7, 9]
            (newX, newY, newE, intc, slope, serr) = compute_fitting(elm, sccd_list, 'spectral', indirs[k], outdirs[k])
            fo.write('ACIS-S Average w/o BI: ')
            line = "%3e\t%3e\n" % (slope, serr)
            fo.write(line)

            if allccd == 1:
                sccd_list = [5]
                (newX, newY, newE, intc, slope, serr) = compute_fitting(elm, sccd_list, 'backside_5', indirs[k], outdirs[k])
                fo.write('Back Side CCD 5: ')
                line = "%3e\t%3e\n" % (slope, serr)
                fo.write(line)

                sccd_list = [7]
                (newX, newY, newE, intc, slope, serr) = compute_fitting(elm, sccd_list, 'backside_7', indirs[k], outdirs[k])
                fo.write('Back Side CCD 7: ')
                line = "%3e\t%3e\n" % (slope, serr)
                fo.write(line)

        fo.close()


#---------------------------------------------------------------------------------------------------
#-- compute_fitting: create combined data set to prepare for the plot                                --
#---------------------------------------------------------------------------------------------------

def compute_fitting(elm, ccd_list, head, indir, outdir):

    """
    create combined data set to prepare for the plot
    Input:  elm     --- element
            ccd_list--- a list of ccd to be used
            head    --- a header for the plot/data table
            indir   --- a directory where the data is kept
            outdir  --- a directory where the plot will be deposted
    Output: a list of 
            newX        --- combined X values in a list
            newY        --- combined Y values in a list
            newE        --- combined Error of Y 
            intList[0]  --- intercept
            slopeList[0]--- slope
            serrList[0] --- erorr of the slope
            data    such as imaging_<elm>_comb this is kept in <indir>
    """

#
#
    comb_data = []
    for ccd in ccd_list:
        file = data_dir +  indir +'/' +  elm + '_ccd' + str(ccd)
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        comb_data = comb_data + data

#
#--- separate the data into each node
#
    (xSets,  ySets, yErrs) = rearrangeData(comb_data)

    xlist   = numpy.array(xSets[0])
    qlist   = [[] for x in range(0, 4)]
    elist   = [[] for x in range(0, 4)]
    qsorted = [[] for x in range(0, 4)]
    esorted = [[] for x in range(0, 4)]

    for i in range(0, 4):
        qlist[i] = numpy.array(ySets[i])
        elist[i] = numpy.array(yErrs[i])

    order    = numpy.argsort(xlist)
    xsorted  = xlist[order]
    for i in range(0, 4):
        qsorted[i]  = qlist[i][order]
        esorted[i]  = elist[i][order]
#
#--- print out combined data
#
    file = data_dir + indir + '/' + head + '_' + elm + '_comb'
    fp   = open(file, 'w')

    newX = []
    newY = []
    newE = []
    yVar = []
    eVar = []
    start = 0
    stop  = 30
    for i in range(0, len(xsorted)):
        x = xsorted[i]
        if (x >= start) and (x < stop):
            for j in range(0, 4):
                yVar.append(qsorted[j][i])
                eVar.append(esorted[j][i])
        else:
            tcnt = 0
            sum  = 0
            sum1 = 0
            sum2 = 0
            esum = 0
            for k in range(0, len(yVar)):
#
#--- remove -99999 error
#
                if yVar[k]  > 0.0:
                    err2  = (1/eVar[k]) * (1/eVar[k])
                    var   = yVar[k] * err2
                    sum  += var
                    sum1 += yVar[k]
                    sum2 += yVar[k] * yVar[k] 
                    esum += err2
                    tcnt  += 1

            if tcnt > 0:
                meanv = sum / esum
                sigma = math.sqrt(1.0 / sum2)
#                avg   = sum1 / tcnt
#                sigma = math.sqrt(sum2 / tcnt - avg * avg)
                mid   = int(0.5 * (start + stop))
                newX.append(mid)
                newY.append(meanv)
                newE.append(sigma)

                line = str(mid) + '\t' + str(meanv) + '\t' + str(sigma) + '\n'
                fp.write(line)

            start = stop
            stop  = start + 30
            yVar = []
            eVar = []
            for j in range(0, 4):
                yVar.append(qsorted[j][i])
                eVar.append(esorted[j][i])

    fp.close()
#
#--- since fitLines takes only a list of lists, put in a list
#
    XSets = [newX]
    YSets = [newY]
#
#--- find a fitting line parameters
#
    (intList, slopeList, serrList) = fitLines(xSets, ySets)
#
#--- set Y plot range
#
    ypositive = []
    for ent in newY:
        if ent > 0:
            ypositive.append(ent)

    return (newX, newY, newE, intList[0], slopeList[0], serrList[0])

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def fyear_to_dom(dlist):

    dom_list = []
    for ent in dlist:
        year = int(ent)
        fy   = ent - year
        if tcnv.isLeapYear(year) == 1:
            base = 366
        else:
            base = 365
        ydate = int(base * fy)

        dom  = tcnv.YdateToDOM(year, ydate)
        dom_list.append(dom)

    return dom_list

#---------------------------------------------------------------------------------------------------
#-- isolateData: separate a table data into arrays of data                                       ---
#---------------------------------------------------------------------------------------------------

def isolateData(ccd, elm, quad, dir_set):

    """
    separate a table data into arrays of data
    Input:  ccd     --- ccd #
            elm     --- name of element
            quad    --- quad #
            dir_set --- a list of data directories 
    Output: xSets   --- a list of lists of x values in fractional year
            ySets   --- a list of lists of y values
    """

    xSets    = []
    ySets    = []
    eSets    = []

    for dir in dir_set:

        file = data_dir + dir + '/' + elm + '_ccd' + str(ccd)
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
#
#--- separeate a table into each column array
#
        coldata = mcf.separate_data_to_arrys(data)
#
#--- convert time into dom ( xxxfractional year) (a list of time)
#
        time    = convTimeFullColumn2(coldata[0])

        xSets.append(time)
        tmax    = max(time)

#
#--- the data part come with cti +- error. drop the error part
#
        [ydata, yerr]  = separateErrPart(coldata[quad + 1])
        ySets.append(ydata)
        eSets.append(yerr)
#
#--- round the data accuracy to 0.1
#
        ypositive = []
        for ent in ydata:
            if ent > 0:
                ypositive.append(ent)

    return [ xSets, ySets, eSets]


#---------------------------------------------------------------------------------------------------
#-- rearrangeData: separate a table data into time and 4 quad data array data sets                --
#---------------------------------------------------------------------------------------------------

def rearrangeData(data):

    """
    separate a table data into time and 4 quad data array data sets
    Input:  data    --- input table data
    Output: xSets   --- a list of lists of x values
            ySets   --- a list of lists of y values
            yErrs   --- a list of lists of y errors
    """

    xSets    = []
    ySets    = []
    yErrs    = []

    coldata  = mcf.separate_data_to_arrys(data)

    time     = convTimeFullColumn(coldata[0])           #---- time in fractional year 
    time2    = convTimeFullColumn2(coldata[0])          #---- time in  dom
#
#--- go around each quad data
#
    for i in range(1, 5):
        xSets.append(time2)
        data  = []
        error = []
        for ent in coldata[i]:
            atemp = re.split('\+\-', ent)
            data.append(float(atemp[0]))
            error.append(float(atemp[1]))

        ySets.append(data)
        yErrs.append(error)

        ypositive = []
        for ent in data:
            if ent > 0:
                ypositive.append(ent)

    return (xSets,  ySets, yErrs)

#---------------------------------------------------------------------------------------------------
#-- fitLines: find intercepts and slopes  of sets of x and y values                               --
#---------------------------------------------------------------------------------------------------

def fitLines(xSets, ySets, echk = 1):

    """
    find intercepts and slopes  of sets of x and y values
    Input:  xSets   --- a list of independent variable lists
            ySets   --- a list of dependent variable lists
            echk    --- if it is larger than 0, compute slope error (default: 1)
    Output: inList  --- a list of intercepts
            slopeList--- a list of slopes
            serrlist--- a list of slope errors
    """

    intList    = []
    slopeList  = []
    serrList   = []

    for i in range(0, len(xSets)):
        [intc, slope, ierr, serr]     = linear_fit(xSets[i], ySets[i])

        intList.append(intc)
        slopeList.append(slope)
        serrList.append(serr)

    return (intList, slopeList, serrList)


#---------------------------------------------------------------------------------------------------
#-- linear_fit: linear fitting function with 99999 error removal                                 ---
#---------------------------------------------------------------------------------------------------

def linear_fit(x, y):

    """
    linear fitting function with -99999 error removal 
    Input:  x   --- independent variable array
    y   --- dependent variable array
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
        if (y[i] > lower) and (y[i] < upper):
            xn.append(x[i])
            yn.append(y[i])

    if len(yn) > 10:
        [intc, slope, serr] = robust.robust_fit(xn, yn, iter=50)
    else:
        [intc, slope, serr] = [0, 0, 0]

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

def convTimeFullColumn(time_list):

    """
    convert time format to fractional year for the entire array
    Input:  time_list   --- a list of time 
    Output: converted   --- a list of tine in fractional year
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
#-- convTimeFullColumn2: convert time format to dom  for the entire array                        ---
#---------------------------------------------------------------------------------------------------

def convTimeFullColumn2(time_list):

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
        dom   = tcnv.YdateToDOM(year, ydate)
        converted.append(dom)    

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


#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    fit_line_with_dom(dir_set, out_set)
    fit_line_with_dom(det_set, dout_set, allccd = 0)


