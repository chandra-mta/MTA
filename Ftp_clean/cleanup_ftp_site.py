#!/usr/bin/env /proj/sot/ska/bin/python
import os
import sys
import re

cmd = 'ls /stage/xmmops_ftp/* > zout'
os.system(cmd)

f    = open('zout', 'r')
data = [line.strip() for line in f.readlines()]
f.close()

os.system('rm -f zout')

for ent in data:
    mc = re.search('.dat', ent)
    if mc is not None:
        continue
    else:
        cmd = 'rm ' + ent
        os.system(cmd)

