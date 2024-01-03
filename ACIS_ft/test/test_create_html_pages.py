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
import create_html_pages as testmodule
#TODO change pathign in WEB_DIR
testmodule.WEB_DIR = f"{OUT_DIR}Web/"
os.system(f"mkdir -p {testmodule.WEB_DIR}")


def test_create_plintbl():
    #No sub func
    year = 2022
    x = testmodule.create_plintbl(year)
    atemp = [i for i in x.split("\n") if i != '']
    assert atemp[0] == "<th><a href=\"javascript:WindowOpener('Year2022/focal_week_long_0.png')\">01</a></th>"
    assert atemp[-1] == "<th><a href=\"javascript:WindowOpener('Year2022/focal_week_long_52.png')\">53</a></th>"
    

def test_create_html_pages():
    #sub func: create_plintbl()
    uyear = 2022
    testmodule.create_html_pages(uyear)
    warnings.warn(UserWarning("Generates HTML page. Manually check in outTest/Web/"))

def test_run_html_page_script():
    #sub func: create_html_pages()
    all = 1
    testmodule.run_html_page_script(all)
    warnings.warn(UserWarning("Generates HTML page. Manually check in outTest/Web/"))
