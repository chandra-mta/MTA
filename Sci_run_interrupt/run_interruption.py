#!/proj/sot/ska3/flight/bin/python

#################################################################################
#                                                                               #
#       run_interruption.py: run all sci run interrupt scripts                  #
#                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                       #
#                                                                               #
#               last update: Apr 02, 2024                                       #
#                                                                               #
#################################################################################

import re
import sys
import os
import numpy as np
from Chandra.Time import DateTime
from kadi import events
from datetime import datetime
import argparse
import getpass

#
#--- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/Interrupt/Scripts'
PLOT_DIR = '/data/mta_www/mta_interrupt/Main_plot'
EPHIN_DIR = '/data/mta_www/mta_interrupt/Ephin_plot'
GOES_DIR = '/data/mta_www/mta_interrupt/GOES_plot'
XMM_DIR = '/data/mta_www/mta_interrupt/XMM_plot'
HTML_DIR = '/data/mta_www/mta_interrupt/Html_dir'
WEB_DIR = '/data/mta_www/mta_interrupt'

#For data extraction
#Out versions for testing
DATA_DIR = '/data/mta/Script/Interrupt/Data'
OUT_DATA_DIR = '/data/mta/Script/Interrupt/Data'

WDATA_DIR = '/data/mta_www/mta_interrupt/Data_dir'
OUT_WDATA_DIR = '/data/mta_www/mta_interrupt/Data_dir'

WDATA_DIR2 = '/data/mta4/www/RADIATION_new/mta_interrupt/Data_dir'

STAT_DIR = '/data/mta_www/mta_interrupt/Stat_dir'
OUT_STAT_DIR = '/data/mta_www/mta_interrupt/Stat_dir'

#Time formats for stat / stop arguments
TIME_FORMATS = ["%Y:%j:%H:%M:%S", "%Y:%j:%H:%M", "%Y:%m:%d:%H:%M:%S", "%Y:%m:%d:%H:%M"]

#
#--- append a path to a privte folder to python directory
#
sys.path.append(BIN_DIR)

#
#--- extracting data
#
import extract_data                     as edata
#
#--- Ephin ploting routines
#
import plot_ephin                       as ephin
#
#---- GOES ploting routiens
#
import plot_goes                        as goes
#
#---- ACE plotting routines
#
import plot_ace_rad                     as ace 
#
#---- extract xmm data and plot
#
import compute_xmm_stat_plot_for_report as xmm
#
#---- update html page
#
import sci_run_print_html               as srphtml

#-------------------------------------------------------------------------------------
#-- compute_gap: process stat / stop time arguments                                 --
#-------------------------------------------------------------------------------------
def compute_gap(start, stop, name = None):
    """
    Intake string-formatted time and output interruption data
    """
    for form in TIME_FORMATS:
        try:
            tstart = datetime.strptime(start, form)
        except:
            pass
    for form in TIME_FORMATS:
        try:
            tstop = datetime.strptime(stop, form)
        except:
            pass
    if name == None:
        name = tstart.strftime("%Y%m%d")
    
    chandra_start = DateTime(tstart.strftime("%Y:%j:%M:%H:%S"), format='date')
    chandra_stop = DateTime(tstop.strftime("%Y:%j:%M:%H:%S"), format='date')
    
    rad_zones = events.rad_zones.filter(start = chandra_start, stop = chandra_stop).table
    rad_zones_duration_secs = np.sum(rad_zones['dur'])
    science_time_lost_secs = chandra_stop.secs - chandra_start.secs - rad_zones_duration_secs
    
    out = {'name': name,
           'tstart': tstart.strftime("%Y:%j:%M:%H:%S"),
           'tstop': tstart.strftime("%Y:%j:%M:%H:%S"),
           'tlost': f'{(science_time_lost_secs / 1000.):.2f}'} # ksec
    return out

#-------------------------------------------------------------------------------------
#-- run_interrupt: run all sci run plot routines                                    --
#-------------------------------------------------------------------------------------

def run_interrupt(event_data):
    
    """
    run all sci run plot routines
    input:  ifile                --- input file name. if it is not given, the script will ask
    output: <plot_dir>/*.png    --- ace data plot
            <ephin_dir>/*.png   --- ephin data plot
            <goes_dir>/*.png    --- goes data plot
            <xmm_dir>/*.png     --- xmm data plot
            <html_dir>/*.html   --- html page for that interruption
            <web_dir>/rad_interrupt.html    --- main page
    """
#
#--- extract data
#
    print( "Extracting Data")
    edata.extract_data(event_data)

    print(f"Plotting: {event_data['name']}")
#
#--- plot Ephin data
#
    print("EPHIN/HRC")
    ephin.plot_ephin_main(event_data)
#
#---- plot GOES data
#
    print("GOES")
    goes.plot_goes_main(event_data)
#
#---- plot other radiation data (from NOAA)
#
    print("NOAA")
    ace.start_ace_plot(event_data)
#
#---- extract and plot XMM data
#
    print("XMM")
    xmm.read_xmm_and_process(event_data)
#
#---- create individual html page
#
    print("HTML UPDATE")
    srphtml.print_each_html_control(event_data)
#
#---- update main html page
#
    srphtml.print_each_html_control()

#-------------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location.")
    parser.add_argument("--start", required = True, help = "Start time of radiation shutdown.")
    parser.add_argument("--stop", required = True, help = "Stop time of radiation shutdown.")
    parser.add_argument("-n","--name", required = False, help = "Custom name for event (defaults to start date in <YYYY><MM><DD> format).")
    parser.add_argument("-r","--run", choices = ['auto','manual'], required = True, help = "Determine SCS-107 run version.")
    args = parser.parse_args()

    event_data = compute_gap(args.start, args.stop, name = args.name)
    event_data['mode'] = args.run

    if args.mode == "test":
#
#--- Send warning if not running test on machine with mta_www access
#
        import platform
        machine = platform.node()
        if machine not in ['boba-v.cfa.harvard.edu', 'luke-v.cfa.harvard.edu', 'r2d2-v.cfa.harvard.edu', 'c3po-v.cfa.harvard.edu']:
            parser.error(f"Need virtual machine (boba, luke, r2d2, c3po) to view /data/mta_www. Current machine: {machine}")
#
#--- Collect imported modules for ease of pathing changes.
#
        MOD_GROUP = {}
        for name, mod in sys.modules.items():
            try:
                if BIN_DIR in mod.__file__:
                    MOD_GROUP[name] = mod
            except:
                pass
#
#--- Iterate over all imported modules and change their pathing
#
        for mod in MOD_GROUP.values():
            if hasattr(mod,'BIN_DIR'):
                mod.BIN_DIR = BIN_DIR
            if hasattr(mod,'PLOT_DIR'):
                mod.PLOT_DIR = PLOT_DIR
            if hasattr(mod,'EPHIN_DIR'):
                mod.EPHIN_DIR = EPHIN_DIR
            if hasattr(mod,'GOES_DIR'):
                mod.GOES_DIR = GOES_DIR
            if hasattr(mod,'XMM_DIR'):
                mod.XMM_DIR = XMM_DIR
            if hasattr(mod,'HTML_DIR'):
                mod.HTML_DIR = HTML_DIR
            if hasattr(mod,'WEB_DIR'):
                mod.WEB_DIR = WEB_DIR


        run_interrupt(event_data)

    elif args.mode == 'flight':
#
#--- Create a lock file and exit strategy in case of race conditions
#
        name = os.path.basename(__file__).split(".")[0]
        user = getpass.getuser()
        if os.path.isfile(f"/tmp/{user}/{name}.lock"):
            sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
        else:
            os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

        run_interrupt(event_data)
#
#--- Remove lock file once process is completed
#
        os.system(f"rm /tmp/{user}/{name}.lock")