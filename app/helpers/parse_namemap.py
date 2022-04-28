# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def extract_namemap_excelsheet_to_dict(folder_path: str, file_name: str = "Limits_other.xlsx") -> dict:
    """
    Extract manual name mapping from excel-sheet and return it to dictionary.
    Mapping is used for names which are not aligned between DD20 and SCADA system.
    """

    # Mapping file parameters
    ACLINE_NAMEMAP_SHEET = 'DD20Mapping'
    ACLINE_NAMEMAP_KEY_NAME = 'DD20 Name'
    ACLINE_NAMEMAP_VALUE_NAME = 'ETS Name'
    ACLINE_NAMEMAP_EXPECTED_COLS = [ACLINE_NAMEMAP_KEY_NAME, ACLINE_NAMEMAP_VALUE_NAME]

    file_path = folder_path + file_name

    try:
        acline_namemap_dataframe = pd.read_excel(file_path, sheet_name=ACLINE_NAMEMAP_SHEET)
        log.info(f"Excel data from sheet: '{ACLINE_NAMEMAP_SHEET}' in: '{file_path}' was parsed to dataframe dictionary.")

        # verifying columns on data from mapping sheet
        # TODO verify columns via lib function
        """verify_dataframe_columns(dataframe=acline_namemap_dataframe,
                                expected_columns=ACLINE_NAMEMAP_EXPECTED_COLS,
                                allow_extra_columns=True)"""

        # creating dictionary for mapping
        return acline_namemap_dataframe.set_index(ACLINE_NAMEMAP_KEY_NAME).to_dict()[ACLINE_NAMEMAP_VALUE_NAME]

    except Exception as e:
        log.exception(f"Parsing data from sheet: '{ACLINE_NAMEMAP_SHEET}' in excel file: '{file_path}' failed with message: '{e}'.")
        raise e
