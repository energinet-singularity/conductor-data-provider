# Generic modules
import os
import logging
from time import sleep, time

# Modules
from singupy import api as singuapi
import pandas as pd

# App modules
from dataframe_handler import parse_dataframe_columns_to_dictionary, verify_dataframe_columns
from csv_file_handler import parse_csv_file_to_dataframe
from excel_sheet_handler import parse_excel_sheets_to_dataframe_dict
from parse_dd20 import DD20Parser

# Initialize log
log = logging.getLogger(__name__)


def extract_dd20_excelsheet_to_dataframe() -> pd.DataFrame:
    """Extract conductor data from DD20 excelsheets and return it in combined dataframe"""

    # DD20 excel file parameters
    DD20_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../tests/valid-testdata/"
    DD20_FILENAME = "DD20.XLSM"
    # DD20_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/../real-data/"
    # DD20_FILENAME = "DD20new.XLSM"
    DD20_HEADER_INDEX = 1
    DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
    DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"

    # parsing data from DD20 to dataframe dictionary
    dd20_dataframe_dict = parse_excel_sheets_to_dataframe_dict(file_path=DD20_FILEPATH+DD20_FILENAME,
                                                               sheets=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
                                                               header_index=DD20_HEADER_INDEX)

    # TODO: use hash function only or both?
    # Expected columns in DD20 excel sheet 'stationsdata'
    """ DD20_EXPECTED_COLS_STATIONSDATA = ['Linjenavn', 'Spændingsniveau', 'Ledningstype', 'Antal fasetråde', 'Antal systemer',
                                       'Kontinuer', '15 min', '1 time', '40 timer'] """
    # verifying columns on data from dd20
    """ verify_dataframe_columns(dataframe=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                             expected_columns=DD20_EXPECTED_COLS_STATIONSDATA,
                             allow_extra_columns=True) """

    # Parsing dd20 data from dataframes to combined dataframe
    dd20 = DD20Parser(df_station=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                      df_line=dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA])
    return dd20.dataframe

    # OLD method:
    # return extract_conductor_data_from_dd20(dataframe_station=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA], dataframe_line=dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA])


def extract_namemap_excelsheet_to_dict() -> dict:
    """Extract ....... TODO

    Returns
    -------
    dict : dict
    """
    #
    ACLINE_NAMEMAP_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/Limits_other.xlsx'
    # ACLINE_NAMEMAP_FILEPATH = os.path.dirname(__file__) + '/../real-data/Limits_other.xlsx'
    ACLINE_NAMEMAP_SHEET = 'DD20Mapping'
    ACLINE_NAMEMAP_KEY_NAME = 'DD20 Name'
    ACLINE_NAMEMAP_VALUE_NAME = 'ETS Name'
    ACLINE_NAMEMAP_EXPECTED_COLS = [ACLINE_NAMEMAP_KEY_NAME, ACLINE_NAMEMAP_VALUE_NAME]

    #
    acline_namemap_dataframe = parse_excel_sheets_to_dataframe_dict(file_path=ACLINE_NAMEMAP_FILEPATH,
                                                                    sheets=[ACLINE_NAMEMAP_SHEET],
                                                                    header_index=0)[ACLINE_NAMEMAP_SHEET]

    # verifying columns on data from mapping sheet
    verify_dataframe_columns(dataframe=acline_namemap_dataframe,
                             expected_columns=ACLINE_NAMEMAP_EXPECTED_COLS,
                             allow_extra_columns=True)

    #
    return parse_dataframe_columns_to_dictionary(dataframe=acline_namemap_dataframe,
                                                 dict_key=ACLINE_NAMEMAP_KEY_NAME,
                                                 dict_value=ACLINE_NAMEMAP_VALUE_NAME)


def extract_lineseg_to_mrid_dataframe() -> pd.DataFrame:
    DLR_MRID_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/seg_line_mrid.csv'
    # DLR_MRID_FILEPATH = os.path.dirname(__file__) + '/../real-data/seg_line_mrid_PROD.csv'
    # TODO verify expected columns

    lineseg_to_mrid_dataframe = parse_csv_file_to_dataframe(file_path=DLR_MRID_FILEPATH, drop_line_index=1)

    # TODO set these somewhere else
    MRIDMAP_EXPECTED_COLS = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

    verify_dataframe_columns(dataframe=lineseg_to_mrid_dataframe,
                             expected_columns=MRIDMAP_EXPECTED_COLS,
                             allow_extra_columns=True)

    return lineseg_to_mrid_dataframe


def create_dlr_dataframe(conductor_dataframe: pd.DataFrame,
                         dd20_to_scada_name: dict,
                         lineseg_to_mrid_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: doc me
    """

    # constant
    MRIDMAP_DLR_ENABLED_COL_NM = 'DLR_ENABLED'
    LINE_EMSNAME_COL_NM = 'LINE_EMSNAME'
    # EXPECTED_NAME_COL_NM = 'ACLINE_EMSNAME_EXPECTED'
    EXPECTED_NAME_COL_NM = 'name'

    # append column with list mapped name based on expected name if is existing in list, else keep name.
    # Remove expected name column
    mapped_name_list = [dd20_to_scada_name[x] if x in dd20_to_scada_name else x
                        for x in conductor_dataframe[EXPECTED_NAME_COL_NM]]
    conductor_dataframe[LINE_EMSNAME_COL_NM] = mapped_name_list
    conductor_dataframe = conductor_dataframe.drop(columns=[EXPECTED_NAME_COL_NM])

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

    # force lowercase
    dlr_dataframe.columns = dlr_dataframe.columns.str.upper()

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
