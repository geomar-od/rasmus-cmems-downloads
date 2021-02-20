# CMEMS automated data retrieval

[![build-and-push-images](https://github.com/geomar-od/rasmus-cmems-downloads/workflows/build-and-push-images/badge.svg?branch=main)](https://github.com/geomar-od/rasmus-cmems-downloads/actions?query=workflow%3Abuild-and-push-images)
[![quay.io/willirath/rasmus-cmems-downloads](https://img.shields.io/badge/quay.io-build-blue)](https://quay.io/repository/willirath/rasmus-cmems-downloads)

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

The data are downloaded as netCDF files into associated name directories: `GLOBAL_ANALYSIS_FORECAST_PHY_NC/` and `GLOBAL_ANALYSIS_FORECAST_WAV_NC/` in a directory that can be chosen via an input argument.

For a time step a separated `.nc` file is created named according to selected model and time stamp, e.g., `GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS_2021-01-23_21:30:00:00.nc` or `GLOBAL_ANALYSIS_FORECAST_WAVE_001_27-TDS_2021-01-23_15:00:00:00.nc`.

To convert data to the tabular `.csv` format, we use Python scripts and create directories `GLOBAL_ANALYSIS_FORECAST_PHY_CSV/` and `GLOBAL_ANALYSIS_FORECAST_WAV_CSV/` which again will be located in a directory that can be chosen via a command line argument. The converted files are called, e.g., `GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS_2021-01-23_21:30:00:00.csv` or `GLOBAL_ANALYSIS_FORECAST_WAVE_001_27-TDS_2021-01-23_15:00:00:00.csv`.


## Usage

This needs a Python environment containing the following packages
- [`motuclient`](https://github.com/clstoulouse/motu-client-python#using-pip)
- [`xarray`](http://xarray.pydata.org/en/stable/installing.html#instructions)
- [`netCDF4'](https://pypi.org/project/netCDF4/)
- [`pandas`](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-from-pypi)
Note that it is, however,  recommended to use the Docker ([see below](#usage-with-docker)).

To initiate an automated data retrieval, copy the `.sh` and `.py` files to the desired output directory, and make sure they are executable (`chmod +x  <name_file.sh>`).

Set environment variables containing your CMEMS credentials:
```shell
export MOTU_USER="XXXXXXXXXXXXXXXX"
export MOTU_PASSWORD="XXXXXXXXXXXXXXXXX"
```

Then run (from the same shell)
```shell
./MotuClCallPhysModel.sh <base_dir>
./MotuClCallWaveModel.sh <base_dir>
```
or
to execute download using python
```shell
  python MotuClDownloadCMEMSPhysModel.py
  python MotuClDownloadCMEMSWavModel.py
```
for retrieving current and waves data accordingly.
With `<base_dir>`, the directory which will contain the directories for the netCDF and the CSV files can be chosen. If no `<base_dir>` is supplied, the current directory will be chosen.

After the data are downloaded, run the python scripts to convert the data to `.csv` format by running:
```shell
python NetCDF2CSVPhysModel.py --basedir <base_dir>
python NetCDF2CSVWaveModel.py --basedir <base_dir>
```
Again, `<base_dir>` indicates the directory which will contain the directories for the netCDF and the CSV files can be chosen. If no `--basedir <base_dir>` is supplied, the current directory will be chosen.

## Usage with Docker

### Build or pull image

First, build the container images with
```shell
docker build \
    -t rasmus-cmems-downloads:motupy-latest - \
    < Dockerfile_motupy
docker build \
    -t rasmus-cmems-downloads:netcdf2csv-latest - \
    < Dockerfile_netcdf2csv
```
or pull the pre-built images with
```shell
docker pull quay.io/willirath/rasmus-cmems-downloads:motupy-latest
docker tag \
    quay.io/willirath/rasmus-cmems-downloads:motupy-latest \
    rasmus-cmems-downloads:motupy-latest
docker pull quay.io/willirath/rasmus-cmems-downloads:netcdf2csv-latest
docker tag \
    quay.io/willirath/rasmus-cmems-downloads:netcdf2csv-latest \
    rasmus-cmems-downloads:netcdf2csv-latest
```

### Set credentials

Set environment variables containing your CMEMS credentials:
```shell
export MOTU_USER="XXXXXXXXXXXXXXXX"
export MOTU_PASSWORD="XXXXXXXXXXXXXXXXX"
```

### Download data

Then, run the download steps with
```shell
docker run -it --rm \
    -e MOTU_USER -e MOTU_PASSWORD \
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:motupy-latest \
    ./MotuClCallPhysModel.sh <base_dir>
```
and
```shell
docker run -it --rm \
    -e MOTU_USER -e MOTU_PASSWORD\
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:motupy-latest \
    ./MotuClCallWaveModel.sh <base_dir>
```
Likewise, to run the download with python via docker
```shell
docker run -it --rm \
    -e MOTU_USER -e MOTU_PASSWORD \
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:motupy-latest \
    python MotuClDownloadCMEMSPhysModel.py 
```
and
```shell
docker run -it --rm \
    -e MOTU_USER -e MOTU_PASSWORD\
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:motupy-latest \
    python MotuClDownloadCMEMSPhysModel.py
```
Again, `<base_dir>` indicates where the data should be downloaded.

### Run conversion

And finally, run the conversion steps with
```shell
docker run -it --rm \
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:netcdf2csv-latest \
    python NetCDF2CSVPhysModel.py --basedir <base_dir>
```
and
```shell
docker run -it --rm \
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:netcdf2csv-latest \
    python NetCDF2CSVWaveModel.py --basedir <base_dir>
```
Again, `<base_dir>` indicates where the data should be downloaded.

To convert to Zarr, run
```shell
docker run -it --rm \
    -v $PWD:/work -w /work \
    cmems_netcdf2zarr \
    python NetCDF2zarrPhysModel.py --basedir <base_dir>
```
and
```shell
docker run -it --rm \
    -v $PWD:/work -w /work \
    cmems_netcdf2zarr \
    python NetCDF2zarrWaveModel.py --basedir <base_dir>
```
