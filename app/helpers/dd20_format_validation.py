import pandas as pd
import hashlib


def validate_dd20_format(data_frame: pd.DataFrame, expected_hash: int) -> bool:
    return calculate_dd20_format_hash(data_frame) == expected_hash


def calculate_dd20_format_hash(data_frame: pd.DataFrame) -> str:
    """
    summarizes the hash value for each cell in the
    first 3 rows (which are considered static header rows).
    We do this to try to detect if the file format has changed.
    """

    rows = data_frame.iloc[1:3, :]
    rows_as_string = rows.to_string()
    rows_encoded = rows_as_string.encode()
    dd20_header_hash = hashlib.md5(rows_encoded).hexdigest()

    return dd20_header_hash
