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
import create_long_term_max_data as testmodule
testmodule.OUT_DATA_DIR = f"{OUT_DIR}Data/"
os.system(f"mkdir -p {testmodule.OUT_DATA_DIR}")

def test_set_start():
    data = ['800000000    foo', '700012868.184    bar']
    start = testmodule.set_start(data)
    assert start == 799977669.184
    start = testmodule.set_start(data,pos=1, add=1)
    assert start == 700012869.184

def test_create_long_term_max_data():
    testmodule.create_long_term_max_data(2022)
    with open(f"{testmodule.OUT_DATA_DIR}long_term_max_data",'r') as f:
        data = f.readlines()
    assert data[0] == '757425669\t-106.600\t-113.541\t-111.132\n'
    assert data[-1] == '788875269\t-110.980\t-118.349\t-118.349\n'