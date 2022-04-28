# Generic modules
import logging
from dataclasses import dataclass

# Modules
import pandas as pd

# Initialize log
log = logging.getLogger(__name__)

# TODO: try/except alle steder
# TODO: type og value verify i ACLinesegment object
# TODO: return og value via getters or?
# TODO: add hash funktion to verify columns did not change

# TODO move to module?
@dataclass(eq=True)
class ACLineProperties:
    """
    Class for representing parameteres and restrictions on a AC-line connection between two stations.
    The AC-line is represented by a name alongside parameters, which must be set based on a given datasource.

    Attributes
    ----------
    name : str
        Name of the AC-line.
    name_datasoruce: str
        Name of the AC-line in datasource which are used to set attributes.
    TODO: describe all attributes
            Pandas dataframe, which will contain the following columns for each line in DD20:
        - ACLINE_EMSNAME_EXPECTED (expected EMSNAME of ACLINE SCADA, derived from columns 'Spændingsniveau' and 'Linjenavn')
        - ACLINE_DD20_NAME (DD20 'Linjenavn')
        - CONDUCTOR_TYPE (DD20 'Luftledertype')
        - CONDUCTOR_COUNT (DD20 'Antal fasetråde')
        - SYSTEM_COUNT (DD20 'Antal systemer')
        - TODO: TEMP
        - TODO: statisk for leder
        - RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS (allowed continuous loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT_15M (allowed 15 minutes loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT_1H (allowed 1 hour loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT_40H (allowed 40 hour loading of components on line.)
        - RESTRICTIVE_COMPONENT_LIMIT (Most restrictive limit for components on line)
        - RESTRICTIVE_CABLE_LIMIT_CONTINUOUS (allowed continuous loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_15M (allowed 15 minutes loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_1H (allowed 1 hour loading of cable on line, if present.)
        - RESTRICTIVE_CABLE_LIMIT_40H (allowed 40 hour loading of cable on line, if present.)
    """
    acline_name_translated: str
    acline_name_datasource: str
    datasource: str
    conductor_type: str
    conductor_count: int
    system_count: int
    max_temperature: float
    restrict_conductor_lim_continuous: float
    restrict_component_lim_continuous: float
    restrict_component_lim_15m: float
    restrict_component_lim_1h: float
    restrict_component_lim_40h: float
    restrict_cable_lim_continuous: float
    restrict_cable_lim_15m: float
    restrict_cable_lim_1h: float
    restrict_cable_lim_40h: float
    # TODO: valideringsregler for attributes


# TODO: move to lib
def convert_voltage_level_to_letter(voltage_level: int) -> str:
    # TODO: make using regex instead?
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


class DD20StationDataframeParser():
    # parse kun data fra station ark til dictionarys som mappes fra name til prop
    # husk at lav hjælpe funktioner til at hente værdier ud

    """
    Class for parsing DD20, which is a Energinet in-house excel-file containing data for high voltage AC transmission lines.
    Each AC lines is represented by a name alongside with limits for transmission capacity and other parameters.
    A mock example of it can be found in 'tests/valid-testdata/DD20.XLSM'.

    TODO: describe data is parsed via dataframes or build in excel?

    Data is extracted from sheets "Stationsdata" and "Linjedata - Sommer" are combined into objects.
    A object for each AC line is added to a combined list of object.
    list of the objects can be fetched via?
    All AC line objects are also combinded into a dataframe where the columns represents the atributes of the object.
    It can be fetched via ??

    TODO: build dictionars into one init function
    TODO: fetc only data to list of objects, make dataframe outside

    Attributes
    ----------
    df_station : pd.DataFrame
        Dataframe containing station data from DD20

    Methods
    ---------
    get stuff?

    TODO: describe all attributes

    Arguments
    ----------
    dataframe_station : pd.Dataframe
        Pandas dataframe containing DD20 data sheet with station data.
    """
    def __init__(self,
                 df_station: pd.DataFrame,
                 acline_name_col_nm: str = 'Linjenavn',
                 kv_col_nm: str = 'Spændingsniveau',
                 conductor_count_col_nm: str = 'Antal fasetråde',
                 system_count_col_nm: str = 'Antal systemer',
                 conductor_type_col_nm: str = 'Ledningstype',
                 conductor_max_temp_col_nm: str = 'Temperatur',
                 cablelim_continuous_col_nm: str = 'Kontinuer',
                 cablelim_15m_col_nm: str = '15 min',
                 cablelim_1h_col_nm: str = '1 time',
                 cablelim_40h_col_nm: str = '40 timer'):

        # init of value for column names (station)
        self.__acline_name_col_nm = acline_name_col_nm
        self.__kv_col_nm = kv_col_nm
        self.__conductor_count_col_nm = conductor_count_col_nm
        self.__system_count_col_nm = system_count_col_nm
        self.__conductor_type_col_nm = conductor_type_col_nm
        self.__conductor_max_temp_col_nm = conductor_max_temp_col_nm
        self.__cablelim_continuous_col_nm = cablelim_continuous_col_nm
        self.__cablelim_15m_col_nm = cablelim_15m_col_nm
        self.__cablelim_1h_col_nm = cablelim_1h_col_nm
        self.__cablelim_40h_col_nm = cablelim_40h_col_nm

        # dataframe init
        self.__df_station_source = df_station

        # cleaned dataframe (parallel representatio only)
        self.__df_station_clean = self.__prepare_df_station()

        # get unique acline names
        self.acline_name_list = self.__get_acline_name_list()

        # init value dicts:
        self.conductor_kv_level_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__kv_col_nm)
        self.conductor_count_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__conductor_count_col_nm)
        self.system_count_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__system_count_col_nm)
        self.conductor_type_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__conductor_type_col_nm)
        self.conductor_max_temp_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__conductor_max_temp_col_nm)
        self.cablelim_continuous_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_continuous_col_nm)
        self.cablelim_15m_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_15m_col_nm)
        self.cablelim_1h_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_1h_col_nm)
        self.cablelim_40h_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_40h_col_nm)

    def __get_acline_name_list(self):
        # TODO: add check for duplicate names
        """
        TODO: doc
        returns list of namesish
        """
        try:
            # Filtering dataframe on 'linename' column to get only unique line names by:
            # - Removing rows with null
            # - Removing rows not containing '-', since line names always contain this character
            # - Removing rows with '(N)', since it is a parallel line representation in DD20 format
            df_filtered = self.__df_station_source[(self.__df_station_source[self.__acline_name_col_nm].notna()) &
                                                   (self.__df_station_source[self.__acline_name_col_nm].str.contains("-"))]
            df_filtered = df_filtered[~(df_filtered[self.__acline_name_col_nm].str.contains(r'\(N\)'))]

            # Return list of unique DD20 names
            acline_names = df_filtered[self.__acline_name_col_nm].values.tolist()
            return acline_names
        except Exception as e:
            log.exception(f"Getting list of line names present in DD20 line sheet failed with message: '{e}'.")
            raise e

    def __prepare_df_station(self):
        """
        Removes single par og parallel from DD20 as they are not needed
        ex.
        GGH-VVV  and GGH-VVV (N). Only (N) needed
        TODO: dok
        """
        try:

            # find lines which have a parallel representation and filter dataframe
            df_parallel_lines = self.__df_station_source[(self.__df_station_source[self.__acline_name_col_nm].notna()) &
                                                         (self.__df_station_source[self.__acline_name_col_nm].str.contains("-")) &
                                                         (self.__df_station_source[self.__acline_name_col_nm].str.contains(r'\(N\)'))][self.__acline_name_col_nm].values.tolist()

            # remove string identifying them as parallel to have only the name
            acline_parallel_dd20_names = [x.replace('(N)', '').strip() for x in df_parallel_lines]

            # filter frame to remove single representation of lines when a parallel repræsentation is present
            # FILNA with none?
            # TODO: explain with example
            df_station_filtered = self.__df_station_source[(self.__df_station_source[self.__acline_name_col_nm].notna()) &
                                                           (self.__df_station_source[self.__acline_name_col_nm].str.contains("-")) &
                                                           ~self.__df_station_source[self.__acline_name_col_nm].isin(acline_parallel_dd20_names)]

            return df_station_filtered

        except Exception as e:
            log.exception(f"Preparing DD20 dataframe from Station-data sheet failed with message: '{e}'.")
            raise e

    # TODO: general function to extract data for row, column and error if more rows returned
    def __create_acline_name_to_column_single_value_dict(self, column_name: str):
        """ Returns dictionary with mapping from acline names in DD20 to corresponding value from column name."""
        try:
            # TODO: check that only one rows is found, else what?
            # for eacj acline:
            # - filter dataframe to only rows which has the linename
            # - pick only value for column
            dict = {acline_name: self.__df_station_clean[self.__df_station_clean[self.__acline_name_col_nm].str.contains(acline_name)]
                    [column_name].values[0]
                    for acline_name in self.acline_name_list}
            return dict
        except Exception as e:
            log.exception(f"Getting data column: {column_name} in Station-data sheet failed with message: '{e}'.")
            raise e


class DD20LineDataframeParser():
    # parse kun data fra line ark til dictionarys som mappes fra name til prop
    # husk at lav hjælpe funktioner til at hente værdier ud
    """
    Arguments
    ----------
    dataframe_line : pd.Dataframe
        Pandas dataframe containing DD20 data sheet with line data.a.
    """
    def __init__(self,
                 df_line: pd.DataFrame,
                 acline_name_col_nm: str = 'System',
                 kv_col_nm: str = 'Spændingsniveau',
                 acline_lim_continuous_col_nm: str = 'I-kontinuert',
                 system_count_col_nm: str = 'Antal sys.',
                 complim_continuous_col_rng: range = range(41, 55),
                 complim_15m_col_rng: range = range(55, 69),
                 complim_1h_col_rng: range = range(69, 83),
                 complim_40h_col_rng: range = range(83, 97)):

        #  init of value for column names and indexing (linjedata)
        self.__df_line_soruce = df_line
        self.__acline_name_col_nm = acline_name_col_nm
        self.__kv_col_nm = kv_col_nm
        self.__acline_lim_continuous_col_nm = acline_lim_continuous_col_nm
        self.__system_count_col_nm = system_count_col_nm
        self.__complim_continuous_col_rng = complim_continuous_col_rng
        self.__complim_15m_col_rng = complim_15m_col_rng
        self.__complim_1h_col_rng = complim_1h_col_rng
        self.__complim_40h_col_rng = complim_40h_col_rng

        # cleaned dataframes (parallel representatio only)
        self.__df_line_clean = self.__prepare_df_line()

        # get unique acline names
        self.acline_name_list = self.__get_acline_name_list()

        # dict init
        # KV og de 4 comp limits
        self.acline_lim_continuous_dict = self.__create_acline_name_to_column_min_value_dict(column_name=self.__acline_lim_continuous_col_nm)
        self.conductor_kv_level_dict = self.__create_acline_name_to_column_min_value_dict(column_name=self.__kv_col_nm)
        self.complim_continuous_dict = self.__create_acline_name_to_column_range_min_value_dict(column_range=self.__complim_continuous_col_rng)
        self.complim_15m_dict = self.__create_acline_name_to_column_range_min_value_dict(column_range=self.__complim_15m_col_rng)
        self.complim_1h_dict = self.__create_acline_name_to_column_range_min_value_dict(column_range=self.__complim_1h_col_rng)
        self.complim_40h_dict = self.__create_acline_name_to_column_range_min_value_dict(column_range=self.__complim_40h_col_rng)

    def __prepare_df_line(self):
        try:
            # remove single part of parallel line representation from sheet (lines with . in antal sys) as only paralle representation data is needed + only lines ('-')
            df_line_filtered = self.__df_line_soruce[(self.__df_line_soruce[self.__acline_name_col_nm].notna()) &
                                                     (self.__df_line_soruce[self.__acline_name_col_nm].str.contains("-")) &
                                                     ~(self.__df_line_soruce[self.__system_count_col_nm].str.contains(".", na=False))]

            return df_line_filtered
        except Exception as e:
            log.exception(f"Preparing DD20 dataframe from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_acline_name_list(self):
        # TODO: add check for duplicate names
        """
        TODO: doc
        returns list of namesish
        """
        try:
            # Filtering dataframe on 'linename' column to get only unique line names by:
            # - Removing rows with null
            # - Removing rows not containing '-', since line names always contain this character
            # - Removing rows with '(N)', since it is a parallel line representation in DD20 format
            # df_filtered = self.__df_line_clean[~(df_filtered[self.__acline_name_col_nm].str.contains(r'\(N\)'))]

            # Return list of DD20 names
            acline_names = self.__df_line_clean[self.__acline_name_col_nm].values.tolist()

            # remove string identifying them as parallel to have only the name
            acline_names_cleaned = [x.replace('(N)', '').strip() for x in acline_names]

            # ensure unique
            # TODO: add to station func also
            acline_names_list = list(set(acline_names_cleaned))
            return acline_names_list
        except Exception as e:
            # TODO: proper error>
            log.exception(f"Getting list of line names present in DD20 line sheet failed with message: '{e}'.")
            raise e

    def __create_acline_name_to_column_min_value_dict(self, column_name: str):
        """
        """
        # todo make general to tak min tiwce?
        try:
            dict = {acline_dd20name: self.__df_line_clean[self.__df_line_clean[self.__acline_name_col_nm].str.contains(acline_dd20name)]
                    [column_name].min(skipna=True)
                    for acline_dd20name in self.acline_name_list}
            return dict
        except Exception as e:
            log.exception(f"Getting data min column: {column_name} in line-data sheet failed with message: '{e}'.")
            raise e

    def __create_acline_name_to_column_range_min_value_dict(self, column_range: range):
        try:
            dict = {acline_dd20name: self.__df_line_clean[self.__df_line_clean[self.__acline_name_col_nm].str.contains(acline_dd20name)]
                    .iloc[:, column_range].min(skipna=True).min(skipna=True)
                    for acline_dd20name in self.acline_name_list}
            return dict
        except Exception as e:
            # TODO: proper error>
            log.exception(f"Getting ? failed with message: '{e}'.")
            raise e


# TODO: overvej at håndtere data vi 2 nye liste data objekter i stedet for dictionarys
def DD20_to_acline_properties_mapper(data_station: object, data_line: object):
    # dictionarys som input, dictionary for hver attribute på endelig ac onjekrt
    # sammel data fra de 2 ark
    # tjek at samme aclines og kv kombi er i begge sheets (error hvis den mangler i den anden og omvendt)
    # lav en liste med names hvis de er ens
    # lav dict med translated names
    # init object og returner dem i liste
    # Først tjekke der er enighed om navne fra begge kilder, Derefter kombiner dicts til liste af acline objekter

    # init name lists
    st_acline_names = data_station.acline_name_list
    ln_acline_names = data_line.acline_name_list

    # init kv mappings
    st_acline_name_to_conductor_kv_level = data_station.conductor_kv_level_dict
    # ln_acline_name_to_conductor_kv_level = data_line.conductor_kv_level_dict

    # init acline properties dict
    acline_name_to_conductor_count = data_station.conductor_count_dict
    acline_name_to_system_count = data_station.system_count_dict
    acline_name_to_conductor_type = data_station.conductor_type_dict
    acline_name_to_conductor_max_temp = data_station.conductor_max_temp_dict
    acline_name_to_cablelim_continuous = data_station.cablelim_continuous_dict
    acline_name_to_cablelim_15m = data_station.cablelim_15m_dict
    acline_name_to_cablelim_1h = data_station.cablelim_1h_dict
    acline_name_to_cablelim_40h = data_station.cablelim_40h_dict
    acline_name_to_lim_continuous = data_line.acline_lim_continuous_dict
    acline_name_to_complim_continuous = data_line.complim_continuous_dict
    acline_name_to_complim_15m = data_line.complim_15m_dict
    acline_name_to_complim_1h = data_line.complim_1h_dict
    acline_name_to_complim_40h = data_line.complim_40h_dict

    # tjeck lines in both
    names_in_station_but_not_line = list(set(st_acline_names).difference(ln_acline_names))
    names_in_line_but_not_station = list(set(ln_acline_names).difference(st_acline_names))
    # TODO: make with if and exception
    print(f" in station but not line {names_in_station_but_not_line}")
    print(f" in line but not station {names_in_line_but_not_station}")

    # as lines are present in both, just use one
    # TODO: make with regex instead
    acline_name__to_translated_name = {acline_dd20name:
                                       f"{convert_voltage_level_to_letter(st_acline_name_to_conductor_kv_level[acline_dd20name])}_{acline_dd20name.strip()[:len(acline_dd20name.strip())-3]}{acline_dd20name.strip()[-3:].replace('-','_')}"
                                       for acline_dd20name in st_acline_names}

    # return obj list
    obj_list = [ACLineProperties(acline_name_translated=acline_name__to_translated_name[acline_dd20_name],
                                 acline_name_datasource=acline_dd20_name,
                                 datasource="DD20",
                                 conductor_type=acline_name_to_conductor_type[acline_dd20_name],
                                 conductor_count=acline_name_to_conductor_count[acline_dd20_name],
                                 system_count=acline_name_to_system_count[acline_dd20_name],
                                 max_temperature=acline_name_to_conductor_max_temp[acline_dd20_name],
                                 restrict_cable_lim_continuous=acline_name_to_cablelim_continuous[acline_dd20_name],
                                 restrict_cable_lim_15m=acline_name_to_cablelim_15m[acline_dd20_name],
                                 restrict_cable_lim_1h=acline_name_to_cablelim_1h[acline_dd20_name],
                                 restrict_cable_lim_40h=acline_name_to_cablelim_40h[acline_dd20_name],
                                 restrict_conductor_lim_continuous=acline_name_to_lim_continuous[acline_dd20_name],
                                 restrict_component_lim_continuous=acline_name_to_complim_continuous[acline_dd20_name],
                                 restrict_component_lim_15m=acline_name_to_complim_15m[acline_dd20_name],
                                 restrict_component_lim_1h=acline_name_to_complim_1h[acline_dd20_name],
                                 restrict_component_lim_40h=acline_name_to_complim_40h[acline_dd20_name])
                for acline_dd20_name in st_acline_names]
    return obj_list


def parse_dd20_excelsheets_to_dataframe(folder_path: str, file_name: str = "DD20.XLSM") -> pd.DataFrame:
    """
    Wrapper function, maybe put in main?
    Extract conductor data from DD20 excel-sheets and return it to one combined dataframe.
    The source data is DD20, which has a non-standard format, why customized cleaning and extraction from it is needed.

    Arguments
    ----------


    Returns
    -------
    dataframe : pd.Dataframe

    """
    # TODO: doc and prettyfi
    # TODO: speci korrekt return af 2 dataframes
    # TODO: try, except
    """Extract conductor data from DD20 excelsheets and return it in combined dataframe"""

    # DD20 excel file parameters
    DD20_HEADER_INDEX = 1
    DD20_SHEETNAME_STATIONSDATA = "Stationsdata"
    DD20_SHEETNAME_LINJEDATA = "Linjedata - Sommer"
    DD20_SHEET_LIST = [DD20_SHEETNAME_STATIONSDATA, DD20_SHEETNAME_LINJEDATA]

    file_path = folder_path + file_name

    # parsing data from DD20 to dataframe dictionary
    dd20_dataframe_dict = pd.read_excel(io=file_path, sheet_name=DD20_SHEET_LIST, header=DD20_HEADER_INDEX)

    # TODO: use hash function only or both?
    # Expected columns in DD20 excel sheet 'stationsdata'
    """ DD20_EXPECTED_COLS_STATIONSDATA = ['Linjenavn', 'Spændingsniveau', 'Ledningstype', 'Antal fasetråde', 'Antal systemer',
                                       'Kontinuer', '15 min', '1 time', '40 timer'] """
    # verifying columns on data from dd20
    """ verify_dataframe_columns(dataframe=dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA],
                             expected_columns=DD20_EXPECTED_COLS_STATIONSDATA,
                             allow_extra_columns=True) """

    df_station = dd20_dataframe_dict[DD20_SHEETNAME_STATIONSDATA]
    df_line = dd20_dataframe_dict[DD20_SHEETNAME_LINJEDATA]

    data_station = DD20StationDataframeParser(df_station=df_station)

    data_line = DD20LineDataframeParser(df_line=df_line)

    # TODO lav 2 nye dataclasses og parse i stedet for?
    obj = DD20_to_acline_properties_mapper(data_station=data_station, data_line=data_line)

    dd20_dataframe = pd.DataFrame(data=[o.__dict__ for o in obj])

    # TODO: add log message it went good

    return dd20_dataframe
