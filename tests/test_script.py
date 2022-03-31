import os
import pytest
#import app.my_script

# Needs to be checked to ensure test files are imported correct
@pytest.fixture
def valid_files():
    return [os.path.abspath(os.path.join(dirpath, f)) for dirpath, _, filenames in
            os.walk(f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/") for f in filenames]

# Dummytest which will always succeed - must be replaced by real tests
def test_dummy():
    assert True

def test_dd20_cleaner():
    pass

def test_mrid_map_dict():
    data = ''
    test_dict = {'d51269gh-25e0-4a11-b32e-bd0fba7af745': 'EEE-FFF-1',
                     'd51269gh-25e0-4a11-b32e-bd0fba7af747': 'EEE-FFF-2',
                     'd51269gh-25e0-4a11-b32e-bd0fba7af751': 'GGG-HHH',
                     'd51269gh-25e0-4a11-b32e-bd0fba7af757': 'CCC-DDD',
                     'd51269gh-25e0-4a11-b32e-bd0fba7af759': 'III-ÆØÅ',
                     'd51269gh-25e0-4a11-b32e-bd0fba7af760': 'ASK-ERS'
                    }
    assert my_function(data) == test_dict

def test_moat_ets_dd20_map_dict():

    data2 = ''
    test_dict2 = {'E_GGG-HHH': 'E_GGGV-HHH'}

    assert my_function2(data2) == test_dict2

def combine_conduct_info_to_pandas():
    pass
