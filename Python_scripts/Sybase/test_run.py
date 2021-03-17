#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################
#                                                                               #
#       test_run.py: testing sybase access with set_sybase_env_and_run.py       #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Jun 21, 2019                                       #
#                                                                               #
#################################################################################

import sys
import subprocess
import os
import string
import re

sys.path.append('/data/mta/Script/Python3.6/Sybase/')

import set_sybase_env_and_run as sser 

cmd = 'select targname from target where obsid=21494'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select obsid,targid,seq_nbr,targname,ocat_propid  from target where obsid=21494'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select distinct pre_id from target where pre_id=21494'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select obsid from target  where group_id=21722'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select ao_str from prop_info where ocat_propid=5427'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select ordr from rollreq where ordr=1 and obsid=21494'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select window_constraint, tstart, tstop  from timereq  where ordr=1 and obsid=21720'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select type,trig,start,stop,followup,remarks,tooid  from too where  tooid=1765'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select targname,instrument,soe_st_sched_date,targid,seq_nbr from target where obsid=21494'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select title,piid,coi_contact,coin_id from prop_info where proposal_id=5427'
out = sser.set_sybase_env_and_run(cmd)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')
#
#---- database: axafusers
#
cmd = 'select last,email from person_short where pers_id=41615'
db  = 'axafusers'
out = sser.set_sybase_env_and_run(cmd, db=db)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')

cmd = 'select last,email from person_short where pers_id=41812'
db  = 'axafusers'
out = sser.set_sybase_env_and_run(cmd, db=db)
print(cmd)
print('Fetchall Results: ' + str(out))
print('\n\n')
