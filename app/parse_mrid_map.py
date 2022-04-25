# Generic modules
import os
import logging

# Modules
from singupy import api as singuapi
import pandas as pd

# App modules
from voltagelevel_handler import convert_voltage_level_to_letter
from csv_file_handler import parse_csv_file_to_dataframe
from excel_sheet_handler import parse_excel_sheets_to_dataframe_dict
from dataframe_handler import parse_dataframe_columns_to_dictionary, verify_dataframe_columns
from obj_aclinesegment import ACLineCharacteristics

# Initialize log
log = logging.getLogger(__name__)


def extract_lineseg_to_mrid_dataframe() -> pd.DataFrame:
    DLR_MRID_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/seg_line_mrid.csv'
    # DLR_MRID_FILEPATH = os.path.dirname(__file__) + '/../real-data/seg_line_mrid_PROD.csv'
    # TODO verify expected columns

    lineseg_to_mrid_dataframe = parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)

    # TODO set these somewhere else
    MRIDMAP_EXPECTED_COLS = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

    verify_dataframe_columns(dataframe=lineseg_to_mrid_dataframe,
                             expected_columns=MRIDMAP_EXPECTED_COLS,
                             allow_extra_columns=True)

    return lineseg_to_mrid_dataframe
