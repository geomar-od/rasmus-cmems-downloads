import argparse
from multiprocessing import Pool
from itertools import product
from datetime import datetime, timedelta
from pathlib import Path
from functools import partial
import re
import os
import subprocess


def call_motuclient(
    variable_name: str = None,
    day: int = 0,
    server_address: str = None,
    product_id: str = None,
    service_id: str = None,
    longitude_min: float = None,
    longitude_max: float = None,
    latitude_min: float = None,
    latitude_max: float = None,
    depth_min: float = None,
    depth_max: float = None,
    time_min: datetime = None,
    name_dir_out_nc: str = None,
    MOTU_USER: str = None,
    MOTU_PASSWORD: str = None,
    **kwargs,
):
    """Wrap call to the motuclient."""
    # Derive start and end time
    time_left = (time_min + timedelta(days=day)).strftime("%Y-%m-%dT00:00:00")
    time_right = (time_min + timedelta(days=day + 1)).strftime("%Y-%m-%dT00:00:00")

    # name netcdf file : {product_id}_{varable_name}_{start_time}_{end_time}.nc
    name_file_out_nc = (
        f"{product_id}_{variable_name}_"
        f"{time_left.split('T')[0]}_{time_right.split('T')[0]}.nc"
    )

    # prepare system call
    call_motu = [
        "python3",
        "-m",
        "motuclient",
        "--motu",
        server_address,
        "--service-id",
        service_id,
        "--product-id",
        product_id,
        "--longitude-min",
        str(longitude_min),
        "--longitude-max",
        str(longitude_max),
        "--latitude-min",
        str(latitude_min),
        "--latitude-max",
        str(latitude_max),
        "--date-min",
        time_left,
        "--date-max",
        time_right,
        "--depth-min",
        str(depth_min),
        "--depth-max",
        str(depth_max),
        "--variable",
        variable_name,
        "--out-dir",
        str(name_dir_out_nc),
        "--out-name",
        str(name_file_out_nc),
        "--user",
        MOTU_USER,
        "--pwd",
        MOTU_PASSWORD,
    ]

    # only download if not present or if re-downloading is wanted
    if (args.replace == True) or not (
        Path(name_dir_out_nc) / name_file_out_nc
    ).exists():
        subprocess.call(call_motu)
    else:
        print(f"skipping download of {name_file_out_nc}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--basedir",
        default=".",
        help=(
            "Base directory where the data dirs will be found." "\nDefaults to $PWD."
        ),
    )
    parser.add_argument(
        "--longitude_min",
        default=-180,
        help=("Set boundary for minimum of longitude"),
    )
    parser.add_argument(
        "--longitude_max",
        default=180,
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
    parser.add_argument(
        "--var", action="append", help="<Required> Add variable", required=False
    )
    parser.add_argument(
        "--service_id",
        default="GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS",
        help=("product name requested"),
    )
    parser.add_argument(
        "--product_id",
        default="global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh",
        help=("file name for model"),
    )
    parser.add_argument(
        "--server_address",
        default="http://nrt.cmems-du.eu/motu-web/Motu",
        help=("Server address for motuclient"),
    )
    parser.add_argument(
        "--parallel_downloads",
        default=8,
        help=("Number of parallel downloads. Defaults to 8."),
    )
    parser.set_defaults(replace=False)
    parser.add_argument(
        "--replace",
        dest="replace",
        action="store_true",
        help=("Flag forces re-downloads."),
    )
    args = parser.parse_args()

    # construct and create output directory
    base_dir = Path(args.basedir)
    product_id = args.product_id
    name_dir_out_nc = base_dir / product_id / "nc"
    name_dir_out_nc.mkdir(parents=True, exist_ok=True)

    # read desired start and end time, make sure zero-offset time zone
    # can be read, and cast to datetime object.
    time_min = datetime.fromisoformat(re.sub("Z$", "+00:00", args.time_min))
    time_max = datetime.fromisoformat(re.sub("Z$", "+00:00", args.time_max))

    # calculate number of number of days between initial and final time stamps
    num_days = (time_max - time_min).days

    # read variables
    if args.var is not None:
        variables = args.var
    else:
        variables = []

    # Read password and username and use DUMMY string if not provided
    MOTU_USER = os.environ.get("MOTU_USER", "NONE")
    MOTU_PASSWORD = os.environ.get("MOTU_PASSWORD", "NONE")

    # Wrap motucall. `partial` will pre-populate all keyword arguments
    # that won't change in the iteration
    args_dict = vars(args)
    _ = args_dict.pop("time_min")
    call_motuclient_partial = partial(
        call_motuclient,
        **vars(args),  # a dict view of the args
        name_dir_out_nc=name_dir_out_nc,
        MOTU_USER=MOTU_USER,
        MOTU_PASSWORD=MOTU_PASSWORD,
        time_min=time_min,
    )

    # call motuclient for every variable and write into daily output file
    pool_size = int(args.parallel_downloads)
    with Pool(pool_size) as p:
        p.starmap(call_motuclient_partial, product(variables, range(num_days)))
