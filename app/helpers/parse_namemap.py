# Generic modules
import logging

# Modules
from singupy.verification import dataframe_columns
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def parse_acline_namemap_excelsheet_to_dict(folder_path: str, file_name: str = "Limits_other.xlsx") -> dict:
    """
    Extract manual name mapping from excel-sheet and return it to dictionary.
    The name mapping is from "AC-line name in DD20" to "AC-line name in SCADA"
    Mapping is used for names which are not aligned between DD20 and SCADA system.

    An example of the file can be seen in test-data file:
    conduck/tests/valid-testdata/Limits_other.xlsx

    Parameters
    ----------
    folder path : str
        Path where CSV-file is placed.
    file_name : str
        (optional) Name of excel-file.
        Default = "Limits_other.xlsx"

    Returns
    -------
    dict
        Dictionary with mapping from AC-line name in DD20 to AC-line name in SCADA.
    """
    # TODO: move config of constants outside code?
    ACLINE_NAMEMAP_SHEET = 'DD20Mapping'
    ACLINE_NAME_DD20 = 'DD20 Name'
    ACLINE_NAME_SCADA = 'ETS Name'

    file_path = folder_path + file_name

    # proces data frem excel file to dictionary
    try:
        # parse data from excel to dataframe
        acline_namemap_dataframe = pd.read_excel(file_path, sheet_name=ACLINE_NAMEMAP_SHEET)
        log.debug(f"Data from excel-file {file_path} is: {acline_namemap_dataframe.to_string()}")

        # verify that expected columns are present
        dataframe_columns(dataframe=acline_namemap_dataframe,
                          expected_columns=[ACLINE_NAME_DD20, ACLINE_NAME_SCADA],
                          allow_extra_columns=True)

        # create dictionary for mapping
        acline_namemap_dict = acline_namemap_dataframe.set_index(ACLINE_NAME_DD20).to_dict()[ACLINE_NAME_SCADA]
        log.info(f"AC-line name mapping in sheet: '{ACLINE_NAMEMAP_SHEET} of file '{file_path}' was parsed to dictionary.")

        return acline_namemap_dict

    except Exception as e:
        log.exception(f"Parsing AC-line name mapping in sheet: '{ACLINE_NAMEMAP_SHEET} of file '{file_path}' " +
                      f"failed with message: '{e}'.")
        raise e
