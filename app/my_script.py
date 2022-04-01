import sys
import json
import logging
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)

DLR_MRID_FILEPATH = '/home/tsp/github/conduck/tests/valid-testdata/DLR_MRID.csv'
MRID_KEY_NAME = 'terminal_name'
MRID_VALUE_NAME = 'segment_id'
MRID_EXPECTED_HEADER_NAMES = ['terminal_name', 'far_near', 'measurement_id', 'segment_id', 'dlr_enable']

LIMITS_NAME_FILEPATH = '/home/tsp/github/conduck/tests/valid-testdata/Limits_other.xlsx'
DD20_DATASHEET_NAME = 'DD20Mapping'
DD20_KEY_NAME = 'DD20 Name'
DD20_VALUE_NAME = 'ETS Name'


def parse_csv_file_to_dataframe(file_path: str, header_index: int = 0) -> pd.DataFrame:
    '''
    Read CSV file and parse it to pandas dataframe.
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
        dataframe = pd.read_csv(file_path, delim_whitespace=True, on_bad_lines='skip',
                                header=header_index)
        log.info(f'CSV data in "{file_path}" was parsed to dataframe.')
    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        sys.exit(1)

    return dataframe


def shaping_mrid_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:

    # Cleaning dataset after dataframe import, specific usecase for the project
    dataframe.drop(dataframe.head(1).index, inplace=True)
    dataframe.drop(dataframe.tail(1).index, inplace=True)

    return dataframe


def define_dictonary_from_two_columns_in_a_dataframe(dataframe: pd.DataFrame, dict_key: str,
                                                     dict_value: str) -> dict:
    '''
    Read dataframe and parse it to dictonary.
    Parameters
    ----------
    dataframe: pd.DataFrame
        Dataframe to convert.
    dict_key: str
        Column name to be used as key for the dictonary
    dict_value: str
        Column name to be used as value for the dictonary
    Returns
    -------
        Dictonary
            A dictonary with the key/value specified by the user.
    '''
    # Checking the dictonary key and value to ensure that the user input is found in the dataframe.
    if dict_key not in dataframe:
        log.exception(f'The column "{dict_key}" is not found in the dataframe, check "dict_key" input to the function.')
        sys.exit(1)

    if dict_value not in dataframe:
        log.exception(f'The column "{dict_value}" is not found in the dataframe, check "dict_value" input to the function.')
        sys.exit(1)

    # Converting dataframe into a dictonary using user input to set key and value of the dictonary.
    try:
        dict_set = dataframe.set_index(dict_key).to_dict()[dict_value]
        log.info(f'Dataframe was parsed to a dictonary with the key: "{dict_key}" and the value: "{dict_value}".')
        log.debug(json.dumps(dict_set, indent=4, ensure_ascii=False))

    except Exception as e:
        log.exception(f'Trying to create dictonary failed with message: {e}')

    return dict_set


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s - %(message)s')
    log.setLevel(logging.INFO)

    # Parsing data from MRID csv file
    mrid_dataframe = parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)

    # Cleaning dataframe for unwanted columns and rows
    mrid_clean_dataframe = shaping_mrid_dataframe(mrid_dataframe)

    # Use the verify_dataframe_columns_naming from AWI part of the assignment before to dictonary function
    # Verifying columns on data from MRID file
    # INSERT FUNCTION CALL HERE

    # Converting MRID dataframe to a dictonary
    mrid_dictonary = define_dictonary_from_two_columns_in_a_dataframe(mrid_clean_dataframe, MRID_KEY_NAME, MRID_VALUE_NAME)

    # Replace the following import with the correct import function
    dd20_dataframe = pd.read_excel(io=LIMITS_NAME_FILEPATH, sheet_name=DD20_DATASHEET_NAME)

    # Use the verify_dataframe_columns_naming from AWI part of the assignment before to dictonary function
    # Verifying columns on data from DD20 file
    # INSERT FUNCTION CALL HERE

    # Converting DD20 dataframe to a dictonary
    dd20_dictonary = define_dictonary_from_two_columns_in_a_dataframe(dd20_dataframe, DD20_KEY_NAME, DD20_VALUE_NAME)
