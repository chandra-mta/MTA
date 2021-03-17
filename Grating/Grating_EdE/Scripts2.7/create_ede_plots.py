#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#           create_ede_plots.py: create ede plots                                               #
#                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                           #
#                                                                                               #
#           last update: Jan 02, 2019                                                           #
#                                                                                               #
#################################################################################################

import os
import sys
import re
import random
import numpy
import time
import Chandra.Time
#
#--- interactive plotting module
#
import mpld3
from mpld3 import plugins, utils

import matplotlib as mpl

if __name__ == '__main__':
    mpl.use('Agg')

sys.path.append('/data/mta/Script/Python_script2.7/')
import convertTimeFormat    as tcnv
import mta_common_functions as mcf
import robust_linear        as robust

#
#--- reading directory list
#
path = '/data/mta/Script/Grating/Grating_EdE/Scripts/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)

import convertTimeFormat    as tcnv
import mta_common_functions as mcf
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

catg_list = ['HEGp1', 'HEGm1', 'MEGp1', 'MEGm1', 'LEGpAll', 'LEGmAll']
type_list = ['hetg',  'hetg',  'metg',  'metg',  'letg',    'letg']
header    = '#year obsid   energy  fwhm denergy error   order   cnt roi_cnt acf acf_err  link'
#
#--- temp writing file name
#
rtail  = int(time.time())
zspace = '/tmp/zspace' + str(rtail)

css = """
    p{
        text-align:left;
    }
"""
#----------------------------------------------------------------------------------------------
#-- plot_ede_data: create letg, metg, and hetg ede plots                                     --
#----------------------------------------------------------------------------------------------

def plot_ede_data():
    """
    create letg, metg, and hetg ede plots
    input:  none, but read from <type><side>_all.txt'
    output: <web_dir>/Plots/<type>_<side>_<start>_<stop>.png
            <web_dir>/Plots/<type>_ede_plot.html
    """

    pfile = 'hegp1_data'
    mfile = 'hegm1_data'
    type  = 'hetg'
    create_plot(pfile, mfile, type)

    pfile = 'megp1_data'
    mfile = 'megm1_data'
    type  = 'metg'
    create_plot(pfile, mfile, type)

    pfile = 'legpall_data'
    mfile = 'legmall_data'
    type  = 'letg'
    create_plot(pfile, mfile, type)

#----------------------------------------------------------------------------------------------
#-- create_plot: creating plots for given catgories                                          --
#----------------------------------------------------------------------------------------------

def create_plot(pfile, mfile, type):
    """
    creating plots for given catgories
    input:  pfile   --- plus side data file name
            mfile   --- minus side data file name
            type    --- type of the data letg, metg, hetg
    output: <web_dir>/Plots/<type>_<side>_<start>_<stop>.png
            <web_dir>/Plots/<type>_ede_plot.html
    """

    pdata    = read_file(pfile)
    p_p_list = plot_each_year(pdata, type, 'p')

    mdata    = read_file(mfile)
    m_p_list = plot_each_year(mdata, type, 'm')

    create_html_page(type, p_p_list, m_p_list)

#----------------------------------------------------------------------------------------------
#-- plot_each_year: create plots for each year for the given categories                     ---
#----------------------------------------------------------------------------------------------

def plot_each_year(tdata, type,  side):
    """
    create plots for each year for the given categories
    input:  tdata   --- a list of lists of data (see select_data below)
            type    --- a type of grating; letg, metg, hetg
            side    --- plus or mius
    """
#
#--- find the current year and group data for 5 year interval
#
    tyear   = int(float(datetime.datetime.today().strftime("%Y")))
    nstep   = int((tyear - 1999)/5) + 1
    tarray  = numpy.array(tdata[0])
    energy  = numpy.array(tdata[2])
    denergy = numpy.array(tdata[4])

    p_list  = []
    for k in range(0, nstep):
        start = 1999 + 5 * k
        stop  = start + 5
#
#--- selecting out data
#
        selec = [(tarray > start) & (tarray < stop)]
        eng   = energy[selec]
        ede   = denergy[selec]

        outfile = str(type) + '_' + str(side) + '_' + str(start) + '_' + str(stop) + '.png'
        p_list.append(outfile)

        outfile = web_dir+ 'Plots/' + outfile
#
#--- actually plotting data
#
        plot_data(eng, ede, start, stop,  type, outfile)
        
    return p_list

#----------------------------------------------------------------------------------------------
#-- select_data: select out data which fit to the selection criteria                         --
#----------------------------------------------------------------------------------------------

def select_data(idata, type):

    """
    select out data which fit to the selection criteria
    input:  indata
                    idata[0]:   year    
                    idata[1]:   obsid   
                    idata[2]:   links   
                    idata[3]:   energy  
                    idata[4]:   fwhm    
                    idata[5]:   denergy 
                    idata[6]:   error   
                    idata[7]:   order   
                    idata[8]:   cnt     
                    idata[9]:   roi_cnt 
                    idata[10]:  acf     
                    idata[11]:  acf_err 
            type    --- type of the data; letg, metg, hetg
    output: out --- selected potion of the data
    """

    out = []
    for k in range(0, 12):
        out.append([])

    for m in range(0, len(idata[0])):

        if (idata[6][m] / idata[4][m] < 0.15):
#
#-- letg case
#
            if type == 'letg':
                for k in range(0, 12):
                    out[k].append(idata[k][m])
#
#--- metg case
#
            elif idata[4][m] * 1.0e3 / idata[3][m] < 5.0:
                if type == 'metg':
                    for k in range(0, 12):
                        out[k].append(idata[k][m])
#
#--- hetg case
#
                else:
                    if abs(idata[3][m] - 1.01) > 0.01:
                        for k in range(0, 12):
                            out[k].append(idata[k][m])

    return out


#----------------------------------------------------------------------------------------------
#-- read_file: read data file                                                                --
#----------------------------------------------------------------------------------------------

def read_file(infile):
    """
    read data file
    input:  infile  --- input file name
    output: a list of:
                    idata[0]:   year    
                    idata[1]:   obsid   
                    idata[2]:   energy  
                    idata[3]:   fwhm    
                    idata[4]:   denergy 
                    idata[5]:   error   
                    idata[6]:   order   
                    idata[7]:   cnt     
                    idata[8]:   roi_cnt 
                    idata[9]:   acf     
                    idata[10]:  acf_err 
                    idata[11]:   links   
    """
    dfile = data_dir + infile

    f    = open(dfile, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    year    = []
    obsid   = []
    energy  = []
    fwhm    = []
    denergy = []
    error   = []
    order   = []
    cnt     = []
    roi_cnt = []
    acf     = []
    acf_err = []
    links   = []
    for ent in data:
        if ent[0] == '#':
            continue

        atemp = re.split('\s+', ent)
        year.append(int(atemp[0]))
        obsid.append(atemp[1])
        energy.append(float(atemp[2]))
        fwhm.append(float(atemp[3]))

        denergy.append(float(atemp[4]))
        error.append(float(atemp[5]))

        order.append(int(atemp[6]))
        cnt.append(int(float(atemp[7])))
        roi_cnt.append(float(atemp[8]))
        acf.append(float(atemp[9]))
        acf_err.append(float(atemp[10]))
        links.append(atemp[11])
#
#--- a couple of data are useful as numpy array
#
    year    = numpy.array(year)
    energy  = numpy.array(energy) 
    denergy = numpy.array(denergy)

    #return [year, obsid, energy, fwhm, denergy, error, order, cnt, roi_cnt, acf, acf_err, links]
    return [year, obsid, energy, fwhm, denergy, error, order, cnt, roi_cnt, acf, acf_err, links]

#----------------------------------------------------------------------------------------------
#-- plot_data: plot a data in log-log form                                                   --
#----------------------------------------------------------------------------------------------

def plot_data(x, y, start, stop, type,  outfile):
    """
    plot a data in log-log form
    input:  x       --- x data
            y       --- y data
            start   --- starting year
            stop    --- stopping year
            type    --- type of the data, letg, metg, hetg
            outfile --- output png file name
    output; outfile
    """
#
#--- set plotting range
#
    if type == 'letg':
        xmin = 0.05 
        xmax = 20.0
        ymin = 0.01
        ymax = 100000
        xpos = 2
        ypos = 15000
        ypos2 = 9000
    else:
        xmin = 0.2 
        xmax = 10.0
        ymin = 1
        ymax = 100000
        xpos = 2
        ypos = 30000
        ypos2 =18000

    plt.close('all')

    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
    ax.set_xscale('log')
    ax.set_yscale('log')

    props = font_manager.FontProperties(size=24)
    mpl.rcParams['font.size']   = 24
    mpl.rcParams['font.weight'] = 'bold'
#
#--- plot data
#
    plt.plot(x, y, color='blue', marker='o', markersize=6, lw=0)
    plt.xlabel('Energy (KeV)')
    plt.ylabel('E / dE')

    text = 'Years: ' + str(start) + ' - ' + str(stop)

    plt.text(xpos, ypos, text)
#
#--- compute fitting line and plot on the scattered plot
#
    [xe, ye, a, b]  =  fit_line(x, y, xmin, xmax)
    plt.plot(xe, ye, color='red', marker='', markersize=0, lw=2)

    line = 'Slope(log-log): %2.3f' % (b)
    plt.text(xpos, ypos2, line)


    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(15.0, 10.0)

    plt.tight_layout()

    plt.savefig(outfile, format='png')

    plt.close('all')

#----------------------------------------------------------------------------------------------
#-- fit_line: fit robust fit line on the data on log-log plane                               --
#----------------------------------------------------------------------------------------------

def fit_line(x, y, xmin, xmax):
    """
    fit robust fit line on the data on log-log plane
    input:  x       --- x data
            y       --- y data
            xmin    --- min of x
            xmax    --- max of x
    """
#
#--- convert the data into log 
#
    xl = numpy.log10(x)
    yl = numpy.log10(y)
#
#--- fit a line on log-log plane with robust fit
#
    if len(xl) > 4:
        [a, b, e] = robust.robust_fit(xl, yl)
    else:
        a = 0.0
        b = 0.0
        e = 0.0
#
#--- compute plotting data points on non-log plane; it is used by the plotting routine
#
    xsave = []
    ysave = []
    step = (xmax - xmin) /100.0
    for k in range(0, 100):
        xe = xmin + step * k
        ye = 10**(a + b * math.log10(xe))
        xsave.append(xe)
        ysave.append(ye)

    return [xsave, ysave, a , b]

#----------------------------------------------------------------------------------------------
#-- create_html_page: create html page for the given type                                    --
#----------------------------------------------------------------------------------------------

def create_html_page(type, p_p_list, m_p_list):
    """
    create html page for the given type
    input:  type    --- type of data; letg, metg, hetg
            p_p_list    --- a list of plus side png plot file names
            m_p_list    --- a list of minus side png plot file names
    output: <web_dir>/<type>_ede_plot.html
    """

    if type == 'letg':
        rest = ['metg', 'hetg']
    elif type == 'metg':
        rest = ['letg', 'hetg']
    else:
        rest = ['letg', 'metg']

    hfile = house_keeping + 'plot_page_header'
    f     =  open(hfile, 'r')
    line  = f.read()
    f.close()

    line  = line + '<h2>' + type.upper() + '</h2>\n'

    line  = line + '<p style="text-align:right;">\n'
    for ent in rest:
        line = line + '<a href="' + ent + '_ede_plot.html">Open: ' + ent.upper() + '</a></br>\n'
    line  = line + '<a href="../index.html">Back to Main Page</a>'
    line  = line + '</p>\n'

    line  = line + '<table border = 0 >\n'
    line  = line + '<tr><th style="width:45%;">Minus Side</th><th style="width:45%;">Plus Side</th></tr>\n'
    for k in range(0, len(p_p_list)):

        line = line + '<tr>'
        line = line + '<th style="width:45%;">'
        line = line + '<a href="javascript:WindowOpener(\'Plots/' + m_p_list[k] +'\')">'
        line = line + '<img src="./Plots/' + m_p_list[k] + '" style="width:95%;"></a></th>\n'

        line = line + '<th style="width:45%;">'
        line = line + '<a href="javascript:WindowOpener(\'Plots/' + p_p_list[k] +'\')">'
        line = line + '<img src="./Plots/' + p_p_list[k] + '" style="width:95%;"></a></th>\n'
        line = line + '</tr>\n'

    line = line + '</table>\n'


    line = line + '</body>\n</html>\n'

    outname = web_dir +  type + '_ede_plot.html'

    fo  = open(outname, 'w')
    fo.write(line)
    fo.close()



#----------------------------------------------------------------------------------------------

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    plot_ede_data()


