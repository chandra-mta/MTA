#!/proj/sot/ska3/flight/bin/python
"""
**update_base_data.py**: Wrapper for updating the short term ACIS focal temperature data files by running the getnrt perl script.

:Author: W. Aaron (william.aaron@cfa.harvad.edu)
:Last Updated: Feb 05, 2026
"""

import sys
import os
import getpass
import argparse
import glob
import json
from Ska.Shell import getenv, bash
#
# --- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/ACIS/Focal/Script'
HOUSE_KEEPING = '/data/mta/Script/ACIS/Focal/Script/house_keeping'
DUMP_DIR = "/dsops/GOT/input"
SHORT_TERM = '/data/mta/Script/ACIS/Focal/Short_term'
#
# --- ASCDS Variables for getnrt
#
ASCDSENV = getenv('source /home/ascds/.ascrc -r release; setenv ACISTOOLSDIR /home/pgf', shell='tcsh')


def update_base_data():
    """
    Update acis focal temperature data files.

    :File In: <DUMP_DIR>/*_Dump_EM_*.gz
    :File Out: <SHORT_TERM>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """
    record_file = f"{HOUSE_KEEPING}/processed_dump_files.json"
    os.system(f"cp -f {record_file} {record_file}~")
    with open(record_file) as f:
        processed_dump_files = json.load(f)

    current_dump_files = glob.glob(f"{DUMP_DIR}/*_Dump_EM_*.gz")

    new_file_list = list(set(processed_dump_files).difference(set(current_dump_files)))

    for i, file in enumerate(new_file_list):
        try:
            extract_data_from_dump(file)
        except Exception as e:
            #: Record the sucessfully processed files then exit with error
            processed_dump_files['data'] += new_file_list[:i]

            with open(record_file, 'w') as f:
                json.dump(processed_dump_files, f, indent = 4)
            raise e

def extract_data_from_dump(file):
    """
    Extract focal data from dump data

    :param file: Path to dumps files
    :type file: str
    
    :File Out: <SHORT_TERM>/data_<yyyy>_<ddd>_<hhmm>_<ddd>_<hhmm>
    """

    name = _filename(file)
    cmd = f"/usr/bin/env PERL5LIB=  gzip -dc {file} | {BIN_DIR}/getnrt -O $* | {BIN_DIR}/acis_ft_fptemp.pl >> {SHORT_TERM}/{name}"
    bash (cmd, env=ASCDSENV)


def _filename(file):
    """
    Generate name for intermediate file.
    """
    basename = os.path.basename(file)
    time_string = basename.split('_Dump')[0]
    return f"data_{time_string}"


if __name__ == "__main__":
    
    update_base_data()