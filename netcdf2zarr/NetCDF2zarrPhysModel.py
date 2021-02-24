"""Conversion from netcdf to zarr_store using xarray and zarr.

"""

import argparse
import pandas as pd
from pathlib import Path
import xarray as xr


def xr_time_coord_to_day_string(time):
    dt = pd.to_datetime(time.data)
    dt = dt.to_pydatetime()
    return dt.strftime("%Y-%m-%d")


# a quick test: Ensure that the above function returns the correct
# day string for a known time stamp
def test_xr_time_coord_to_day_string():
    """Test functionality of xr_time_coord_to_day_string.

    Ensure that the above function returns the correct
    day string for a known time stamp."""
    assert "2001-01-23" == xr_time_coord_to_day_string(
        xr.DataArray(pd.Timestamp("2001-01-23T01:23:45Z"))
    )


# run test
test_xr_time_coord_to_day_string()


if __name__ == "__main__":
    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--basedir",
        default=".",
        help=(
            "Base directory where the data dirs will be found." "\nDefaults to $PWD."
        ),
    )
    parser.add_argument(
        "--product_id",
        default="global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh",
        help=(
            "Product ID."
            "\nDefaults to global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh."
        ),
    )
    parser.add_argument(
        "--var", action="append", help="<Required> Add variable", required=True
    )

    args = parser.parse_args()
    base_dir = Path(args.basedir)
    variables = args.var
    product_id = args.product_id

    # set input and output paths
    path_in_dir = base_dir / product_id / "nc"
    path_out_dir = base_dir / product_id

    # make sure the output dir exists
    path_out_dir.mkdir(parents=True, exist_ok=True)

    # set zarr store name
    for variable_name in variables:
        # select files containing variable {variable_name}
        input_files = sorted(path_in_dir.glob(f"*{variable_name}*.nc"))

        # convert files in nc directory to dataset using xarray
        nc_ds = xr.open_mfdataset(
            input_files,
            parallel=True,
            concat_dim="time",
            data_vars="minimal",
            combine="nested",
        )

        start_day = xr_time_coord_to_day_string(nc_ds.time.min())
        end_day = xr_time_coord_to_day_string(nc_ds.time.max())

        # define zarr store name according to convention
        # {product_id}/{product_id}_{variable_name}_{start_day}_{end_day}.zarr
        zarr_store_name = (
            f"{product_id}/zarr/{product_id}_{variable_name}_{start_day}_{end_day}.zarr"
        )

        # convert dataset to zarr
        zarr_store = nc_ds.to_zarr(zarr_store_name, mode="w")
