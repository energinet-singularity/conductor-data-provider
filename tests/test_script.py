import pytest
import os
import app.my_script
import pandas as pd


# TODO: add negative test with invalid data also
def test_extract_conducter_data_from_dd20():
    # Input is DD20 file. Output is pandas datafram with conductor data (needed data in format below).
    expected_dict = {'ACLINE_EMSNAME_EXPECTED': ['E_EEE-FFF-1', 'E_EEE-FFF-2', 'E_GGG-HHH', 'E_AAA-BBB', 'D_CCC-DDD', 'C_III-ÆØÅ'],
                     'ACLINE_DD20_NAME': ['EEE-FFF-1', 'EEE-FFF-2', 'GGG-HHH', 'AAA-BBB', 'CCC-DDD', 'III-ÆØÅ'],
                     'CONDUCTER_TYPE': ['Air', 'Air', 'Air', 'Air', 'Air', 'Air'],
                     'RESTRICTIVE_COMPONENT_LIMIT': [455, 455, 1111, 1222, 1333, 1444],
                     'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': [700, 700, None, 800, None, None],
                     'RESTRICTIVE_CABLE_LIMIT_15M': [1100, 1100, None, 1200, None, None],
                     'RESTRICTIVE_CABLE_LIMIT_1H': [900, 900, None, 1000, None, None],
                     'RESTRICTIVE_CABLE_LIMIT_40H': [800, 800, None, 900, None, None]}
    expected_dd20_dataframe = pd.DataFrame.from_dict(expected_dict).fillna('None')

    dd20_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DD20.XLSM"

    dd20_dataframe = app.my_script.parse_excel_sheet_to_dataframe(file_path=dd20_filepath,
                                                                  sheet_name='Stationsdata',
                                                                  header_index=1)

    resulting_dd20_dataframe = app.my_script.extract_conducter_data_from_dd20(dataframe=dd20_dataframe)
    print(resulting_dd20_dataframe)
    print(expected_dd20_dataframe)

    assert resulting_dd20_dataframe.equals(expected_dd20_dataframe)


"""
# TODO: how to test function which does not return but sys.exit(1)?
def test_verify_dataframe_columns():
    # test columns verify
    columns = ['A', 'B', 'C']
    data = [[1, 2, 3]]
    dataframe = pd.DataFrame(data=data, columns=columns)
    check = app.my_script.verify_dataframe_columns(dataframe=dataframe, expected_columns=columns, allow_extra_columns=False)
    assert True
"""

'''
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
'''
"""
def test_combine_conduct_info_to_pandas():

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

"""
