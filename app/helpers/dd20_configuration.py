from dataclasses import dataclass
from pydantic import BaseSettings, root_validator, Field


class DD20Settings(BaseSettings):
    """Simple dataclass for setting and storing code/script configuration
    """
    debug: bool = False
    use_mock_data: bool = False
    mock_dd20_filepath: str = "../tests/valid-testdata/DD20.xlsm"
    mock_mapping_filepath: str = "../tests/valid-testdata/Limits_other.xlsx"
    mock_mrid_mapping_filepath: str = "../tests/valid-testdata/seg_liine_mrid_PROD.csv"
    dd20_filepath: str = "/input/DD20.XLSM"
    mapping_filepath: str = "/input/Limits_other.xlsx"
    mrid_mapping_filepath: str = "/input/seg_line_mrid_PROD.csv"
    station_data_valid_hash: str
    line_data_valid_hash: str
    api_port: int = 5000
    api_dbname: str = "CONDUCTOR_DATA"
    api_refresh_rate: float = 60

    @root_validator(pre=False)
    def assign_mock_data(cls, values):

        assert "use_mock_data" in values, "use_mock_data is invalid or missing"

        use_mock_data = bool(values["use_mock_data"])
        if(use_mock_data):
            values["dd20_filepath"] = values["mock_dd20_filepath"]
            values["mapping_filepath"] = values["mock_mapping_filepath"]
            values["mrid_mapping_filepath"] = values["mock_mrid_mapping_filepath"]

        return values

    # Configure how envionment variables should be parsed
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = ""
        case_sensitive = False
