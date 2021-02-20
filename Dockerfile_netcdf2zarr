FROM python:3.8

# install xarray, netcdf and pandas
# TODO: cleanup cache?
RUN python -m pip install xarray netcdf4 zarr dask distributed numpy

# drop this later, but we might need a bash for debugging
# TODO: cleanup cache?
RUN apt update && apt install -y bash