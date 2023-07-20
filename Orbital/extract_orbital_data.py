#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#       extract_orbital_data.py: extract orbital data and create ascii data file        #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Jul 19, 2023                                                       #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import copy
import time
import numpy
import astropy.io.fits  as pyfits
import Chandra.Time
import random
#
#--- reading directory list
#
path = '/data/mta/Script/Orbital/Scripts/house_keeping/dir_list'
with open(path, 'r') as f:
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
#
#--- import several functions
#
import mta_common_functions     as mcf
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)
#
#--- set column names and header
#
orb_col_list  = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz']
ang_col_list  = ['time','point_x','point_y','point_z','point_suncentang','point_sunlimbang',\
                 'point_mooncentang','point_moonlimbang','point_earthcentang',\
                 'point_earthlimbang','dist_satearth','sun_earthcentang','sun_earthlimbang',\
                 'point_ramvectorang']

header = '#time   X   Y   Z   VX  VY  VZ  Point_X Point_Y Point_Z SunCentAng  SunLimbAng  MoonCentAng MoonLimbAng EarthCentAng    EarthLimbAng    Dist_SatEarth   Sun_EarthCent   Sun_EarthLimb   RamVector\n#\n'
#
#--- step of the time: set for 10 days
#
tstep = 864000.0

#-------------------------------------------------------------------------------------------------
#-- extract_orbital_data: extract orbital data and create ascii data file -- seting time span   --
#-------------------------------------------------------------------------------------------------

def extract_orbital_data(start='', stop=''):
    """
    extract orbital data and create ascii data file 
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: <data_dir>/orbit_data_<timestamp>
    """
#
#--- if it is not given, set data collection period
#
    if start == '':
        start   = find_last_entry_time()
        ttemp   = time.strftime("%Y:%j:00:00:00", time.gmtime())
        stop    = Chandra.Time.DateTime(ttemp).secs - 86400.0
#
#--- somehow orbital data cannot extract unless the period is small than 15 days; so set to 10 days
#
    ncnt  = int((stop - start) / tstep) + 3
    for k in range(0, ncnt):
        tstart = start + tstep * k
        tstop  = tstart + tstep

        tbegin = Chandra.Time.DateTime(tstart).date
        tend   = Chandra.Time.DateTime(tstop).date
        print("Time Period: "+ str(tbegin) + '<--->' + str(tend))
#
#--- call actual function which create orbital data file
#
        create_orbital_base_data_file(tstart, tstop)

#-------------------------------------------------------------------------------------------------
#-- create_orbital_base_data_file: extract orbital data and create ascii data file              --
#-------------------------------------------------------------------------------------------------

def create_orbital_base_data_file(tstart, tstop):
    """
    extract orbital data and create ascii data file 
    input:  start   --- start time in seconds from 1998.1.1
            stop    --- stop time in seconds from 1998.1.1
    output: <data_dir>/orbit_data_<timestamp>
    """

    olen   = len(orb_col_list)
    alen   = len(ang_col_list)
    elen   = alen - 1
    dlen   = olen + elen
    dsave  = []
    sline  = ''
    rdb_sv = []
#
#--- extract orbital data fits files
#
    detector = 'ephem'
    level    = '1'
    filetype = 'orbitephem1'
    e_list   = run_arc5gl(detector, level, filetype, tstart, tstop)
#
#--- for each orbital fits file, find correspoinding pointing info fits files 
#
    for fits in e_list:
        tstmp = get_file_time_stamp(fits)

        orb_data = read_fits_data(fits, orb_col_list)
        mcf.rm_files(fits)

        detector = 'ephem'
        level    = '1'
        filetype = 'angleephem'
        astart   = float(orb_data[0][0])
        astop    = float(orb_data[0][-1])
        a_list   = run_arc5gl(detector, level, filetype, astart, astop)
#
#--- read and combine the extracted pointing information fits file data
#
        save = []
        for k in range(0, alen):
            save.append([])

        for afits in a_list:
            ang_data = read_fits_data(afits, ang_col_list)

            tlen     = len(ang_data[0])
            for k in range(0, alen):
                for j in range(0, tlen):
                    save[k].append(ang_data[k][j])

            mcf.rm_files(afits)
#
#--- for a given time of orbital data, find corresponding pointing information
#
        j = 0
        for k in range(0, len(orb_data[0])):
            otime = orb_data[0][k]
            m    = find_time_match(otime, save[0], j)
#
#--- if the correspoinding entry cannot be found, skip
#
            if m == -999:
                continue

            elif m == -998:
                break
#
#--- if the correspoinding data are found, create the data line for that time
#
            else:
                line = "%d" % otime
                for n in range(1, olen):
                    line = line + "\t%3.2f" % orb_data[n][k]

                for n in range(1, alen):

                    if abs(save[n][m]) < 1.0:
                        line = line + "\t%3.5f" % save[n][m]
                    else:
                        line = line + "\t%3.2f" % save[n][m]

                rdb_sv.append(line)
                sline = sline + line + '\n'
                j = m
#
#--- check which directory the data should be saved
#
        outdir  = chk_dir(tstmp)
        outname =  outdir + '/orbit_data_' + str(tstmp)
#
#--- print out the data
#
        with open(outname, 'w') as fo:
            fo.write(header)
            fo.write(sline)
#
#--- update rdb files
#
    update_rdb_files(rdb_sv)

#-------------------------------------------------------------------------------------------------
#-- chk_dir: check which directory (year name) to save and if it does not exist, create it     ---
#-------------------------------------------------------------------------------------------------

def chk_dir(tstmp):
    """
    check which directory (year name) to save and if it does not exist, create it
    input:  tstmp   --- time stamp of the data file
    output: year    --- directory name
    """
    out    = Chandra.Time.DateTime(float(tstmp)).date
    atemp  = re.split(':', out)
    year   = atemp[0]

    outdir = data_dir + year
    if not os.path.isdir(outdir):
        cmd = 'mkdir ' + outdir
        os.system(cmd)

    return outdir

#-------------------------------------------------------------------------------------------------
#-- find_last_entry_time: check the last entry time                                             --
#-------------------------------------------------------------------------------------------------

def find_last_entry_time():
    """
    check the last entry time 
    input: none but read from <data_dir>/orbit_data_*
    output: stime   --- the last entry time in seconds from 1998.1.1
    """
    ifile = repository + 'aorbital.rdb'
    fdata = mcf.read_data_file(ifile)

    atemp = re.split('\s+', fdata[-1])
    stime = float(atemp[0]) - 10 * 86400.0
    
    return stime

#-------------------------------------------------------------------------------------------------
#-- run_arc5gl: extract data using arc5gl                                                       --
#-------------------------------------------------------------------------------------------------

def run_arc5gl(detector, level, filetype, tstart, tstop, sub=''):
    """
    extract data using arc5gl
    input:  dectctor    --- detector name
            level       --- level
            filetype    --- file type
            tstart      --- starting time
            tstop       --- stopping time
            sub         --- sub detctor name; default: ""
    output: out         --- a list of fits file names
                            also actual fits files extracted in the running directory
    """
#
#--- extract ephin hk lev 0 fits data
#
    line = 'operation=retrieve\n'
    line = line + 'dataset = flight\n'
    line = line + 'detector = ' + detector + '\n'
    
    if sub != '':
        line = line + 'subdetector = ' + sub + '\n'
    
    line = line + 'level = '+ level + '\n'
    line = line + 'filetype = ' + filetype + '\n'
    line = line + 'tstart = '   + str(tstart) + '\n'
    line = line + 'tstop = '+ str(tstop)  + '\n'
    line = line + 'go\n'
    
    out = mcf.run_arc5gl_process(line)

    return out

#-------------------------------------------------------------------------------------------------
#-- find_time_match: find which row match/closest to the given time                             --
#-------------------------------------------------------------------------------------------------

def find_time_match(otime, t_list, tstart):
    """
    find which row match/closest to the given time
    input:  otime   --- time in seconds from 1998.1.1
            t_list  --- a list of time to be compared
            tstart  --- a row # of which the search will be started
    output: k       --- the row # matched to the given time
                        if it cannot find, -999 or -998 will be returned
    """

    if otime < t_list[tstart]:
        return -999

    for k in range(tstart, len(t_list)-1):
        if otime >= t_list[k] and otime < t_list[k+1]:
            return k
        else:
            continue

    return -998

#-------------------------------------------------------------------------------------------------
#-- get_file_time_stamp: get the time stamp of the fits file                                    --
#-------------------------------------------------------------------------------------------------

def get_file_time_stamp(fits):
    """
    get the time stamp of the fits file
    input:  fits    --- fits file name
    output: tstamp  --- time stamp
    """

    atemp  = re.split('orbitf', fits)
    btemp  = re.split('N',     atemp[1])
    tstamp = btemp[0]

    return tstamp

#-------------------------------------------------------------------------------------------------
#-- read_fits_data: read fits data                                                              --
#-------------------------------------------------------------------------------------------------

def read_fits_data(fits, cols):
    """
    read fits data
    input:  fits    --- fits file name
            cols    --- a list of col names to be extracted
    output: save    --- a list of lists of data extracted
    """

    hout = pyfits.open(fits)
    data = hout[1].data
    hout.close()

    save = []
    for col in cols:
        out = data[col]
        save.append(out)

    return save

#-------------------------------------------------------------------------------------------------
#-- read_fits_header: read fits file header and return a header value                           --
#-------------------------------------------------------------------------------------------------

def read_fits_header(fits, name):
    """
    read fits file header and return a header value
    input:  fits    --- fits file name
            name    --- header value name
    output: val     --- header value
    """

    hout = pyfits.open(fits)
    val  = hout[0].header[name]
    hout.close()

    return val

#-------------------------------------------------------------------------------------------------
#-- update_rdb_files: update rdb files                                                          --
#-------------------------------------------------------------------------------------------------

def update_rdb_files(data_list):
    """
    update rdb files
    input:  a list of data
    ouptput:    <repository>/aorbital.rdb    
                <repository>/orb_angle.rdb
    """
    afile   = repository + 'aorbital.rdb'
    ofile   = repository + 'orb_angle.rdb'
    afile_b = data_dir   + 'aorbital.rdb'
    ofile_b = data_dir   + 'orb_angle.rdb'
    orbital = ''
    angle   = ''
#
#--- find the last entry time
#
    data  = mcf.read_data_file(afile)
    atemp = re.split('\s+', data[-1])
    ltime = float(atemp[0])
#
#--- go though new data
#
    try: #If data list is empty, errors, meaning no new data is pulled from arc5gl
        atemp = re.split('\s+', data_list[0])
        ptime = float(atemp[0]) - 300
    except:
        os.system(f"rm -f /tmp/mta/{name}.lock")
        exit("No new orbital data pulled")
    
    for k in range(0, len(data_list)):
        ent   = re.split('\s+', data_list[k])
        ctime = float(ent[0])
#
#--- drop the data already in the previous data file
#
        if ctime <= ltime:
            ptime = ctime
            continue
#
#--- remove wrong order or duplicated data
#
        elif ctime <= ptime:
            continue
        else:
            ptime = ctime

        orbital = orbital + ent[0]
        for k in range(1, 10):
            orbital = orbital + '\t' + ent[k]
        orbital = orbital + '\n'

        angle = angle + ent[0]
        for k in range(10, 20):
            angle = angle + '\t' + ent[k]
        angle = angle + '\n'
#
#--- make backup
#
    cmd = 'cp -f ' + afile + ' ' + afile_b
    os.system(cmd)

    cmd = 'cp -f ' + ofile + ' ' + ofile_b
    os.system(cmd)
#
#--- update the data files
#
    with open(afile, 'a') as fo:
        fo.write(orbital)

    with open(ofile, 'a') as fo:
        fo.write(angle)

#-------------------------------------------------------------------------------------------------
#-- clean_the_data: sort the data and remove the duplicate                                       -
#-------------------------------------------------------------------------------------------------

def clean_the_data(tfile):
    """
    sort the data and remove the duplicate
    input:  tfile   --- the data file name
    output: tfile   --- cleaned data file
    """

    data = red_file(tfile)

    data.sort()
    clean = data[0]
    ptime = float(data[0][0])
    for k in range(1, len(data)):
        ent = data[k]
        atemp = re.split('\t', ent)
        test = float(atemp[0])
        if test == ptime:
            continue
        else:
            ptime = test
            clean = clean + '\t' + ent

    with open(tfile, 'w') as fo:
        fo.write(clean)
            

#-------------------------------------------------------------------------------------------------

if __name__ == "__main__":
#
#--- Create a lock file and exit strategy in case of race conditions
#
    name = os.path.basename(__file__).split(".")[0]
    if os.path.isfile(f"/tmp/mta/{name}.lock"):
        sys.exit(f"Lock file exists as /tmp/mta/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
    else:
        os.system(f"mkdir -p /tmp/mta; touch /tmp/mta/{name}.lock")

    if len(sys.argv) > 3:
        start = float(sys.argv[1])
        stop  = float(sys.argv[2])
    else:
        start = ''
        stop  = ''

    extract_orbital_data(start, stop)

#
#--- Remove lock file once process is completed
#
    os.system(f"rm -f /tmp/mta/{name}.lock")