#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#####################################################################################
#                                                                                   #
#   count_rate_main.py: Read ACIS evnent 1 file and create quick dose count plot    #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           Last Update: Apr 02, 2019                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import operator
import math
import numpy

import matplotlib as mpl
if __name__ == '__main__':
    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

path = '/data/mta/Script/ACIS/Count_rate/Scripts3.6/house_keeping/dir_list_py'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

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
#--- import libraries
#
import mta_common_functions       as mcf  
#
#--- following three all contain acis dose related functions
#
import update_data_files          as udf
import plot_count_rate            as pcr
import print_html_page            as phtml

#---------------------------------------------------------------------------------------
#--- count_rate_main: the main function to run all acis count rate                   ---
#---------------------------------------------------------------------------------------

def count_rate_main():
    """
    the main function to run all acis count rate 
    input:  none
    output: data file (e.g. ccd0) and plots
    """
#
#--- update data files
#
    dir_save = udf.update_data_files()
#
#--- for the case the data are collected over two months period
#
    for idir in dir_save:
        pcr.create_plots(idir)
#
#--- update html pages
#
    phtml.print_html_page(comp_test)

#--------------------------------------------------------------------

if __name__ == '__main__':

    count_rate_main()

