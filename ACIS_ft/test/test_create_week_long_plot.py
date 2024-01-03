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
import create_week_long_plot as testmodule
testmodule.OUT_DATA_DIR = f"{OUT_DIR}Data/"
os.system(f"mkdir -p {testmodule.OUT_DATA_DIR}")
testmodule.PLOT_DIR = f"{OUT_DIR}Plots/"
os.system(f"mkdir -p {testmodule.PLOT_DIR}")


def test_is_leapyear():
    #no sub func
    assert testmodule.is_leapyear(2023) == False
    assert testmodule.is_leapyear(2100) == False
    assert testmodule.is_leapyear(2024) == True

@pytest.mark.skip(reason="Unused")
def test_set_plotting_range():
    #no sub func
    x = [0,3,5,10]
    y = [-5,0,2,5]
    [xmin, xmax, ymin, ymax] = testmodule.set_plotting_range(x,y)
    assert xmin == -1
    assert xmax == 11
    assert ymin == -6
    assert ymax == 6

@pytest.mark.skip(reason="Unused")
def test_create_moving_average():
    #no sub func
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

def test_change_ctime_to_ydate():
    #sub func
    #is_leapyear()
    x = testmodule.change_ctime_to_ydate(800000000,yd=0)
    y = testmodule.change_ctime_to_ydate(800000000,yd=1)
    assert x == [2023.0, 2023.3541327630644]
    assert y == [2023.0, 129.25845851851852]

def test_select_data():
    #sub func
    #change_ctime_to_ydate()
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
def test_check_time_format():
    #no sub func
    pass

@pytest.mark.skip(reason="Unused")
def test_adjust_year_date():
    #sub func
    #is_leapyear()
    pass

@pytest.mark.skip(reason="Unused")
def test_convert_date_list():
    #sub func
    #change_ctime_to_ydate()
    pass

@pytest.mark.skip(reason="Unused")
def test_convert_to_ydate_list():
    #sub func()
    #change_ctime_to_ydate()
    pass

def test_create_week_list():
    #no sub func()
    #divisions by week in ctime
    year = 2022
    bweek = 32
    eweek = 46
    [year, wlist, blist, elist] = testmodule.create_week_list(year, bweek, eweek)
    assert year == 2022
    assert wlist == [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
    assert blist == [776736069.184, 777340869.184, 777945669.184, 778550469.184, 779155269.184, 779760069.184, 780364869.184, 780969669.184, 781574469.184, 782179269.184, 782784069.184, 783388869.184, 783993669.184, 784598469.184]
    assert elist == [777340869.184, 777945669.184, 778550469.184, 779155269.184, 779760069.184, 780364869.184, 780969669.184, 781574469.184, 782179269.184, 782784069.184, 783388869.184, 783993669.184, 784598469.184, 785203269.184]
    

def test_find_week():
    #sub func
    #create_week_list()
    year = 2022
    [ylist, wlist, blist, elist]  = testmodule.find_week(year)
    #print(f"year : {year}")
    #print(f"wlist : {wlist}")
    #print(f"blist : {blist}")
    #print(f"elist : {elist}")
    assert year == 2022
    assert wlist == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
    assert blist == [757382469.184, 757987269.184, 758592069.184, 759196869.184, 759801669.184, 760406469.184, 761011269.184, 761616069.184, 762220869.184, 762825669.184, 763430469.184, 764035269.184, 764640069.184, 765244869.184, 765849669.184, 766454469.184, 767059269.184, 767664069.184, 768268869.184, 768873669.184, 769478469.184, 770083269.184, 770688069.184, 771292869.184, 771897669.184, 772502469.184, 773107269.184, 773712069.184, 774316869.184, 774921669.184, 775526469.184, 776131269.184, 776736069.184, 777340869.184, 777945669.184, 778550469.184, 779155269.184, 779760069.184, 780364869.184, 780969669.184, 781574469.184, 782179269.184, 782784069.184, 783388869.184, 783993669.184, 784598469.184, 785203269.184, 785808069.184, 786412869.184, 787017669.184, 787622469.184, 788227269.184, 788832069.184, 789436869.184]
    assert elist == [757987269.184, 758592069.184, 759196869.184, 759801669.184, 760406469.184, 761011269.184, 761616069.184, 762220869.184, 762825669.184, 763430469.184, 764035269.184, 764640069.184, 765244869.184, 765849669.184, 766454469.184, 767059269.184, 767664069.184, 768268869.184, 768873669.184, 769478469.184, 770083269.184, 770688069.184, 771292869.184, 771897669.184, 772502469.184, 773107269.184, 773712069.184, 774316869.184, 774921669.184, 775526469.184, 776131269.184, 776736069.184, 777340869.184, 777945669.184, 778550469.184, 779155269.184, 779760069.184, 780364869.184, 780969669.184, 781574469.184, 782179269.184, 782784069.184, 783388869.184, 783993669.184, 784598469.184, 785203269.184, 785808069.184, 786412869.184, 787017669.184, 787622469.184, 788227269.184, 788832069.184, 789436869.184, 790041669.184]


def test_plot_data():
    #no sub func
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

def test_create_plot():
    #TODO
    #sub func
    #select data()
    #plot_data()
    year = 2022
    week = 0
    start = 757382469.184
    stop = 757987269.184
    testmodule.create_plot(year, week, start, stop)
    warnings.warn(UserWarning("Manually check validity of plot in outTest/Plots/Year2022"))


def test_create_week_long_plot():
    #used
    #TODO main function
    #Sub func
    #find_week()
    #create_plot() - based on cycliong through each week and other
    testmodule.create_week_long_plot('')
    warnings.warn(UserWarning("Manually check validity of plot in outTest/Plots"))
    pass