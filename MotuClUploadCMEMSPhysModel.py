import argparse
import pandas as pd
from pathlib import Path
import sys, os
from datetime import datetime
import time

def change_time_format(time_f):
    # change format from "yyyy-MM-dd HH:mm:SS" to
    # ISO 8601 notation: {yyyy}-{MM}-{dd}T{HH}:{mm}:{SS}Z
    # ISO 8601 date: {yyyy}-{MM}-{dd}
    time_ISO8601=f"{time_f[0:10]}T{time_f[11:19]}Z"
    time_ISO8601_short=f"{time_f[0:10]}"
    return time_ISO8601_short

def convert_to_secs(tt):
   # The input time should be given in format "{yyyy}-{MM}-{dd}"
   time_format = f"{tt[8:10]}/{tt[5:7]}/{tt[0:4]} 00:00:00"
   obj2 = time.strptime(time_format,"%d/%m/%Y %H:%M:%S")
   time_secs = time.mktime(obj2)
   return time_secs

if __name__ == "__main__":

    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--basedir",
            default=".",
            help=("Base directory where the data dirs will be found." "\nDefaults to $PWD."),
    )
    parser.add_argument(
            "--longitude_min",
            default=-180,
            help=("Set boundary for minimum of longitude"),
    )
    parser.add_argument(
            "--longitude_max",
            default=-179.91667,
            help=("Set boundary for maximum of longitude"),
    )
    parser.add_argument(
            "--latitude_min",
            default=-80,
            help=("Set boundary for minimum of latitude"),
    )
    parser.add_argument(
            "--latitude_max",
            default=90,
            help=("Set boundary for maximum of latitude"),
    )
    parser.add_argument(
            "--depth_min",
            default=0.493,
            help=("Set boundary for upper depth layer"),
    )
    parser.add_argument(
            "--depth_max",
            default=0.4942,
            help=("Set boundary for lower depth layer"),
    )
    parser.add_argument(
            "--time_min",
            default="2021-01-23 00:00:00",
            help=("Set time start"),
    )
    parser.add_argument(
            "--time_max",
            default="2021-01-26 00:00:00",
            help=("Set time end"),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)

    # parameters
    service_id = "GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS"
    product_id = "global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh"
    name_dir_out_nc = base_dir / product_id / "nc"
    #lon_min = -180
    #lon_max = 179.91667
    #lat_min = -80
    #lat_max = 90
    #depth_min = 0.493
    #depth_max = 0.4942
    #time_min = "2021-01-23 21:00:00"
    #time_max = "2021-01-23 22:30:00"
    lon_min = args.longitude_min
    lon_max = args.longitude_max
    lat_min = args.latitude_min
    lat_max = args.latitude_max
    depth_min = args.depth_min
    depth_max = args.depth_max
    time_min = args.time_min
    time_max = args.time_max

    #convert starting time and ending time to iso 8601 format
    start_day = change_time_format(time_min)
    end_day = change_time_format(time_max)

    start_sec = convert_to_secs(start_day)
    end_sec = convert_to_secs(end_day)

    # make sure the output dir exists
    name_dir_out_nc.mkdir(parents=True, exist_ok=True)

    # set variables
    variables=["uo", "vo"]
    initial_times=[]

    # total number of days
    num_days =  int((convert_to_secs(time_max) - convert_to_secs(time_min))/3600/24) + 1

    for day in range(num_days):
        next_day = f"{time_min[0:4]}-{time_min[5:7]}-{str(int(time_min[8:10])+day)}"
        initial_times.append(next_day)

    # call motuclient for every variable and write into output file
    for variable_name in variables:
       for time_start in initial_times:
           # name netcdf file : {product_id}_{varable_name}_{start_day}.nc
           name_file_out_nc = f"{product_id}_{variable_name}_{time_start}.nc"
           call_motu = (f"python3 -m motuclient "
                f"--motu http://nrt.cmems-du.eu/motu-web/Motu "
                f"--service-id {service_id} --product-id {product_id} "
                f"--longitude-min {str(lon_min)} --longitude-max {str(lon_max)} "
                f"--latitude-min {str(lat_min)} --latitude-max {str(lat_max)} "
                f"--date-min {time_min} --date-max {time_min} "
                f"--depth-min {str(depth_min)} --depth-max {str(depth_max)} "
                f"--variable {variable_name} "
                f"--out-dir {str(name_dir_out_nc)} --out-name {str(name_file_out_nc)} "
                f"--user {os.environ['MOTU_USER']} --pwd {os.environ['MOTU_PASSWORD']}"
           )
           os.system(call_motu)
