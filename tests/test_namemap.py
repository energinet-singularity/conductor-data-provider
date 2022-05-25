import pandas as pd
import os

from app.helpers.parse_namemap import parse_acline_namemap_excelsheet_to_dataframe


def test_parse_acline_namemap_excelsheet_to_dataframe():
    """
    Verifies that Excel file with AC-line name mapping is parsed correctly
    """
    # arrange expected dataframe
    expected_acline_namemap_dict = {
        "DD20 Name": ["E_EEE-FFF_1"],
        "ETS Name": ["E_EEEV-FFF_1"],
        "Comment": ["andet navn i ETS. Forkert model."],
        "User": ["AWI"],
    }
    expected_acline_namemap_dataframe = pd.DataFrame.from_dict(
        expected_acline_namemap_dict
    )

    # act by creating resulting dataframe from valid testfile
    name_mapping_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/valid-testdata/Limits_other.xlsx"
    resulting_acline_namemap_dataframe = parse_acline_namemap_excelsheet_to_dataframe(
        file_path=name_mapping_filepath
    )

    # assert
    assert (
        pd.testing.assert_frame_equal(
            expected_acline_namemap_dataframe, resulting_acline_namemap_dataframe
        )
        is None
    )
