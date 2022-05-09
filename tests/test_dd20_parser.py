import pandas as pd
from numpy import nan
import os
import pytest

# App modules
from app.helpers.parse_dd20 import DD20StationDataframeParser, DD20LineDataframeParser
from app.helpers.parse_mrid_map import parse_aclineseg_scada_csvdata_to_dataframe
from app.helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dataframe

# Global parameters
DD20_HEADER_INDEX = 1
DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"

# fixtures for DD20
@pytest.fixture
def dd20_data_frame_dict():
    dd20_file_path = (f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DD20.XLSM")
    return pd.read_excel(io=dd20_file_path, sheet_name=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA], header=DD20_HEADER_INDEX)


def test_DD20StationDataframeParser(dd20_data_frame_dict):
    """
    This test verfies that all DD20 "station data" can be parsed correctly.
    """

    # arrange data needed for tests
    df_stationdata = dd20_data_frame_dict[DD20_SHEETNAME_STATIONSDATA]
    data_parse_result = DD20StationDataframeParser(df_station=df_stationdata)

    # Test dataframe has expected amount of datarows
    df_row_count_expected = 12
    assert len(df_stationdata.index) == df_row_count_expected

    # Test acline name list contain expected names
    acline_list_expected = ['AAA-BBB',
                            'CCC-DDD',
                            'EEE-FFF-1',
                            'EEE-FFF-2',
                            'GGG-HHH',
                            'III-ÆØÅ']
    assert data_parse_result.acline_name_list == acline_list_expected

    # Test mapping from AC-line name to voltagelevel in kV.
    conductor_kv_level_dict_expected = {'AAA-BBB': 150,
                                        'CCC-DDD': 220,
                                        'EEE-FFF-1': 132,
                                        'EEE-FFF-2': 132,
                                        'GGG-HHH': 132,
                                        'III-ÆØÅ': 400}
    assert data_parse_result.get_conductor_kv_level_dict() == conductor_kv_level_dict_expected

    # Test mapping from AC-line name to amount of conductors.
    conductor_count_dict_expected = {'AAA-BBB': 1,
                                     'CCC-DDD': 1,
                                     'EEE-FFF-1': 2,
                                     'EEE-FFF-2': 1,
                                     'GGG-HHH': 1,
                                     'III-ÆØÅ': 1}
    assert data_parse_result.get_conductor_count_dict() == conductor_count_dict_expected

    # Test mapping from AC-line name to amount of parallel systems.
    system_count_dict_expected = {'AAA-BBB': 2,
                                  'CCC-DDD': 1,
                                  'EEE-FFF-1': 1,
                                  'EEE-FFF-2': 1,
                                  'GGG-HHH': 2,
                                  'III-ÆØÅ': 1}
    assert data_parse_result.get_system_count_dict() == system_count_dict_expected

    # Test mapping from AC-line name to conductor type.
    conducter_type_dict_expected = {'AAA-BBB': 'Conduck',
                                    'CCC-DDD': 'Conduck',
                                    'EEE-FFF-1': 'Conduck',
                                    'EEE-FFF-2': 'Conduck',
                                    'GGG-HHH': 'Conduck',
                                    'III-ÆØÅ': 'Conduck'}
    assert data_parse_result.get_conductor_type_dict() == conducter_type_dict_expected

    # Test mapping from AC-line name to max temperature.
    max_temperature_dict_expected = {'AAA-BBB': 70,
                                     'CCC-DDD': 70,
                                     'EEE-FFF-1': 70,
                                     'EEE-FFF-2': 70,
                                     'GGG-HHH': 70,
                                     'III-ÆØÅ': 70}
    assert data_parse_result.get_conductor_max_temp_dict() == max_temperature_dict_expected

    # Test mapping from AC-line name to allowed continuous ampere loading of cabling along the AC-line.
    cablelim_continuous_dict_expected = {'AAA-BBB': 800,
                                         'CCC-DDD': nan,
                                         'EEE-FFF-1': 700,
                                         'EEE-FFF-2': 700,
                                         'GGG-HHH': nan,
                                         'III-ÆØÅ': nan}
    assert data_parse_result.get_cablelim_continuous_dict() == cablelim_continuous_dict_expected

    # Test mapping from AC-line name to allowed 15 minutes ampere loading of cabling along the AC-line.
    cablelim_15m_dict_expected = {'AAA-BBB': 1200,
                                  'CCC-DDD': nan,
                                  'EEE-FFF-1': 1100,
                                  'EEE-FFF-2': 1100,
                                  'GGG-HHH': nan,
                                  'III-ÆØÅ': nan}
    assert data_parse_result.get_cablelim_15m_dict() == cablelim_15m_dict_expected

    # Test mapping from AC-line name to allowed 1 hour ampere loading of cabling along the AC-line.
    cablelim_1h_dict_expected = {'AAA-BBB': 1000,
                                 'CCC-DDD': nan,
                                 'EEE-FFF-1': 900,
                                 'EEE-FFF-2': 900,
                                 'GGG-HHH': nan,
                                 'III-ÆØÅ': nan}
    assert data_parse_result.get_cablelim_1h_dict() == cablelim_1h_dict_expected

    # Test mapping from AC-line name to allowed 40 hour ampere loading of cabling along the AC-line.
    cablelim_40h_dict_expected = {'AAA-BBB': 900,
                                  'CCC-DDD': nan,
                                  'EEE-FFF-1': 800,
                                  'EEE-FFF-2': 800,
                                  'GGG-HHH': nan,
                                  'III-ÆØÅ': nan}
    assert data_parse_result.get_cablelim_40h_dict() == cablelim_40h_dict_expected


def test_DD20LineDataframeParser(dd20_data_frame_dict):
    """
    This test verfies that all DD20 "line" can be parsed correctly.
    """

    # arrange data needed for tests
    df_linedata = dd20_data_frame_dict[DD20_SHEETNAME_LINJEDATA]
    data_parse_result = DD20LineDataframeParser(df_line=df_linedata)

    # Test dataframe has expected amount of datarows
    df_row_count_expected = 29
    assert len(df_linedata.index) == df_row_count_expected

    # Test acline name list contain expected names
    acline_list_expected = ['AAA-BBB',
                            'CCC-DDD',
                            'EEE-FFF-1',
                            'EEE-FFF-2',
                            'GGG-HHH',
                            'III-ÆØÅ']
    assert data_parse_result.acline_name_list == acline_list_expected

    # Test mapping from AC-line name to voltagelevel in kV.
    conductor_kv_level_dict_expected = {'AAA-BBB': 150,
                                        'CCC-DDD': 220,
                                        'EEE-FFF-1': 132,
                                        'EEE-FFF-2': 132,
                                        'GGG-HHH': 132,
                                        'III-ÆØÅ': 400}
    assert data_parse_result.get_conductor_kv_level_dict() == conductor_kv_level_dict_expected

    # Test mapping from AC-line name to allowed continuous ampere loading of conductor.
    acline_lim_continuous_dict_expected = {'AAA-BBB': 1432,
                                           'CCC-DDD': 801,
                                           'EEE-FFF-1': 1168,
                                           'EEE-FFF-2': 1131,
                                           'GGG-HHH': 1624,
                                           'III-ÆØÅ': 2413}
    assert data_parse_result.get_acline_lim_continuous_dict() == acline_lim_continuous_dict_expected

    # Test mapping from AC-line name to allowed continuous ampere loading of components along the AC-line.
    complim_continuous_dict_expected = {'AAA-BBB': 1600,
                                        'CCC-DDD': 1200,
                                        'EEE-FFF-1': 400,
                                        'EEE-FFF-2': 1200,
                                        'GGG-HHH': 100,
                                        'III-ÆØÅ': 2400}
    assert data_parse_result.get_complim_continuous_dict() == complim_continuous_dict_expected

    # Test mapping from AC-line name to allowed 15 minutes ampere loading of components along the AC-line.
    complim_15m_dict_expected = {'AAA-BBB': 1600,
                                 'CCC-DDD': 1200,
                                 'EEE-FFF-1': 415,
                                 'EEE-FFF-2': 1200,
                                 'GGG-HHH': 115,
                                 'III-ÆØÅ': 2400}
    assert data_parse_result.get_complim_15m_dict() == complim_15m_dict_expected

    # Test mapping from AC-line name to allowed 1 hour ampere loading of components along the AC-line.
    complim_1h_dict_expected = {'AAA-BBB': 1600,
                                'CCC-DDD': 1200,
                                'EEE-FFF-1': 460,
                                'EEE-FFF-2': 1200,
                                'GGG-HHH': 160,
                                'III-ÆØÅ': 2400}
    assert data_parse_result.get_complim_1h_dict() == complim_1h_dict_expected

    # Test mapping from AC-line name to allowed 40 hour ampere loading of components along the AC-line.
    complim_40h_dict_expected = {'AAA-BBB': 1600,
                                 'CCC-DDD': 1200,
                                 'EEE-FFF-1': 440,
                                 'EEE-FFF-2': 1200,
                                 'GGG-HHH': 140,
                                 'III-ÆØÅ': 2400}
    assert data_parse_result.get_complim_40h_dict() == complim_40h_dict_expected

# test combined DD20 dataframe eller blot objekter hver for sig, eller begge?


# TEST: map parse
# expected_dd20_to_scada_name_dict = {'E_EEE-FFF_1': 'E_EEEV-FFF_1'} - given E_EEE-FFF_1 then E_EEEV-FFF_1
def test_parse_acline_namemap_excelsheet_to_dataframe():
    """
    This test verfies that Excel file with AC-line name mapping is parsed correcrtly
    """
    # expected dataframe
    expected_acline_namemap_dict = {'DD20 Name': ['E_EEE-FFF_1'],
                                    'ETS Name': ['E_EEEV-FFF_1'],
                                    'Comment': ['andet navn i ETS. Forkert model.'],
                                    'User': ['AWI']}
    expected_acline_namemap_dataframe = pd.DataFrame.from_dict(expected_acline_namemap_dict)

    # resulting dataframe from valid testfile
    name_mapping_filepath =  f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/Limits_other.xlsx"
    resulting_acline_namemap_dataframe = parse_acline_namemap_excelsheet_to_dataframe(file_path=name_mapping_filepath)

    # assert
    assert resulting_acline_namemap_dataframe.equals(expected_acline_namemap_dataframe)




# TEST: mrid parse
def test_parse_aclineseg_scada_csvdata_to_dataframe():
    """
    This test verfies that CSV file with aclineseg mapping is parsed correcrtly
    """
    # expected dataframe
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

    # resulting dataframe from valid testfile
    mrid_mapping_filepath =  f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/seg_line_mrid_PROD.csv"
    resulting_lineseg_to_mrid_dataframe = parse_aclineseg_scada_csvdata_to_dataframe(file_path=mrid_mapping_filepath)

    # assert
    assert resulting_lineseg_to_mrid_dataframe.equals(expected_lineseg_to_mrid_dataframe)



# TEST final merge
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


"""
# TODO: add negative test with invalid data also
def test_extract_conductor_data_from_dd20():

    DD20_FILE = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/"

    # Input is DD20 file. Output is pandas datafram with conductor data (needed data in format below).

    dd20_dataframe_dict = app.helpers.excel_sheet_handler.parse_excel_sheets_to_dataframe_dict(file_path=DD20_FILE,
                                                                    sheets=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
                                                                    header_index=[1])
    df_station, df_line = app.helpers.parse_dd20.parse_dd20_excelsheets_to_dataframes(folder_path=DD20_FILE)

    data_station = app.helpers.parse_dd20.DD20StationDataframeParser(df_station=df_station)

    data_line = app.helpers.parse_dd20.DD20LineDataframeParser(df_line=df_line)

    obj = app.helpers.parse_dd20.DD20_to_acline_properties_mapper(data_station=data_station, data_line=data_line)

    resulting_dd20_dataframe = pd.DataFrame(data=[o.__dict__ for o in obj])

    print(resulting_dd20_dataframe.to_string())
    print(expected_dd20_dataframe.to_string())

    assert resulting_dd20_dataframe.equals(expected_dd20_dataframe)

"""

"""
def test_create_dlr_dataframe():
    resulting_dlr_dataframe = app.main.create_dlr_dataframe(conductor_dataframe=expected_dd20_dataframe,
                                                            dd20_to_scada_name=expected_dd20_to_scada_name_dict,
                                                            lineseg_to_mrid_dataframe=expected_lineseg_to_mrid_dataframe)

    print(resulting_dlr_dataframe.to_string())
    print(expected_dlr_dataframe.to_string())

    assert resulting_dlr_dataframe.equals(expected_dlr_dataframe)
"""


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
