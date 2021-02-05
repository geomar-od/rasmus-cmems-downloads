#------------------------------------------------------------------------------------------------------------------
# Convertion from netcdf to zarr_store using xarray and zarr
# --------------------------------------------------------------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------------------------------------------------------------'''

import argparse
from dask.distributed import Client, progress, LocalCluster
import pandas as pd
from pathlib import Path
import dask.array
import xarray

import xarray as xr
import numpy as np
import numcodecs
import zarr
from datetime import datetime
import time
import sys

def change_time_format(time_f):
    # change format from "yyyy-MM-dd HH:mm:SS" to
    # ISO 8601 notation: {yyyy}-{MM}-{dd}T{HH}:{mm}:{SS}Z or
    # ISO 8601 date: {yyyy}-{MM}-{dd}
    time_ISO8601=f"{time_f[0:10]}T{time_f[11:19]}Z"
    time_ISO8601_short=f"{time_f[0:10]}"
    return time_ISO8601_short

def mkdate(datestr):
   # function make time string for argument parser
   try:
    return datestr
   except ValueError:
    raise argparse.ArgumentTypeError(f"{datestr} time start is not in a proper format dd/MM/yy HH:mm:SS")

def convert_to_secs(tt):
   # The input time should be given in format "{yyyy}-{MM}-{dd}"
   time_format = f"{tt[8:10]}/{tt[5:7]}/{tt[0:4]} 00:00:00"
   obj2 = time.strptime(time_format,"%d/%m/%Y %H:%M:%S")
   time_secs = time.mktime(obj2)
   return time_secs

def extract_time(input_files, product_id):
   sorted_files = sorted(input_files)
   start_day = str(sorted_files[0]).replace('.nc','')[-10:]
   end_day = str(sorted_files[-1]).replace('.nc','')[-10:]
   return start_day, end_day

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
    #parser.add_argument('start_time',
    #                    type = mkdate,
    #                    help = ("Start time in the format dd/MM/yy HH:mm:SS")
    #)
    #parser.add_argument(
    #           'numbatches',
    #           type = int,
    #           help=("number of branches for chunk"),
    #)
    #parser.add_argument(
    #           'batchsize',
    #           type = int,
    #           help = ("batch size"),
    #)

    args = parser.parse_args()
    base_dir = Path(args.basedir)

    #    number_batches_to_append = int(args.numbatches)
    #batch_size = int(args.batchsize)
    #start_time = str(args.start_time)'''

    # set input and output paths
    service_id = "GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
    product_id = "global-analysis-forecast-wav-001-027"
    path_in_dir = base_dir / product_id / "nc"
    path_out_dir = base_dir / product_id

    # make sure the output dir exists
    path_out_dir.mkdir(parents=True, exist_ok=True)

    # set list of variables
    variables=["VPED", "VSDX", "VSDY"]

    start_day, end_day = extract_time(sorted(path_in_dir.glob("*.nc")), product_id)

    # set zarr store name
    for variable_name in variables:
        # select files containing variable {variable_name}
        input_files = sorted(path_in_dir.glob(f"*{variable_name}*.nc"))

        # convert files in nc directory to dataset using xarray
        nc_ds = xr.open_mfdataset(input_files, parallel=True, concat_dim="time", data_vars="minimal",combine='nested')

        # define zarr store name according to convention {product_id}/{product_id}_{variable_name}_{start_day}_{end_day}.zarr
        zar_store = f"{product_id}/{product_id}_{variable_name}_{start_day}_{end_day}.zarr"

        # convert dataset to zarr
        nc_ds.to_zarr(zar_store, mode="w")
