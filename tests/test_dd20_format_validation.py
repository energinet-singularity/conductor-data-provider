"""
Tests for validating dd20 format by calculating a checksum / hash value
"""

# from pickle import TRUE
import pandas as pd
import os

import pytest

import app.helpers.dd20_format_validation as validators

from  app.helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe


@pytest.fixture
def dd20_data_frames():
    dd20_file_path = (
        f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DD20.XLSM"
    )
    sheets = ["Stationsdata", "Linjedata - Sommer"]
    header_index = 0

  # Parsing data from DD20 to dataframe dictionary, with mapping from sheet to dataframe
    dd20_dataframes = pd.read_excel(
        io=dd20_file_path,
        sheet_name=sheets,
        header=header_index,
    )
    return dd20_dataframes

def test_can_validate_dd20_line_data_summer_format(dd20_data_frames):

    expected_hash = "9cf51349b6b13d3c52deb66bf569eb49"

    dd20_line_data_summer_data_frame = dd20_data_frames["Linjedata - Sommer"]

    _hash = validators.calculate_dd20_format_hash(dd20_line_data_summer_data_frame)

    assert _hash == expected_hash

    assert validators.validate_dd20_format(
        dd20_line_data_summer_data_frame, expected_hash
    )

def test_can_validate_dd20_line_data_station_format(dd20_data_frames):

    expected_hash = "f06edffbc927aea71f0a501f520cf583"

    dd20_line_data_station_data_frame = dd20_data_frames["Stationsdata"]

    _hash = validators.calculate_dd20_format_hash(dd20_line_data_station_data_frame)

    assert _hash == expected_hash

    assert validators.validate_dd20_format(
        dd20_line_data_station_data_frame, expected_hash
    )