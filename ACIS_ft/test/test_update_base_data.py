#!/proj/sot/ska3/flight/bin/python


import sys, os
import pytest
import warnings

#Path altering to import script which is undergoing testing
PARENT_DIR = os.path.dirname(os.getcwd())
OUT_DIR = f"{os.getcwd()}/outTest/"
sys.path.insert(0,PARENT_DIR)
import update_base_data as testmodule

#Define new global paths for test running.
testmodule.SHORT_TERM = f"{OUT_DIR}Short_term/"
os.system(f"mkdir -p {testmodule.SHORT_TERM}")
testmodule.BIN_DIR = f"{PARENT_DIR}/"
ORIGINAL_HOUSE_KEEPING = testmodule.HOUSE_KEEPING
testmodule.HOUSE_KEEPING = f"{OUT_DIR}house_keeping/"
os.system(f"cp -r {ORIGINAL_HOUSE_KEEPING} {testmodule.HOUSE_KEEPING}")


def test_create_out_name():
    ifile = '/dsops/GOT/input/2018_119_2325_120_1206_Dump_EM_76390.gz'
    out   = testmodule.create_out_name(ifile)
    atemp = out.split("/")
    assert atemp[-1] == 'data_2018_119_2325_120_1206'


def test_extract_data_from_dump():
    if os.path.isdir('/dsops/GOT/input/'):
        nlist = ['/dsops/GOT/input/2023_254_0207_254_1126_Dump_EM_07557.gz']
        plist = testmodule.extract_data_from_dump(nlist)
        warnings.warn(UserWarning(f"This function generates data files. Manually check {plist[0]}."))
        assert plist[0] == f"{testmodule.SHORT_TERM}data_2023_254_0207_254_1126"
        with open(plist[0],'r') as f:
            compare = f.readlines()
        
        assert compare[0] == '  2332016 254:7659.500000 -111.30 -248.67\n'
        assert compare[-1] == '  2462840 254:41183.150000 -119.54 -248.52\n'
    else:
        raise AssertionError("Cannot find /dsops/GOT/input. Run test on c3po-v.")

@pytest.marker.skip()
def test_update_base_data():
    #TODO do we need this test for what is essetially a wrapper function of pairing Dump files to their shortterm locations?
    testmodule.update_base_data()

