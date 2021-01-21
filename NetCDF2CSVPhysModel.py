from pathlib import Path
import xarray as xr
import pandas as pd

# to be move to a command line argument later
base_path = Path(".")

# set input and output paths
path_in_curr = base_path / "GLOBAL_ANALYSIS_FORECAST_PHY_NC"
path_out_curr = base_path / "GLOBAL_ANALYSIS_FORECAST_PHY_CSV"

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