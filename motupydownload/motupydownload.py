import argparse
from multiprocessing import Pool
from itertools import product
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import glob
import re
import sys, os

def call_motuclient(variable_name, day):
    # set time limits corresponding to start_time and end_time in string format
    start_time = (time_start + timedelta(day)).strftime("%Y-%m-%d")
    end_time = (time_start + timedelta(day + 1)).strftime("%Y-%m-%d")
    # set time limits for motuclient in format "YYYY-mm-dd ss:MM:HH"
    time_left_motu = f"{start_time}T00:00:00"
    time_right_motu = f"{end_time}T00:00:00"

    # name netcdf file : {product_id}_{varable_name}_{start_time}_{end_time}.nc
    name_file_out_nc = f"{product_id}_{variable_name}_{start_time}_{end_time}.nc"
    call_motu = (
        f"python3 -m motuclient "
        f"--motu {server_address} "
        f"--service-id {service_id} --product-id {product_id} "
        f"--longitude-min {str(lon_min)} --longitude-max {str(lon_max)} "
        f"--latitude-min {str(lat_min)} --latitude-max {str(lat_max)} "
        f"--date-min {time_left_motu} --date-max {time_right_motu} "
        f"--depth-min {str(depth_min)} --depth-max {str(depth_max)} "
        f"--variable {variable_name} "
        f"--out-dir {str(name_dir_out_nc)} --out-name {str(name_file_out_nc)} "
        f"--user {MOTU_USER} --pwd {MOTU_PASSWORD}"
    )
    if (
        (args.replace == True)
        or not (Path(name_dir_out_nc) / name_file_out_nc).exists()
    ):
        os.system(call_motu)
    else:
        print(f"skipping download of {name_file_out_nc}")

if __name__ == "__main__":

    # get base directory
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--basedir",
        default = ".",
        help = (
            "Base directory where the data dirs will be found." "\nDefaults to $PWD."
        ),
    )
    parser.add_argument(
        "--longitude_min",
        default = -180,
        help = ("Set boundary for minimum of longitude"),
    )
    parser.add_argument(
        "--longitude_max",
        default = 179.91667,
        help = ("Set boundary for maximum of longitude"),
    )
    parser.add_argument(
        "--latitude_min",
        default = -80,
        help = ("Set boundary for minimum of latitude"),
    )
    parser.add_argument(
        "--latitude_max",
        default = 90,
        help = ("Set boundary for maximum of latitude"),
    )
    parser.add_argument(
        "--depth_min",
        default = 0.493,
        help = ("Set boundary for upper depth layer"),
    )
    parser.add_argument(
        "--depth_max",
        default = 0.4942,
        help = ("Set boundary for lower depth layer"),
    )
    parser.add_argument(
        "--time_min",
        default = "2021-01-23 00:00:00",
        help = ("Set time start"),
    )
    parser.add_argument(
        "--time_max",
        default = "2021-01-26 00:00:00",
        help = ("Set time end"),
    )
    parser.add_argument(
        "--replace",
        default = False,
        help = ("force re-downloads"),
    )
    parser.add_argument(
        "--var", action = "append", help = "<Required> Add variable", required = False
    )
    parser.add_argument(
        "--service_id",
        default = "GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS",
        help = ("product name requested"),
    )
    parser.add_argument(
        "--product_id",
        default = "global-analysis-forecast-phy-001-024-hourly-t-u-v-ssh",
        help = ("file name for model"),
    )
    parser.add_argument(
        "--motu",
        default = "http://nrt.cmems-du.eu/motu-web/Motu",
        help = ("Server address for motuclient"),
    )
    parser.add_argument(
        "--parallel_downloads",
        default = 8,
        help = ("Number of parallel downloads. Defaults to 8."),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)

    # parameters
    service_id = args.service_id
    product_id = args.product_id
    name_dir_out_nc = base_dir / product_id / "nc"
    lon_min = args.longitude_min
    lon_max = args.longitude_max
    lat_min = args.latitude_min
    lat_max = args.latitude_max
    depth_min = args.depth_min
    depth_max = args.depth_max
    time_min = args.time_min
    time_max = args.time_max
    server_address = args.motu
    pool_size = args.parallel_downloads

    # Make sure times can be parsed
    # we use datetime.fromisoformat, which strangely cannot handle the Z
    # notation for indicating UTC
    time_min = re.sub("Z$", "+00:00", time_min)
    time_max = re.sub("Z$", "+00:00", time_max)

    # calculate number of number of days between initial and final time stamps
    num_days = (
        datetime.fromisoformat(time_max) - datetime.fromisoformat(time_min)
    ).days

    # make sure the output dir exists
    name_dir_out_nc.mkdir(parents=True, exist_ok=True)

    # get list of existing netcdf files inside netcdf dir
    nc_file_names = [os.path.basename(x) for x in glob.glob(f"{name_dir_out_nc}/*")]

    # set variables
    if args.var is not None:
        variables = args.var
    else:
        variables = []

    # extract start day from sting
    time_start = datetime.fromisoformat(time_min)
    time_end = datetime.fromisoformat(time_max)

    # Read password and username and use DUMMY string if not provided
    MOTU_USER = os.environ.get("MOTU_USER", "NONE")
    MOTU_PASSWORD = os.environ.get("MOTU_PASSWORD", "NONE")

    # generate range of days
    days = range(num_days)
    # define a combination consisting of variables and times for which downloading is performed
    #paramList = list(itertools.product(variables, days))
    paramList = [(variable_name, day) for (variable_name, day) in product(variables, days)]

    # call motuclient for every variable and write into daily output file
    with Pool(pool_size) as p:
      p.starmap(call_motuclient,[(variable_name, day) for (variable_name, day) in product(variables, days)])
