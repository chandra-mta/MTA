#!/proj/sot/ska3/flight/bin/python
##!/usr/bin/env /data/mta/Script/Python3.8/envs/ska3-shiny/bin/python

"""
This version runs with the latest Ska release
Will replace the existing sci_run_compute_gap
following transition from local MTA to public
Ska environment
"""

import numpy as np
from Chandra.Time import DateTime
from kadi import events
import os

PATH = "/data/mta/Script/Interrupt/Exc"

def sci_run_compute_gap(input_file):
    """
    Compute lost science time by subtracting the radzone
    time from tstop-tstart
    """
        
    dat = np.loadtxt(input_file, dtype=str)
    tstop = DateTime(dat[2], format='date').date
    tstart = DateTime(dat[1], format='date').date
    rad_zones = events.rad_zones.filter(start=tstart, stop=tstop).table
    rad_zones_duration_secs = np.sum(rad_zones['dur'])
    science_time_lost_secs = DateTime(tstop).secs - DateTime(tstart).secs - rad_zones_duration_secs

    out = {'name': dat[0],
           'tstart': dat[1],
           'tstop': dat[2],
           'tlost': f'{(science_time_lost_secs / 1000.):.2f}', # ksec
           'mode': dat[4]}
    
    return out


if __name__ == '__main__':

    input_file = f'{PATH}/interruption_time_list'
    out = sci_run_compute_gap(input_file)
    
    line = ''
    for key in out.keys():
        line = ' '.join([line, out[key]])
    
    os.remove(input_file)
    
    with open(input_file, 'w') as fh:
        fh.write(f'{line.strip()}\n')
