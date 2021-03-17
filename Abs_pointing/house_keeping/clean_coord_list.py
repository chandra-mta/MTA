#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           clean_coord_list.py: sort and remove duplicated entries                             #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Jun 29, 2018                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string

f   = open('coord_list', 'r')
data = [line.strip() for line in f.readlines()]
f.close()

data.sort()

save = []
fo  = open('zout', 'w')
prev = ''
for ent in data:
    if ent == prev:
        continue
    else:
        fo.write(ent)
        fo.write('\n')
        prev = ent

fo.close()

cmd = 'mv coord_list coord_list~'
os.system(cmd)

cmd = 'mv zout coord_list'
os.system(cmd)
