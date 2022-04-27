# import pandas as pd
import logging

# Initialize log
log = logging.getLogger(__name__)

# TODO make aclinesegment class


class ACLineProperties():
    # TODO: setters or functions in init which validates input data
    # TODO: https://docs.python.org/3/library/dataclasses.html
    '''
    Class for representing parameteres and restrictions on a AC-line connection between two stations.

    The AC-line is represented by a name alongside parameters, which must be set based on a given datasource.

    Attributes
    ----------
    name : str
        Name of the AC-line.
    name_datasoruce: str
        Name of the AC-line in datasource which are used to set attributes.
    TODO: describe all attributes
    '''

    def __init__(self,
                 acline_name_translated: str,
                 acline_name_datasource: str,
                 datasource: str,
                 conductor_type: str,
                 conductor_count: int,
                 system_count: int,
                 max_temperature: float,
                 restrict_conductor_lim_continuous: float,
                 restrict_component_lim_continuous: float,
                 restrict_component_lim_15m: float,
                 restrict_component_lim_1h: float,
                 restrict_component_lim_40h: float,
                 restrict_cable_lim_continuous: float,
                 restrict_cable_lim_15m: float,
                 restrict_cable_lim_1h: float,
                 restrict_cable_lim_40h: float
                 ):

        self.acline_name_translated = acline_name_translated
        self.acline_name_datasource = acline_name_datasource
        self.datasource = datasource
        self.conductor_type = conductor_type
        self.conductor_count = conductor_count
        self.system_count = system_count
        self.max_temperature = max_temperature
        self.restrict_conductor_lim_continuous = restrict_conductor_lim_continuous
        self.restrict_component_lim_continuous = restrict_component_lim_continuous
        self.restrict_component_lim_15m = restrict_component_lim_15m
        self.restrict_component_lim_1h = restrict_component_lim_1h
        self.restrict_component_lim_40h = restrict_component_lim_40h
        self.restrict_cable_lim_continuous = restrict_cable_lim_continuous
        self.restrict_cable_lim_15m = restrict_cable_lim_15m
        self.restrict_cable_lim_1h = restrict_cable_lim_1h
        self.restrict_cable_lim_40h = restrict_cable_lim_40h

    """
    # MRID
    @property
    def mrid(self) -> str:
        return self.__mrid

    # PARM1
    @property
    def parm1(self) -> str:
        return self.__parm1
    """
