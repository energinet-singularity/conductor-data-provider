import os
from app.helpers.dd20_configuration import DD20Settings
from pydantic import ValidationError

def test_should_load_dd20_settings():

    # Arrange
    expected_line_data_hash = "A"
    expected_station_data_hash = "B"
    expected_dd20_filepath: str = "/xxxx/DD20.XLSM"
    expected_mapping_filepath: str = "/xxxx/Limits_other.xlsx"
    expected_mrid_mapping_filepath: str = "/xxxx/seg_line_mrid_PROD.csv"
    expected_mock_dd20_filepath: str = "/yyyy/DD20.XLSM"
    expected_mock_mapping_filepath: str = "/yyyy/Limits_other.xlsx"
    expected_mock_mrid_mapping_filepath: str = "/yyyy/seg_line_mrid_PROD.csv"
    expected_api_port: int = 9999
    expected_api_dbname: str = "SOME_DB_NAME"
    expected_api_refresh_rate: float = 100
    expected_use_mock_data: bool = False
    expected_debug: bool = True

    # Set all enviornment variables
    os.environ["LINE_DATA_VALID_HASH"] = expected_line_data_hash
    os.environ["STATION_DATA_VALID_HASH"] = expected_station_data_hash
    os.environ["DD20_FILEPATH"] = expected_dd20_filepath
    os.environ["MAPPING_FILEPATH"] = expected_mapping_filepath
    os.environ["MRID_MAPPING_FILEPATH"] = expected_mrid_mapping_filepath
    os.environ["MOCK_DD20_FILEPATH"] = expected_mock_dd20_filepath
    os.environ["MOCK_MAPPING_FILEPATH"] = expected_mock_mapping_filepath
    os.environ["MOCK_MRID_MAPPING_FILEPATH"] = expected_mock_mrid_mapping_filepath
    os.environ["API_PORT"] = str(expected_api_port)
    os.environ["API_DBNAME"] = expected_api_dbname
    os.environ["API_REFRESH_RATE"] = str(expected_api_refresh_rate)
    os.environ["USE_MOCK_DATA"] = str(expected_use_mock_data)
    os.environ["DEBUG"] = str(expected_debug)

    # Act
    settings = DD20Settings()

    # Assert
    assert(settings.line_data_valid_hash == expected_line_data_hash)
    assert(settings.station_data_valid_hash == expected_station_data_hash)
    assert(settings.dd20_filepath == expected_dd20_filepath)
    assert(settings.mapping_filepath == expected_mapping_filepath)
    assert(settings.mrid_mapping_filepath == expected_mrid_mapping_filepath)
    assert(settings.api_port == expected_api_port)
    assert(settings.api_dbname == expected_api_dbname)
    assert(settings.api_refresh_rate == expected_api_refresh_rate)
    assert(settings.use_mock_data == expected_use_mock_data)
    assert(settings.debug == expected_debug)

def test_should_use_mock_data_if_use_mock_data_is_true():

    # Arrange
    expected_line_data_hash = "A"
    expected_station_data_hash = "B"
    expected_dd20_filepath: str = "/xxxx/DD20.XLSM"
    expected_mapping_filepath: str = "/xxxx/Limits_other.xlsx"
    expected_mrid_mapping_filepath: str = "/xxxx/seg_line_mrid_PROD.csv"
    expected_mock_dd20_filepath: str = "/yyyy/DD20.XLSM"
    expected_mock_mapping_filepath: str = "/yyyy/Limits_other.xlsx"
    expected_mock_mrid_mapping_filepath: str = "/yyyy/seg_line_mrid_PROD.csv"
    expected_api_port: int = 9999
    expected_api_dbname: str = "SOME_DB_NAME"
    expected_api_refresh_rate: float = 100
    expected_use_mock_data: bool = True
    expected_debug: bool = True

    # Set all enviornment variables
    os.environ["LINE_DATA_VALID_HASH"] = expected_line_data_hash
    os.environ["STATION_DATA_VALID_HASH"] = expected_station_data_hash
    os.environ["DD20_FILEPATH"] = expected_dd20_filepath
    os.environ["MAPPING_FILEPATH"] = expected_mapping_filepath
    os.environ["MRID_MAPPING_FILEPATH"] = expected_mrid_mapping_filepath
    os.environ["MOCK_DD20_FILEPATH"] = expected_mock_dd20_filepath
    os.environ["MOCK_MAPPING_FILEPATH"] = expected_mock_mapping_filepath
    os.environ["MOCK_MRID_MAPPING_FILEPATH"] = expected_mock_mrid_mapping_filepath
    os.environ["API_PORT"] = str(expected_api_port)
    os.environ["API_DBNAME"] = expected_api_dbname
    os.environ["API_REFRESH_RATE"] = str(expected_api_refresh_rate)
    os.environ["USE_MOCK_DATA"] = str(expected_use_mock_data)
    os.environ["DEBUG"] = str(expected_debug)

    # Act
    settings = DD20Settings()

    # Assert
    assert(settings.use_mock_data == expected_use_mock_data)
    assert(settings.dd20_filepath == expected_mock_dd20_filepath)
    assert(settings.mapping_filepath == expected_mock_mapping_filepath)
    assert(settings.mrid_mapping_filepath == expected_mock_mrid_mapping_filepath)

def test_should_load_default_dd20_settings():

    # Arrange
    expected_line_data_hash = "A"
    expected_station_data_hash = "B"
    expected_dd20_filepath: str = "/input/DD20.XLSM"
    expected_mapping_filepath: str = "/input/Limits_other.xlsx"
    expected_mrid_mapping_filepath: str = "/input/seg_line_mrid_PROD.csv"
    expected_mock_dd20_filepath: str = "../tests/valid-testdata/DD20.xlsm"
    expected_mock_mapping_filepath: str = "../tests/valid-testdata/Limits_other.xlsx"
    expected_mock_mrid_mapping_filepath: str = "../tests/valid-testdata/seg_liine_mrid_PROD.csv"
    expected_api_port: int = 5000
    expected_api_dbname: str = "CONDUCTOR_DATA"
    expected_api_refresh_rate: float = 60
    expected_use_mock_data: bool = False
    expected_debug: bool = False

    # only set settings with no defaults
    os.environ["LINE_DATA_VALID_HASH"] = expected_line_data_hash
    os.environ["STATION_DATA_VALID_HASH"] = expected_station_data_hash
    # remove env vars to force defaults
    os.environ.pop("DD20_FILEPATH", None)
    os.environ.pop("MAPPING_FILEPATH", None)
    os.environ.pop("MRID_MAPPING_FILEPATH", None)
    os.environ.pop("MOCK_DD20_FILEPATH", None)
    os.environ.pop("MOCK_MAPPING_FILEPATH", None)
    os.environ.pop("MOCK_MRID_MAPPING_FILEPATH", None)
    os.environ.pop("API_PORT", None)
    os.environ.pop("API_DBNAME", None)
    os.environ.pop("API_REFRESH_RATE", None)
    os.environ.pop("USE_MOCK_DATA", None)
    os.environ.pop("DEBUG", None)

    # Act
    settings = DD20Settings(_env_file='empty.env')

    # Assert
    assert(settings.line_data_valid_hash == expected_line_data_hash)
    assert(settings.station_data_valid_hash == expected_station_data_hash)
    assert(settings.dd20_filepath == expected_dd20_filepath)
    assert(settings.mapping_filepath == expected_mapping_filepath)
    assert(settings.mrid_mapping_filepath == expected_mrid_mapping_filepath)
    assert(settings.mock_dd20_filepath == expected_mock_dd20_filepath)
    assert(settings.mock_mapping_filepath == expected_mock_mapping_filepath)
    assert(settings.mock_mrid_mapping_filepath == expected_mock_mrid_mapping_filepath)
    assert(settings.api_port == expected_api_port)
    assert(settings.api_dbname == expected_api_dbname)
    assert(settings.api_refresh_rate == expected_api_refresh_rate)
    assert(settings.use_mock_data == expected_use_mock_data)
    assert(settings.debug == expected_debug)

def test_should_raise_error_for_invalid_setting():

    # Arrange
    expected_line_data_hash = "A"
    expected_station_data_hash = "B"
    expected_dd20_filepath: str = "/xxxx/DD20.XLSM"
    expected_mapping_filepath: str = "/xxxx/Limits_other.xlsx"
    expected_mrid_mapping_filepath: str = "/xxxx/seg_line_mrid_PROD.csv"
    expected_mock_dd20_filepath: str = "/yyyy/DD20.XLSM"
    expected_mock_mapping_filepath: str = "/yyyy/Limits_other.xlsx"
    expected_mock_mrid_mapping_filepath: str = "/yyyy/seg_line_mrid_PROD.csv"
    expected_api_port: int = 9999
    expected_api_dbname: str = "SOME_DB_MANE"
    expected_api_refresh_rate: float = 100
    expected_debug: bool = True

    # set bad value
    os.environ["USE_MOCK_DATA"] = "SOME BAD VALUE"

    # Set all enviornment variables
    os.environ["LINE_DATA_VALID_HASH"] = expected_line_data_hash
    os.environ["STATION_DATA_VALID_HASH"] = expected_station_data_hash
    os.environ["DD20_FILEPATH"] = expected_dd20_filepath
    os.environ["MAPPING_FILEPATH"] = expected_mapping_filepath
    os.environ["MRID_MAPPING_FILEPATH"] = expected_mrid_mapping_filepath
    os.environ["MOCK_DD20_FILEPATH"] = expected_mock_dd20_filepath
    os.environ["MOCK_MAPPING_FILEPATH"] = expected_mock_mapping_filepath
    os.environ["MOCK_MRID_MAPPING_FILEPATH"] = expected_mock_mrid_mapping_filepath
    os.environ["API_PORT"] = str(expected_api_port)
    os.environ["API_DBNAME"] = expected_api_dbname
    os.environ["API_REFRESH_RATE"] = str(expected_api_refresh_rate)
    os.environ["DEBUG"] = str(expected_debug)

    exception_caught: ValidationError = None

    # Act
    try:
        settings = DD20Settings()
    except Exception as ex:
        exception_caught = ex

    # Assert
    assert(exception_caught is not None)
    assert(type(exception_caught) is ValidationError)
