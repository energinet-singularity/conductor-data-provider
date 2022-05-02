# Generic modules
import logging

# Modules
from singupy.verification import dataframe_columns
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def parse_aclineseg_scada_csvdata_to_dataframe(folder_path: str, file_name: str = "seg_line_mrid.csv") -> pd.DataFrame:
    """
    Parse data from non-standard CSV-file format to dataframe.

    An example of the file can be seen in test-data file:
    "conduck/tests/valid-testdata/seg_line_mrid.csv"

    Parameters
    ----------
    folder path : str
        Path where CSV-file is placed.
    file_name : str
        (optional) Name of CSV-file.
        Default = "seg_line_mrid.csv"

    Returns
    -------
    pd.Dataframe
        Dataframe containg data from CSV-file.
    """
    # TODO: move config of constants outside code?
    CSV_FILE_HEADER_INDEX = 0
    DLR_ENABLED_COL_NM = 'DLR_ENABLED'
    EXPECTED_COLUMNS = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

    file_path = folder_path + file_name

    # process data from csv file til dataframe
    try:
        # read data from CSV to dataframe and drop row with index 1 as it contains only hyphnens
        aclineseg_scada_dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip', header=CSV_FILE_HEADER_INDEX)
        aclineseg_scada_dataframe.drop(aclineseg_scada_dataframe.head(1).index, inplace=True)

        # replace yes/no with true/false
        aclineseg_scada_dataframe.loc[aclineseg_scada_dataframe[DLR_ENABLED_COL_NM] == "YES", DLR_ENABLED_COL_NM] = True
        aclineseg_scada_dataframe.loc[aclineseg_scada_dataframe[DLR_ENABLED_COL_NM] == "NO", DLR_ENABLED_COL_NM] = False

        # set type on 'DLR_enabled' column to boolean datatype
        aclineseg_scada_dataframe = aclineseg_scada_dataframe.astype({DLR_ENABLED_COL_NM: bool})

        # verify that expected columns are present
        dataframe_columns(dataframe=aclineseg_scada_dataframe,
                          expected_columns=EXPECTED_COLUMNS,
                          allow_extra_columns=True)

        log.info(f'AC-linsegment csv-data from "{file_path}" was parsed to dataframe.')
        log.debug(f"Data from csv-file {file_path} is: {aclineseg_scada_dataframe.to_string()}")

        return aclineseg_scada_dataframe

    except Exception as e:
        log.exception(f'Parsing AC-insegment csv-data from: "{file_path}" failed with message: {e}.')
        raise e
