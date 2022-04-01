import logging
import os
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


def parse_excel_sheet_to_dataframe(file_path: str, sheet_name: str, header_index: int = 0) -> pd.DataFrame:
    """Read sheet from excel file and parse it to pandas dataframe.

    Parameters
    ----------
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
        dataframe = pd.read_excel(io=file_path, sheet_name=sheet_name, header=header_index)
        log.info(f"Excel data from sheet '{sheet_name}' in '{file_path}' was parsed to dataframe.")
    except Exception as e:
        log.exception(f"Parsing data from sheet: '{file_path}' in excel file: '{sheet_name}' failed with message: '{e}'.")
        raise e

    return dataframe


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
            log.info('Dataframe contains expected columns.')
        else:
            raise ValueError(f"The columns: '{dataframe_columns}' in dataframe does not match expected columns: " +
                             f"'{expected_columns}'.")


def extract_conducter_data_from_dd20(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Extract conductor data from DD20 dataframe and returns it to a dataframe.
    The source data is DD20, which has a non-standard format, why customized cleaning and extraction from it is needed.

    Arguments
    ----------
    dataframe : pd.Dataframe
        Pandas dataframe containing DD20 data.

    Returns
    -------
    dataframe : pd.Dataframe
        Pandas dataframe, which will contain the following columns for each line in DD20:
        - ACLINE_EMSNAME_EXPECTED (expected EMSNAME of ACLINE SCADA, derived from columns 'Spændingsniveau' and 'Linjenavn')
        - ACLINE_DD20_NAME (DD20 'Linjenavn')
        - CONDUCTER_TYPE (DD20 'Luftledertype')
        - RESTRICTIVE_COMPONENT_LIMIT (Most restrictive limit for components on line)
        - RESTRICTIVE_CABLE_LIMIT_CONTINUOUS (allowed continous loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_15M (allowed 15 minutes loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_1H (allowed 1 hour loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_40H (allowed 40 hour loading of cable on line, if present.)
    """
    # Columns in DD20 containing components restriction values
    DD20_COLUMNS_COMPONENT_RESTICT = ['Unnamed: 5', 'AF1', 'LA1', 'SA1', 'TR1', 'Unnamed: 11',
                                      'SR1', 'Unnamed: 15', 'AF2', 'LA2', 'SA2', 'TR2', 'Unnamed: 21', 'SR2']

    # Columns in DD20 defined as constants, since data will be extracted from them
    DD20_LINENAME_COL_NM = 'Linjenavn'
    DD20_KV_COL_NM = 'Spændingsniveau'
    DD20_CONDUCTOR_TYPE_COL_NM = 'Luftledertype'
    DD20_CONTINIOUS_COL_NM = 'Kontinuer'
    DD20_15M_COL_NM = '15 min'
    DD20_1H_COL_NM = '1 time'
    DD20_40H_COL_NM = '40 timer'

    # TODO: build error if duplicata name (also check types or rely on try-catch?)
    try:
        # Select only rows where line name are present, by removing rows with null value and rows not containing "-"
        dataframe = dataframe[(dataframe[DD20_LINENAME_COL_NM].notna()) &
                              (dataframe[DD20_LINENAME_COL_NM].str.contains("-"))]

        # Filtered frame of unique line names by removing rows with '(N)'(parallel line representation in DD20).
        dataframe_filtered = dataframe[~(dataframe[DD20_LINENAME_COL_NM].str.contains(r'\(N\)'))]

        # Extract unique line names to list
        acline_dd20_names = dataframe_filtered[DD20_LINENAME_COL_NM].values.tolist()

        # Extract kv level to letters list
        acline_kv_names = [convert_voltage_level_to_letter(voltage_level=kv)
                           for kv in dataframe_filtered[DD20_KV_COL_NM].values.tolist()]

        # make list of expected ets names by combining line name and kv letter
        acline_expected_ets_names = [f"{kv_name}_{acline_dd20_name.strip()}"
                                     for kv_name, acline_dd20_name in zip(acline_kv_names, acline_dd20_names)]

        # make list of conductor type per line
        conductor_type = [dataframe[dataframe[DD20_LINENAME_COL_NM] == line_name][DD20_CONDUCTOR_TYPE_COL_NM].values[0]
                          for line_name in acline_dd20_names]

        # make list of restrictive component limit per line by taking minimum value of all component limits (min is called twice to take min of rows and columns)
        restrictive_component_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_COLUMNS_COMPONENT_RESTICT].min(skipna=True).min(skipna=True)
                                        for line_name in acline_dd20_names]

        # make lists of restrictive limits for cable (continuous, 15M, 1H and 40H)
        restrictive_continious_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_CONTINIOUS_COL_NM].min(skipna=True)
                                               for line_name in acline_dd20_names]
        restrictive_15m_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_15M_COL_NM].min(skipna=True)
                                        for line_name in acline_dd20_names]
        restrictive_1h_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_1H_COL_NM].min(skipna=True)
                                       for line_name in acline_dd20_names]
        restrictive_40h_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_40H_COL_NM].min(skipna=True)
                                        for line_name in acline_dd20_names]

        # combine data to dictionary and dataframe
        conductor_data_dict = {'ACLINE_EMSNAME_EXPECTED': acline_expected_ets_names,
                               'ACLINE_DD20_NAME': acline_dd20_names,
                               'CONDUCTER_TYPE': conductor_type,
                               'RESTRICTIVE_COMPONENT_LIMIT': restrictive_component_limits,
                               'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': restrictive_continious_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_15M': restrictive_15m_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_1H': restrictive_1h_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_40H': restrictive_40h_cable_limits}
        conducter_dataframe = pd.DataFrame.from_dict(conductor_data_dict).fillna('None')

    except Exception as e:
        log.exception(f"Parsing data failed with message: '{e}'.")
        raise e

    return conducter_dataframe


def parse_dd20() -> pd.DataFrame:
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
    DD20_DATASHEET_NAME = "Stationsdata"
    DD20_HEADER_INDEX = 1

    # Expected columns in DD20 excel sheet
    DD20_EXPECTED_COLUMN_NAMES = ['Linjenavn', 'Spændingsniveau', 'Antal sys.', 'Stationstype', 'IT1', 'Unnamed: 5',
                                  'AF1', 'LA1', 'SA1', 'TR1', 'SK1', 'Unnamed: 11', 'SR1', 'Stationstype.1',
                                  'IT2', 'Unnamed: 15', 'AF2', 'LA2', 'SA2', 'TR2', 'SK2', 'Unnamed: 21',
                                  'SR2', 'Dato', 'Kommentar', 'Unnamed: 25', 'Kabeltype', 'Kontinuer',
                                  '15 min', '1 time', '40 timer', 'Luftledertype']

    # parsing data from DD20
    dd20_dataframe = parse_excel_sheet_to_dataframe(file_path=DD20_FILEPATH+DD20_FILENAME,
                                                    sheet_name=DD20_DATASHEET_NAME,
                                                    header_index=DD20_HEADER_INDEX)

    # verifying columns on data from dd20
    verify_dataframe_columns(dataframe=dd20_dataframe,
                             expected_columns=DD20_EXPECTED_COLUMN_NAMES,
                             allow_extra_columns=True)

    # extracting data for each line
    return extract_conducter_data_from_dd20(dataframe=dd20_dataframe)


def combine_list_and_dicts():
    pass
    # input: cleaned dataframe, dict (dd20 name --> ets name when not auto tranlateable), dict (name-mrid)
    # output: dataframe with MRID inserted and mapping name (if present)
    # CODE:
    # use dict to fill out NAME_MAPPED (warning if mapping name not used, or just info?)
    # use dict to fill out MRID (error if not possible to map?)


if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    log.info("Collecting conductor data.")

    # TODO: make API
    # TODO: keep old data if new read fails?

    # parsing data from dd20
    try:
        conductor_data = parse_dd20()
        print(conductor_data)
    except Exception as e:
        log.exception(f"Parsing DD20 failed with the message: '{e}'")
