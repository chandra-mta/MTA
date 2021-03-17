#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################################
#                                                                                                   #
#       clean_the_data.py: remove duplicated data line from data_summary data                       #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Mar 10, 2021                                                               #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string

#-----------------------------------------------------------------------------------------
#-- clean_the_data: remove duplicated data line from data_summary data                  --
#-----------------------------------------------------------------------------------------

def clean_the_data(ifile):
    """
    remove duplicated data line from data_summary data
    input:  ifile   --- a file name
    output: ifile   --- a cleaned data file
    """

    with open(ifile, 'r') as f
        data = [line.strip() for line in f.readlines()]

    head = data[0]
    data = data[1:]
    data.sort()

    save = [data[0]]
    comp = data[0]
    for ent in data:
        if ent == comp:
            continue
        else:
            comp = ent
            save.append(ent)

    line = head + '\n'
    for ent in save:
        line = line + ent + '\n'

    with open(ifile, 'w') as fo:
        fo.write(line)

#-----------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) > 1:
        ifile = sys.argv[1]
        clean_the_data(ifile)
    else:
        print "Need a input file\n"
        exit(1)

