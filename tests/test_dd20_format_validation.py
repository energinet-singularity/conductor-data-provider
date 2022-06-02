"""
Tests for validating dd20 format by calculating a checksum / hash value
"""

import pandas as pd
import os

import pytest

import app.helpers.dd20_format_validation as validators

from  app.helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe


STATION_DATA_SHEET_NAME = "Stationsdata"
LINE_DATA_SHEET_NAME = "Linjedata - Sommer"

@pytest.fixture
def dd20_data_frames():
    dd20_file_path = (
        f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DD20.XLSM"
    )
    sheets = [STATION_DATA_SHEET_NAME, LINE_DATA_SHEET_NAME]
    header_index = 1

  # Parsing data from DD20 to dataframe dictionary, with mapping from sheet to dataframe
    dd20_dataframes = pd.read_excel(
        io=dd20_file_path,
        sheet_name=sheets,
        header=header_index,
    )
    return dd20_dataframes

def test_can_validate_dd20_line_data_summer_format(dd20_data_frames):

    expected_hash = "eb087129d0c2413ee9768957c2c847ae"

    dd20_line_data_summer_data_frame = dd20_data_frames[LINE_DATA_SHEET_NAME]

    _hash = validators.calculate_dd20_format_hash(dd20_line_data_summer_data_frame)

    assert _hash == expected_hash

    assert validators.validate_dd20_format(
        dd20_line_data_summer_data_frame, expected_hash
    )

def test_can_validate_dd20_line_data_station_format(dd20_data_frames):

    expected_hash = "91006da47706518d76724105a97dfb61"

    dd20_line_data_station_data_frame = dd20_data_frames[STATION_DATA_SHEET_NAME]

    _hash = validators.calculate_dd20_format_hash(dd20_line_data_station_data_frame)

    assert _hash == expected_hash

    assert validators.validate_dd20_format(
        dd20_line_data_station_data_frame, expected_hash
    )