import argparse
import pandas as pd
from pathlib import Path
import xarray as xr
import sys

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
name_file_out = "GLOBAL_ANALYSIS_FORECAST_PHY_001_24-TDS"
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

# make sure the output dir exists
name_dir_out_nc.mkdir(parents=True, exist_ok=True)

call_motu = "python3 -m motuclient \
  --motu http://nrt.cmems-du.eu/motu-web/Motu \
  --service-id "${service_id}" --product-id $product_id \
  --longitude-min $lon_min --longitude-max $lon_max \
  --latitude-min $lat_min --latitude-max $lat_max \
  --date-min "$time_min" --date-max "$time_max" \
  --depth-min $depth_min --depth-max $depth_max \
  --variable uo --variable vo \
  --out-dir "$name_dir_out_nc" --out-name "${name_file_out_nc}.nc" \
  --user "${MOTU_USER}" --pwd "${MOTU_PASSWORD}" ""

os.system(call_motu)
