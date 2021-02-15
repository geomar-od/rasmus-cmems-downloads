import argparse
from datetime import datetime
from pathlib import Path
import re
import sys, os


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
        "--longitude_min", default=-180, help=("Set boundary for minimum of longitude"),
    )
    parser.add_argument(
        "--longitude_max",
        default=-179.91667,
        help=("Set boundary for maximum of longitude"),
    )
    parser.add_argument(
        "--latitude_min", default=-80, help=("Set boundary for minimum of latitude"),
    )
    parser.add_argument(
        "--latitude_max", default=90, help=("Set boundary for maximum of latitude"),
    )
    parser.add_argument(
        "--depth_min", default=0.493, help=("Set boundary for upper depth layer"),
    )
    parser.add_argument(
        "--depth_max", default=0.4942, help=("Set boundary for lower depth layer"),
    )
    parser.add_argument(
        "--time_min", default="2021-01-23T21:00:00+00:00", help=("Set time start"),
    )
    parser.add_argument(
        "--time_max", default="2021-01-23T22:30:00+00:00", help=("Set time end"),
    )
    args = parser.parse_args()
    base_dir = Path(args.basedir)

    print(base_dir)

    # parameters
    service_id = "GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
    product_id = "global-analysis-forecast-wav-001-027"
    name_dir_out_nc = base_dir / product_id / "nc"
    lon_min = args.longitude_min
    lon_max = args.longitude_max
    lat_min = args.latitude_min
    lat_max = args.latitude_max
    depth_min = args.depth_min
    depth_max = args.depth_max
    time_min = args.time_min
    time_max = args.time_max

    # make sure the output dir exists
    name_dir_out_nc.mkdir(parents=True, exist_ok=True)

    # Make sure times can be parsed
    # we use datetime.fromisoformat, which strangely cannot handle the Z
    # notation for indicating UTC
    time_min = re.sub("Z$", "+00:00", time_min)
    time_max = re.sub("Z$", "+00:00", time_max)

    # extract start day (needed for file name)
    start_day = datetime.fromisoformat(time_min).strftime("%Y-%m-%d")

    variables = ["VPED", "VSDX", "VSDY"]

    # call motuclient for every variable and write into output file
    for variable_name in variables:
        # name netcdf file : {product_id}_{varable_name}_{start_day}.nc
        name_file_out_nc = f"{product_id}_{variable_name}_{start_day}.nc"
        call_motu = (
            f"python3 -m motuclient "
            f"--motu http://nrt.cmems-du.eu/motu-web/Motu "
            f"--service-id {service_id} --product-id {product_id} "
            f"--longitude-min {str(lon_min)} --longitude-max {str(lon_max)} "
            f"--latitude-min {str(lat_min)} --latitude-max {str(lat_max)} "
            f"--date-min {time_min} --date-max {time_max} "
            f"--depth-min {str(depth_min)} --depth-max {str(depth_max)} "
            f"--variable {variable_name} "
            f"--out-dir {str(name_dir_out_nc)} --out-name {str(name_file_out_nc)} "
            f"--user {os.environ['MOTU_USER']} --pwd {os.environ['MOTU_PASSWORD']}"
        )
        os.system(call_motu)
