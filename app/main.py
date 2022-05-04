# Generic modules
import os
import logging
from time import sleep, time

# Modules
from singupy import api as singuapi

# App modules
from helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dict
from helpers.parse_mrid_map import parse_aclineseg_scada_csvdata_to_dataframe
from helpers.join_data import create_conductor_dataframe

# Initialize log
log = logging.getLogger(__name__)


def get_aclinesegment_properties():
    """
    Function for gathering AC-line conductor properties and exposing them via REST API.
    The conductor properties are exposed with a unique identifier called "ACLINESEGMENT_MRID".

    The conductor properties are gathred from a non-standard format called "DD20"(excel-file) and combined with mapping data
    from non-standard datasource from SCADA system (excel and csv-file).
    It is done in order to establish link bewteen conductor data from DD20 and SCADA database records.

    The usecase is to provide coductor data for Dynamic Line Rating calculations to be utilized in a SCADA system.

    The following 3 datasources are processed:
    1. "DD20" excel-file.
        Conductor properties are collected for each AC-line represented in DD20.
        A object for each AC-line is created. All objects are gathered into a dataframe holding all extracted data.
    2. "DD20 name to SCADA AC-line name mapping" excel-file.
        Mapping from DD20 AC-line name to AC-line name used in SCADA system are parsed to a dictionary.
        The need for this mapping is present, since not all AC-line names are aligned between SCADA and DD20.
    3. "AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system.
        Mapping from AC-line name used in SCADA system to AC-linesegment MRID in SCADA system are parsed to a dataframe.
        The AC-linesegment MRID is a unique identifier, which all conductor data must be linked to.

    Returns
    -------
        pd.DataFrame
            A dataframe containing conductor data represented row-wise with AC-Linsegment MRID as unique key.
    """
    # TODO: pass filepatch via env var
    # TODO: parse others settings via env vars also or leave as defaults on funtions/class? 
    DATA_INPUT_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/"
    DATA_INPUT_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../real-data/"

    # 1. parsing data from dd20 file
    try:
        dd20_dataframe = parse_dd20_excelsheets_to_dataframe(folder_path=DATA_INPUT_FILEPATH)
    except Exception as e:
        log.exception(f"Parsing DD20 failed with message: '{e}'")
        raise e

    # 2. parsing data from name map file
    try:
        dd20_to_scada_acline_name = parse_acline_namemap_excelsheet_to_dict(folder_path=DATA_INPUT_FILEPATH)
    except Exception as e:
        log.exception(f"Parsing Name mapping failed with message: '{e}'")
        raise e

    # 3. parsing data from scada system csv-file
    try:
        scada_mapping_dataframe = parse_aclineseg_scada_csvdata_to_dataframe(folder_path=DATA_INPUT_FILEPATH)
    except Exception as e:
        log.exception(f"Parsing SCADA data failed with message: '{e}'")
        raise e

    # Finally - combining data
    try:
        aclinesegment_dataframe = create_conductor_dataframe(conductor_dataframe=dd20_dataframe,
                                                             dd20_to_scada_name=dd20_to_scada_acline_name,
                                                             scada_mapping_datafram=scada_mapping_dataframe)
    except Exception as e:
        log.exception(f"Creating dataframe with AC-linesegment properties failed with message: '{e}'")
        raise e

    return aclinesegment_dataframe


if __name__ == "__main__":

    time_begin = time()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    log.info("Collecting conductor data and exposing via API.")

    # TODO: build use of mock data flag to use test data, else read file via mounted volume instead from filemover
    # TODO: build debug flag
    # TODO: default port samt folderpath og via helm og env vars i stedet for (6666)
    # TODO: keep old data if new read fails?
    # TODO: schdule job to scandir every 5 secound and update dataframe if new data can be fetched

    dataframe = get_aclinesegment_properties()

    log.debug(f"Data is: {dataframe.to_string()}")

    port_api = 5666
    coductor_data_api = singuapi.DataFrameAPI(dataframe, dbname='CONDUCTOR_DATA', port=port_api)
    log.info(f"Data exposed via api on port '{port_api}'.")
    log.info(f"It took {round(time()-time_begin,3)} secounds")

    while True:
        sleep(300)
