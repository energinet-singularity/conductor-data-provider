import pandas as pd
import hashlib


def validate_dd20_format(data_frame: pd.DataFrame, expected_hash: str) -> bool:
    """Compare header hash of dataframe with expected hash value

    Parameters
    ----------
    data_frame: pd.DataFrame
        dd20 data frame station data or line data
    expected_hash: str
        the expected known hash value that must match the computed hash of the dd20 dataframe headers

    Returns
    -------
    bool
        true if hash values match.
    """
    return calculate_dd20_format_hash(data_frame) == expected_hash


def calculate_dd20_format_hash(data_frame: pd.DataFrame) -> str:
    """
    summarizes the hash value for each cell in row
    1,2 (zero indexed) (which are considered static header rows).
    We do this to try to detect if the file format has changed.

    Parameters
    ----------
    data_frame: pd.DataFrame
        dd20 data frame station data or line data

    Returns
    -------
    str
        the hash value of the headers of the dd20 sheet

    """

    DD20_HEADER_ROWS = [1, 2]

    rows = data_frame.iloc[DD20_HEADER_ROWS, :]
    rows_encoded = rows.to_string().encode()
    dd20_header_hash = hashlib.md5(rows_encoded).hexdigest()

    return dd20_header_hash


class DD20FormatError(Exception):
    pass
