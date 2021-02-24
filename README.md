# CMEMS automated data retrieval

[![build-and-push-images](https://github.com/geomar-od/rasmus-cmems-downloads/workflows/build-and-push-images/badge.svg?branch=main)](https://github.com/geomar-od/rasmus-cmems-downloads/actions?query=workflow%3Abuild-and-push-images)
[![quay.io/willirath/rasmus-cmems-downloads](https://img.shields.io/badge/quay.io-build-blue)](https://quay.io/repository/willirath/rasmus-cmems-downloads)

## Overview

Currently, automated data downloading (https://github.com/geomar-od/rasmus-cmems-downloads) includes two steps:

1. data download and extraction,

2. format conversion from netCDF to `zarr` format.

In the future, we may have more conversion steps (e.g., Parquet) and / or an upload step to the True Ocean systems.

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

The data are downloaded as netCDF files into associated name directories: `global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh/nc` and `global-analysis-forecast-wav-001-027/nc` in a directory that can be chosen via an input argument.

For a time step a separated `.nc` file is created named according to selected model, variable and start and end time stamp, e.g., `global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_uo_2021-01-23_2021-01-24.nc` or `global-analysis-forecast-wav-001-027_VPED_2021-01-23_2021-01-24.nc`. We create daily data files for every variable.  

To convert data to the tabular `.csv` format, we use Python scripts and create directories `GLOBAL_ANALYSIS_FORECAST_PHY_CSV/` and `GLOBAL_ANALYSIS_FORECAST_WAV_CSV/` which again will be located in a directory that can be chosen via a command line argument. The converted files are called, e.g., `GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS_2021-01-23_21:30:00:00.csv` or `GLOBAL_ANALYSIS_FORECAST_WAVE_001_27-TDS_2021-01-23_15:00:00:00.csv`.


## Usage

### Data download and extraction

This needs a Python environment containing the following packages
- [`motuclient`](https://github.com/clstoulouse/motu-client-python#using-pip)
- [`xarray`](http://xarray.pydata.org/en/stable/installing.html#instructions)
- [`netCDF4`](https://pypi.org/project/netCDF4/)
- [`pandas`](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html#installing-from-pypi)
Note that it is, however,  recommended to use the Docker ([see below](#usage-with-docker)).

To initiate an automated data retrieval, copy the `.py` files to the desired output directory.

Set environment variables containing your CMEMS credentials:
```shell
export MOTU_USER="XXXXXXXXXXXXXXXX"
export MOTU_PASSWORD="XXXXXXXXXXXXXXXXX"
```

To execute download using python and default set of arguments:
```shell
  python MotuClDownloadCMEMSPhysModel.py
  python MotuClDownloadCMEMSWavModel.py
```
or, otherwise with selected arguments call:

```shell
   python MotuClDownloadCMEMSPhysModel.py --basedir <basedir_name> --longitude_min <lon_min_value> --longitude_max <lon_max_value> --latitude_min <lat_min_value> --latitude_max <lat_max_value> --depth_min <depth_min_value> --depth_max <depth_max_value> --time_min <YYYY-MM-DD SS:mm:HH> --time_max <YYYY-MM-DD SS:mm:HH> --replace <True/False> --vars <list of variables> --service_id <service_id_name> --product_id <product_id_name>
   python MotuClDownloadCMEMSWavModel.py --basedir <basedir_name> --longitude_min <lon_min_value> --longitude_max <lon_max_value> --latitude_min <lat_min_value> --latitude_max <lat_max_value> --depth_min <depth_min_value> --depth_max <depth_max_value> --time_min <YYYY-MM-DD SS:mm:HH> --time_max <YYYY-MM-DD SS:mm:HH> --replace <True/False> --vars <list of variables> --service_id <service_id_name> --product_id <product_id_name>
   ```
where the set of arguments is defined as follows:
*  basedir  - directory which contains the directories for the netCDF and the CSV files can be chosen. If no `<base_dir>` is supplied, the current directory will be chosen.
*  longitude_min, --longitude_max - longitudinal domain extend (default = -180, -179.91667), 
*  latitude_min, --latitude_max - latitudonal domain extend (default = -80, 90), 
*  depth_min, --depth_max - bottom and top depth layers (default = 0.493, 0.4942),
*  time_min, --time_max - time range in the format "YYYY-MM-DD SS:mm:HH", 
*  replace - option for re--downloading of data files, True/False is selected depending on whether existing files are replaced automatically <br>
               upon downloading (default = False)                             
*  vars - list of variables could be selected from available model ocean parameters  
*  service_id - name of ocean model (default = GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS/GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS for ocean/wave model correspondingly) 
*  product_id - name of ocean product (default = global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh/global-analysis-forecast-wav-001-027 for ocean/wave model correspondingly)

## Data conversion from netcdf to Zarr

This step is outdated
After the data are downloaded, run the python scripts to convert the data to `.csv` format by running:
```shell
python NetCDF2CSVPhysModel.py --basedir <base_dir>
python NetCDF2CSVWaveModel.py --basedir <base_dir>
```
After downloads are finished, run the python scripts to convert netcdf files to `zarr store` by running
in command line with default arguments:
```shell
  python NetCDF2zarrPhysModel.py
  python NetCDF2zarrWavModel.py
```
or using list of arguments as follows:

```shell
   python NetCDF2zarrPhysModel.py --basedir <basedir_name> --product_id <product_id_name> --var <list of variables>
   python NetCDF2zarrWavModel.py --basedir <basedir_name> --product_id <product_id_name> --var <list of variables>
   ```
where the set of arguments is defined as above in previous section. 
After the conversion is finished `zarr store` directories with data are created named according to convention `product_id/product_id_variable_name_start_day_end_day.zarr`.

In future versions,there will be a single data conversion call, the model selection will be passed as argument.    


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
docker build \
    -t rasmus-cmems-downloads:netcdf2zarr-latest - \
    netcdf2zarr/
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

docker pull quay.io/willirath/rasmus-cmems-downloads:netcdf2zarr-latest
docker tag \
    quay.io/willirath/rasmus-cmems-downloads:netcdf2zarr-latest \
    rasmus-cmems-downloads:netcdf2zarr-latest
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

To convert to Zarr, run:
```shell
docker run --rm \
    -v $PWD:/work -w /work \
    rasmus-cmems-downloads:netcdf2zarr-latest \
    --basedir <base_dir> --product-id <productid> --var <var1> --var <var2> 
```

## Usage with Singularity

### Load singularity module

If necessary, make sure `singularity` is in your path.
On Nesh, you currently need to run
```shell
module load singularity/3.5.2
```

### Build or pull image

First, pull the container images with
```shell
singularity pull --disable-cache --dir $PWD docker://quay.io/willirath/rasmus-cmems-downloads:motupy-latest

singularity pull --disable-cache --dir $PWD docker://quay.io/willirath/rasmus-cmems-downloads:netcdf2csv-latest
```
This will create two singularity files (ending on `sif`):
```
rasmus-cmems-downloads_motupy-latest.sif
rasmus-cmems-downloads_motupy-latest.sif
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
singularity run rasmus-cmems-downloads_motupy-latest.sif \
    ./MotuClCallPhysModel.sh <base_dir>
```
and
```shell
singularity run rasmus-cmems-downloads_motupy-latest.sif \
    ./MotuClCallWaveModel.sh <base_dir>
```
Likewise, to run the download with python via docker
```shell
singularity run rasmus-cmems-downloads_motupy-latest.sif \
    python MotuClDownloadCMEMSPhysModel.py 
```
and
```shell
singularity run rasmus-cmems-downloads_motupy-latest.sif \
    python MotuClDownloadCMEMSPhysModel.py
```
Again, `<base_dir>` indicates where the data should be downloaded.

### Run conversion

And finally, run the conversion steps with
```shell
singularity run rasmus-cmems-downloads_netcdf2csv-latest. \
    python NetCDF2CSVPhysModel.py --basedir <base_dir>
```
and
```shell
singularity run rasmus-cmems-downloads_netcdf2csv-latest. \
    python NetCDF2CSVWaveModel.py --basedir <base_dir>
```
Again, `<base_dir>` indicates where the data should be downloaded.
