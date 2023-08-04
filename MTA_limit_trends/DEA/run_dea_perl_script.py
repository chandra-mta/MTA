#!/proj/sot/ska3/flight/bin/python

#####################################################################################    
#                                                                                   #
#           run_dea_perl_script.py: run DEA related perl scripts                    #
#               THIS MUST BE RUN ON R2D2-V OR C3PO-V WHERE /dsops/ IS VISIBLE       #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Feb 02, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import getpass
#
#--- reading directory list
#
#path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
path = '/data/mta4/testDEA/Scripts/house_keeping/dir_list'
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
sys.path.append("/data/mta4/Script/Python3.10/MTA")

dea_dir    = bin_dir + '/DEA/'
infile     = dea_dir + 'past_dump_list'
infile2    = dea_dir + 'past_dump_list~'
ofile      = dea_dir + 'today_dump_files'
repository = dea_dir + 'RDB/'
input_dir  = '/dsops/GOT/input/'
#
#--- just in a case acistoodir is not set
#
if "ACISTOOLSDIR" not in os.environ:
    os.environ['ACISTOOLSDIR'] = dea_dir
    try:
        os.execv(sys.argv[0], sys.argv)
    except Exception:
        print('Failed re-exec:', exc)
        sys.exit(1)

#------------------------------------------------------------------------------------
#-- run_dea_perl_script: run dea extraction perl scripts                           --
#------------------------------------------------------------------------------------

def run_dea_perl_script():
    """
    run dea extraction perl scripts
    input:  none, but read from /dsops/GOT/input/. must be run on r2d2-v or c3po-v
    output: <repository>/deahk_<temp/elec>.rdb
    """
    data_list = find_new_dump()

    run_dea_perl(data_list)

#------------------------------------------------------------------------------------
#-- find_new_dump: create a list of new dump data files                            --
#------------------------------------------------------------------------------------

def find_new_dump():
    """
    create a list of new dump data files
    input:  none, but read from /dsops/GOT/input/
    output: dlist   --- a list of new data file names
    """
#
#--- read the list of the data already processed
#
    with open(infile, 'r') as f:
        plist   = [line.strip() for line in f.readlines()]
#
#--- find the last entry
#
    last_entry = plist[-1]
    
    cmd = ' mv ' +  infile + ' ' + infile2
    os.system(cmd)
#
#--- create the current data list
#
    cmd = 'ls -rt /dsops/GOT/input/*Dump_EM*.gz > ' + infile
    os.system(cmd)
    
    if os.stat(infile).st_size == 0:
        cmd = 'cp -f ' + infile2 + ' ' + infile
        os.system(cmd)
    
    with open(infile, 'r') as f:
        data    = [line.strip() for line in f.readlines()]

#
#---- find the data which are not processed yet and print out
#
    chk   = 0
    dlist = []
    line  = ''
    for ent in data:
        if chk == 0:
            if ent == last_entry:
                chk = 1
                continue
        else:
            dlist.append(ent)
    
    return dlist

#------------------------------------------------------------------------------------
#-- run_dea_perl: run perl scripts to extract data from dump data                  --
#------------------------------------------------------------------------------------

def run_dea_perl(dlist):
    """
    run perl scripts to extract data from dump data
    input:  dlist   --- a list of dump data file names
    output: <repository>/deahk_<temp/elec>.rdb
    """

    for ifile in dlist:
        atemp = re.split('\/', ifile)
        btemp = re.split('_', atemp[-1])
        year  = str(btemp[0])
#
#--- following is Peter Ford script to extract data from dump data
#
        cmd = '/bin/gzip -dc ' + ifile + ' | ' + dea_dir + 'getnrt -O  | ' + dea_dir + 'deahk.pl'
        os.system(cmd)

        cmd = dea_dir + 'out2in.pl deahk_temp.tmp deahk_temp_in.tmp ' + year
        os.system(cmd)

        cmd = dea_dir + 'out2in.pl deahk_temp.tmp deahk_elec_in.tmp ' + year
        os.system(cmd)
#
#--- 5 min resolution
#
        cmd  = dea_dir + 'average1.pl -i deahk_temp_in.tmp -o deahk_temp.rdb'
        os.system(cmd)
        cmd  = 'cat deahk_temp.rdb >> ' + repository + 'deahk_temp_week' + year + '.rdb'
        os.system(cmd)

        cmd  = dea_dir + 'average1.pl -i deahk_elec_in.tmp -o deahk_elec.rdb'
        os.system(cmd)
        cmd  = 'cat deahk_elec.rdb >> ' + repository + 'deahk_elec_week' + year + '.rdb'
        os.system(cmd)
#
#--- one hour resolution
#
        cmd  = dea_dir + 'average2.pl -i deahk_temp_in.tmp -o deahk_temp.rdb'
        os.system(cmd)
        cmd  = 'cat deahk_temp.rdb >> ' + repository + 'deahk_temp_short.rdb'
        os.system(cmd)

        cmd  = dea_dir + 'average2.pl -i deahk_elec_in.tmp -o deahk_elec.rdb'
        os.system(cmd)
        cmd  = 'cat deahk_elec.rdb >> ' + repository + 'deahk_elec_short.rdb'
        os.system(cmd)
#
#--- clean up
#
        cmd  = 'rm -rf deahk_*.tmp deahk_*.rdb '
        os.system(cmd)

#------------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

    run_dea_perl_script()
#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")