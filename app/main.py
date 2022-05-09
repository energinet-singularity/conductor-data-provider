# Generic modules
import os
import logging
from time import sleep, time
from dataclasses import dataclass

# Modules
from singupy import api as singuapi
import pandas as pd

# App modules
from helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dataframe
from helpers.parse_mrid_map import parse_aclineseg_scada_csvdata_to_dataframe
from helpers.join_data import create_conductor_dataframe

# Initialize log
log = logging.getLogger(__name__)


class ACLineSegmentProperties():
    """
    Class for managing AC-line conductor properties.

    The purpose of the class is to collect data from the input-files, transform it into dataframes and join
    them all into a single property-set in order to provide conductor data for Dynamic Line Rating calculations
    to be utilized in a SCADA system.

    The conductor properties are gathered from a non-standard format called "DD20"(excel-file) and combined with mapping data
    from non-standard datasources from a SCADA system (excel and csv-file).
    It is done in order to establish link between conductor data from DD20 and SCADA database records.

    Attributes
    ----------
    dataframe : pd.DataFrame
        The ACLineSegment properties in DataFrame format

    Methods
    -------
    refresh_data()
        Reload data from files and update the dataframe if necessary
    """

    @dataclass
    class __Metadata:
        """
        TODO: doc it
        Attributes
        ----------
        name : str
            xxx
        """
        name: str
        path: str
        func: callable
        dataframe: pd.DataFrame = None
        mtime: float = None

    def __init__(self, dd20_filepath: str, dd20_mapping_filepath: str, mrid_mapping_filepath: str, refresh_data: bool = True):
        """
        Create new ACLineSegmentProperties instance.

        Parameters
        ----------
        dd20_filepath : str
            Path of the DD20 excel-file
        dd20_mapping_filepath : str
            Path of the mapping excel-file between DD20 and SCADA names
        mrid_mapping_filepath : str
            Path of the mapping csv-file between Line name and MRID
        refresh_data : bool, default: True
            If True data will automatically be loaded at instantiation
        """
        self.__DD20 = self.__Metadata('DD20', dd20_filepath, parse_dd20_excelsheets_to_dataframe)
        self.__DD20_MAP = self.__Metadata('DD20 name mapping', dd20_mapping_filepath, parse_acline_namemap_excelsheet_to_dataframe)
        self.__MRID_MAP = self.__Metadata('MRID mapping', mrid_mapping_filepath, parse_aclineseg_scada_csvdata_to_dataframe)
        self.dataframe = None

        if refresh_data:
            self.refresh_data()

    def refresh_data(self) -> pd.DataFrame:
        """
        This function will check the input files for updates and reload any changes. If one or more files were
        updated, the combined dataframe will be recalculated.

        The following 3 datasources are processed:
        1. "DD20" excel-file.
            Conductor properties are collected for each AC-line represented in DD20.
            An object for each AC-line is created. All objects are gathered into a dataframe holding all extracted data.
        2. "DD20 name to SCADA AC-line name mapping" excel-file.
            Mapping from DD20 AC-line name to AC-line name used in SCADA system are parsed to a dictionary.
            This is necessary since some AC-line names differ between SCADA and DD20.
        3. "AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system.
            Mapping from AC-line name used in SCADA system to AC-linesegment MRID in SCADA system are parsed to a dataframe.
            The AC-linesegment MRID is a unique identifier, which all conductor data must be linked to.

        Returns
        -------
        pd.DataFrame
            Will return the combined dataframe
        """
        log.info("Checking if files has updated and data refreh is needed.")
        data_change = False

        for input in [self.__DD20, self.__DD20_MAP, self.__MRID_MAP]:
            try:
                file_update_time = os.path.getmtime(input.path)

                if file_update_time != input.mtime:
                    log.info(f"Updating {input.name} file")
                    data_change = True
                    input.mtime = file_update_time
                    input.dataframe = input.func(file_path=input.path)
            except Exception as e:
                log.exception(f"Parsing {input.name} failed with message: '{e}'")
                raise e

        # Combine data into common dataframe
        try:
            if data_change:
                log.info("Files has changed, refreshing data for API.")
                self.dataframe = create_conductor_dataframe(conductor_data=self.__DD20.dataframe,
                                                            dd20_to_scada_name=self.__DD20_MAP.dataframe,
                                                            scada_mapping=self.__MRID_MAP.dataframe)
            else:
                log.info("Files has not changed, refresh of data for API not needed.")
        except Exception as e:
            log.exception(f"Creating dataframe with AC-linesegment properties failed with message: '{e}'")
            raise e

        return self.dataframe


if __name__ == "__main__":

    """
    TODO: doc
    """

    time_begin = time()

    # default values for filepaths
    DD20_FILEPATH_DEFAULT = '/input/DD20.XLSM'
    DD20_MAPPING_FILEPATH_DEFAULT = '/input/Limits_other.xlsx'
    MRID_MAPPING_FILEPATH_DEFAULT = '/input/seg_line_mrid_PROD.csv'
    # TEMP: test data
    DD20_FILEPATH_DEFAULT = f'{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/DD20.XLSM'
    DD20_MAPPING_FILEPATH_DEFAULT = f'{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/Limits_other.xlsx'
    MRID_MAPPING_FILEPATH_DEFAULT = f'{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/seg_line_mrid_PROD.csv'

    # refresh rate for checking if new data is avalialbe from files
    REFRESH_RATE_API_INPUT = 60

    # Set up logging
    if os.environ.get('DEBUG', 'FALSE').upper() == 'FALSE':
        # __main__ will output INFO-level, everything else stays at WARNING
        logging.basicConfig(format="%(levelname)s:%(asctime)s:%(name)s - %(message)s")
        logging.getLogger(__name__).setLevel(logging.INFO)
    elif os.environ['DEBUG'].upper() == 'TRUE':
        # Set EVERYTHING to DEBUG level
        logging.basicConfig(format="%(levelname)s:%(asctime)s:%(name)s - %(message)s", level=logging.DEBUG)
        log.debug('Setting all logs to debug-level')
    else:
        raise ValueError(f"'DEBUG' env. variable is '{os.environ['DEBUG']}', but must be either 'TRUE', 'FALSE' or unset.")

    log.info("Loading environment variables.")

    # Load file paths from env vars - or use defaults
    try:
        dd20_filepath = os.environ.get("DD20FILEPATH", DD20_FILEPATH_DEFAULT)
        dd20_mapping_filepath = os.environ.get("DD20MAPPINGFILEPATH", DD20_MAPPING_FILEPATH_DEFAULT)
        mrid_mapping_filepath = os.environ.get("MRIDMAPPINGFILEPATH", MRID_MAPPING_FILEPATH_DEFAULT)
    except Exception:
        raise ValueError(f"Error while loading one or more file paths.")

    # Set up mocking of data
    if os.environ.get('USE_MOCK_DATA', 'FALSE').upper() == 'FALSE':
        pass
    elif os.environ['USE_MOCK_DATA'].upper() == 'TRUE':
        # Mock-data will overrule file paths
        # TODO: will only work in container, is it ok?
        dd20_filepath = '/test-data/DD20.XLSM'
        dd20_mapping_filepath = '/test-data/Limits_other.xlsx'
        mrid_mapping_filepath = '/test-data/seg_line_mrid_PROD.csv'
    else:
        raise ValueError(f"'USE_MOCK_DATA' env. variable is '{os.environ['USE_MOCK_DATA']}',"
                         " but must be either 'TRUE', 'FALSE' or unset.")

    # Load environment variables for API
    try:
        api_port = int(os.environ.get('PORT', '5000'))
        api_dbname = os.environ.get('DBNAME', 'CONDUCTOR_DATA').upper()
    except Exception:
        raise ValueError(f"Invalid API config (PORT and/or DBNAME)")

    log.info("Collecting conductor data and exposing via API.")

    conductor_data = ACLineSegmentProperties(dd20_filepath=dd20_filepath, dd20_mapping_filepath=dd20_mapping_filepath,
                                             mrid_mapping_filepath=mrid_mapping_filepath)
    conductor_api = singuapi.DataFrameAPI(conductor_data.dataframe, dbname=api_dbname, port=api_port)
    log.info(f"API initialized on port '{conductor_api.web.port}' with dbname '{api_dbname}'.")
    log.info(f"Started up in {round(time()-time_begin,3)} seconds")

    while True:
        sleep(REFRESH_RATE_API_INPUT)
        conductor_api[api_dbname] = conductor_data.refresh_data()
