#!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

#################################################################################################
#                                                                                               #
#           extract_hrma_focus_data.py: extract data and plot hrma focus related plots          #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Oct 20, 2021                                                       #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits  as pyfits
import time
import Chandra.Time
import random
#
#--- from ska
#
from Ska.Shell import getenv, bash

ascdsenv = getenv('source /home/ascds/.ascrc -r release; source /home/mta/bin/reset_param', shell='tcsh')
#
#--- reading directory list
#
path = '/data/mta/Script/Hrma_src/Scripts/house_keeping/dir_list'

with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts
#
#--- temp writing file name
#
rtail    = int(time.time() * random.random())
zspace   = '/tmp/zspace' + str(rtail)
#
#--- filtering parameters
#
snr_lim   = 6.0
rmaj_hrc  = 500.0
rmaj_acis = 15.0
defoc_lim = 0.01
#
#--- arc5gl user name
#
arc_user = 'isobe'

#-----------------------------------------------------------------------------------------
#-- extract_hrma_focus_data: extract hrma src2 data                                     --
#-----------------------------------------------------------------------------------------

def extract_hrma_focus_data(start, stop):
    """
    extract hrma src2 data
    input:  start   --- start time in format of 01/01/18; defalut: <blank> --- automatically set the data
            stop    --- stop time in format of 01/01/18
    output: <data_dir>/hrma_src_data
    """

    [fits_a, fits_h] = extract_data(start, stop)
    
    if (len(fits_a) > 0) or (len(fits_h) > 0):

        cmd = 'rm -rf param'
        os.system(cmd)
        cmd = 'mkdir -p param'
        os.system(cmd)

        if len(fits_a) > 0:
            data = extract_src_info(fits_a, 'acis')
            print_out_data(data)

        if len(fits_h) > 0:
            data = extract_src_info(fits_h, 'hrc')
            print_out_data(data)

#-----------------------------------------------------------------------------------------
#-- print_out_data: append extracted data to <data_dir>/hrma_src_data                   --
#-----------------------------------------------------------------------------------------

def print_out_data(data):
    """
    append extracted data to <data_dir>/hrma_src_data
    input:  data    --- data 
    output: updated <data_dir>/hrma_src_data
            see read_src_file for column information
    """

    if len(data) > 0:
        outfile = data_dir + 'hrma_src_data'
        fo      = open(outfile, 'a')
        for ent in data:
            fo.write(ent)
    
        fo.close()

#-----------------------------------------------------------------------------------------
#-- extract_data: extract data to compute HRMA focus plots                              --
#-----------------------------------------------------------------------------------------

def extract_data(start, stop):
    """
    extract data to compute HRMA focus plots
    input:  start   ---- start time in the foramt of mm/dd/yy (e.g. 05/01/15)
            stio    ---- stop time in the format of mm/dd/yy
    output: acis*evt2.fits.gz, hrc*evt2.fits.gz
    """
#
#--- check whether previous fits files are still around, and if so, remove them
#
    cmd = 'ls * > ' + zspace
    os.system(cmd)
    with  open(zspace, 'r') as f:
        chk = f.read()

    mcf.rm_files(zspace)
    mc  = re.search('fits', chk)
    if mc is not None:
        cmd = 'rm *fits*'
        os.system(cmd)
#
#--- if time interval is not given, set for a month interval
#
    if start == '':
        [start, stop] = set_interval()
#
#--- extract acis and hrc evt2 files
#
    inst = 'acis'
    fits_a = create_fits_list(inst, start, stop)
    inst = 'hrc'
    fits_h = create_fits_list(inst, start, stop)


    return [fits_a, fits_h]

#-----------------------------------------------------------------------------------------
#-- set_interval: set time inteval for a month                                          --
#-----------------------------------------------------------------------------------------

def set_interval():
    """
    set time inteval for a month
    input:  none but read from <data_dir>/hrma_src_data
    output: start   --- start time in format of mm/dd/yy (e.g., 05/01/15)
            stop    --- stop time in format of mm/dd/yy
    """
#
#--- find the last entry date
#
    stday = find_last_input_date() + 86400      #--- starting date start from the next day

    ldate = Chandra.Time.DateTime(stday).date
    atemp = re.split(':', ldate)
    year  = atemp[0]
    yday  = atemp[1]

    idate = year + ':' + yday
    #start = time.strftime('%m/%d/%y', time.strptime(idate, '%Y:%j'))
    start = time.strftime('%Y-%m-%d', time.strptime(idate, '%Y:%j'))
#
#--- find today's date
#
    #stop  = time.strftime("%m/%d/%y", time.gmtime())
    stop  = time.strftime("%Y-%m-%d", time.gmtime())

    return (start, stop)

#-----------------------------------------------------------------------------------------
#-- find_last_input_date: find the last entry date                                      --
#-----------------------------------------------------------------------------------------

def find_last_input_date():
    """
    find the last entry date
    input:  none but read from <data_dir>/hrma_src_data
    output: ldate   --- the last entry time in seconds from 1998.1.1
    """

    ifile = data_dir + 'hrma_src_data'
    data  = mcf.read_data_file(ifile)
    f.close()
    t_list = []
    for ent in data:
        atemp = re.split('\s+', ent)
        t_list.append(float(atemp[3]))

    ldate = max(t_list)

    return ldate

#-----------------------------------------------------------------------------------------
#-- create_fits_list: run arc5gl and extract evt2 fits file names of "inst"             --
#-----------------------------------------------------------------------------------------

def create_fits_list(inst, start, stop):
    """
    run arc5gl and extract evt2 fits file names of "inst"
    input:  inst    --- instrument, acis or hrc
            start   --- interval start time in format of mm/dd/yy (e.g. 05/01/15)
            stop    --- interval stop time in format of mm/dd/yy
    output: fits_l  --- a list of evt2 fits files
    """
    tstart = date_foramat_change(start)
    tstop  = date_foramat_change(stop)

    operation = 'browse'
    write_arc5gl_input(tstart, tstop, inst=inst, operation=operation)

    cmd2 = ' /proj/sot/ska/bin/arc5gl -user ' + arc_user + ' -script ' + zspace + '> zout'
    os.system(cmd2)
    mcf.rm_files(zspace)

    data = mcf.read_data_file('./zout', remove=1)

    f_list = ''
    fits_l = []
    for ent in data:
        atemp = re.split('\s+', ent)
        if inst == 'acis':
            mc    = re.search('acisf',  ent)
            mc1   = re.search('acisf5', ent)
            mc2   = re.search('acisf6', ent)     
        else:
            mc    = re.search('hrcf',   ent)
            mc1   = re.search('hrcf5',  ent)
            mc2   = re.search('hrcf6',  ent)

        if mc is not None:
            if (mc1 is not None) or (mc2 is not None):
                continue
            else:
                name = atemp[0] + '.gz'
                if f_list == '':
                    f_list = atemp[0]
                    fits_l.append(name)
                else:
                    f_list = f_list + ', ' +atemp[0]
                    fits_l.append(name)

    return fits_l


#-----------------------------------------------------------------------------------------
#-- write_arc5gl_input: write input of arc5gl                                           --
#-----------------------------------------------------------------------------------------

def write_arc5gl_input(tstart, tstop, operation='retrieve', dataset='flight',\
                        inst='hrc', level=2, filetype='evt2', filename=''):
    """
    write input of arc5gl
    input:  tstart  --- start time (arc5gl acceptable format)
            tstop   --- stop time
            operation   --- operation (retrieve/browse): default: retrieve
            dataset     --- dataset; default: flight
            inst        --- instrument; default: hrc
            level       --- level; defalut: 2
            filetype    --- file type; default: evt2
            filename    --- file name; if this is given, tstart and tstop are ignored.
    output: zspace      --- arc5gl command input saved in zspace
    """
    line = 'operation=' + operation + '\n'
    line = line + 'dataset=' + dataset + '\n'
    line = line + 'detector=' + inst + '\n'
    line = line + 'level=' + str(level) + '\n'
    line = line + 'filetype=' + filetype + '\n'
    if filename != '':
        line = line + 'filename=' + filename + '\n'
    else:
        line = line + 'tstart=' + tstart + '\n'
        line = line + 'tstop=' + tstop  + '\n'
    line = line + 'go\n'
    with  open(zspace, 'w') as fo:
        fo.write(line)

#-----------------------------------------------------------------------------------------
#-- date_foramat_change: convert the data format from 05/01/16 to 2016-05-01T00:00:00   --
#-----------------------------------------------------------------------------------------

def date_foramat_change(date):
    """
    convert the data format from 05/01/16 to 2016-05-01T00:00:00
    input:  date    --- date in format of 05/01/16
    output: date    --- date in format of 2016-05-01T00:00:00
    """
    atemp = re.split('-', date)
    year  = atemp[0]
    mon   = atemp[1]
    date  = '01'
    date = year + '-' + mon + '-' + date + 'T00:00:00'

    return date

#-----------------------------------------------------------------------------------------
#-- extract_src_info: create src fits file and extract needed information               --
#-----------------------------------------------------------------------------------------

def extract_src_info(fits_list, inst):
    """
    create src fits file and extract needed information
    input:  fits_list       ---  a list of fits files
            inst            --- instrument acis or hrc
    output: results         --- the list of src data (see read_src_file)
    """
    results = []
    print("# of Files: " + str(len(fits_list)))
    for ent in fits_list:
        ###print("FILE: " + ent)
#
#--- extract evt2 file
#
        fnam = ent.replace('.gz', '')
        write_arc5gl_input(0, 0, inst=inst, filename=fnam)
        cmd2 = ' /proj/sot/ska/bin//arc5gl -user  ' + arc_user + ' -script ' + zspace + '> zout'
        try:
            os.system(cmd2)
            mcf.rm_files(zspace)
        except:
            mcf.rm_files(zspace)
            continue
#
#--- handle only none grating observations
#
        grating = 'NONE'
        try:
            grating = read_header_value(ent, 'GRATING')
        except:
            continue

        if grating == 'NONE':
#
#--- run celldetect script
#
            cmd1 = '/usr/bin/env PERL5LIB= '
            mc = re.search('acis', ent)
            if mc is not None:
                cmd2 = 'dmcopy "' + ent + '[events][bin x=::4, y=::4]" img.fits clobber=yes'
            else:
                cmd2 = 'dmcopy "' + ent + '[events][bin x=::32, y=::32]" img.fits clobber=yes'

            cmd3 = 'mkpsfmap img.fits psf.fits 0.9 ecf=0.9 clobber=yes'
            cmd4 = 'celldetect mode=h infile=img.fits outfile=cell.fits psffile=psf.fits clobber=yes'
#
#-- it seems fixed cell detection is good enough
#
            bcmd1 = cmd1 + cmd2
            bcmd2 = cmd1 + cmd3
            bcmd3 = cmd1 + cmd4
            try:
                bash(bcmd1,  env=ascdsenv)
                bash(bcmd2,  env=ascdsenv)
                bash(bcmd3,  env=ascdsenv)
            except:
                pass
        else:
            mcf.rm_files(ent)
            continue

        mcf.rm_files(ent)
#
#--- extract information needed from src2 fits file
#
        try:
            out   = read_src_file('./cell.fits')
        except:
            out   = []

        if len(out) > 0:
            results = results + out

        mcf.rm_files('./cell.fits')

    print("# of resulted lists: " + str(len(results)))
    return results

#-----------------------------------------------------------------------------------------
#-- read_src_file: read src file and create table                                       --
#-----------------------------------------------------------------------------------------

def read_src_file(ifits):
    """
    read src file and create table
    input:  ifits   --- src2 fits file name
    output: lsave   --- a list of: 
                            obsid   --- obsid
                            start   --- start time in sec from 1998.1.1
                            stop    --- stop time in sec from 1998.1.1
                            simx    --- sim x postion
                            simz    --- sim z position
                            x       --- sky x
                            y       --- sky y
                            snr     --- SNR
                            ravg    --- the average of major and minor axis
                            rnd     --- roundness: <major axis> / <minor axis>
                            rotang  --- rotation angle
                            psf     --- PSF
                            dist    --- distance from the center
                            angd    --- angle estimated from x and y
    """
#
#--- get data from header
#
    try:
        obsid = int(float(read_header_value(ifits, 'OBS_ID')))
    except:
        return []

    try:
        start = float(read_header_value(ifits, 'TSTART'))
        stop  = float(read_header_value(ifits, 'TSTOP'))
        sim_x = float(read_header_value(ifits, 'SIM_X'))
        sim_z = float(read_header_value(ifits, 'SIM_Z'))
        defoc = float(read_header_value(ifits, 'DEFOCUS'))
        roll  = float(read_header_value(ifits, 'ROLL_NOM')) * math.pi /180.0
    except:
        return []
#
#--- defocus is too large
#
    if abs(defoc) > defoc_lim:
        return []
#
#--- set parmas depending on sim z position
#
    if sim_z < -210.0:                          #--- acis i
        zoff  = -233.6 - sim_z
        xref  = 4096.5
        yref  = 4086.5
        scale = 0.492                           #--- arcsec/pix
        rmaj_lim = rmaj_acis
        inst  = 'acis_i'

    elif (sim_z >=-210.0) and(sim_z < -150.):   #--- acis s
        zoff  = -190.1 - sim_z
        xref  = 4096.5
        yref  = 4086.5
        scale = 0.492                           #--- arcsec/pix
        rmaj_lim = rmaj_acis
        inst  = 'acis_s'

    elif (sim_z >=100.0) and(sim_z < 200.0):   #--- hrc i
        zoff  = 126.99 - sim_z
        xref  = 16384.5
        yref  = 16384.5
        scale = 0.13175                         #--- arcsec/pix
        rmaj_lim = rmaj_hrc 
        inst  = 'hrc_i'

    elif sim_z >= 200.0:                        #--- hrc s 
        zoff  = 250.1 - sim_z
        xref  = 32768.5
        yref  = 32768.5
        scale = 0.13175                         #--- arcsec/pix
        rmaj_lim = rmaj_hrc 
        inst  = 'hrc_s'

    else:                                       #--- sim is not at the correct position
        return []
#
#--- get data from table
#
    x        = read_col_data(ifits, 'cell_x')
    y        = read_col_data(ifits, 'cell_y')
    snr      = read_col_data(ifits, 'snr')
    r        = list(read_col_data(ifits, 'r'))
    rotang   = read_col_data(ifits, 'rotang') * 0.01745   #--- convert to rads
    psfratio = read_col_data(ifits,'psfratio')
#
#---- separate major and minor axes
#
    rmaj     = []
    rmin     = []
    for ent in r:
        rmaj.append(float(ent[0]))
        rmin.append(float(ent[1]))
    rmaj     = numpy.array(rmaj)
    rmin     = numpy.array(rmin)
#
#--- remove zero data
#
    rindx    = (rmaj > 0) & (rmin > 0) & (psfratio > 0)

    x        = x[rindx]
    y        = y[rindx]
    snr      = snr[rindx]
    rotang   = rotang[rindx]
    psfratio = psfratio[rindx]
    rmaj     = rmaj[rindx]
    rmin     = rmin[rindx]

    ravg     = ((rmaj + rmin) / 2) * scale
    psf      = ravg / psfratio
    rnd      = rmaj / rmin
#
#--- select data satisfy the selection condition
#
    rindx  = numpy.where((snr >= snr_lim) & (rmaj < rmaj_lim))

    x      = x[rindx]
    y      = y[rindx]
    snr    = snr[rindx]
    ravg   = ravg[rindx]
    rotang = rotang[rindx]
    psf    = psf[rindx]
    rnd    = rnd[rindx]
#
#--- print out the data
#
    lsave  = []
    for j in range(0, len(x)):
#
#--- compute two more elements before printing the results
#
        dist = scale * (math.sqrt((x[j] - xref)**2 + (y[j] - yref)**2))
        try:
            angd = math.atan((y[j] - yref) / (x[j] - xref))
        except:
            angd = 0
        if angd < 0:
            angd += math.pi

        line = str(obsid) + '\t'
        line = line  + inst            + '\t'
        line = line  + str(int(start)) + '\t'
        line = line  + str(int(stop))  + '\t'
        line = line  + "%4.6f\t" % sim_x
        line = line  + "%4.6f\t" % sim_z
        line = line  + "%4.1f\t" % x[j]
        line = line  + "%4.1f\t" % y[j]

        if snr[j] < 10:
            line = line  + "%4.5f\t\t" % snr[j]
        else:
            line = line  + "%4.5f\t" % snr[j]

        if ravg[j] < 10:
            line = line  + "%4.5f\t" % ravg[j]
        else:
            line = line  + "%4.5f\t" % ravg[j]

        line = line  + "%4.5f\t" % rnd[j]
        line = line  + "%4.5f\t" % rotang[j]

        if psf[j] < 10:
            line = line  + "%4.5f\t" % psf[j]
        else:
            line = line  + "%4.5f\t" % psf[j]

        line = line  + "%4.5f\t" % dist
        line = line  + "%4.5f\n" % angd

        lsave.append(line)



    return lsave

#-----------------------------------------------------------------------------------------------
#-- read_header_value: read fits header value for a given parameter name                      --
#-----------------------------------------------------------------------------------------------

def read_header_value(fits, name):
    """
    read fits header value for a given parameter name
    input:  fits--- fits file name
    name--- parameter name
    output: val --- parameter value
    if the parameter does not exist, reuturn "NULL"
    """

    hfits = pyfits.open(fits)
    hdr   = hfits[1].header
    try:
        val   = hdr[name.lower()]
    except:
        val   = "NULL"
    
    hfits.close()
    
    return val

#-----------------------------------------------------------------------------------------------
#-- read_col_data: read data from fits file for given conlum name                             --
#-----------------------------------------------------------------------------------------------

def read_col_data(fits, name):
    """
    read data from fits file for given conlum name
    input:  fits    --- fits file name
            name    --- column name
    output: data    --- numpy array of data
    """

    hfits = pyfits.open(fits)
    hdata = hfits[1].data

    data  = hdata[name]
    hfits.close()

    return data

#-----------------------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 2:
        start = sys.argv[1].strip()
        stop  = sys.argv[2].strip()
    else:
        start = ''
        stop  = ''

    extract_hrma_focus_data(start, stop)

#    for year in range(1999, 2021):
#        for month in range(1, 13):
#            if year == 1999 and month < 10:
#                continue
#
#            if year == 2020 and month > 4:
#                exit(1)
#                break
#
#            nyear = year
#            nmonth = month + 1
#            if nmonth > 12:
#                nmonth = 1
#                nyear += 1
#
#            start = str(year)  + '-' + mcf.add_leading_zero(month)
#            stop  = str(nyear) + '-' + mcf.add_leading_zero(nmonth)
#
#            print('Period: ' + start +'<-->'+ stop)
#            extract_hrma_focus_data(start, stop)
