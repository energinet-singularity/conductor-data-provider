import pandas as pd
from numpy import nan
import os

from app.helpers.parse_dd20 import parse_dd20_excelsheets_to_dataframe
from app.helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dataframe
from app.helpers.parse_mrid_map import parse_aclineseg_scada_csvdata_to_dataframe

from app.helpers.combine_data import create_aclinesegment_dataframe


def test_create_aclinesegment_dataframe():
    """
    Verifies creation of aclinesegment dataframe
    """

    # arrange expected dataframe
    expected_aclinesegment_dataframe_dict = {
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
        "ACLINE_NAME_DATASOURCE": [
            "EEE-FFF-1",
            "EEE-FFF-2",
            "GGG-HHH",
            "GGG-HHH",
            "CCC-DDD",
            "III-ÆØÅ",
        ],
        "DATASOURCE": [
            "DD20",
            "DD20",
            "DD20",
            "DD20",
            "DD20",
            "DD20",
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
        "RESTRICT_CONDUCTOR_LIM_CONTINUOUS": [1168, 1131, 1624, 1624, 801, 2413],
        "RESTRICT_COMPONENT_LIM_CONTINUOUS": [400, 1200, 100, 100, 1200, 2400],
        "RESTRICT_COMPONENT_LIM_15M": [415, 1200, 115, 115, 1200, 2400],
        "RESTRICT_COMPONENT_LIM_1H": [460, 1200, 160, 160, 1200, 2400],
        "RESTRICT_COMPONENT_LIM_40H": [440, 1200, 140, 140, 1200, 2400],
        "RESTRICT_CABLE_LIM_CONTINUOUS": [700, 700, nan, nan, nan, nan],
        "RESTRICT_CABLE_LIM_15M": [1100, 1100, nan, nan, nan, nan],
        "RESTRICT_CABLE_LIM_1H": [900, 900, nan, nan, nan, nan],
        "RESTRICT_CABLE_LIM_40H": [800, 800, nan, nan, nan, nan],
    }
    expected_aclinesegment_dataframe = pd.DataFrame.from_dict(
        expected_aclinesegment_dataframe_dict
    )

    # act by creating needed dataframes and parsing them to function
    dd20_file_path = (
        f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/DD20.XLSM"
    )
    dd20_dataframe = parse_dd20_excelsheets_to_dataframe(file_path=dd20_file_path)

    name_mapping_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/Limits_other.xlsx"
    acline_namemap_dataframe = parse_acline_namemap_excelsheet_to_dataframe(
        file_path=name_mapping_filepath
    )

    mrid_mapping_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/seg_line_mrid_PROD.csv"
    acline_to_mrid_dataframe = parse_aclineseg_scada_csvdata_to_dataframe(
        file_path=mrid_mapping_filepath
    )

    resulting_dataframe = create_aclinesegment_dataframe(
        dd20_data=dd20_dataframe,
        dd20_to_scada_name_map=acline_namemap_dataframe,
        scada_aclinesegment_map=acline_to_mrid_dataframe,
    )

    # assert
    assert (
        pd.testing.assert_frame_equal(
            expected_aclinesegment_dataframe, resulting_dataframe
        )
        is None
    )
