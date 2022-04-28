# Generic modules
import os
import logging
from time import sleep, time

# Modules
from singupy import api as singuapi
import pandas as pd

# App modules
from helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from helpers.parse_namemap import extract_namemap_excelsheet_to_dict
from helpers.parse_mrid_map import extract_lineseg_to_mrid_dataframe
from helpers.join_data import create_dlr_dataframe

# Initialize log
log = logging.getLogger(__name__)

def get_acline_properties():

    # TODO: build use of mock data flag
    # TODO: parse env
    DATA_INPUT_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/"
    # os.path.dirname(__file__) + '/../real-data/

    # parsing data from dd20
    try:
        dd20_dataframe = parse_dd20_excelsheets_to_dataframe(folder_path=DATA_INPUT_FILEPATH)
    except Exception as e:
        log.exception(f"Parsing DD20 failed with the message: '{e}'")
        raise e

    # parsing data from name map
    try:
        #  os.path.dirname(__file__) + '/../real-data/
        dd20_to_scada_name = extract_namemap_excelsheet_to_dict(folder_path=DATA_INPUT_FILEPATH)
    except Exception as e:
        log.exception(f"Parsing Namemap failed with the message: '{e}'")
        raise e

    # parsing data from lineseg to mrid map
    try:
        lineseg_to_mrid_dataframe = extract_lineseg_to_mrid_dataframe(folder_path=DATA_INPUT_FILEPATH)
    except Exception as e:
        log.exception(f"Parsing Namemap failed with the message: '{e}'")
        raise e

    # TODO: Verify if data missing in columns where required
    try:
        final_dataframe = create_dlr_dataframe(conductor_dataframe=dd20_dataframe,
                                               dd20_to_scada_name=dd20_to_scada_name,
                                               lineseg_to_mrid_dataframe=lineseg_to_mrid_dataframe)
    except Exception as e:
        log.exception(f".. Failed with the message: '{e}'")
        raise e

    return final_dataframe


if __name__ == "__main__":

    time_begin = time()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    log.info("Collecting conductor data and exposing via API.")

    # TODO: make mock data flag fra env, else read from volume
    # TODO: read file via mounted volume instead from filemover
    # TODO: keep old data if new read fails?
    # TODO: default port og via helm og env vars i stedet for (6666)

    dataframe = get_acline_properties()

    log.info('Data collected.')
    log.debug(f"Data is: {dataframe.to_string()}")

    port_api = 5666
    coductor_data_api = singuapi.DataFrameAPI(dataframe, dbname='CONDUCTOR_DATA', port=port_api)
    log.info(f"Data exposed via api on port '{port_api}'.")
    log.info(f"It took {round(time()-time_begin,3)} secounds")

    # erstat med 5 sekund schduled job der tjekker for om der er kommet nye filer (brug scandir)
    # Hvis ændring i filer så 
    while True:
        sleep(300)
