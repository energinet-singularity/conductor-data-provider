import os
import json
import logging
from re import X
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)


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
        raise

    return dataframe


def parse_excel_sheets_to_dataframe_dict(file_path: str, sheets: list, header_index: list = None) -> dict:
    """Read sheet from excel file and parse it to pandas dataframe.

    Parameters
    ----------
    TODO rewrite doc
    file_path : str
        Full path of the excel file.
    sheet_name : str
        Name of sheet in excel file.
    header_index : int
        Index number for row to be used as header (Default = 0)

    Returns
    -------
    pd.DataFrame
        A dataframe containing the data from excel sheet.
    """
    # try to read data from excel file to dataframe.
    try:
        dataframe = pd.read_excel(io=file_path, sheet_name=sheets, header=header_index)
        log.info(f"Excel data from sheet(s): '{sheets}' in: '{file_path}' was parsed to dataframe dictionary.")
    except Exception as e:
        log.exception(f"Parsing data from sheet(s): '{sheets}' in excel file: '{file_path}' failed with message: '{e}'.")
        raise e

    return dataframe


def define_dictonary_from_two_columns_in_a_dataframe(dataframe: pd.DataFrame, dict_key: str,
                                                     dict_value: str) -> dict:
    '''
    Read dataframe and parse it to dictonary.
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
        log.exception(f'The column "{dict_key}" is not found in the dataframe, check "dict_key" input to the function.')
        raise ValueError(f'The column "{dict_key}" is not found in the dataframe, check "dict_key" input to the function.')

    if dict_value not in dataframe:
        log.exception(f'The column "{dict_value}" is not found in the dataframe, check "dict_value" input to the function.')
        raise ValueError(f'The column "{dict_value}" is not found in the dataframe, check "dict_value" input to the function.')

    # Converting dataframe into a dictonary using user input to set key and value of the dictonary.
    try:
        dict_set = dataframe.set_index(dict_key).to_dict()[dict_value]
        log.info(f'Dataframe was parsed to a dictonary with the key: "{dict_key}" and the value: "{dict_value}".')
        log.debug(json.dumps(dict_set, indent=4, ensure_ascii=False))

    except Exception as e:
        log.exception(f'Trying to create dictonary failed with message: {e}')
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
    """Extract conductor data from DD20 dataframe and returns it to a dataframe.
    The source data is DD20, which has a non-standard format, why customized cleaning and extraction from it is needed.

    Arguments
    ----------
    # TODO rewrite
    dataframe : pd.Dataframe
        Pandas dataframe containing DD20 data.

    Returns
    -------
    dataframe : pd.Dataframe
        Pandas dataframe, which will contain the following columns for each line in DD20:
        - ACLINE_EMSNAME_EXPECTED (expected EMSNAME of ACLINE SCADA, derived from columns 'Spændingsniveau' and 'Linjenavn')
        - ACLINE_DD20_NAME (DD20 'Linjenavn')
        - CONDUCTER_TYPE (DD20 'Luftledertype')
        - TODO: add the rest
        - RESTRICTIVE_COMPONENT_LIMIT (Most restrictive limit for components on line)
        - RESTRICTIVE_CABLE_LIMIT_CONTINUOUS (allowed continous loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_15M (allowed 15 minutes loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_1H (allowed 1 hour loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_40H (allowed 40 hour loading of cable on line, if present.)
    """

    # Columns in DD20 (sheet 'Station') defined as constants, since data will be extracted from them
    DD20_STATION_LINENAME_COL_NM = 'Linjenavn'
    DD20_LINJEDATA_LINENAME_COL_NM = 'System'
    DD20_KV_COL_NM = 'Spændingsniveau'
    DD20_CONDUCTOR_TYPE_COL_NM = 'Ledning'
    DD20_CONDUCTOR_COUNT_COL_NM = 'Antal fasetråde'
    DD20_SYSTEM_COUNT_COL_NM = 'Antal systemer'
    DD20_CABLE_CONTINIOUS_COL_NM = 'Kontinuer'
    DD20_CABLE_15M_COL_NM = '15 min'
    DD20_CABLE_1H_COL_NM = '1 time'
    DD20_CABLE_40H_COL_NM = '40 timer'

    # Columns index hardcoded for reading from DD20 sheet "Linjedata" since no uniquie headers exist
    DD20_COMPONENT_CONTINIOUS_COL_INDEX = range(41, 55)
    DD20_COMPONENT_15M_COL_INDEX = range(55, 69)
    DD20_COMPONENT_1H_COL_INDEX = range(69, 83)
    DD20_COMPONENT_40H_COL_INDEX = range(83, 97)

    # TODO: build error if duplicata name (also check types or rely on try-catch?)
    try:
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

        # make list of conductor type per line
        conductor_type = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM] == line_name][DD20_CONDUCTOR_TYPE_COL_NM].values[0]
                          for line_name in acline_dd20_names]

        # make list of conductor count per line
        conductor_count = [int(dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM] == line_name][DD20_CONDUCTOR_COUNT_COL_NM].values[0])
                           for line_name in acline_dd20_names]

        # make list of system count per line
        system_count = [int(dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM] == line_name][DD20_SYSTEM_COUNT_COL_NM].values[0])
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

        # make lists of restrictive limits for cable (continuous, 15M, 1H and 40H)
        restrictive_continious_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_CONTINIOUS_COL_NM].min(skipna=True)
                                               for line_name in acline_dd20_names]
        restrictive_15m_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_15M_COL_NM].min(skipna=True)
                                        for line_name in acline_dd20_names]
        restrictive_1h_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_1H_COL_NM].min(skipna=True)
                                       for line_name in acline_dd20_names]
        restrictive_40h_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_40H_COL_NM].min(skipna=True)
                                        for line_name in acline_dd20_names]

        # combine data to dictionary and dataframe
        conductor_data_dict = {'ACLINE_EMSNAME_EXPECTED': acline_expected_ets_names,
                               'ACLINE_DD20_NAME': acline_dd20_names,
                               'CONDUCTER_TYPE': conductor_type,
                               'CONDUCTER_COUNT': conductor_count,
                               'SYSTEM_COUNT': system_count,
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
    """Extract conductor data from DD20 excelsheet and return it in dataframe

    Returns
    -------
    dataframe : pd.Dataframe
    """
    # TODO: doc it properly
    # TODO: mount DD20 file and read it automaitcally if new (later)
    # TODO: change path to file moved via filemover

    # DD20 excel sheet naming and format
    DD20_FILEPATH = f"{os.path.dirname(os.path.realpath(__file__))}/"
    DD20_FILENAME = "DD20.XLSM"
    DD20_HEADER_INDEX = 1

    # TEMP TEST HACK
    DD20_FILEPATH = DD20_FILEPATH.replace('/app/', '/tests/valid-testdata/')

    DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
    DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"

    # Expected columns in DD20 excel sheet 'stationsdata'
    DD20_EXPECTED_COLS_STATIONSDATA = ['Linjenavn', 'Spændingsniveau', 'Antal sys.', 'Stationstype', 'IT1', 'Unnamed: 5',
                                       'AF1', 'LA1', 'SA1', 'TR1', 'SK1', 'Unnamed: 11', 'SR1', 'Stationstype.1',
                                       'IT2', 'Unnamed: 15', 'AF2', 'LA2', 'SA2', 'TR2', 'SK2', 'Unnamed: 21',
                                       'SR2', 'Dato', 'Kommentar', 'Unnamed: 25', 'Kabeltype', 'Kontinuer',
                                       '15 min', '1 time', '40 timer', 'Ledning']

    # parsing data from DD20
    dd20_dataframe_dict = parse_excel_sheets_to_dataframe_dict(file_path=DD20_FILEPATH+DD20_FILENAME,
                                                               sheets=[DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA],
                                                               header_index=[DD20_HEADER_INDEX])

    # verifying columns on data from dd20
    # TODO: also for linjedata and/or hash val of columns instead
    verify_dataframe_columns(dataframe=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                             expected_columns=DD20_EXPECTED_COLS_STATIONSDATA,
                             allow_extra_columns=True)

    # extracting data for each line
    return extract_conducter_data_from_dd20(dataframe_station=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA], dataframe_line=dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA])


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
    ACLINE_NAMEMAP_EXPECTED_COLS = ['DD20 Name', 'ETS Name', 'Comment', 'User']

    #
    acline_namemap_dataframme_dict = parse_excel_sheets_to_dataframe_dict(file_path=ACLINE_NAMEMAP_FILEPATH,
                                                                          sheets=[ACLINE_NAMEMAP_SHEET],
                                                                          header_index=[0])
    acline_namemap_dataframe = acline_namemap_dataframme_dict[ACLINE_NAMEMAP_SHEET]

    # verifying columns on data from dd20
    # TODO: also for linjedata and/or hash val of columns instead
    verify_dataframe_columns(dataframe=acline_namemap_dataframe,
                             expected_columns=ACLINE_NAMEMAP_EXPECTED_COLS,
                             allow_extra_columns=True)

    # Converting DD20 dataframe to a dictonary
    # line_emsname_to_aclinesegment_mrid()
    return define_dictonary_from_two_columns_in_a_dataframe(dataframe=acline_namemap_dataframe,
                                                            dict_key=ACLINE_NAMEMAP_KEY_NAME,
                                                            dict_value=ACLINE_NAMEMAP_VALUE_NAME)


def extract_lineseg_to_mrid_dataframe() -> pd.DataFrame:
    DLR_MRID_FILEPATH = os.path.dirname(__file__) + '/../tests/valid-testdata/seg_line_mrid.csv'
    # MRIDMAP_LINENAME_COL_NM = 'LINE_EMSNAME'
    # MRIDMAP_LINESEGMENT_MRID_COL_NM = 'ACLINESEGMENT_MRID'
    # TODO verify expected columns
    
    
    lineseg_to_mrid_dataframe = parse_csv_file_to_dataframe(DLR_MRID_FILEPATH)
    
    MRIDMAP_EXPECTED_COLS = ['ACLINESEGMENT_MRID', 'LINE_EMSNAME', 'DLR_ENABLED']

    verify_dataframe_columns(dataframe=lineseg_to_mrid_dataframe,
                             expected_columns=MRIDMAP_EXPECTED_COLS,
                             allow_extra_columns=True)

    return lineseg_to_mrid_dataframe


def create_dlr_dataframe(conductor_dataframe: pd.DataFrame, dd20_to_scada_name: dict, lineseg_to_mrid_dataframe: pd.DataFrame) -> pd.DataFrame:
    # input: cleaned dataframe, dict (dd20 name --> ets name when not auto tranlateable), dict (name-mrid)
    # output: dataframe with MRID inserted and mapping name (if present)
    # CODE:
    # use dict to fill out NAME_MAPPED (warning if mapping name not used, or just info?)
    # use dict to fill out MRID (error if not possible to map?)

    MRIDMAP_DLR_ENABLED_COL_NM = 'DLR_ENABLED'

    # append column with mapped EMSNAME
    mapped_name_list = [dd20_to_scada_name[x] if x in dd20_to_scada_name else x
                        for x in conductor_dataframe['ACLINE_EMSNAME_EXPECTED']]

    conductor_dataframe['LINE_EMSNAME'] = mapped_name_list
    conductor_dataframe = conductor_dataframe.drop(columns=['ACLINE_EMSNAME_EXPECTED'])

    # Join two dataframes where emsname commen key    
    # TODO replace yes og no med true/false
    # TODO skriv ren og fjern kolonner som ikke skal bruges (fjern dem før join?)
    # TODO hvordan håndteres dem som ikke mappes (både fra dd20 og ets)
    dlr_dataframe = lineseg_to_mrid_dataframe.join(conductor_dataframe.set_index('LINE_EMSNAME'), on='LINE_EMSNAME', how='inner')

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

    #
    try:
        lineseg_to_mrid_dataframe = extract_lineseg_to_mrid_dataframe()
        print(lineseg_to_mrid_dataframe.to_csv())
    except Exception as e:
        log.exception(f"Parsing Namemap failed with the message: '{e}'")
        raise e
    

    # TODO: Verify if data missing in columns where required
    try:
        final = create_dlr_dataframe(conductor_dataframe=dd20_dataframe, dd20_to_scada_name=dd20_to_scada_name, lineseg_to_mrid_dataframe=lineseg_to_mrid_dataframe)
        print(final.to_string())
    except Exception as e:
        log.exception(f".. Failed with the message: '{e}'")
        raise e


if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    log.info("Collecting conductor data.")

    # TODO: make API
    # TODO: keep old data if new read fails?

    main()
