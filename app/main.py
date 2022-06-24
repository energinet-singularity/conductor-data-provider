# Generic modules
import os
import logging
from time import sleep, time
from dataclasses import dataclass
from typing import Union

# Modules
from singupy import api as singuapi
import pandas as pd
from pydantic import ValidationError

# App modules
from configuration import DD20Settings
from helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dataframe
from helpers.parse_mrid_map import parse_aclineseg_scada_csvdata_to_dataframe
from helpers.combine_data import create_aclinesegment_dataframe

# Initialize log
log = logging.getLogger(__name__)


class ACLineSegmentProperties:
    """
    Class for managing AC-line conductor properties.

    The purpose of the class is to collect data from the input-files,
    transform it into dataframes and join them all into a single
    dataframe containing ACLineSegment properties. It is done in order
    to provide conductor data for Dynamic Line Rating calculations to be
    utilized in a SCADA system.

    The conductor properties are gathered from a non-standard format
    called "DD20"(excel-file) and combined with mapping data from non-
    standard datasources from a SCADA system (excel and csv-file). It is
    done in order to establish link between conductor data from DD20 and
    SCADA database records.

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
        name: str
        path: str
        func: callable
        dataframe: pd.DataFrame = None
        mtime: float = None

    def __init__(
        self,
        dd20_filepath: str,
        dd20_mapping_filepath: str,
        mrid_mapping_filepath: str,
        refresh_data: bool = True,
    ):
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
        self.__DD20 = self.__Metadata(
            "DD20", dd20_filepath, parse_dd20_excelsheets_to_dataframe
        )
        self.__DD20_MAP = self.__Metadata(
            "DD20 name mapping",
            dd20_mapping_filepath,
            parse_acline_namemap_excelsheet_to_dataframe,
        )
        self.__MRID_MAP = self.__Metadata(
            "MRID mapping",
            mrid_mapping_filepath,
            parse_aclineseg_scada_csvdata_to_dataframe,
        )
        self.dataframe: pd.DataFrame = pd.DataFrame()
        self.__data_updated: bool = False

        if refresh_data:
            self.refresh_data()

    def refresh_data(self) -> pd.DataFrame:
        """
        This function will check the input files for updates and reload
        any changes. If one or more files were updated, the combined
        dataframe will be recalculated.

        The following 3 datasources are processed:
        1. "DD20" excel-file.
            Conductor properties are collected for each AC-line in DD20.
            An object for each AC-line is created. All objects are
            gathered into a dataframe holding all extracted data.
        2. "DD20 name to SCADA AC-line name mapping" excel-file.
            Mapping from DD20 AC-line name to AC-line name used in SCADA
            system are parsed to a dictionary. This is necessary since
            some AC-line names differ between SCADA and DD20.
        3. "AC-line name to AC-linesegment MRID mapping" csv-file.
            Mapping from AC-line name used in SCADA system to AC-line
            segment MRID in SCADA system are parsed to a dataframe.
            The AC-linesegment MRID is a unique identifier, which all
            conductor data must be linked to.

        Returns
        -------
        pd.DataFrame
            Will return the combined dataframe
        """
        # Deprecation warning: The "refresh_data" method should not
        # invoke update or return a dataframe. Change this later!
        try:
            for input in [self.__DD20, self.__DD20_MAP, self.__MRID_MAP]:
                file_update_time = os.path.getmtime(input.path)

                if file_update_time != input.mtime:
                    log.info(f"Updating {input.name} file")
                    input.dataframe = input.func(file_path=input.path)
                    input.mtime = file_update_time
                    self.__data_updated = True
        except Exception as e:
            log.error("Parsing of input file failed.")
            log.exception(e)

        # This try should propably be removed at next major version bump
        try:
            if self.__data_updated:
                self.__data_updated = False
                self.join_dataframes()
        except Exception as e:
            log.error("Parsing of input file failed.")
            log.exception(e)

        # Return should probably be removed at next major version bump
        return self.dataframe

    def join_dataframes(self):
        try:
            obj_list = [self.__DD20, self.__DD20_MAP, self.__MRID_MAP]
            if any(obj.dataframe.empty for obj in obj_list):
                raise ValueError(
                    "Cannot calculate common dataframe, as "
                    + "one or more underlying dataframes are missing"
                )
            else:
                self.dataframe = create_aclinesegment_dataframe(
                    dd20_data=self.__DD20.dataframe,
                    dd20_to_scada_name_map=self.__DD20_MAP.dataframe,
                    scada_aclinesegment_map=self.__MRID_MAP.dataframe,
                )
        except Exception as e:
            log.error("Create dataframe with AC-linesegment properties failed")
            log.exception(e)
            raise e


def setup_logging(debug: Union[str, bool] = False):
    """Function which sets up properties for logging."""
    if debug == "FALSE" or debug is False:
        # __main__ will output INFO-level, everything else stays at WARNING
        LOGFORMAT = "%(levelname)s:%(asctime)s:%(name)s - %(message)s"
        logging.basicConfig(format=LOGFORMAT)
        logging.getLogger(__name__).setLevel(logging.INFO)
    elif debug == "TRUE" or debug is True:
        # Set EVERYTHING to DEBUG level
        logging.basicConfig(
            format="%(levelname)s:%(asctime)s:%(name)s - %(message)s",
            level=logging.DEBUG,
        )
        log.debug("Setting all logs to debug-level")
    else:
        raise ValueError(
            f"Debug is set to '{debug}', but must be either 'TRUE' or 'FALSE'."
        )


if __name__ == "__main__":

    time_begin = time()

    log.info("Loading environment variables in to DD20Settings.")
    try:

        settings = DD20Settings()
    except ValidationError as validation_error:
        log.error(validation_error.errors)
        raise validation_error
    except Exception as error:
        log.error(error.errors)
        raise ValueError("Error while reading application settings.")

    setup_logging(settings.debug)

    log.info("Collecting conductor data and preparing dataframe.")
    conductor_data = ACLineSegmentProperties(
        dd20_filepath=settings.dd20_filepath,
        dd20_mapping_filepath=settings.dd20_mapping_filepath,
        mrid_mapping_filepath=settings.mrid_mapping_filepath,
    )

    log.info("Starting conductor data provider API.")
    conductor_api = singuapi.DataFrameAPI(
        conductor_data.dataframe,
        dbname=settings.api_dbname,
        port=settings.api_port,
    )
    log.info(
        f"API initialized on port '{conductor_api.web.port}' "
        + f"with dbname '{settings.api_dbname}'."
    )
    log.debug(f"Started up in {round(time()-time_begin,3)} seconds")

    # Loop eternally and refresh data if files change
    while True:
        sleep(settings.api_refresh_rate)
        conductor_api[settings.api_dbname] = conductor_data.refresh_data()
