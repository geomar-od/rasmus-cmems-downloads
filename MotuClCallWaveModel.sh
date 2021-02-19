#!/usr/bin/env bash

# read base dir (if any)
if [ $# -eq 0 ]; then
    echo "No arguments provided, will use $(pwd) as base dir."
    base_dir="$(pwd)"
else
    base_dir="$1"
fi

# parameters
name_dir_out_nc="${base_dir}/GLOBAL_ANALYSIS_FORECAST_WAV_NC"
name_file_out="GLOBAL_ANALYSIS_FORECAST_WAVE_001_027-TDS"
name_file_out_nc="GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
product_id="global-analysis-forecast-wav-001-027"
service_id="GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
lon_min=-180
lon_max=179.91667
lat_min=-80
lat_max=90
times=("2021-01-23 15:00:00" "2021-01-23 18:00:00" "2021-01-23 21:00:00" "2021-01-24 00:00:00")

# make sure output dir exists
mkdir -p "$name_dir_out_nc"

# loop over each time step and download the respective file
for i in "${!times[@]}";
do
  time_min=${times[$i]}
  time_max=$time_min
  time_stamp=$(echo "$time_min" | tr -s ' ' '_')
  name_file_out_nc="$name_file_out"_"$time_stamp"
  python3 -m motuclient \
    --motu http://nrt.cmems-du.eu/motu-web/Motu \
    --service-id "$service_id" --product-id $product_id \
    --longitude-min $lon_min --longitude-max $lon_max \
    --latitude-min $lat_min --latitude-max $lat_max \
    --date-min "$time_min" --date-max "$time_max" \
    --variable VPED --variable VSDX --variable VSDY \
    --out-dir "$name_dir_out_nc" --out-name "${name_file_out_nc}.nc" \
    --user "${MOTU_USER}" --pwd "${MOTU_PASSWORD}"
done
