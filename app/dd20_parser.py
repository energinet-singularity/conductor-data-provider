# Generic modules
import os
import logging
from time import sleep

# Modules
from singupy import api as singuapi
from json import dumps
import pandas as pd


# Initialize log
log = logging.getLogger(__name__)

# Globally used constants
LINE_EMSNAME_COL_NM = 'LINE_EMSNAME'


def convert_voltage_level_to_letter(voltage_level: int) -> str:
    """Converts voltage level to voltage letter representation.

    Parameters
    ----------
    voltage_level : int
        Voltage level in kV.

    Returns
    -------
    str
        Voltage letter.

    Example
    -------
        >>> convert_voltage_level_to_letter(400)
        C
    """
    if voltage_level >= 420:
        voltage_letter = 'B'
    elif 380 <= voltage_level < 420:
        voltage_letter = 'C'
    elif 220 <= voltage_level < 380:
        voltage_letter = 'D'
    elif 110 <= voltage_level < 220:
        voltage_letter = 'E'
    elif 60 <= voltage_level < 110:
        voltage_letter = 'F'
    elif 45 <= voltage_level < 60:
        voltage_letter = 'G'
    elif 30 <= voltage_level < 45:
        voltage_letter = 'H'
    elif 20 <= voltage_level < 30:
        voltage_letter = 'J'
    elif 10 <= voltage_level < 20:
        voltage_letter = 'K'
    elif 6 <= voltage_level < 10:
        voltage_letter = 'L'
    elif 1 <= voltage_level < 6:
        voltage_letter = 'M'
    elif voltage_level < 1:
        voltage_letter = 'N'

    return voltage_letter


def parse_csv_file_to_dataframe(file_path: str, header_index: int = 0) -> pd.DataFrame:
    '''
    Read CSV file and parse it to pandas dataframe.
    Note. Line number 2 in the CSV file will be removed.
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
        dataframe = pd.read_csv(file_path, delimiter=',', on_bad_lines='skip',
                                header=header_index)
        dataframe.drop(dataframe.head(1).index, inplace=True)
        log.info(f'CSV data from "{file_path}" was parsed to dataframe.')
    except Exception as e:
        log.exception(f'Parsing data from: "{file_path}" failed with message: {e}.')
        raise e

    return dataframe


def parse_excel_sheets_to_dataframe_dict(file_path: str, sheets: list, header_index: int = 0) -> dict:
    """Read sheets from excel file and parse them to a dictionary of pandas dataframes.

    Parameters
    ----------
    file_path : str
        Full path of the excel file.
    sheets : str
        List with names of sheets in excel.
    header_index : int
        Index number for row to be used as header on sheets (Default = 0)

    Returns
    -------
    dict
        A dict og dataframes containing the data from excel sheet.
        The dictionary key will be name of sheet.
    """
    # try to read data from excel file to dataframe.
    try:
        dataframe = pd.read_excel(io=file_path, sheet_name=sheets, header=header_index)
        log.info(f"Excel data from sheet(s): '{sheets}' in: '{file_path}' was parsed to dataframe dictionary.")
    except Exception as e:
        log.exception(f"Parsing data from sheet(s): '{sheets}' in excel file: '{file_path}' failed with message: '{e}'.")
        raise e

    return dataframe


def parse_dataframe_columns_to_dictionary(dataframe: pd.DataFrame, dict_key: str, dict_value: str) -> dict:
    '''
    Read two dataframe columns and parse them to a dictonary.
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
        dict
            A dictionary with the key/value specified by the user.
    '''
    # Checking the dictonary key and value to ensure that the user input is found in the dataframe.
    if dict_key not in dataframe:
        raise ValueError(f'The column "{dict_key}" does not exist in the dataframe.')

    if dict_value not in dataframe:
        raise ValueError(f'The column "{dict_value}" does not exist in the dataframe.')

    # Converting dataframe into a dictonary using user input to set key and value of the dictonary.
    try:
        dict_set = dataframe.set_index(dict_key).to_dict()[dict_value]
        log.info(f'Dataframe was parsed to a dictonary with key: "{dict_key}" and value: "{dict_value}".')
        log.debug(dumps(dict_set, indent=4, ensure_ascii=False))

    except Exception as e:
        log.exception(f'Creating dictonary from dataframe columns "{dict_key}" and "{dict_value}" failed with message: {e}')
        raise

    return dict_set


def verify_dataframe_columns(dataframe: pd.DataFrame, expected_columns: list, allow_extra_columns: bool = False) -> bool:
    """Verify if columns in dataframe contains expected colums.

    Parameters
    ----------
    dataframe : pd.Dataframe
        Pandas dataframe.
    expected_columns : list
        List of expected columns.
    allow_extra_columns : bool
        Set True if columns in addition to the expected columns are accepted.
        (Default = False)

    Returns
    -------
    bool
        True if columns are as expected, else False.
    """
    dataframe_columns = list(dataframe.columns)

    # If extra columns are allowed in dataframe, check if expected columns are present in dataframe
    if allow_extra_columns:
        if all(item in dataframe_columns for item in expected_columns):
            log.info('Dataframe contains expected columns.')
        else:
            raise ValueError(f"The columns: {expected_columns} are not present in dataframe, " +
                             f"since it only has the columns: '{dataframe_columns}'.")

    # If only expected columns are allowed in dataframe, check if only expected columns are in dataframe
    else:
        if sorted(dataframe_columns) == sorted(expected_columns):
            log.info('Dataframe contains only expected columns.')
        else:
            raise ValueError(f"The columns: '{dataframe_columns}' in dataframe does not match expected columns: " +
                             f"'{expected_columns}'.")


def extract_conducter_data_from_dd20(dataframe_station: pd.DataFrame, dataframe_line: pd.DataFrame) -> pd.DataFrame:
    """Extract conductor data from DD20 dataframes and returns it to one combined dataframe.
    The source data is DD20, which has a non-standard format, why customized cleaning and extraction from it is needed.

    Arguments
    ----------
    dataframe_station : pd.Dataframe
        Pandas dataframe containing DD20 data sheet with station data.
    dataframe_line : pd.Dataframe
        Pandas dataframe containing DD20 data sheet with line data.

    Returns
    -------
    dataframe : pd.Dataframe
        Pandas dataframe, which will contain the following columns for each line in DD20:
        - ACLINE_EMSNAME_EXPECTED (expected EMSNAME of ACLINE SCADA, derived from columns 'Spændingsniveau' and 'Linjenavn')
        - ACLINE_DD20_NAME (DD20 'Linjenavn')
        - CONDUCTER_TYPE (DD20 'Luftledertype')
        - CONDUCTER_COUNT (DD20 'Antal fasetråde')
        - SYSTEM_COUNT (DD20 'Antal systemer')
        - TODO: TEMP
        - TODO: statisk for leder
        - RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS (allowed continous loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT_15M (allowed 15 minutes loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT_1H (allowed 1 hour loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT_40H (allowed 40 hour loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT (Most restrictive limit for components on line)
        - RESTRICTIVE_CABLE_LIMIT_CONTINUOUS (allowed continous loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_15M (allowed 15 minutes loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_1H (allowed 1 hour loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_40H (allowed 40 hour loading of cable on line, if present.)
    """

    # Columns in DD20 (sheet 'Station') defined as constants, since data will be extracted from them
    DD20_STATION_LINENAME_COL_NM = 'Linjenavn'
    DD20_KV_COL_NM = 'Spændingsniveau'
    DD20_CONDUCTOR_TYPE_COL_NM = 'Ledningstype'
    DD20_CONDUCTOR_COUNT_COL_NM = 'Antal fasetråde'
    DD20_MAX_TEMP_COL_NM = 'Temperatur'
    DD20_SYSTEM_COUNT_COL_NM = 'Antal systemer'
    DD20_CABLE_CONTINIOUS_COL_NM = 'Kontinuer'
    DD20_CABLE_15M_COL_NM = '15 min'
    DD20_CABLE_1H_COL_NM = '1 time'
    DD20_CABLE_40H_COL_NM = '40 timer'

    # Columns name and index hardcoded for reading from DD20 sheet "Linjedata" since no uniquie headers exist
    DD20_LINJEDATA_LINENAME_COL_NM = 'System'
    DD20_LINJEDATA_KONT_COL_NM = 'I-kontinuert'
    DD20_LINJEDATA_ANTAL_SYS_COL_NM = 'Antal sys.'
    DD20_COMPONENT_CONTINIOUS_COL_INDEX = range(41, 55)
    DD20_COMPONENT_15M_COL_INDEX = range(55, 69)
    DD20_COMPONENT_1H_COL_INDEX = range(69, 83)
    DD20_COMPONENT_40H_COL_INDEX = range(83, 97)

    # TODO: build error if duplicata name (also check types or rely on try-catch?)
    try:

        # -- make unique list of aclines 
        
        # Select only rows where line name are present, by removing rows with null value and rows not containing "-"
        dataframe_station = dataframe_station[(dataframe_station[DD20_STATION_LINENAME_COL_NM].notna()) &
                                              (dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains("-"))]

        # Filtered frame of unique line names by removing rows with '(N)'(parallel line representation in DD20).
        dataframe_filtered = dataframe_station[~(dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(r'\(N\)'))]

        # Extract unique line names to list
        acline_dd20_names = dataframe_filtered[DD20_STATION_LINENAME_COL_NM].values.tolist()

        # Extract kv level to letters list
        acline_kv_names = [convert_voltage_level_to_letter(voltage_level=kv)
                           for kv in dataframe_filtered[DD20_KV_COL_NM].values.tolist()]

        # make list of expected ets names by combining line name and kv letter
        acline_expected_ets_names = [f"{kv_name}_{acline_dd20_name.strip()}"
                                     for kv_name, acline_dd20_name in zip(acline_kv_names, acline_dd20_names)]


        # -- make list of lines which have paralle representation --
        aclines_double = dataframe_station[(dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(r'\(N\)'))][DD20_STATION_LINENAME_COL_NM].values.tolist()
        aclines_double =  [x.replace('(N)', '').strip() for x in aclines_double]

        # filter frame to remove sin representation of lines when ad parallel repræsentation is present
        dataframe_station = dataframe_station[~dataframe_station[DD20_STATION_LINENAME_COL_NM].isin(aclines_double)]
        
        # TODO: verify that no uplicates are present in list of aclines

        # make list of conductor type per line (TODO: check parallel)
        conductor_type = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CONDUCTOR_TYPE_COL_NM].values[0]
                          for line_name in acline_dd20_names]

        # make list of conductor count per line (TODO: verify if correct ore to take max?)
        conductor_count = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CONDUCTOR_COUNT_COL_NM].values[0]
                           for line_name in acline_dd20_names]

        # make list of system count per line (TODO: verify if correct ore to take max?)
        system_count = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_SYSTEM_COUNT_COL_NM].values[0]
                        for line_name in acline_dd20_names]

        # make list of max temperature per line (TODO: verify if correct for parallel)
        max_temp = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_MAX_TEMP_COL_NM].values[0]
                    for line_name in acline_dd20_names]
        
        # make lists of restrictive cable limits for all durations
        restrictive_continious_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_CONTINIOUS_COL_NM].min(skipna=True)
                                               for line_name in acline_dd20_names]
        restrictive_15m_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_15M_COL_NM].min(skipna=True)
                                        for line_name in acline_dd20_names]
        restrictive_1h_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_1H_COL_NM].min(skipna=True)
                                       for line_name in acline_dd20_names]
        restrictive_40h_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_40H_COL_NM].min(skipna=True)
                                        for line_name in acline_dd20_names]

        # -- LINEDATA --

        # remove single part of parallel line representation from sheet (lines with . in antal sys) as only paralle representation data is needed + only lines ('-')
        dataframe_line = dataframe_line[(dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].notna()) &
                                        (dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains("-")) &
                                        ~(dataframe_line[DD20_LINJEDATA_ANTAL_SYS_COL_NM].str.contains(".", na=False))]
        
        # make list of coductor static limit (TODO: check if it is correct source?)
        restrictive_continious_conductor_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)][DD20_LINJEDATA_KONT_COL_NM ].min(skipna=True)
                                                   for line_name in acline_dd20_names]

        # restictive component limits for all durations
        restrictive_continious_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_CONTINIOUS_COL_INDEX].min(skipna=True).min(skipna=True)
                                              for line_name in acline_dd20_names]
        restrictive_15m_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_15M_COL_INDEX].min(skipna=True).min(skipna=True)
                                       for line_name in acline_dd20_names]
        restrictive_1h_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_1H_COL_INDEX].min(skipna=True).min(skipna=True)
                                      for line_name in acline_dd20_names]
        restrictive_40h_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_40H_COL_INDEX].min(skipna=True).min(skipna=True)
                                       for line_name in acline_dd20_names]

        # combine data to dictionary and dataframe
        conductor_data_dict = {'ACLINE_EMSNAME_EXPECTED': acline_expected_ets_names,
                               'ACLINE_DD20_NAME': acline_dd20_names,
                               'CONDUCTER_TYPE': conductor_type,
                               'CONDUCTER_COUNT': conductor_count,
                               'SYSTEM_COUNT': system_count,
                               'MAX_TEMPERATURE': max_temp,
                               'RESTRICTIVE_CONDUCTOR_LIMIT_CONTINIOUS' : restrictive_continious_conductor_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS': restrictive_continious_comp_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_15M': restrictive_15m_comp_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_1H': restrictive_1h_comp_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_40H': restrictive_40h_comp_limits,
                               'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': restrictive_continious_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_15M': restrictive_15m_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_1H': restrictive_1h_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_40H': restrictive_40h_cable_limits}
        conducter_dataframe = pd.DataFrame.from_dict(conductor_data_dict).fillna('None')

    except Exception as e:
        log.exception(f"Parsing data failed with message: '{e}'.")
        raise e

    return conducter_dataframe


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
    DD20_HEADER_INDEX = 1

    # sheet names
    DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
    DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"

    # Expected columns in DD20 excel sheet 'stationsdata'
    DD20_EXPECTED_COLS_STATIONSDATA = ['Linjenavn', 'Spændingsniveau', 'Ledningstype', 'Antal fasetråde', 'Antal systemer',
                                       'Kontinuer', '15 min', '1 time', '40 timer']

    # parsing data from DD20
    dd20_dataframe_dict = parse_excel_sheets_to_dataframe_dict(file_path=DD20_FILEPATH+DD20_FILENAME,
                                                               sheets=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
                                                               header_index=DD20_HEADER_INDEX)

    # verifying columns on data from dd20
    # TODO: also for linjedata and/or hash val of columns instead
    verify_dataframe_columns(dataframe=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                             expected_columns=DD20_EXPECTED_COLS_STATIONSDATA,
                             allow_extra_columns=True)

    # extracting data for each line
    return extract_conducter_data_from_dd20(dataframe_station=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                                            dataframe_line=dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA])


def extract_namemap_excelsheet_to_dict() -> dict:
    """Extract ....... TODO

    Returns
    -------
    dict : dict
    """
    #
    ACLINE_NAMEMAP_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/Limits_other.xlsx'
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
    # TODO verify expected columns

    lineseg_to_mrid_dataframe = parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)

    MRIDMAP_EXPECTED_COLS = ['ACLINESEGMENT_MRID', LINE_EMSNAME_COL_NM, 'DLR_ENABLED']

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

    # append column with list mapped name based on expected name if is existing in list, else keep name.
    # Remove expected name column
    mapped_name_list = [dd20_to_scada_name[x] if x in dd20_to_scada_name else x
                        for x in conductor_dataframe['ACLINE_EMSNAME_EXPECTED']]
    conductor_dataframe[LINE_EMSNAME_COL_NM] = mapped_name_list
    conductor_dataframe = conductor_dataframe.drop(columns=['ACLINE_EMSNAME_EXPECTED'])

    # extract lists of unique line names from conductor and scada dataframe
    lines_in_conductor_data = set(conductor_dataframe[LINE_EMSNAME_COL_NM].to_list())
    lines_in_scada_data = set(lineseg_to_mrid_dataframe[LINE_EMSNAME_COL_NM].to_list())

    # Create list of lines which have DLR enabled flag set True
    lines_dlr_enabled = lineseg_to_mrid_dataframe.loc[lineseg_to_mrid_dataframe[MRIDMAP_DLR_ENABLED_COL_NM] == "YES", LINE_EMSNAME_COL_NM].to_list()

    # report line names which are in DD20, but not ETS as info
    lines_only_in_conductor_data = [x for x in lines_in_conductor_data if x not in lines_in_scada_data]
    if lines_only_in_conductor_data:
        log.info(f"Line(s) with name(s): '{lines_only_in_conductor_data}' exists in conductor data but not in SCADA data.")

    # report line names which are in ETS, but not DD20 as info
    lines_only_in_scada_data = [x for x in lines_in_scada_data if x not in lines_in_conductor_data]
    # TODO: list(set(self.topics_consumed_list) - set(self.topics_produced_list)) or differnence?
    if lines_only_in_scada_data:
        log.info(f"Line(s) with name(s): '{lines_only_in_scada_data}' exists in SCADA data but not in conductor data.")

    # report lines for which DLR is enabled, but date is not availiable in DD20 as errors
    lines_dlr_enabled_data_missing = [x for x in lines_dlr_enabled if x not in lines_in_conductor_data]
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

    while True:
        sleep(300)
