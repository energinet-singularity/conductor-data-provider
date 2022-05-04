# Generic modules
import logging

# Modules
from singupy.verification import dataframe_columns
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def parse_aclineseg_scada_csvdata_to_dataframe(folder_path: str,
                                               file_name: str = "seg_line_mrid_PROD.csv",
                                               aclinesegment_mrid_col_nm: str = "ACLINESEGMENT_MRID",
                                               acline_name_col_nm: str = "LINE_EMSNAME",
                                               dlr_enabled_col_nm: str = "DLR_ENABLED") -> pd.DataFrame:
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
    aclinesegment_mrid_col_nm : str
        (optional) Name of column which contains ACLineSegment MRID.
        Default = "ACLINESEGMENT_MRID"
    acline_name_col_nm: str
        (optional) Name of column which contains Line Name.
        Default = "LINE_EMSNAME"
    dlr_enabled_col_nm : str
        (optional) Name of column which contains DLR enabled flag.
        Default = "DLR_ENABLED"  
    Returns
    -------
    pd.Dataframe
        Dataframe containg data from CSV-file.
    """

    file_path = folder_path + file_name

    # process data from csv file til dataframe
    try:
        # read data from CSV to dataframe and drop row with index 1 as it contains only hyphnens
        aclineseg_scada_dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip', encoding='cp1252')
        aclineseg_scada_dataframe.drop(aclineseg_scada_dataframe.head(1).index, inplace=True)

        # replace yes/no with true/false
        aclineseg_scada_dataframe.loc[aclineseg_scada_dataframe[dlr_enabled_col_nm] == "YES", dlr_enabled_col_nm] = True
        aclineseg_scada_dataframe.loc[aclineseg_scada_dataframe[dlr_enabled_col_nm] == "NO", dlr_enabled_col_nm] = False

        # set type on 'DLR_enabled' column to boolean datatype
        aclineseg_scada_dataframe = aclineseg_scada_dataframe.astype({dlr_enabled_col_nm: bool})

        # verify that expected columns are present
        dataframe_columns(dataframe=aclineseg_scada_dataframe,
                          expected_columns= [aclinesegment_mrid_col_nm, acline_name_col_nm, dlr_enabled_col_nm],
                          allow_extra_columns=True)

        log.info(f'AC-linsegment csv-data from "{file_path}" was parsed to dataframe.')
        log.debug(f"Data from csv-file {file_path} is: {aclineseg_scada_dataframe.to_string()}")

        return aclineseg_scada_dataframe

    except Exception as e:
        log.exception(f'Parsing AC-insegment csv-data from: "{file_path}" failed with message: {e}.')
        raise e
