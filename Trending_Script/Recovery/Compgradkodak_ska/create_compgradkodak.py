#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#       create_compgradkodak.py: create compgradkodak.fits file                             #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Apr 07, 2017                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import astropy.io.fits  as pyfits

import Chandra.Time
import Ska.engarchive.fetch as fetch

#
#--- add the path to mta python code directory
#
sys.path.append('/data/mta/Script/Python_script2.7/')

import mta_common_functions as mcf
import convertTimeFormat    as tcnv

#-----------------------------------------------------------------------------------
#-- create_compgradkodak: create  compgradkodak.fits file                         --
#-----------------------------------------------------------------------------------

def create_compgradkodak(input_file, outfile):
    """
    create  compgradkodak.fits file
    input:  input_file  --- input fits file which contains 5 min average data of all needed data
                            see: compgradkodak_input_msid_list for msid 
            outputfile  --- output fits file name
    """
#
#--- input_file contains all 5 min average data for the entier time period
#
    ff = pyfits.open(input_file)
    col_list = ff[1].columns.names
    data_list = ff[1].data
    ff.close()
#
#--- separate data into array
#
    for ent in col_list:
        data = data_list[ent]
        if ent == 'TIME':
            atime = data
        else:
            exec "%s = data" %(ent.upper())
#------

    HRMASUM1 = (OHRTHR02_AVG + OHRTHR03_AVG + OHRTHR04_AVG + OHRTHR05_AVG + OHRTHR06_AVG\
              + OHRTHR07_AVG + OHRTHR08_AVG + OHRTHR09_AVG + OHRTHR10_AVG + OHRTHR11_AVG)

    HRMASUM2 = (OHRTHR12_AVG + OHRTHR13_AVG + OHRTHR21_AVG + OHRTHR22_AVG + OHRTHR23_AVG\
              + OHRTHR24_AVG + OHRTHR25_AVG + OHRTHR26_AVG + OHRTHR28_AVG)

    HRMASUM3 = (OHRTHR29_AVG + OHRTHR30_AVG + OHRTHR33_AVG + OHRTHR36_AVG + OHRTHR37_AVG\
              + OHRTHR44_AVG + OHRTHR45_AVG + OHRTHR46_AVG + OHRTHR47_AVG)

    HRMASUM4 = (OHRTHR49_AVG + OHRTHR50_AVG + OHRTHR51_AVG + OHRTHR52_AVG + OHRTHR53_AVG\
              + OHRTHR55_AVG + OHRTHR56_AVG)

    HRMAAVG_AVG  = (HRMASUM1 + HRMASUM2 + HRMASUM3 + HRMASUM4) / 35.0

    print "Step 1"

#------

    HRMACS1 = (OHRTHR06_AVG + OHRTHR07_AVG + OHRTHR08_AVG + OHRTHR09_AVG + OHRTHR10_AVG\
             + OHRTHR11_AVG + OHRTHR12_AVG + OHRTHR13_AVG + OHRTHR14_AVG)

    HRMACS2 = (OHRTHR15_AVG + OHRTHR17_AVG + OHRTHR25_AVG + OHRTHR26_AVG + OHRTHR29_AVG\
             + OHRTHR30_AVG + OHRTHR31_AVG + OHRTHR33_AVG + OHRTHR34_AVG)

    HRMACS3 = (OHRTHR35_AVG + OHRTHR36_AVG + OHRTHR37_AVG + OHRTHR39_AVG + OHRTHR40_AVG\
             + OHRTHR50_AVG + OHRTHR51_AVG + OHRTHR52_AVG + OHRTHR53_AVG)

    HRMACS4 = (OHRTHR54_AVG + OHRTHR55_AVG + OHRTHR56_AVG + OHRTHR57_AVG + OHRTHR58_AVG\
             + OHRTHR60_AVG + OHRTHR61_AVG)

    HRMACAV_AVG = (HRMACS1 + HRMACS2 + HRMACS3 + HRMACS4) / 34.0

    print "Step 2"

#------

    HRMAXGRD_AVG1 = (OHRTHR10_AVG + OHRTHR11_AVG + OHRTHR34_AVG\
                   + OHRTHR35_AVG + OHRTHR55_AVG + OHRTHR56_AVG) / 6.0

    HRMAXGRD_AVG2 = (OHRTHR12_AVG + OHRTHR13_AVG + OHRTHR36_AVG\
                   + OHRTHR37_AVG + OHRTHR57_AVG + OHRTHR58_AVG) / 6.0

    HRMAXGRD_AVG = (HRMAXGRD_AVG1 - HRMAXGRD_AVG2)

    print "Step 3"

#------

    HRMARAD1GRD = (OHRTHR08_AVG + OHRTHR31_AVG + OHRTHR33_AVG + OHRTHR52_AVG) / 4.0

    HRMARAD2GRD = (OHRTHR09_AVG + OHRTHR53_AVG + OHRTHR54_AVG)/3.0

    HRMARADGRD_AVG = (HRMARAD1GRD - HRMARAD2GRD)

    print "Step 4"

#------

    OBASUM1 = (OOBTHR08_AVG + OOBTHR09_AVG + OOBTHR10_AVG + OOBTHR11_AVG + OOBTHR12_AVG\
             + OOBTHR11_AVG + OOBTHR12_AVG + OOBTHR13_AVG + OOBTHR14_AVG + OOBTHR15_AVG)

    OBASUM2 = (OOBTHR17_AVG + OOBTHR18_AVG + OOBTHR19_AVG + OOBTHR20_AVG + OOBTHR21_AVG\
             + OOBTHR22_AVG + OOBTHR23_AVG + OOBTHR24_AVG + OOBTHR25_AVG + OOBTHR26_AVG)

    OBASUM3 = (OOBTHR27_AVG + OOBTHR28_AVG + OOBTHR29_AVG + OOBTHR30_AVG + OOBTHR31_AVG\
             + OOBTHR33_AVG + OOBTHR34_AVG + OOBTHR35_AVG + OOBTHR36_AVG + OOBTHR37_AVG)

    OBASUM4 = (OOBTHR38_AVG + OOBTHR39_AVG + OOBTHR40_AVG + OOBTHR41_AVG + OOBTHR44_AVG\
             + OOBTHR45_AVG + OOBTHR36_AVG)

    OBAAVG_AVG = (OBASUM1 + OBASUM2 + OBASUM3 + OBASUM4) / 37.0

    print "Step 5"

#-----

    OBACONE1 = (OOBTHR08_AVG + OOBTHR09_AVG + OOBTHR10_AVG + OOBTHR11_AVG + OOBTHR12_AVG\
              + OOBTHR13_AVG + OOBTHR14_AVG + OOBTHR15_AVG + OOBTHR17_AVG + OOBTHR18_AVG)


    OBACONE2 = (OOBTHR19_AVG + OOBTHR20_AVG + OOBTHR21_AVG + OOBTHR22_AVG + OOBTHR23_AVG\
              + OOBTHR24_AVG + OOBTHR25_AVG + OOBTHR26_AVG + OOBTHR27_AVG + OOBTHR28_AVG)

    OBACONE3 = (OOBTHR29_AVG + OOBTHR30_AVG + OOBTHR57_AVG + OOBTHR58_AVG + OOBTHR59_AVG\
              + OOBTHR60_AVG + OOBTHR61_AVG)

    OBACONEAVG_AVG = (OBACONE1 + OBACONE2 + OBACONE3) / 27.0

    print "Step 6"
#------

    FWBLKHDT1_AVG = (OOBTHR62_AVG + OOBTHR63_AVG + _4RT700T_AVG + _4RT701T_AVG\
                   + _4RT702T_AVG + _4RT703T_AVG + _4RT704T_AVG)

    FWBLKHDT2_AVG = (_4RT705T_AVG + _4RT706T_AVG + _4RT707T_AVG + _4RT708T_AVG\
                   + _4RT709T_AVG + _4RT710T_AVG + _4RT711T_AVG)

    FWBLKHDT_AVG = (FWBLKHDT1_AVG + FWBLKHDT2_AVG) / 14.0

    print "Step 7"
#------

    AFTBLKHDT_AVG = (OOBTHR31_AVG + OOBTHR33_AVG + OOBTHR34_AVG) / 3.0

    OBAAXGRD_AVG  = (FWBLKHDT_AVG - AFTBLKHDT_AVG)

    MZOBACONE_AVG = (OOBTHR08_AVG + OOBTHR19_AVG + OOBTHR26_AVG + OOBTHR31_AVG\
                   + OOBTHR57_AVG + OOBTHR60_AVG + _4RT575T_AVG) / 7.0

    PZOBACONE_AVG = (OOBTHR13_AVG + OOBTHR22_AVG + OOBTHR23_AVG + OOBTHR28_AVG\
                   + OOBTHR29_AVG + OOBTHR61_AVG) / 6.0

    OBADIAGRAD_AVG = (MZOBACONE_AVG - PZOBACONE_AVG)

    print "Step 8"
#-----------------------------

    alen = len(atime)
    HRMARANGE_AVG     = numpy.zeros(alen)
    TFTERANGE_AVG     = numpy.zeros(alen)
    HRMASTRUTRNGE_AVG = numpy.zeros(alen)
    SCSTRUTRNGE_AVG   = numpy.zeros(alen)
    for i in range(0, alen):
    
        if (OHRTHR02_AVG[i] <= OHRTHR03_AVG[i]) : 
            OHRTHR_MIN_AVG = OHRTHR02_AVG[i] 
        else:
            OHRTHR_MIN_AVG = OHRTHR03_AVG[i]
    
        if (OHRTHR04_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR04_AVG[i]
    
        if (OHRTHR05_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR05_AVG[i]
    
        if (OHRTHR06_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR06_AVG[i]
    
        if (OHRTHR07_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR07_AVG[i]
    
        if (OHRTHR08_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR08_AVG[i]
    
        if (OHRTHR09_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR09_AVG[i]
    
        if (OHRTHR10_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR10_AVG[i]
    
        if (OHRTHR11_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR11_AVG[i]
    
        if (OHRTHR12_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR12_AVG[i]
    
        if (OHRTHR13_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR13_AVG[i]
    
        if (OHRTHR21_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR21_AVG[i]
    
        if (OHRTHR22_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR22_AVG[i]
    
        if (OHRTHR23_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR23_AVG[i]
    
        if (OHRTHR24_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR24_AVG[i]
    
        if (OHRTHR25_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR25_AVG[i]
    
        if (OHRTHR26_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR26_AVG[i]
    
        if (OHRTHR29_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR29_AVG[i]
    
        if (OHRTHR30_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR30_AVG[i]
    
        if (OHRTHR33_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR33_AVG[i]
    
        if (OHRTHR36_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR36_AVG[i]
    
        if (OHRTHR37_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR37_AVG[i]
    
        if (OHRTHR44_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR44_AVG[i]
    
        if (OHRTHR45_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR45_AVG[i]
    
        if (OHRTHR46_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR46_AVG[i]
    
        if (OHRTHR47_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR47_AVG[i]
    
        if (OHRTHR49_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR49_AVG[i]
    
        if (OHRTHR50_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR50_AVG[i]
    
        if (OHRTHR51_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR51_AVG[i]
    
        if (OHRTHR52_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR52_AVG[i]
    
        if (OHRTHR53_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR53_AVG[i]
    
        if (OHRTHR55_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR55_AVG[i]
    
        if (OHRTHR56_AVG[i] <= OHRTHR_MIN_AVG) : 
            OHRTHR_MIN_AVG = OHRTHR56_AVG[i]
    
#----------------

        if (OHRTHR02_AVG[i] >= OHRTHR03_AVG[i]) : 
            OHRTHR_MAX_AVG = OHRTHR02_AVG[i] 
        else:
            OHRTHR_MAX_AVG = OHRTHR03_AVG[i]
    
        if (OHRTHR04_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR04_AVG[i]
    
        if (OHRTHR05_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR05_AVG[i]
    
        if (OHRTHR06_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR06_AVG[i]
    
        if (OHRTHR07_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR07_AVG[i]
    
        if (OHRTHR08_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR08_AVG[i]
    
        if (OHRTHR09_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR09_AVG[i]
    
        if (OHRTHR10_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR10_AVG[i]
    
        if (OHRTHR11_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR11_AVG[i]
    
        if (OHRTHR12_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR12_AVG[i]
    
        if (OHRTHR13_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR13_AVG[i]
    
        if (OHRTHR21_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR21_AVG[i]
    
        if (OHRTHR22_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR22_AVG[i]
    
        if (OHRTHR23_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR23_AVG[i]
    
        if (OHRTHR24_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR24_AVG[i]
    
        if (OHRTHR25_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR25_AVG[i]
    
        if (OHRTHR26_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR26_AVG[i]
     
        if (OHRTHR29_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR29_AVG[i]
    
        if (OHRTHR30_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR30_AVG[i]
    
        if (OHRTHR33_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR33_AVG[i]

        if (OHRTHR36_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR36_AVG[i]
    
        if (OHRTHR37_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR37_AVG[i]
    
        if (OHRTHR44_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR44_AVG[i]
    
        if (OHRTHR45_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR45_AVG[i]
    
        if (OHRTHR46_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR46_AVG[i]
    
        if (OHRTHR47_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR47_AVG[i]
    
        if (OHRTHR49_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR49_AVG[i]
    
        if (OHRTHR50_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR50_AVG[i]
    
        if (OHRTHR51_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR51_AVG[i]
    
        if (OHRTHR52_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR52_AVG[i]
    
        if (OHRTHR53_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR53_AVG[i]
    
        if (OHRTHR55_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR55_AVG[i]
    
        if (OHRTHR56_AVG[i] >= OHRTHR_MAX_AVG) : 
            OHRTHR_MAX_AVG = OHRTHR56_AVG[i]
    
        HRMARANGE_AVG[i] = ((OHRTHR_MAX_AVG)-(OHRTHR_MIN_AVG))

#------

        if (OOBTHR42_AVG[i] <= OOBTHR43_AVG[i]) : 
            TFTE_MIN_AVG = OOBTHR42_AVG[i] 
        else:
            TFTE_MIN_AVG = OOBTHR43_AVG[i]
    
        if (OOBTHR44_AVG[i] <= TFTE_MIN_AVG) : 
            TFTE_MIN_AVG = OOBTHR44_AVG[i]
    
        if (OOBTHR42_AVG[i] >= OOBTHR43_AVG[i]) : 
            TFTE_MAX_AVG = OOBTHR42_AVG[i] 
        else: 
            TFTE_MAX_AVG = OOBTHR43_AVG[i]
    
        if (OOBTHR44_AVG[i] >= TFTE_MAX_AVG) : 
            TFTE_MAX_AVG = OOBTHR44_AVG[i]
    
        TFTERANGE_AVG[i] = (TFTE_MAX_AVG - TFTE_MIN_AVG)

#------

        if (OOBTHR02_AVG[i] <= OOBTHR03_AVG[i]) : 
            HSTRUT_MIN_AVG = OOBTHR02_AVG[i] 
        else: 
            HSTRUT_MIN_AVG = OOBTHR03_AVG[i]
    
        if (OOBTHR04_AVG[i] <= HSTRUT_MIN_AVG) : 
            HSTRUT_MIN_AVG = OOBTHR04_AVG[i]
    
        if (OOBTHR05_AVG[i] <= HSTRUT_MIN_AVG) : 
            HSTRUT_MIN_AVG = OOBTHR05_AVG[i]
    
        if (OOBTHR06_AVG[i] <= HSTRUT_MIN_AVG) : 
            HSTRUT_MIN_AVG = OOBTHR06_AVG[i]
    
        if (OOBTHR07_AVG[i] <= HSTRUT_MIN_AVG) : 
            HSTRUT_MIN_AVG = OOBTHR07_AVG[i]
    
        if (OOBTHR02_AVG[i] >= OOBTHR03_AVG[i]) : 
            HSTRUT_MAX_AVG = OOBTHR02_AVG[i] 
        else:
            HSTRUT_MAX_AVG = OOBTHR03_AVG[i]
    
        if (OOBTHR04_AVG[i] >= HSTRUT_MAX_AVG) : 
            HSTRUT_MAX_AVG = OOBTHR04_AVG[i]
    
        if (OOBTHR05_AVG[i] >= HSTRUT_MAX_AVG) : 
            HSTRUT_MAX_AVG = OOBTHR05_AVG[i]
    
        if (OOBTHR06_AVG[i] >= HSTRUT_MAX_AVG) : 
            HSTRUT_MAX_AVG = OOBTHR06_AVG[i]
    
        if (OOBTHR07_AVG[i] >= HSTRUT_MAX_AVG) : 
            HSTRUT_MAX_AVG = OOBTHR07_AVG[i]
    
        HRMASTRUTRNGE_AVG[i] = (HSTRUT_MAX_AVG - HSTRUT_MIN_AVG)

#-----

        if (OOBTHR49_AVG[i] <= OOBTHR50_AVG[i]) : 
            SSTRUT_MIN_AVG = OOBTHR49_AVG[i] 
        else: 
            SSTRUT_MIN_AVG = OOBTHR50_AVG[i]
    
        if (OOBTHR51_AVG[i] <= SSTRUT_MIN_AVG) : 
            SSTRUT_MIN_AVG = OOBTHR51_AVG[i]
    
        if (OOBTHR52_AVG[i] <= SSTRUT_MIN_AVG) : 
            SSTRUT_MIN_AVG = OOBTHR52_AVG[i]
    
        if (OOBTHR53_AVG[i] <= SSTRUT_MIN_AVG) : 
            SSTRUT_MIN_AVG = OOBTHR53_AVG[i]
    
        if (OOBTHR54_AVG[i] <= SSTRUT_MIN_AVG) : 
            SSTRUT_MIN_AVG = OOBTHR54_AVG[i]
    
        if (OOBTHR49_AVG[i] >= OOBTHR50_AVG[i]) : 
            SSTRUT_MAX_AVG = OOBTHR49_AVG[i] 
        else: 
            SSTRUT_MAX_AVG = OOBTHR50_AVG[i]
    
        if (OOBTHR51_AVG[i] >= SSTRUT_MAX_AVG) : 
            SSTRUT_MAX_AVG = OOBTHR51_AVG[i]
    
        if (OOBTHR52_AVG[i] >= SSTRUT_MAX_AVG) : 
            SSTRUT_MAX_AVG = OOBTHR52_AVG[i]
    
        if (OOBTHR53_AVG[i] >= SSTRUT_MAX_AVG) : 
            SSTRUT_MAX_AVG = OOBTHR53_AVG[i]
    
        if (OOBTHR54_AVG[i] >= SSTRUT_MAX_AVG) : 
            SSTRUT_MAX_AVG = OOBTHR54_AVG[i]
    
        SCSTRUTRNGE_AVG[i] = (SSTRUT_MAX_AVG - SSTRUT_MIN_AVG)

    print "Step 9"

#
#-- take a daily avg and std
#
    cname = ["HRMAAVG_AVG",   "HRMACAV_AVG",    "HRMAXGRD_AVG",      "HRMARADGRD_AVG", "OBAAVG_AVG",    "OBACONEAVG_AVG",\
             "OBAAXGRD_AVG",  "OBADIAGRAD_AVG", "FWBLKHDT_AVG",      "AFTBLKHDT_AVG",  "MZOBACONE_AVG", "PZOBACONE_AVG",\
             "HRMARANGE_AVG", "TFTERANGE_AVG",  "HRMASTRUTRNGE_AVG", "SCSTRUTRNGE_AVG"] 

#
#--- set time range for each day
#
    out        = Chandra.Time.DateTime(float(atime[0])).date
    btemp      = re.split(':', out)
    start_year = int(float(btemp[0]))
    start_yday = int(float(btemp[1]))

    out        = Chandra.Time.DateTime(float(atime[-1])).date
    btemp      = re.split(':', out)
    stop_year  = int(float(btemp[0]))
    stop_yday  = int(float(btemp[1]))

    start_list = []
    stop_list  = []
    time_list  = []
    dom        = compute_dom(start_year, start_yday)

    mm = 0
    for year in range(start_year, (stop_year + 1)):
        if tcnv.isLeapYear(year) == 1:
            yend = 367
        else:
            yend = 366
        for yday in range(1, yend):
            if (year == start_year) and (yday < start_yday):
                continue
            elif (year == stop_year) and (yday > stop_yday):
                break

            lyday = str(int(yday))
            if yday < 10:
                lyday = '00' + lyday
            elif yday< 100:
                lyday = '0' + lyday

            btime = str(year) + ':' + lyday + ':00:00:00'
            begin = Chandra.Time.DateTime(btime).secs

            etime = str(year) + ':' + lyday + ':23:59:59.9'
            end   = Chandra.Time.DateTime(etime).secs

            #-------------------------
            #-- time format; currently it is dom but you may want to change to sec from 1998.1.1 in future
            #-------------------------
            #time_list.append(begin + 43200.0)
            time_list.append(dom)
            dom += 1.0
            #-------------------------

#
#--- create lists of indecies (in start_list and stop_list) which enclose each day
#
            chk = 0
            for k in range(mm, len(atime)):
                if (chk == 0) and (atime[k] >= begin):
                    start_list.append(k)
                    chk = 1
                elif atime[k] > end:
                    stop_list.append(k-1)
                    mm = k-5
                    break


    if len(stop_list) < len(start_list):
       stop_list.append(len(atime) -1) 

    print "Step 10"
#
#--- go through for each data set and compute daily average and std
#
    sdata = [time_list]
    for m in range(0, len(cname)):
        exec "data = %s" % (cname[m])

        avg_list = []
        dev_list = []
        for k in range(0, len(start_list)):
            avg = numpy.mean(data[start_list[k]:stop_list[k]])
            avg_list.append(avg)

            std = numpy.std(data[start_list[k]:stop_list[k]])
            dev_list.append(std)

        sdata.append(avg_list)
        sdata.append(dev_list)


    print "Step 11"
#
#--- print out the data
#
    sname = ["TIME"]
    for ent in cname:
        sname.append(ent)
        dname = ent.replace('_AVG', '_DEV')
        sname.append(dname)

    mcf.rm_file(outfile)
    write_fits(sname, sdata, outfile)


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def write_fits(col_list, data_list, outfile="",  format_list=''):

    if format_list == '':
        #format_list['E'] * len(col_list)
        format_list =[]
        for k in range(0, len(col_list)):
            format_list.append('E')

    ent_list = []
    for k in range(0, len(col_list)):
        acol = pyfits.Column(name=col_list[k], format=format_list[k], array=numpy.array(data_list[k]))
        ent_list.append(acol)

    coldefs = pyfits.ColDefs(ent_list)
    tbhdu   = pyfits.BinTableHDU.from_columns(coldefs)

    if outfile == "":
        outfile = "./temp_comp.fits"

    tbhdu.writeto(outfile)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def compute_dom(eyear, eyday):

    if eyear == 1999:
        dom = eyday - 201

    else:
        dom = 164
        for year in range(2000, eyear):
            if tcnv.isLeapYear(year) == 1:
                dom += 366
            else:
                dom += 365

        dom += eyday

    return dom

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    input_file = sys.argv[1]
    input_file.strip()

    if len(sys.argv) > 2:
        outfile = sys.argv[2]
        outfile.strip()
    else:
        outfile = 'compgradkodak.fits'

    create_compgradkodak(input_file, outfile)


