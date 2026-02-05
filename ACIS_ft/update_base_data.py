#!/proj/sot/ska3/flight/bin/python
"""
**update_base_data.py**: Wrapper for updating the short term ACIS focal temperature data files by running the getnrt perl script.

:Author: W. Aaron (william.aaron@cfa.harvad.edu)
:Last Updated: Feb 05, 2026
"""

import os
import argparse
import glob
import json
from Ska.Shell import getenv, bash
#
# --- Define Directory Pathing
#
BIN_DIR = '/data/mta/Script/ACIS/Focal/Script'
HOUSE_KEEPING = f'{BIN_DIR}/house_keeping'
DUMP_DIR = "/dsops/GOT/input"
SHORT_TERM = '/data/mta/Script/ACIS/Focal/Short_term'
#
# --- ASCDS Variables for getnrt
#
ASCDSENV = getenv('source /home/ascds/.ascrc -r release; setenv ACISTOOLSDIR /home/pgf', shell='tcsh')

def get_options(args=None):
    parser = argparse.ArgumentParser(description="Update short term ACIS focal temp data files.")
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    opt = parser.parse_args(args)
    return opt

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

    new_file_list = list(set(current_dump_files).difference(set(processed_dump_files['data'])))
    for i, file in enumerate(new_file_list):
        try:
            extract_data_from_dump(file)
        except Exception as e:
            #: Record the sucessfully processed files then exit with error
            processed_dump_files['data'] += sorted(new_file_list[:i])

            with open(record_file, 'w') as f:
                json.dump(processed_dump_files, f, indent = 4)
            raise e
    #: Succesfully processed all files without error. Update processed file information.
    processed_dump_files['data'] = sorted(current_dump_files)
    with open(record_file, 'w') as f:
        json.dump(processed_dump_files, f, indent = 4)

def extract_data_from_dump(file):
    """
    Extract focal data from dump data.

    :param file: Path to dump files
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

    opt = get_options()
    if opt.mode == 'test':
        BIN_DIR = os.path.abspath(os.path.dirname(__file__))
        HOUSE_KEEPING = f'{BIN_DIR}/house_keeping'
        SHORT_TERM = f"{os.getcwd()}/test/_outTest"
        os.makedirs(SHORT_TERM, exist_ok=True)

    update_base_data()