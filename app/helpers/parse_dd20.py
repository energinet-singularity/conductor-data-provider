# Generic modules
import logging
from dataclasses import dataclass

# Modules
import pandas as pd
from singupy.conversion import kv_to_letter

# Initialize log
log = logging.getLogger(__name__)


@dataclass(eq=True)
class ACLineProperties:
    """
    Class for representing parameteres and restrictions on a overhead AC-line connection between two stations.
    The AC-line is represented by a name alongside parameters, which must be set based on a given datasource.

    Attributes
    ----------
    acline_name_translated : str
        Translated name of the AC-line, can be used to alternative naming that the one in datasource.
    acline_name_datasource: str
        Name of the AC-line in datasource which are used to set attributes.
    datasource: str
        Datasoruce for parameteres and restrictions on a AC-line.
    conductor_type: str
        Type name of the conductor used on the AC-line
    conductor_count: int
        Amount of conductors used for the AC-line.
    system_count: int
        Anount of systems in parallel for the AC-line.
    max_temperature: float
        Maximum allowed temperature in celsius degrees for the conductor.
    restrict_conductor_lim_continuous: float
        Allowed continuous ampere loading of conducter.
    restrict_component_lim_continuous: float
        Allowed continuous ampere loading of components along the AC-line.
    restrict_component_lim_15m: float
        Allowed 15 minutes ampere loading of components along the AC-line.
    restrict_component_lim_1h: float
        Allowed 1 hour ampere loading of components along the AC-line.
    restrict_component_lim_40h: float
        Allowed 40 hour ampere loading of components along the AC-line.
    restrict_cable_lim_continuous: float
        Allowed continuous ampere loading of cabling along the AC-line, if any.
    restrict_cable_lim_15m: float
        Allowed 15 minutes ampere loading of cabling along the AC-line, if any.
    restrict_cable_lim_1h: float.
         Allowed 15 minutes ampere loading of cabling along the AC-line, if any.
    restrict_cable_lim_40h: float
         Allowed 15 minutes ampere loading of cabling along the AC-line, if any.
    """
    # TODO: type og value verify i ACLinesegment object
    # TODO: regler for (int værdier skal være mellem 0 og ?, temp mellem 0 og 100, ampere mellem 0 og 9999)
    # TODO: valider hvilke værdier der skal være sat og hvilke der er optional/NaN
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


class DD20StationDataframeParser():
    """
    Class for representing "station data" from DD20 as dictionarys with mapping from each AC-line name
    in dataframe to miscellaneous properties.

    The data "station data" need to be parsed as paramerer "df_station" upon instantiation.
    Dictionarys exists as atributes to the class after initialisation.

    The "station data" is the data presented in sheet "Stationsdata" of DD20 excel file.
    DD20 is a non-standard format containing data for high voltage AC transmission lines.
    Each AC-line is represented by a name alongside with limits for transmission capacity and other parameters.
    A mock example of it can be found in 'tests/valid-testdata/DD20.XLSM'. 

    Attributes
    ----------
    acline_name_list : list
        List of names for AC-lines present in dataframe.
    conductor_kv_level_dict : dict
        Dictionary with mapping from AC-line name to voltagelevel in kV.
    conductor_count_dict : dict
        Dictionary with mapping from AC-line name to amount of conductors.
    system_count_dict : dict
        Dictionary with mapping from AC-line name to amount of parallel systems.
    conductor_type_dict : dict
        Dictionary with mapping from AC-line name to conductor type.
    conductor_max_temp_dict : dict
        Dictionary with mapping from AC-line name to max temperature.
    cablelim_continuous_dict : dict
        Dictionary with mapping from AC-line name to allowed continuous ampere loading of cabling along the AC-line, if any.
    cablelim_15m_dict : dict
        Dictionary with mapping from AC-line name to allowed 15 minutes ampere loading of cabling along the AC-line, if any.
    cablelim_1h_dict : dict
        Dictionary with mapping from AC-line name to allowed 1 hour ampere loading of cabling along the AC-line, if any.
    cablelim_40h_dict : dict
        Dictionary with mapping from AC-line name to allowed 40 hour ampere loading of cabling along the AC-line, if any.

    df_station : pd.DataFrame
        Dataframe containing data from sheet "Stationsdata" of DD20 excel file.
    acline_name_col_nm : str, default='Linjenavn'
        Name of column containing AC-line name.
    kv_col_nm : str, Default='Spændingsniveau'
        Name of column containing voltagelevel in kV.
    conductor_count_col_nm : str, default='Antal fasetråde'
        Name of column containing amount of conductors .
    system_count_col_nm : str, default='Antal systemer'
        Name og column containing amount of parallel systems.
    conductor_type_col_nm : str, default='Ledningstype'
        Name of column containing conductor type.
    conductor_max_temp_col_nm : str, default='Temperatur'
        Name of column containing max temperature.
    cablelim_continuous_col_nm : str, default='Kontinuer'
        Name of column containing allowed continuous ampere loading of cabling along the AC-line, if any.
    cablelim_15m_col_nm : str, default='15 min'
        Name of column containing allowed 15 minutes ampere loading of cabling along the AC-line, if any.
    cablelim_1h_col_nm : str, default='1 time'
        Name of column containing allowed 1 hour ampere loading of cabling along the AC-line, if any.
    cablelim_40h_col_nm : str, default='40 timer'
        Name of column containing allowed 40 hour ampere loading of cabling along the AC-line, if any.
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
        """
        Parameters
        ----------
        df_station : pd.DataFrame
            Dataframe containing station sheet "Stationsdata" of DD20 excel file.
        acline_name_col_nm : str, default='Linjenavn'
            Name of column containing AC-line name.
        kv_col_nm : str, Default='Spændingsniveau'
            Name of column containing voltagelevel in kV.
        conductor_count_col_nm : str, default='Antal fasetråde'
            Name of column containing amount of conductors .
        system_count_col_nm : str, default='Antal systemer'
            Name og column containing amount of parallel systems.
        conductor_type_col_nm : str, default='Ledningstype'
            Name of column containing conductor type.
        conductor_max_temp_col_nm : str, default='Temperatur'
            Name of column containing max temperature.
        cablelim_continuous_col_nm : str, default='Kontinuer'
            Name of column containing allowed continuous ampere loading of cabling along the AC-line, if any.
        cablelim_15m_col_nm : str, default='15 min'
            Name of column containing allowed 15 minutes ampere loading of cabling along the AC-line, if any.
        cablelim_1h_col_nm : str, default='1 time'
            Name of column containing allowed 1 hour ampere loading of cabling along the AC-line, if any.
        cablelim_40h_col_nm : str, default='40 timer'
            Name of column containing allowed 40 hour ampere loading of cabling along the AC-line, if any.
        """

        # Init of parameters
        self.__df_station_source = df_station
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

        # Cleaning dataframe
        self.__df_station_clean = self.__prepare_df_station()

        # Get unique list of acline names present in dataframe
        self.acline_name_list = self.__get_acline_name_list()

        # Init value dicts
        self.conductor_kv_level_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__kv_col_nm)
        self.conductor_count_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__conductor_count_col_nm)
        self.system_count_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__system_count_col_nm)
        self.conductor_type_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__conductor_type_col_nm)
        self.conductor_max_temp_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__conductor_max_temp_col_nm)
        self.cablelim_continuous_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_continuous_col_nm)
        self.cablelim_15m_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_15m_col_nm)
        self.cablelim_1h_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_1h_col_nm)
        self.cablelim_40h_dict = self.__create_acline_name_to_column_single_value_dict(column_name=self.__cablelim_40h_col_nm)


    def __prepare_df_station(self):
        """
        Cleans the dataframe of unneeded data.
        Result is a dataframe containing only one row of data for each AC-line.

        Returns
        -------
        pd.dataframe
            Cleaned dataframe.
        """
        try:
            # 1. Filter dataframe to only contain AC-lines which have a parallel representation by:
            # - Removing rows with no AC-line name
            # - Excluding rows withpot a hyphen in AC-line name, as all AC-line names has one.
            # - Excluding rows without "(N)" in the name, as lines which are not parallel does not contain it.
            df_parallel_lines = self.__df_station_source[(self.__df_station_source[self.__acline_name_col_nm].notna()) &
                                                         (self.__df_station_source[self.__acline_name_col_nm].str.contains("-")) &
                                                         (self.__df_station_source[self.__acline_name_col_nm].str.contains(r'\(N\)'))][self.__acline_name_col_nm]

            # 2. Create list og parallel AC-line names where "(N)" is removed.
            # The "(N)" string are in DD20 to identify them as parallel. The actual name of the AC-Line does not have "(N)" in it.
            # Ie. a parallel line is represented by 2 single parts with name is "GGH-VVV" and one with "GGH-VVV (N)" for the parallel combination.
            # Only the parallel representation is needed.
            acline_parallel_dd20_names = [x.replace('(N)', '').strip() for x in df_parallel_lines.values.tolist()]

            # 3. Return filtered frame by:
            # - Removing rows with no AC-line name
            # - Excluding rows withpot a hyphen in AC-line name, as all AC-line names has one.
            # - Excluding single part representation of AC-lines where a paralle part is present
            df_station_filtered = self.__df_station_source[(self.__df_station_source[self.__acline_name_col_nm].notna()) &
                                                           (self.__df_station_source[self.__acline_name_col_nm].str.contains("-")) &
                                                           ~self.__df_station_source[self.__acline_name_col_nm].isin(acline_parallel_dd20_names)]
            # 4. cleaning frame by:
            # - Removing (N) from values in AC-line name column
            # - Removing spaces from values in AC-line name column
            # TODO: generates warning, fix it
            # https://www.dataquest.io/blog/settingwithcopywarning/
            df_station_filtered.loc[:, self.__acline_name_col_nm] = df_station_filtered[self.__acline_name_col_nm].replace(r"\(N\)", "", regex=True).replace(" ", "", regex=True)

            # TODO: verify only one row is present per ac-line before returning value, since else DD20 format has error

            # 
            return df_station_filtered

        except Exception as e:
            log.exception(f"Preparing DD20 dataframe from Station-data sheet failed with message: '{e}'.")
            raise e


    def __get_acline_name_list(self):
        """
        Create list of unique AC-line names which exist in dataframe.

        Returns
        -------
        list
            List of unique AC-line names.
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
            acline_names = list(set(df_filtered[self.__acline_name_col_nm].values.tolist()))

            return acline_names
        except Exception as e:
            log.exception(f"Getting list of line names present in DD20 line sheet failed with message: '{e}'.")
            raise e

    def __create_acline_name_to_column_single_value_dict(self, column_name: str):
        """ 
        Returns dictionary with mapping from acline names in DD20 to corresponding value from column name.

        Parameters
        ----------
        column_name : str
            Name of column for which value must be extracted.
        
        Returns
        -------
        dict
            Mapping from each AC-line name to value in choosen column.
        """
        try:
            # for each AC line in DD20:
            # - filter dataframe to only rows which has the linename
            # - pick only value for column
            dict = {acline_dd20name: self.__df_station_clean[self.__df_station_clean[self.__acline_name_col_nm] == acline_dd20name][column_name].values[0]
                    for acline_dd20name in self.acline_name_list}
            return dict
        except Exception as e:
            log.exception(f"Getting data column: {column_name} in Station-data sheet failed with message: '{e}'.")
            raise e


class DD20LineDataframeParser():
    """
    Class for representing "line data" from DD20 as dictionarys with mapping from each AC-line name
    in dataframe to miscellaneous properties.

    The data "line data" need to be parsed as parameter "df_line" upon instantiation.
    Dictionarys exists as atributes to the class after initialisation.

    The "line data" is the data presented in sheet "Linjedata - Sommer" of DD20 excel file.
    DD20 is a non-standard format containing data for high voltage AC transmission lines.
    Each AC-line is represented by a name alongside with limits for transmission capacity and other parameters.
    A mock example of it can be found in 'tests/valid-testdata/DD20.XLSM'. 

    Attributes
    ----------
    acline_name_list : list
        List of names for AC-lines present in dataframe.
    conductor_kv_level_dict : dict
        Dictionary with mapping from AC-line name to voltagelevel in kV.
    acline_lim_continuous_dict : dict
        Dictionary with mapping from AC-line name to allowed continuous ampere loading of conducter.
    complim_continuous_dict : dict
        Dictionary with mapping from AC-line name to allowed continuous ampere loading of components along the AC-line.
    complim_15m_dict : dict
        Dictionary with mapping from AC-line name to allowed 15 minutes ampere loading of components along the AC-line.
    complim_1h_dict : dict
        Dictionary with mapping from AC-line name to allowed 1 hour ampere loading of components along the AC-line.
    complim_40h_dict : dict
        Dictionary with mapping from AC-line name to allowed 40 hour ampere loading of components along the AC-line.

    df_line : pd.DataFrame
        Dataframe containing data from sheet "Linjedata - Sommer" of DD20 excel file.
    acline_name_col_nm : str, default='System'
        Name of column containing AC-line name.
    kv_col_nm : str, Default='Spændingsniveau'
        Name of column containing voltagelevel in kV.
    acline_lim_continuous_col_nm : str, Default = 'I-kontinuert'
        Name of column containing allowed continuous ampere loading of conducter.
    system_count_col_nm : str, Default='Antal sys.'
        Name of columns containing system count.
    complim_continuous_col_rng : range, Default=range(41, 55)
        Range of columns which contains allowed continuous ampere loading of components along the AC-line.
    complim_15m_col_rng : range, Default=range(55, 69)
        Range of columns which contains allowed 15 minutes ampere loading of components along the AC-line.
    complim_1h_col_rng : range, Default=range(69, 83)
        Range of columns which contains allowed 1 hour ampere loading of components along the AC-line.
    complim_40h_col_rng : range, Defualt=range(83, 97))
        Range of columns which contains allowed 40 hour ampere loading of components along the AC-line.
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
        """
        Parameters
        ----------
        df_line : pd.DataFrame
            Dataframe containing data from sheet "Linjedata - Sommer" of DD20 excel file.
        acline_name_col_nm : str, default='System'
            Name of column containing AC-line name.
        kv_col_nm : str, Default='Spændingsniveau'
            Name of column containing voltagelevel in kV.
        acline_lim_continuous_col_nm : str, Default = 'I-kontinuert'
            Name of column containing allowed continuous ampere loading of conducter.
        system_count_col_nm : str, Default='Antal sys.'
            Name of columns containing system count.
        complim_continuous_col_rng : range, Default=range(41, 55)
            Range of columns which contains allowed continuous ampere loading of components along the AC-line.
        complim_15m_col_rng : range, Default=range(55, 69)
            Range of columns which contains allowed 15 minutes ampere loading of components along the AC-line.
        complim_1h_col_rng : range, Default=range(69, 83)
            Range of columns which contains allowed 1 hour ampere loading of components along the AC-line.
        complim_40h_col_rng : range, Defualt=range(83, 97))
            Range of columns which contains allowed 40 hour ampere loading of components along the AC-line.
        """

        # Init of parameters
        self.__df_line_soruce = df_line
        self.__acline_name_col_nm = acline_name_col_nm
        self.__kv_col_nm = kv_col_nm
        self.__acline_lim_continuous_col_nm = acline_lim_continuous_col_nm
        self.__system_count_col_nm = system_count_col_nm
        self.__complim_continuous_col_rng = complim_continuous_col_rng
        self.__complim_15m_col_rng = complim_15m_col_rng
        self.__complim_1h_col_rng = complim_1h_col_rng
        self.__complim_40h_col_rng = complim_40h_col_rng

        # Cleaning dataframe
        self.__df_line_clean = self.__prepare_df_line()

        # Get unique list of acline names present in dataframe
        self.acline_name_list = self.__get_acline_name_list()

        # Init value dicts
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
            # 4. cleaning frame by:
            # - Removing (N) from values in AC-line name column
            # - Removing spaces from values in AC-line name column
            # TODO: generates warning, fix it
            df_line_filtered[self.__acline_name_col_nm] = df_line_filtered[self.__acline_name_col_nm].replace(r"\(N\)", "", regex=True).replace(" ", "", regex=True)

            return df_line_filtered

        except Exception as e:
            log.exception(f"Preparing DD20 dataframe from Line-data sheet failed with message: '{e}'.")
            raise e

    def __get_acline_name_list(self):
        """
        Create list of unique AC-line names which exist in dataframe.

        Returns
        -------
        list
            List of unique AC-line names.
        """
        try:
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
            dict = {acline_dd20name: self.__df_line_clean[self.__df_line_clean[self.__acline_name_col_nm] == acline_dd20name]
                    [column_name].min(skipna=True)
                    for acline_dd20name in self.acline_name_list}
            return dict
        except Exception as e:
            log.exception(f"Getting data min column: {column_name} in line-data sheet failed with message: '{e}'.")
            raise e

    def __create_acline_name_to_column_range_min_value_dict(self, column_range: range):
        try:
            dict = {acline_dd20name: self.__df_line_clean[self.__df_line_clean[self.__acline_name_col_nm] == acline_dd20name]
                    .iloc[:, column_range].min(skipna=True).min(skipna=True)
                    for acline_dd20name in self.acline_name_list}
            return dict
        except Exception as e:
            # TODO: proper error
            log.exception(f"Getting ? failed with message: '{e}'.")
            raise e


# TODO: overvej at håndtere data vi 2 nye liste data objekter i stedet for dictionarys
def DD20_to_acline_properties_mapper(data_station: object, data_line: object):
    """
    Data is extracted from sheets "Stationsdata" and "Linjedata - Sommer" are combined into objects.
    A object for each AC line is added to a combined list of object.
    list of the objects can be fetched via?
    All AC line objects are also combinded into a dataframe where the columns represents the atributes of the object.
    It can be fetched via ??
    """
    # Try/except?
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
    # TODO: include kv to account for kv match also?
    names_in_station_but_not_line = list(set(st_acline_names).difference(ln_acline_names))
    names_in_line_but_not_station = list(set(ln_acline_names).difference(st_acline_names))
    # TODO: make with if and exception
    print(f" in station but not line {names_in_station_but_not_line}")
    print(f" in line but not station {names_in_line_but_not_station}")

    # as lines are present in both, just use one
    # TODO: make with regex instead
    acline_name__to_translated_name = {acline_dd20name:
                                       f"{kv_to_letter(st_acline_name_to_conductor_kv_level[acline_dd20name])}_{acline_dd20name.strip()[:len(acline_dd20name.strip())-3]}{acline_dd20name.strip()[-3:].replace('-','_')}"
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
    Wrapper function, maybe put in main? if not then parse parameters via arguments
    
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
    # TODO: how to handle if encoding fails?
    dd20_dataframe_dict = pd.read_excel(io=file_path, sheet_name=DD20_SHEET_LIST, header=DD20_HEADER_INDEX)

    # TODO: use hash function only or both?
    # TODO: build into parser classes or externally?
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
