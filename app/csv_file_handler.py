# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def parse_csv_file_to_dataframe(file_path: str, header_index: int = 0, drop_line_index: int = None) -> pd.DataFrame:
    '''
    Read CSV file and parse it to pandas dataframe.
    Will drop line from csv-file with number 'drop_line_index' if it is set.

    Parameters
    ----------
    file_path: str
        Full path of the excel file.
    header_index: int
        Index number for row to be used as header (Default = 0)
    drop_line_index: int
        Index number for row to be dropped from csv-file (Default = None)

    Returns
    -------
        pd.DataFrame
            A dataframe containing the data from csv file.
    '''
    # Trying to read data from CSV file and convert it to a dataframe.
    try:
        dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip',
                                header=header_index)
        if drop_line_index:
            dataframe.drop(dataframe.head(drop_line_index).index, inplace=True)

        log.info(f'CSV data from "{file_path}" was parsed to dataframe.')
    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        raise e

    return dataframe
