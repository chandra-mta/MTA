#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#   create_adjusted_cti_tables.py: create adjusted cti data and print out the results       #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               Last update: Mar 03, 2021                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits as pyfits
import time
import Chandra.Time
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
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions as mcf     #---- contains other functions commonly used in MTA scripts
import robust_linear        as robust  #---- robust linear fit program
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random()) 
zspace = '/tmp/zspace' + str(rtail)

working_dir  = exc_dir + '/Working_dir/'
full_ccd     = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
det_ccd      = (0, 1, 2, 3, 4, 6, 8, 9)
elm_list     = ['al', 'mn', 'ti']

#---------------------------------------------------------------------------
#-- update_cti_tables: update all cti tables                             ---
#---------------------------------------------------------------------------

def update_cti_tables():
    """
    update all cti tables
    Input:  none, but read from <data_dir>/Results and <data_dir>/Det_Results
    Output: <data_dir>/Data*/* and <data_dir>/Det_Data*/*
    """
#
#--- make backup files
#
    for elm in elm_list:
        ifile  = data_dir + '/' + elm + '_factor'
        mk_backup(ifile)
#
#--- update normal cti data tables
#
    ccd_list      = full_ccd
    sub_dir       = '/Results/'
    sub2_dir_list = ['Data119', 'Data_cat_adjust', 'Data2000', 'Data7000']
    sub3_dir      = 'Data_adjust'

    create_adjusted_cti_tables(ccd_list, sub_dir, sub2_dir_list, sub3_dir)

    sub2_dir_list.append(sub3_dir)
    for idir in sub2_dir_list:
        clean_cti_data_table(idir)
#
#--- update detrended cti data tables
#
    ccd_list      = det_ccd
    sub_dir       = '/Det_Results/'
    sub2_dir_list = ['Det_Data119', 'Det_Data_cat_adjust', 'Det_Data2000', 'Det_Data7000']
    sub3_dir      = 'Det_Data_adjust'

    create_adjusted_cti_tables(ccd_list, sub_dir, sub2_dir_list, sub3_dir)

    sub2_dir_list.append(sub3_dir)
    for idir in sub2_dir_list:
        clean_cti_data_table(idir)

#---------------------------------------------------------------------------
#-- create_adjusted_cti_tables: create adjusted table: Data119, Data2000, Data7000, Data_cat-adjust-
#---------------------------------------------------------------------------

def create_adjusted_cti_tables(ccd_list, sub_dir, sub2_dir_list, out_dir):
    """
    create adjusted cti table: Data119, Data2000, Data7000, Data_cat-adjust
    Input:  ccd_list        --- a list of ccd #
            sub_dir         --- a name of sub directory which cti lists are read
            sub2_dir_list   --- a list of sub directories which adjusted cti tables are deposited
            out_dir         --- a directory name which adjucted cti will be deposited
                cti data are read from <data_dir>/<sub_dir>/<elm>_ccd<ccd #>
    Output: <data_dir>/<dir in sub2_dir_list>/<elm>_ccd<ccd#>
    """
    for elm in elm_list:

        for ccd in ccd_list:

            if ccd in [5, 7]:
                factor = 0.045              #--- these factors are given by C. Grant
            else:
                factor = 0.036
#
#--- read the main data set
#
            ifile = data_dir + sub_dir + '/' + elm + '_ccd' + str(ccd)
            data  = mcf.read_data_file(ifile)

            save1 = []
            save2 = []
            save3 = []
            save4 = []

            time3 = []
            time4 = []
            del_temp = []

            for ent in data:
#
#--- convert time format from 2013-10-05T17:35:58 to  year, stime and fractional year
#
                atemp   = re.split('\s+', ent)
                out     = time.strftime('%Y:%j:%H:%M:%S', time.strptime(atemp[0], '%Y-%m-%dT%H:%M:%S'))
                sectime = Chandra.Time.DateTime(out).secs
                fyear   = mcf.chandratime_to_fraq_year(sectime)
                
                tspan       = int(atemp[12]) - int(atemp[11])
                temperature = float(atemp[7])
#
#--- use only data with the integration time longer than 1000 sec before 2003
#--- and only data with the integration time longer than 2000 sec after 2003
#
                if tspan < 1000:
                    pass
                elif (tspan < 2000) and (fyear >= 2003):
                    pass

                line = ent + '\n'
                save3.append(line)
                time3.append(fyear)
#
#--- we need to adjust focal plane temperature between 9/16/2005 - 10/16/2005
#--- a reported temperature is about 1.3 warmer than a real focal temperature
#--- (from 12/1/05 email from C. Grant)
#
                if (sectime >= 243215999) and (sectime <= 245894399):
                    temperature -= 1.3

                if temperature <= -119.5:
                    line = ent + '\n'
                    save1.append(line)

                    if tspan >= 7000:
                        save4.append(line)
                        time4.append(fyear)
#
#--- correct temperature dependency with C. Grat factors
#
                val = factor * (temperature + 119.87)

                quad0 = select_grant_cti(atemp[1], val)
                quad1 = select_grant_cti(atemp[2], val)
                quad2 = select_grant_cti(atemp[3], val)
                quad3 = select_grant_cti(atemp[4], val)

                if (quad0 != 'na') and (quad1 != 'na') and (quad2 != 'na') and (quad3 != 'na'):
                    line = atemp[0]         + '\t'
                    line = line + quad0     + '\t' 
                    line = line + quad1     + '\t' 
                    line = line + quad2     + '\t' 
                    line = line + quad3     + '\t' 
                    line = line + atemp[5]  + '\t' 
                    line = line + atemp[6]  + '\t' 
                    line = line + atemp[7]  + '\t' 
                    line = line + atemp[8]  + '\t' 
                    line = line + atemp[9]  + '\t' 
                    line = line + atemp[10] + '\t' 
                    line = line + atemp[11] + '\t' 
                    line = line + atemp[12] + '\n' 

                    save2.append(line)
#
#--- print out adjsted cti data table
#
            j = 0
            for sdir in sub2_dir_list:
                j += 1
                sdata = eval('save%s' % (j))
                print_cti_results(sdir, elm, ccd, sdata)
#
#---- compute adjusted cti values and update tables
#
            compute_adjusted_cti(elm, ccd, time3, save3, time4, save4, out_dir)

#---------------------------------------------------------------------------------------
#-- mk_backup: copy a file to file~ if file is not an enmpty file                     --
#---------------------------------------------------------------------------------------

def mk_backup(ifile):
    """
    copy a file to file~ if file is not an enmpty file
    Input:  file    --- original file
    Output: file2   --- file with "~" at the end
    """
    file2 = ifile + '~'
    if os.path.isfile(ifile):
        if os.stat(ifile).st_size != 0:
            if os.path.isfile(file2):
                cmd = 'rm -f ' + file2
                os.system(cmd)
            cmd = 'cp -f ' + ifile + ' ' + file2
            os.system(cmd)
        else:
            cmd =  'cp ' + file2 + ' ' +  ifile
            os.system(cmd)
    else:
        cmd =  'cp ' + file2 + ' ' + ifile
        os.system(cmd)

#---------------------------------------------------------------------------------------
#-- select_grant_cti: select and adjust cti accroding to C. Grant criteria           ---
#---------------------------------------------------------------------------------------

def select_grant_cti(line, val):
    """
    select and adjust cti accroding to C. Grant criteria
    Input:  line        --- cti value +- error
            val         --- a correcting value
    Output: corrected   --- a corrected cti
    """
    r1 = re.search('-99999', line)
    if r1 is not None:
        return line

    else:
        atemp = re.split('\+\-', line)
        ftemp = float(atemp[0])
        err   = atemp[1]
    
        qtemp = ftemp - val
        if qtemp > 10.0:
            return 'na'
        else:
            if qtemp < 0:
                corrected = str(int(qtemp))  + '+-' + err
            else:
                qtemp = '%.3f' % round(qtemp, 3)
                qvar  = str(qtemp)
                qlen  = len(qvar)
                if qlen < 5:
                    for i in range(qlen, 5):
                        qvar = qvar + '0'

                corrected = qvar + '+-' + err
            return corrected

#---------------------------------------------------------------------------------------
#-- print_cti_results: print out selected/corrected cti data to an appropriate file   --
#---------------------------------------------------------------------------------------

def print_cti_results(out_type, elm, ccd, content):
    """
    print out selected/corrected cti data to an appropriate file
    Input:  out_type    --- directory name under <data_dir>
            elm         --- the name of element (al, mn, ti)
            ccd         --- ccd #
            content     --- a table list. each line is already terminated by "\n"
    Output: <data_dir>/<out_type>/<elm>_ccd<ccd#>
    """
    sline = ''
    for ent in content:
        sline = sline + ent
#
#--- just in a case, the line is not terminated by '\n', add it
#
        chk = re.search('\n', ent)
        if chk is None:
            sline = sline + '\n'

    if sline != '':
        ifile = data_dir + '/' +  out_type + '/' + elm + '_ccd' + str(ccd)
        mcf.rm_files(ifile)

        with open(ifile, 'w') as fo:
            fo.write(sline)

#---------------------------------------------------------------------------------------
#-- compute_adjusted_cti: compute adjusted cti                                       ---
#---------------------------------------------------------------------------------------

def compute_adjusted_cti(elm, ccd, time, data, atime, adata, sub_dir):
    """
    compute adjusted cti
    Input:  elm     --- element al, mn, ti
            ccd     --- ccd #
            time    --- array of time for the data
            data    --- array of data
            atime   --- array of time of the referenced data
            adata   --- array of data fo the referenced data
            sub_dir --- sub directory name
    Output: <data_dir>/<elm>_factor
            <data_dir>/<sub_dir>/<elm>_ccd<ccd#>
    """
#
#--- initialize
#
    quad  = ['' for x in range(4)]
    err   = ['' for x in range(4)]
    aquad = ['' for x in range(4)]
    equad = ['' for x in range(4)]

    m  = re.search('Det_', sub_dir)
    if m is not None:
        t_type =  'det'
    else:
        t_type = ''
#
#--- separate th main data set to arrays, each of out[i] is an array of data
#
    out = separate_data(data)

    for i in range(0, 4):
        quad[i] = out[i]
        err[i]  = out[i+4]

    start = out[8]
    stop  = out[9]
    obsid = out[10]
    temp  = out[11]
    sigm  = out[12]
    tmin  = out[13]
    tmax  = out[14]
    secs  = out[15]
    sece  = out[16]
    del_temp = out[17]
#
#--- extract cti data part from comparison data set
#
    out = separate_data(adata)
    for i in range(0, 4):
        aquad[i] = out[i]
#
#--- go though each quad
#
    for i in range(0, 4):
#
#--- compute a linear fit for time vs cti so that we can remove a cti evolution effect
#
        adjusted = get_time_adjustment(time, quad[i], atime, aquad[i])
#
#--- compute a linear fit for temp vs cti so that we can find a correciton factor
#
        xv = []
        yv = []
        for k in range(0, len(adjusted)):
            if adjusted[k] != -99999:
                xv.append(del_temp[k])
                yv.append(adjusted[k])

        [intc, slope] = linear_fit(xv, yv)
#
#--- print out the correction fuctors
#
        if t_type != 'det':
            print_out_factor(elm, ccd, i, slope)
#
#--- adjust cti with the esimated fit
#
        equad[i] = adjst_cti_with_factor(quad[i], del_temp, intc, slope)
#
#--- print out adjusted cti data table
#
    cti_list = [equad[0], equad[1], equad[2], equad[3]]
    err_list = [err[0],   err[1],   err[2],   err[3]]

    print_adjusted_cti_table(elm, ccd, start,stop, obsid, temp, sigm, tmin,\
                             tmax, secs, sece, cti_list, err_list, sub_dir)

#---------------------------------------------------------------------------------------
#-- print_out_factor: printing out correction factors                                ---
#---------------------------------------------------------------------------------------

def print_out_factor(elm, ccd, quad, factor):
    """
    printing out correction factors
    Input:  elm     --- element al, mn, ti
            ccd     --- ccd #
            quad    --- quad #
            factor  --- correction factor
    Output: <data_dir>/<elm>_factor
    """
    ifile   = data_dir + '/' + elm + '_factor'
    with open(ifile, 'a') as fo:
        factor = '%.5f' %  round(factor, 5)
        line   = 'CCD' + str(ccd) + '\tQuad' + str(quad) + '\tFactor: ' + str(factor) + '\n'
        fo.write(line)

#---------------------------------------------------------------------------------------
#-- adjst_cti_with_factor: adjust cti with the esimated fit                          ---
#---------------------------------------------------------------------------------------

def adjst_cti_with_factor(data, del_temp, intc, slope):
    """
    adjust cti with the esimated fit
    Input:  data    --- cti data
            del_temp--- temperature with -119.7 as 0 point
            intc    --- intercept of the correction fitting
            slope   --- slope of the correction fitting
    Output: q_estimate  --- corrected cti list
    """
    q_estimated = []

    for j in range(0, len(data)):
        if float(data[j]) < 0:
            q_estimated.append(int(data[j]))
        elif del_temp[j] > 0:
            val  = float(data[j]) - (intc + slope * float(del_temp[j]))
            valm = '%.3f' %  round(val, 3)
            q_estimated.append(valm)       
        else:
#
#--- if the focal temperature is lower than -119.7 (or del_temp < 0), use the cti 
#--- value without correcting
#
            valm = '%.3f' %  round(float(data[j]), 3)
            q_estimated.append(valm)

    return q_estimated

#---------------------------------------------------------------------------------------
#-- separate_data: separate each element to a set of arrays                          ---
#---------------------------------------------------------------------------------------

def separate_data(data):
    """
    separate each element to a set of arrays
    Input:  data    --- data sets which contains:
                        <start><quad#>+-<err> <obsid> <stop> <span> <temperature>
    Output: quad#   --- cti value for the quad
            err#    --- error value for the quad
            start   --- start time
            stop    --- stop time
            obsid   --- obsid
            span    --- time span in seconds
            temp    --- focal temperature
            del_tep --- temperature - 119.7
    """
#
#--- initialize
#
    cti   = [[] for x in range(4)]
    err   = [[] for x in range(4)]
    start = []
    stop  = []
    obsid = []
    temp  = []
    sigm  = []
    tmin  = []
    tmax  = []
    secs  = []
    sece  = []
    del_temp = []
#
#--- separate cti values and error values
#
    try:
        outarray = mcf.separate_data_to_arrays(data)
        chk  = 1
    except:
        chk  = 0

    if chk  > 0:
        for i in range(1, 5):
            for ent in outarray[i]:
                atemp = re.split('\+\-', ent)
    
                cti[i-1].append(atemp[0])
                err[i-1].append(atemp[1])
    
        start = outarray[0]
        obsid = outarray[5]
        stop  = outarray[6]
        temp  = outarray[7]
        sigm  = outarray[8]
        tmin  = outarray[9]
        tmax  = outarray[10]
        secs  = outarray[11]
        sece  = outarray[12]
    
        for ent in temp:
            val = float(ent) + 119.7
            del_temp.append(val)

    return (cti[0], cti[1], cti[2], cti[3], err[0], err[1], err[2], err[3], start, stop,\
            obsid, temp, sigm, tmin, tmax, secs, sece, del_temp);

#---------------------------------------------------------------------------------------
#-- get_quad_cti: get cti parts of error parts from input lines                      ---
#---------------------------------------------------------------------------------------

def get_quad_cti(ent, pos = 0):
    """
    get cti parts of error parts from input lines
    Input:  ent     --- line contains cti of quad0, 1, 2, 3 values in the positin 1, 2, 3, 4
            pos     --- if 0, cti value, if 1, error value
    Output: olist   --- a list of 4 values of either quad cti or their error
    """
    olist  = []
    atemp = re.split(ent)
    for i in range(1, 5):
        btemp = re.split('+-', atemp[i])

        try:
            val = float(btemp[pos])
        except:
            val = -99999;

        olist.append(val)

    return olist

#---------------------------------------------------------------------------------------
#-- get_time_adjustment: compute a linear fit for time vs cti and remove a cti evolution effect 
#---------------------------------------------------------------------------------------

def get_time_adjustment(time, quad, atime, aquad):
    """
    compute a linear fit for time vs cti so that we can remove a cti evolution effect
    Input:  time    --- time array of the data set which will be modified
            quad    --- quad array of the data set which will be modified
            atime   --- time array which is used to compute a base line
            aquad   --- quad array which is used to compute a base line
    Output: adjusted--- a list of cti values which are removed time dependency
    """
    [intc, slope] = linear_fit(atime, aquad)

    adjusted = []
    for i in range(0, len(time)):
#
#--- if quad < 0, it is an error case; so just pass it as it is
#
        if float(quad[i]) == -99999:
            adjusted.append(quad[i])
        else:
            estimate = float(quad[i]) - (intc + slope * float(time[i]))
            adjusted.append(estimate)

    return adjusted

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
#--- first remove error entries (which is -99999)
#
    xn = []
    yn = []
    for i in range(0, len(x)):
        if float(y[i]) != -99999:
            xn.append(float(x[i]))
            yn.append(float(y[i]))

    if len(xn) > 3:
        try:
            (a, b, berr) = robust.robust_fit(xn, yn)
            return [a, b]
        except:
            return [0,0]
    else:
        return [0, 0]

#---------------------------------------------------------------------------------------
#-- print_adjusted_cti_table: print out adjusted cti data tables                     ---
#---------------------------------------------------------------------------------------

def print_adjusted_cti_table(elm, ccd, start, stop, obsid, temp, sigm, tmin, tmax,\
                             secs, sece, equad, err, out_dir):
    """
    print out adjusted cti data tables
    Input:  elm     --- element: al, mn, ti
            ccd     --- ccd #
            start   --- start time
            stop    --- stop time
            obsid   --- obsid
            span    --- data time span in seconds
            equad   --- a list of cti of quad#
            err     --- a list of error of quad#
            out_dir --- output directory name
    Output: <data_dir>/<out_dir>/<elm>_ccd<ccd#>
    """
    sline = ''
    for i in range(0, len(start)):
        sline = sline + start[i] + '\t'

        for j in range(0, 4):
            data  = str(equad[j][i])
            dlen  = len(data)
            if dlen < 5:
                for k in range(dlen, 5):
                    data = data + '0'

            error = str(err[j][i])
            sline = sline + data +  '+-' + error + '\t'

        sline = sline + str(obsid[i]) + '\t'
        sline = sline + str(stop[i])  + '\t'
        sline = sline + str(temp[i])  + '\t'
        sline = sline + str(sigm[i])  + '\t'
        sline = sline + str(tmin[i])  + '\t'
        sline = sline + str(tmax[i])  + '\t'
        sline = sline + str(secs[i])  + '\t'
        sline = sline + str(sece[i])  + '\n'

    ifile = data_dir + out_dir + '/' +  elm + '_ccd' + str(ccd)
    with open(ifile, 'w') as fo:
        fo.write(sline)

#---------------------------------------------------------------------------------------
#-- clean_cti_data_table: remove  extrme outlyers and then clean up output data tables--
#---------------------------------------------------------------------------------------

def clean_cti_data_table(idir):
    """
    remmove data points which are extrme outlyers and then clean up output data tables.
    Input:  idir     --- the directory where the data files are kept
    Output: updated data files in the directory <dir>
    """
    dropped_obsids = []
    sline = ''
    for elm in elm_list:
        sline = sline + 'ELM: ' + elm + '\n'

        for ccd in range(0, 10):
#
#--- drop_factor sets the boundray of the outlyer: how may signam away?
#
            if ccd in [5, 7]:
                drop_factor = 5.0
            else:
                drop_factor = 4.0
#
#--- check the input file exists
#
            dname = data_dir + idir + '/' +  elm + '_ccd' + str(ccd)
            if os.stat(dname).st_size > 0:
                sline = sline + 'CCD: ' + str(ccd) + '\n'

                data = mcf.read_data_file(dname)
#
#--- separate data into separate array data sets
#
                dcolumns = separate_data(data)

                cti    = ['' for x in range(4)]

                cti[0] = dcolumns[0]
                cti[1] = dcolumns[1]
                cti[2] = dcolumns[2]
                cti[3] = dcolumns[3]
                obsid  = dcolumns[10]

                fy_list = []
                for ent in dcolumns[-2]:
#
#--- dcolumns[-2] is the end time in seconds from 1998.1.1; convert  to fractional year
#
                    fyr  = mcf.chandratime_to_fraq_year(ent)
                    fy_list.append(fyr)
#
#--- go around quads 
#
                drop_list = []
                for i in range(0, 4):
                    sline = sline + "QUAD" + str(i)+ '\n'
#
#--- fit a lienar line
#
                    (intc, slope) = linear_fit(fy_list, cti[i])
                    isum = 0
#
#--- compute a deviation from the fitted line
#
                    diff_save = []
                    for j in range(0, len(fy_list)):
                        diff = float(cti[i][j]) - (intc + slope * float(fy_list[j]))
                        diff_save.append(diff)
                        isum += diff * diff

                    sigma = math.sqrt(isum/len(fy_list))
#
#--- find outlyers
#
                    out_val = drop_factor * sigma
                    for j in range(0, len(fy_list)):
                        if diff_save[j] > out_val:
                            drop_list.append(j)

                            sline = sline + data[j] + '\n'
#
#--- clean up the list; removing duplicated lines
#
                drop_list = sorted(list(set(drop_list)))

                cleaned_data = []
                for i in range(0, len(fy_list)):
                    chk = 0
                    for comp in drop_list:
                        if i == comp:
                            chk = 1
                            break
                    if chk == 0:
                        cleaned_data.append(data[i])

                cleaned_data = sorted(set(cleaned_data))

                for ent in drop_list:
                    dropped_obsids.append(obsid[ent])

            with open(dname, 'w') as f:
                for ent in cleaned_data:
                    f.write(ent + '\n')
            
    dropped = data_dir + idir + '/dropped_data'
    with  open(dropped, 'w') as fo:
        fo.write(sline)

    dropped_obsids = sorted(set(dropped_obsids))

    out = data_dir + idir + '/bad_data_obsid'
    with open(out, 'w') as f:
        for ent in dropped_obsids:
            f.write(ent + '\n')

#--------------------------------------------------------------------

if __name__ == '__main__':

    update_cti_tables()

