# Generic modules
import os
import logging

# App modules
from excel_sheet_handler import parse_excel_sheets_to_dataframe_dict
from dataframe_handler import parse_dataframe_columns_to_dictionary, verify_dataframe_columns

# Initialize log
log = logging.getLogger(__name__)


def extract_namemap_excelsheet_to_dict() -> dict:
    """Extract ....... TODO

    Returns
    -------
    dict : dict
    """
    #
    ACLINE_NAMEMAP_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/Limits_other.xlsx'
    # ACLINE_NAMEMAP_FILEPATH = os.path.dirname(__file__) + '/../real-data/Limits_other.xlsx'
    ACLINE_NAMEMAP_SHEET = 'DD20Mapping'
    ACLINE_NAMEMAP_KEY_NAME = 'DD20 Name'
    ACLINE_NAMEMAP_VALUE_NAME = 'ETS Name'
    ACLINE_NAMEMAP_EXPECTED_COLS = [ACLINE_NAMEMAP_KEY_NAME, ACLINE_NAMEMAP_VALUE_NAME]

    #
    acline_namemap_dataframe = parse_excel_sheets_to_dataframe_dict(file_path=ACLINE_NAMEMAP_FILEPATH,
                                                                    sheets=[ACLINE_NAMEMAP_SHEET],
                                                                    header_index=0)[ACLINE_NAMEMAP_SHEET]

    # verifying columns on data from mapping sheet
    verify_dataframe_columns(dataframe=acline_namemap_dataframe,
                             expected_columns=ACLINE_NAMEMAP_EXPECTED_COLS,
                             allow_extra_columns=True)

    #
    return parse_dataframe_columns_to_dictionary(dataframe=acline_namemap_dataframe,
                                                 dict_key=ACLINE_NAMEMAP_KEY_NAME,
                                                 dict_value=ACLINE_NAMEMAP_VALUE_NAME)
