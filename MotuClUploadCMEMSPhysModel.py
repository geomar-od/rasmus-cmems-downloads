import argparse
import pandas as pd
from pathlib import Path
import sys, os

def change_time_format(timemin,timemax):
    # change time format from "yyyy-MM-dd HH:mm:SS" to "ddMMyyyyHHmmSS"
    timestamp_nc = timemin.replace("-","").replace(":","").replace(" ","")
    t_min=timestamp_nc[6:8]+timestamp_nc[4:6]+timestamp_nc[0:4]+\
          timestamp_nc[8::]
    timestamp_mc = ""
    timestamp_nc = timemax.replace("-","").replace(":","").replace(" ","")
    t_max=timestamp_nc[6:8]+timestamp_nc[4:6]+timestamp_nc[0:4]+\
                timestamp_nc[8::]
    return t_min,  t_max

if __name__ == "__main__":

    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--basedir",
            default=".",
            help=("Base directory where the data dirs will be found." "\nDefaults to $PWD."),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)
    print(base_dir)

    # parameters
    name_dir_out_nc = base_dir / "GLOBAL_ANALYSIS_FORECAST_PHY_NC"
    name_file_prefix = "GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS"
    service_id = "GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS"
    product_id = "global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh"
    lon_min = -180
    lon_max = 179.91667
    lat_min = -80
    lat_max = 90
    depth_min = 0.493
    depth_max = 0.4942
    time_min = "2021-01-23 21:00:00"
    time_max = "2021-01-23 22:30:00"

    # change time format
    timestamp_nc_min,  timestamp_nc_max = change_time_format(time_min, time_max)

    # make sure the output dir exists
    name_dir_out_nc.mkdir(parents=True, exist_ok=True)

    # name netcdf file : name_file_prefix _ timestamp_nc_min _ timestamp_nc_max.nc
    name_file_out_nc = name_file_prefix + "_" + timestamp_nc_min + \
                   "_" + timestamp_nc_max + ".nc"

    call_motu = "python3 -m motuclient " + \
                "--motu http://nrt.cmems-du.eu/motu-web/Motu " + \
                "--service-id "+service_id + " --product-id "+ product_id + \
                " --longitude-min " + str(lon_min) + " --longitude-max " + str(lon_max) + \
                " --latitude-min " + str(lat_min) + " --latitude-max " + str(lat_max) + \
                " --date-min " + time_min + " --date-max " + time_max  + \
                " --depth-min " + str(depth_min) + " --depth-max " + str(depth_max)  + \
                " --variable " + "uo" + " --variable " + "vo" + \
                " --out-dir " + str(name_dir_out_nc) + " --out-name " + name_file_out_nc + \
                " --user " + "${MOTU_USER}" + " --pwd " + "${MOTU_PASSWORD}"

    os.system(call_motu)
