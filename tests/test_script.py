import pytest
import app
import os

# Needs to be checked to ensure test files are imported correct
@pytest.fixture
def valid_files():
    return [os.path.abspath(os.path.join(dirpath, f)) for dirpath, _, filenames in
            os.walk(f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/") for f in filenames]

# Dummytest which will always succeed - must be replaced by real tests
def test_dummy():
    assert True


def test_dd20_cleaner():
    # Input is DD20 file. Output is pandas datafram with cleaned DD20 (needed data in format below).
    while 1 == 0:
        dd20_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/dd20.xlsm"
        expected_dict = {'LINESEGMENT_MRID': [None, None, None, None, None, None],
                            'ACLINE_EMSNAME': ['E_EEE-FFF-1', 'E_EEE-FFF-2', 'E_GGG-HHH', 'E_AAA-BBB', 'D_CCC-DDD', 'C_III-ÆØÅ'],
                            'ACLINE_DD20_NAME': ['EEE-FFF-1', 'EEE-FFF-2', 'GGG-HHH', 'AAA-BBB', 'CCC-DDD', 'III-ÆØÅ'],
                            'ACLINE_NAME_MAPPED': [None, None, None, None, None, None],
                            'CONDUCTER_TYPE': ['Air', 'Air', 'Air', 'Air', 'Air', 'Air'],
                            'RESTRICTIVE_COMPONENT_LIMIT': [455, 455, 1111, 1222, 1333, 1444],
                            'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': [700, 700, None, 800, None, None],
                            'RESTRICTIVE_CABLE_LIMIT_15M': [1100, 1100, None, 1200, None, None],
                            'RESTRICTIVE_CABLE_LIMIT_1H': [900, 900, None, 1000, None, None],
                            'RESTRICTIVE_CABLE_LIMIT_40H': [800, 800, None, 900, None, None]}

        assert app.my_script.parse_dd20(file=dd20_filepath) == expected_dict
        
    assert True

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

"""
def combine_conduct_info_to_pandas():
    # CODE:
    # input: cleaned dataframe, dict (dd20 name --> ets name when not auto tranlateable), dict (name-mrid)
    # output: dataframe with MRID inserted and mapping name (if present)
    expected_dict = {'LINESEGMENT_MRID': ['d51269gh-25e0-4a11-b32e-bd0fba7af745',
                                           'd51269gh-25e0-4a11-b32e-bd0fba7af747',
                                           'd51269gh-25e0-4a11-b32e-bd0fba7af751',
                                           None,
                                           'd51269gh-25e0-4a11-b32e-bd0fba7af757',
                                           'd51269gh-25e0-4a11-b32e-bd0fba7af759'],
                     'ACLINE_DD20_NAME': ['EEE-FFF-1', 'EEE-FFF-2', 'GGG-HHH', 'AAA-BBB', 'CCC-DDD', 'III-ÆØÅ'],
                     'ACLINE_NAME_MAPPING': [None, None, 'E_GGGV-HHH', None, None, None],
                     'ACLINE_EMSNAME': ['E_EEE-FFF-1', 'E_EEE-FFF-2', 'E_GGG-HHH', 'E_AAA-BBB', 'D_CCC-DDD', 'C_III-ÆØÅ'],
                     'CONDUCTER_TYPE': ['Air', 'Air', 'Air', 'Air', 'Air', 'Air'],
                     'RESTRICTIVE_COMPONENT_LIMIT': [455, 455, 1111, 1222, 1333, 1444],
                     'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': [700, 700, None, 800, None, None],
                     'RESTRICTIVE_CABLE_LIMIT_15M': [1100, 1100, None, 1200, None, None],
                     'RESTRICTIVE_CABLE_LIMIT_1H': [900, 900, None, 1000, None, None],
                     'RESTRICTIVE_CABLE_LIMIT_40H': [800, 800, None, 900, None, None]}

    assert my_func(file = "dd20.xlsm", dict1 = dict_from_func, dict2 = dict_from_func) == expected_dict

    # CODE:
    # use dict to fill out NAME_MAPPED (warning if mapping name not used)
    # use dict to fill out MRID (error if not possible)

"""
