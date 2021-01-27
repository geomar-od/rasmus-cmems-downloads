#------------------------------------------------------------------------------------------------------------------
# Convertion from netcdf to zarr_store using xarray and pandas libraries
# --------------------------------------------------------------------------------------------------------------------
#
#   USAGE
#
#  python3 NetCDF2zarrPhysModel.py start_time number_batches_append batch_size
#  or
#  python3 NetCDF2zarrPhysModel.py --basedir base_dir_name  start_time number_batches_append batch_size
#
#  start_time            - begining time stamp given by user
#  number_batches_append - how many time steps to keep
#  batch_size            - size of time in seconds
#
#  start_time is provided as a string in format "dd/mm/yy HH:MM:SS"
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
format_short = "ddMMyyyyHHmmSS"
# format for time string extended
format_extended = "dd/MM/yy HH:mm:SS"

def mkdate(datestr):
   # function make time string for argument parser
   try:
    return datestr
   except ValueError:
    raise argparse.ArgumentTypeError(datestr + 'time start is not in a proper format "dd/MM/yy HH:mm:SS" ')

def convert_time_formats(t_short):
   # convert from "ddMMyyyyHHmmSS" to "dd/mm/yy HH:MM:SS"
   t_extended = t_short[0:2] + "/" + t_short[2:4] + "/" + \
                t_short[6:8] + " " + t_short[8:10] + ":" + \
                t_short[10:12] + ":" + t_short[12:14]
   return t_extended

def convert_secs_date(time_secs,time_format):
   # convert from seconds to time given in format "dd/mm/yy HH:MM:SS"
   dt_object = datetime.fromtimestamp(time_secs)
   str_time = dt_object.strftime("%d/%m/%y %H:%M:%S")
   return str_time

def convert_to_secs(tt,time_time_format):
    # Convertion from time in format dd/MM/yy HH:mm:SS to time in seconds
    # tt - should be given in format "dd/mm/yy HH:MM:SS"
    obj1 = time.strptime(tt,"%d/%m/%y %H:%M:%S")
    time_secs = time.mktime(obj1)
    return time_secs

def extract_time_stamp_from_name(name_netcdf_file, time_format):
    # get the prefix name and time intervals from netcdf file name
    # the time format string is "ddMMyyyyHHmmSS"
    # the netcdf file naming : {netcdf_file_prefix}_ddMMyyyyHHmmSS_ddMMyyyyHHmmSS.nc
    len_stamp=len(time_format)
    netcdf_file_prefix = name_netcdf_file[0:-2*len_stamp-2]
    time_start = name_netcdf_file[-2*len_stamp-1:-len_stamp-1]
    time_end = name_netcdf_file[-len_stamp:]
    return time_start, time_end, netcdf_file_prefix


def create_or_append_zarr(names_netcdf, zarr_store, start_time, \
                          number_batches_to_append, batch_size, chunks, time_format):
    # open zarr store or append to an existing zarr store netcdf files

    # extract netcdf prefix, initial and final time steps
    name_file_netcdf=f'{".".join(input_files[0].name.split(".")[:-1])}'
    time_ini_nc, time_fin_nc, file_prefix_nc = extract_time_stamp_from_name(name_file_netcdf, format_short)

    # Convert from "ddMMyyyyHHmmSS" to "dd/MM/yy HH:mm:SS" time format
    begin_time_nc = convert_time_formats(time_ini_nc)
    end_time_nc = convert_time_formats(time_fin_nc)

    # Convert to seconds
    start_time_secs = convert_to_secs(start_time, time_format)
    end_time_secs = start_time_secs
    final_time_secs = start_time_secs + (number_batches_to_append * batch_size)
    # Convert back time from seconds to string format "dd/mm/yy HH:MM:SS"
    end_time = convert_secs_date(end_time_secs,format_extended)

    print(time_ini_nc)
    # convert time interval from netcdf file to seconds
    time_ini_secs = convert_to_secs(begin_time_nc,format_extended)
    time_fin_secs = convert_to_secs(end_time_nc,format_extended)

    # Convert back time from seconds to string format "dd/MM/yy HH:mm:SS"
    #time_ini_extended = convert_secs_date(time_ini_secs,format_extended)
    #time_fin_extended = convert_secs_date(time_fin_secs,format_extended)
    #time_fin_stepforward_extended = convert_days_date(time_fin_secs + batch_size,format_extended)

    while start_time_secs < final_time_secs:
        end_time_secs = start_time_secs + batch_size
        print(f"start time: {start_time}, starting file: {names_netcdf[0]}")
        print(f"end time: {end_time}, ending file: {names_netcdf[:0]}")
        args = {'consolidated': True}
        # Either append or initiate store
        print(start_time_secs,time_ini_secs)
        # make sure that given initial time match the time of netcdf
        if start_time_secs == time_ini_secs:
            ds = xr.open_mfdataset(names_netcdf, parallel=True, combine='by_coords',\
                                   mask_and_scale=False)
            ds = ds.chunk(chunks)
            args['mode'] = 'w'
#        elif start_time_secs < time_ini_secs:
#            raise Exception(f"Start time {start_time} is too early, chose start time \
#                            no earlier than {time_ini_extend}")
#            break
#        elif start_time_secs > time_fin_secs + batch_size:
#            raise Exception(f"Start time {start_time} is too late, chose start time no \
#                            later than {time_fin_stepforward_extend}")
#        elif start_time_secs == time_fin_secs + batch_size:
#            current_ds = xr.open_zarr(zarr_store, consolidated=True)
#            ds = xr.open_mfdataset(names_necdf, parallel=True, combine='by_coords')
#            ds = ds.chunk(chunks)
#            args['mode'] = 'a'
#            args['append_dim'] = 'time'
        ds.to_zarr(zarr_store, **args)
        start_time_secs = end_time_secs
        print(f"Done with this batch")
        print()

if __name__ == "__main__":

    numcodecs.blosc.use_threads = False

    # Read arguments from STDIN
    # batch_size is given in seconds, number_batches_to_append - number of time steps
    # start_time is initial time given by user in format "dd/mm/yy HH:MM:SS"

    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
               "--basedir",
               default=".",
               help=("Base directory where the data dirs will be found." "\nDefaults to $PWD."),
    )
    parser.add_argument('start_time',
                        type = mkdate,
                        help = ("Start time in the format dd/MM/yy HH:mm:SS")
    )
    parser.add_argument(
               'numbatches',
               type = int,
               help=("number of branches for chunk"),
    )
    parser.add_argument(
               'batchsize',
               type = int,
               help = ("batch size"),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)
    number_batches_to_append = int(args.numbatches)
    batch_size = int(args.batchsize)
    start_time = str(args.start_time)

    # set input and output paths
    path_in_curr = base_dir / "GLOBAL_ANALYSIS_FORECAST_PHY_NC"
    path_out_curr = base_dir / "GLOBAL_ANALYSIS_FORECAST_PHY_ZARR"

    # find all input files
    input_files = sorted(path_in_curr.glob("*.nc"))

    # convert first file in nc directory to dataset using xarray
    nc_ds = xr.open_dataset(input_files[0])

    # get dimensions of lon,lat, depth and time from netcdf file
    dim_lon = len(nc_ds['longitude'])
    dim_lat = len(nc_ds['latitude'])
    dim_time =  len(nc_ds['time'])
    dim_depth =  len(nc_ds['depth'])

    # set number of batches and batch size
    number_batches_to_append = len(nc_ds['time'])
    batch_size = 1

    # define size of chunking for further zarr conversion
    chunks = {'time': 1, 'depth': dim_depth, 'latitude': dim_lat, \
              'longitude': dim_lon}

    # define zarr_store directory (how to name zarr_store ??)
    zarr_store = path_out_curr / f"1x{dim_depth}x{dim_lat}x{dim_lon}"

    # Invariants - but could be made configurable
    numcodecs.blosc.use_threads = False
    print(f"zarr store directory: {zarr_store}")

    # Initialize Dask
    cluster = LocalCluster(n_workers=4)
    client = Client(cluster)
    print(f"Dask client {client}")

    create_or_append_zarr(input_files, zarr_store, start_time, \
                          number_batches_to_append, batch_size, chunks, format_short)
