# Generic modules
import os
import logging
from time import sleep, time

# Modules
from singupy import api as singuapi
import pandas as pd

# App modules
from excel_sheet_handler import parse_excel_sheets_to_dataframe_dict
from parse_dd20 import DD20Parser, extract_conductor_data_from_dd20
from parse_mrid_map import extract_lineseg_to_mrid_dataframe
from parse_name_map import extract_namemap_excelsheet_to_dict

# Initialize log
log = logging.getLogger(__name__)

#
LINE_EMSNAME_COL_NM = 'LINE_EMSNAME'


def extract_dd20_excelsheet_to_dataframe() -> pd.DataFrame:
    """Extract conductor data from DD20 excelsheets and return it in combined dataframe
    # TODO: doc it properly
    Returns
    -------
    dataframe : pd.Dataframe
    """

    # DD20 excel sheet naming and format
    DD20_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/"
    DD20_FILENAME = "DD20.XLSM"
    # DD20_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../real-data/"
    # DD20_FILENAME = "DD20new.XLSM"
    DD20_HEADER_INDEX = 1

    # sheet names
    DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
    DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"

    # Expected columns in DD20 excel sheet 'stationsdata'
    """ DD20_EXPECTED_COLS_STATIONSDATA = ['Linjenavn', 'Spændingsniveau', 'Ledningstype', 'Antal fasetråde', 'Antal systemer',
                                       'Kontinuer', '15 min', '1 time', '40 timer'] """

    # parsing data from DD20
    dd20_dataframe_dict = parse_excel_sheets_to_dataframe_dict(file_path=DD20_FILEPATH+DD20_FILENAME,
                                                               sheets=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
                                                               header_index=DD20_HEADER_INDEX)

    # verifying columns on data from dd20
    # TODO: also for linjedata and/or hash val of columns instead
    """ verify_dataframe_columns(dataframe=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                             expected_columns=DD20_EXPECTED_COLS_STATIONSDATA,
                             allow_extra_columns=True) """

    # TESTCLASS
    objs = DD20Parser(df_station=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                      df_line=dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA])
    # print(obj.acline_emsname_expected)
    # print(obj.acline_dd20_name)
    # dataframe = pd.DataFrame([o.__dict__ for o in objs])
    # print(dataframe)
    print(objs.dataframe)
    # import sys
    # sys.exit()

    # extracting data for each line
    return extract_conductor_data_from_dd20(dataframe_station=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                                            dataframe_line=dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA])


def create_dlr_dataframe(conductor_dataframe: pd.DataFrame,
                         dd20_to_scada_name: dict,
                         lineseg_to_mrid_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: doc me
    """

    # constant
    MRIDMAP_DLR_ENABLED_COL_NM = 'DLR_ENABLED'

    # append column with list mapped name based on expected name if is existing in list, else keep name.
    # Remove expected name column
    mapped_name_list = [dd20_to_scada_name[x] if x in dd20_to_scada_name else x
                        for x in conductor_dataframe['ACLINE_EMSNAME_EXPECTED']]
    conductor_dataframe[LINE_EMSNAME_COL_NM] = mapped_name_list
    conductor_dataframe = conductor_dataframe.drop(columns=['ACLINE_EMSNAME_EXPECTED'])

    # extract lists of unique line names from conductor and scada dataframe
    # TODO: remove lines which are below 132 as DLR will not be enabled for them?
    # TODO: list(set(self.topics_consumed_list) - set(self.topics_produced_list)) or differnence instead of comprehensions?
    # TODO: names_not_in_gis = list(set(mrid_list).difference(translated_names))
    # TODO: found_lines = list(set(mrid_list).intersection(translated_names))
    lines_in_conductor_data = set(conductor_dataframe[LINE_EMSNAME_COL_NM].to_list())
    lines_in_scada_data = set(lineseg_to_mrid_dataframe[LINE_EMSNAME_COL_NM].to_list())

    # Create list of lines which have DLR enabled flag set True
    lines_dlr_enabled = lineseg_to_mrid_dataframe.loc[lineseg_to_mrid_dataframe[MRIDMAP_DLR_ENABLED_COL_NM] == "YES", LINE_EMSNAME_COL_NM].to_list()

    # report line names which are in DD20, but not ETS as info
    lines_only_in_conductor_data = sorted([x for x in lines_in_conductor_data if x not in lines_in_scada_data])
    if lines_only_in_conductor_data:
        log.info(f"Line(s) with name(s): '{lines_only_in_conductor_data}' exists in conductor data but not in SCADA data.")

    # report line names which are in ETS, but not DD20 as info
    lines_only_in_scada_data = sorted([x for x in lines_in_scada_data if x not in lines_in_conductor_data])
    if lines_only_in_scada_data:
        log.info(f"Line(s) with name(s): '{lines_only_in_scada_data}' exists in SCADA data but not in conductor data.")

    # report lines for which DLR is enabled, but date is not availiable in DD20 as errors
    lines_dlr_enabled_data_missing = sorted([x for x in lines_dlr_enabled if x not in lines_in_conductor_data])
    if lines_dlr_enabled_data_missing:
        log.error(f"Line(s) with name(s): '{lines_dlr_enabled_data_missing}', are enabled for DLR but has no conductor data.")

    # Join two dataframes where emsname commen key
    # TODO: how to handle missing data? (dlr enabled but no conductor data)
    dlr_dataframe = lineseg_to_mrid_dataframe.join(conductor_dataframe.set_index(LINE_EMSNAME_COL_NM),
                                                   on=LINE_EMSNAME_COL_NM,
                                                   how='inner')

    # replace yes/no with true/false
    dlr_dataframe.loc[dlr_dataframe[MRIDMAP_DLR_ENABLED_COL_NM] == "YES", MRIDMAP_DLR_ENABLED_COL_NM] = True
    dlr_dataframe.loc[dlr_dataframe[MRIDMAP_DLR_ENABLED_COL_NM] == "NO", MRIDMAP_DLR_ENABLED_COL_NM] = False

    return dlr_dataframe


def main():

    # parsing data from dd20
    try:
        dd20_dataframe = extract_dd20_excelsheet_to_dataframe().copy()
        print(dd20_dataframe)
    except Exception as e:
        log.exception(f"Parsing DD20 failed with the message: '{e}'")
        raise e

    # parsing data from name map
    try:
        dd20_to_scada_name = extract_namemap_excelsheet_to_dict()
    except Exception as e:
        log.exception(f"Parsing Namemap failed with the message: '{e}'")
        raise e

    # parsing data from lineseg to mrid map
    try:
        lineseg_to_mrid_dataframe = extract_lineseg_to_mrid_dataframe()
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

    # TODO: replace loop with scheduler
    # TODO: read only when new file (check all 3 files in one go?)
    # TODO: make mock data flag fra env, else read from volume
    # TODO: read file via mounted volume instead from filemover
    # TODO: keep old data if new read fails?
    # TODO: verify hash of 3 top columns in DD20
    # TODO: default port og via helm og env vars i stedet for (6666)

    # TODO: Rewrite filter funktion så den er nice (loc?)

    dataframe = main()
    log.info('Data collected.')
    log.debug(f"Data is: {dataframe.to_string()}")

    port_api = 5666
    coductor_data_api = singuapi.DataFrameAPI(dataframe, dbname='CONDUCTOR_DATA', port=port_api)
    log.info(f"Data exposed via api on port '{port_api}'.")
    log.info(f"It took {round(time()-time_begin,3)} secounds")

    while True:
        sleep(300)
