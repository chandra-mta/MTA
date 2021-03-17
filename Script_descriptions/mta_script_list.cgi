#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#       mta_script_list.cgi:    create a list of MTA managed scripts                                    #
#                                                                                                       #
#           python version                                                                              #
#           author: t. isobe (tisobecfa.harvard.edu)                                                    #
#                                                                                                       #
#           last updated:   Oct 01, 2014                                                                #
#                                                                                                       #
#########################################################################################################

import sys
import os
import string
import re
import cgi
import time
import random

#
#--- import a local function
#
sys.path.append("/data/mta/www/mta_script_list/Scripts/")
import mta_script_sub_functions as mssf 

#-------------------------------------------------------------------------------------------------------
#-- print_page: this is a control cgi script to run the rest of the fuctnions                        ---
#-------------------------------------------------------------------------------------------------------

def print_page():
    """
    this is a control cgi script to run the rest of the fuctnions. this will make the loading
    of the page faster.

    """
    mssf.print_main_page()

#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    print_page()
