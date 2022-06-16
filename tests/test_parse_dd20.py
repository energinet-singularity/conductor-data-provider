import pandas as pd
from numpy import nan
from deepdiff import DeepDiff
import os
import pytest

from sys import path
# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
path.append(os.path.join(os.path.split(os.path.split(__file__)[0])[0], "app"))

# App modules
from helpers.parse_dd20 import (
    DD20StationDataframeParser,
    DD20LineDataframeParser,
    parse_dd20_excelsheets_to_dataframe,
)


# Global parameters
DD20_HEADER_INDEX = 1
DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"
DD20_FILE_PATH = (
    f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DD20.XLSM"
)


# fixture for DD20
@pytest.fixture
def dd20_data():
    return pd.read_excel(
        io=DD20_FILE_PATH,
        sheet_name=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
        header=DD20_HEADER_INDEX,
    )


# expected DD20 values as list and dictionarys
expected_acline_datasource_names = [
    "AAA-BBB",
    "CCC-DDD",
    "EEE-FFF-1",
    "EEE-FFF-2",
    "GGG-HHH",
    "III-ÆØÅ",
]
expected_conductor_kv_level = {
    "AAA-BBB": 150,
    "CCC-DDD": 220,
    "EEE-FFF-1": 132,
    "EEE-FFF-2": 132,
    "GGG-HHH": 132,
    "III-ÆØÅ": 400,
}
expected_conductor_count = {
    "AAA-BBB": 1,
    "CCC-DDD": 1,
    "EEE-FFF-1": 2,
    "EEE-FFF-2": 1,
    "GGG-HHH": 1,
    "III-ÆØÅ": 1,
}
expected_system_count = {
    "AAA-BBB": 2,
    "CCC-DDD": 1,
    "EEE-FFF-1": 1,
    "EEE-FFF-2": 1,
    "GGG-HHH": 2,
    "III-ÆØÅ": 1,
}
expected_conductor_type = {
    "AAA-BBB": "Conduck",
    "CCC-DDD": "Conduck",
    "EEE-FFF-1": "Conduck",
    "EEE-FFF-2": "Conduck",
    "GGG-HHH": "Conduck",
    "III-ÆØÅ": "Conduck",
}
expected_max_temperature = {
    "AAA-BBB": 70,
    "CCC-DDD": 70,
    "EEE-FFF-1": 70,
    "EEE-FFF-2": 70,
    "GGG-HHH": 70,
    "III-ÆØÅ": 70,
}
expected_cablelim_continuous = {
    "AAA-BBB": 800,
    "CCC-DDD": nan,
    "EEE-FFF-1": 700,
    "EEE-FFF-2": 700,
    "GGG-HHH": nan,
    "III-ÆØÅ": nan,
}
expected_cablelim_15m = {
    "AAA-BBB": 1200,
    "CCC-DDD": nan,
    "EEE-FFF-1": 1100,
    "EEE-FFF-2": 1100,
    "GGG-HHH": nan,
    "III-ÆØÅ": nan,
}
expected_cablelim_1h = {
    "AAA-BBB": 1000,
    "CCC-DDD": nan,
    "EEE-FFF-1": 900,
    "EEE-FFF-2": 900,
    "GGG-HHH": nan,
    "III-ÆØÅ": nan,
}
expected_cablelim_40h = {
    "AAA-BBB": 900,
    "CCC-DDD": nan,
    "EEE-FFF-1": 800,
    "EEE-FFF-2": 800,
    "GGG-HHH": nan,
    "III-ÆØÅ": nan,
}
expected_acline_lim_continuous = {
    "AAA-BBB": 1432,
    "CCC-DDD": 801,
    "EEE-FFF-1": 1168,
    "EEE-FFF-2": 1131,
    "GGG-HHH": 1624,
    "III-ÆØÅ": 2413,
}
expected_complim_continuous = {
    "AAA-BBB": 1600,
    "CCC-DDD": 1200,
    "EEE-FFF-1": 400,
    "EEE-FFF-2": 1200,
    "GGG-HHH": 100,
    "III-ÆØÅ": 2400,
}
expected_complim_15m = {
    "AAA-BBB": 1600,
    "CCC-DDD": 1200,
    "EEE-FFF-1": 415,
    "EEE-FFF-2": 1200,
    "GGG-HHH": 115,
    "III-ÆØÅ": 2400,
}
expected_complim_1h = {
    "AAA-BBB": 1600,
    "CCC-DDD": 1200,
    "EEE-FFF-1": 460,
    "EEE-FFF-2": 1200,
    "GGG-HHH": 160,
    "III-ÆØÅ": 2400,
}
expected_complim_40h = {
    "AAA-BBB": 1600,
    "CCC-DDD": 1200,
    "EEE-FFF-1": 440,
    "EEE-FFF-2": 1200,
    "GGG-HHH": 140,
    "III-ÆØÅ": 2400,
}
expected_datasource = {
    "AAA-BBB": "DD20",
    "CCC-DDD": "DD20",
    "EEE-FFF-1": "DD20",
    "EEE-FFF-2": "DD20",
    "GGG-HHH": "DD20",
    "III-ÆØÅ": "DD20",
}
expected_translated_acline_names = {
    "AAA-BBB": "E_AAA-BBB",
    "CCC-DDD": "D_CCC-DDD",
    "EEE-FFF-1": "E_EEE-FFF_1",
    "EEE-FFF-2": "E_EEE-FFF_2",
    "GGG-HHH": "E_GGG-HHH",
    "III-ÆØÅ": "C_III-ÆØÅ",
}


def test_DD20StationDataframeParser(dd20_data):
    """
    Verfies that all DD20 "station" data are parsed correctly.
    """

    # arrange dd20 dataframe needed for tests
    df_stationdata = dd20_data[DD20_SHEETNAME_STATIONSDATA]

    # Parsing dataframe
    data_parse_result = DD20StationDataframeParser(df_station=df_stationdata)

    # Test dataframe has expected amount of datarows
    df_row_count_expected = 12
    assert len(df_stationdata.index) == df_row_count_expected

    # Test acline name list contain expected names
    assert data_parse_result.acline_name_list == expected_acline_datasource_names

    # Test mapping from AC-line name to voltagelevel in kV.
    assert (
        data_parse_result.get_conductor_kv_level_dict() == expected_conductor_kv_level
    )

    # Test mapping from AC-line name to amount of conductors.
    assert data_parse_result.get_conductor_count_dict() == expected_conductor_count

    # Test mapping from AC-line name to amount of parallel systems.
    assert data_parse_result.get_system_count_dict() == expected_system_count

    # Test mapping from AC-line name to conductor type
    assert data_parse_result.get_conductor_type_dict() == expected_conductor_type

    # Test mapping from AC-line name to max temperature.
    assert data_parse_result.get_conductor_max_temp_dict() == expected_max_temperature

    # Test mapping from AC-line name to allowed continuous ampere loading of cabling along the AC-line.
    assert (
        data_parse_result.get_cablelim_continuous_dict() == expected_cablelim_continuous
    )

    # Test mapping from AC-line name to allowed 15 minutes ampere loading of cabling along the AC-line.
    assert data_parse_result.get_cablelim_15m_dict() == expected_cablelim_15m

    # Test mapping from AC-line name to allowed 1 hour ampere loading of cabling along the AC-line.
    assert data_parse_result.get_cablelim_1h_dict() == expected_cablelim_1h

    # Test mapping from AC-line name to allowed 40 hour ampere loading of cabling along the AC-line.
    assert data_parse_result.get_cablelim_40h_dict() == expected_cablelim_40h


def test_DD20LineDataframeParser(dd20_data):
    """
    Verfies that all DD20 "line" data are parsed correctly.
    """

    # arrange dd20 dataframe needed for tests
    df_linedata = dd20_data[DD20_SHEETNAME_LINJEDATA]

    # Parsing dataframe
    data_parse_result = DD20LineDataframeParser(df_line=df_linedata)

    # Test dataframe has expected amount of datarows
    df_row_count_expected = 29
    assert len(df_linedata.index) == df_row_count_expected

    # Test acline name list contain expected names
    assert data_parse_result.acline_name_list == expected_acline_datasource_names

    # Test mapping from AC-line name to voltagelevel in kV.
    assert (
        data_parse_result.get_conductor_kv_level_dict() == expected_conductor_kv_level
    )

    # Test mapping from AC-line name to allowed continuous ampere loading of conductor.
    assert (
        data_parse_result.get_acline_lim_continuous_dict()
        == expected_acline_lim_continuous
    )

    # Test mapping from AC-line name to allowed continuous ampere loading of components along the AC-line.
    assert (
        data_parse_result.get_complim_continuous_dict() == expected_complim_continuous
    )

    # Test mapping from AC-line name to allowed 15 minutes ampere loading of components along the AC-line.
    assert data_parse_result.get_complim_15m_dict() == expected_complim_15m

    # Test mapping from AC-line name to allowed 1 hour ampere loading of components along the AC-line.
    assert data_parse_result.get_complim_1h_dict() == expected_complim_1h

    # Test mapping from AC-line name to allowed 40 hour ampere loading of components along the AC-line.
    assert data_parse_result.get_complim_40h_dict() == expected_complim_40h


# test combined DD20 dataframe
def test_parse_dd20_excelsheets_to_dataframe(dd20_data):
    """
    Verifies DD20 dataframe contains expected data
    """
    # Constans for holding expected column names of dataframe
    ACLINE_NAME_TRANSLATED_COL_NM = "acline_name_translated"
    ACLINE_NAME_DATASOURCE_COL_NM = "acline_name_datasource"
    DATASOURCE_COL_NM = "datasource"
    CONDUCTOR_TYPE_COL_NM = "conductor_type"
    CONDUCTOR_COUNT_COL_NM = "conductor_count"
    SYSTEM_COUNT_COL_NM = "system_count"
    MAX_TEMPERATUR_COL_NM = "max_temperature"
    RESTRICT_CONDUCTOR_LIM_CONTINIOUS = "restrict_conductor_lim_continuous"
    RESTRICT_COMPONENT_LIM_CONTINIOUS = "restrict_component_lim_continuous"
    RESTRICT_COMPONENT_LIM_15M = "restrict_component_lim_15m"
    RESTRICT_COMPONENT_LIM_1H = "restrict_component_lim_1h"
    RESTRICT_COMPONENT_LIM_40H = "restrict_component_lim_40h"
    RESTRICT_CABLE_LIM_CONTINUOUS = "restrict_cable_lim_continuous"
    RESTRICT_CABLE_LIM_15M = "restrict_cable_lim_15m"
    RESTRICT_CABLE_LIM_1H = "restrict_cable_lim_1h"
    RESTRICT_CABLE_LIM_40H = "restrict_cable_lim_40h"

    # arrange expected columns in dataframe
    expected_dd20_dataframe_columns = [
        ACLINE_NAME_TRANSLATED_COL_NM,
        ACLINE_NAME_DATASOURCE_COL_NM,
        DATASOURCE_COL_NM,
        CONDUCTOR_TYPE_COL_NM,
        CONDUCTOR_COUNT_COL_NM,
        SYSTEM_COUNT_COL_NM,
        MAX_TEMPERATUR_COL_NM,
        RESTRICT_CONDUCTOR_LIM_CONTINIOUS,
        RESTRICT_COMPONENT_LIM_CONTINIOUS,
        RESTRICT_COMPONENT_LIM_15M,
        RESTRICT_COMPONENT_LIM_1H,
        RESTRICT_COMPONENT_LIM_40H,
        RESTRICT_CABLE_LIM_CONTINUOUS,
        RESTRICT_CABLE_LIM_15M,
        RESTRICT_CABLE_LIM_1H,
        RESTRICT_CABLE_LIM_40H,
    ]

    # parse data
    resulting_dd20_dataframe = parse_dd20_excelsheets_to_dataframe(
        file_path=DD20_FILE_PATH
    )
    resulting_dd20_dataframe_columns = resulting_dd20_dataframe.columns.to_list()
    resulting_acline_name_datasource = resulting_dd20_dataframe[
        ACLINE_NAME_DATASOURCE_COL_NM
    ].values.tolist()

    # Test if expect amount of columns are present
    assert len(resulting_dd20_dataframe_columns) == len(expected_dd20_dataframe_columns)

    # Test if expected column names are present
    assert sorted(resulting_dd20_dataframe_columns) == sorted(
        expected_dd20_dataframe_columns
    )

    # Test dataframe has expected amount of datarows
    df_row_count_expected = 6
    assert len(resulting_dd20_dataframe.index) == df_row_count_expected

    # Test if expected AC-line names are in dataframe
    assert sorted(resulting_acline_name_datasource) == sorted(
        expected_acline_datasource_names
    )

    # Test if columns values of of dataframe are as expected
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            ACLINE_NAME_TRANSLATED_COL_NM
        ]
        == expected_translated_acline_names
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            DATASOURCE_COL_NM
        ]
        == expected_datasource
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            CONDUCTOR_TYPE_COL_NM
        ]
        == expected_conductor_type
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            CONDUCTOR_COUNT_COL_NM
        ]
        == expected_conductor_count
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            SYSTEM_COUNT_COL_NM
        ]
        == expected_system_count
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            MAX_TEMPERATUR_COL_NM
        ]
        == expected_max_temperature
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_CONDUCTOR_LIM_CONTINIOUS
        ]
        == expected_acline_lim_continuous
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_COMPONENT_LIM_CONTINIOUS
        ]
        == expected_complim_continuous
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_COMPONENT_LIM_15M
        ]
        == expected_complim_15m
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_COMPONENT_LIM_1H
        ]
        == expected_complim_1h
    )
    assert (
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_COMPONENT_LIM_40H
        ]
        == expected_complim_40h
    )

    assert not DeepDiff(
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_CABLE_LIM_CONTINUOUS
        ],
        expected_cablelim_continuous,
        ignore_nan_inequality=True,
        ignore_numeric_type_changes=True
    )

    assert not DeepDiff(
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_CABLE_LIM_15M
        ],
        expected_cablelim_15m,
        ignore_nan_inequality=True,
        ignore_numeric_type_changes=True
    )

    assert not DeepDiff(
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_CABLE_LIM_1H
        ],
        expected_cablelim_1h,
        ignore_nan_inequality=True,
        ignore_numeric_type_changes=True
    )

    assert not DeepDiff(
        resulting_dd20_dataframe.set_index(ACLINE_NAME_DATASOURCE_COL_NM).to_dict()[
            RESTRICT_CABLE_LIM_40H
        ],
        expected_cablelim_40h,
        ignore_nan_inequality=True,
        ignore_numeric_type_changes=True
    )
