# Conductor data provider

A container that parses AC-line conductor properties from various datasoruces and expose it via a REST API.
The datasources are costum in-house Energinet specific files, examples of them can be found under:
https://github.com/energinet-singularity/conduck/tree/feature/dd20_format_change/tests/valid-testdata

The purpose is to link AC-line conductor properties from a datasource named DD20, to AC-line conductor database records in a SCADA (supervisory control and data acquisition) system.
The linked information is exposed via a REST API, because it is used by a Dynamic Line Rating application running at Energinet.

## Description
This repo contains a python-script that will read/parse following datasources:
- "DD20" excel-file.
Contains various conductor properties for AC-lines.
- "DD20 name to SCADA AC-line name mapping" excel-file.
Contains mapping from DD20 AC-line name to AC-line name used in SCADA system. This is necessary since some AC-line names differ between SCADA and DD20.
- "AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system.
Contains mapping from AC-line name used in SCADA system to AC-linesegment MRID in SCADA system are parsed to a dataframe.
The AC-linesegment MRID is a unique identifier, which all conductor data must be linked to.

The shared id used to link the datasoruces are the name of the AC-line.
            
The script is intended to be run as a container, so a Dockerfile is provided as well, as is a set of helm charts with a default configuration.

### Exposed environment variables:

| Name | Default value | Description |
|--|--|--|
|DEBUG|(not set)|Set to 'TRUE' to enable very verbose debugging log|
|USE_MOCK_DATA|(not set)|Set to 'TRUE' to enable creating mock forecast files|
|DD20FILEPATH|/input/DD20.XLSM|Filepath for "DD20" excel-file|
|DD20MAPPINGFILEPATH|/input/Limits_other.xlsx|"DD20 name to SCADA AC-line name mapping" excel-file.|
|MRIDMAPPINGFILEPATH|/input/seg_line_mrid_PROD.csv|"AC-line name to AC-linesegment MRID mapping" csv-file from SCADA system.|
|PORT|5000|Port for exposing REST API|
|DBNAME|CONDUCTOR_DATA|Name of database exposed via REST API|

### File handling / Input

Every 60 seconds the files are 


s. Files that fit the name-filter will be parsed one by one and then deleted (other files will be ignored). The files must fit the agreed structure (examples can be found in the '/tests/valid-testdata/' subfolder) and naming, otherwise it will most likely break execution and not be able to recover (an issue has been rasied for this).

#### Using MOCK data

The container has an option to generate mock-data. This is done by taking the test-data files and changing their timestamps and dumping them into the input directory. This can be used if real forecast files are not available. Be aware that all forecast data will be identical and thereby not dynamic/changing.



## Getting Started

The quickest way to have something running is through docker (see the section [Running container](#running-container)).

Feel free to either import the python-file as a lib or run it directly - or use HELM to spin it up as a pod in kubernetes. These methods are not documented and you will need the know-how yourself (the files have been prep'ed to our best ability though).

### Dependencies

To run the script a kafka broker must be available (use the 'KAFKA_HOST' environment variable). Furthermore a kSQL server should be available (use the 'KSQL_HOST' environment variable) - if unavaliable, the application will still run but error-messages will be logged periodically.

#### Python (if not run as part of the container)

The python script can probably run on any python 3.9+ version, but your best option will be to check the Dockerfile and use the same version as the container. Further requirements (python packages) can be found in the app/requirements.txt file.

#### Docker

Built and tested on version 20.10.7.

#### HELM (only relevant if using HELM for deployment)

Built and tested on version 3.7.0.

### Running container

1. Clone the repo to a suitable place
````bash
git clone https://github.com/energinet-singularity/forecast-parser.git
````

2. Build the container and create a volume
````bash
docker build forecast-parser/ -t forecast-parser:latest
docker volume create forecast-files
````

3. Start the container in docker (change hosts to fit your environment - KSQL_HOST is not required as stated above)
````bash
docker run -v forecast-files:/forecast-files -e KAFKA_HOST=127.0.0.1:9092 -e KSQL_HOST=127.0.0.1:8088 -it --rm forecast-parser:latest
````
The container will now be running interactively and you will be able to see the log output. To parse a forecast, it will have to be delivered to the volume somehow. This can be done by another container mapped to the same volume, or manually from another bash-client

To mock output data and show debugging information, use the two flags USE_MOCK_DATA and DEBUG:
````bash
docker run -v forecast-files:/forecast-files -e DEBUG=TRUE -e USE_MOCK_DATA=TRUE -e KAFKA_HOST=127.0.0.1:9092 -e KSQL_HOST=127.0.0.1:8088 -it --rm forecast-parser:latest
````

Manual file-move to the volume (please verify volume-path is correct before trying this):
````bash
sudo cp forecast-parser/tests/valid-testdata/EnetEcm_2010010100.txt /var/lib/docker/volumes/forecast-files/_data/
````

## Help

* Be aware: There are at least two kafka-python-brokers available - make sure to use the correct one (see app/requirements.txt file).

For anything else, please submit an issue or ask the authors.

## Version History

* 1.1.3:
    * First production-ready version
    <!---* See [commit change]() or See [release history]()--->

Older versions are not included in the README version history. For detauls on them, see the main-branch commit history, but beware: it was the early start and it was part of the learning curve, so it is not pretty. They are kept as to not disturb the integrity of the history.

## License

This project is licensed under the Apache-2.0 License - see the LICENSE.md file for details
