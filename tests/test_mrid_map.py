import pandas as pd
import os

from app.helpers.parse_mrid_map import parse_aclineseg_scada_csvdata_to_dataframe

def test_parse_aclineseg_scada_csvdata_to_dataframe():
    """
    This test verfies that CSV file with aclineseg mapping is parsed correcrtly
    """
    # expected dataframe
    expected_lineseg_to_mrid_dict = {
        "ACLINESEGMENT_MRID": [
            "66b4596e-asfv-tyuy-5478-bd208f26a446",
            "66b4596e-asfv-tyuy-5478-bd208f26a447",
            "66b4596e-asfv-tyuy-5478-bd208f26a451",
            "66b4596e-asfv-tyuy-5478-bd208f26a452",
            "66b4596e-asfv-tyuy-5478-bd208f26a455",
            "66b4596e-asfv-tyuy-5478-bd208f26a457",
            "66b4596e-asfv-tyuy-5478-bd208f26a459",
        ],
        "LINE_EMSNAME": [
            "E_EEEV-FFF_1",
            "E_EEE-FFF_2",
            "E_GGG-HHH",
            "E_GGG-HHH",
            "D_CCC-DDD",
            "C_III-ÆØÅ",
            "C_ASK-ERS",
        ],
        "DLR_ENABLED": [True, True, False, False, True, True, True],
    }
    expected_lineseg_to_mrid_dataframe = pd.DataFrame.from_dict(
        expected_lineseg_to_mrid_dict
    )

    # resulting dataframe from valid testfile
    mrid_mapping_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/seg_line_mrid_PROD.csv"
    resulting_lineseg_to_mrid_dataframe = parse_aclineseg_scada_csvdata_to_dataframe(
        file_path=mrid_mapping_filepath
    )

    # assert
    assert resulting_lineseg_to_mrid_dataframe.equals(
        expected_lineseg_to_mrid_dataframe
    )
