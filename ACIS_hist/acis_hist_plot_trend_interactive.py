#!/usr/bin/env /data/mta/Script/Python3.9/bin/python3

#####################################################################################################
#                                                                                                   #
#   acis_hist_plot_trend_interactive.py: plot acis histgram peak, width, and count rate trends      #
#                                                                                                   #
#          mpld3 does not work with python3.6; use another version of this                          #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           last update: Feb 03, 2021                                                               #
#                                                                                                   #
#####################################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import numpy
import getopt
import os.path
import time
from scipy.optimize import curve_fit
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')
#
#--- read argv
#
try:
    option, remainder = getopt.getopt(sys.argv[1:],'t',['test'])
except getopt.GetoptError as err:
     print(str(err))
     sys.exit(2)

path = '/data/mta/Script/ACIS/Acis_hist/house_keeping/dir_list_py'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
sys.path.append(mta_dir)
sys.path.append(sp_dir)
sys.path.append(bin_dir)
#
#--- mta common functions
#
import mta_common_functions as mcf
#
#--- interactive html page
#
import mpld3
from mpld3 import plugins, utils
#
#--  peak position y direction plotting range (x2 of pdelta)
#
pdelta = 70
#
#--  peak width y direction plotting range (x2 of wdelta)
#
wdelta = 70
#
#--- count rate y direction plotting range
#
count_ymin = 1.0e-4   
count_ymax = 0.07
#
#--- each frame takes 3.241 sec
#
sec_per_frame = 3.2412

#----------------------------------------------------------------------------------------
#-- acis_hist_plot_trend: main function to plot trend of acis histgram data and create a html page
#----------------------------------------------------------------------------------------

def acis_hist_plot_trend():
    """
    main function to plot trend of acis histgram data and create interactive html page
    input: none, this will read data from data_dir
    output: interactive web pages in <web_dir>/Html_pages/
    """
#
#--- go through given ccds, nodes, and data collection regions
#
    for ccd in (1, 2, 3, 6, 7):
        for dtype in ('pos', 'cnt', 'width'):
            for loc in ('low', 'high'):
#
#--- read data
#
                node0_data = readdata(ccd, 0, loc)
                if node0_data == False:
                    continue

                node1_data = readdata(ccd, 1, loc)
                if node1_data == False:
                    continue

                node2_data = readdata(ccd, 2, loc)
                if node2_data == False:
                    continue

                node3_data = readdata(ccd, 3, loc)
                if node3_data == False:
                    continue
#
#--- create the interactive web pages
#
                plot_interactive_trend(node0_data, node1_data, node2_data, node3_data, ccd, loc, dtype)
#
#--- udate the main web page
#
    update_web_page()

#----------------------------------------------------------------------------------------
#--- readdata: read trend data from database                                          ---
#----------------------------------------------------------------------------------------

def readdata(ccd, node, loc):
    """
    read trend data from database
    input:  ccd     --- ccd #
            node    --- node #
            loc     --- low or high
    output: a list of lists: [time, pos1, cnt1, width1, pos2, cnt2, width2, pos3, cnt3, width3]
    """
#
#--- initialize lists
#
    time   = []
    pos1   = []
    cnt1   = []
    width1 = []
    pos2   = []
    cnt2   = []
    width2 = []
    pos3   = []
    cnt3   = []
    width3 = []
    perr1  = []
    cerr1  = []
    werr1  = []
    perr2  = []
    cerr2  = []
    werr2  = []
    perr3  = []
    cerr3  = []
    werr3  = []
    interv = []
    y_list = []
    m_list = []
#
#-- check whether the data file exists... not all CCDs have the histgram data
#
    ifile = data_dir + 'ccd' + str(ccd) + '_node' + str(node) + '_' + loc

    if not os.path.isfile(ifile):
        return False

    data  = mcf.read_data_file(ifile)

    for ent in data:
        atemp     = re.split('\s+|t+', ent)
        btemp     = re.split(':', atemp[0])
#
#--- adding 15 day to set position at mid month
#
        ytime     = float(btemp[0]) + (float(btemp[1])+0.5) / 12.0    
        duration  = float(atemp[20])

        interv.append(duration)
        chk = 0
        for k in range(2, 20):
            if k in (6, 12, 18):
                atemp[k] = float(atemp[k]) * 2.354      #--- changing sigma to FWHM
            else:
                atemp[k] = float(atemp[k])

            if (atemp[k] <= 0) or (atemp[k] >1.0e5):
                chk = 1
                break
        
        if chk == 1:
            continue

        time.append(ytime)

        y_list.append(btemp[0])
        m_list.append(btemp[1])

        pos1.append(atemp[2])
        perr1.append(atemp[3])
        cnt1.append(log10(atemp[4] / duration))
        cerr1.append(atemp[5] / duration)
        width1.append(atemp[6])
        werr1.append(atemp[7])

        pos2.append(atemp[8])
        perr2.append(atemp[9])
        cnt2.append(log10(atemp[10] / duration))
        cerr2.append(atemp[11] / duration)
        width2.append(atemp[12])
        werr2.append(atemp[13])

        pos3.append(atemp[14])
        perr3.append(atemp[15])
        cnt3.append(log10(atemp[16] / duration))
        cerr3.append(atemp[17] / duration)
        width3.append(atemp[18])
        werr3.append(atemp[19])

    out1 = [time, pos1, cnt1, width1, pos2, cnt2, width2, pos3, cnt3, width3]
    out2 = [perr1, cerr1, werr1, perr2, cerr2, werr2, perr3, cerr3, werr3, y_list, m_list, interv]
    out  = out1 + out2
    return out
        
#---------------------------------------------------------------------------------------------
#-- save_results: print out line fitted result in a file                                   ---
#---------------------------------------------------------------------------------------------

def save_results(ccd, loc, dtype, int_list, slp_list):
    """
    print out line fitted result in a file
    input:  ccd         --- ccd #
            loc         --- location; low, high
            dtype       --- data type: pos, cnt, width
            int_list    --- a list of lists of parameter 1 [[node0-al, node0-ti, node0-mn], [node1al..}..]
            slp_list    --- a list of lists of parameter 2 [[node0-al, node0-ti, node0-mn], [node1al..}..]
    output: a file      --- ccd<ccd#>_<dtype>_<loc>_fitting_results
    """
#
#--- set which one to print out
#
    if dtype == 'cnt':
        dline    = ': Log Count Rate '
        equation = 'y = const1 * exp*(-1 * const2 * (Time - 2000) (Time in year))\n'

    elif dtype == 'width':
        dline    = ': Peak Width  '
        equation = 'y = const1  +  const2 * (Time - 2000) (Time in year))\n'

    else:
        dline    = ': Peak Position  '
        equation = 'y = const1  +  const2 * (Time - 2000) (Time in year))\n'
#
#--- open the output file and start printing 
#
    ofile = web_dir + 'Fittings/ccd' + str(ccd) + '_' +  dtype + '_' + loc + '_fitting_results'
    with open(ofile , 'w') as fout:

        fout.write('\n')
    
        line = 'CCD' + str(ccd) + dline + 'Al K-alpha (set Year 2000 to 0)\n'
        fout.write(line)
        fout.write('#\n')
        fout.write(equation)
        fout.write('#\n')
        fout.write('node    rows            element     const1   const2\n')
        fout.write('#---------------------------------------------------------------------\n')
     
        print_out_fit_result(fout, loc, 'al', 0, int_list[0][0], slp_list[0][0])
        print_out_fit_result(fout, loc, 'al', 1, int_list[1][0], slp_list[1][0])
        print_out_fit_result(fout, loc, 'al', 2, int_list[2][0], slp_list[2][0])
        print_out_fit_result(fout, loc, 'al', 3, int_list[3][0], slp_list[3][0])
    
        fout.write('\n\n')
    
        line = 'CCD' + str(ccd) + dline +  'Ti K-alpha (set Year 2000 to 0)  \n'
        fout.write(line)
        fout.write('#\n')
        fout.write(equation)
        fout.write('#\n')
        fout.write('node    rows            element     const1   const2\n')
        fout.write('#---------------------------------------------------------------------\n')
     
        print_out_fit_result(fout, loc, 'ti', 0, int_list[0][1], slp_list[0][1])
        print_out_fit_result(fout, loc, 'ti', 1, int_list[1][1], slp_list[1][1])
        print_out_fit_result(fout, loc, 'ti', 2, int_list[2][1], slp_list[2][1])
        print_out_fit_result(fout, loc, 'ti', 3, int_list[3][1], slp_list[3][1])
    
        fout.write('\n\n')
    
        line = 'CCD' + str(ccd) + dline + 'Mn K-alpha (set Year 2000 to 0)  \n'
        fout.write(line)
        fout.write('#\n')
        fout.write(equation)
        fout.write('#\n')
        fout.write('node    rows            element     const1   const2\n')
        fout.write('#---------------------------------------------------------------------\n')
     
        print_out_fit_result(fout, loc, 'mn', 0, int_list[0][2], slp_list[0][2])
        print_out_fit_result(fout, loc, 'mn', 1, int_list[1][2], slp_list[1][2])
        print_out_fit_result(fout, loc, 'mn', 2, int_list[2][2], slp_list[2][2])
        print_out_fit_result(fout, loc, 'mn', 3, int_list[3][2], slp_list[3][2])
    
        fout.write('\n\n')

#--------------------------------------------------------------------------------------------
#-- print_out_fit_result: create an output line for the result                            ---
#--------------------------------------------------------------------------------------------

def print_out_fit_result(fout, loc, elm, node, a1, a2):
    """
    create an output line for the result
    input:  fout    --- print out device
            loc     --- location of data colletion; low, hight
            elm     --- elements: al, ti, mn
            node    --- node #
            al      --- parameter 1
            a2      --- parameter 2
    ouput:  printint out the result
    """

    if loc == 'low':
        lpos = '21- 221'
    else:
        lpos = '801 - 1001'

    b1 = '%.4f' % float(a1)
    b2 = '%.4f' % float(a2)
    line = str(node) + '\t\t' + lpos + '\t\t\t' + elm + '\t\t' + str(b1) + '\t' + str(b2) + '\n'
    fout.write(line)

#--------------------------------------------------------------------------------------------
#----fit_line: ftting line with a given function                                          ---
#--------------------------------------------------------------------------------------------
    
def fit_line(paramsinit, x, y, err, ftype):
    """
    ftting line with a given function
    input: paramsinit   --- initial guess for the parameters
           x            --- a list of x data
           y            --- a list of y data
           err          --- a list of y error --- not used
           type         --- linear or exp:
    output: two parameters (a, b) are returned
    """
    sx   = []
    sy   = []
    se   = []
    avg  = mean(y)
    stdp = std(y)
    bot  = avg - 3.0 * stdp
    top  = avg + 3.0 * stdp
    i    = 0
    for val in y:
        if (val >= bot) and (val <= top):
            sx.append(x[i])
            sy.append(y[i])
            se.append(err[i])
        i += 1
#
#--- make sure that the arrays are numpyed
#
    d = numpy.array(sx)
    v = numpy.array(sy)
    e = numpy.array(se)
#
#--- linear fit
#
    if ftype == 'linear':
        try:
            popt, pcov = curve_fit(linear_fit, d, v, p0=paramsinit)
            [a, b] = list(popt)
        except:
            [a, b] = paramsinit
#
#--- exp fit
#
    else:
        try:
            popt, pcov = curve_fit(exp_fit, d, v, p0=paramsinit)
            [a, b] = list(popt)
        except:
            [a, b] = paramsinit

    return [a, b]

#--------------------------------------------------------------------------------------------
#---linear_fit: linear model fit                                                          ---
#--------------------------------------------------------------------------------------------

def linear_fit(x, a, b):
    """
    linear model fit
    input: param: (a,b)
    x     independent val
    ouptput: estimate
    """
    return (a + b * x)

#--------------------------------------------------------------------------------------------
#-- exp_fit: exponential model                                                            ---
#--------------------------------------------------------------------------------------------

def exp_fit(x, a, b):
    """
    exponential model
    input: param (a, b)
           x      independent variable
    output: estimate
    """
    return  (a * exp(-1.0 * b * x))

#--------------------------------------------------------------------------------------------
#-- update_web_page: update "update date" on the main page                                 --
#--------------------------------------------------------------------------------------------

def update_web_page():
    """
    update "update date" on the main page
    input: none but read <house_keeping>/acis_hist_main.html
    output: <web_page>/acis_hist_main.html
    """
    path  = house_keeping + 'acis_hist_main.html'
    data  = open(path, 'r').read()

    ldate = time.ctime()
    data  = data.replace("#DATE#", ldate)
    
    out   = web_dir + 'acis_hist_main.html'
    with open(out, 'w') as fout:
        fout.write(data)

#--------------------------------------------------------------------------------------------
#-- plot_interactive_trend: create an interactive web page                                ---
#--------------------------------------------------------------------------------------------

def plot_interactive_trend(node_0_data, node_1_data, node_2_data, node_3_data, ccd, loc, dtype):
    """
    create an interactive web page
    input:  node_0_data     --- data set for node 0 of a given ccd, loc, and dtype
            node_1_data     --- data set for node 1 of a given ccd, loc, and dtype
            node_2_data     --- data set for node 2 of a given ccd, loc, and dtype
            node_3_data     --- data set for node 3 of a given ccd, loc, and dtype
            ccd             --- ccd #
            loc             --- location of the data collection either "low" or "high"
            dtype           --- data type, cnt, width, or pos
    outout: interactive html page:      acis_hist_ccd<ccd#>_<loc>_<dtype>.html  
                                        (e.g., acis_hist_cccd1_low_cnt.html)
            line fitted result page:    ccd<ccd#>_<dtype>_<loc>_fitting_results 
                                        (e.g., ccd1_cnt_low_fitting_results)
    """
#
#--- set several values used in the plots
#
    color_table  = ['red', 'blue', 'green', 'lime']
    marker_table = ['s',   '*',    '^',     'o']
    marker_size  = [50,    80,     70,      50]
#
#--- this css is used for the pop up page
#
    css = """
        body{
            width:600px;
            height:300px;
        }
        p{
            text-align:center;
        }
    """
#
#--- open the data packs
#
    [n0_time, n0_pos3, n0_cnt3, n0_width3, n0_pos1, n0_cnt1, n0_width1, n0_pos2, n0_cnt2, n0_width2] = node_0_data[:10]
    [n1_time, n1_pos3, n1_cnt3, n1_width3, n1_pos1, n1_cnt1, n1_width1, n1_pos2, n1_cnt2, n1_width2] = node_1_data[:10]
    [n2_time, n2_pos3, n2_cnt3, n2_width3, n2_pos1, n2_cnt1, n2_width1, n2_pos2, n2_cnt2, n2_width2] = node_2_data[:10]
    [n3_time, n3_pos3, n3_cnt3, n3_width3, n3_pos1, n3_cnt1, n3_width1, n3_pos2, n3_cnt2, n3_width2] = node_3_data[:10]

    [y_list0, m_list0, duration0] =  node_0_data[-3:]
    [y_list1, m_list1, duration1] =  node_1_data[-3:]
    [y_list2, m_list2, duration2] =  node_2_data[-3:]
    [y_list3, m_list3, duration3] =  node_3_data[-3:]

    xmin     = 2000
    xmax     = int(max(n0_time)) + 1
    xdiff    = xmax - xmin
    xtext    = xmin + 0.05 * xdiff
#
#--- set plotting page
#
    plt.close('all')

    fig, ax = plt.subplots(3, figsize=(8,6), sharex='col')

    mpl.rcParams['font.size'] = 12
    props = font_manager.FontProperties(size=12)
    plt.subplots_adjust(hspace=0.08)
#
#---- trending plots
#
    int_list  = []
    slp_list  = []
    t_list0   = []
    t_list1   = []
    t_list2   = []
    for node in range(0, 4):
        a_list = []
        b_list = []

        xtime  = eval('n%s_time' %(str(node)))
        y_list = eval('y_list%s' %(str(node)))
        m_list = eval('m_list%s' %(str(node)))

        for k in range(0, 3):
            ydata = eval('n%s_%s%s' % (str(node), dtype, str(k+1)))
            if k == 0:
                t_list0 = t_list0 + ydata
            elif k == 1:
                t_list1 = t_list1 + ydata
            elif k == 2:
                t_list2 = t_list2 + ydata

            nlabel = 'node' + str(node)
#
#--- the main plots are created here
#
            points = ax[k].scatter(xtime, ydata, color=color_table[node], marker=marker_table[node], s=marker_size[node] ,lw=0)
#
#--- pop up plots are created here
#
            labels = create_label_html(ccd, node, loc, y_list, m_list)
#
#--- link the two pages
#
            plugins.connect(fig, mpld3.plugins.PointHTMLTooltip(points, labels, css=css, hoffset=-140)) 
#
#--- prepare for line fittings then fit a linear line
#
            shifted = []
            for m in range(0, len(xtime)):
                shifted.append(xtime[m] - 2000)

            paramsinitial = set_initial_guess(dtype, k)
            ferr   = [0] * len(xtime)

            (a, b) = fit_line(paramsinitial, shifted, ydata, ferr, 'linear')

            start  = a + b * ((xmin-2000) - 0.5) 
            stop   = a + b * ((xmax-2000) + 0.5) 
            ax[k].plot([xmin, xmax], [start, stop],  color=color_table[node], marker=marker_table[node], lw=2, label=nlabel)

            a_list.append(a)
            b_list.append(b)

        int_list.append(a_list)
        slp_list.append(b_list)
#
#--- setting plotting range using all data and with fitted lines
#
    [ymin_list, ymax_list, ylab] = set_plot_range(xmin, xmax, int_list, slp_list, t_list0, t_list1, t_list2, dtype, loc)
#
#--- printing out fitted results
#
    save_results(ccd, loc, dtype, int_list, slp_list)
#
#--- set plotting frames
#
    ymin  = ymin_list[0]
    ymax  = ymax_list[0]
    ax[0].set_xlim(xmin, xmax)
    ax[0].set_ylim(ymin, ymax)
    ax[0].text(xtext, y_text(ymin, ymax), 'Al K-alpha',fontsize=16)

    ymin  = ymin_list[1]
    ymax  = ymax_list[1]
    ax[1].set_xlim(xmin, xmax)
    ax[1].set_ylim(ymin, ymax)
    ax[1].text(xtext, y_text(ymin, ymax), 'Ti K-alpha', fontsize=16)

    ymin  = ymin_list[2]
    ymax  = ymax_list[2]
    ax[2].set_xlim(xmin, xmax)
    ax[2].set_ylim(ymin, ymax)
    ax[2].text(xtext, y_text(ymin, ymax), 'Mn K-alpha', fontsize=16)
#
#
    ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.00), ncol=4, fancybox=True, shadow=True)
#
#--- shift y label so that it is easily seen
#
    ax[1].set_ylabel(ylab)
    ax[1].yaxis.set_label_coords(-0.10, 0.5)
#
#---- set x tick labels
#
    xt_list = []
    xn_list = []
    for val in range(xmin, xmax+1, 2):
        val = int(val)
        xt_list.append(val)
        val = '%s' % (val)
        xn_list.append(str(val))

    for az in ax.flatten():
        az.set_xticks(xt_list, xn_list)
        az.set_xticklabels(xn_list)
#
#--- add x label on the bottom panel
#
    ax[2].set_xlabel('Time (year)')
#
#--- set the size of plot
#
    fig.set_size_inches(10.0, 15.0)
    fig.tight_layout()

    plt.close('all')
#
#
#------------  start making the web page ---------------------------------
#

#
#--- read javascript file
#
    jfile   = house_keeping + 'java_script_deposit'
    f       = open(jfile, 'r')
    jscript = f.read()
    f.close()
#
#--- set title description
#
    if dtype == 'cnt':
        description = 'Normalized Count Rates '
    elif dtype == 'width':
        description = 'Peak Width '
    else:
        description = 'Peak Position '
    if loc == 'low':
        description = description + '<br /> Rows: 21 - 221'
    else:
        description = description + '<br /> Rows: 801 - 1001'
#
#--- the file name which keeps  the fitted results
#
    file_name = 'ccd' + str(ccd) + '_' +  dtype + '_' + loc + '_fitting_results'
#
#--- start creating html page
#
    out = '<!DOCTYPE html>\n<html>\n<head>\n\t<title>ACIS Histogram Plots</title>\n'
    out = out + jscript + '\n'
    out = out + '</head>\n<body style="width:95%;margin-left:10px; margin-right;10px;background-color:#FFEBCD">\n\n'
    out = out + '<a href="https://cxc.cfa.harvard.edu/mta_days/mta_acis_hist/acis_hist_main.html" '
    out = out + 'style="float:right;padding-right:50px;font-size:120%"><b>Back to Top</b></a>'
    out = out + '<h2>CCD ' + str(ccd) + ' ' + description 
    out = out + ' (<a href="javascript:WindowOpener(\'' + file_name + '\')" style="text-align:right">Fitted Results </a>)'
    out = out + '</h2>\n\n'
    out = out + '<p style="text-align:left; ">'
    out = out + 'If you move the mouse to one of the data point, the distribution plot will pop up. '
    out = out + 'If you like to magnify the plot, click the <b>magnifier icon</b> at the bottom of the plot'
    out = out + ' or  the <b>cross icon</b> to move the plot location around. You can go back to the full view by clicking '
    out = out + ' the <b>house icon</b>.</p>'
#
#--- convert mat plot  figure to html page format
#
    out = out + mpld3.fig_to_html(fig)
    out = out.replace('None', '')           #--- fixing a bug to remove un-wanted "None" appears on the web page

    out = out + '<div style="padding-top:30px"></div>'
    out = out + '<hr /><p style="text-align:left; padding-top:10px;padding-bottom:20px">'
    out = out + 'If you have any questions, please contact <a href="mailto:tisobe@cfa.harvard.edu">tisobe@cfa.harvard.edu</a>.'
    out = out + '\n\n\n</body>\n</html>\n'
#
#--- write out the html data
#
    name = web_dir + 'Html_pages/acis_hist_cccd' + str(ccd) + '_' + loc + '_' + dtype + '.html'
    with open(name, 'w') as fo:
        fo.write(out)

#--------------------------------------------------------------------------------------------
#-- set_plot_param: set  plotting parameters                                               --
#--------------------------------------------------------------------------------------------

def set_plot_range(xmin, xmax, int_list, slp_list, tlist0, tlist1, tlist2, dtype, loc):
    """
    set  plotting range parameters
    input:  xmin        --- min of x
            xmax        --- max of x
            int_list    --- a list of intercepts {[node0-al, node0-ti, node0-mn], {node1-al...]...]
            slp_list    --- a list of slopes
            tlist0      --- a list of lists of al [node0, node1, node2, node3t]
            tlist1      --- a list of lists of ti [node0, node1, node2, node3t]
            tlist2      --- a list of lists of mn [node0, node1, node2, node3t]
            dtype       --- data type: cnt, width, pos
            loc         --- location of data, either low or high
    output: ymin_list   --- a list of ymin for al, ti, mn
            ymax_list   --- a list of ymax for al, ti, mn
    """

    if dtype == 'cnt':
        ymin_list = [-5, -5, -5]
        ymax_list = [-1, -1, -1]
        ylab      = 'Log(Counts/Sec)'
    else:
        prange = find_range(xmin, xmax, int_list, slp_list)
        ymin_list = []
        ymax_list = []
        for k in range(0, 3):
            ydata = eval('tlist%s' %(str(k)))
            [ymin, ymax] = set_range(ydata, prange)
            ymin_list.append(ymin)
            ymax_list.append(ymax)

        ylab  = 'ADU'

    return [ymin_list, ymax_list, ylab]

#--------------------------------------------------------------------------------------------
#-- find_range: setting the size of plotting range                                       ----
#--------------------------------------------------------------------------------------------

def find_range(xmin, xmax, int_list, slp_list):
    """
    setting the size of plotting range
    input:  xmin        --- min of x value
            xmax        --- max of x value
            int_list    --- a list of intercepts {[node0-al, node0-ti, node0-mn], {node1-al...]...]
            slp_list    --- a list of slopes
    output: range       --- plotting width
    """

    prange = 1
    for n in range(0, 3):
        pmin =  1.0e6
        pmax = -1.0e6
#
#--- find min and max among all node data
#
        for m in range(0, 4):
            intc  = int_list[m][n]
            slope = slp_list[m][n]
            tval1 = intc + slope * (xmin -2000)
            tval2 = intc + slope * (xmax -2000)
            if tval1 < pmin:
                pmin = tval1
            if tval2 < pmin:
                pmin = tval2

            if tval1 > pmax:
                pmax = tval1
            if tval2 > pmax:
                pmax = tval2
#
#--- find the largest interval among the elements
#
        trange = pmax - pmin
        if trange > prange:
            prange = trange
    
    prange *= 1.8 

    return int(prange)

#--------------------------------------------------------------------------------------------
#-- set_range: set plotting range                                                         ---
#--------------------------------------------------------------------------------------------

def set_range(ydata, prange):
    """
    set plotting range
    input:  ydata   --- the data which the plotting range to be set
            prange  --- the width of the plotting range
    output: [ymin, ymax]    --- min and max of the range
    """

    med  = numpy.median(ydata)

    ymin  = int(med - 0.5 * prange)
    ymax  = ymin + prange
    
    return [ymin, ymax]

#----------------------------------------------------------------------------------
#-- create_label_html: creating a list of html links to the distribution plots  ---   
#----------------------------------------------------------------------------------

def create_label_html(ccd, node, loc,  y_list, m_list):
    """
    creating a list of html links to the distribution plots
    input:  ccd     --- ccd #
            node    --- node #
            loc     --- location: either"low" or "high"
            y_list  --- a list of year
            m_list  --- a list of month
    output: hlist   --- a list of html links
    """
#
#--- set directory path and html top link to the plot
#
    fdir      = web_dir + 'Plot_indivisual/'
    html_plot = 'https://cxc.cfa.harvard.edu/mta_days/mta_acis_hist/Plot_indivisual/';
    #html_plot = 'https://cxc.cfa.harvard.edu/mta_days/mta_acis_hist_test/Plot_indivisual/';
    hlink     = '<p> <img src="' + html_plot 
#
#--- read data for the given ccd/node/loc combination
#
    dfile     = data_dir + 'ccd' + str(ccd) + '_node' + str(node) + '_' + loc
    f         = open(dfile, 'r')
    data      = [line.strip() for line in f.readlines()]
    f.close()

    hlist = []
    for k in range(0, len(y_list)):

        lyear = y_list[k]
        mon   = m_list[k]

        lmon = mon
        if float(mon) < 10:
            lmon = '0' + lmon

        hfile = 'CCD' + str(ccd) + '/node' + str(node) + '/' + loc + '/hist_'
        hfile = hfile +  lyear + '_' + lmon + '.png'

        title = '<b style="background-color:yellow">CCD' + str(ccd)
        title = title + ' Node: ' + str(node) + ' (Year: ' + lyear +' Month: ' + lmon +')</b>'

        ulink = title + hlink
#
#--- check whether the plot exists
#
        chk   = fdir + hfile
        if os.path.isfile(chk):
#
#--- add a plot
#
            alink = ulink + hfile + '" width=600px> </p>'
#
#--- add a data table
#
            line  = create_table(data, lyear, mon)

            alink = alink + line
        else:
            alink = '<p><span style="font-size:250%"><b>No Plot</b></span> </p>'
            line  = create_table(data, lyear, mon)
            if line != 'No Data':
                alink = title + alink + line
            else:
                alink = title + alink

        hlist.append(alink)

    return hlist

#---------------------------------------------------------------------
#-- create_table: create data table for the html page               --
#---------------------------------------------------------------------

def create_table(data, year, mon):
    """
    create data table for the html page
    input:  data    --- a list of data
            year    --- a year of the data needed
            mon     --- a month of the data needed
    output: line    --- a html table of data. if there is no data, 
                        return "No Data"
    """

    tag = str(year) + ':' + str(mon)
    for ent in data:
        atemp = re.split('\s+', ent)
        if atemp[0] == tag:
            duration = float(atemp[-1])

            mn_p = str(round(float(atemp[2]),  2))
            al_p = str(round(float(atemp[8]),  2))
            ti_p = str(round(float(atemp[14]), 2))
#
#--- by multiplying 2.354, change it from signa to width
#
            mn_w = str(round(float(atemp[6])  * 2.354, 2))
            al_w = str(round(float(atemp[12]) * 2.354, 2))
            ti_w = str(round(float(atemp[18]) * 2.354, 2))
#
#--- count rate is rather small, when it goes < 1e-4, use the form, e.g. 1.0e-5
#
            mn_c = float(atemp[4]) /duration
            if mn_c < 1e-4:
                mn_c = "%1.2e" % (mn_c)
            else:
                mn_c = str(round(mn_c, 4))

            al_c = float(atemp[10])/duration
            if al_c < 1e-4:
                al_c = "%1.2e" % (al_c)
            else:
                al_c = str(round(al_c, 4))

            ti_c = float(atemp[16])/duration
            if ti_c < 1e-4:
                ti_c = "%1.2e" % (ti_c)
            else:
                ti_c = str(round(ti_c, 4))

            line = '<table border=1 cellpadding=2 style="text-aligne:center;background-color:yellow">'
            line = line + '<tr><th>&#160;</th>'
            line = line + '<th>Peak Position</th>'
            line = line + '<th>Peak Width</th>'
            line = line + '<th>Counts Rate<br />(cnts/sec)</th></tr>'

            line = line + '<tr><th>Al k-alpha</th>'
            line = line + '<th>' + al_p + '</th>'
            line = line + '<th>' + al_w + '</th>'
            line = line + '<th>' + al_c + '</th>'
            line = line + '</tr>'

            line = line + '<tr><th>Ti k-alpha</th>'
            line = line + '<th>' + ti_p + '</th>'
            line = line + '<th>' + ti_w + '</th>'
            line = line + '<th>' + ti_c + '</th>'
            line = line + '</tr>'

            line = line + '<tr><th>Mn k-alpha</th>'
            line = line + '<th>' + mn_p + '</th>'
            line = line + '<th>' + mn_w + '</th>'
            line = line + '<th>' + mn_c + '</th>'
            line = line + '</tr></table>'

            return line
            break

    return '<p>No Data</p>'

#---------------------------------------------------------------------
#-- set_initial_guess: provide initial guess for kmpfit procedure   --
#---------------------------------------------------------------------

def set_initial_guess(dtype, k):
    """
    provide initial guess for kmpfit procedure
    input:  dtype   --- data type: pos, width, cnt
            k       --- line # (al, ti, mn in order)
    output: [const1, cost2]
    """

    if dtype == 'pos':
        glist = [360, 1120, 1300]
    elif dtype == 'width':
        glist = [20, 30, 40]
    else:
        glist = [-3, -3, -3]

    return [glist[k], -0.3]


#---------------------------------------------------------------------
#-- y_text: set y position of text                                 ---
#---------------------------------------------------------------------

def y_text(ymin, ymax):
    """
    set y position of text
    input:  ymin    --- min of y
            ymax    --- max of y
    output  ytext   --- y position of the text
    """

    ydiff = ymax - ymin
    ytext = ymin + 0.10 * ydiff

    return ytext

#--------------------------------------------------------------------------------------------

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':

    acis_hist_plot_trend()
