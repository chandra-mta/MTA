#!/proj/sot/ska3/flight/bin/python
import sys, os
import pytest
import warnings

#Path altering to import script which is undergoing testing
PARENT_DIR = os.path.dirname(os.getcwd())
OUT_DIR = f"{os.getcwd()}/outTest/"
sys.path.insert(0,PARENT_DIR)
import full_focal_plane_data as testmodule

#Define new global paths for test running.
testmodule.BIN_DIR = f"{PARENT_DIR}/"
testmodule.DATA_DIR = f"{OUT_DIR}/Data/"
os.system(f"mkdir -p {testmodule.DATA_DIR}")
    
def test_ptime_to_ctime():
    year = 2022
    val1 = '366:1.000000'
    chg = 1
    ctime = testmodule.ptime_to_ctime(year, val1, chg)
    assert ctime == 788918470.184

#---------------------------------------------------------------------------------

def test_find_year_change():
    ifile = '/data/mta/Script/ACIS/Focal/Short_term/data_2017_365_2059_001_0241'
    [year, chg] = testmodule.find_year_change(ifile)
    assert year == 2017
    assert chg == 1

    ifile = '/data/mta/Script/ACIS/Focal/Short_term/data_2018_007_1000_007_1200'
    [year, chg] = testmodule.find_year_change(ifile)
    assert year == 2018
    assert chg == 0

#-------------------------------------------------------------------------------

def test_find_cold_plates():
    t_list = [638025960, 638243227]
    testa = [-123.14513244628904, -125.53862609863279]
    testb = [-123.14513244628904, -125.53862609863279]

    [crat, crbt] = testmodule.find_cold_plates(t_list)

    assert crat == testa
    assert crbt == testb

#-------------------------------------------------------------------------------

def test_create_full_focal_plane_data():
    rfile = 'data_2023_226_2116_227_0241'
    testmodule.create_full_focal_plane_data(rfile)
    with open(f"{testmodule.DATA_DIR}full_focal_plane_data_2023",'r') as f:
        data = [line.strip() for line in f.readlines()]
    assert data[0] == '808435046\t-114.860\t-123.145\t-120.749'
    assert data[-1] == '808454568\t-119.380\t-125.539\t-125.539'