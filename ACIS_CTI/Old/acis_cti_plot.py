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
#
#--- set several lists
#
#dir_set  = ['Data2000', 'Data119', 'Data_adjust', 'Data_cat_adjust']
#det_set  = ['Det_Data2000', 'Det_Data119', 'Det_Data_adjust', 'Det_Data_cat_adjust']
#out_set  = ['Plot2000', 'Plot119', 'Plot_adjust', 'Plot_cat_adjust']
#dout_set = ['Det_Plot2000', 'Det_Plot119', 'Det_Plot_adjust', 'Det_Plot_cat_adjust']

dir_set  = ['Data2000', 'Data119', 'Data7000', 'Data_adjust', 'Data_cat_adjust']
det_set  = ['Det_Data2000', 'Det_Data119', 'Det_Data7000', 'Det_Data_adjust', 'Det_Data_cat_adjust']
out_set  = ['Plot2000', 'Plot119', 'Plot7000', 'Plot_adjust', 'Plot_cat_adjust']
dout_set = ['Det_Plot2000', 'Det_Plot119', 'Det_Plot7000', 'Det_Plot_adjust', 'Det_Plot_cat_adjust']


elm_set  = ['al', 'mn', 'ti']

#
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
#-- plot_data1: plotting indivisual (CCD/quad) data for 5 different data criteria                 --
#---------------------------------------------------------------------------------------------------

def plot_data1():

    """
    plotting indivisual (CCD/quad) data for 5 different data criteria.
    Input: None, but read from eadh data set: see nam_list
    Output: indivisual data plot in png format. 
    """

    nam_list = ['No Correction', 'Temp < -119.7', 'Temp < -119.7 & Time > 7000', 'Adjusted', 'MIT/ACIS Adjusted']
    xname    = 'Time (Year)'
    yname    = '(S/I)x10**4'

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

#---------------------------------------------------------------------------------------------------
#-- plot_data1_sub: sub fuction of "plot_data1" to plot indivisula data                          ---
#---------------------------------------------------------------------------------------------------

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
    if (ccd == 5) or (ccd == 7):
        ydiv = bks_div
    elif (ccd == 4) or (ccd == 6) or (ccd == 8) or (ccd == 9):
        ydiv = spc_div
    else:
        ydiv = img_div
#
#--- separate a data table into 5 arrays
#
    (xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets) = isolateData(ccd, elm, quad, data_set)
#
#--- fit a line
#
    (intList, slopeList, serrList) = fitLines(xSets, ySets, ydiv, echk=0)
#
#--- plot five panel plots (eSets added 4/24/14)
#
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, ydiv,  yErrs = eSets, intList = intList, slopeList = slopeList)


    outname = web_dir + plot_dir + '/' + elm + '_ccd' + str(ccd) +  '_quad' + str(quad) + '_plot.png'
    cmd     = 'mv out.png ' + outname
    os.system(cmd)


#---------------------------------------------------------------------------------------------------
#-- plot_data2: plot indivisual CCD CTI trends and combined CTI trends for all different cases    --
#---------------------------------------------------------------------------------------------------

def plot_data2(indirs, outdirs, allccd = 1):

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
        file = web_dir + outdirs[k] + '/fitting_result'
        fo   = open(file, 'w')

        for elm in elm_set:
            uelm = elm
            uelm.lower()
            line = '\n\n' + uelm + ' K alpha (S/I * 10^4)' + '\n'
            fo.write(line)
#
#--- write a table head
#
            fo.write('-----------------------\n')
            fo.write('CCD     Quad0                           Quad1                           Quad2                           Quad3\n')
            fo.write('        Slope           Sigma           Slope           Sigma           Slope           Sigma           Slope           Sigma\n\n')
#            fo.write('CCD     Quad0                                                           Quad1')
#            fo.write('Quad2                                                           Quad3\n')
#            fo.write('        Slope           Sigma           Slope           Sigma           Slope           Sigma           Slope           Sigma')
#            fo.write('        Slope           Sigma           Slope           Sigma           Slope           Sigma           Slope           Sigma\n\n')

#
#--- read each ccd data set
#
            for ccd in ccd_list:
                if (ccd == 5) or (ccd == 7):
                    ydiv = bks_div
                elif (ccd == 4) or (ccd == 6) or (ccd == 8) or (ccd == 9):
                    ydiv = spc_div
                else:
                    ydiv = img_div

                file = data_dir +  dir + '/' +  elm + '_ccd' + str(ccd)
                f    = open(file, 'r')
                data = [line.strip() for line in f.readlines()]
                f.close()
#
#--- fit a line and get intercepts and slopes: they are save in a list form
#
                (xmin, xmax, yMinSets, yMaxSets, xSets, ySets, yErrs) = rearrangeData(data)
                (intList, slopeList, serrList) = fitLines(xSets, ySets, ydiv, echk=50)

                line = str(ccd) + '\t'
                fo.write(line)

                entLabels = []
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
                    line = "%3e\t%3e\t" % (slopeList[i], serrList[i])
                    fo.write(line)

                fo.write('\n')
#
#--- create the plot
#
                plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, ydiv, yErrs = yErrs, intList = intList, slopeList = slopeList)
                outname = web_dir + outdirs[k] + '/' + elm + '_ccd' + str(ccd) + '_plot.png'
                cmd     = 'mv out.png ' + outname
                os.system(cmd)
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

            sccd_list = [0, 1, 2, 3]
            (xmin, xmax, ymin, ymax, newX, newY, newE, intc, slope, serr) = prepPartPlot(elm, sccd_list, 'imaging', indirs[k], outdirs[k])
            fo.write('ACIS-I Average: ')
            line = "%3e\t%3e\n" % (slope, serr)
            fo.write(line)

            yMinSets.append(ymin)
            yMaxSets.append(ymax)
            xSets.append(newX)
            ySets.append(newY)
            entLabels.append('imaging')
            yErrs.append(newE)
            intList.append(intc)
            slopeList.append(slope)

            sccd_list = [4, 6, 7, 9]
            (xmin, xmax, ymin, ymax, newX, newY, newE, intc, slope, serr) = prepPartPlot(elm, sccd_list, 'spectral', indirs[k], outdirs[k])
            fo.write('ACIS-S Average w/o BI: ')
            line = "%3e\t%3e\n" % (slope, serr)
            fo.write(line)

            yMinSets.append(ymin)
            yMaxSets.append(ymax)
            xSets.append(newX)
            ySets.append(newY)
            entLabels.append('spectral')
            yErrs.append(newE)
            intList.append(intc)
            slopeList.append(slope)

            if allccd == 1:
                sccd_list = [5]
                (xmin, xmax, ymin, ymax, newX, newY, newE, intc, slope, serr) = prepPartPlot(elm, sccd_list, 'backside_5', indirs[k], outdirs[k])
                fo.write('Back Side CCD 5: ')
                line = "%3e\t%3e\n" % (slope, serr)
                fo.write(line)

                yMinSets.append(ymin)
                yMaxSets.append(ymax)
                xSets.append(newX)
                ySets.append(newY)
                entLabels.append('backside_5')
                yErrs.append(newE)
                intList.append(intc)
                slopeList.append(slope)

                sccd_list = [7]
                (xmin, xmax, ymin, ymax, newX, newY, newE, intc, slope, serr) = prepPartPlot(elm, sccd_list, 'backside_7', indirs[k], outdirs[k])
                fo.write('Back Side CCD 7: ')
                line = "%3e\t%3e\n" % (slope, serr)
                fo.write(line)

                yMinSets.append(ymin)
                yMaxSets.append(ymax)
                xSets.append(newX)
                ySets.append(newY)
                entLabels.append('backside_7')
                yErrs.append(newE)
                intList.append(intc)
                slopeList.append(slope)
#
#--- create the plot
#

            xname    = 'Time (Year)'
            yname    = '(S/I)x10**4'
            plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, ydiv, yErrs = yErrs, intList = intList, slopeList = slopeList)
            outname = web_dir + outdirs[k] + '/combined'  + '_' + elm + '_plot.png'
            cmd     = 'mv out.png ' + outname
            os.system(cmd)


        fo.close()


#---------------------------------------------------------------------------------------------------
#-- prepPartPlot: create combined data set to prepare for the plot                                --
#---------------------------------------------------------------------------------------------------

def prepPartPlot(elm, ccd_list, head, indir, outdir):

    """
    create combined data set to prepare for the plot
    Input:  elm     --- element
            ccd_list--- a list of ccd to be used
            head    --- a header for the plot/data table
            indir   --- a directory where the data is kept
            outdir  --- a directory where the plot will be deposted
    Output: a list of 
            xmin        --- min of x axis
            xmax        --- max of x axis
            ymin        --- min of y axis
            ymax        --- max of y axis
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

        if (ccd == 5) or (ccd == 7):
            ydiv = bks_div
        elif (ccd == 4) or (ccd == 6) or (ccd == 8) or (ccd == 9):
            ydiv = spc_div
        else:
            ydiv = img_div

#
#--- separate the data into each node
#
    (xmin, xmax, yMinSets, yMaxSets, xSets, ySets, yErrs) = rearrangeData(comb_data)

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
    (intList, slopeList, serrList) = fitLines(xSets, ySets, ydiv, echk = 50)
#
#--- set Y plot range
#
    ypositive = []
    for ent in newY:
        if ent > 0:
            ypositive.append(ent)

    yavg =  intList[0] + slopeList[0] * 2005    
    ymin = yavg - 1.0
    ymax = yavg + 2.0
    if ymin < 0:
        ymin = 0.0
        ymax = 3.0
#
#--- create a title label for plot
#
    return (xmin, xmax, ymin, ymax, newX, newY, newE, intList[0], slopeList[0], serrList[0])

#---------------------------------------------------------------------------------------------------
#-- plot_data3: plotting multi-panel plots of imaging, spectral, and backside ccd CTI trends     ---
#---------------------------------------------------------------------------------------------------

def plot_data3():

    """
    plotting multi-panel plots of imaging, spectral, and backside ccd CTI trends
    Input: none, but read from <data_dir>
    Output: imgiing_<elm>_plot.png, spectral_<elm>_plot.png, backside_5_plot.png backside_7_plot.png
            note that for detrended data, backside ccds trends won't be created
    """

    head_list = ['imaging', 'spectral', 'backside_5', 'backside_7']
    outdir    = 'Data_Plot/'
    plot_data3_sub(head_list, dir_set, outdir)

    head_list = ['imaging', 'spectral']
    outdir    = 'Det_Plot/'
    plot_data3_sub(head_list, det_set, outdir)

#---------------------------------------------------------------------------------------------------
#-- plot_data3_sub: create a 5 panel plot of CTI trends                                          ---
#---------------------------------------------------------------------------------------------------

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
    name_list = ['No Correction', 'Temp < -119.7', 'Temp < -119.7 & Time > 7000', 'Adjusted', 'MIT/ACIS Adjusted']

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

            for dir in dir_list:
                file = data_dir + dir + '/'  + head + '_' + elm + '_comb'
                f    = open(file, 'r')
                data = [line.strip() for line in f.readlines()];
                f.close()

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
                    ymax = 3.0

                yMinSets.append(ymin)
                yMaxSets.append(ymax)
                xSets.append(xdata)
                ySets.append(ydata)
                yErrs.append(yerr)
#
#--- find fitting line parameters
#
            (intList, slopeList, serrList) = fitLines(xSets, ySets, ydiv)
#
#--- create the plot
#
            xmax = txmax

            plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, name_list, ydiv, yErrs = yErrs, intList = intList, slopeList = slopeList)
            outname = web_dir + outdir + '/' +  head + '_' + elm + '_plot.png'
            cmd     = 'mv out.png ' + outname
            os.system(cmd)

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
    Output: xmin    --- min of independent var
            xmax    --- max of independent var
            yMinSets--- a list of min of y values
            yMaxSets--- a list of max of y values
            xSets   --- a list of lists of x values
            ySets   --- a list of lists of y values
    """

    xSets    = []
    ySets    = []
    eSets    = []
    yMinSets = []
    yMaxSets = []
    xmin     = 1999
    xmax     = txmax

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
#--- convert time into fractional year (a list of time)
#
        time    = convTimeFullColumn(coldata[0])

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
#        ymin  = round(min(ydata), 1) - 0.1
#        ymax  = round(max(ydata), 1) + 0.1
#
        ypositive = []
        for ent in ydata:
            if ent > 0:
                ypositive.append(ent)
        ymean = round(mean(ypositive),1)
        ymin  = ymean - 1.0
        ymax  = ymean + 2.0
        if ymin < 0.0:
            ymin = 0.0
            ymax = 3.0

        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    return [xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets]


#---------------------------------------------------------------------------------------------------
#-- rearrangeData: separate a table data into time and 4 quad data array data sets                --
#---------------------------------------------------------------------------------------------------

def rearrangeData(data):

    """
    separate a table data into time and 4 quad data array data sets
    Input:  data    --- input table data
    Output: xmin    --- min of x
            xmax    --- max of x
            yMinSets--- a list of min y of each quad
            yMaxSets--- a list of max y of each quad
            xSets   --- a list of lists of x values
            ySets   --- a list of lists of y values
            yErrs   --- a list of lists of y errors
    """

    xSets    = []
    ySets    = []
    yErrs    = []
    yMinSets = []
    yMaxSets = []
    xmin     = 1999
    xmax     = txmax

    coldata  = mcf.separate_data_to_arrys(data)

    time     = convTimeFullColumn(coldata[0])           #---- time in dom
#
#--- go around each quad data
#
    for i in range(1, 5):
        xSets.append(time)
        data  = []
        error = []
        for ent in coldata[i]:
            atemp = re.split('\+\-', ent)
            data.append(float(atemp[0]))
            error.append(float(atemp[1]))

        ySets.append(data)
        yErrs.append(error)

#        ymin = round(min(data), 1) - 0.1
#        ymax = round(max(data), 1) + 0.1
        ypositive = []
        for ent in data:
            if ent > 0:
                ypositive.append(ent)
        yavg = round(mean(ypositive), 1)
        ymin = yavg - 1.0
        ymax = yavg + 2.0
        if ymin < 0:
            ymin = 0.0
            ymax = 3.0
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    return (xmin, xmax, yMinSets, yMaxSets, xSets, ySets, yErrs)

#---------------------------------------------------------------------------------------------------
#-- fitLines: find intercepts and slopes  of sets of x and y values                               --
#---------------------------------------------------------------------------------------------------

def fitLines(xSets, ySets, ydiv,  echk = 0):

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
        [intc, slope, ierr, serr]     = linear_fit(xSets[i], ySets[i], echk)

        intList.append(intc)
        slopeList.append(slope)
        serrList.append(serr)

    return (intList, slopeList, serrList)


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

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    plot_data1()
    plot_data2(dir_set, out_set)
    plot_data2(det_set, dout_set, allccd = 0)
#    plot_data3()                           #---- this is a combined plot; we do not use this any more (5/21/2014)

#    update_cti_page()

