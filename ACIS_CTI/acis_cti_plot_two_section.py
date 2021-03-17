#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#       acis_cti_plot_two_section.py: plotting cti trends                   #
#                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                   #
#                                                                           #
#               Last update: Mar 02, 2021                                   #
#                                                                           #
#############################################################################

import os
import sys
import re
import string
import operator
import numpy
import time

import matplotlib as mpl
if __name__ == '__main__':
    mpl.use('Agg')
#
#--- pylab plotting routine related modules
#
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines
#
#--- read directory list
#
path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

with open(path, 'r') as f:
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
import mta_common_functions as mcf
import robust_linear        as robust     #---- robust linear fit
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set several lists
#
dir_set   = ['Data2000', 'Data119', 'Data7000', 'Data_adjust', 'Data_cat_adjust']
det_set   = ['Det_Data2000', 'Det_Data119', 'Det_Data7000', 'Det_Data_adjust', 'Det_Data_cat_adjust']
out_set   = ['Plot2000', 'Plot119', 'Plot7000', 'Plot_adjust', 'Plot_cat_adjust']
dout_set  = ['Det_Plot2000', 'Det_Plot119', 'Det_Plot7000', 'Det_Plot_adjust', 'Det_Plot_cat_adjust']
elm_set   = ['al', 'mn', 'ti']
colorList = ['blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive']
#
#--- fitting line division date (in year)
#
img_div = 2012.5
spc_div = 2012.5
bks_div = 2014.5
#
#--- standard y plotting range. this could be overwritten if the data contain larger values
#
y_std_max = 6.0

#---------------------------------------------------------------------------------------
#-- plot_data1: plotting indivisual (CCD/quad) data for 5 different data criteria     --
#---------------------------------------------------------------------------------------

def plot_data1():
    """
    plotting indivisual (CCD/quad) data for 5 different data criteria.
    Input: None, but read from eadh data set: see nam_list
    Output: indivisual data plot in png format. 
    """
    xname    = 'Time (Year)'
    yname    = '(S/I)x10**4'
    nam_list = ['No Correction', 'Temp < -119.7', 'Temp < -119.7 & Time > 7000',\
                'Adjusted', 'MIT/ACIS Adjusted']

    for elm in elm_set:
        for ccd in range(0, 10):
            for quad in range(0, 4):
#
#--- standard CTI plottings
#
                plot_data1_sub(ccd, elm, quad, dir_set, xname, yname, nam_list, "Data_Plot/")
#
#--- detrended CTI plottings
#
                if (ccd != 5) or (ccd != 7):
                    plot_data1_sub(ccd, elm, quad, det_set, xname, yname, nam_list, "Det_Plot/")

#---------------------------------------------------------------------------------------
#-- plot_data1_sub: sub fuction of "plot_data1" to plot indivisula data              ---
#---------------------------------------------------------------------------------------

def plot_data1_sub(ccd, elm, quad, data_set, xname, yname, entLabels, plot_dir):
    """
    sub fuction of "plot_data1" to plot indivisula data
    Input:  ccd     --- ccd #
            elm     --- element
            quad    --- qud #
            data_set--- name of data directory
            xname   --- a label of x axis
            yname   --- a label of y axis
            entLabels--- a set of tiles
            plot_dir--- output directory name
    Output: <web_dir>/<plot_dir>/<elm>_ccd<ccd#>_quad<quad#>_plot.png
    """
#
#--- set fitting line division date
#
    if ccd in [5, 7]:
        ydiv = bks_div
    elif ccd in [4, 6, 8, 9]:
        ydiv = spc_div
    else:
        ydiv = img_div
#
#--- get data of given selection; provide 5 different selection cases
#
    (xSets, ySets, eSets) = isolateData(ccd, elm, quad, data_set)
#
#--- fit a line
#
    (intList, slopeList, serrList, intList2, slopeList2, serrList2)\
                                = fitLines(xSets, ySets, ydiv, echk=0)
#
#--- plot five panel plots (eSets added 4/24/14)
#
    outname = web_dir + plot_dir + '/' + elm + '_ccd' + str(ccd) 
    outname = outname +  '_quad' + str(quad) + '_plot.png'

    plotPanel(xSets, ySets, xname, yname, entLabels, ydiv, outname,\
              yErrs = eSets, intList = intList, slopeList = slopeList,\
              intList2= intList2, slopeList2=slopeList2)

#---------------------------------------------------------------------------------------
#-- plot_data2: plot indivisual CCD CTI trends and combined CTI trends for all different cases
#---------------------------------------------------------------------------------------

def plot_data2(indirs, outdirs, allccd = 1):
    """
    plot indivisual CCD CTI trends and combined CTI trends for all different cases 
    Input:  indirs  --- a list of directories which contain data
            outdirs --- a list of directories which the plots will be deposted
            allccd  --- if it is 1, the funciton processes all ccd, if it is 0, detrended ccd only
    Output: plots such as <elm>_ccd<ccd#>_plot.png, imaging_<elm>_plot.png, etc 
            fitting_result  --- a file contains a table of fitted parameters
            combined data sets  such as imging_<elm>_comb, spectral_<elm>_comb etc saved 
            in data_dir/<indir>
    """
    if allccd == 0:                                         #--- detrended data case
         ccd_list = [0, 1, 2, 3, 4, 6, 8, 9]
    else:
         ccd_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]          #---- normal case

    xname    = 'Time (Year)'
    yname    = '(S/I)x10**4'

    for k in range(0, len(indirs)):
        idir  = indirs[k]

        sline = '\n\nData are devided into two sets at year 2012.5 for front-side CCDs '
        sline = sline + 'and year 2014.5 for back-side CCDs to fit two trending '
        sline = sline + 'lines as the data character changes. The top line of each '
        sline = sline + 'CCD lists the fitted results before the the date and the '
        sline = sline + 'bottom line lists after the date.\n\n\n'

        for elm in elm_set:
            uelm = elm
            uelm.lower()

            sline = sline  + '\n\n' + uelm + ' K alpha' + '\n'
#
#--- write a table head
#
            sline = sline + '----------\n'
            sline = sline + 'CCD     '
            sline = sline + 'Quad0' + '\t\t\t\t'
            sline = sline + 'Quad1' + '\t\t\t\t'
            sline = sline + 'Quad2' + '\t\t\t\t'
            sline = sline + 'Quad3' + '\n'
            sline = sline + '\tSlope\t\t Sigma\t' * 4
            sline = sline + '\n\n'
#
#--- read each ccd data set
#
            for ccd in ccd_list:
                sline = sline + str(ccd) + '\t'

                if ccd in [5, 7]:
                    ydiv = bks_div

                elif ccd in [4, 6, 8, 9]:
                    ydiv = spc_div

                else:
                    ydiv = img_div

                ifile = data_dir +  idir + '/' +  elm + '_ccd' + str(ccd)
                data  = mcf.read_data_file(ifile)
#
#--- fit a line and get intercepts and slopes: they are save in a list form
#
                (xSets, ySets, yErrs) = rearrangeData(data)

                (intList, slopeList, serrList, intList2, slopeList2, serrList2)\
                                            = fitLines(xSets, ySets, ydiv)

                entLabels = []
                tline1 = ''
                tline2 = ''
                for i in range(0, 4):
#
#--- create a title label for plot
#
                    cslope = round((slopeList[i] * 1.0e9), 3)
                    line   = 'CCD' + str(ccd) + ': Node' + str(i) 
                    entLabels.append(line)
#
#--- print out the slope and the error for each quad
#
                    tline1 = tline1 + "%3.3e\t" % slopeList[i]
                    tline1 = tline1 + "%3.3e\t" % serrList[i]
                    tline2 = tline2 + "%3.3e\t" % slopeList2[i]
                    tline2 = tline2 + "%3.3e\t" % serrList2[i]

                sline = sline + tline1 + '\n'
                sline = sline + '\t' +  tline2 + '\n'
#
#--- create the plot
#
                outname = web_dir + outdirs[k] + '/' + elm + '_ccd' + str(ccd) + '_plot.png'

                plotPanel(xSets, ySets, xname, yname, entLabels, ydiv, outname,\
                          yErrs = yErrs, intList = intList, slopeList = slopeList,\
                          intList2= intList2, slopeList2=slopeList2)
#
#--- create combined plots (image ccd, spec ccd, backside ccds)
#
            yMinSets   = []
            yMaxSets   = []
            xSets      = []
            ySets      = []
            entLabels  = []
            yErrs      = []
            intList    = []
            slopeList  = []
            intList2   = []
            slopeList2 = []

            sccd_list = [0, 1, 2, 3]
            (newX, newY, newE, intc, slope, serr, intc2, slope2, serr2) \
                                = prepPartPlot(elm, sccd_list, 'imaging', indirs[k], outdirs[k])

            sline = sline + '\n\n'
            sline = sline + 'ACIS-I Average:\n '
            sline = sline + "\t%3.3e\t%3.3e\n" % (slope,  serr)
            sline = sline + "\t%3.3e\t%3.3e\n" % (slope2, serr2)

            xSets.append(newX)
            ySets.append(newY)
            entLabels.append('imaging')
            yErrs.append(newE)
            intList.append(intc)
            slopeList.append(slope)
            intList2.append(intc2)
            slopeList2.append(slope2)

            sccd_list = [4, 6, 7, 9]
            (newX, newY, newE, intc, slope, serr, intc2, slope2, serr2) \
                                = prepPartPlot(elm, sccd_list, 'spectral', indirs[k], outdirs[k])

            sline = sline + '\n\n'
            sline = sline + 'ACIS-S Average w/o BI:\n '
            sline = sline + "\t%3.3e\t%3.3e\n" % (slope,  serr)
            sline = sline + "\t%3.3e\t%3.3e\n" % (slope2, serr2)

            xSets.append(newX)
            ySets.append(newY)
            entLabels.append('spectral')
            yErrs.append(newE)
            intList.append(intc)
            slopeList.append(slope)
            intList2.append(intc2)
            slopeList2.append(slope2)

            if allccd == 1:
                sccd_list = [5]
                (newX, newY, newE, intc, slope, serr, intc2, slope2, serr2) \
                        = prepPartPlot(elm, sccd_list, 'backside_5', indirs[k], outdirs[k])

                sline = sline + '\n\n'
                sline = sline + 'Back Side CCD 5:\n '
                sline = sline + "\t%3.3e\t%3.3e\n" % (slope,  serr)
                sline = sline + "\t%3.3e\t%3.3e\n" % (slope2, serr2)

                xSets.append(newX)
                ySets.append(newY)
                entLabels.append('backside_5')
                yErrs.append(newE)
                intList.append(intc)
                slopeList.append(slope)
                intList2.append(intc2)
                slopeList2.append(slope2)

                sccd_list = [7]
                (newX, newY, newE, intc, slope, serr, intc2, slope2, serr2) \
                            = prepPartPlot(elm, sccd_list, 'backside_7', indirs[k], outdirs[k])

                sline = sline + '\n\n'
                sline = sline + 'Back Side CCD 7:\n '
                sline = sline + "\t%3.3e\t%3.3e\n" % (slope,  serr)
                sline = sline + "\t%3.3e\t%3.3e\n" % (slope2, serr2)

                xSets.append(newX)
                ySets.append(newY)
                entLabels.append('backside_7')
                yErrs.append(newE)
                intList.append(intc)
                slopeList.append(slope)
                intList2.append(intc2)
                slopeList2.append(slope2)
#
#--- create the plot
#
            xname    = 'Time (Year)'
            yname    = '(S/I)x10**4'
            outname  = web_dir + outdirs[k] + '/combined'  + '_' + elm + '_plot.png'

            plotPanel(xSets, ySets, xname, yname, entLabels, ydiv, outname,\
                      yErrs = yErrs, intList = intList, slopeList = slopeList,\
                      intList2 = intList2, slopeList2 = slopeList2)
#
#--- write out the fitting results
#
        ifile = web_dir + outdirs[k] + '/fitting_result'
        with open(ifile, 'w') as fo:
            fo.write(sline)

#---------------------------------------------------------------------------------------
#-- prepPartPlot: create combined data set to prepare for the plot                    --
#---------------------------------------------------------------------------------------

def prepPartPlot(elm, ccd_list, head, indir, outdir):
    """
    create combined data set to prepare for the plot
    Input:  elm         --- element
            ccd_list    --- a list of ccd to be used
            head        --- a header for the plot/data table
            indir       --- a directory where the data is kept
            outdir      --- a directory where the plot will be deposted
    Output: a list of 
            newX        --- combined X values in a list
            newY        --- combined Y values in a list
            newE        --- combined Error of Y 
            intList[0]  --- intercept
            slopeList[0]--- slope
            serrList[0] --- erorr of the slope
            data    such as imaging_<elm>_comb this is kept in <indir>
    """
    comb_data = []
    for ccd in ccd_list:
        ifile = data_dir +  indir +'/' +  elm + '_ccd' + str(ccd)
        data  = mcf.read_data_file(ifile)

        comb_data = comb_data + data

        if ccd in [5, 7]:
            ydiv = bks_div

        elif ccd in [4, 6, 8, 9]:
            ydiv = spc_div

        else:
            ydiv = img_div

#
#--- separate the data into each node
#
    (xSets, ySets, yErrs) = rearrangeData(comb_data)

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

    newX = []
    newY = []
    newE = []
    yVar = []
    eVar = []
    start = 0
    stop  = 30
    sline = ''
    for i in range(0, len(xsorted)):
        x = xsorted[i]
        if (x >= start) and (x < stop):
            for j in range(0, 4):
                yVar.append(qsorted[j][i])
                eVar.append(esorted[j][i])
        else:
            tcnt = 0
            sum0 = 0
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
                    sum0 += var
                    sum1 += yVar[k]
                    sum2 += yVar[k] * yVar[k] 
                    esum += err2
                    tcnt  += 1

            if tcnt > 0:
                meanv = sum0 / esum
                sigma = math.sqrt(1.0 / sum2)
                mid   = int(0.5 * (start + stop))
                newX.append(mid)
                newY.append(meanv)
                newE.append(sigma)

                sline = sline +  str(mid) + '\t' + str(meanv) + '\t' + str(sigma) + '\n'

            start = stop
            stop  = start + 30
            yVar = []
            eVar = []
            for j in range(0, 4):
                yVar.append(qsorted[j][i])
                eVar.append(esorted[j][i])
#
#--- print out combined data
#
    ofile = data_dir + indir + '/' + head + '_' + elm + '_comb'
    with open(ofile, 'w') as fo:
        fo.write(sline)
#
#--- since fitLines takes only a list of lists, put in a list
#
    XSets = [newX]
    YSets = [newY]
#
#--- find a fitting line parameters
#
    (intList, slopeList, serrList, intList2, slopeList2, serrList2)\
                                            = fitLines(xSets, ySets, ydiv)
#
#--- create a title label for plot
#
    return (newX, newY, newE, intList[0], slopeList[0],\
            serrList[0], intList2[0],  slopeList2[0], serrList2[0])

#---------------------------------------------------------------------------------------
#-- plot_data3: plotting multi-panel plots of imaging, spectral, and backside ccd CTI trends
#---------------------------------------------------------------------------------------

def plot_data3():
    """
    plotting multi-panel plots of imaging, spectral, and backside ccd CTI trends
    Input: none, but read from <data_dir>
    Output: imgiing_<elm>_plot.png, spectral_<elm>_plot.png, backside_5_plot.png 
            backside_7_plot.png
            note that for detrended data, backside ccds trends won't be created
    """
    head_list = ['imaging', 'spectral', 'backside_5', 'backside_7']
    outdir    = 'Data_Plot/'
    plot_data3_sub(head_list, dir_set, outdir)

    head_list = ['imaging', 'spectral']
    outdir    = 'Det_Plot/'
    plot_data3_sub(head_list, det_set, outdir)

#---------------------------------------------------------------------------------------
#-- plot_data3_sub: create a 5 panel plot of CTI trends                                -
#---------------------------------------------------------------------------------------

def plot_data3_sub(head_list, dir_list, outdir):
    """
    create a 5 panel plot of CTI trends 
    Input:  head_list   --- the file name head list
            dir_list    --- a list of directries which contain data
            outdir      --- a directory name where the plot will be deposited
    Output: <web_dir>/<outdir>/<head>_<elm>_plot.png
    """
    xname    = 'Time (Year) '
    yname    = '(S/I) * 10 ** 4'
    name_list = ['No Correction', 'Temp < -119.7', 'Temp < -119.7 & Time > 7000',\
                 'Adjusted', 'MIT/ACIS Adjusted']

    for head in head_list:

        mc = re.search(head, 'backside')
        md = re.search(head, 'spec')

        if mc is not None:
            ydiv = bks_div
        elif md is not None:
            ydiv = spc_div
        else:
            ydiv = img_div

        for elm in elm_set:

            yMinSets = []
            yMaxSets = []
            xSets    = []
            ySets    = []
            yErrs    = []
            xmin     = 1999
            xmax     = 0

            for idir in dir_list:
                ifile = data_dir + idir + '/'  + head + '_' + elm + '_comb'
                data  = mcf.read_data_file(ifile)

                xdata = []
                ydata = []
                yerr  = []
                for ent in data:
                    atemp = re.split('\t+|\s+', ent)
                    xdata.append(float(atemp[0]))
                    ydata.append(float(atemp[1]))
                    yerr.append(float(atemp[2]))

                ymin  = min(ydata)
                ymax  = max(ydata)
                ypositive = []
                for ent in ydata:
                    if ent > 0:
                        ypositive.append(ent)
                yavg = mean(ypositive)
                ymin = yavg - 1.0
                ymax - yavg + 2.0
                if ymin < 0:
                    ymin = 0.0
                    ymax = 4.0

                yMinSets.append(ymin)
                yMaxSets.append(ymax)
                xSets.append(xdata)
                ySets.append(ydata)
                yErrs.append(yerr)
#
#--- find fitting line parameters
#
            (intList, slopeList, serrList, intList2, slopeList2, serrList2) \
                                        = fitLines(xSets, ySets, ydiv)
#
#--- create the plot
#
            xmax = int(float(time.strftime('%Y', time.gmtime())))

            outname = web_dir + outdir + '/' +  head + '_' + elm + '_plot.png'
            plotPanel(xSets, ySets, xname, yname, name_list, ydiv, outname, \
                      yErrs = yErrs, intList = intList, slopeList = slopeList,\
                      intList2 = intList2, slopeList2 = slopeList2)

#---------------------------------------------------------------------------------------
#-- isolateData: separate a table data into arrays of data                           ---
#---------------------------------------------------------------------------------------

def isolateData(ccd, elm, quad, dir_set):
    """
    separate a table data into arrays of data
    Input:  ccd     --- ccd #
            elm     --- name of element
            quad    --- quad #
            dir_set --- a list of data directories 
    Output: xSets   --- a list of lists of x values
            ySets   --- a list of lists of y values
            eSets   --- a list of lists of y errors
    """
    xSets    = []
    ySets    = []
    eSets    = []

    for idir in dir_set:
        ifile = data_dir + idir + '/' + elm + '_ccd' + str(ccd)
        data  = mcf.read_data_file(ifile)
        if len(data)  < 1:
            xSets.append([])
            ySets.append([])
            eSets.append([])
            continue
#
#--- separeate a table into each column array
#
        coldata = mcf.separate_data_to_arrays(data)
#
#--- convert time into fractional year (a list of time)
#
        stime   = convert_time_list(coldata[0])

        xSets.append(stime)
#
#--- the data part come with cti +- error. drop the error part
#
        [ydata, yerr]  = separateErrPart(coldata[quad + 1])
        ySets.append(ydata)
        eSets.append(yerr)

    return [xSets, ySets, eSets]

#---------------------------------------------------------------------------------------
#-- rearrangeData: separate a table data into time and 4 quad data array data sets    --
#---------------------------------------------------------------------------------------

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

    coldata  = mcf.separate_data_to_arrays(data)

    stime    = convert_time_list(coldata[0])           #---- time in ydate 
#
#--- go around each quad data
#
    for i in range(1, 5):
        xSets.append(stime)
        data  = []
        error = []
        for ent in coldata[i]:
            atemp = re.split('\+\-', ent)
            data.append(float(atemp[0]))
            error.append(float(atemp[1]))

        ySets.append(data)
        yErrs.append(error)

    return (xSets, ySets, yErrs)

#---------------------------------------------------------------------------------------
#-- fitLines: find intercepts and slopes  of sets of x and y values                   --
#---------------------------------------------------------------------------------------

def fitLines(xSets, ySets, ydiv,  echk = 1):
    """
    find intercepts and slopes  of sets of x and y values
    Input:  xSets   --- a list of independent variable lists
            ySets   --- a list of dependent variable lists
            ydiv    --- fitting dividing point (in year)
            echk    --- if it is larger than 0, compute slope error (default: 1)
    Output: inList  --- a list of intercepts
            slopeList--- a list of slopes
            serrlist--- a list of slope errors
    """
    intList    = []
    slopeList  = []
    serrList   = []
    intList2   = []
    slopeList2 = []
    serrList2  = []

    for i in range(0, len(xSets)):
        xset1 = []
        yset1 = []
        xset2 = []
        yset2 = []
        for k in range(0, len(xSets[i])):
            if xSets[i][k] <= ydiv:              
                xset1.append(xSets[i][k])
                yset1.append(ySets[i][k])
            else:
                xset2.append(xSets[i][k])
                yset2.append(ySets[i][k])

        [intc, slope, ierr, serr]     = linear_fit(xset1, yset1)
        [intc2, slope2, ierr2, serr2] = linear_fit(xset2, yset2)

        intList.append(intc)
        slopeList.append(slope)
        serrList.append(serr)

        intList2.append(intc2)
        slopeList2.append(slope2)
        serrList2.append(serr2)

    return (intList, slopeList, serrList, intList2, slopeList2, serrList2)

#---------------------------------------------------------------------------------------
#-- linear_fit: linear fitting function with 99999 error removal                     ---
#---------------------------------------------------------------------------------------

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
    sum1 = 0.0 
    sum2 = 0.0
    tot  = 0.0
    for i in range(0, len(y)):
        if y[i] > 0:
            sum1 += y[i]
            sum2 += y[i] *y[i]
            tot  += 1.0
    if tot > 0:
        avg = sum1 / tot
        sig = math.sqrt(sum2/tot - avg * avg)
    else: 
        avg = 4.0

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

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def model(p, x):
    a, b = p
    y = a + b * x
    return y

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

def residuals(p, data):

    x, y = data

    return  y - model(p, x)

#---------------------------------------------------------------------------------------
#-- convert_time_list: convert time format to fractional year for the entire array   ---
#---------------------------------------------------------------------------------------

def convert_time_list(time_list):
    """
    convert time format to fractional year for the entire array
    Input:  time_list   --- a list of time (format: <yyyy>-<mm>-<dd>Thh:mm:ss)
    Output: converted   --- a list of time in  fractional year
    """
    converted = []
    for ent in time_list:
        out   = time.strftime('%Y:%j:%H:%M:%S', time.strptime(ent, "%Y-%m-%dT%H:%M:%S"))
        atemp = re.split(':', out)
        year  = float(atemp[0])
        yday  = float(atemp[1])
        hh    = float(atemp[2])
        mm    = float(atemp[3])
        ss    = float(atemp[4])
     
        if mcf.is_leapyear(year):
            base = 366.0
        else:
            base = 365.0
     
        fyear = year + (yday + hh / 24.0 + mm / 1440.0 + ss / 86400.0) / base
        converted.append(fyear)
     
    return converted

#---------------------------------------------------------------------------------------
#-- separateErrPart: separate  the error part of each entry of the data array        ---
#---------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                               ---
#---------------------------------------------------------------------------------------

def plotPanel(xSets, ySets, xname, yname, entLabels, ydiv, outname,\
              yErrs = [], intList = [], slopeList = [], intList2 = [], slopeList2 = []):
    """
    This function plots multiple data in separate panels
    Input:  xSets       --- a list of lists containing x-axis data
            ySets       --- a list of lists containing y-axis data
            xname       --- x label
            yname       --- y label
            entLabels: a list of the names of each data
            ydiv        --- where to devide the data
            outname     ---- output file name

    Output: a png plot: outname
    """
#
#--- set plotting range
    xmin = 1999
    xmax = int(float(time.strftime('%Y', time.gmtime()))) + 1
    chk  = int(float(time.strftime('%j', time.gmtime())))
#
#--- if the date is passed a half year, add one more year
#
    if chk > 183:
        xmax +=1

    ymin = 0.0
    ymax = 0.0
    for cdat in ySets:
        try:
            comp = max(cdat)
        except:
            continue
        if comp > ymax:
            ymax = comp

    if ymax > y_std_max:        #--- y_std_max is defined at the top
        ymax = int(ymax) + 2
    elif ymax > 0.9 * y_std_max:
        ymax = y_std_max + 1
    else:
        ymax = y_std_max
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

        exec("ax%s = plt.subplot(%s)"       % (str(i), line))
        exec("ax%s.set_autoscale_on(False)" % (str(i)))
        exec("ax%s.set_xbound(xmin,xmax)"   % (str(i)))
        exec("ax%s.set_xlim(left=xmin, right=xmax, auto=False)" % (str(i)))
        exec("ax%s.set_ylim(bottom=ymin, top=ymax, auto=False)" % (str(i)))

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
            pstop   = intc + slope * ydiv 

            intc2   = intList2[i] 
            slope2  = slopeList2[i]
            pstart2 = intc2 + slope2 * ydiv
            pstop2  = intc2 + slope2 * xmax 
            pchk    = 1
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=3.0, lw =0)
        if echk > 0:
            plt.errorbar(xdata, ydata, yerr=yerr,color=colorList[i],  markersize=3.0, fmt='.')
        if pchk > 0:
            plt.plot([xmin,ydiv], [pstart, pstop],   colorList[i], lw=1)
            plt.plot([ydiv,xmax], [pstart2, pstop2], colorList[i], lw=1)
#
#--- add legend
#
        ltext = entLabels[i] + ' \nSlope (CTI/Year):   ' 
        ltext = ltext + '%3.3e' % slopeList[i]
        ltext = ltext + '\nAfter Year ' + str(ydiv) + ': '   +'%3.3e' % slopeList2[i] 
        leg = legend([p],  [ltext], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        #exec("ax%s.set_ylabel(yname, size=8)" % (str(i)))
        ylabel(yname)
#
#--- add x ticks label only on the last panel
#
        if i != tot-1: 
            line =  eval("ax%s.get_xticklabels()" % (str(i)))
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
    plt.savefig(outname, format='png', dpi=300)

#--------------------------------------------------------------------

if __name__ == '__main__':

    plot_data1()
    plot_data2(dir_set, out_set)
    plot_data2(det_set, dout_set, allccd = 0)

