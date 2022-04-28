import pandas as pd
import os

# App modules
from app.helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from app.helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dict
from app.helpers.parse_mrid_map import parse_aclineseg_scada_data_to_dataframe
from app.helpers.join_data import create_conductor_dataframe

# expected DD20 data
# TODO: build line with _1 and?
expected_dd20_dict = {'ACLINE_EMSNAME_EXPECTED': ['E_EEE-FFF_1', 'E_EEE-FFF_2', 'E_GGG-HHH', 'E_AAA-BBB', 'D_CCC-DDD', 'C_III-ÆØÅ'],
                      'ACLINE_DD20_NAME': ['EEE-FFF-1', 'EEE-FFF-2', 'GGG-HHH', 'AAA-BBB', 'CCC-DDD', 'III-ÆØÅ'],
                      'CONDUCTOR_TYPE': ['Conduck', 'Conduck', 'Conduck', 'Conduck', 'Conduck', 'Conduck'],
                      'CONDUCTOR_COUNT': [2, 1, 1, 1, 1, 1],
                      'SYSTEM_COUNT': [1, 1, 2, 2, 1, 1],
                      'MAX_TEMPERATURE': [70, 70, 70, 70, 70, 70],
                      'RESTRICTIVE_CONDUCTOR_LIMIT_CONTINIOUS': [1168, 1131, 1624, 1432, 801, 2413],
                      'RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS': [1600, 1200, 1250, 1600, 1200, 2400],
                      'RESTRICTIVE_COMPONENT_LIMIT_15M': [1600, 1200, 1250, 1600, 1200, 2400],
                      'RESTRICTIVE_COMPONENT_LIMIT_1H': [1600, 1200, 1250, 1600, 1200, 2400],
                      'RESTRICTIVE_COMPONENT_LIMIT_40H': [1600, 1200, 1250, 1600, 1200, 2400],
                      'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': [700, 700, None, 800, None, None],
                      'RESTRICTIVE_CABLE_LIMIT_15M': [1100, 1100, None, 1200, None, None],
                      'RESTRICTIVE_CABLE_LIMIT_1H': [900, 900, None, 1000, None, None],
                      'RESTRICTIVE_CABLE_LIMIT_40H': [800, 800, None, 900, None, None]}
expected_dd20_dataframe = pd.DataFrame.from_dict(expected_dd20_dict).fillna('None')

#
expected_dd20_to_scada_name_dict = {'E_EEE-FFF_1': 'E_EEEV-FFF_1'}

#
expected_lineseg_to_mrid_dict = {'ACLINESEGMENT_MRID': ['66b4596e-asfv-tyuy-5478-bd208f26a446',
                                                        '66b4596e-asfv-tyuy-5478-bd208f26a447',
                                                        '66b4596e-asfv-tyuy-5478-bd208f26a451',
                                                        '66b4596e-asfv-tyuy-5478-bd208f26a452',
                                                        '66b4596e-asfv-tyuy-5478-bd208f26a455',
                                                        '66b4596e-asfv-tyuy-5478-bd208f26a457',
                                                        '66b4596e-asfv-tyuy-5478-bd208f26a459'],
                                 'LINE_EMSNAME': ['E_EEEV-FFF_1', 'E_EEE-FFF_2', 'E_GGG-HHH', 'E_GGG-HHH', 'D_CCC-DDD', 'C_III-ÆØÅ', 'C_ASK-ERS'],
                                 'DLR_ENABLED': [True, True, False, False, True, True, True]}
expected_lineseg_to_mrid_dataframe = pd.DataFrame.from_dict(expected_lineseg_to_mrid_dict)

#
expected_dlr_dataframe_dict = {'ACLINESEGMENT_MRID': ['66b4596e-asfv-tyuy-5478-bd208f26a446',
                                                      '66b4596e-asfv-tyuy-5478-bd208f26a447',
                                                      '66b4596e-asfv-tyuy-5478-bd208f26a451',
                                                      '66b4596e-asfv-tyuy-5478-bd208f26a452',
                                                      '66b4596e-asfv-tyuy-5478-bd208f26a455',
                                                      '66b4596e-asfv-tyuy-5478-bd208f26a457'],
                               'LINE_EMSNAME': ['E_EEEV-FFF_1', 'E_EEE-FFF_2', 'E_GGG-HHH', 'E_GGG-HHH', 'D_CCC-DDD', 'C_III-ÆØÅ'],
                               'DLR_ENABLED': [True, True, False, False, True, True],
                               'ACLINE_DD20_NAME': ['EEE-FFF-1', 'EEE-FFF-2', 'GGG-HHH', 'GGG-HHH', 'CCC-DDD', 'III-ÆØÅ'],
                               'CONDUCTOR_TYPE': ['Conduck', 'Conduck', 'Conduck', 'Conduck', 'Conduck', 'Conduck'],
                               'CONDUCTOR_COUNT': [2, 1, 1, 1, 1, 1],
                               'SYSTEM_COUNT': [1, 1, 2, 2, 1, 1],
                               'MAX_TEMPERATURE': [70, 70, 70, 70, 70, 70],
                               'RESTRICTIVE_CONDUCTOR_LIMIT_CONTINIOUS': [1168, 1131, 1624, 1624, 801, 2413],
                               'RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS': [1600, 1200, 1250, 1250, 1200, 2400],
                               'RESTRICTIVE_COMPONENT_LIMIT_15M': [1600, 1200, 1250, 1250, 1200, 2400],
                               'RESTRICTIVE_COMPONENT_LIMIT_1H': [1600, 1200, 1250, 1250, 1200, 2400],
                               'RESTRICTIVE_COMPONENT_LIMIT_40H': [1600, 1200, 1250, 1250, 1200, 2400],
                               'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': [700, 700, None,  None, None, None],
                               'RESTRICTIVE_CABLE_LIMIT_15M': [1100, 1100, None,  None, None, None],
                               'RESTRICTIVE_CABLE_LIMIT_1H': [900, 900, None,  None, None, None],
                               'RESTRICTIVE_CABLE_LIMIT_40H': [800, 800, None, None, None, None]}
expected_dlr_dataframe = pd.DataFrame.from_dict(expected_dlr_dataframe_dict).fillna('None')


# TODO: add negative test with invalid data also
def test_extract_conductor_data_from_dd20():

    DD20_FILE = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/"

    # Input is DD20 file. Output is pandas datafram with conductor data (needed data in format below).

    """dd20_dataframe_dict = app.helpers.excel_sheet_handler.parse_excel_sheets_to_dataframe_dict(file_path=DD20_FILE,
                                                                    sheets=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
                                                                    header_index=[1])"""
    df_station, df_line = app.helpers.parse_dd20.parse_dd20_excelsheets_to_dataframes(folder_path=DD20_FILE)

    data_station = app.helpers.parse_dd20.DD20StationDataframeParser(df_station=df_station)

    data_line = app.helpers.parse_dd20.DD20LineDataframeParser(df_line=df_line)

    obj = app.helpers.parse_dd20.DD20_to_acline_properties_mapper(data_station=data_station, data_line=data_line)

    resulting_dd20_dataframe = pd.DataFrame(data=[o.__dict__ for o in obj])

    print(resulting_dd20_dataframe.to_string())
    print(expected_dd20_dataframe.to_string())

    assert resulting_dd20_dataframe.equals(expected_dd20_dataframe)


def test_create_dlr_dataframe():
    resulting_dlr_dataframe = app.main.create_dlr_dataframe(conductor_dataframe=expected_dd20_dataframe,
                                                            dd20_to_scada_name=expected_dd20_to_scada_name_dict,
                                                            lineseg_to_mrid_dataframe=expected_lineseg_to_mrid_dataframe)

    print(resulting_dlr_dataframe.to_string())
    print(expected_dlr_dataframe.to_string())

    assert resulting_dlr_dataframe.equals(expected_dlr_dataframe)


"""
def test_define_dictonary_from_two_columns_in_a_dataframe():

    DLR_MRID_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/seg_line_mrid.csv'
    MRID_KEY_NAME = 'LINE_EMSNAME'
    MRID_VALUE_NAME = 'ACLINESEGMENT_MRID'

    mrid_dataframe = code.parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)
    TEST_DICTONARY = {'E_EEEV-FFF-1':    '66b4596e-asfv-tyuy-5478-bd208f26a446',
                      'E_EEE-FFF-2':    '66b4596e-asfv-tyuy-5478-bd208f26a447',
                      'E_GGG-HHH':      '66b4596e-asfv-tyuy-5478-bd208f26a451',
                      'E_GGG-HHH':      '66b4596e-asfv-tyuy-5478-bd208f26a452',
                      'D_CCC-DDD':      '66b4596e-asfv-tyuy-5478-bd208f26a455',
                      'C_III-ÆØÅ':      '66b4596e-asfv-tyuy-5478-bd208f26a457',
                      'C_ASK-ERS':      '66b4596e-asfv-tyuy-5478-bd208f26a459'}

    assert code.define_dictonary_from_two_columns_in_a_dataframe(mrid_dataframe,
                                                                 MRID_KEY_NAME, MRID_VALUE_NAME) == TEST_DICTONARY
"""


def test_parse_dataframe_columns_to_dictionary2():

    LIMITS_NAME_FILEPATH = f'{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/Limits_other.xlsx'
    DD20_DATASHEET_NAME = 'DD20Mapping'
    DD20_KEY_NAME = 'DD20 Name'
    DD20_VALUE_NAME = 'ETS Name'

    dd20_dataframe = pd.read_excel(io=LIMITS_NAME_FILEPATH, sheet_name=DD20_DATASHEET_NAME)
    TEST_DICTONARY = {'E_EEE-FFF_1': 'E_EEEV-FFF_1'}

    assert app.main.parse_dataframe_columns_to_dictionary(dd20_dataframe, DD20_KEY_NAME, DD20_VALUE_NAME) == TEST_DICTONARY


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
