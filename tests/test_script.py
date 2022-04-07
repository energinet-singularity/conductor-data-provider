import pandas as pd
import os
import app.my_script as code


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

    dd20_dataframe = code.parse_excel_sheet_to_dataframe(file_path=dd20_filepath,
                                                         sheet_name='Stationsdata',
                                                         header_index=1)

    resulting_dd20_dataframe = code.extract_conducter_data_from_dd20(dataframe=dd20_dataframe)

    assert resulting_dd20_dataframe.equals(expected_dd20_dataframe)


def test_define_dictonary_from_two_columns_in_a_dataframe():

    DLR_MRID_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DLR_MRID.csv'
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    mrid_dataframe = code.parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)
    TEST_DICTONARY = {'E_EEE-FFF-1':    '66b4596e-asfv-tyuy-5478-bd208f26a446',
                      'E_EEE-FFF-2':    '66b4596e-asfv-tyuy-5478-bd208f26a447',
                      'E_GGG-HHH':      '66b4596e-asfv-tyuy-5478-bd208f26a451',
                      'D_CCC-DDD':      '66b4596e-asfv-tyuy-5478-bd208f26a455',
                      'C_III-ÆØÅ':      '66b4596e-asfv-tyuy-5478-bd208f26a457',
                      'C_ASK-ERS':      '66b4596e-asfv-tyuy-5478-bd208f26a459'}

    assert code.define_dictonary_from_two_columns_in_a_dataframe(mrid_dataframe,
                                                                 MRID_KEY_NAME, MRID_VALUE_NAME) == TEST_DICTONARY


def test_define_dictonary_from_two_columns_in_a_dataframe2():

    LIMITS_NAME_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/Limits_other.xlsx'
    DD20_DATASHEET_NAME = 'DD20Mapping'
    DD20_KEY_NAME = 'DD20 Name'
    DD20_VALUE_NAME = 'ETS Name'

    dd20_dataframe = pd.read_excel(io=LIMITS_NAME_FILEPATH, sheet_name=DD20_DATASHEET_NAME)
    TEST_DICTONARY = {'E_GGG-HHH': 'E_GGGV-HHH'}

    assert code.define_dictonary_from_two_columns_in_a_dataframe(dd20_dataframe,
                                                                 DD20_KEY_NAME, DD20_VALUE_NAME) == TEST_DICTONARY


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
