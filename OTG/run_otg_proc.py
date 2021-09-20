#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################################
#                                                                                           #
#       run_otg_proc.py: run otg process                                                    #
#                                                                                           #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                   #
#                                                                                           #
#               last update: Sep 16, 2021                                                   #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import time
import unittest

path = '/data/mta/Script/Dumps/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))

sys.path.append(bin_dir)
sys.path.append(mta_dir)
import mta_common_functions as mcf
#
#--- set several data lists
#
h_list   = ['4HILSA','4HRLSA','4HILSB', '4HRLSB']
l_list   = ['4LILSA','4LRLSA','4LILSBD','4LRLSBD']
l_dict   = {'H':h_list, 'L':l_list}
ph_list  = ['4HPOSARO', '4HPOSBRO']
pl_list  = ['4LPOSARO', '4LPOSBRO']
p_dict   = {'H':ph_list, 'L':pl_list}

ovc      = "OFLVCDCT"
cvc      = "CCSDSVCD"
#
#--- temp writing file name
#
rtail    = int(time.time()*random.random())
zspace   = '/tmp/zspace' + str(rtail)

#-----------------------------------------------------------------------------------------------
#-- run_otg_proc: run OTG process                                                             --
#-----------------------------------------------------------------------------------------------

def run_otg_proc():
    """   
    run OTG process
    input:  none but read from <main_dir>/PRIMARYOTG_*.tl files
    output: <arc_dir>/OTG_summary.rdb
    """
#
#--- set temp file 
#
    tmp_file = work_dir + 'gratstat.in.tl'
    fmt4     = 0
#
#--- if gratstat.in.tl already exists, append. otherwise create it.
#
    if os.path.isfile(tmp_file):
        fmt4 = 1
#
#--- open each data file and read data
#
    cmd = 'ls ' + main_dir + '*OTG*tl > ' + zspace
    os.system(cmd)
    tlist  = mcf.read_data_file(zspace, remove=1)

    if len(tlist) == 0:
        exit(1)

    for dfile in tlist:
        schk   = 0
        tdata  = mcf.read_data_file(dfile)
        header = tdata[0]
        seline = tdata[1]
        for ent in tdata[2:]:
#
#--- use only FMT4 data
#
            mc = re.search('FMT4', ent)
            if mc is not None:
                schk = 1
                atemp = re.split('FMT4', ent)
                atime = atemp[0]
                ntime = convert_time_format(atime)
                ent   = ent.replace(atime.strip(), ntime)

                if fmt4 > 0:
                    with  open(tmp_file, 'a') as fo:
                        fo.write(ent + '\n')
                else:
                    with  open(tmp_file, 'w') as fo:
                        fo.write(header + '\n')
                        fo.write(seline + '\n')
                fmt4 = 1
            else:
#
#--- move finished create a summary file
#
                if fmt4 > 0:
                    cmd = 'head -1 ' + tmp_file + '>' + tmp_file + '.tmp'
                    os.system(cmd)

                    cmd = 'tail -n +2 ' + tmp_file + ' | sort -k 29,29 -u >> ' 
                    cmd = cmd + tmp_file + '.tmp'
                    os.system(cmd)

                    cmd = 'mv -f ' + tmp_file + '.tmp ' + tmp_file 
                    os.system(cmd)

                    gratstat()
                    cmd = 'rm -f ' + tmp_file
                    os.system(cmd)
                    fmt4 = 0

    cmd = 'rm -f ' + tmp_file
    os.system(cmd)

#-----------------------------------------------------------------------------------------------
#-- convert_time_format: convert tl file time format to yyyddd.hhmmss                         --
#-----------------------------------------------------------------------------------------------

def convert_time_format(itime):
    """
    convert tl file time format to yyyddd.hhmmss
    example: 2019  10 18:38:28.5 ---> 2019010.183828
    input:  time in tl time format
    output: time in yyyyddd.hhmmss
    """
    itime = itime.strip()
    year  = itime[0]  + itime[1] + itime[2] + itime[3]
    ydate = itime[5]  + itime[6] + itime[7]
    hh    = itime[9]  + itime[10]
    mm    = itime[12] + itime[13]
    ss    = itime[15] + itime[16]

    ydate = mcf.add_leading_zero(ydate, 3)
    hh    = mcf.add_leading_zero(hh)
    mm    = mcf.add_leading_zero(mm)
    ss    = mcf.add_leading_zero(ss)

    date  = year + ydate + '.' + hh + mm + ss + '00'

    return date

#-----------------------------------------------------------------------------------------------
#-- gratstat: analyze OTG moves                                                               --
#-----------------------------------------------------------------------------------------------

def gratstat():
    """
    analyze OTG moves
    input:  <work_dir>/gratstat.in.tl
    output: <arc_dir>/OTG_summary.rdb
    """
    sline = ''.join([char*70 for char in '*'])
    eline = ''.join([char*60 for char in '='])
#
#--- define variable back-emf thresholds for long moves and nudges
#
    thresh = {'N':3.9, 'L':4.5, 'H':4.5}
    ovc    = cvc
#
#--- input file
#
    tmp_file = work_dir + 'gratstat.in.tl'

    if os.path.isfile(tmp_file):
        d_dict = read_gratsat_in(tmp_file)
    else:
        exit(1)
#
#--- initial identificaiton of moves, using back-emf
#
    st_list = []
    pst     = 'N'
    for k in range(0, len(d_dict['TIME'])):
        st = 'N'
        if (d_dict['4MP28AV'][k] >thresh[pst]) and (d_dict['4MP28BV'][k] > thresh[pst])\
            and (d_dict['4MP5AV'][k] > 4.5) and (d_dict['4MP5BV'][k] > 4.5):

            if d_dict['4HENLBX'][k] == 'ENAB':
                st = 'H'

            if d_dict['4LENLBX'][k] == 'ENAB':
                st = 'L'
        st_list.append(st)
        pst = st
#
#--- open stat summary page
#
    bline = sline + "\nProcessing /data/mta/Script/Dumps/Scripts/gratstat.in.tl\n"
#
#--- find separate move
#
    out = find_moves(d_dict, st_list)
    if out[0] == 'NA':
        print(out[1])
        exit(1)
    else:
        [st_list, m_dict, aline] = out
        bline = bline + aline
#
#--- analyze the moves
#
    rex = sorted(m_dict.keys())
    rex.append(len(st_list) + 1)
    for k in range(0, len(rex) -1):
        ibeg  = rex[k]
        iend  = rex[k+1] -1
        #iend = rex[k+1]
        otg   = m_dict[ibeg]
        oline = bline + eline + '\n'
        oline = oline +  '\n\n' + otg + 'ETG move, between records ' 
        oline = oline + str(ibeg) + ' and ' + str(iend) + '\n'

        [aline, t0] = analyze_move(otg, ibeg, iend, st_list, d_dict, ovc, cvc)

        oline = oline + aline + '\n' +  sline + '\n'

        ofile = arc_dir + 'Sub_html/' + str(t0)
        with  open(ofile, 'w') as fo:
            fo.write(oline)

#-----------------------------------------------------------------------------------------------
#--read_gratsat_in: read an ACORN tracelog file into a hash of arrays                         --
#-----------------------------------------------------------------------------------------------

def read_gratsat_in(tmp_file):
    """
    read an ACORN tracelog file into a hash of arrays
    input:  tmp_file
    output: d_dict  --- data saved in a dictionary form
    """
    data     = mcf.read_data_file(tmp_file)
#
#--- first row of the data keeps column names
#
    header   = re.split('\s+', data[0])
    clen     = len(header)
    save     = []
#
#--- create <clen> numbers of emptry lists
#
    for k in range(0, clen):
        save.append([])

    for ent in data[1:]:
        atemp = re.split('\s+', ent)
        if len(atemp) != clen:
            continue

        for k in range(0, clen):
#
#--- convert numerical value into float
#
            try:
                if k == 0:
                    save[k].append(atemp[k].strip())
                else:
                    val = float(atemp[k])
                    save[k].append(val)
            except:
                save[k].append(atemp[k].strip())
#
#--- save the data in dict form
#
    d_dict = {}
    for k in range(0, clen):
#
#--- shift the arrays of MSIDs 4HENLBX, 4HEXRBX, 4LENLBX, 4LEXRBX 
#--- by 1 element later to align with the back-emf telemetry
#
        tmsid = header[k].upper()
        if tmsid in ['4HENLBX', '4HEXRBX', '4LENLBX', '4LEXRBX']:
            val = save[k].pop()
            save[k] = [val] + save[k]

        d_dict[tmsid] = save[k]

    return d_dict

#-----------------------------------------------------------------------------------------------
#-- find_moves: find separate OTG moves                                                       --
#-----------------------------------------------------------------------------------------------

def find_moves(d_dict, st_list):
    """
    find separate OTG moves
    input:  d_dict
            st_list
    output: st_list --- updated st_list
            m_dict  --- dictionary holds movements
    """
    st_len = len(st_list)
#
#--- check any OTG moves exit
#
    chk = 0
    if 'L' in st_list:
        chk = 1
    elif 'H' in st_list:
        chk = 1
#
#--- if no move return 'NA'
#
    if chk == 0:
        return 'NA'
#
#--- there are some movements, analyze farther
#
    m0_list = []
    m1_list = []
    mg_list = []
    pst = 'N'
    k0  =  0
    for k in range(0, st_len):
        if st_list[k] == pst:
            continue

        if (pst != 'N') and (st_list[k] != 'N'):
            line = 'Bad state transition at record ' + str(k) + ': ' 
            line = line + pst + ' to ' + st_list[k] + '. Stopping!\n'
            return ['NA',line]

        if pst == 'N':
            k0 = k
        else:
            m0_list.append(k0)
            m1_list.append(k)
            mg_list.append(pst)

        pst = st_list[k]

    if len(m0_list) == 0:
        line = "No OTG moves found. Stopping!\n"
        return ['NA', line]
#
#--- revise start and stop of long moves, based on bi-level telemetry
#
    line = ''
    for k in range(0, len(m0_list)):
        ml = m1_list[k] - m0_list[k] -1
        if ml < 10:
            continue

        otg  = mg_list[k]
        otg2 = otg + 'ETG'
        ben  = '4' + otg + 'ENLBX'
        bex  = '4' + otg + 'EXRBX'
        j0   = m0_list[k] - 2
        if j0 < 0:
            j0 = 0
        j1   = m1_list[k] + 2
        if j1 > st_len:
            j1 = st_len
        nl   = 0
        line = line + '\nRevising long ' + str(otg2) + ' move between records ' + str(j0)
        line = line + ' and ' + str(j1) + '\n'

        for m in range(j0, j1):
            st_list[m] = 'N'
            if (d_dict[ben][m] == 'ENAB') and (d_dict[bex][m] == 'ENAB'):
                st_list[m] = otg
                nl += 1
            else:
                continue

        if abs(ml - nl) > 3:
            line = line + '\n>>WARNING! Large revision in move length at record  ' + str(m0[k]) + ':  '
            line = line + str(ml) + ' to ' + str(nl) + '\n'
#
#--- report revised long moves
#
    pst    = 'N'
    m_dict = {}
    k0     = 0
    for k in range(0, st_len):
        if st_list[k] == pst:
            continue

        if (pst != 'N') and (st_list[k] != 'N'):
            line = line + 'Bad state transition at record ' + str(k) + ': ' 
            line = line + str(pst) + ' to ' + str(k) + '. Stopping!\n'
            return ['NA', line]

        if pst == 'N':
            k0 = k 
        else:
            if k -k0 > 100:
                m_dict[k0] = pst
        pst = st_list[k]

    if len(m_dict) == 0:
        line = line + "No long OTG moves found. Stopping!\n"

        return ['NA', line]

    return [st_list, m_dict, line]

#-----------------------------------------------------------------------------------------------
#-- analyze_move: report data on OTG move                                                     --
#-----------------------------------------------------------------------------------------------

def analyze_move(otg, ibeg, iend, st_list, d_dict, ovc, cvc):
    """
    report data on OTG move
    inpupt: otg     --- OTG: H, L or N
            ibeg    --- beginning of ETG move
            iend    --- ending of ETG move
            st_list --- a list of postion H, L, or N
            d_dict  --- a dictonary of data; keys are msids and give a list of data
            ovc     --- either 'OFLVCDCT' or 'CCSDSVCD' if asvt data, former otherwise latter
            cvs     --- 'CCSDSVCD'
    output: <arc_dir>/OTG_summary.rdb
    """
    i0     = []
    i1     = []
    dt     = []
    emf_l  = []
    emf_s  = []
    l_list = l_dict[otg]        #--- see top area for definition
    p_list = p_dict[otg]        #--- see top area for definition
    line   = otg + 'ETG'
    arc    = [line]
    aline  = ''
#
#--- find moves
#
    pst    = 'N'
    for k in range(ibeg, iend):
        if (pst == 'N') and (st_list[k] == otg):
            i0.append(k)
        if (pst == otg) and (st_list[k] == 'N'):
            i1.append(k)
        pst = st_list[k]

    if len(i0) != len(i1):
        line = 'Oops! Found ' + str(len(i0) + 1) + ' move starts and ' 
        line = line + str(len(i1) + 1) + 'move stops.\n'
        return line

    if i0[0] < 5:
        aline = aline + '\n >>WARNING! Move starts at data record ' + str(i0[0]) + '\n'
    if (len(st_list) - i1[-1] < 5):
        aline = aline +  '\n >>WARNING! Move ends at data record ' + str(i1[-1]) + '\n'
#
#--- move times
#
    t0 = d_dict['TIME'][i0[0]]
    t1 = d_dict['TIME'][i1[-1]]
    aline = aline +  '\nMove started at ' + str(t0) + '; VCDU = ' + str(d_dict[ovc][i0[0]]) + '\n'
    aline = aline + 'Move stopped at '    + str(t1) + '; VCDU = ' + str(d_dict[ovc][i1[-1]]) + '\n'
    aline = aline +  '\n Number of movements = ' + str(len(i0)) + '\n'

    vcdu  = '%10d' % d_dict[ovc][i0[0]]
    arc.append(t0)
    arc.append(vcdu)
    vcdu  = '%10d' % d_dict[ovc][i1[-1]]
    arc.append(t1)
    arc.append(vcdu)
    nl    = 0
    tl    = 0
    ns    = 0
    aline = aline + " Move durations (seconds):" + '\n'
    for k in range(0, len(i0)):
        dv = (d_dict[cvc][i1[k]] - d_dict[cvc][i0[k]]) * 0.25625
        dt.append(dv)
        if dv > 100:
            for m in range(i0[k], i1[k]-1):
                emf_l.append(d_dict["4MP28AV"][m])
            nl += 1
            tl += dv
        if dv < 2:
            for m in range(i0[k], i1[k]-1):
                emf_s.append(d_dict["4MP28AV"][m])
            ns += 1
        aline = aline +  "%6d: %8.3f" % (k+1, dt[k]) + '\n'
#
#---  N_MOVES N_LONG  T_LONG  N_SHORT
#
    arc.append(len(i0))
    arc.append(nl)
    try:
        vchk = float(tl) / float(nl)
    except:
        vchk = 0.0
    vchk = '%3.3f' % vchk
    arc.append(vchk)
#
#--- make sure that ns matches with a definition!
#
    if ns != len(i0) -1:
        ns = len(i0) - 1

    arc.append(ns)
#
#--- Limit switch data
#
    aline = aline +  "\n Limit Switch states: " + '\n'
#
#--- pre move
#
    j = 0
    while (d_dict["4MP5AV"][i0[0] -j] > 4.5) and (d_dict["4MP5BV"][i0[0]-j] > 4.5) and (j < 5):
        j += 1
    j -= 1
    if j > 2:
        k = i0[0] -2
    elif j == 2:
        k = i0[0] -1
    elif j < 2:
        k = i0[0]

    aline = aline +  " Pre-move: (Time = " + str(d_dict["TIME"][k]) + ')' + '\n'

    for ent in l_list:
        aline = aline +  '%-7s = %s' % (ent, d_dict[ent][k]) + '\n'
        arc.append(d_dict[ent][k])
#
#--- post move
#
    j = 0
    while (d_dict["4MP5AV"][i1[-1]+j] > 4.5) and (d_dict["4MP5BV"][i1[-1]+j] > 4.5) and (j < 5):
        j += 1
    j -= 1
    if j > 2:
        k = i1[-1] +2
    elif j == 2:
        k = i1[-1] +1
    elif j < 2:
        k = i1[-1]

    aline = aline +  "Post-move: (Time = " + str(d_dict["TIME"][k]) + ')' + '\n'

    for ent in l_list:
        aline = aline + '%-7s = %s' % (ent, d_dict[ent][k]) + '\n'
        arc.append(d_dict[ent][k])
#
#--- potentiometer data
#
    aline = aline +  "\nPotentiometer Angles (degrees):\n"

    if i0[0] -2 < 0:
        k0 = 0
    else:
        k0 = i0[0] - 2

    err0  = d_dict['COERRCN'][k0]
    aline = aline +  "Pre-move: (Time = " + str(d_dict['TIME'][k0]) + ')' + '\n'

    for ent in p_list:
        aline = aline +  str(ent) + ' = ' + str(d_dict[ent][k0]) + '\n'
        arc.append(d_dict[ent][k0])

    p0_list = arc[-2:]
#
#
    if i1[-1] + 2 > len(st_list):
        k1 = len(st_list)
    else:
        k1 = i1[-1] + 2

    err1  = d_dict['COERRCN'][k1]
    aline = aline +  "Post-move: (Time = " + str(d_dict["TIME"][k1]) + '\n'

    for ent in p_list:
        aline = aline +   str(ent) + ' = ' + str(d_dict[ent][k1]) + '\n'
        arc.append(d_dict[ent][k1])
    p1_list = arc[-2:]
#
#--- move direction
#
    dirct = "UNDF"
    if(p0_list[0] > p1_list[0]) and (p0_list[1] > p1_list[1]):
        dirct = "INSR"
    elif(p0_list[0] < p1_list[0]) and (p0_list[1] < p1_list[1]):
        dirct = "RETR"

    aline = aline +  "\nMove Direction = " + str(dirct) + '\n'
    arc   = [dirct] + arc
#
#--- back-emf data
#
    aline = aline +  "\nBack-emf statistics:" + '\n'
    if len(emf_l) > 0:
        aline = aline +  "Long moves: " + '\n'
        [emf_min, emf_avg, emf_max] = emf_stats(emf_l)
        aline = aline +  "Min. back-emf (V) = " + str(emf_min) + '\n'
        aline = aline +  "Avg. back-emf (V) = " + str(emf_avg) + '\n'
        aline = aline +  "Max. back-emf (V) = " + str(emf_max) + '\n'
        arc.append(emf_min)
        arc.append(emf_avg)
        arc.append(emf_max)
    else:
        arc.append(0.0)
        arc.append(0.0)
        arc.append(0.0)
        
    if len(emf_s) > 0:
        aline = aline +  "Short moves: "  + '\n'
        [emf_min, emf_avg, emf_max] = emf_stats(emf_s)
        aline = aline +  "Min. back-emf (V) = " + str(emf_min) + '\n'
        aline = aline +  "Avg. back-emf (V) = " + str(emf_avg) + '\n'
        aline = aline +  "Max. back-emf (V) = " + str(emf_max) + '\n'
        arc.append(emf_min)
        arc.append(emf_avg)
        arc.append(emf_max)
    else:
        arc.append(0.0)
        arc.append(0.0)
        arc.append(0.0)
#
#--- OBC error count
#
    ediff = err1 - err0
    aline = aline +   "\n OBC Error Count increment = " + str(ediff) + '\n'
    arc.append(ediff)
#
#--- print summary record to archive
#
    sumfile = arc_dir + 'OTG_summary.rdb'
    hchk    = 0
    if  os.path.isfile(sumfile):
        hchk = 1

    fo      = open(sumfile, 'a')
#
#---printing the header
#
    if hchk == 0:
        hout = prep_file(l_list, p_list, sumfile)
        fo.write(hout)

    for m in range(0, 18):
        fo.write(str(arc[m]) + '\t')

    for m in range(18, 28):
        fo.write('%.2f\t' % arc[m])

    fo.write(str(arc[-1]) + '\n')

    fo.close()

    aline = aline +   "\nMove data record appended to " + sumfile + '\n'

    return [aline, t0]

#-----------------------------------------------------------------------------------------------
#-- prep_file: creating header                                                                --
#-----------------------------------------------------------------------------------------------

def prep_file(l_list, p_list, sumfile):
    """
    creating header
    input:  l_list  --- a list of msids
            p_list  --- a list of msids
            sumfile --- output file name
    output: line    --- header line
    """
    hdr1 = ['DIRN', 'GRATING', 'START_TIME', 'START_VCDU', 'STOP_TIME', 'STOP_VCDU',\
            'N_MOVES', 'N_LONG', 'T_LONG', 'N_SHORT']
    hdr2 = ['EMF_MIN_LONG', 'EMF_AVG_LONG', 'EMF_MAX_LONG', 'EMF_MIN_SHORT',\
            'EMF_AVG_SHORT', 'EMF_MAX_SHORT', 'OBC_ERRS']
    htyp = ['S', 'S', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'S', 'S', 'S', 'S', 'S',\
            'S', 'S', 'S', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']

    pre_l_list  = []
    post_l_list = []
    pre_p_list  = []
    post_p_list = []
    for ent in l_list:
        pre_l_list.append('i' + ent)
        post_l_list.append('f' + ent)

    for ent in p_list:
        pre_p_list.append('i' + ent)
        post_p_list.append('f' + ent)

    thdr = hdr1 + pre_l_list + post_l_list + pre_p_list + post_p_list + hdr2[:-1]
    line = ''
    for ent in thdr:
        line = line + ent + '\t'
    line = line + hdr2[-1] + '\n'
    for ent in htyp[:-1]:
        line = line + ent + '\t'
    line = line + htyp[-1] + '\n'
    
    print("\nRDB header records output to " + sumfile)

    return line

#-----------------------------------------------------------------------------------------------
#-- emf_stats: calculate back-emf statistics                                                  --
#-----------------------------------------------------------------------------------------------

def emf_stats(edata):
    """
    calculate back-emf statistics
    """
    if len(edata) > 0:
        try:
            out  = numpy.mean(edata)
        except:
            out  = 0.0
        avg  = float('%.2f' % out)
        emin = min(edata)
        emax = max(edata)
        return [emin, avg, emax]
    else:
        return[0, 0, 0]


#-----------------------------------------------------------------------------------------------

if __name__ == "__main__":

    run_otg_proc()
