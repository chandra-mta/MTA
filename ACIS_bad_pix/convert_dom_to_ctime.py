#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

import os
import sys
import re
import Chandra.Time

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

def run():
    cmd = 'ls ccd*_cnt col*_cnt hccd*_cnt hist_* front_side* > zxc'
    os.system(cmd)
    
    with open('zxc', 'r') as f:
        data = [line.strip() for line in f.readlines()]
    
    cmd = 'rm -f zxc'
    os.system(cmd)
    
    for dfile in data:
        print(dfile)
    
        with open(dfile, 'r') as f:
            out = [line.strip() for line in f.readlines()]
    
        save = []
        for line in out:
            atemp = re.split('<>', line)
#
#---- assume that if the first entry is not neumeric, the file is 
#---- either already removed dom or the file is not appropriate for the treatment
#
            try:
                val = float(atemp[0])
                chk = 1
            except:
                chk = 0
            if chk == 0:
                break
    
            alen  = len(atemp)
            btemp = re.split(':', atemp[1])

            ltime = btemp[0] + ':' + add_leading_zero(btemp[1], dlen=3)  + ':00:00:00'
            ctime = int(Chandra.Time.DateTime(ltime).secs)
            oline = str(ctime)
            for k in range(1,alen):
                oline = oline + '<>' + atemp[k]
    
            oline = oline + '\n'
            save.append(oline)
    
        if chk == 0:
            continue
    
        with open(dfile, 'w') as fo:
            for line in save:
                fo.write(line)

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

def add_leading_zero(val, dlen=2):

    try:
        val = int(val)
    except:
        return val
    
    val  = str(val)
    vlen = len(val)
    for k in range(vlen, dlen):
        val = '0' + val
    
    return val

#--------------------------------------------------------------------------

if __name__ == "__main__":
    run()
