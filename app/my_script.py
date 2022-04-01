import logging
import sys
import pandas as pd


# Initialize log
log = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# defintion of mapping from kV voltage level to voltageletter in dictionary
KV_LEVEL_TO_LETTER = {132: "E",
                      150: "E",
                      220: "D",
                      400: "C"}

# constant definitions for DD20 sheet naming and format
DD20_FILEPATH = ""
DD20_FILENAME = "DD20.xlsm"
DD20_DATASHEET_NAME = "Stationsdata"
DD20_HEADER_INDEX = 1
DD20_EXPECTED_HEADER_NAMES = ['Linjenavn',
                              'Spændingsniveau',
                              'Antal sys.',
                              'Stationstype',
                              'IT1',
                              'Unnamed: 5',
                              'AF1',
                              'LA1',
                              'SA1',
                              'TR1',
                              'SK1',
                              'Unnamed: 11',
                              'SR1',
                              'Stationstype.1',
                              'IT2',
                              'Unnamed: 15',
                              'AF2',
                              'LA2',
                              'SA2',
                              'TR2',
                              'SK2',
                              'Unnamed: 21',
                              'SR2',
                              'Dato',
                              'Kommentar',
                              'Unnamed: 25',
                              'Kabeltype',
                              'continious',
                              '15 min',
                              '1 time',
                              '40 timer',
                              'Luftledertype']
DD20_HEADERS_COMPONENT_RESTICT = ['Unnamed: 5',
                                  'AF1',
                                  'LA1',
                                  'SA1',
                                  'TR1',
                                  'Unnamed: 11',
                                  'SR1',
                                  'Unnamed: 15',
                                  'AF2',
                                  'LA2',
                                  'SA2',
                                  'TR2',
                                  'Unnamed: 21',
                                  'SR2']
DD20_LINENAME_COL_NM = 'Linjenavn'
DD20_KV_COL_NM = 'Spændingsniveau'
DD20_CONDUCTOR_TYPE_COL_NM = 'Luftledertype'
DD20_CONTINIOUS_COL_NM = 'continious'
DD20_15M_COL_NM = '15 min'
DD20_1H_COL_NM = '1 time'
DD20_40H_COL_NM = '40 timer'


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
        sys.exit(1)

    return dataframe


def verify_dataframe_columns_naming(dataframe: pd.DataFrame,
                                    expected_columns_naming: list,
                                    respect_order: bool = True) -> bool:
    """Verify columns naming in dataframe matches expected columns naming by comparing them with og without respect to ordering.
    Parameters
    ----------
    dataframe : pd.Dataframe
        Pandas dataframe.
    expected_columns_naming : list
        List of expected columns.
    respect order : bool
        Set True if order of columns in dataframe names must follow order in list of expected columns.
        set False if order of columns does not need to be respected.
        (Default = True)
    Returns
    -------
        bool
            True if columns are as expected, else False.
    """
    dataframe_columns = list(dataframe.columns)

    # sort the two list of columns if order of them does not need to be respected when comparing.
    if not respect_order:
        dataframe_columns.sort()
        expected_columns_naming.sort()

    if dataframe_columns == expected_columns_naming:
        return True
    else:
        log.warning(f"The columns: '{dataframe_columns}' in dataframe does not match expected columns: " +
                    f"'{expected_columns_naming}', when respect order is set: '{respect_order}'")
        return False


def extract_conducter_data_from_dd20(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Extract conductor data from DD20 dataframe and returns it to a dataframe.
    The soruce data is DD20, which has a non standard format, why costum cleaning and extraction from it is needed.

    The returned dataframe contain columns:
    - LINESGEMNT_MRID (contain None value, will be filled out later via mapping)
    - ACLINE_EMSNAME (contain EMSNAME of ACLINE)
    - bla bla bla
    ----------
    dataframe : pd.Dataframe
        Pandas dataframe.
    Returns
    -------
    dataframe : pd.Dataframe
        Pandas dataframe.
    """

    # TODO:
    # documentation
    # verify that name is string, verify other types also? (that columns are numeric etc?)
    # trim input to avoid spaces in sheet
    # build in error if not valid kv
    # build error if duplicata name

    # Select only rows where line name are pesent, by removing rows wtih null value and rows not conataing "-"
    dataframe = dataframe[(dataframe[DD20_LINENAME_COL_NM].notna()) &
                          (dataframe[DD20_LINENAME_COL_NM].str.contains("-"))]

    # make filtered frame of unique line names by removing rows with '(N)'(parallel line representation in DD20).
    dataframe_filtered = dataframe[~(dataframe[DD20_LINENAME_COL_NM].str.contains(r'\(N\)'))]

    # extract line names to list
    acline_dd20_names = dataframe_filtered[DD20_LINENAME_COL_NM].values.tolist()

    # extract kv level to letters listg
    acline_kv_names = [KV_LEVEL_TO_LETTER[kv]
                       for kv in dataframe_filtered[DD20_KV_COL_NM].values.tolist()]

    # make list of expected ets names by combining line name and kv letter
    acline_expected_ets_names = [f"{kv_name}_{acline_name}"
                                 for kv_name, acline_name in zip(acline_kv_names, acline_dd20_names)]

    # make list os conductor type per line
    conductor_type = [dataframe[dataframe[DD20_LINENAME_COL_NM] == line_name][DD20_CONDUCTOR_TYPE_COL_NM].values[0]
                      for line_name in acline_dd20_names]

    # make list of restrictive component limit per line by taking minimum value of all component limits
    restrictive_component_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_HEADERS_COMPONENT_RESTICT].min(skipna=True).min(skipna=True)
                                    for line_name in acline_dd20_names]

    # make lists of restrictive limits for cable (continious, 15M, 1H and 40H)
    restrictive_continious_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_CONTINIOUS_COL_NM].min(skipna=True)
                                           for line_name in acline_dd20_names]
    restrictive_15m_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_15M_COL_NM].min(skipna=True)
                                    for line_name in acline_dd20_names]
    restrictive_1h_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_1H_COL_NM].min(skipna=True)
                                   for line_name in acline_dd20_names]
    restrictive_40h_cable_limits = [dataframe[dataframe[DD20_LINENAME_COL_NM].str.contains(line_name)][DD20_40H_COL_NM].min(skipna=True)
                                    for line_name in acline_dd20_names]

    conducter_dataframe = pd.DataFrame.from_dict({'LINESEGMENT_MRID': [None]*len(acline_dd20_names),
                                                  'ACLINE_EMSNAME': acline_expected_ets_names,
                                                  'ACLINE_DD20_NAME': acline_dd20_names,
                                                  'ACLINE_NAME_MAPPED': [None]*len(acline_dd20_names),
                                                  'CONDUCTER_TYPE': conductor_type,
                                                  'RESTRICTIVE_COMPONENT_LIMIT': restrictive_component_limits,
                                                  'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': restrictive_continious_cable_limits,
                                                  'RESTRICTIVE_CABLE_LIMIT_15M': restrictive_15m_cable_limits,
                                                  'RESTRICTIVE_CABLE_LIMIT_1H': restrictive_1h_cable_limits,
                                                  'RESTRICTIVE_CABLE_LIMIT_40H': restrictive_40h_cable_limits}).fillna('None')

    return conducter_dataframe


def combine_list_and_dicts():
    pass
    # input: cleaned dataframe, dict (dd20 name --> ets name when not auto tranlateable), dict (name-mrid)
    # output: dataframe with MRID inserted and mapping name (if present)
    # CODE:
    # use dict to fill out NAME_MAPPED (warning if mapping name not used)
    # use dict to fill out MRID (error if not possible)


if __name__ == "__main__":
    log.info("Doing it..")

    # TODO:
    # mount DD20 file and read it automaitcally if new (later)
    # make API
    # keep old data if new read fails?

    # parsing data from dd20
    dd20_dataframe = parse_excel_sheet_to_dataframe(file_path=DD20_FILEPATH+DD20_FILENAME,
                                                    sheet_name=DD20_DATASHEET_NAME,
                                                    header_index=DD20_HEADER_INDEX)

    # verifying columns on data from dd20
    if verify_dataframe_columns_naming(dataframe=dd20_dataframe,
                                       expected_columns_naming=DD20_EXPECTED_HEADER_NAMES,
                                       respect_order=True):
        log.info('Dataframe contains expected columns.')
    else:
        log.exception("Excelsheet does not have correct formatting of headers, can't continue.")
        sys.exit(1)

    # extracting data for each line
    condutor_data = extract_conducter_data_from_dd20(dataframe=dd20_dataframe)
    print(condutor_data) 
