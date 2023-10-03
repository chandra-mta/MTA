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

def test_is_leapyear():
    assert testmodule.is_leapyear(2023) == False
    assert testmodule.is_leapyear(2100) == False
    assert testmodule.is_leapyear(2024) == True

@pytest.mark.skip(reason="Unused")
def test_set_plotting_range():
    x = [0,3,5,10]
    y = [-5,0,2,5]
    [xmin, xmax, ymin, ymax] = testmodule.set_plotting_range(x,y)
    assert xmin == -1
    assert xmax == 11
    assert ymin == -6
    assert ymax == 6

def test_create_moving_average():
    x = list(range(20)) + list(range(20,0,-1))
    y = [4] * 40
    smoothx = testmodule.create_moving_average(x, 3)
    assert smoothx == [1.0, 1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, \
                       11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 19.333333333333332, 19.0, 18.0, 17.0, \
                        16.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0]
    smoothy = testmodule.create_moving_average(y, 100)
    assert smoothy == [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, \
                       4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, \
                        4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]

@pytest.mark.skip(reason="Unused")
def test_check_time_format():
    pass

def test_change_ctime_to_ydate():
    x = testmodule.change_ctime_to_ydate(800000000,yd=0)
    y = testmodule.change_ctime_to_ydate(800000000,yd=1)
    assert x == [2023.0, 2023.3541327630644]
    assert y == [2023.0, 129.25845851851852]

def test_select_data():
    ifile = os.path.join(testmodule.DATA_DIR,'full_focal_plane_data_2022')
    start = 757393880
    stop  = 757394080
    [xdata, ydata, radata, rbdata] = testmodule.select_data(ifile, start, stop)
    assert ydata == [-118.9, -118.9, -118.9, -118.9, -118.9, -118.9, -118.9, -118.9, -118.9, -118.9, -118.9, -118.9]
    assert radata == [6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 9.028999999999996, 9.028999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996]
    assert rbdata == [6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996, 6.638999999999996]

    ifile = os.path.join(testmodule.DATA_DIR,'full_focal_plane_data_2019')
    start = 672146830
    stop  = 672147275
    [xdata, ydata, radata, rbdata] = testmodule.select_data(ifile, start, stop)
    assert ydata == [-117.45, -117.45, -117.45, -117.61, -117.61, -117.61, -117.45, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.61, -117.77, -117.61]
    assert radata == [8.088999999999999, 8.088999999999999, 8.088999999999999, 7.929000000000002, 7.929000000000002, 7.929000000000002, 8.088999999999999, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.7690000000000055, 7.929000000000002]
    assert rbdata == [5.694999999999993, 5.694999999999993, 5.694999999999993, 7.929000000000002, 7.929000000000002, 7.929000000000002, 8.088999999999999, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.929000000000002, 7.7690000000000055, 7.929000000000002]

@pytest.mark.skip(reason="Unused")
def test_convert_to_ydate_list():
    pass

@pytest.mark.skip(reason="Unused")
def test_select_data_over_data_files():
    pass

def test_plot_data():
    x = list(range(7))
    y0 = [2*x-120 for x in x]
    y1 = [(x-1)**2 +3 for x in x]
    y2 = [x + 3 for x in x]
    xmin = min(x) - 1
    xmax = max(x) + 1
    ymin = min(y0+y1+y2) - 1
    ymax = max(y0+y1+y2) + 1
    xname = 'xvalue'
    yname = 'yvalue'
    outname = 'test_plot'
    testmodule.plot_data(x, y0, y1, y2, xmin, xmax, ymin, ymax,  xname, yname, outname)
    warnings.warn(UserWarning("Manually check validity of plot in outTest/Plots"))

def test_create_focal_temperature_plots():
    testmodule.create_focal_temperature_plots()
    warnings.warn(UserWarning("Manually chekc validity of plot in outTest/Plots"))
