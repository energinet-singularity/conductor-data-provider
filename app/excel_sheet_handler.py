# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def parse_excel_sheets_to_dataframe_dict(file_path: str, sheets: list, header_index: int = 0) -> dict:
    """Read sheets from excel file and parse them to a dictionary of pandas dataframes.

    Parameters
    ----------
    file_path : str
        Full path of the excel file.
    sheets : str
        List with names of sheets in excel.
    header_index : int
        Index number for row to be used as header on sheets (Default = 0)

    Returns
    -------
    dict
        A dict of dataframes containing the data from excel sheet.
        The dictionary key will be name of sheet.
    """
    # try to read data from excel file to dataframe.
    try:
        dataframe = pd.read_excel(io=file_path, sheet_name=sheets, header=header_index)
        log.info(f"Excel data from sheet(s): '{sheets}' in: '{file_path}' was parsed to dataframe dictionary.")
    except Exception as e:
        log.exception(f"Parsing data from sheet(s): '{sheets}' in excel file: '{file_path}' failed with message: '{e}'.")
        raise e

    return dataframe
