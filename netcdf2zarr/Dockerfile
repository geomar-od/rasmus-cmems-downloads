FROM python:3.8

# install xarray, netcdf and pandas
# TODO: cleanup cache?
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# drop this later, but we might need a bash for debugging
# TODO: cleanup cache?
RUN apt update && apt install -y bash

RUN mkdir -p /opt/netcdf2zarr/
COPY netcdf2zarr.py /opt/netcdf2zarr/.
ENTRYPOINT ["python", "/opt/netcdf2zarr/netcdf2zarr.py"]