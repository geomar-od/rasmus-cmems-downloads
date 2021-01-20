# CMEMS automated data retrieval

## Overview

Currently, automated data downloading (https://github.com/eshchekinova/example-cmems-download-automation) includes two steps: 

1. data download and extraction,

2. format conversion from netCDF to tabular `csv`.

In the future, we may have more conversion steps (e.g., to ZARR and to Parquet) and / or an upload step to the True Ocean systems.

## Description

For real-time downloading from the Copernicus Ocean website (https://resources.marine.copernicus.eu/?option=com_csw&task=results) the data are selected according to user-given parameters:

- spatial domain
- depth
- time span
- variables
      
To extract the data we use the [`motuclient`](https://github.com/clstoulouse/motu-client-python/) implemented in Python and bash scripting.

Currently, two simulation datasets are downloaded:

- GLOBAL_ANALYSIS_FORECAST_PHY
- GLOBAL_ANALYSIS_FORECAST_WAV

The data are downloaded as netCDF files into associated name directories:
- `name_dir_out_nc="$(pwd)/GLOBAL_ANALYSIS_FORECAST_PHY_NC"`
- `name_dir_out_nc="$(pwd)/GLOBAL_ANALYSIS_FORECAST_WAV_NC"`
      
For a time step a separated `.nc` file is created named according to selected model and time stamp:

- `file_out=”GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS_2021-01-23_21:30:00:00"`   
- `file_out=”GLOBAL_ANALYSIS_FORECAST_WAVE_001_27-TDS_2021-01-23_15:00:00:00"`

To convert  data to tabular `.csv` format, we use Python scripts and create a separate directories for the corresponding datasets:

- `name_dir_out_csv="$(pwd)/GLOBAL_ANALYSIS_FORECAST_PHY_CSV"`
- `name_dir_out_csv="$(pwd)/GLOBAL_ANALYSIS_FORECAST_WAV_CSV"`

Analogously, the directories contain for every time step a csv file with the name according to model and time stamp:

- `file_out=”GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS_2021-01-23_21:30:00:00"`
- `file_out=”GLOBAL_ANALYSIS_FORECAST_WAVE_001_27-TDS_2021-01-23_15:00:00:00"`


## Usage

To initiate an automated data retrieval, copy the `.sh` and `.py` files to the desired output directory, and make sure they are executable (`chmod +x  <name_file.sh>`).

Set environment variables containing your CMEMS credentials:
```shell
export MOTU_USER="XXXXXXXXXXXXXXXX"
export MOTU_PASSWORD="XXXXXXXXXXXXXXXXX"
```

Then run (from the same shell)
```shell
./MotuClCallPhysModel.sh 
./MotuClCallWaveModel.sh 
```
for retrieving current and waves data accordingly.

After the data are uploaded, run the python scripts to convert the data to `.csv` format by running:
```shell
python NetCDF2CSVPhysModel.py
python NetCDF2CSVWaveModel.py
```

## Usage with Docker

_**TODO**: Provide two docker files with the environment necessary for downloading and for converting the data._