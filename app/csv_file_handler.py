# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


# TODO: lav line remove som parm
def parse_csv_file_to_dataframe(file_path: str, header_index: int = 0) -> pd.DataFrame:
    '''
    Read CSV file and parse it to pandas dataframe.
    Note. Line number 2 in the CSV file will be removed.
    Parameters
    ----------
    file_path: str
        Full path of the excel file.
    header_index: int
        Index number for row to be used as header (Default = 0)
    Returns
    -------
        pd.DataFrame
            A dataframe containing the data from csv file.
    '''
    # Trying to read data from CSV file and convert it to a dataframe.
    try:
        dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip',
                                header=header_index)
        dataframe.drop(dataframe.head(1).index, inplace=True)
        log.info(f'CSV data from "{file_path}" was parsed to dataframe.')
    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        raise e

    return dataframe
