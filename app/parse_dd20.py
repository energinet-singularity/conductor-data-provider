# Generic modules
import logging

# Modules
import pandas as pd

# App modules
from voltagelevel_handler import convert_voltage_level_to_letter
from dataframe_handler import parse_dataframe_columns_to_dictionary
from obj_aclinesegment import ACLineCharacteristics

# Initialize log
log = logging.getLogger(__name__)

# TODO: try/except alle steder
# TODO: type og value verify i ACLinesegment object
# TODO: return og value via getters or?

class DD20ExcelSheetToDataframeDict():
# parse fra excel fil til 2 dataframe
# byg pandas funktion her ind i i stedet for hjælper?
    pass

class DD20StationDataParser():
# parse kun data fra station ark til dictionarys som mappes fra name til prop
# husk at lav hjælpe funktioner til at hente værdier ud
    pass


class DD20LineDataParser():
# parse kun data fra line ark til dictionarys som mappes fra name til prop
# husk at lav hjælpe funktioner til at hente værdier ud
    pass

class DD20ACLineMapper():
# sammel data fra de 2 ark
# husk at tjekke ssamme aclines er i begge sheets (error hvis den mangler i den anden og omvendt)
# husk at overvej opdeling er mapper for begge sheet her
    pass



class DD20Parser():
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
    """
    def __init__(self,
                 df_station: pd.DataFrame,
                 df_line: pd.DataFrame,
                 station_linename_col_nm: str = 'Linjenavn',
                 station_kv_col_nm: str = 'Spændingsniveau',
                 station_conductor_count_col_nm: str = 'Antal fasetråde',
                 station_system_count_col_nm: str = 'Antal systemer',
                 station_conductor_type_col_nm: str = 'Ledningstype',
                 station_conductor_max_temp_col_nm: str = 'Temperatur',
                 station_cablelim_continuous_col_nm: str = 'Kontinuer',
                 station_cablelim_15m_col_nm: str = '15 min',
                 station_cablelim_1h_col_nm: str = '1 time',
                 station_cablelim_40h_col_nm: str = '40 timer',
                 line_linename_col_nm: str = 'System',
                 line_conductor_continuous_col_nm: str = 'I-kontinuert',
                 line_antal_sys: str = 'Antal sys.',
                 line_complim_continuous_col_rng: range = range(41, 55),
                 line_complim_15m_col_rng: range = range(55, 69),
                 line_complim_1h_col_rng: range = range(69, 83),
                 line_complim_40h_col_rng: range = range(83, 97)):

        # init of value for column names (station)
        self.station_linename_col_nm = station_linename_col_nm
        self.station_kv_col_nm = station_kv_col_nm
        self.station_conductor_count_col_nm = station_conductor_count_col_nm
        self.station_system_count_col_nm = station_system_count_col_nm
        self.station_conductor_type_col_nm = station_conductor_type_col_nm
        self.station_conductor_max_temp_col_nm = station_conductor_max_temp_col_nm
        self.station_cablelim_continuous_col_nm = station_cablelim_continuous_col_nm
        self.station_cablelim_15m_col_nm = station_cablelim_15m_col_nm
        self.station_cablelim_1h_col_nm = station_cablelim_1h_col_nm
        self.station_cablelim_40h_col_nm = station_cablelim_40h_col_nm

        #  init of value for column names and indexing (linjedata)
        self.line_linename_col_nm = line_linename_col_nm
        self.line_conductor_continuous_col_nm = line_conductor_continuous_col_nm  # TODO: rename to better name (line staic restrict)
        self.line_antal_sys = line_antal_sys
        self.line_complim_continuous_col_rng = line_complim_continuous_col_rng
        self.line_complim_15m_col_rng = line_complim_15m_col_rng
        self.line_complim_1h_col_rng = line_complim_1h_col_rng
        self.line_complim_40h_col_rng = line_complim_40h_col_rng

        # dataframe init
        self.df_station_source = df_station
        self.df_line_source = df_line

        # get unique line names
        self.__line_dd20_name_list = self.__get_line_dd20_name_list()

        # cleaned dataframes (parallel representatio only)
        self.__df_line_clean = self.__prepare_df_line()
        self.__df_station_clean = self.__prepare_df_station()

        # init dict with expected name
        self.__acline_emsname_expected_dict = self.__get_expected_acline_emsnames_to_dict()

        # init from station data
        self.__conductor_type_dict = self.__get_conductor_types_to_dict()
        self.__conductor_count_dict = self.__get_conductor_counts_to_dict()
        self.__system_count_dict = self.__get_system_counts_to_dict()
        self.__max_temperature_dict = self.__get_max_temp_to_dict()
        self.__restrict_cable_lim_continuous_dict = self.__get_restrict_cable_lim_continuous_to_dict()
        self.__restrict_cable_lim_15m_dict = self.__get_restrict_cable_lim_15m_to_dict()
        self.__restrict_cable_lim_1h_dict = self.__get_restrict_cable_lim_1h_to_dict()
        self.__restrict_cable_lim_40h_dict = self.__get_restrict_cable_lim_40h_to_dict()

        # init from line data
        self.__restrict_conductor_lim_continuous_dict = self.__get_restrict_conductor_lim_continuous_to_dict()
        self.__restrict_component_lim_continuous_dict = self.__get_restrict_component_lim_continuous_to_dict()
        self.__restrict_component_lim_15m_dict = self.__get_restrict_component_lim_15m_to_dict()
        self.__restrict_component_lim_1h_dict = self.__get_restrict_component_lim_1h_to_dict()
        self.__restrict_component_lim_40h_dict = self.__get_restrict_component_lim_40h_to_dict()

        # output-ish (definer getter i stedet?)
        self.dataobjectlist = self.__create_object_list()
        self.dataframe = self.__create_dataframe()

    def __get_line_dd20_name_list(self):
        """
        TODO: doc
        returns list of namesish
        """
        try:
            # Filtering dataframe on 'linename' column to get only unique line names by:
            # - Removing rows with null
            # - Removing rows not containing '-', since line names always contain this character
            # - Removing rows with '(N)', since it is a parallel line representation in DD20 format
            df_filtered = self.df_station_source[(self.df_station_source[self.station_linename_col_nm].notna()) &
                                                 (self.df_station_source[self.station_linename_col_nm].str.contains("-"))]
            df_filtered = df_filtered[~(df_filtered[self.station_linename_col_nm].str.contains(r'\(N\)'))]

            # Return list of unique DD20 names
            line_dd20_names = df_filtered[self.station_linename_col_nm].values.tolist()
            return line_dd20_names
        except Exception as e:
            log.exception(f"Getting list of line names present in DD20 failed with message: '{e}'.")
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
            df_parallel_lines = self.df_station_source[(self.df_station_source[self.station_linename_col_nm].notna()) &
                                                       (self.df_station_source[self.station_linename_col_nm].str.contains("-")) &
                                                       (self.df_station_source[self.station_linename_col_nm].str.contains(r'\(N\)'))][self.station_linename_col_nm].values.tolist()

            # remove string identifying them as parallel to have only the name
            acline_parallel_dd20_names = [x.replace('(N)', '').strip() for x in df_parallel_lines]

            # filter frame to remove single representation of lines when a parallel repræsentation is present
            # FILNA with none?
            # TODO: explain with example
            df_station_filtered = self.df_station_source[(self.df_station_source[self.station_linename_col_nm].notna()) &
                                                         (self.df_station_source[self.station_linename_col_nm].str.contains("-")) &
                                                         ~self.df_station_source[self.station_linename_col_nm].isin(acline_parallel_dd20_names)].fillna('None')

            return df_station_filtered

        except Exception as e:
            log.exception(f"Preparing DD20 dataframe from Station-data sheet failed with message: '{e}'.")
            raise e

    def __prepare_df_line(self):
        try:
            # remove single part of parallel line representation from sheet (lines with . in antal sys) as only paralle representation data is needed + only lines ('-')
            df_line_filtered = self.df_line_source[(self.df_line_source[self.line_linename_col_nm].notna()) &
                                                   (self.df_line_source[self.line_linename_col_nm].str.contains("-")) &
                                                   ~(self.df_line_source[self.line_antal_sys].str.contains(".", na=False))].fillna('None')
            return df_line_filtered
        except Exception as e:
            log.exception(f"Preparing DD20 dataframe from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_expected_acline_emsnames_to_dict(self):
        """
        TODO: doc
        returns list of namesish
        """
        # Filtering dataframe on 'linename' column to get only unique line names by:
        # - Removing rows with null
        # - Removing rows not containing '-', since line names always contain this character
        # - Removing rows with '(N)', since it is a parallel line representation in DD20 format
        dataframe_filtered = self.df_station_source[(self.df_station_source[self.station_linename_col_nm].notna()) &
                                                    (self.df_station_source[self.station_linename_col_nm].str.contains("-"))]
        dataframe_filtered = dataframe_filtered[~(dataframe_filtered[self.station_linename_col_nm].str.contains(r'\(N\)'))]

        # dict
        line_dd20name_to_kv = parse_dataframe_columns_to_dictionary(dataframe=dataframe_filtered, dict_key=self.station_linename_col_nm, dict_value=self.station_kv_col_nm)
        line_dd20name_to_voltageletter = {k: convert_voltage_level_to_letter(v) for (k, v) in line_dd20name_to_kv.items()}

        # make list of expected ets names by combining line name and kv letter and replace ie. -1 with _1:
        # TODO: make it withg regex instead
        acline_exp = {line_dd20name: f"{line_dd20name_to_voltageletter[line_dd20name]}_{line_dd20name.strip()[:len(line_dd20name.strip())-3]}{line_dd20name.strip()[-3:].replace('-','_')}"
                      for line_dd20name in self.__line_dd20_name_list}

        return acline_exp
    # TODO: lav hjælpefunktion det i stedet blot returnere dict, eller evt. blot værdi?
    # get single row, column val (check det kun er single row, ellers fail)
    # get min of column for rows
    # get min of columns and

    def __get_conductor_types_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to corresponding 'Conductor type'."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_conductor_type_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting conductor type from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_conductor_counts_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to number of conductors."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_conductor_count_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting conductor count from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_system_counts_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to number of systems."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_system_count_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting syste, count from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_max_temp_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to maximum temperature."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_conductor_max_temp_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting maximum temperature from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_cable_lim_continuous_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive continuous cable limit."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_cablelim_continuous_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive continuous cable limit from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_cable_lim_15m_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive 15 min cable limit."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_cablelim_15m_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive 15 min cable limit from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_cable_lim_1h_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive 1 hour cable limit."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_cablelim_1h_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive 1 hour cable limit from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_cable_lim_40h_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive 40 hour cable limit."""
        try:
            return {line_dd20name: self.__df_station_clean[self.__df_station_clean[self.station_linename_col_nm].str.contains(line_dd20name)]
                    [self.station_cablelim_40h_col_nm].values[0]
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive 40 hour cable limit from Station-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_conductor_lim_continuous_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive continuous conductor limit."""
        try:
            return {line_dd20name: self.__df_line_clean[self.__df_line_clean[self.line_linename_col_nm].str.contains(line_dd20name)]
                    [self.line_conductor_continuous_col_nm].min(skipna=True)
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive continuous conductor limit from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_component_lim_continuous_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive continuous component limit."""
        try:
            return {line_dd20name: self.__df_line_clean[self.__df_line_clean[self.line_linename_col_nm].str.contains(line_dd20name)].iloc[:, self.line_complim_continuous_col_rng].min(skipna=True).min(skipna=True)
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive continuous component limit from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_component_lim_15m_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive 15 min component limit."""
        try:
            return {line_dd20name: self.__df_line_clean[self.__df_line_clean[self.line_linename_col_nm].str.contains(line_dd20name)].iloc[:, self.line_complim_15m_col_rng].min(skipna=True).min(skipna=True)
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive 15 min component limit from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_component_lim_1h_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive 1 hour component limit."""
        try:
            return {line_dd20name: self.__df_line_clean[self.__df_line_clean[self.line_linename_col_nm].str.contains(line_dd20name)].iloc[:, self.line_complim_1h_col_rng].min(skipna=True).min(skipna=True)
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive 1 hour component limit from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_restrict_component_lim_40h_to_dict(self):
        """ Returns dictionary with mapping from linenames in DD20 to restrictive 40 hour component limit."""
        try:
            return {line_dd20name: self.__df_line_clean[self.__df_line_clean[self.line_linename_col_nm].str.contains(line_dd20name)].iloc[:, self.line_complim_40h_col_rng].min(skipna=True).min(skipna=True)
                    for line_dd20name in self.__line_dd20_name_list}
        except Exception as e:
            log.exception(f"Getting restrictive 40 hour component limit from Line-data sheet failed with message: '{e}'.")
            raise e

    def __create_object_list(self):
        # TODO: via getter?
        obj_list = [ACLineCharacteristics(name=self.__acline_emsname_expected_dict[line_dd20_name],
                                          name_datasource=line_dd20_name,
                                          conductor_type=self.__conductor_type_dict[line_dd20_name],
                                          conductor_count=self.__conductor_count_dict[line_dd20_name],
                                          system_count=self.__system_count_dict[line_dd20_name],
                                          max_temperature=self.__max_temperature_dict[line_dd20_name],
                                          restrict_cable_lim_continuous=self.__restrict_cable_lim_continuous_dict[line_dd20_name],
                                          restrict_cable_lim_15m=self.__restrict_cable_lim_15m_dict[line_dd20_name],
                                          restrict_cable_lim_1h=self.__restrict_cable_lim_1h_dict[line_dd20_name],
                                          restrict_cable_lim_40h=self.__restrict_cable_lim_40h_dict[line_dd20_name],
                                          restrict_conductor_lim_continuous=self.__restrict_conductor_lim_continuous_dict[line_dd20_name],
                                          restrict_component_lim_continuous=self.__restrict_component_lim_continuous_dict[line_dd20_name],
                                          restrict_component_lim_15m=self.__restrict_component_lim_15m_dict[line_dd20_name],
                                          restrict_component_lim_1h=self.__restrict_component_lim_1h_dict[line_dd20_name],
                                          restrict_component_lim_40h=self.__restrict_component_lim_40h_dict[line_dd20_name])
                    for line_dd20_name in self.__line_dd20_name_list]
        return obj_list

    def __create_dataframe(self):
        # TODO: via getter?
        # TODO: maybe alternativ via get funktioner: [{attr: getattr(p,attr) for attr in dir(p) if not attr.startswith('_')} for p in objs]
        # TODO: eller lav datafram udenfor class for at adskille?
        dataframe = pd.DataFrame([o.__dict__ for o in self.dataobjectlist])
        return dataframe


# TODO: OLD version - delete when class is made instead?
def extract_conductor_data_from_dd20(dataframe_station: pd.DataFrame, dataframe_line: pd.DataFrame) -> pd.DataFrame:
    """
    Extract conductor data from DD20 dataframes and returns it to one combined dataframe.
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

    # Columns in DD20 (sheet 'Station') defined as constants, since data will be extracted from them
    DD20_STATION_LINENAME_COL_NM = 'Linjenavn'
    DD20_KV_COL_NM = 'Spændingsniveau'
    DD20_CONDUCTOR_TYPE_COL_NM = 'Ledningstype'
    DD20_CONDUCTOR_COUNT_COL_NM = 'Antal fasetråde'
    DD20_MAX_TEMP_COL_NM = 'Temperatur'
    DD20_SYSTEM_COUNT_COL_NM = 'Antal systemer'
    DD20_CABLE_CONTINUOUS_COL_NM = 'Kontinuer'
    DD20_CABLE_15M_COL_NM = '15 min'
    DD20_CABLE_1H_COL_NM = '1 time'
    DD20_CABLE_40H_COL_NM = '40 timer'

    # Columns name and index hardcoded for reading from DD20 sheet "Linjedata" since no uniquie headers exist
    DD20_LINJEDATA_LINENAME_COL_NM = 'System'
    DD20_LINJEDATA_KONT_COL_NM = 'I-kontinuert'
    DD20_LINJEDATA_ANTAL_SYS_COL_NM = 'Antal sys.'
    DD20_COMPONENT_CONTINUOUS_COL_INDEX = range(41, 55)
    DD20_COMPONENT_15M_COL_INDEX = range(55, 69)
    DD20_COMPONENT_1H_COL_INDEX = range(69, 83)
    DD20_COMPONENT_40H_COL_INDEX = range(83, 97)

    # TODO:
    # make as object with acline attributes (maybe as secondary class with data model?)
    # make methods to:
    # - extract unique list of aclines
    # - prepare station frame
    # - prepare linedta frame
    # - init the different attributes from frames via method per datatype

    # -- Make unique list of aclines dd20 naming and expected name en scada --
    # TODO: build error if duplicata name
    try:
        # Select only rows where line name are present, by removing rows with null value and rows not containing "-"
        # TODO: flyt og lav fitler nedeunder i stedet for så det ikke blandes sammen
        dataframe_station = dataframe_station[(dataframe_station[DD20_STATION_LINENAME_COL_NM].notna()) &
                                              (dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains("-"))]

        # Filtered frame of unique line names by removing rows with '(N)'(parallel line representation in DD20).
        dataframe_filtered = dataframe_station[~(dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(r'\(N\)'))]

        # Extract unique line names to list
        acline_dd20_names = dataframe_filtered[DD20_STATION_LINENAME_COL_NM].values.tolist()

        # Extract kv level to letters list
        acline_kv_names = [convert_voltage_level_to_letter(voltage_level=kv)
                           for kv in dataframe_filtered[DD20_KV_COL_NM].values.tolist()]

        # make list of expected ets names by combining line name and kv letter and replace ie. -1 with _1:
        # TODO: make it withg regex instead
        acline_expected_ets_names = [f"{kv_name}_{acline_dd20_name.strip()[:len(acline_dd20_name.strip())-3]}{acline_dd20_name.strip()[-3:].replace('-','_')}"
                                     for kv_name, acline_dd20_name in zip(acline_kv_names, acline_dd20_names)]
    except Exception as e:
        log.exception(f"Creating lists of ACLine names failed with message: '{e}'.")
        raise e

    # -- STATIONS data parsing ---
    try:

        # make list of lines which have paralle representation
        aclines_double = dataframe_station[(dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(r'\(N\)'))][DD20_STATION_LINENAME_COL_NM].values.tolist()
        aclines_double = [x.replace('(N)', '').strip() for x in aclines_double]

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
        restrictive_continuous_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_CONTINUOUS_COL_NM].values[0]
                                               for line_name in acline_dd20_names]
        restrictive_15m_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_15M_COL_NM].values[0]
                                        for line_name in acline_dd20_names]
        restrictive_1h_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_1H_COL_NM].values[0]
                                       for line_name in acline_dd20_names]
        restrictive_40h_cable_limits = [dataframe_station[dataframe_station[DD20_STATION_LINENAME_COL_NM].str.contains(line_name)][DD20_CABLE_40H_COL_NM].values[0]
                                        for line_name in acline_dd20_names]

    except Exception as e:
        log.exception(f"Parsing data from Station dataframe failed with message: '{e}'.")
        raise e

    # -- LINIE DATA parsing --
    try:
        # remove single part of parallel line representation from sheet (lines with . in antal sys) as only paralle representation data is needed + only lines ('-')
        dataframe_line = dataframe_line[(dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].notna()) &
                                        (dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains("-")) &
                                        ~(dataframe_line[DD20_LINJEDATA_ANTAL_SYS_COL_NM].str.contains(".", na=False))]

        # make list of coductor static limit (TODO: check if it is correct source?)
        restrictive_continuous_conductor_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)][DD20_LINJEDATA_KONT_COL_NM].min(skipna=True)
                                                   for line_name in acline_dd20_names]

        # restictive component limits for all durations
        restrictive_continuous_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_CONTINUOUS_COL_INDEX].min(skipna=True).min(skipna=True)
                                              for line_name in acline_dd20_names]
        restrictive_15m_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_15M_COL_INDEX].min(skipna=True).min(skipna=True)
                                       for line_name in acline_dd20_names]
        restrictive_1h_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_1H_COL_INDEX].min(skipna=True).min(skipna=True)
                                      for line_name in acline_dd20_names]
        restrictive_40h_comp_limits = [dataframe_line[dataframe_line[DD20_LINJEDATA_LINENAME_COL_NM].str.contains(line_name)].iloc[:, DD20_COMPONENT_40H_COL_INDEX].min(skipna=True).min(skipna=True)
                                       for line_name in acline_dd20_names]

    except Exception as e:
        log.exception(f"Parsing data from Line dataframe failed with message: '{e}'.")
        raise e

    # --- Make combined dataframe ---
    try:
        # combine data to dictionary and dataframe
        conductor_data_dict = {'ACLINE_EMSNAME_EXPECTED': acline_expected_ets_names,
                               'ACLINE_DD20_NAME': acline_dd20_names,
                               'CONDUCTOR_TYPE': conductor_type,
                               'CONDUCTOR_COUNT': conductor_count,
                               'SYSTEM_COUNT': system_count,
                               'MAX_TEMPERATURE': max_temp,
                               'RESTRICTIVE_CONDUCTOR_LIMIT_CONTINUOUS': restrictive_continuous_conductor_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS': restrictive_continuous_comp_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_15M': restrictive_15m_comp_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_1H': restrictive_1h_comp_limits,
                               'RESTRICTIVE_COMPONENT_LIMIT_40H': restrictive_40h_comp_limits,
                               'RESTRICTIVE_CABLE_LIMIT_CONTINUOUS': restrictive_continuous_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_15M': restrictive_15m_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_1H': restrictive_1h_cable_limits,
                               'RESTRICTIVE_CABLE_LIMIT_40H': restrictive_40h_cable_limits}
        conductor_dataframe = pd.DataFrame.from_dict(conductor_data_dict).fillna('None')
    except Exception as e:
        log.exception(f"Parsing data from Line dataframe failed with message: '{e}'.")
        raise e

    return conductor_dataframe
