#!/proj/sot/ska3/flight/bin/python

#############################################################################################
#                                                                                           #
#       create_msid_sun_angle_file.py: create sun angle -- msid value data fits file        #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           last update: Feb 02, 2021                                                       #
#                                                                                           #
#############################################################################################

import os
import sys
import re
import string
import random
import math
import time
import numpy
import Chandra.Time
import getpass
#
#--- reading directory list
#
path = '/data/mta/Script/MTA_limit_trends/Scripts/house_keeping/dir_list'
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
sys.path.append(mta_dir)
sys.path.append(bin_dir)
#
import mta_common_functions     as mcf  #---- mta common functions
import envelope_common_function as ecf  #---- collection of functions used in envelope fitting
#
#--- set a temporary file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

sun_angle_file = data_dir +  'sun_angle.fits' 

#-----------------------------------------------------------------------------------
#-- create_msid_sun_angle_file: create sun angle - msid data fits file            --
#-----------------------------------------------------------------------------------

def create_msid_sun_angle_file(msid_list, inyear = ''):
    """
    create sun angle - msid data fits file
    input:  msid_list   --- the name of msid list which list msids and group id
            inyear      --- the year in which you want to extract the data; if "all", 1999-current year
    output: <data_dir>/<group>/<msid>_sun_angle_<year>.fits
    """
    if inyear == '':
        tyear = int(float(time.strftime('%Y', time.gmtime())))
        tday  = int(float(time.strftime('%j', time.gmtime())))
        if tday < 5:
            year_list = [tyear-1, tyear]
        else:
            year_list = [tyear]

    elif inyear == 'all':
        this_year = int(float(time.strftime("%Y", time.gmtime())))
        year_list = range(1999, this_year+1)

    else:
        year_list = [inyear]

    [s_time, s_angle] = ecf.read_fits_col(sun_angle_file, ['time', 'sun_angle'])

    ifile  = house_keeping + msid_list
    data   = mcf.read_data_file(ifile)

    for ent in data:
        atemp = re.split('\s+', ent)
        msid  = atemp[0]
        group = atemp[1]
        mc = re.search('#', msid)
        if mc is not None:
            continue

        print("msid: " + msid)

        odir = data_dir + group.capitalize() + '/' + msid.capitalize()
        if not os.path.isdir(odir):
            cmd = 'mkdir ' + odir
            os.system(cmd)

        mfile = data_dir + group.capitalize() + '/' + msid + '_data.fits'

        if not os.path.isfile(mfile):
            print("No data file found: " + str(mfile))
            continue

        try:
            [m_time, m_val, m_min, m_max] = ecf.read_fits_col(mfile, ['time', msid, 'min', 'max'])
        except:
            print("Could not read: " + str(mfile))
            continue

        for year in year_list:

            print("Year: " + str(year))

            ofits = odir + '/' + msid + '_sun_angle_' + str(year) + '.fits'
            cols  = ['sun_angle', msid, 'min', 'max']
            cdata = match_the_data(s_time, s_angle, m_time, m_val, m_min, m_max, year)

            ecf.create_fits_file(ofits, cols, cdata)

#-----------------------------------------------------------------------------------
#-- match_the_data: extract sun angle - msid value data for a given year          --
#-----------------------------------------------------------------------------------

def match_the_data(s_time, s_angle, m_time, m_val, m_min, m_max, year):
    """
    extract sun angle - msid value data for a given year
    input:  s_time  --- an array of sun angle data time
            s_angle --- an array of sun angle data
            m_time  --- an array of msid data time
            m_val   --- an array of msid data
            m_min   --- an array of msid min values
            m_max   --- an array of msid max_values
    output: angle   --- an array of sun angles
            mval    --- an array of msid values correspond to the sun angle
            mmin    --- an array of msid min values correspond to the sun angle
            mmax    --- an array of msid max values correspond to the sun angle

    """
#
#--- select out the data of the year
#
    start = str(year)   + ':001:00:00:00'
    stop  = str(year+1) + ':001:00:00:00'
    start = Chandra.Time.DateTime(start).secs
    stop  = Chandra.Time.DateTime(stop).secs

    s_time2  = s_time[(s_time  >= start) & (s_time < stop)]
    s_angle2 = s_angle[(s_time >= start) & (s_time < stop)]
    m_time2  = m_time[(m_time  >= start) & (m_time < stop)]
    m_val2   = m_val[(m_time   >= start) & (m_time < stop)]
    m_min2   = m_min[(m_time   >= start) & (m_time < stop)]
    m_max2   = m_max[(m_time   >= start) & (m_time < stop)]

    kstart = 0
    kend   = len(s_time2)-1
    angle  = []
    mval   = []
    mmin   = []
    mmax   = []
    chk    = 0

    for m in range(0, len(m_time2)):
        for k in range(kstart, kend):
            if (m_time2[m] >= s_time2[k]) and (m_time2[m] <= s_time2[k+1]):
                mval.append(m_val2[m])
                mmin.append(m_min2[m])
                mmax.append(m_max2[m])

                diff1 = abs(m_time2[m] - s_time2[k])
                diff2 = abs(m_time2[m] - s_time2[k+1])
                tot   = diff1 + diff2
                aval  = s_angle2[k] * diff2 / tot + s_angle2[k+1] * diff1 /tot
                angle.append(aval)

                kstart = k-1
                break
            else:
                if k == kend:
                    chk = 1
                    break
        if chk > 0:
            break

    angle = numpy.array(angle)
    mval  = numpy.array(mval)

    return [angle, mval, mmin, mmax]

#-----------------------------------------------------------------------------------

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

    if len(sys.argv) == 2:
        msid_list = sys.argv[1]
        create_msid_sun_angle_file(msid_list)

    elif len(sys.argv) == 3:
        msid_list = sys.argv[1]
        year      = int(float(sys.argv[2]))
        create_msid_sun_angle_file(msid_list, year)

    else:
        print("please provide <msid_list>. you can also specify the year")

#
#--- Remove lock file once process is completed
#
    os.system(f"rm /tmp/{user}/{name}.lock")
            
