#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#            run_compute_bias_data.py: run a script to extract bias related data            #
#                                                                                           #
#                       author: t. isobe (tisobe@cfa.harvard.edu)                           #
#                                                                                           #
#                       Last Update: Apr 02, 2021                                           #
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
import time
import astropy.io.fits as pyfits
import unittest
#
#--- reading directory list
#
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
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------
#--- compute_bias_data_main: the calling function to extract bias data          ----
#-----------------------------------------------------------------------------------

def compute_bias_data_main():
    """
    the calling function to extract bias data
    input:  None but read from local files (see find_today_data)
    output: bias data (see extract_bias_data)
    """
    if os.path.isdir('./Working_dir'):
        cmd = 'rm -rf ./Working_dir/*'
    else:
        cmd = 'mkdir -p ./Working_dir'
    os.system(cmd)
#
#--- find which data to use
#
    today_data = find_today_data()
#
#--- extract bias reated data
#
    extract_bias_data(today_data)

    update_bias_html()

#-----------------------------------------------------------------------------------
#--- find_today_data: find which data to use for the data anaysis                ---
#-----------------------------------------------------------------------------------

def find_today_data():
    """
    find which data to use for the data anaysis 
    input:  none but  read from <hosue_keeping>/past_input_data
                               /dsops/ap/sdp/cache/*/acis/*bias0.fits
    output:     today_data   ---- a list of fits files to be used
    """
#
#--- the find the last data entry date
#
    ifile = house_keeping + 'past_input_data'
    data1 = mcf.read_data_file(ifile)
    try:
        cut_date = bcf.extractTimePart(data1[-1])
        cut_date = int(cut_date)
    except:
        cut_date = 0

    file2 = house_keeping + 'past_input_data~'
    cmd   = 'mv ' + ifile + ' ' + file2
    os.system(cmd)
#
#--- read the current data list
#
    cmd   = 'ls /dsops/ap/sdp/cache/*/acis/*bias0.fits >' + zspace
    os.system(cmd)
    data2 = mcf.read_data_file(zspace, remove=1)
#
#--- find data which have not been analyzied
#
    today_data = []
    with  open(ifile, 'w') as fo:
        for ent in data2:
            fo.write(ent + '\n')
            chk = 0
            for comp in data1:
                if ent == comp:
                    chk = 1
                    break
    
            if chk == 0:
                date  = bcf.extractTimePart(ent)
#
#--- choose the data which are newer than the last entry
#
                if int(date) > cut_date:
                    today_data.append(ent)

    return today_data

#-----------------------------------------------------------------------------------
#--- extract_bias_data: extract bias data using a given data list               ----
#-----------------------------------------------------------------------------------

def extract_bias_data(today_data):
    """
    extract bias data using a given data list
    input:      today_data   --- a list of data fits files
                also need:
                <house_keeping>/Defect/bad_col_list --- a list of known bad columns
    output:     <data_dir>/Bias_save/CCD<ccd>/quad<quad>  see more in write_bias_data()
                <data_dir>/Info_dir/CCD<ccd>/quad<quad>   see more in printBiasInfo()
    """
    stime_list = []
    for dfile in today_data:
#
#--- check whether file exists
#
        if not os.path.isfile(dfile):
            continue 
#
#--- extract time stamp
#
        stime = bcf.extractTimePart(dfile)
        if stime < 0:
            continue
#
#--- extract CCD information
#
        [ccd_id, readmode, date_obs, overclock_a, overclock_b, overclock_c, overclock_d]\
                    = bcf.extractCCDInfo(dfile)

        if readmode != 'TIMED':
            continue

        bad_col0 = []
        bad_col1 = []
        bad_col2 = []
        bad_col3 = []

        ifile = house_keeping + 'Defect/bad_col_list'
        data  = mcf.read_data_file(ifile)

        for ent in data:
#
#--- skip none data line
#
            m = re.search('#', ent)
            if m is not None:
                continue

            atemp = re.split(':', ent)
            dccd  = int(atemp[0])

            if dccd  == ccd_id:
                val = int(atemp[1])
                if val <= 256:
                    bad_col0.append(val)
                elif val <= 512:
                    val -= 256
                    bad_col1.append(val)
                elif val <= 768:
                    val -= 512
                    bad_col2.append(val)
                elif val <= 1024:
                    val -= 768
                    bad_col3.append(val)
#
#--- trim the data at the threshold = 4000
#
        f     = pyfits.open(dfile)
        sdata = f[0].data
        sdata[sdata < 0]    = 0
        sdata[sdata > 4000] = 0
        f.close()
#
#--- compte and write out bias data
#
        result_list = bcf.extractBiasInfo(dfile)

        [fep, dmode, srow, rowcnt, orcmode, dgain, biasalg, barg0, barg1, barg2, barg3, \
         overclock_a, overclock_b, overclock_c, overclock_d] = result_list

        write_bias_data(sdata, ccd_id, 0, overclock_a, stime, bad_col0)
        write_bias_data(sdata, ccd_id, 1, overclock_b, stime, bad_col1)
        write_bias_data(sdata, ccd_id, 2, overclock_c, stime, bad_col2)
        write_bias_data(sdata, ccd_id, 3, overclock_d, stime, bad_col3)
#
#---- more bias info
#
        printBiasInfo(ccd_id, 0, stime, fep, dmode, srow, rowcnt, orcmode, dgain,\
                      biasalg,  barg0, barg1, barg2, barg3, overclock_a)
        printBiasInfo(ccd_id, 1, stime, fep, dmode, srow, rowcnt, orcmode, dgain,\
                      biasalg,  barg0, barg1, barg2, barg3, overclock_b)
        printBiasInfo(ccd_id, 2, stime, fep, dmode, srow, rowcnt, orcmode, dgain,\
                      biasalg,  barg0, barg1, barg2, barg3, overclock_c)
        printBiasInfo(ccd_id, 3, stime, fep, dmode, srow, rowcnt, orcmode, dgain,\
                      biasalg,  barg0, barg1, barg2, barg3, overclock_d)
    
        stime_list.append(stime)
#
#--- now count how many CCDs are used for a particular observations and write out to list_of_ccd_no
#
        countObservation(stime_list)

#-----------------------------------------------------------------------------------
#-- write_bias_data: extract and write out bias data                             ---
#-----------------------------------------------------------------------------------

def write_bias_data(sdata, ccd, quad, overclock, stime, bad_col):
    """
    extract and write out bias data 
    input:      sdata   ---- numpy array of 2D bias iamge
                ccd     ---- ccd #
                quad    ---- quad #
                overclock --- a list of overclock values
                stime     --- a list of time stamps
                bad_col   --- a list of known bad columns
                also need:
                ./comb.fits  --- created in extract_bias_data()
    output:     <data_dir>/Bias_save/CCD<ccd>/quad<quad>
                    this contains: 
                        time  ---- time in sec from 1998.1.1
                        avg   ---- average vaule of the entire surface except bad column regions
                        std   ---- standard deviation fo the eitire surface
                        overclock --- overclock value
    """
    if quad == 0:
        start = 1
        end   = 256

    elif quad == 1:
        start = 257
        end   = 512

    elif quad == 2:
        start = 513
        end   = 768

    elif quad == 3:
        start = 769
        end   = 1024
#
#--- extract the part (quad) we need
#
    tdata = sdata[1:1204, int(start):int(end)]
#
#---  compute average and std; if the column is listed in bad col list, skip it
#
    asum  = 0.0
    scnt  = 0.0
    lsave = [-999 for x in range(0,255)]
    for i in range(0, 255):
        csum = 0.0
        chk = 0
        for col in bad_col:
            if int(col) == i:
                chk = 1
                break
        if chk == 1:
            continue

        for j in range(0, 1023):
            csum += tdata[j, i]
            asum  += tdata[j, i]
            scnt += 1.0

        lsave[i] = csum / 1023.0

    if scnt > 0.0:
#
#--- find average and then coumpute std
#
        avg  = float(asum) / float(scnt)
        sum2 = 0.0
        scnt = 0.0
        for j in range(0, 255):
            if lsave[j]  >= 0:
                diff  = lsave[j] - avg
                sum2 += diff * diff
                scnt += 1.0

        std  = math.sqrt(float(sum2)/ float(scnt))
#
#--- print out the results
#
        bias_out = data_dir + 'Bias_save/CCD'+ str(ccd) + '/quad' + str(quad)
        line     = "%10.1f\t%4.2f\t%4.2f\t%s.0\n" % (stime, avg, std, overclock)

        with open(bias_out, 'a') as fo:
            fo.write(line)

#-----------------------------------------------------------------------------------
#-- printBiasInfo: create files containing bias file information                 ---
#-----------------------------------------------------------------------------------

def printBiasInfo(ccd, quad, stime, fep, dmode, srow, rowcnt, orcmode, dgain, biasalg,  barg0, barg1, barg2, barg3, overclock):
    """
    create files containing bias file information
    input:  ccd     --- ccd #
            quad    --- quad #
            steim   --- time stamp in DOM
            fep     --- fep value
            dmode   --- mode FAINT, VFAINT etc
            srow    --- starting row
            rowcnt  --- # of rows
            orcmode --- ORC mode
            biasalg --- bias algorithm
            barg0, barg1, barg2,barg3 --- biasarg0-3
            overclock-- overclock value
    output: <data_dir>/Info_dir/CCD<ccd>/quad<quad> 
              --- this contains all above information in that order
    """
    line = "%10.1f\t%4.2f\t" % (stime, overclock)
    line = line + str(dmode)   + '\t' + str(fep)     + '\t' + str(srow)  + '\t' 
    line = line + str(rowcnt)  + '\t' + str(orcmode) + '\t' + str(dgain) + '\t' 
    line = line + str(biasalg) + '\t' + str(barg0)   + '\t' + str(barg1) + '\t' 
    line = line + str(barg2)   + '\t' + str(barg3)   + '\n'

    ofile = data_dir + '/Info_dir/CCD' + str(ccd) + '/quad' + str(quad)
    with open(ofile, 'a') as fo:
        fo.write(line)

#-----------------------------------------------------------------------------------
#-- countObservation: count how many CCDs are used for a particular observations and write it out 
#-----------------------------------------------------------------------------------

def countObservation(stime_list):
    """
    count how many CCDs are used for a particular observations and write out to list_of_ccd_no
    input:  stime_list  ---  a list of time stamps used today
    output: <data_dir>/Info_dir/list_of_ccd_no
    """
    if len(stime_list) > 0:
        sorted_list = sorted(stime_list)

        comp = sorted_list[0]
        line = ''
        cnt  = 1
        for i in range(1, len(sorted_list)):
            if sorted_list[i] == comp:
                cnt += 1
            else:
                line = line +  str(comp) + '\t' + str(cnt) + '\n'

                comp = sorted_list[i]
                cnt  = 1

        line = line +  str(comp) + '\t' + str(cnt) + '\n'

        ofile = data_dir + '/Info_dir/list_of_ccd_no'
        with  open(ofile, 'a') as fo:
            fo.write(line)

#-----------------------------------------------------------------------------------
#-- update_bias_html: update bias_home.html page                                 ---
#-----------------------------------------------------------------------------------

def update_bias_html():
    """
    pdate bias_home.html page
    input: None but read from:
            <house_keeping>/bias_home.html
    output: <web_dir>/bias_home.html
    """
#
#--- line to replace
#
    newdate = "Last Upate: " + time.strftime("%m/%d/%Y", time.gmtime())
#
#--- read the template
#
    ifile = house_keeping + 'bias_home.html'
    data  = mcf.read_data_file(ifile)
#
#--- print out
#
    outfile = web_dir + 'bias_home.html'
    with open(outfile, 'w') as fo:
        for ent in data:
            m = re.search('Last Update', ent)
            if m is not None:
                fo.write(newdate + '\n')
            else:
                fo.write(ent + '\n')

#-----------------------------------------------------------------------------------------
#-- TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST    ---
#-----------------------------------------------------------------------------------------

class TestFunctions(unittest.TestCase):
    """
    testing functions
    """
#------------------------------------------------------------
    
    def test_compute_bias_data(self):

        today_data = find_today_data('test')
#
#--- extract bias reated data
#
        out = extract_bias_data(today_data, 'test')

        test_data = [1, 'VFAINT', 0, 1023, 0, 0, 1, 10, 26, 20, 26, 806, 577, 724, 670]
        self.assertEquals(out, test_data)

#--------------------------------------------------------------------

if __name__ == '__main__':

    #unittest.main()
    compute_bias_data_main()
