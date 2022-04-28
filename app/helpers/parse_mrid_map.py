# Generic modules
import logging

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


def extract_lineseg_to_mrid_dataframe(folder_path: str, file_name: str = "seg_line_mrid.csv") -> pd.DataFrame:
    """
    TODO: doc
    """

    file_path = folder_path + file_name

    try:
        lineseg_to_mrid_dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip', header=0)
        lineseg_to_mrid_dataframe.drop(lineseg_to_mrid_dataframe.head(1).index, inplace=True)

        # TODO set these somewhere else
        MRIDMAP_EXPECTED_COLS = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

        # focing type, make with dataclass instead?
        lineseg_to_mrid_dataframe = lineseg_to_mrid_dataframe.astype({'DLR_ENABLED': 'bool'})

        """
        verify_dataframe_columns(dataframe=lineseg_to_mrid_dataframe,
                                expected_columns=MRIDMAP_EXPECTED_COLS,
                                allow_extra_columns=True)"""

        log.info(f'CSV data from "{file_path}" was parsed to dataframe.')
        return lineseg_to_mrid_dataframe

    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        raise e
