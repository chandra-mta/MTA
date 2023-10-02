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
import create_focal_temperature_plots as testmodule
testmodule.OUT_DATA_DIR = f"{OUT_DIR}Data/"
os.system(f"mkdir -p {testmodule.OUT_DATA_DIR}")
testmodule.PLOT_DIR = f"{OUT_DIR}Plots/"
os.system(f"mkdir -p {testmodule.PLOT_DIR}")

