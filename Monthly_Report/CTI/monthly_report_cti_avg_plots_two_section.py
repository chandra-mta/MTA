#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#   monthly_report_cti_avg_plots.py: create data and plots of cti trends for monthly report     #
#                                                                                               #
#           this version does not use "al k alpha" values                                       #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           Last Update: Aug 04, 2020                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import time
import numpy
import argparse
import math

import matplotlib as mpl
if __name__ == '__main__':
    mpl.use('Agg')
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines


path = '/data/mta/Script/ACIS/CTI/house_keeping/dir_list_py'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

#
#--- append a path to a private folder to python directory
#
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions as mcf
import robust_linear        as robust
#
#--- temp writing file name
#
import random
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

yupper = 4.0

#---------------------------------------------------------------------------------------------------
#-- monthly_report_cti_avg_plots: a control function to create plots and data for monthly report ---
#---------------------------------------------------------------------------------------------------

def monthly_report_cti_avg_plots(year, mon):

    """
    a control function to create plots and data for monthly report cti trends
    Input: none, but read from cti full data table (/data/mta/Script/ACIS/CTI/Data/...)
    Output: plots in ./Plots
            data  in ./Data
    """
#
#--- set which CCDs belong to which set
#
    image_ccds = (0, 1, 2, 3)
    spec_ccds  = (4, 6, 8, 9)
    back_ccds  = (5, 7)
#
#--- set a few plotting related values
#
    xname = 'Time (Year)'
    yname = 'Mean CTI (S/I * 10**4)'
#
#--- extract data for imaging
#
    [xSets, ySets, eSets] = get_data(image_ccds, 'image', year, mon)

    xmin = int(min(xSets[0])) -1
    xmax = int(max(xSets[0])) +1

    ymin  = 1.0
    ymax  = 4.0
    yMinSets = []
    yMaxSets = []
    for ent in ySets:

        yMinSets.append(ymin)
        yMaxSets.append(ymax)
#
#--- plot the trend
#
    entLabels = ['CCD0', 'CCD1', 'CCD2', 'CCD3']
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets, xname, yname, entLabels, 2012.5)
    cmd = 'mv out.png ./Plots/cti_avg_acis_i.png'
    os.system(cmd)
#
#--- spectral
#

    ymin  = 1.0
    ymax  = 4.0
    yMinSets = []
    yMaxSets = []
    for ent in ySets:

        yMinSets.append(ymin)
        yMaxSets.append(ymax)
    [xSets, ySets, eSets] = get_data(spec_ccds, 'spec', year, mon)
    entLabels = ['CCD4', 'CCD6', 'CCD8', 'CCD9']
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets, xname, yname, entLabels, 2012.5)
    cmd = 'mv out.png ./Plots/cti_avg_acis_s.png'
    os.system(cmd)
#
#--- back side
#

    ymin  = 0.0
    ymax  = 2.0
    yMinSets = []
    yMaxSets = []
    for ent in ySets:

        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    [xSets, ySets, eSets] = get_data(back_ccds, 'back', year, mon)
    entLabels = ['CCD5', 'CCD7']
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets, xname, yname, entLabels, 2014.5)
    cmd = 'mv out.png ./Plots/cti_avg_acis_bi.png'
    os.system(cmd)
#
#--- copy the plots to CTI magin page
#
    cmd = 'rm -rf /data/mta_www/mta_cti/Main_Plot/*png'
    os.system(cmd)
    cmd = 'cp ./Plots/*.png /data/mta_www/mta_cti/Main_Plot/.'
    os.system(cmd)

    
#---------------------------------------------------------------------------------------------------
#-- get_data: read out data from the full cti data table and creates monthly report data table  ----
#---------------------------------------------------------------------------------------------------

def get_data(ccd_list, out, year, mon):

    """
    read out data from the full cti data table and creates monthly report data table
    Input: ccd_list     --- a list of ccds which you want to read the data
           out          --- a type of the data, "image", "spec", or "back"
           year         --- year of data fetch
           mon          --- month of data fetch
           data are read from "/data/mta/Script/ACIS/CTI/DATA/..."
    Output: xSets       --- a list of lists of x values of each ccd
            ySets       --- a list of lists of y values of each ccd
            eSets       --- a list of lists of y error of each ccd
            ./Data/ccd<ccd>_data: monthly averaged cti for monthly report
    """
#
#--- read intercept adjusting table
#
    al_factors = read_correction_factor('al')
    mn_factors = read_correction_factor('mn')
    ti_factors = read_correction_factor('ti')

#
#--- set dimension of the array
#
    c_cnt = 12 * (year - 2000) + mon
    d_cnt = len(ccd_list)
#
#--- for none backside CCDs, we use detrended data sets
#
    if out == 'back':
        idir = '/data/mta/Script/ACIS/CTI/Data/Data_adjust/'
#
#--- vadd to adjust the mean position of CTI
#
    else:
        idir = '/data/mta/Script/ACIS/CTI/Data/Det_Data_adjust/'

    xSets = []
    ySets = []
    eSets = []
#
#-- go around each ccds
#
    for i in range(0, d_cnt):
        ccd = ccd_list[i]
#
#--- set cti data array and error array
#
        avals = [0 for x in range(0, c_cnt)]
        sum1  = [0 for x in range(0, c_cnt)]
        sum2  = [0 for x in range(0, c_cnt)]
#
#--- go around all lines
#
        for elm in ('mn'):
            vadd = 0
            corrections = mn_factors
            for k in range(0, 4):
                vadd += corrections[k][ccd]
            vadd /= 4.0

            ifile = idir + 'mn_ccd' + str(ccd)
            data  = mcf.read_data_file(ifile)

            for ent in data:
                atemp = re.split('\s+', ent)
                btemp = re.split('-', atemp[0])
#
#--- find the row that you want to add this data 
#
                pos   = 12 * (int(btemp[0]) - 2000) + int(btemp[1]) - 1

                for k in range(1, 5):
                    ctemp = re.split('\+\-', atemp[k])
                    val  = float(ctemp[0])
                    if val > 0 and val < yupper:
#
#--- correct the value so that all data points have about the same base line
#
                        val -= (corrections[k-1][ccd])
                        val += vadd
                        err  = float(ctemp[1])
                        if err > 0:
                            avals[pos] += val 
                            sum1[pos]  += 1.0
                            sum2[pos]  += val * val
#
#--- open file for print out
#
        line = '#\n#date       cti     errer\n#\n'
        
        chk  = 0
        xvals = []
        yvals = []
        evals = []
        for k in range(2000, year+1):
            for m in range(0, 13):
                if (k == year) and (m > mon):
                    chk = 1
                    break

                pos = 12 * (k - 2000) + m -1
#
#--- set time in fractional year. adding 0.04 to set time to the mid month
#
                date = k + float(m) / 12.0 + 0.04     
                date = round(date, 3)
#
#--- compute average and erorr
#
                if avals[pos] > 0:
                    avg = avals[pos] / sum1[pos]
                    err = math.sqrt(sum2[pos] /sum1[pos] - avg * avg)
                    avg =  round(avg, 3)
                    err =  round(err, 3)

                    if len(str(date)) == 7:
                        line = line +  str(date) + ' \t' + str(avg) + '\t' + str(err) + '\n'
                    else:
                        line = line + str(date) + '\t'  + str(avg) + '\t' + str(err) + '\n'


                    xvals.append(date)
                    yvals.append(avg)
                    evals.append(err)

            if chk  > 0:
                break

        ifile = './Data/cti_data/ccd' + str(ccd) + '_data'
        with  open(ifile, 'w') as fo:
            fo.write(line)
#
#--- create a lists of lists
#
        xSets.append(xvals)
        ySets.append(yvals)
        eSets.append(evals)

    return [xSets, ySets, eSets]


#---------------------------------------------------------------------------------------------------
#-- read_correction_factor: read mean CTI values from table                                      ---
#---------------------------------------------------------------------------------------------------

def read_correction_factor(elm):

    """
    read mean CTI values from table
    Input:  elm --- element al, mn, or ti
    Output: save --- 4 x 10 data table contatining mean CTI values of <node> x <ccd>
    """
    save = numpy.zeros((4,10))

    ifile = './house_keeping/' + elm + '_intc'
    data  = mcf.read_data_file(ifile)

    for i in range(0, len(data)):
        temp = re.split('\s+', data[i])
        for j in range(0, 4):
            val  = float(temp[j+1])
            save[j][i] = val

    return save


#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, eSets, xname, yname, entLabels, ydiv):

    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets: a list of lists containing x-axis data
            ySets: a list of lists containing y-axis data
            eSets: a list of lists containing error values of y-axis
            yMinSets: a list of ymin 
            yMaxSets: a list of ymax
            entLabels: a list of the names of each data
            ydiv:   a location of dividing spot

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
    mpl.rcParams['font.size'] = 13
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.06)

    tot = len(entLabels)
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

        exec("%s = plt.subplot(%s)"       % (axNam, line))
        exec("%s.set_autoscale_on(False)" % (axNam))      #---- these three may not be needed for the new pylab, but 
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))      #---- they are necessary for the older version to set

        exec("%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam))
        exec("%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam))
#
#--- since the cti seems evolving after year <ydiv>, fit two different lines before and after that point
#
        xdata  = xSets[i]
        ydata  = ySets[i]
        edata  = eSets[i]
  
        xdata1 = []
        ydata1 = []
        edata1 = []
        xdata2 = []
        ydata2 = []
        edata2 = []
        for k in range(0, len(xdata)):
            if xdata[k] < ydiv:
                xdata1.append(xdata[k])
                ydata1.append(ydata[k])
                edata1.append(edata[k])
            else:
                xdata2.append(xdata[k])
                ydata2.append(ydata[k])
                edata2.append(edata[k])

#
#---- actual data plotting
#
        #p, = plt.plot(xdata, ydata, color=colorList[i], marker='*', markersize=4.0, lw =0)
        #errorbar(xdata, ydata, yerr=edata, color=colorList[i],  markersize=4.0, fmt='*')
        p, = plt.plot(xdata, ydata, color='black', marker='*', markersize=4.0, lw =0)
        errorbar(xdata, ydata, yerr=edata, color=colorList[i],  markersize=0.0, fmt='*')
#
#--- fitting straight lines with robust method and plot the results
#
        xdata1 = numpy.array(xdata1)
        ydata1 = numpy.array(ydata1)
        edata1 = numpy.array(edata1)
        (intc, slope, err)  = robust.robust_fit(xdata1, ydata1)

        ystart = intc + slope * 2000
        ystop  = intc + slope * ydiv 
        lxdata = [2000, ydiv]
        lydata = [ystart, ystop]
        p, = plt.plot(lxdata, lydata, color=colorList[i], marker='', markersize=1.0, lw =2)

        xdata2 = numpy.array(xdata2)
        ydata2 = numpy.array(ydata2)
        edata2 = numpy.array(edata2)
        (intc2, slope2,err)  = robust.robust_fit(xdata2, ydata2)

        ystart = intc2 + slope2 * ydiv 
        ystop  = intc2 + slope2 * xmax 
        lxdata = [ydiv, xmax]
        lydata = [ystart, ystop]
        p, = plt.plot(lxdata, lydata, color=colorList[i], marker='', markersize=1.0, lw =2)

#
#--- add legend
#
        lslope = round(slope, 3)
        lslope2 = round(slope2, 3)
        line = entLabels[i] + ' Slope: ' + str(lslope) + ' (before '+ str(ydiv) + ') / ' + str(lslope2) + ' (after '+ str(ydiv) + ')'
        leg = legend([p],  [line], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec("%s.set_ylabel(yname, size=8)" % (axNam))

#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            line = eval("%s.get_xticklabels()" % (ax))
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

#----------------------------------------------------------------------------------
#-- find_previous_month: determine the previous month                            --
#----------------------------------------------------------------------------------
def find_previous_month():
#
#--- find today's date
#
    out   = time.strftime("%Y:%m:%d", time.gmtime())
    ltime = re.split(':', out)
    year  = int(float(ltime[0]))
#
#--- set the last month's month and year
#
    mon   = int(float(ltime[1])) - 1
    if mon < 1:
        mon   = 12
        year -= 1

    return [year, mon]

#--------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of report.")
    parser.add_argument("-d", "--date", required = False, help = "Date of month (format yyyy/mm) for monthly report.")
    args = parser.parse_args()

    if args.date:
        date_info = args.date.split("/")
        if len(date_info) != 2:
            parser.error(f"Provided data: {args.date} must be in yyyy/mm format")
        year = int(date_info[0])
        mon = int(date_info[1])
    else:
        [year, mon] = find_previous_month()

    if args.mode == 'test':
#
#--- TODO Redefine Directory Pathing
#
        monthly_report_cti_avg_plots(year, mon)
    else:
        
        monthly_report_cti_avg_plots(year, mon)
