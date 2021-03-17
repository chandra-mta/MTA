#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#########################################################################################
#                                                                                       #
#       plot_bias.py: create  various history plots of bias related data                #
#                                                                                       #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                       #
#                   Last update: Mar 04, 2021                                           #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import random
import operator
import Chandra.Time
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

path = '/data/mta/Script/ACIS/Bad_pixels/house_keeping/bias_dir_list_py'
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
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- converTimeFormat contains MTA time conversion routines
#
import mta_common_functions    as mcf
import bad_pix_common_function as bcf
#
#--- set line color list
#
colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')

#---------------------------------------------------------------------------------------------------
#--- plot_bias_data: creates history plots of bias, overclock and bias - overclock               ---
#--------------------------------------------------------------------------------------------------- 

def plot_bias_data():
    """
    creates history plots of bias, overclock and bias - overclock
    input:  None but read from:
                <data_dir>/Bias_save/CCD<ccd>/quad<quad>
    output:     <web_dir>/Plots/Bias_bkg/ccd<ccd>.png'
                <web_dir>/Plots/Overclock/ccd<ccd>.png
                <web_dir>/Plots/Sub/ccd<ccd>.png
    """
    for ccd in range(0, 10):
#
#--- set arrays
#
        yMinSets1  = []
        yMaxSets1  = []
        xSets1     = []
        ySets1     = []
        entLabels1 = []

        yMinSets2  = []
        yMaxSets2  = []
        xSets2     = []
        ySets2     = []
        entLabels2 = []

        yMinSets3  = []
        yMaxSets3  = []
        xSets3     = []
        ySets3     = []
        entLabels3 = []

        for quad in range(0, 4):
#
#--- read data in
#
            file = data_dir + 'Bias_save/CCD' + str(ccd) + '/quad' + str(quad)
            f    = open(file, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()

            dtime     = []
            bias      = []
            overclock = []
            bdiff     = []
            scnt      = 0.0
            sum1      = 0.0
            sum2      = 0.0
            sum3      = 0.0

            for ent in data:
                try:
                    atemp = re.split('\s+|\t+', ent)
                    stime = float(atemp[0])

                    bval  = float(atemp[1])
                    oval  = float(atemp[3])
                    bmo   = bval - oval 

                    dtime.append(stime)
                    bias.append(bval)
                    overclock.append(oval)
                    bdiff.append(bmo)

                    sum1 += bval
                    sum2 += oval
                    sum3 += bmo
                    scnt += 1.0
                except:
                    pass
#
#--- put x and y data list into  the main list
#
            title = 'CCD' + str(ccd) + ' Quad' + str(quad)
            dtime = convert_stime_to_ytime(dtime)

            xSets1.append(dtime)
            ySets1.append(bias)
            entLabels1.append(title)

            xSets2.append(dtime)
            ySets2.append(overclock)
            entLabels2.append(title)

            xSets3.append(dtime)
            ySets3.append(bdiff)
            entLabels3.append(title)
#
#--- set plotting range
#
            xmin = min(dtime)
            xmax = max(dtime)
            diff = xmax - xmin
            xmin = int(xmin - 0.05 * diff)
            if xmin < 0:
                xmin = 0

            xmax = int(xmax + 0.05 * diff)
#
#-- plotting range of bias
#
            avg  = float(sum1) / float(scnt)
            ymin = int(avg - 200.0)
            ymax = int(avg + 200.0)

            yMinSets1.append(ymin)
            yMaxSets1.append(ymax)
#
#-- plotting range of overclock
#
            avg  = float(sum2) / float(scnt)
            ymin = int(avg - 200.0)
            ymax = int(avg + 200.0)

            yMinSets2.append(ymin)
            yMaxSets2.append(ymax)
#
#-- plotting range of bias - overclock
#
            ymin = -1.0
            ymax = 2.5
            if ccd == 7:
                ymin = 2.5
                ymax = 6.0

            yMinSets3.append(ymin)
            yMaxSets3.append(ymax)

        xname = "Time (Year)"
#
#--- plotting bias 
#
        yname = 'Bias'
        ofile = web_dir + 'Plots/Bias_bkg/ccd' + str(ccd) +'.png'
        plotPanel(xmin, xmax, yMinSets2, yMaxSets1, xSets1, ySets1, xname, yname,\
                  entLabels1, ofile, mksize=1.0, lwidth=0.0)
#
#--- plotting overclock
#
        yname = 'Overclock Level'
        ofile = web_dir + 'Plots/Overclock/ccd' + str(ccd) +'.png'
        plotPanel(xmin, xmax, yMinSets2, yMaxSets2, xSets2, ySets2, xname, yname,\
                  entLabels2, ofile,  mksize=1.0, lwidth=0.0)
#
#--- plotting bias - overclock
#
        yname = 'Bias'
        ofile = web_dir + 'Plots/Sub/ccd' + str(ccd) +'.png'
        plotPanel(xmin, xmax, yMinSets3, yMaxSets3, xSets3, ySets3, xname, yname,\
                  entLabels3, ofile, mksize=1.0, lwidth=0.0)

#-----------------------------------------------------------------------------------------------
#-- convert_stime_to_ytime: convert a list of time in seconds to fractional year              --
#-----------------------------------------------------------------------------------------------

def convert_stime_to_ytime(stime):
    """
    convert a list of time in seconds to fractional year
    input:  stime   --- a list of time in seconds from 1998.1.1
    output: ytime   --- a list of time in fractional year
    """
    ytime = []
    for ent in stime:
        out   = Chandra.Time.DateTime(ent).date
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
        year += (yday + hh / 24.0 + mm /1440.0 + ss / 86400.) / base

        ytime.append(year)

    return ytime

#-----------------------------------------------------------------------------------------------
#--- plot_bias_sub_info: creates history plots for overclock and bias devided by sub category --
#-----------------------------------------------------------------------------------------------

def plot_bias_sub_info():

    """
    creates history plots for overclock and bias devided by sub category 
    input:  None but read from:
                <data_dir>/Info_dir/CCD<ccd>/quad<quad>
                <data_dir>/Bias_save/CCD<ccd>/quad<quad>
    output:     <web_dir>/Plot/Param_diff/CCD<ccd>/CCD<ccd>_q<quad>/*
                <web_dir>/Plot/Param_diff/CCD<ccd>/CCD<ccd>_bias_q<quad>/*
                            obs_mode.png            --- categorized by FAINT / VERY FAINT / Others
                            partial_readout.png     --- categorized by Full Data / Partial Data
                            bias_arg1.png           --- categorized by biasarg1 = 9, 10, or others
                            no_ccds.png             --- categorized by # of CCD used: 5, 6, or others
    """

    for ccd in range(0, 10):
        for quad in range(0, 4):
#
#--- read data
#
            ifile    = data_dir + '/Info_dir/CCD' + str(ccd) + '/quad' + str(quad)
            dataSets = readBiasInfo(ifile)
            if dataSets == 0:
                continue
#
#--- overclock
#
            dir1   = web_dir + 'Plots/Param_diff/CCD' + str(ccd) + '/CCD' 
            dir1   = dir1    + str(ccd) +  '_q' + str(quad)
            col    = 1
            yname  = 'Overclock Level'
            lbound = 200
            ubound = 200
            plot_obs_mode(dir1,  dataSets, col, yname, lbound, ubound)
            plot_partial_readout(dir1, dataSets, col, yname, lbound, ubound)
            plot_bias_arg1(dir1, dataSets, col, yname, lbound, ubound)
            plot_num_ccds(dir1,  dataSets, col, yname, lbound, ubound)
#
#---  bias background
#
#
#--- since data size is different, adjust the data to the bais data sets
#
            biasSets    = readBiasInfo2(ccd, quad, dataSets)
            t_list      = biasSets[0]
            y_list      = convert_stime_to_ytime(t_list)
            biasSets[0] = y_list

            dir2   = web_dir + 'Plots/Param_diff/CCD' + str(ccd) + '/CCD' 
            dir2   = dir2    + str(ccd) + '_bias_q' + str(quad)

            col    = 13
            yname  = 'Bias'
            lbound = 3.0
            ubound = 3.0
            plot_obs_mode(dir2,  biasSets, col, yname, lbound, ubound)
            plot_partial_readout(dir2, biasSets, col, yname, lbound, ubound)
            plot_bias_arg1(dir2, biasSets, col, yname, lbound, ubound)
            plot_num_ccds(dir2,  biasSets, col, yname, lbound, ubound)

#-----------------------------------------------------------------------------------------------
#-- readBiasInfo: reads bias related data and make a list of 12 lists                        ---
#-----------------------------------------------------------------------------------------------

def readBiasInfo(ifile):
    """
    reads bias related data and make a list of 12 lists
    input:      ifile   --- inputfile name
    output:     a list of 12 lists which contains:
                    time, overclock, mode, ord_mode, 
                    outrow, num_row, sum2_2, deagain, 
                    biasalg, biasarg0, biasarg1, biasarg2, biasarg3
    """
    data = mcf.read_data_file(ifile)

    time      = []
    overclock = []
    mode      = []
    ord_mode  = []
    outrow    = []
    num_row   = []
    sum2_2    = []
    deagain   = []
    biasalg   = []
    biasarg0  = []
    biasarg1  = []
    biasarg2  = []
    biasarg3  = []
    bias      = []
    stest     = 0

    for ent in data:
        try:
            atemp = re.split('\s+|\t+', ent)
            time.append(float(atemp[0]))
            overclock.append(float(atemp[1]))
            mode.append(atemp[2])
            ord_mode.append(atemp[3])
            outrow.append(int(atemp[4]))
            num_row.append(int(atemp[5]))
            sum2_2.append(int(atemp[6]))
            deagain.append(float(atemp[7]))
            biasalg.append(float(atemp[8]))
            biasarg0.append(float(atemp[9]))
            biasarg1.append(float(atemp[10]))
            biasarg2.append(float(atemp[11]))
            biasarg3.append(float(atemp[12]))
            stest += 1
        except:
            pass

    if stest > 0:
        return [time, overclock, mode, ord_mode, outrow, num_row, sum2_2, deagain, \
                biasalg, biasarg0, biasarg1, biasarg2, biasarg3]
    else:
        return 0

#-----------------------------------------------------------------------------------------------
#--- readBiasInfo2: reads bias data and adds the list to category information                ---
#-----------------------------------------------------------------------------------------------

def readBiasInfo2(ccd, quad, dataSets):
    """
    reads bias data and adds the list to category information
    input:      ccd   --- CCD #
                quad  --- Quad #
                dataSets --- a list of 12 data sets (lists) which contains category data
                also need:
                <data_dir>/Bias_save/CCD<ccd>/quad<quad>
    output:     a list of 13 entiries; 12 above and one of category of 
                    <bias> - <overclock>
                at the 13th position
    """
    dlen  = len(dataSets)
#
#--- get a list of time stamp from the dataSets.
#
    ctime = dataSets[0]
#
#--- read the bias data
#
    ifile = data_dir + '/Bias_save/CCD' + str(ccd) + '/quad' + str(quad)
    data  = mcf.read_data_file(ifile)
#
#--- initialize a list to read out each category from dataSets
#
    biasSets = [[] for x in range(0, 13)]
    biasdata = []
#
#--- start checking bias data
#
    for ent in data:
       atemp = re.split('\s+|\t+', ent)
       try:
#
            btime = float(atemp[0])
            diff  = float(atemp[1]) - float(atemp[3])
#
#--- there are some bad data; ignore them
#
            if abs(diff) > 5:
                continue
#
#--- match the time in two data sets
#
            for i in range(0, len(ctime)):
                if btime < int(ctime[i]):
                    break
                elif int(btime) == int(ctime[i]):
#
#--- if the time stamps match, save all category data 
#
                    biasdata.append(diff)
                    for j in range(0, dlen):
                        earray  = dataSets[j]
                        val     = earray[i]
                        if isinstance(val, (long, int)):
                            biasSets[j].append(int(val))

                        elif isinstance(val, float):
                            biasSets[j].append(float(val))

                        else:
                            biasSets[j].append(val)
                    break    
       except:
            pass

    biasSets.append(biasdata)


    return biasSets

#-----------------------------------------------------------------------------------------------
#--- plot_obs_mode: creates history plots categorized by observation modes                   ---
#-----------------------------------------------------------------------------------------------

def plot_obs_mode(mdir, dataSets, col, yname, lbound, ubound):
    """
    creates history plots categorized by observation modes
    input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category 
                             data (except the first one is time)
                col      --- a position of data we want to use as a data
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
    output:     <mdir>/obs_mode.png     
    """
    dtime     = dataSets[0]             #--- time in Year

    if len(dtime) < 1:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + mdir + '/obs_mode.png'
        os.system(cmd)
        return

    dataset   = dataSets[col]
    mode      = dataSets[2]             #--- FAINT, VFAINT, etc

    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
#
#--- divide data into three categories
#
    try:
        for i in range(0, len(dtime)):
            if mode[i] == 'FAINT':
                x1.append(dtime[i])
                y1.append(dataset[i])
            elif mode[i] == 'VFAINT':
                x2.append(dtime[i])
                y2.append(dataset[i])
            else:
                x3.append(dtime[i])
                y3.append(dataset[i])
    except:
        pass
#
#--- create lists of lists to pass the data into plotting rouinte
#
    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)
    xSets.append(x3)

    ySets.append(y1)
    ySets.append(y2)
    ySets.append(y3)

    entLabels.append('Faint Mode')
    entLabels.append('Very Faint Mode')
    entLabels.append('Others')
#
#--- set plotting range
#
    xmin = min(dtime)
    xmax = max(dtime)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    acnt  = 0.0
    for ent  in dataset:
        asum += float(ent)
        acnt += 1.0
    avg = asum / acnt

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)

    for i in range(0, 3):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (Year)' 
#
#--- calling plotting routines; create 3 panels
#
    ofile = mdir + '/obs_mode.png'
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname,\
              entLabels, ofile,  mksize=1.0, lwidth=0.0)

#-----------------------------------------------------------------------------------------------
#--- plot_partial_readout: creates history plots categorized by full/partial readout         ---
#-----------------------------------------------------------------------------------------------

def plot_partial_readout(mdir, dataSets, col, yname, lbound, ubound):
    """
    creates history plots categorized by full/partial readout
    input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category 
                             data (except the first one is time)
                col      --- a position of data we want to use as a data
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
    output:     <mdir>/partial_readout.png
    """
    dtime     = dataSets[0]             #--- time in Year

    if len(dtime) < 1:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + mdir + '/partial_readout.png'
        os.system(cmd)
        return

    dataset   = dataSets[col]
    num_row   = dataSets[5]             #--- partial or full readout (if full 1024)

    x1 = []
    y1 = []
    x2 = []
    y2 = []
#
#--- categorize the data
#
    try:
        for i in range(0, len(dtime)):
            if int(num_row[i]) == 1024:
                x1.append(dtime[i])
                y1.append(dataset[i])
            else:
                x2.append(dtime[i])
                y2.append(dataset[i])
    except:
        pass

    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)

    ySets.append(y1)
    ySets.append(y2)

    entLabels.append('Full Readout')
    entLabels.append('Partial Readout')
#
#--- set plotting range
#
    xmin = min(dtime)
    xmax = max(dtime)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    for ent  in dataset:
        asum += float(ent)
    avg = asum / float(len(dataset))

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)

    for i in range(0, 2):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (Year)' 
#
#--- call plotting routine
#
    ofile = mdir + '/partial_readout.png'
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname,\
              entLabels, ofile, mksize=1.0, lwidth=0.0)

#-----------------------------------------------------------------------------------------------
#--- plot_bias_arg1: creates history plots categorized by biasarg1 value                    ----
#-----------------------------------------------------------------------------------------------

def plot_bias_arg1(mdir, dataSets, col, yname, lbound, ubound):
    """
    creates history plots categorized by biasarg1 value
    Input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category data 
                             (except the first one is time)
                col      --- a position of data we want to use as a data
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
    Output:     <mdir>/bias_arg1.png
    """
    dtime     = dataSets[0]

    if len(dtime) < 1:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + mdir + '/bias_arg1.png'
        os.system(cmd)
        return

    dataset   = dataSets[col]
    biasarg1  = dataSets[10]

    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
#
#--- categorize data biasarg = 9, 10, or others
#
    try:
        for i in range(0, len(dtime)):
            if biasarg1[i] == 9:
                x1.append(dtime[i])
                y1.append(dataset[i])
            elif biasarg1[i] == 10:
                x2.append(dtime[i])
                y2.append(dataset[i])
            else:
                x3.append(dtime[i])
                y3.append(dataset[i])
    except:
        pass

    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)
    xSets.append(x3)

    ySets.append(y1)
    ySets.append(y2)
    ySets.append(y3)

    entLabels.append('Bias Arg 1 = 9')
    entLabels.append('Bias Arg 1 = 10')
    entLabels.append('Bias Arg 1 : Others')
#
#--- set plotting range
#
    xmin = min(dtime)
    xmax = max(dtime)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    for ent  in dataset:
        asum += float(ent)
    avg = asum / float(len(dataset))

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)


    for i in range(0, 3):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (Year)' 
#
#--- call plotting routine
#
    ofile = mdir + '/bias_arg1.png'
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, \
              entLabels, ofile, mksize=1.0, lwidth=0.0)


#-----------------------------------------------------------------------------------------------
#--- plot_num_ccds: creates history plots categorized by numbers of ccd used                 ---
#-----------------------------------------------------------------------------------------------

def plot_num_ccds(mdir, dataSets, col, yname, lbound, ubound):

    """
    creates history plots categorized by numbers of ccd used 
    input:      mdir     --- Output directory
                dataSets --- a list of multiple lists. each list contains category data 
                             (except the first one is time)
                lbound   --- a lower boundary interval from the mean value of the data
                ubound   --- a upper boundary interval from the mean value of the data
                col      --- a position of data we want to use as a data
                also need:
                <data_dir>/Info_dir/list_of_ccd_no

    output:     <mdir>/no_ccds.png
    """
    dtime   = dataSets[0]

    if len(dtime) < 1:
        cmd = 'cp ' + house_keeping + 'no_data.png ' + mdir + '/no_ccds.png'
        os.system(cmd)
        return 

    dataset = dataSets[col]
#
#---- read ccd information --- ccd information coming from a different file
#
    ifile = data_dir + 'Info_dir/list_of_ccd_no'
    data  = mcf.read_data_file(line)

    ttime  = []
    ccd_no = []
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        ttime.append(float(atmpe[0]))
        ccd_no.append(int(atemp[1]))

    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
#
#--- compare time stamps and if they are same, catogorize the data
#
    for i in range(0, len(dtime)):
        chk = 0
        for j in range(0, len(ttime)):
            if dtime[i] == ttime[j]:
                if ccd_no[j] == 6:
                    x1.append(dtime[i])
                    y1.append(dataset[i])
                elif ccd_no[j] == 5:
                    x2.append(dtime[i])
                    y2.append(dataset[i])
                else:
                    x3.append(dtime[i])
                    y3.append(dataset[i])
                chk = 1
                continue
        if chk > 0:
            continue

    xSets     = []
    ySets     = []
    yMinSets  = []
    yMaxSets  = []
    entLabels = []

    xSets.append(x1)
    xSets.append(x2)
    xSets.append(x3)

    ySets.append(y1)
    ySets.append(y2)
    ySets.append(y3)

    entLabels.append('# of CCDs = 6')
    entLabels.append('# of CCDs = 5')
    entLabels.append('# of CCDs : Others')
#
#--- set plotting range
#
    xmin = min(dtime)
    xmax = max(dtime)
    diff = xmax - xmin
    xmin = int(xmin - 0.05 * diff)
    if xmin < 0:
        xmin = 0
    xmax = int(xmax + 0.05 * diff)
#
#--- for y axis, the range is the mean of the data - lbound/ + ubound
#
    asum  = 0.0
    for ent  in dataset:
        asum += float(ent)
    avg = asum / float(len(dataset))

    if lbound > 10:
        ymin = int(avg - lbound)
        ymax = int(avg + ubound)
    else:
        ymin = avg - lbound
        ymin = round(ymin, 1)
        ymax = avg + ubound
        ymax = round(ymax, 1)


    for i in range(0, 3):
        yMinSets.append(ymin)
        yMaxSets.append(ymax)

    xname = 'Time (Year)' 
#
#--- calling plotting rouinte
#
    ofile = mdir + '/no_ccds.png'
    plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, \
              entLabels, ofile, mksize=1.0, lwidth=0.0)

#---------------------------------------------------------------------------------------------------
#--- plotPanel: plots multiple data in separate panels                                           ---
#---------------------------------------------------------------------------------------------------

def plotPanel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels,ofile, mksize=1.0, lwidth=1.5):

    """
    This function plots multiple data in separate panels
    input:  xmin, xmax, ymin, ymax: plotting area
            xSets       --- a list of lists containing x-axis data
            ySets       --- a list of lists containing y-axis data
            yMinSets    --- a list of ymin 
            yMaxSets    --- a list of ymax
            ofile       --- output file name. png
            entLabels   --- a list of the names of each data
            mksize      --- a size of maker
            lwidth      --- a line width

    output: ofile       --- a png plot
    """
#
#--- close all opened plot
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

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
        exec("%s.set_autoscale_on(False)" % (axNam))
        exec("%s.set_xbound(xmin,xmax)"   % (axNam))

        exec("%s.set_xlim(left=xmin,          right=xmax,      auto=False)" % (axNam))
        exec("%s.set_ylim(bottom=yMinSets[i], top=yMaxSets[i], auto=False)" % (axNam))

        xdata  = xSets[i]
        ydata  = ySets[i]
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[i], marker='.', markersize=mksize, lw = lwidth)
#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
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
    fig    = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(ofile, format='png', dpi=200)

#--------------------------------------------------------------------

if __name__ == '__main__':
    
    plot_bias_data()
    plot_bias_sub_info()
