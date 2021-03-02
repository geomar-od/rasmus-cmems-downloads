# CMEMS automated data retrieval

[![build-and-push-images](https://github.com/geomar-od/rasmus-cmems-downloads/actions/workflows/build_and_push_images.yaml/badge.svg)](https://github.com/geomar-od/rasmus-cmems-downloads/actions/workflows/build_and_push_images.yaml)
[![quay.io/willirath/rasmus-cmems-downloads](https://img.shields.io/badge/quay.io-build-blue)](https://quay.io/repository/willirath/rasmus-cmems-downloads)

## Overview

Currently, the automated data downloading includes two steps:

1. data download and extraction: [`motypydownload`](motypydownload/)

2. format conversion from netCDF to [Zarr](https://zarr.readthedocs.io/en/stable/): [`netcdf2zarr`](netcdf2zarr/)

In the future, there will be more conversion steps (e.g., from Zarr to Parquet) and / or an upload step to the systems of a collaborator.

## Description

For real-time downloading from the [Copernicus Ocean website](https://resources.marine.copernicus.eu/?option=com_csw&task=results), the data are selected according to user-given parameters:

- spatial domain
- depth
- time span
- variables

To extract the data we use the [`motuclient`](https://github.com/clstoulouse/motu-client-python/).

## File and directory naming

### netCDF

The data are downloaded as netCDF files into associated name directories:
- for the [physics analysis dataset](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=GLOBAL_ANALYSIS_FORECAST_PHY_001_024): `global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh/nc/`
- for the [wave analysis dataset](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=GLOBAL_ANALYSIS_FORECAST_WAV_001_027): `global-analysis-forecast-wav-001-027/nc/`

For each day, a separate `.nc` file is created named according to the selected, variable and start and end time stamp, e.g., `global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_uo_2021-01-23_2021-01-24.nc` or `global-analysis-forecast-wav-001-027_VPED_2021-01-23_2021-01-24.nc`.

### Zarr

We'll combine all timesteps into one Zarr store per variable.
For the [physics analysis dataset](https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=GLOBAL_ANALYSIS_FORECAST_PHY_001_024), there would, e.g., be `global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh/zarr/global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh_uo_2021-01-01_2021-02-01.zarr/`.

### General

`{produc-id}/{format}/{product-id}_{variable}_{start-date}_{end-time}.{extension}`
with
- `product-id` being, e.g., `global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh`, or `global-analysis-forecast-wav-001-027`.
- `format` being `nc`, `zarr`, etc.
- `variable`, being `uo`, `vo`, etc.
- `start-time` being interpreted as left inclusive boundary of the time interval covered by the data file / data store, and `end-time` being interpreted as the right exclusive boundary of the time interval
- `extension` being `nc`, `zarr/`, etc.


## Usage (with Docker)

### Building or pulling the container images

The necessary container images can be built locally:
```shell
docker build -t rasmus-cmems-downloads:motupydownload-latest motupydownload/
docker build -t rasmus-cmems-downloads:netcdf2zarr-latest netcdf2zarr/
```

Or pre-built images can be pulled and tagged:
```shell
docker pull quay.io/willirath/rasmus-cmems-downloads:motupydownload-latest
docker pull quay.io/willirath/rasmus-cmems-downloads:netcdf2zarr-latest

docker tag \
    quay.io/willirath/rasmus-cmems-downloads:motupydownload-latest \
    rasmus-cmems-downloads:motupydownload-latest
docker tag \
    quay.io/willirath/rasmus-cmems-downloads:netcdf2zarr-latest \
    rasmus-cmems-downloads:netcdf2zarr-latest
```

### Running the containers

For a help message, just run:
```shell
docker run rasmus-cmems-downloads:motupydownload-latest --help
```
and
```shell
docker run rasmus-cmems-downloads:netcdf2zarr-latest --help
```

For actually downloading data and for authenticating on the copernicus service providing the data, read below.

### Data download example

We'll read credentials from environment variables:
```shell
export MOTU_USER="XXXXXXXXXXXXXXXX"
export MOTU_PASSWORD="XXXXXXXXXXXXXXXXX"
```

To run the container for downloading 10 days of the wave forecast product into `./data/`, do:
```shell
docker run -v $PWD:/work --rm \
    -e MOTU_USER -e MOTU_PASSWORD \
    rasmus-cmems-downloads:motupydownload-latest \
    --service_id GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS \
    --product_id global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh \
    --var uo --var vo --basedir /work/data
```

### Zarr conversion example

To convert the data that was just downloaded to `./data/`, run:
```shell
docker run -v $PWD:/work --rm \
    rasmus-cmems-downloads:netcdf2zarr-latest \
    --product_id global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh \
    --var uo --var vo --basedir /work/data
```

## Usage (with Singularity)

TBD

## Usage (with local Python installation)

TBD