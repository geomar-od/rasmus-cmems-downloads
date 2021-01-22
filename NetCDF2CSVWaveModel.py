import argparse
import pandas as pd
from pathlib import Path
import xarray as xr

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

# set input and output paths
path_in_curr = base_dir / "GLOBAL_ANALYSIS_FORECAST_WAV_NC"
path_out_curr = base_dir / "GLOBAL_ANALYSIS_FORECAST_WAV_CSV"

# make sure output path exists
path_out_curr.mkdir(parents=True, exist_ok=True)

# find all input files
input_files = sorted(path_in_curr.glob("*.nc"))

# loop over input files and use netCDF -> xarray -> pandas -> CSV
for input_file in input_files:
    output_file = path_out_curr / f'{".".join(input_file.name.split(".")[:-1])}.csv'

    print(f"will convert {str(input_file)} to {str(output_file)}.")

    nc_ds = xr.open_dataset(input_file)
    pd_df = nc_ds.to_dataframe()
    pd_df.to_csv(output_file)