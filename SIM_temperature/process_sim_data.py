#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#       process_sim_data.py: extract TL data, read TL files, and analyze sim movements      #
#                                                                                           #
#               author: w. aaron (william.aaron@cfa.harvard.edu)                            #
#                                                                                           #
#               last update: Jul 21, 2023                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import math
import string
import random
import time
import Chandra.Time
import glob
import getpass

#
#--- from ska
#
from Ska.Shell import getenv, bash
ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param; ', shell='tcsh')
ascdsenv['IPCL_DIR'] = "/home/ascds/DS.release/config/tp_template/P011/"
ascdsenv['ACORN_GUI'] = "/home/ascds/DS.release/config/mta/acorn/scripts/"
ascdsenv['LD_LIBRARY_PATH'] = "/home/ascds/DS.release/lib:/home/ascds/DS.release/ots/lib:/soft/SYBASE_OSRV15.5/OCS-15_0/lib:/home/ascds/DS.release/otslib:/opt/X11R6/lib:/usr/lib64/alliance/lib"

#
#--- reading directory list
#
#path = '/data/mta/Script/SIM/Scripts/house_keeping/dir_list'
path = '/data/mta4/testSIM/Scripts/house_keeping/dir_list'

with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append("/data/mta4/Script/Python3.10/MTA")
#--- import several functions
#
import mta_common_functions   as mcf
#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

#
#--- Record of Processed Files
#
DUMP_EM_PROCESSED = set()
TL_PROCESSED = set()

tl_dir = exc_dir

simt   = [23336, 92905, 75620, -50505, -99612]
tscloc = ["SAFE", "ACIS-I", "ACIS-S", "HRC-I", "HRC-S"]
simf   = [-595, -505, -536, -468, -716, -991, -1048, -545, -455, -486, -418, -666, -941, -998]
faloc  = ["INIT1", "INIT2", "ACIS-I", "ACIS-S", "HRC-I", "HRC-S", "HRC-S", "INIT1+", "INIT2+",\
          "ACIS-I+", "ACIS-S+", "HRC-I+", "HRC-S+", "HRC-S+"]
#
#--- test limits
#
tsc_test     = 9
fa_test      = 9

#
#--Data Extraction Section
#

#---------------------------------------------------------------------------------------
#-- extract_tl_data: extract TL data                                                 ---
#---------------------------------------------------------------------------------------

def extract_tl_data(year, yday):
    """
    extract tl data
    input:  year    --- year of the data to be extracted
            sdate   --- stating ydate
            edate   --- ending ydate
        these three can be <blank>. if that is the case, the period starts from the
        day after the date of the last data entry to today
    output: List of unanalyzed data
            <exc_dir>/PRIMARYSIM_<#>.tl
    """
#
#--- covert date foramt to  mm/dd/yy, 00:00:00
#
    [start, stop] = start_stop_period(year, yday)
#
#--- extract trace log files. if chk == 0, no files are extracted. Recorda TL files recently extracted but unanalyzed.
#
    chk, unanalyzed_data = run_filter_script(start, stop)
    return unanalyzed_data

#---------------------------------------------------------------------------------------
#-- start_stop_period: convert year and yday to the mm/dd/yy, 00:00:00 format         --
#---------------------------------------------------------------------------------------

def start_stop_period(year, yday):
    """
    convert year and yday to the mm/dd/yy, 00:00:00 format
    input:  year    --- year
            yday    --- yday
    output: [start, stop]   --- in the format of mm/dd/yy, 00:00:00 
    """
    today = str(year) + ':' + mcf.add_leading_zero(yday, 3)
    start = today + ':00:00:00'
    stop  = today + ':23:59:59'

    return [start, stop]
            
#---------------------------------------------------------------------------------------
#-- run_filter_script: collect data and run sim script                               ---
#---------------------------------------------------------------------------------------

def run_filter_script(start, stop):
    """
    collect data and run sim script
    input:  none
    output: various *.tl files
            list of unanalyzed TL files
            return 1 if the data extracted; otherwise: 0
    """
#
#--- get Dump_EM files
#
    unprocessed_data = get_dump_em_files(start, stop)

    if len(unprocessed_data) < 1:
        return 0, []
    else:
#
#--- create .tl files from Dmup_EM files
#
        #"""
        unanalyzed_data = filters_sim(unprocessed_data)
        return 1, unanalyzed_data
        #"""
    #test without acorn processing
        """
        unanalyzed_data =[]
        return 1, unanalyzed_data
        """
#---------------------------------------------------------------------------------------
#-- filters_sim: run acorn for sim filter                                             --
#---------------------------------------------------------------------------------------

def filters_sim(unprocessed_data):
    """
    run acorn for sim filter
    input: unprocessed_data    --- list of data
    output: List of unanalyzed TL files
            various *.tl files
    """

    for ent in unprocessed_data:
        cmd1 = '/usr/bin/env PERL5LIB="" '
        cmd2 = ' /home/ascds/DS.release/bin/acorn -nOC '
        cmd2 = cmd2 + house_keeping + 'msids_sim.list -f ' + ent
        cmd  = cmd1 + cmd2
        try:
            print('Data: ' + ent)
            bash(cmd, env=ascdsenv)
        except:
            pass
#
#--- Identify which recently added *tl files need to be analyzed and store them
#
    tmp = glob.glob(tl_dir+'*.tl')
    global TL_PROCESSED
    data = list(set(tmp) - TL_PROCESSED)
    data.sort()
    TL_PROCESSED = TL_PROCESSED.union(tmp)
    return data
#---------------------------------------------------------------------------------------
#-- get_dump_em_files: extract Dump_EM files from archive                             --
#---------------------------------------------------------------------------------------

def get_dump_em_files(start, stop):
    """
    extract Dump_EM files from archive
    input:  start   --- start time in format of mm/dd/yy
            stop    --- stop time in format of mm/dd/yy
    output: *Dump_EM* data in ./EM_data directory
            data    --- return data lists
    """
#
#--- get data from archive
#
    out = run_arc5gl(start, stop)
#
#--- if data are extracted..
#
    if len(out) > 0:
#
#--- Find the list of the data extracted
#       
        mc   = re.search('sto', ' '.join(out))
    
        if mc is not None:
            cmd = 'gzip -qd ' + exc_dir + '*.sto.gz'
            os.system(cmd)
#
#--- Select only the most recently aquired data files which have yet to be processed into tl files
#

            tmp = [a[:-3] for a in out if 'log' not in a]
            global DUMP_EM_PROCESSED
            data = list(set(tmp) - DUMP_EM_PROCESSED)
            data.sort()
            DUMP_EM_PROCESSED = DUMP_EM_PROCESSED.union(tmp)
        else:
            data = []
    else:
        data = []
    
    return  data

#---------------------------------------------------------------------------------------
#-- run_arc5gl: extract data from archive using arc5gl                                --
#---------------------------------------------------------------------------------------

def run_arc5gl(start, stop):
    """
    extract data from archive using arc5gl
    input:  start   --- starting time in the format of mm/dd/yy,hh/mm/ss. hh/mm/ss is optional. mm/dd/yy, 00:00:00 format    
            stop    --- stoping time
    output: extracted data set
    """
#
#--- write arc5gl command
#
    line = 'operation=retrieve\n'
    line = line + 'dataset =flight\n'
    line = line + 'detector=telem\n'
    line = line + 'level =raw\n'
    line = line + 'tstart=' + str(start) + '\n'
    line = line + 'tstop='  + str(stop)  + '\n'
    line = line + 'go\n'
#
#--- extract data
#
    out  = mcf.run_arc5gl_process(line)

    return out

#---------------------------------------------------------------------------------------
#-- set_data_period: create a list of dates to be examined                           ---
#---------------------------------------------------------------------------------------

def set_data_period(year, sdate, edate):
    """
    create a list of dates to be examined
    input:  year    --- year of the date
            sdate   --- starting yday
            edate   --- ending ydate
        these three can be <blank>. if that is the case, it will fill from 
        the date of the last data entry to today's date
    output: dperiod --- a list of dates in the formant of [[2015, 199], [2015, 200], ...]
    """
    if year != '':
        dperiod = []
        for yday in range(sdate, edate+1):
            dperiod.append([year, yday])
    else:
#
#--- find today's date
#
        today = time.localtime()
        year  = today.tm_year
        yday  = today.tm_yday
#
#--- find the last date of the data entry
#--- entry format: 2015365.21252170    16.4531   27.0   33.0     10   174040    0    0   28.4
#
        ifile = data_dir + 'tsc_temps.txt'
        data  = mcf.read_data_file(ifile)
        lent  = data[-1]
        atemp = re.split('\s+', lent)
        btemp = re.split('\.',  atemp[0])
        ldate = btemp[0]
    
        dyear = ldate[0] + ldate[1] + ldate[2] + ldate[3]
        dyear = int(float(dyear))
        dyday = ldate[4] + ldate[5] + ldate[6]
        dyday = int(float(dyday))
#
#--- check whether it is a leap year
#
        if mcf.is_leapyear(dyear):
            base = 366
        else:
            base = 365
#
#--- now start filling the data period (a pair of [year, ydate])
#
        dperiod = []
#
#--- for the case, year change occurred
#
        if dyear < year:
    
            for ent in range(dyday, base+1):
                dperiod.append([dyear, ent])
    
            for ent in range(1, yday+1):
                dperiod.append([year, ent])
#
#--- the period in the same year
#
        else:
            for ent in range(dyday, yday+1):
                dperiod.append([year, ent])
#
#--- return the result
#
    return dperiod

#
#-- Analyze Section
#

#---------------------------------------------------------------------------------------
#-- run_tl_analysis: run sim analysis function                                       ---
#---------------------------------------------------------------------------------------

def run_tl_analysis(unanalyzed_data):
    """
    run sim analysis function
    input:none
    output: tsc_temps.txt etc (see analyze_sim_data)
    """
#
#--- check whether there are tl data
#
    if unanalyzed_data != []:
        analyze_sim_data(unanalyzed_data)

#
#--- order and removed duplicated entries from tsc_temps.txt
#
    clean_tsc_data()


#---------------------------------------------------------------------------------------
#-- analyze_sim_data: read data from TL files and analyze sim movements               --
#---------------------------------------------------------------------------------------

def analyze_sim_data(unanalyzed_data):
    """
    read data from TL files and analyze sim movements
    input:  none, but read from saved TL files
    output: <data_dir>/sim_ttabs.out
            <data_dir>/sim_summary.out
            <data_dir>/tsc_pos.out
            <data_dir>/fa_pos.out
            <data_dir>/errors.lis
            <data_dir>/plotfile.out
            <data_dir>/tsc_histogram.out
            <data_dir>/limits.txt
            <data_dir>/tsc_temps.txt
            <data_dir>/tsc_temps2.txt
    """
#
#--- read data from tl files
#
    tldat, deltsc, delfa, ntsc, nfa  = read_tl_file(unanalyzed_data)
#
#--- open the list of lists; just to make it easy to read
#
    tsec      = tldat[0]
    tdays     = tldat[1]
    dd        = tldat[2]
    tsc       = tldat[3]
    tscmove   = tldat[4]
    fa        = tldat[5]
    famove    = tldat[6]
    maxpwm    = tldat[7]
    tabaxis   = tldat[8]
    tabno     = tldat[9]
    tabpos    = tldat[10]
    motoc     = tldat[11]
    stall     = tldat[12]
    tflexa    = tldat[13]
    tflexb    = tldat[14]
    tflexc    = tldat[15]
    ttscmot   = tldat[16]
    tfamot    = tldat[17]
    tseaps    = tldat[18]
    trail     = tldat[19]
    tseabox   = tldat[20]
    trpm      = tldat[21]
    frpm      = tldat[22]
    tstate    = tldat[23]
    fstate    = tldat[24]
    tloc      = tldat[25]
    tsc_err   = tldat[26]
    floc      = tldat[27]
    fa_err    = tldat[28]
    bus_volts = tldat[29]
#
#--- initialization
#
    ttab_line    = ''
    sum_line     = ''
    tsc_line     = ''
    fa_line      = ''
    err_line     = ''
    plt_line     = ''
    th_line      = ''
    lim_line     = ''
    ttmp_line    = ''
    ttmp2_line   = ''

    lasttsc      = tsc[0]
    lastfa       = fa[0]
    lasttabaxis  = tabaxis[0]
    lasttabno    = tabno[0]
    lasttabpos   = tabpos[0]
    tscpos       = 0
    tscneg       = 0
    fapos        = 0
    faneg        = 0
    tmoves       = 0
    fmoves       = 0
    n_tt_sum     = 0
    n_fa_sum     = 0
    sumsq_tt_err = 0.0
    rms_tt_err   = 0.0
    sumsq_fa_err = 0.0
    rms_fa_err   = 0.0
    tscsum       = 0.0
    tsctot       = 0.0
    fasum        = 0.0
    fatot        = 0.0
    last_tsctot  = 0.0
    last_tscsum  = 0.0
    last_tmoves  = 0.0
    last_fatot   = 0.0
    last_fasum   = 0.0
    last_fmoves  = 0.0

    for k in range(1, len(tldat[0])):
#
#--- check errors
#
        terror = 'FALSE'
        del_sec = tsec[k] - tsec[k-1]
        if (del_sec > 33.0) or (del_sec < 32.0):
            terror   = 'TRUE'
            err_line = err_line + "%16s  TIME SKIP ERROR - %20s %12.3f %12.3f %12.1f\n" \
                                    % (dd[k], dd[k-1], tsec[k], tsec[k-1], del_sec)

        trpm[k] = (60.0/32.8) * (tsc[k] - tsc[k-1]) / 18.0

        if (terror == "FALSE") and (abs(trpm[k]) > 3200.0):
            err_line = err_line + "%16s  TSC RPM ERROR   - %10d %10d %10d\n" \
                                    % (dd[k], tsc[k], tsc[k-1], trpm[k])
            tsc[k]   = lasttsc
            trpm[k]  = 0.0

        frpm[k]  = (60.0/32.8) * (fa[k] - fa[k-1]) / 18.0

        if (terror == 'FALSE') and (abs(frpm[k]) > 1200.):
            err_line = err_line + "%16s   FA RPM ERROR   - %10d %10d\n" \
                                    % (dd[k], fa[k], frpm[k])
            fa[k]    = lastfa
            frpm[k]  = 0.0
#
#--- update tsc movment data
#
        if tsc[k-1] != tsc[k]:
            tstate[k] = 'MOVE'
            if tsc[k] > tsc[k-1]:
                tscpos  += tsc[k] - lasttsc
                tscsum  += tsc[k] - lasttsc
                tsctot  += tsc[k] - lasttsc
            else:
                tscneg  -= tsc[k] - lasttsc
                tscsum  += tsc[k] - lasttsc
                tsctot  -= tsc[k] - lasttsc
        else:
            tstate[k] = 'STOP'
#
#--- update fa movement data
#
        if fa[k-1] != fa[k]:
            fstate[k] = "MOVE"
            if fa[k] > lastfa:
                fapos += fa[k] - lastfa
                fasum += fa[k] - lastfa
                fatot += fa[k] - lastfa
            else:
                faneg -= fa[k] - lastfa
                fasum += fa[k] - lastfa
                fatot -= fa[k] - lastfa
        else:
            fstate[k] = "STOP"

        if (fstate[k-1] == 'STOP')  and(fstate[k] == 'MOVE'):
            fmoves += 1

        ptab = 0
        if tabaxis[k-1] != tabaxis[k]:
            ptab = 1
        if tabno[k-1]    != tabno[k]:
            ptab = 1
        if tabpos[k-1]   != tabpos[k]:
            ptab = 1
#
#--- TSC  moved
#
        if (tstate[k-1] == 'STOP') and (tstate[k] == 'MOVE'):
            start_tsc = tsc[k-1]
            tsc_line = tsc_line + "\n%16s %8s %6s %6s %6s %3s %7s %4s %4s %4s \
                                   %10s %10s %4s %3s %3s %6s %5s %2s %6s %6s\n" \
                                   % ("DATE", "TSCPOS", "STATE", "MFLAG", "RPM", \
                                      "PWM", " LOCN", "ERR", "   N", " RMS",\
                                      "TOTSTP", "DELSTP", "MVES", "OVC", "STL",\
                                      "TMOT", "AXIS", "NO", "TABPOS", "TRAIL")

            tsc_line = tsc_line + "%16s %8d %6s %6s %6d %3d %7s %4d %4s %4s \
                                   %10d %10d \%4d %3d %3d %6.1f\n" \
                                   % (dd[k-1], tsc[k-1], tstate[k-1], tscmove[k-1], \
                                      trpm[k-1], maxpwm[k-1], tloc[k-1], tsc_err[k-1],\
                                      "    ", "    ", last_tsctot, last_tscsum, \
                                      last_tmoves, motoc[k-1], stall[k-1], ttscmot[k-1])

            temp_tsc_start = ttscmot[k]
            max_tsc_pwm    = maxpwm[k]
            tsc_pos_start  = tsc[k-1]
            met            = tdays[k-1] - 204.5
            metyr          = met / 365.0

            ttmp2_line     = ttmp2_line + "%16s %10.4f %10.4f %6.1f\n" \
                                        % (dd[k-1], met, metyr, ttscmot[k-1])
#
#--- continue TSC move
#
        if tstate[k] == 'MOVE':
            tsc_line = tsc_line + "%16s %8d %6s %6s %6d %3d %7s %4d %4s \
                                   %4s %10d %10d %4d %3d %3d %6.1f"\
                                % (dd[k], tsc[k], tstate[k], tscmove[k], trpm[k], \
                                   maxpwm[k], tloc[k], tsc_err[k], "    ", "    ", \
                                   tsctot, tscsum, tmoves, motoc[k], stall[k], ttscmot[k])

            if (ptab > 0) and (tabaxis[k] == 'TSC'):
                tsc_line = tsc_line + "%6s %2d %6d %6.1f\n" \
                                    % (tabaxis[k], tabno[k], tabpos[k], trail[k])
            else:
                tsc_line = tsc_line + '\n'

            if motoc[k] > 0:
                lim_line = lim_line + "%16s %8d\n" % (dd[k], motoc[k])

            if maxpwm[k-1] > max_tsc_pwm:
                max_tsc_pwm = maxpwm[k]
#
#--- TSC stopped
#
        if  (tstate[k-1] == "MOVE") and (tstate[k] == "STOP"):

            if tsc_err[k] < 999:
                n_tt_sum     = n_tt_sum + 1
                sumsq_tt_err = sumsq_tt_err + tsc_err[k]**2
                rms_tt_err   = math.sqrt(sumsq_tt_err / n_tt_sum)

            stop_tsc      = tsc[k];
            tsc_move_size = stop_tsc - start_tsc
            met           = tdays[k] - 204.5
            metyr         = met / 365.0

            if maxpwm[k-1] > max_tsc_pwm:
                max_tsc_pwm = maxpwm[k]

            tsc_pos_end     = tsc[k]
            tsc_steps_moved = abs(tsc_pos_end - tsc_pos_start)


            if tsc_steps_moved > 0:
                tmoves                += 1
                tsc_line = tsc_line + "%16s %8d %6s %6s %6d \
                                        %3d %7s %4d %4d \
                                        %4.1f %10d %10d %4d %3d \
                                        %3d %6.1f\n"\
                                    % (dd[k], tsc[k], tstate[k], tscmove[k], trpm[k],\
                                       maxpwm[k], tloc[k], tsc_err[k], n_tt_sum, \
                                       rms_tt_err, tsctot, tscsum, tmoves, motoc[k],\
                                       stall[k], ttscmot[k])
                
                th_line    = th_line + "%16s %10d %10d %10d\n" \
                                   % (dd[k], start_tsc, stop_tsc, tsc_move_size)

                ttmp2_line = ttmp2_line + "%16s %10.4f %10.4f %6.1f\n" \
                                        % (dd[k], met, metyr, ttscmot[k])

                ttmp_line  = ttmp_line + "%16s %10.4f %6.1f %6.1f %6d %8d %4d %4d %6.1f\n" \
                                      % (dd[k], metyr, temp_tsc_start, ttscmot[k], max_tsc_pwm,\
                                         tsc_steps_moved, motoc[k], stall[k], bus_volts[k])

                plt_line   = plt_line + "%16s %10.4f %10.4f %10.4f %6d %10d %6d \
                                        %6.1f %6d %10d %6d %6.1f %10d %10d\n"\
                                     % (dd[k], tdays[k], met, metyr, tmoves, tsctot, n_tt_sum,\
                                        rms_tt_err, fmoves, fatot, n_fa_sum, rms_fa_err,\
                                        tsc[k], fa[k])
#
#--- FA moved
#
        if (fstate[k-1] == "STOP") and (fstate[k] == "MOVE"):
            fa_line = fa_line + '\n'
            fa_line = fa_line + "%16s %8s %6s %6s %6s %3s %7s %4s %4s %4s %10s \
                                 %10s %4s %3s %3s %6s %5s %2s %6s %6s\n"\
                              % ("DATE", "TSCPOS", "STATE", "MFLAG", "RPM", "PWM", \
                                 " LOCN", "ERR", "   N", " RMS", "TOTSTP", "DELSTP",\
                                 "MVES", "OVC", "STL", "TMOT", "AXIS", "NO", "TABPOS", "TRAIL")

            fa_line = fa_line + "%16s %8d %6s %6s %6d %3d %7s %4d %4s \
                                 %4s %10d %10d %4d %3d %3d %6.1f\n"\
                              % (dd[k-1], fa[k-1], fstate[k-1], famove[k-1], frpm[k-1], \
                                 maxpwm[k-1], floc[k-1], fa_err[k-1], "    ", "    ", \
                                 last_fatot, last_fasum, last_fmoves, motoc[k-1], \
                                 stall[k-1], tfamot[k-1])
#
#--- Continue FA move
#
        if fstate[k] == 'MOVE':
            fa_line = fa_line + "%16s %8d %6s %6s %6d %3d %7s %4d %4s \
                                 %4s %10d %10d %4d %3d %3d %6.1f"\
                              % (dd[k], fa[k], fstate[k], famove[k], frpm[k], maxpwm[k],\
                                 floc[k], fa_err[k], "    ", "    ", fatot, fasum, \
                                 fmoves, motoc[k], stall[k], tfamot[k])

            if (ptab > 0) and (tabaxis[k] == "FA" ):
                fa_line = fa_line + "%6s %2d %6d %6.1f\n"\
                                  % (tabaxis[k], tabno[k], tabpos[k], trail[k])
            else:
                fa_line = fa_line + '\n'
#
#--- FA stopped
#
        if (fstate[k-1] == "MOVE") and (fstate[k] == "STOP"):
            if fa_err[k] < 999:
                n_fa_sum     = n_fa_sum + 1
                sumsq_fa_err = sumsq_fa_err + fa_err[k]**2
                rms_fa_err   = math.sqrt(sumsq_fa_err / n_fa_sum)

            fa_line = fa_line + "%16s %8d %6s %6s %6d %3d %7s %4d %4d \
                                 %4.1f %10d %10d %4d %3d %3d %6.1f\n"\
                              % (dd[k], fa[k], fstate[k], famove[k], frpm[k], maxpwm[k], floc[k],\
                                 fa_err[k], n_fa_sum, rms_fa_err, fatot, fasum, fmoves, motoc[k],\
                                 stall[k], tfamot[k])

            met   = tdays[k] - 204.5
            metyr = met / 365.0
            plt_line = plt_line + "%16s %10.4f %10.4f %10.4f %6d %10d \
                                   %6d %6.1f %6d %10d %6d %6.1f %10d %10d\n"\
                                % (dd[k], tdays[k], met, metyr, tmoves, tsctot, n_tt_sum,\
                                   rms_tt_err, fmoves, fatot, n_fa_sum, rms_fa_err, tsc[k], fa[k])
        if ptab > 0:
            if tabaxis[k] == "TSC":
                ttab_line = ttab_line + "%16s %6s %2d %6d %6.1f\n"\
                                      % (dd[k], tabaxis[k], tabno[k], tabpos[k], trail[k])

        last_tscsum = tscsum
        last_tsctot = tsctot
        last_fasum  = fasum
        last_fatot  = fatot
        last_tmoves = tmoves
        last_fmoves = fmoves
        lasttsc     = tsc[k]
        lastfa      = fa[k]
        lasttabaxis = tabaxis[k]
        lasttabno   = tabno[k]
        lasttabpos  = tabpos[k]

        init = 1

    if ntsc < 1:
        ntsc = 1
    if nfa  < 1:
        nfa  = 1
#
#--- create summary table
#
    tscerr = deltsc / ntsc
    faerr  = delfa  / nfa

    sum_line = sum_line + "%24s %16d\n"    %  ("Total FA moves:      ",       fmoves)
    sum_line = sum_line + "%24s %16d\n"    %  ("Total TT moves:      ",       tmoves)
    sum_line = sum_line + "%24s %16d\n"    %  ("Sum of Pos TSC Steps:",       tscpos)
    sum_line = sum_line + "%24s %16d\n"    %  ("Sum of Neg TSC Steps:",       tscneg)
    sum_line = sum_line + "%24s %16d\n"    %  ("Sum of Pos  FA Steps:",       fapos)
    sum_line = sum_line + "%24s %16d\n"    %  ("Sum of Pos  FA Steps:",       faneg)
    sum_line = sum_line + "%24s  %16.2f\n" %  ("Avg Error in TSC Position: ", tscerr)
    sum_line = sum_line + "%24s  %16.2f\n" %  ("Avg Error in  FA Position: ", faerr)
#
#--- write out the results
#
    l_list = [ttab_line, sum_line, tsc_line, fa_line,   err_line, \
              plt_line,  th_line,  lim_line, ttmp_line, ttmp2_line]
    o_list = ['sim_ttabs.out', 'sim_summary.out',   'tsc_pos.out', 'fa_pos.out',    'errors.lis',\
              'plotfile.out',  'tsc_histogram.out', 'limits.txt',  'tsc_temps.txt', 'tsc_temps2.txt']
    f_list = ['w','w','w','w','w','w','w','w','a','a']

    for k in range(0, len(o_list)):
        out = data_dir + o_list[k]
        with open(out, f_list[k]) as fo:
            fo.write(l_list[k])

#---------------------------------------------------------------------------------------
#-- read_tl_file: read all tl files and create data table                             --
#---------------------------------------------------------------------------------------

def read_tl_file(file_list):
    """
    read all tl files and create data table
    input:  file_list   --- a list of tl files
                tl file columns
                    col 0   time
                    col 1   3seaid
                    col 2   3searset
                    col 3   3searomf
                    col 4   3searamf
                    col 5   3seaincm
                    col 6   3tscmove
                    col 7   3tscpos
                    col 8   3famove
                    col 9   3fapos 
                    col 10  3mrmmxmv
                    col 11  3smotoc
                    col 12  3smotstl
                    col 13  3stab2en
                    col 14  3ldrtmek
                    col 15  3ldrtno
                    col 16  3ldrtpos
                    col 17  3faflaat
                    col 18  3faflbat
                    col 19  3faflcat
                    col 20  3trmtrat
                    col 21  3famtrat
                    col 22  3fapsat
                    col 23  3ttralat
                    col 24  3faseaat
                    col 25  3smotpen
                    col 26  3smotsel
                    col 27  3prmramf
                    col 28  3spdmpa
                    col 29  3shtren
                    col 30  elbv
    output: tldat       --- a list of list of data
                    0   tsec
                    1   tdays
                    2   dd
                    3   tsc
                    4   tscmove
                    5   fa
                    6   famove
                    7   maxpwm
                    8   tabaxis
                    9   tabno
                    10  tabpos
                    11  motoc
                    12  stall
                    13  tflexa
                    14  tflexb
                    15  tflexc
                    16  ttscmot
                    17  tfamot
                    18  tseaps
                    19  trail
                    20  tseabox
                    21  trpm
                    22  frpm
                    23  tstate
                    24  fstate
                    25  tloc
                    26  tsc_err
                    27  floc
                    28  fa_err
                    29  deltsc
                    30  delfa
                    31  ntsc
                    32  nfa

    """
#
#--- initialization
#
    lsec   = 0.0
    deltsc = 0
    delfa  = 0
    ntsc   = 0
    nfa    = 0
#
#--- initialize a list to save tl data
#
    tldat = []
    for k in range(0, 30):
        tldat.append([])

    for ifile in file_list:
    #for ifile in file_list[1:2]:
#
#--- check whether the data is zipped or not, if it is unzip it
#
        mc = re.search('gz', ifile)
        if mc is not None:
            cmd = 'gzip -d ' + ifile
            os.system(cmd)
            ifile = ifile.replace('.gz','')

        data = mcf.read_data_file(ifile)
#
#--- skip none data part
#
        for ent in data[2:]:
            atemp = re.split('\t+', ent)
    
            tline = atemp[0].strip()
            if tline in ['TIME', '', 'N']:
                continue
            if len(atemp) < 30:
                continue
#
#--- convert time into chandra time, day of mission, and display time
#
            try:
                [stime, dom, atime] = convert_time_format(tline)
            except:
                continue

            sdiff = stime - lsec
#
#---  save the data every 32 seconds
#
            if sdiff > 32.0:
#
#--- skip empty data fields
#
                try:
                    tscmove   = check_value(tldat, atemp,  6, 0)
                    tsc       = check_value(tldat, atemp,  7)
                    famove    = check_value(tldat, atemp,  8, 0)
                    fa        = check_value(tldat, atemp,  9)
                    mrmmxmv   = check_value(tldat, atemp, 10)
                    ldrtmek   = check_value(tldat, atemp, 14, 0)
                    ldrtno    = check_value(tldat, atemp, 15)
                    ldrtno    = check_value(tldat, atemp, 16)
                    smotoc    = check_value(tldat, atemp, 11)
                    smotstl   = check_value(tldat, atemp, 12)
                    faflaat   = check_value(tldat, atemp, 17)
                    faflbat   = check_value(tldat, atemp, 18)
                    faflcat   = check_value(tldat, atemp, 19)
                    trmtrat   = check_value(tldat, atemp, 20)
                    famtrat   = check_value(tldat, atemp, 21)
                    fapsat    = check_value(tldat, atemp, 22)
                    ttralat   = check_value(tldat, atemp, 23)
                    faseaat   = check_value(tldat, atemp, 24)
                    bus_volts = check_value(tldat, atemp, 30)

                except:
                    continue

                lsec = stime

                tldat[0].append(stime)
                tldat[1].append(dom)
                tldat[2].append(atime)
                tldat[3].append(tsc)                    #--- 3tscpos
                tldat[4].append(tscmove)                #--- 3tscmove
                tldat[5].append(fa)                     #--- 3fapos
                tldat[6].append(famove)                 #--- 3favome
                tldat[7].append(mrmmxmv)                #--- 3mrmmxmv
                tldat[8].append(ldrtmek)                #--- 3ldrtmek
                tldat[9].append(ldrtno)                 #--- 3ldrtno 
                tldat[10].append(ldrtno)                #--- 3ldrtno 
                tldat[11].append(smotoc)                #--- 3smotoc 
                tldat[12].append(smotstl)               #--- 3smotstl
                tldat[13].append(faflaat)               #--- 3faflaat
                tldat[14].append(faflbat)               #--- 3faflbat
                tldat[15].append(faflcat)               #--- 3faflcat
                tldat[16].append(trmtrat)               #--- 3trmtrat
                tldat[17].append(famtrat)               #--- 3famtrat
                tldat[18].append(fapsat)                #--- 3fapsat 
                tldat[19].append(ttralat)               #--- 3ttralat
                tldat[20].append(faseaat)               #--- 3faseaat
                tldat[21].append(0.0)
                tldat[22].append(0.0)
                tldat[23].append("STOP")
                tldat[24].append("STOP")
    
                [tloc, floc, tsc_err, fa_err, deltsc, delfa, ntsc, nfa] \
                        = find_locs(tscmove, tsc, famove, fa, deltsc, delfa, ntsc, nfa)

                tldat[25].append(tloc)
                tldat[26].append(tsc_err)
                tldat[27].append(floc)
                tldat[28].append(fa_err)
                tldat[29].append(bus_volts)

    return tldat, deltsc, delfa, ntsc, nfa

#---------------------------------------------------------------------------------------
#-- check_value: check value and convert to an appropriate type                       --
#---------------------------------------------------------------------------------------

def check_value(tldata, adata,  pos, fv=1):
    """
    check value and convert to an appropriate type. if the value is not good use
    the last entry value
    input:  tldata  --- a list of lists of data
            adata   --- a list of the current data
            pos     --- a column position of the data to be analyzed
            fv      --- if 1, the value is float, otherwise string
    output: fval    --- the value
    """

    val = adata[pos]

    if fv == 1:
        try:
            fval = float(val)
        except:
            try:
                fval = tldata[pos][-1]
            except:
                fval = FALSE
    else:
        if val == "":
            fval = tldata[pos][-1]
        else:
            try:
                fval = val.strip()
            except:
                fval = FALSE

    return fval

#---------------------------------------------------------------------------------------
#-- find_locs: check the position of the instrument after stopped                     --
#---------------------------------------------------------------------------------------

def find_locs(tscmove, tsc, famove, fa, deltsc, delfa, ntsc, nfa):
    """
    check the position of the instrument after stopped
    input:  tscmove     --- 3tscmove
            tsc         --- 3tscpos
            famove      --- 3famove
            fa          --- 3fapos
            deltsc 
            delfa 
            ntsc 
            nfa
    output: tloc        --- label name of tsc location
            floc        --- label name of fa location
            tsc_err     --- tsc postion difference from the expected position
            fa_err      --- fa postion difference from the expected position
            deltsc 
            delfa
            ntsc 
            nfa
    """

    tloc    = '---'
    floc    = '---'
    tsc_err = 999
    fa_err  = 999

    for j in range(0, len(simt)):
        if tscmove == 'STOP':
            dtsc = abs(tsc - simt[j])
            if dtsc < tsc_test:
                tsc_err = tsc - simt[j]
                deltsc += dtsc
                ntsc   += 1
                tloc    = tscloc[j]

    for j in range(0, len(simf)):
        if famove  == 'STOP':
            dfa = abs(fa - simf[j])

            if dfa < fa_test:
                fa_err = fa - simf[j]
                delfa += dfa
                nfa   += 1
                floc   = faloc[j]

    return [tloc, floc, tsc_err, fa_err, deltsc, delfa, ntsc, nfa]

    
#---------------------------------------------------------------------------------------
#-- convert_time_format: convert time formats from that in TL files                   --
#---------------------------------------------------------------------------------------

def convert_time_format(tline):
    """
    convert time formats from that in TL files
    input:  tline   --- time in TL format
    output: stime   --- seconds from 1998.1.1
            dom     --- day of mission
            atime   --- display time <yyyy><ddd><hh><mm><ss><ss>
    """

    atemp = re.split(':', tline)
    btemp = re.split('\s+', atemp[0])
    year  = btemp[0]
    yday  = mcf.add_leading_zero(btemp[1], 3)
    hh    = mcf.add_leading_zero(btemp[2])
    mm    = mcf.add_leading_zero(atemp[1])
    ctemp = re.split('\.', atemp[2])
    ss    = mcf.add_leading_zero(ctemp[0])
    fsq   = ctemp[1] + '0'
#
#--- chandra time
#
    ltime = year + ':' + yday + ':' + hh + ':' + mm + ':' + ss + '.' + fsq
    stime = Chandra.Time.DateTime(ltime).secs
#
#--- display time
#
    atime = year + yday+ '.' + hh + mm + ss + fsq
#
#--- day of mission
#
    dom   = mcf.ydate_to_dom(year, yday)
    dom   = dom + float(hh) / 24.0 + float(mm) / 1440.0 + float(ss) / 86400.0 
    dom   = dom + float(fsq) / 8640000.0

    return [stime, dom, atime]


#---------------------------------------------------------------------------------------
#-- clean_tsc_data: order and removed duplicated entries                              --
#---------------------------------------------------------------------------------------

def clean_tsc_data():
    """
    order and removed duplicated entries
    input:  none, but read from data file tsc_temps.txt
    output: cleaned tsc_temps.txt
    """
    ifile  = data_dir + 'tsc_temps.txt'
    data   = mcf.read_data_file(ifile)
#
#--- the first line is the header
#
    header = data[0]
    body   = data[1:]
#
#--- sort the data part
#
    body = sorted(body)
#
#--- remove duplicates
#
    prev = ''
    line = header + '\n'
    for ent in body:
        if ent == prev:
            continue
        else:
            prev = ent
#
#--- only the lines with full 9 entries are put back
#
            atemp = re.split('\s+', ent)
            if len(atemp) == 9:
                line = line + ent + '\n'
#
#--- put back into the data file
#
    with open(ifile, 'w') as fo:
        fo.write(line)

#---------------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    user = getpass.getuser()
    if os.path.isfile(f"/tmp/{user}/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/{user}/{name}.lock")
    
#
#--- if you like to specify the date period, give
#---  a year and starting yday and ending yday
#
    if len(sys.argv) > 3:
        year  = int(float(sys.argv[1]))
        sdate = int(float(sys.argv[2]))
        edate = int(float(sys.argv[3]))
#
#--- if the date period is not specified,
#--- the period is set from the last entry date to
#--- today's date
#
    else:
        year  = ''
        sdate = ''
        edate = ''

#
#--- Split process into time sections for digestable processing with removal stages
#
    count = 0
    rm_len = 14 #14 days of data before deletion, making room for more intermediary files
#
#--- if the range is not given, start from the last date of the data entry
#
    tperiod = set_data_period(year, sdate, edate)
#
#--- process the data for each day
#
    for tent in tperiod:
        print(f"Processing: {tent}")
        year  = tent[0]
        yday  = tent[1]

        unanalyzed_data = extract_tl_data(year, yday)

        run_tl_analysis(unanalyzed_data)

        print(f"Count:{count}")
        if count == rm_len:
            count = 0
            print("Removing Files")
            cmd = f'rm -f {exc_dir}*Dump_EM* {exc_dir}*Merge_EM* {tl_dir}*tl'
            os.system(cmd)
            DUMP_EM_PROCESSED = set()
            TL_PROCESSED = set()
        else:
            count +=1

    print(f"Running Final Removal")
    cmd = f'rm -f {exc_dir}*Dump_EM* {exc_dir}*Merge_EM* {tl_dir}*tl'
    os.system(cmd)

#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")