from distutils.command.config import config
import os
from app.configuration import DD20Settings
from pydantic import ValidationError

def test_should_load_dd20_settings():

    # Arrange
    expected_settings = arrange_dd20_settings()
    set_dd20_environment_variables(expected_settings)

    # Act
    settings = DD20Settings()

    # Assert
    assert(settings == expected_settings)

def test_should_use_mock_data_if_use_mock_data_is_true():

    # Arrange
    expected_settings = arrange_dd20_settings()

    expected_settings.use_mock_data = True

    set_dd20_environment_variables(expected_settings)

    # Act
    settings = DD20Settings()

    # Assert
    assert(settings.use_mock_data == expected_settings.use_mock_data)
    assert(settings.dd20_filepath == expected_settings.mock_dd20_filepath)
    assert(settings.dd20_mapping_filepath == expected_settings.mock_dd20_mapping_filepath)
    assert(settings.mrid_mapping_filepath == expected_settings.mock_mrid_mapping_filepath)

def test_should_load_default_dd20_settings():

    # Arrange
    expected_settings = arrange_default_dd20_settings()

    # remove env vars to force defaults
    clear_dd20_environment_variables()

    # Act
    settings = DD20Settings(_env_file='empty.env')

    # Assert
    assert(settings == expected_settings)

def test_should_raise_error_for_invalid_setting():

    # Arrange
    expected_settings = arrange_dd20_settings()

    # set bad value
    expected_settings.use_mock_data = "SOME BAD VALUE"

    set_dd20_environment_variables(expected_settings)

    exception_caught: ValidationError = None

    # Act
    try:
        settings = DD20Settings()
    except Exception as ex:
        exception_caught = ex

    # Assert
    assert(exception_caught is not None)
    assert(type(exception_caught) is ValidationError)


def arrange_dd20_settings() -> DD20Settings:

    settings = DD20Settings(
        debug=True,
        line_data_valid_hash="A",
        station_data_valid_hash="B",
        dd20_filepath="/xxxx/DD20.XLSM",
        dd20_mapping_filepath="/xxxx/Limits_other.xlsx",
        mrid_mapping_filepath="/xxxx/seg_line_mrid_PROD.csv",
        mock_dd20_filepath="/yyyy/DD20.XLSM",
        mock_dd20_mapping_filepath="/yyyy/Limits_other.xlsx",
        mock_mrid_mapping_filepath="/yyyy/seg_line_mrid_PROD.csv",
        api_port=9999,
        api_dbname="SOME_DB_NAME",
        api_refresh_rate=100,
        use_mock_data=False,
    )

    return settings

def arrange_default_dd20_settings() -> DD20Settings:
    """Initialize DD20Settings with default values"""
    settings = DD20Settings(
        debug=False,
        line_data_valid_hash="86e61101fa327e1b4f769c26300be01f",
        station_data_valid_hash="6ac10cff51c6dbc586e729e10b943854",
        dd20_filepath="/input/DD20.XLSM",
        dd20_mapping_filepath="/input/Limits_other.xlsx",
        mrid_mapping_filepath="/input/seg_line_mrid_PROD.csv",
        mock_dd20_filepath="/valid-testdata/DD20.XLSM",
        mock_dd20_mapping_filepath="/valid-testdata/Limits_other.xlsx",
        mock_mrid_mapping_filepath="/valid-testdata/seg_line_mrid_PROD.csv",
        api_port=5000,
        api_dbname="CONDUCTOR_DATA",
        api_refresh_rate=60,
        use_mock_data=False,
    )

    return settings

def set_dd20_environment_variables(settings: DD20Settings):
    """write settings to environment variables"""
    os.environ["LINE_DATA_VALID_HASH"] = settings.line_data_valid_hash
    os.environ["STATION_DATA_VALID_HASH"] = settings.station_data_valid_hash
    os.environ["DD20_FILEPATH"] = settings.dd20_filepath
    os.environ["DD20_MAPPING_FILEPATH"] = settings.dd20_mapping_filepath
    os.environ["MRID_MAPPING_FILEPATH"] = settings.mrid_mapping_filepath
    os.environ["MOCK_DD20_FILEPATH"] = settings.mock_dd20_filepath
    os.environ["MOCK_DD20_MAPPING_FILEPATH"] = settings.mock_dd20_mapping_filepath
    os.environ["MOCK_MRID_MAPPING_FILEPATH"] = settings.mock_mrid_mapping_filepath
    os.environ["API_PORT"] = str(settings.api_port)
    os.environ["API_DBNAME"] = settings.api_dbname
    os.environ["API_REFRESH_RATE"] = str(settings.api_refresh_rate)
    os.environ["USE_MOCK_DATA"] = str(settings.use_mock_data)
    os.environ["DEBUG"] = str(settings.debug)   

def clear_dd20_environment_variables():
    """clear all dd20 related environamnet variables """
    os.environ.pop("LINE_DATA_VALID_HASH", None)
    os.environ.pop("STATION_DATA_VALID_HASH", None)
    os.environ.pop("DD20_FILEPATH", None)
    os.environ.pop("DD20_MAPPING_FILEPATH", None)
    os.environ.pop("MRID_MAPPING_FILEPATH", None)
    os.environ.pop("MOCK_DD20_FILEPATH", None)
    os.environ.pop("MOCK_DD20_MAPPING_FILEPATH", None)
    os.environ.pop("MOCK_MRID_MAPPING_FILEPATH", None)
    os.environ.pop("API_PORT", None)
    os.environ.pop("API_DBNAME", None)
    os.environ.pop("API_REFRESH_RATE", None)
    os.environ.pop("USE_MOCK_DATA", None)
    os.environ.pop("DEBUG", None)
