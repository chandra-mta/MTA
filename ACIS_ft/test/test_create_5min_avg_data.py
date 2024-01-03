#!/proj/sot/ska3/flight/bin/python
import sys, os
import pytest
import warnings

#
#--- Pathing
#
PARENT_DIR = os.path.dirname(os.getcwd())
OUT_DIR = f"{os.getcwd()}/outTest/"
sys.path.insert(0,PARENT_DIR)
import create_5min_avg_data as testmodule
testmodule.OUT_DATA_DIR = f"{OUT_DIR}Data/"
os.system(f"mkdir -p {testmodule.OUT_DATA_DIR}")


def test_set_start():
    data = ['800000000    foo', '700012868.184    bar']
    start = testmodule.set_start(data)
    assert start == 799977669.184
    start = testmodule.set_start(data,pos=1, add=1)
    assert start == 700012869.184


def test_create_5min_avg_data():
    year = 2022
    testmodule.create_5min_avg_data(year)
    with open(f"{testmodule.OUT_DATA_DIR}focal_plane_data_5min_avg_2022",'r') as f:
        data = f.readlines()
    assert data[0] == '757383369\t-118.900\t-125.539\t-125.539\n'
    assert data[-1] == '788919369\t-115.145\t-121.313\t-120.749\n'