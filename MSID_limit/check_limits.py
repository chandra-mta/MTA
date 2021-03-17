#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

import os
import sys
import re
import string
import math
import sqlite3

#
#--- reading directory list
#
path = '/data/mta/Script/MSID_limit/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

glimmon      = main_dir +'glimmondb.sqlite3'

msid = sys.argv[1].strip().lower()

db = sqlite3.connect(glimmon)
cursor = db.cursor()
cursor.execute("SELECT * FROM limits WHERE msid='%s'" %msid)
allrows = cursor.fetchall()

if len(allrows) == 0:
    print("not in glimmon database")
    exit(1)

for ent in allrows:
    print(str(ent))



