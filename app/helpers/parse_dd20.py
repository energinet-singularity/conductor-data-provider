# Generic modules
import logging
from dataclasses import dataclass
from typing import Union

# Modules
import re
import pandas as pd
from singupy.conversion import kv_to_letter as convert_kv_to_letter
import dd20_format_validation

# Initialize log
log = logging.getLogger(__name__)


@dataclass
class ACLineProperties:
    """
    Class for representing parameteres and restrictions on a overhead AC-line connection between two stations.
    The AC-line is represented by a name alongside parameters, which must be set based on a given datasource.

    Attributes
    ----------
    acline_name_translated : str
        Translated name of the AC-line, can be used as alternative to the data source name.
    acline_name_datasource: str
        Name of the AC-line in data source which is used to set attributes.
    datasource: str
        Data source for parameters and restrictions for the AC-line.
    conductor_type: str
        Type name of the conductor used on the AC-line
    conductor_count: int
        Amount of conductors used for the AC-line.
    system_count: int
        Amount of systems in parallel for the AC-line.
    max_temperature: float
        Maximum allowed temperature in celsius degrees for the conductor.
    restrict_conductor_lim_continuous: float
        Allowed continuous ampere load of conductor.
    restrict_component_lim_continuous: float
        Allowed continuous ampere load of components along the AC-line.
    restrict_component_lim_15m: float
        Allowed 15 minutes ampere load of components along the AC-line.
    restrict_component_lim_1h: float
        Allowed 1 hour ampere load of components along the AC-line.
    restrict_component_lim_40h: float
        Allowed 40 hour ampere load of components along the AC-line.
    restrict_cable_lim_continuous: float
        Allowed continuous ampere load of cabling along the AC-line, if any.
    restrict_cable_lim_15m: float
        Allowed 15 minutes ampere load of cabling along the AC-line, if any.
    restrict_cable_lim_1h: float.
         Allowed 15 minutes ampere load of cabling along the AC-line, if any.
    restrict_cable_lim_40h: float
         Allowed 15 minutes ampere load of cabling along the AC-line, if any.
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


class DD20StationDataframeParser:
    """
    Class for parsing "station data" from DD20.
    The dataframe containing "station data" must be passed as parameter "df_station" upon instantiation.

    After instantiation a list af AC-line names are available as attribute.
    Dictionaries containing properties for the AC-lines can be fetched via methods.

    The "station data" is the data presented in sheet "Stationsdata" of DD20 excel file.
    DD20 is a non-standard format containing data for high voltage AC transmission lines.
    Each AC-line is represented by a name alongside limits for transmission capacity and other parameters.
    A mock example of it can be found in 'tests/valid-testdata/DD20.XLSM'.

    Attributes
    ----------
    acline_name_list : list
        Sorted list of unique names for AC-lines present in the dataframe.

    Methods:
    ----------
    get_conductor_kv_level_dict()
        Returns a dictionary with mapping from AC-line name to voltage level in kV.
    get_conductor_count_dict()
        Returns dictionary with mapping from AC-line name to amount of conductors.
    get_system_count_dict()
        Returns dictionary with mapping from AC-line name to amount of parallel systems.
    get_conductor_type_dict()
        Returns dictionary with mapping from AC-line name to conductor type.
    get_conductor_max_temp_dict()
        Returns dictionary with mapping from AC-line name to max temperature.
    get_cablelim_continuous_dict()
        Returns dictionary with mapping from AC-line name to allowed continuous ampere load of cabling along the AC-line.
    get_cablelim_15m_dict()
        Returns dictionary with mapping from AC-line name to allowed 15 minutes ampere load of cabling along the AC-line.
    get_cablelim_1h_dict()
        Returns dictionary with mapping from AC-line name to allowed 1 hour ampere load of cabling along the AC-line.
    get_cablelim_40h_dict()
        Returns dictionary with mapping from AC-line name to allowed 40 hour ampere load of cabling along the AC-line.
    """

    def __init__(
        self,
        df_station: pd.DataFrame,
        acline_name_col_nm: str = "Linjenavn",
        kv_col_nm: str = "Spændingsniveau",
        conductor_count_col_nm: str = "Antal fasetråde",
        system_count_col_nm: str = "Antal systemer",
        conductor_type_col_nm: str = "Ledningstype",
        conductor_max_temp_col_nm: str = "Temperatur",
        cablelim_continuous_col_nm: str = "Kontinuer",
        cablelim_15m_col_nm: str = "15 min",
        cablelim_1h_col_nm: str = "1 time",
        cablelim_40h_col_nm: str = "40 timer",
    ):
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
            Name of column containing allowed continuous ampere load of cabling along the AC-line, if any.
        cablelim_15m_col_nm : str, default='15 min'
            Name of column containing allowed 15 minutes ampere load of cabling along the AC-line, if any.
        cablelim_1h_col_nm : str, default='1 time'
            Name of column containing allowed 1 hour ampere load of cabling along the AC-line, if any.
        cablelim_40h_col_nm : str, default='40 timer'
            Name of column containing allowed 40 hour ampere load of cabling along the AC-line, if any.
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

    def get_conductor_kv_level_dict(self) -> dict[str, str]:
        """
        Returns dictionary with mapping from AC-line name to voltagelevel in kV.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__kv_col_nm
        )

    def get_conductor_count_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to amount of conductors.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__conductor_count_col_nm
        )

    def get_system_count_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to amount of parallel systems.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__system_count_col_nm
        )

    def get_conductor_type_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to conductor type.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__conductor_type_col_nm
        )

    def get_conductor_max_temp_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to max temperature.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__conductor_max_temp_col_nm
        )

    def get_cablelim_continuous_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to allowed continuous ampere load of cabling along the AC-line.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__cablelim_continuous_col_nm
        )

    def get_cablelim_15m_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to allowed 15 minutes ampere load of cabling along the AC-line.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__cablelim_15m_col_nm
        )

    def get_cablelim_1h_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to allowed 1 hour ampere load of cabling along the AC-line.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__cablelim_1h_col_nm
        )

    def get_cablelim_40h_dict(self) -> dict:
        """
        Returns dictionary with mapping from AC-line name to allowed 40 hour ampere load of cabling along the AC-line.
        """
        return self.__create_acline_name_to_column_single_value_dict(
            column_name=self.__cablelim_40h_col_nm
        )

    def __prepare_df_station(self) -> pd.DataFrame:
        """
        Cleans the dataframe of unneeded data.
        Result is a dataframe containing only one row of data for each AC-line.

        Returns
        -------
        pd.dataframe
            Cleaned dataframe.
        """
        try:
            """
            1. Filter dataframe to only contain AC-lines which have a parallel representation by:
            - Removing rows with no AC-line name
            - Excluding rows without a hyphen in AC-line name, as all valid AC-line names has one.
            - Excluding rows without "(N)" in the name, as parallel lines contain this.
            """
            df_parallel_lines = self.__df_station_source[
                (self.__df_station_source[self.__acline_name_col_nm].notna())
                & (
                    self.__df_station_source[self.__acline_name_col_nm].str.contains(
                        "-"
                    )
                )
                & (
                    self.__df_station_source[self.__acline_name_col_nm].str.contains(
                        r"\(N\)"
                    )
                )
            ][self.__acline_name_col_nm]

            """
            2. Create list of parallel AC-line names where "(N)" is removed:
            - The "(N)" in DD20 identifies a line as parallel. Actual name of the AC-Line does not have "(N)" in it.
            - I.e. a parallel line is represented by 2 single parts with names
            "GGH-VVV" and one with "GGH-VVV (N)" for the parallel combination.
            - Only the parallel representation is needed.
            """
            acline_parallel_dd20_names = [
                x.replace("(N)", "").strip() for x in df_parallel_lines.values.tolist()
            ]

            """
            3. Return filtered frame by:
            - Removing rows with no AC-line name
            - Excluding rows without a hyphen in AC-line name, as all valid AC-line names have one.
            - Excluding single part representation of AC-lines where a parallel part is present
            """
            df_station_filtered = self.__df_station_source[
                (self.__df_station_source[self.__acline_name_col_nm].notna())
                & (
                    self.__df_station_source[self.__acline_name_col_nm].str.contains(
                        "-"
                    )
                )
                & ~self.__df_station_source[self.__acline_name_col_nm].isin(
                    acline_parallel_dd20_names
                )
            ]
            """
            4. cleaning frame by:
            - Removing (N) from values in AC-line name column
            - Removing spaces from values in AC-line name column
            """
            df_station_filtered.loc[:, self.__acline_name_col_nm] = (
                df_station_filtered[self.__acline_name_col_nm]
                .replace(r"\(N\)", "", regex=True)
                .replace(" ", "", regex=True)
            )

            return df_station_filtered

        except Exception as e:
            log.exception(
                f"Preparing DD20 dataframe from Station-data sheet failed with message: '{e}'."
            )
            raise e

    def __get_acline_name_list(self) -> list[str]:
        """
        Create sorted list of unique AC-line names which exist in the included dataframe.

        Returns
        -------
        list
            Sorted list of unique AC-line names.
        """
        try:
            """
            Filtering dataframe on 'linename' column to get only unique AC-line names by:
            - Removing rows with null
            - Removing rows not containing '-', since AC-line names always contain this character
            - Removing rows with '(N)', since it is a parallel AC-line representation in DD20 format
            """
            df_filtered = self.__df_station_source[
                (self.__df_station_source[self.__acline_name_col_nm].notna())
                & (
                    self.__df_station_source[self.__acline_name_col_nm].str.contains(
                        "-"
                    )
                )
            ]
            df_filtered = df_filtered[
                ~(df_filtered[self.__acline_name_col_nm].str.contains(r"\(N\)"))
            ]

            # Return sorted list of unique DD20 names
            return sorted(
                list(set(df_filtered[self.__acline_name_col_nm].values.tolist()))
            )
        except Exception as e:
            log.exception(
                f"Getting list of AC-line names present in DD20 station sheet failed with message: '{e}'."
            )
            raise e

    def __create_acline_name_to_column_single_value_dict(
        self, column_name: str
    ) -> dict[str, Union[str, float]]:
        """
        Returns dictionary with mapping from AC-line names in DD20 to corresponding value from column name.

        Parameters
        ----------
        column_name : str
            Name of column for which value must be extracted.

        Returns
        -------
        dict[str, union(str, float)]
            Mapping from each AC-line name to value in choosen column.
        """
        try:
            """
            For each AC-line in DD20:
            - filter dataframe so it only contains rows which have the AC-line name
            - pick only value for column
            """
            return {
                acline_dd20name: self.__df_station_clean[
                    self.__df_station_clean[self.__acline_name_col_nm]
                    == acline_dd20name
                ][column_name].values[0]
                for acline_dd20name in self.acline_name_list
            }
        except Exception as e:
            log.exception(
                f"Getting data column: {column_name} in Station-data sheet failed with message: '{e}'."
            )
            raise e


class DD20LineDataframeParser:
    """
    Class for parsing "line data" from DD20.
    The dataframe containing "line data" must be passed as parameter "df_line" upon instantiation.

    After instantiaton a list af AC-line name are availiable as attribute.
    Dictionarys with mapping from each AC-line name to miscellaneous properties can be fetched via methods.

    The "station data" is the data presented in sheet "Linjedata - Sommer" of DD20 excel file.
    DD20 is a non-standard format containing data for high voltage AC transmission lines.
    Each AC-line is represented by a name alongside with limits for transmission capacity and other parameters.
    A mock example of it can be found in 'tests/valid-testdata/DD20.XLSM'.

    Attributes
    ----------
    acline_name_list : list
        List of names for AC-lines present in dataframe.

    Methods:
    ----------
    get_conductor_kv_level_dict()
        Returns dictionary with mapping from AC-line name to voltagelevel in kV.
    acline_lim_continuous_dict()
        Returns dictionary with mapping from AC-line name to allowed continuous ampere load of conductor.
    complim_continuous_dict()
        Returns dictionary with mapping from AC-line name to allowed continuous ampere load of components along the AC-line.
    complim_15m_dict()
        Returns dictionary with mapping from AC-line name to allowed 15 minutes ampere load of components along the AC-line.
    complim_1h_dict()
        Returns dictionary with mapping from AC-line name to allowed 1 hour ampere load of components along the AC-line.
    complim_40h_dict()
        Returns dictionary with mapping from AC-line name to allowed 40 hour ampere load of components along the AC-line.
    """

    def __init__(
        self,
        df_line: pd.DataFrame,
        acline_name_col_nm: str = "System",
        kv_col_nm: str = "Spændingsniveau",
        acline_lim_continuous_col_nm: str = "I-kontinuert",
        system_count_col_nm: str = "Antal sys.",
        complim_continuous_col_rng: range = range(41, 55),
        complim_15m_col_rng: range = range(55, 69),
        complim_1h_col_rng: range = range(69, 83),
        complim_40h_col_rng: range = range(83, 97),
    ):
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
            Name of column containing allowed continuous ampere load of conductor.
        system_count_col_nm : str, Default='Antal sys.'
            Name of columns containing system count.
        complim_continuous_col_rng : range, Default=range(41, 55)
            Range of columns which contains allowed continuous ampere load of components along the AC-line.
        complim_15m_col_rng : range, Default=range(55, 69)
            Range of columns which contains allowed 15 minutes ampere load of components along the AC-line.
        complim_1h_col_rng : range, Default=range(69, 83)
            Range of columns which contains allowed 1 hour ampere load of components along the AC-line.
        complim_40h_col_rng : range, Defualt=range(83, 97))
            Range of columns which contains allowed 40 hour ampere load of components along the AC-line.
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

    def get_conductor_kv_level_dict(self):
        """
        Returns dictionary with mapping from AC-line name to voltagelevel in kV.
        """
        return self.__create_acline_name_to_column_min_value_dict(
            column_name=self.__kv_col_nm
        )

    def get_acline_lim_continuous_dict(self):
        """
        Returns dictionary with mapping from AC-line name to allowed
        continuous ampere load of conductor.
        """
        return self.__create_acline_name_to_column_min_value_dict(
            column_name=self.__acline_lim_continuous_col_nm
        )

    def get_complim_continuous_dict(self):
        """
        Returns dictionary with mapping from AC-line name to allowed
        continuous ampere load of components along the AC-line.
        """
        return self.__create_acline_name_to_column_range_min_value_dict(
            column_range=self.__complim_continuous_col_rng
        )

    def get_complim_15m_dict(self):
        """
        Returns dictionary with mapping from AC-line name to
        allowed 15 minutes ampere load of components along the AC-line.
        """
        return self.__create_acline_name_to_column_range_min_value_dict(
            column_range=self.__complim_15m_col_rng
        )

    def get_complim_1h_dict(self):
        """
        Returns dictionary with mapping from AC-line name to allowed
        1 hour ampere load of components along the AC-line.
        """
        return self.__create_acline_name_to_column_range_min_value_dict(
            column_range=self.__complim_1h_col_rng
        )

    def get_complim_40h_dict(self):
        """
        Returns dictionary with mapping from AC-line name to allowed
        40 hour ampere load of components along the AC-line.
        """
        return self.__create_acline_name_to_column_range_min_value_dict(
            column_range=self.__complim_40h_col_rng
        )

    def __prepare_df_line(self):
        """
        Cleans the dataframe of unneeded data.
        Result is a dataframe containing only one row of data for each AC-line.

        Returns
        -------
        pd.dataframe
            Cleaned dataframe.
        """
        try:
            """
            Filtering dataframe on 'linename' column to get only unique AC-line names by:
            - Removing rows with null
            - Removing rows not containing '-', since AC-line names always contain this character
            - Remove single part of parallel AC-line representation from sheet (AC-lines with . in antal sys)
            """
            df_line_filtered = self.__df_line_soruce[
                (self.__df_line_soruce[self.__acline_name_col_nm].notna())
                & (self.__df_line_soruce[self.__acline_name_col_nm].str.contains("-"))
                & ~(
                    self.__df_line_soruce[self.__system_count_col_nm].str.contains(
                        ".", na=False
                    )
                )
            ]
            """
            Cleaning frame by:
            - Removing (N) from values in AC-line name column
            - Removing spaces from values in AC-line name column
            """
            df_line_filtered[self.__acline_name_col_nm] = (
                df_line_filtered[self.__acline_name_col_nm]
                .replace(r"\(N\)", "", regex=True)
                .replace(" ", "", regex=True)
            )

            return df_line_filtered

        except Exception as e:
            log.exception(
                f"Preparing DD20 dataframe from Line-data sheet failed with message: '{e}'."
            )
            raise e

    def __get_acline_name_list(self):
        """
        Create sorted list of unique AC-line names which exist in dataframe.

        Returns
        -------
        list
            Sorted list of unique AC-line names.
        """
        try:
            # extract line names from dataframe
            acline_names = self.__df_line_clean[
                self.__acline_name_col_nm
            ].values.tolist()

            # remove string identifying them as parallel to have only the name
            acline_names_cleaned = [x.replace("(N)", "").strip() for x in acline_names]

            # Return sorted list of unique DD20 names
            acline_names_list = sorted(list(set(acline_names_cleaned)))
            return acline_names_list
        except Exception as e:
            log.exception(
                f"Getting list of AC-line names present in DD20 line sheet failed with message: '{e}'."
            )
            raise e

    def __create_acline_name_to_column_min_value_dict(self, column_name: str):
        """
        Returns dictionary with mapping from AC-line names in DD20
        to minimum values of choosen column for all rows related to AC-line.

        Parameters
        ----------
        column_name : str
            Name of column for which minimum value must be fetched.

        Returns
        -------
        dict
            Mapping from each AC-line name to minimum value of choosen column.
        """
        try:
            """
            For each AC-line in DD20:
            - filter dataframe to only rows which has the AC-linename
            - pick only minimum value for column value in all rows related to AC-linename
            """
            return {
                acline_dd20name: self.__df_line_clean[
                    self.__df_line_clean[self.__acline_name_col_nm] == acline_dd20name
                ][column_name].min(skipna=True)
                for acline_dd20name in self.acline_name_list
            }
        except Exception as e:
            log.exception(
                f"Getting minimum value of column: {column_name} in line-data sheet failed with message: '{e}'."
            )
            raise e

    def __create_acline_name_to_column_range_min_value_dict(self, column_range: range):
        """
        Returns dictionary with mapping from AC-line names in DD20 to minimum value in the column range
        for all rows related and columns to AC-line.

        Parameters
        ----------
        column_range : range
            Range of column for which minimum value must be fetched.

        Returns
        -------
        dict
            Mapping from each AC-line name to minimum value of choosen column range.
        """
        try:
            """
            For each AC-line in DD20:
            - filter dataframe to only rows which has the AC-line name
            - filter dataframe to only contain column in range
            - pick minimum value for all columns and rows
            """
            return {
                acline_dd20name: self.__df_line_clean[
                    self.__df_line_clean[self.__acline_name_col_nm] == acline_dd20name
                ]
                .iloc[:, column_range]
                .min(skipna=True)
                .min(skipna=True)
                for acline_dd20name in self.acline_name_list
            }
        except Exception as e:
            log.exception(
                f"Getting minimum value of column_range: {column_range} in line sheet failed with message: '{e}'."
            )
            raise e


def DD20_to_acline_properties_mapper(
    data_station: DD20StationDataframeParser, data_line: DD20LineDataframeParser
):
    """
    DD20 station and line data is extracted from parsed objects.
    The data is combined per AC-line present in the objects and returned as a list of objects with one object per AC-line.
    Both objects need to contain the same AC-lines, since else a format error has occurred and properties can't be mapped.


    Parameters
    ----------
    data_station : class
        Object containing station data from DD20.
        Must be instantiated with D20StationDataframeParser.
    data_line : class
        Object containing line data from DD20.
        Must be instantiated with D20LineDataframeParser.

    Returns
    -------
    acline_objects : list
        List of objects containing combined data from station and line.
        One object will exist per AC-line.
    """
    try:
        # Create lists with AC-Line names present in object from station and line
        station_acline_names = data_station.acline_name_list
        line_acline_names = data_line.acline_name_list

        # Verify that the same names are present in both station and line data, since else DD20 format has an error.
        names_in_station_but_not_line = list(
            set(station_acline_names).difference(line_acline_names)
        )
        if names_in_station_but_not_line:
            raise ValueError(
                f"The following AC-line names are present in station "
                + "but not line sheet of DD20: {names_in_station_but_not_line}."
            )

        names_in_line_but_not_station = list(
            set(line_acline_names).difference(station_acline_names)
        )
        if names_in_line_but_not_station:
            raise ValueError(
                f"The following AC-line names are present in line "
                + "but not station sheet of DD20: {names_in_line_but_not_station}."
            )

        # Initialize AC-Line properties mapping dictionaries via methods on objects
        acline_name_to_conductor_count = data_station.get_conductor_count_dict()
        acline_name_to_system_count = data_station.get_system_count_dict()
        acline_name_to_conductor_type = data_station.get_conductor_type_dict()
        acline_name_to_conductor_max_temp = data_station.get_conductor_max_temp_dict()
        acline_name_to_cablelim_continuous = data_station.get_cablelim_continuous_dict()
        acline_name_to_cablelim_15m = data_station.get_cablelim_15m_dict()
        acline_name_to_cablelim_1h = data_station.get_cablelim_1h_dict()
        acline_name_to_cablelim_40h = data_station.get_cablelim_40h_dict()
        acline_name_to_lim_continuous = data_line.get_acline_lim_continuous_dict()
        acline_name_to_complim_continuous = data_line.get_complim_continuous_dict()
        acline_name_to_complim_15m = data_line.get_complim_15m_dict()
        acline_name_to_complim_1h = data_line.get_complim_1h_dict()
        acline_name_to_complim_40h = data_line.get_complim_40h_dict()

        # Init kV mapping dict (name list verified identical, so okay to just use one of them)
        st_acline_name_to_conductor_kv_level = (
            data_station.get_conductor_kv_level_dict()
        )

        """
        Translation of AC-line names from DD20 datasource to desired format using Regex.
        I.e 132 kV line with data source name "EEE-FFF-2" is translated to "E_EEE-FFF_2"

        Regex expression does the following:
        (?P<STN1>\\w{3,4}?) makes a group 'STN1' and input a word between 3-4 chars
        (?P<STN2>\\w{3,4}?) makes a group 'STN2' and input a word between 3-4 chars
        (?P<id>\\w)? makes a group 'id' and if there is a word in the end of the name it stores it
        """
        acline_name_to_translated_name = {}
        untranslated_acline_names = []
        REGEX = r"^(?P<STN1>\w{3,4})-(?P<STN2>\w{3,4})-?(?P<id>\w)?$"

        for acline_dd20name in station_acline_names:
            match = re.match(REGEX, acline_dd20name)
            if match:
                # Converting the extracted voltage to a letter
                volt_letter = f"{convert_kv_to_letter(st_acline_name_to_conductor_kv_level[acline_dd20name])}"

                # Restructuring name to agreed upon standard
                translated_ac_line_name = (
                    f"{volt_letter}_{match.group('STN1')}-{match.group('STN2')}"
                )

                # Add index of line to name, if it is present
                if match.group("id") is not None:
                    translated_ac_line_name += f"_{match.group('id')}"
                acline_name_to_translated_name[
                    acline_dd20name
                ] = translated_ac_line_name
            else:
                untranslated_acline_names.append(acline_dd20name)

        # Throw an error if there are untranslated names, as it indicates a format error
        if untranslated_acline_names:
            raise ValueError(
                f"The following AC-line names could not be translated due to unepxected format:{untranslated_acline_names}"
            )
        else:
            log.info("All names from the acline_dd20name column have been translated.")

        # Map station and line data to list with objects of the type "ACLineProperties" dataclass.
        acline_objects = [
            ACLineProperties(
                acline_name_translated=acline_name_to_translated_name[acline_dd20name],
                acline_name_datasource=acline_dd20name,
                datasource="DD20",
                conductor_type=acline_name_to_conductor_type[acline_dd20name],
                conductor_count=acline_name_to_conductor_count[acline_dd20name],
                system_count=acline_name_to_system_count[acline_dd20name],
                max_temperature=acline_name_to_conductor_max_temp[acline_dd20name],
                restrict_cable_lim_continuous=acline_name_to_cablelim_continuous[
                    acline_dd20name
                ],
                restrict_cable_lim_15m=acline_name_to_cablelim_15m[acline_dd20name],
                restrict_cable_lim_1h=acline_name_to_cablelim_1h[acline_dd20name],
                restrict_cable_lim_40h=acline_name_to_cablelim_40h[acline_dd20name],
                restrict_conductor_lim_continuous=acline_name_to_lim_continuous[
                    acline_dd20name
                ],
                restrict_component_lim_continuous=acline_name_to_complim_continuous[
                    acline_dd20name
                ],
                restrict_component_lim_15m=acline_name_to_complim_15m[acline_dd20name],
                restrict_component_lim_1h=acline_name_to_complim_1h[acline_dd20name],
                restrict_component_lim_40h=acline_name_to_complim_40h[acline_dd20name],
            )
            for acline_dd20name in station_acline_names
        ]
        return acline_objects

    except Exception as e:
        log.exception(
            f"Mapping DD20 data from station and line data to common object failed with message: '{e}'."
        )
        raise e


def parse_dd20_excelsheets_to_dataframe(
    file_path: str,
    header_index: int = 1,
    sheetname_linedata: str = "Linjedata - Sommer",
    sheetname_stationsdata: str = "Stationsdata",
    line_data_valid_format_hash_value = "9cf51349b6b13d3c52deb66bf569eb49", # todo refactor and move to env variables
    station_data_valid_format_hash_value = "f06edffbc927aea71f0a501f520cf583" # todo refactor and move to env variables
) -> pd.DataFrame:
    """
    Extract conductor data from DD20 excel-sheets and return it to one combined dataframe.
    The source data is DD20, which has a non-standard format so customized cleaning and extraction from it is needed.

    Parameters
    ----------
    file_path : str
        Path of DD20 excel-file.
    header_index : int, Default = 1
        (optional) Index header of DD20 excel sheets.
    sheetname_linedata : str, Default = "Linjedata - Sommer"
        (optional) Name of excel sheet in DD20 containing line data.
    sheetname_stationdata : str, Default = "Stationsdata"
        (optional) Name of excel sheet in DD20 containing station data.

    Returns
    -------
    pd.Dataframe
        Dataframe containg selected data from DD20, where each row represents an AC-line.
    """
    # Parsing data from DD20 to dataframe dictionary, with mapping from sheet to dataframe
    dd20_dataframe_dict = pd.read_excel(
        io=file_path,
        sheet_name=[sheetname_linedata, sheetname_stationsdata],
        header=header_index,
    )

    # Instantiation of objects for parsing data from station and line sheets of DD20
    data_station = DD20StationDataframeParser(
        df_station=dd20_dataframe_dict[sheetname_stationsdata]
    )

    if not dd20_format_validation.validate_dd20_format(data_station, station_data_valid_format_hash_value):
        error_message = f"invalid dd20 file format detected for {sheetname_stationsdata}"
        log.critical(error_message) # toto improve error message
        raise dd20_format_validation.DD20FormatError(error_message) 


    data_line = DD20LineDataframeParser(df_line=dd20_dataframe_dict[sheetname_linedata])

    if not dd20_format_validation.validate_dd20_format(data_line, line_data_valid_format_hash_value):
        error_message = f"invalid dd20 file format detected for {sheetname_linedata}"
        log.critical(error_message) # toto improve error message
        raise dd20_format_validation.DD20FormatError(error_message) 

    # Combining station and line data into a list of objects, where each object represents an AC-line
    acline_objects = DD20_to_acline_properties_mapper(
        data_station=data_station, data_line=data_line
    )

    # Creating dataframe from list of objects
    dd20_dataframe = pd.DataFrame(data=[acline.__dict__ for acline in acline_objects])

    return dd20_dataframe
