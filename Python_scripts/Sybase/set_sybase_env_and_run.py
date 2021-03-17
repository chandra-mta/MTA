#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#########################################################################################
#                                                                                       #
#   set_sybase_env_and_run.py: set Sybase environment to run with python3.6             #
#                               and run the command                                     #
#                                                                                       #
#               author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                       #
#               last update: Jun 21, 2019                                               #
#                                                                                       #
#########################################################################################

import sys
import subprocess
import os
import string
import re
import json
#
#--- mta managed python3.6 related libraries etc
#
sys.path.append('/data/mta/Script/Python3.6/envs/ska3/lib/python3.6/site-packages')
sys.path.append('/data/mta/Script/Python3.6/lib/python3.6/site-packages')

#---------------------------------------------------------------------------------
#-- set_sybase_env_and_run: set Sybase environment to run with python3.6 and run the command
#---------------------------------------------------------------------------------

def set_sybase_env_and_run(cmd, db='axafocat', fetch='fetchall'):
    """
    set Sybase environment to run with python3.6 and run the command
    input:  cmd     --- sybase command; fetching only
            db      --- database name; default axafocat
            fetch   --- fetchone or fetchall
    output: either a list of output (fetchall) or a string of output (fetchone)
    """
#
#--- setting the environment
#
    line = 'source /soft/SYBASE16.0/SYBASE.csh;'
    line = line + 'setenv PYTHONPATH /soft/SYBASE16.0/OCS-16_0/python/python34_64r/lib:'
    line = line + '/data/mta/Script/Python3.6/envs/ska3/lib/python3.6/site-packages:'
    line = line + '/data/mta/Script/Python3.6/lib/python3.6/site-packages/; '
#
#--- sybase command is run in get_value_from_sybase.py
#
    line = line + '/data/mta/Script/Python3.6/Sybase/get_value_from_sybase.py ' 
    line = line + '"' +  cmd + '"'  + ' ' + db
#
#--- run the command; output is a json string
#
    try:
        output = subprocess.check_output(line, shell=True, executable='/bin/csh')
    except:
        if fetch == 'fetchall':
            return [[]] 
        else:
            return []
#
#--- convert json string to a list (of list)
#
    olist = json.loads(output)

    if len(olist) < 1:
        if fetch == 'fetchall':
            return [[]] 
        else:
            return []
#
#--- return either a list of lists  (fetchall) or a list (fetchone)
#
    if fetch == 'fetchall':
        return olist
    else:
        try:
            return olist[0]
        except:
            return []

#---------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) == 2:
        cmd = sys.argv[1]
        out = set_sybase_env_and_run(cmd)
        print(str(out))

    elif len(sys.argv) == 3:
        cmd = sys.argv[1]

        mc  = re.search('fetch', sys.argv[2])
        if mc is not None:
            out = set_sybase_env_and_run(cmd, fetch=sys.argv[2])
            print(str(out))

        else:
            out = set_sybase_env_and_run(cmd, db=sys.argv[2])
            print(str(out))

    elif len(sys.argv) == 4:
        cmd = sys.argv[1]

        mc = re.search('fetch', sys.argv[2])
        if mc is not None:
            fetch = sys.argv[2]
            db    = sys.argv[3]
        else:
            fetch = sys.argv[3]
            db    = sys.argv[2]

        out = set_sybase_env_and_run(cmd, db=db, fetch=fetch)
        print(str(out))

    else:
        print("Usage: set_sybase_env_and_run.py 'cmd' <db name> <fetchall/fetchone>")
        print("<db name> and <fetch> are optional. The choice for fetch are two listed.")
        print("\nExample: set_sybase_env_and_run.py 'select last,email from person_short where pers_id=41812' axafusers")



