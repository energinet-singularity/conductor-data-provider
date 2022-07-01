"""
Tests for validating dd20 format by calculating a checksum / hash value
"""
import os
from sys import path
# Ugly hack to allow absolute import from the root folder
# whatever its name is. Please forgive the heresy.
path.append(os.path.join(os.path.split(os.path.split(__file__)[0])[0], "app"))

import pandas as pd
import pytest
import helpers.dd20_format_validation as validators
from helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from app.configuration import DD20Settings

STATION_DATA_SHEET_NAME = "Stationsdata"
LINE_DATA_SHEET_NAME = "Linjedata - Sommer"


@pytest.fixture
def dd20_data_frames() -> pd.DataFrame:

    settings = DD20Settings()

    dd20_file_path = (
        f"{os.path.dirname(os.path.realpath(__file__))}/{settings.mock_dd20_filepath}"
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
    expected_hash = "86e61101fa327e1b4f769c26300be01f"
    dd20_line_data_summer_data_frame = dd20_data_frames[LINE_DATA_SHEET_NAME]
    _hash = validators.calculate_dd20_format_hash(dd20_line_data_summer_data_frame)

    assert _hash == expected_hash
    assert validators.validate_dd20_format(
        dd20_line_data_summer_data_frame, expected_hash
    )


def test_can_validate_dd20_station_data_format(dd20_data_frames):
    expected_hash = "94d5d5019d83350980b49e884159b215"

    dd20_line_data_station_data_frame = dd20_data_frames[STATION_DATA_SHEET_NAME]
    _hash = validators.calculate_dd20_format_hash(dd20_line_data_station_data_frame)

    assert _hash == expected_hash
    assert validators.validate_dd20_format(
        dd20_line_data_station_data_frame, expected_hash
    )
