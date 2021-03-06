# Conductor data provider

A container that parses AC-line conductor properties from various data sources and exposes them via a REST API.
The data sources are custom in-house Energinet specific files, examples of them can be found in the tests/valid-testdata subfolder of this repo.

The purpose is to link AC-line conductor properties from a datasource named DD20, to AC-line conductor database records in a SCADA (supervisory control and data acquisition) system.
The linked information is exposed via a REST API, because it is used by a Dynamic Line Rating application running at Energinet.

## Description

This repo contains a python-script that will read/parse following datasources:

- "DD20" excel-file.
  Contains various conductor properties for AC-lines.
- "DD20 name to SCADA AC-line name mapping" excel-file.
  Contains mapping from DD20 AC-line name to AC-line name used in SCADA system. This is necessary since some AC-line names differ between SCADA and DD20.
- "AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system.
  Contains mapping from AC-line name used in SCADA system to AC-linesegment MRID in SCADA system.
  The AC-linesegment MRID is a unique identifier, which all conductor data must be linked to.

The shared id used to link the datasoruces are the name of the AC-line. The AC-line nameing in DD20 is converted to match the style of the naming in SCADA system.
When standard name conversion is not sufficient, due to discrepancies in naming, the "DD20 name to SCADA AC-line name mapping" is used to manually link AC-lines.

The script is intended to be run as a container, so a Dockerfile is provided as well, as is a set of helm charts with a default configuration.

### Exposed environment variables:

| Name                       | Default value                               | Description                                                                            |
| -------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------- |
| DEBUG                      | False                                       | Set to 'TRUE' to enable very verbose debugging log                                     |
| STATION_DATA_VALID_HASH    |                                             | hash value for decting dd20 format change in station data sheet                        |
| LINE_DATA_VALID_HASH       |                                             | hash value for decting dd20 format change in line data sheet                           |
| DD20_FILEPATH              | /input/DD20.XLSM                            | Filepath for "DD20" excel-file                                                         |
| DD20_MAPPING_FILEPATH      | /input/Limits_other.xlsx                    | Filepath for "DD20 name to SCADA AC-line name mapping" excel-file.                     |
| MRID_MAPPING_FILEPATH      | /input/seg_line_mrid_PROD.csv               | Filepath for "AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system. |
| MOCK_DD20_FILEPATH         | tests/valid-testdata/DD20.XLSM              | Filepath for "DD20" excel-file                                                         |
| MOCK_DD20_MAPPING_FILEPATH | tests/valid-testdata/Limits_other.xlsx      | Filepath for "DD20 name to SCADA AC-line name mapping" excel-file.                     |
| MOCK_MRID_MAPPING_FILEPATH | tests/valid-testdata/seg_line_mrid_PROD.csv | Filepath for "AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system. |
| API_PORT                   | 5000                                        | Port for exposing REST API                                                             |
| API_DBNAME                 | CONDUCTOR_DATA                              | Name of database exposed via REST API                                                  |
| USE_MOCK_DATA              | False                                       | Set to 'TRUE' to enable creating mock forecast files                                   |

### File handling / Input

Every 60 seconds data from files are parsed, if files has changed since last read.
The files must fit the agreed structure (examples can be found in the '/tests/valid-testdata/' subfolder), otherwise the data cannot be parsed and the API will not return any data.

#### Using MOCK data

The container has an option to generate mock-data. This is done by taking the test-data files and dumping them into the input directory. This can be used if input files are not available. Be aware that it is dummy data and only intended for illustration of functionality.

### API

The DataFrame is made available through a REST API which accepts SQL-queries. More information on the API itself can be found [here](https://github.com/energinet-singularity/singupy/tree/main/singupy#class-apidataframeapi).

The DataFrame contains the following columns/indexes:
| Name | type | description |
|--|--|--|
|ACLINESEGMENT_MRID|str|MRID of the line|
|LINE_EMSNAME|str|EMSName of the line|
|DLR_ENABLED|bool|DLR Enabled True=Yes, False=No|
|ACLINE_NAME_DATASOURCE|str|Sourcefile name of the line|
|DATASOURCE|str|Source of the data|
|CONDUCTOR_TYPE|str|Type of conductor|
|CONDUCTOR_COUNT|int|Number of conductors|
|SYSTEM_COUNT|int|Number of systems|
|MAX_TEMPERATURE|int|Mac temperature of the line|
|RESTRICT_CONDUCTOR_LIM_CONTINUOUS|int|Conductor continous limit|
|RESTRICT_COMPONENT_LIM_CONTINUOUS|int|Component continous limit|
|RESTRICT_COMPONENT_LIM_15M|int|Component 15 min limit|
|RESTRICT_COMPONENT_LIM_1H|int|Component 1 hour limit|
|RESTRICT_COMPONENT_LIM_40H|int|Component 40 hour limit|
|RESTRICT_CABLE_LIM_CONTINUOUS|float|Cable continous limit|
|RESTRICT_CABLE_LIM_15M|float|Cable 15 min limit|
|RESTRICT_CABLE_LIM_1H|float|Cable 1 hour limit|
|RESTRICT_CABLE_LIM_40H|float|Cable 40 hour limit|

## Getting Started

The quickest way to have something running is through docker (see the section [Running container](#running-container)).

Feel free to either import the python-file as a lib or run it directly - or use HELM to spin it up as a pod in kubernetes. These methods are not documented and you will need the know-how yourself (the files have been prep'ed to our best ability though).

### Dependencies

Files must be supplied at the location specified via environment variables, if not using MOCK data.

#### Python (if not run as part of the container)

The python script can probably run on any python 3.9+ version, but your best option will be to check the Dockerfile and use the same version as the container. Further requirements (python packages) can be found in the app/requirements.txt file.

#### Docker

Built and tested on version 20.10.14.

#### HELM (only relevant if using HELM for deployment)

Built and tested on version 3.7.0.

### Running container

1. Clone the repo to a suitable place

```bash
git clone https://github.com/energinet-singularity/conductor-data-provider.git
```

2. Build the container and create a volume

```bash
docker build conductor-data-provider/ -t conductor-data-provider:latest
docker volume create conductor-data-files
```

3. Start the container in docker

```bash
docker run -v conductor-data-files:/input -it --rm conductor-data-provider:latest
```

The container will now be running interactively and you will be able to see the log output. The container will need the input files available in the volume, otherwise it will not calculate.
The files have to be delivered to the volume somehow. This can be done by another container mapped to the same volume, or manually from another bash-client

Manual file-move to the volume (please verify volume-path is correct before trying this):

```bash
sudo cp conductor-data-provider/tests/valid-testdata/* /var/lib/docker/volumes/conductor-data-files/_data/
```

To use mock output data, use the flag USE_MOCK_DATA:

```bash
docker run -e USE_MOCK_DATA=TRUE -it --rm conductor-data-provider:latest
```

### SQL command

When the container is running in your local environment you can use the following bash command to query data from it. The example below assumes you are using Mock data with default settings, please change "localhost" with the IP that your API is running on.

```bash
curl -d '{"sql-query": "SELECT * FROM CONDUCTOR_DATA;"}' -H 'Content-Type: application/json' -X POST http://localhost:5000/
```

## DD20 format change detection

In order to detect if DD20 file format has changed, we calcaulate a hash value of the headers of the dd20 file.
In case the format of the headers change, we will trigger an exception!

To update the expected hash value, which will be needed once correction has been made to handle a new dd20 format.
One has to run the hash calculation and store the value as the new expected hash value.

This can be done by following these steps.

- 1. Save the new dd20 file in a sub folder under the tests folder. For example
     > \tests\real-data\new-dd20.XLSM
- 2. update your local .env file under app folder to contain (You can create one if it doesnn't exist)
     > MOCK_DD20_FILEPATH="real-data/new-dd20.XLSM
- 3. run the test test_can_validate_dd20_line_data_summer_format. It should fail. And you should be able to see the old and the new hash value in the assertion message
- 4. search and replace the old default values with the new value in the code base.
     (You can also override hard coded default hash values by setting alternative values in env variables
     or by adding them to the local .env file)
- 5. repeat step 3,4 using test_can_validate_dd20_station_data_format

## Help

Please submit an issue or ask the authors.

## Version History

* 1.2.5:
    * HASH values for DD20 can now be configured via environment variables.
* 1.2.3:
    * Handle update for single files.
* 1.1.1:
    * Handle missing or bad files
* 1.1.0:
    * Add functionality to verify excel-file format/headers
* 1.0.0:
    * First production-ready version

## License

This project is licensed under the Apache-2.0 License - see the LICENSE.md file for details
