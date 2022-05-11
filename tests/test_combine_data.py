import pandas as pd
from numpy import nan
import os
import pytest

from app.helpers.combine_data import create_aclinesegment_dataframe



# TEST final merge
# test first columns match, then test each property
def test_create_aclinesegment_dataframe():
    """
    This test verifies creation of aclinesegment dataframe
    parse_dd20_excelsheets_to_dataframe,
    parse_acline_namemap_excelsheet_to_dataframe,
    parse_aclineseg_scada_csvdata_to_dataframe
    """

    pass


expected_dlr_dataframe_dict = {
    "ACLINESEGMENT_MRID": [
        "66b4596e-asfv-tyuy-5478-bd208f26a446",
        "66b4596e-asfv-tyuy-5478-bd208f26a447",
        "66b4596e-asfv-tyuy-5478-bd208f26a451",
        "66b4596e-asfv-tyuy-5478-bd208f26a452",
        "66b4596e-asfv-tyuy-5478-bd208f26a455",
        "66b4596e-asfv-tyuy-5478-bd208f26a457",
    ],
    "LINE_EMSNAME": [
        "E_EEEV-FFF_1",
        "E_EEE-FFF_2",
        "E_GGG-HHH",
        "E_GGG-HHH",
        "D_CCC-DDD",
        "C_III-ÆØÅ",
    ],
    "DLR_ENABLED": [True, True, False, False, True, True],
    "ACLINE_DD20_NAME": [
        "EEE-FFF-1",
        "EEE-FFF-2",
        "GGG-HHH",
        "GGG-HHH",
        "CCC-DDD",
        "III-ÆØÅ",
    ],
    "CONDUCTOR_TYPE": [
        "Conduck",
        "Conduck",
        "Conduck",
        "Conduck",
        "Conduck",
        "Conduck",
    ],
    "CONDUCTOR_COUNT": [2, 1, 1, 1, 1, 1],
    "SYSTEM_COUNT": [1, 1, 2, 2, 1, 1],
    "MAX_TEMPERATURE": [70, 70, 70, 70, 70, 70],
    "RESTRICTIVE_CONDUCTOR_LIMIT_CONTINIOUS": [1168, 1131, 1624, 1624, 801, 2413],
    "RESTRICTIVE_COMPONENT_LIMIT_CONTINUOUS": [1600, 1200, 1250, 1250, 1200, 2400],
    "RESTRICTIVE_COMPONENT_LIMIT_15M": [1600, 1200, 1250, 1250, 1200, 2400],
    "RESTRICTIVE_COMPONENT_LIMIT_1H": [1600, 1200, 1250, 1250, 1200, 2400],
    "RESTRICTIVE_COMPONENT_LIMIT_40H": [1600, 1200, 1250, 1250, 1200, 2400],
    "RESTRICTIVE_CABLE_LIMIT_CONTINUOUS": [700, 700, None, None, None, None],
    "RESTRICTIVE_CABLE_LIMIT_15M": [1100, 1100, None, None, None, None],
    "RESTRICTIVE_CABLE_LIMIT_1H": [900, 900, None, None, None, None],
    "RESTRICTIVE_CABLE_LIMIT_40H": [800, 800, None, None, None, None],
}
expected_dlr_dataframe = pd.DataFrame.from_dict(expected_dlr_dataframe_dict).fillna(
    "None"
)
