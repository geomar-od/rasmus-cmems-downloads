import argparse
import pandas as pd
from pathlib import Path
import xarray as xr
import sys, os

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
name_dir_out_nc = base_dir / "GLOBAL_ANALYSIS_FORECAST_WAV_NC"
name_file_out = "GLOBAL_ANALYSIS_FORECAST_WAVE_001_027-TDS"
service_id="GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
product_id="global-analysis-forecast-wav-001-027"
lon_min = -180
lon_max = 179.91667
lat_min = -80
lat_max = 90
depth_min = 0.493
depth_max = 0.4942
time_min = "2021-01-23 15:00:00"
time_max = "2021-01-24 00:00:00"

# make sure the output dir exists
name_dir_out_nc.mkdir(parents=True, exist_ok=True)

name_file_out_nc = name_file_out + time_min.replace(":","_").replace(" ","_") + time_max.replace(":","_").replace(" ","_") + ".nc"
call_motu = "python3 -m motuclient " + \
  "--motu http://nrt.cmems-du.eu/motu-web/Motu " + \
  "--service-id "+service_id + " --product-id "+ product_id + \
  " --longitude-min " + str(lon_min) + " --longitude-max " + str(lon_max) + \
  " --latitude-min " + str(lat_min) + " --latitude-max " + str(lat_max) + \
  " --date-min " + time_min + " --date-max " + time_max  + \
  " --depth-min " + str(depth_min) + " --depth-max " + str(depth_max)  + \
  " --variable " + "VPED" + " --variable " + "VSDX" + " --variable " + "VSDY" + \
  " --out-dir " + str(name_dir_out_nc) + " --out-name " + name_file_out_nc + \
  " --user " + MOTU_USER + " --pwd " + MOTU_PASSWORD

os.system(call_motu)
