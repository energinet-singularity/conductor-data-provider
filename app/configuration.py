import os
from pydantic import BaseSettings, root_validator

class DD20Settings(BaseSettings):
    """BaseSetting superclass for managing configuration"""

    debug: bool = False
    use_mock_data: bool = False
    mock_dd20_filepath: str = "valid-testdata/DD20.XLSM"
    mock_dd20_mapping_filepath: str = "valid-testdata/Limits_other.xlsx"
    mock_mrid_mapping_filepath: str = "valid-testdata/seg_line_mrid_PROD.csv"
    dd20_filepath: str = "/input/DD20.XLSM"
    dd20_mapping_filepath: str = "/input/Limits_other.xlsx"
    mrid_mapping_filepath: str = "/input/seg_line_mrid_PROD.csv"
    station_data_valid_hash: str = "6ac10cff51c6dbc586e729e10b943854"
    line_data_valid_hash: str = "86e61101fa327e1b4f769c26300be01f"
    api_port: int = 5000
    api_dbname: str = "CONDUCTOR_DATA"
    api_refresh_rate: float = 60

    @root_validator(pre=False)
    def assign_mock_data(cls, values):

        assert "use_mock_data" in values, "use_mock_data is invalid or missing"

        use_mock_data = bool(values["use_mock_data"])
        if use_mock_data:
            values["dd20_filepath"] = values["mock_dd20_filepath"]
            values["dd20_mapping_filepath"] = values["mock_dd20_mapping_filepath"]
            values["mrid_mapping_filepath"] = values["mock_mrid_mapping_filepath"]

        return values

    # Configure how envionment .env file should be parsed
    class Config:
        env_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], ".env")
        env_file_encoding = 'utf-8'
        env_prefix = ""
        case_sensitive = False
