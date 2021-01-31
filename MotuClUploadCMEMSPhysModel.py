import argparse
import pandas as pd
from pathlib import Path
import sys, os

def change_time_format(time_f):
    # change format from "yyyy-MM-dd HH:mm:SS" to
    # ISO 8601 notation: {yyyy}-{MM}-{dd}T{HH}:{mm}:{SS}Z
    time_ISO8601=f"{time_f[0:10]}T{time_f[11:19]}Z"
    return time_ISO8601

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
            default="2021-01-23 21:00:00",
            help=("Set time start"),
    )
    parser.add_argument(
            "--time_max",
            default="2021-01-23 22:30:00",
            help=("Set time end"),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)

    print(base_dir)

    # parameters
    name_dir_out_nc = base_dir / "GLOBAL_ANALYSIS_FORECAST_PHY_NC"
    name_file_prefix = "PHY_001_24-TDS"
    service_id = "GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS"
    product_id = "global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh"
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

    # change time formats
    timestamp_nc_min = change_time_format(time_min)
    timestamp_nc_max = change_time_format(time_max)

    # make sure the output dir exists
    name_dir_out_nc.mkdir(parents=True, exist_ok=True)

    # name netcdf file : name_file_prefix _ timestamp_nc_min _ timestamp_nc_max.nc
    name_file_out_nc = f"{name_file_prefix}_{timestamp_nc_min}_{timestamp_nc_max}.nc"

    call_motu = f"python3 -m motuclient \
                --motu http://nrt.cmems-du.eu/motu-web/Motu \
                --service-id {service_id} --product-id {product_id} \
                 --longitude-min {str(lon_min)} --longitude-max {str(lon_max)} \
                 --latitude-min {str(lat_min)} --latitude-max {str(lat_max)} \
                 --date-min {time_min} --date-max {time_max} \
                 --depth-min {str(depth_min)} --depth-max {str(depth_max)} --variable uo --variable vo \
                 --out-dir {str(name_dir_out_nc)} --out-name {str(name_file_out_nc)}\
                 --user $MOTU_USER --pwd $MOTU_PASSWORD"

    os.system(call_motu)
