#------------------------------------------------------------------------------------------------------------------
# Convertion from netcdf to zarr_store using xarray and pandas libraries
# --------------------------------------------------------------------------------------------------------------------
#
#   USAGE
#
#  python netcdf-to-zarr.py start_time number_batches_append batch_size
#
#  start_time            - begining time stamp given by user
#  number_batches_append - how many time steps to keep
#  batch_size            - size of time in seconds
#
#  start_time is provided as a string in format "dd/mm/yyyy,HH:MM:SS"
#
#-----------------------------------------------------------------------------------------------------------------------'''

import argparse
from dask.distributed import Client, progress, LocalCluster
import pandas as pd
from pathlib import Path
import xarray as xr
import numpy as np
import numcodecs
import zarr
from datetime import datetime
import time
import sys

# Define time string formats:
#
# format for time string (convention for netcdf file name : file_name_prefix_time1_time2.nc,
# where time1, time2 -start, end  time given in a format
format = "ddMMyyyyHHmmSS"
# format for time string extended
format_extend = "dd/mm/yy HH:MM:SS"


def convert_secs_date(time_secs,time_format):
   # convert from seconds to time given in format "dd/mm/yy HH:MM:SS"
   dt_object = datetime.fromtimestamp(time_secs)
   str_time = dt_object.strftime("%d/%m/%y %H:%M:%S")
   return str_time

def convert_to_secs(tt,time_format):
    # Convertion from time in format ddMMyyyyHHmmSS to time in days from 01.01.1950
    # tt - should be given in format "ddMMyyyyHHmmSS"
    # time_format - is a conversion time format "dd/mm/yy HH:MM:SS"
    ti = tt[0:2] + "/"+ tt[2:4] + "/"+ tt[6:8] + " " + tt[8:10] + ":" + \
         tt[10:12] + ":" + tt[12:14]
    print(ti)
    obj1 = time.strptime(ti,"%d/%m/%y %H:%M:%S")
    time_secs = time.mktime(obj1)
    return time_secs

def extract_time_stamp_from_name(name_netcdf_file, time_format):
    # get the prefix name and time intervals from netcdf file name
    # the time format string is "ddMMyyyyHHmmSS"
    len_stamp=len(time_format)
    netcdf_file_prefix = name_netcdf_file[0:-2*len_stamp]
    time_start = name_netcdf_file[1-2*len_stamp:-len_stamp]
    print(time_start,"time_start")
    time_end = name_netcdf_file[1-len_stamp:]
    return time_start, time_end, netcdf_file_prefix


def create_or_append_zarr(names_netcdf, zarr_store, start_time, \
                          number_batches_to_append, batch_size, time_format):
    # open zarr store or append to an existing zarr store netcdf files

    # convert user start time to time in seconds
    start_time_secs =convert_to_secs(start_time, time_format)
    end_time_secs = start_time_secs
    final_time_secs = start_time_secs + (number_batches_to_append * batch_size)
    # convert back time from seconds to string format "dd/mm/yyyy,HH:MM:SS"
    end_time = convert_secs_date(end_time_secs,format_extend)

    # isolate prefix file name and time range : begining time and ending time
    time_ini, time_fin, file_prefix = extract_time_stamp_from_name(names_necdf[0], format)

    # convert time interval from netcdf file to seconds
    time_ini_secs = convert_to_secs(time_ini,format)
    time_fin_secs = convert_to_secs(time_fin,format)

    # convert back time from seconds to string format "dd/mm/yyyy,HH:MM:SS"
    time_ini_extend = convert_secs_date(time_ini_secs,format_extend)
    time_fin_extend = convert_secs_date(time_fin_secs,format_extend)
    time_fin_stepforward_extend = convert_days_date(time_fin_secs + batch_size,format_extend)

#    while start_time_seconds < final_time_seconds:
#        end_time_days = start_time_days + batch_size
#        print(f"start time: {start_time}, starting file: {names_netcdf[0]}")
#        print(f"end time: {end_time}, ending file: {names_netcdf[:0]}")
#        args = {'consolidated': True}
        # Either append or initiate store
#        print(start_time_days,time_ini_days)
#        if start_time_days == time_ini_days:
#            ds = xr.open_mfdataset(names_netcdf, parallel=True, combine='by_coords',\
#                                   mask_and_scale=False)
#            ds = ds.chunk(chunks)
#            args['mode'] = 'w'
#        elif start_time_days < time_ini_days:
#            raise Exception(f"Start time {start_time} is too early, chose start time \
#                            no earlier than {time_ini_extend}")
#            break
#        elif start_time_days > time_fin_days + batch_size:
#            raise Exception(f"Start time {start_time} is too late, chose start time no \
#                            later than {time_fin_stepforward_extend}")
#        elif start_time_days == time_fin_days + batch_size:
#            current_ds = xr.open_zarr(zarr_store, consolidated=True)
#            ds = xr.open_mfdataset(names_necdf, parallel=True, combine='by_coords')
#            ds = ds.chunk(chunks)
#            args['mode'] = 'a'
#            args['append_dim'] = 'time'
#        ds.to_zarr(zarr_store, **args)
#        start_time_days = end_time_days
#        print(f"Done with this batch")
#        print()

if __name__ == "__main__":
    # Invariants - but could be made configurable
    #chunks = {'time': 5, 'lat': 1799, 'lon': 3600}
    numcodecs.blosc.use_threads = False

    # Read arguments from STDIN
    # batch_size is given in seconds, number_batches_to_append - number of time steps
    # start_time is initial time given by user in format "dd/mm/yyyy,HH:MM:SS"
    # print(sys.argv)
    #_, start_time, number_batches_to_append, batch_size = sys.argv
    # number_batches_to_append, batch_size = int(number_batches_to_append), int(batch_size)'''

    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
               "--basedir",
               default=".",
               help=("Base directory where the data dirs will be found." "\nDefaults to $PWD."),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)

    # set input and output paths
    path_in_curr = base_dir / "GLOBAL_ANALYSIS_FORECAST_PHY_NC"
    path_out_curr = base_dir / "GLOBAL_ANALYSIS_FORECAST_PHY_ZARR"

    # find all input files
    input_files = sorted(path_in_curr.glob("*.nc"))

    # get dimensions of lon,lat, depth and time from netcdf file
    nc_ds = xr.open_dataset(input_files[0])

    dim_lon = len(nc_ds['longitude'])
    dim_lat = len(nc_ds['latitude'])
    dim_time =  len(nc_ds['time'])
    dim_depth =  len(nc_ds['depth'])

    # Invariants - but could be made configurable
    chunks = {'time': 1, 'depth': dim_depth, 'latitude': dim_lat, \
              'longitude': dim_lon}

    # depfine zarr_store directory
    zarr_store = path_out_curr / f"1x{dim_depth}x{dim_lat}x{dim_lon}"

    # Invariants - but could be made configurable
    numcodecs.blosc.use_threads = False
    print(f"zarr store directory: {zarr_store}")

    # Initialize Dask
    #cluster = LocalCluster(n_workers=4)
    #client = Client(cluster)
    #print(f"Dask client {client}")

    # days since 01/01/1950 00:00:00 622920.5
    #ddMMyyyyHHmmSS
    name_file_netcdf=f'{".".join(input_files[0].name.split(".")[:-1])}'
    time_ini, time_fin, file_prefix = extract_time_stamp_from_name(name_file_netcdf, format)

    print(time_ini)
    print(time_fin)
    start_time = time_ini[0:2] + "/" + time_ini[2:4] + "/" + time_ini[6:7] + " " \
                 + time_ini[8:10] + ":" + time_ini[10:12] + ":" +time_ini[12:14]
    number_batches_to_append = len(nc_ds['time'])
    batch_size = 1
    create_or_append_zarr(input_files, zarr_store, start_time, \
                          number_batches_to_append, batch_size, format)
