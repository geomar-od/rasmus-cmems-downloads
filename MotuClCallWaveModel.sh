#!/usr/bin/env bash

#times = times
#for t_s in $FILES
#do

lon_min=-180
lon_max=179.91667
lat_min=-80
lat_max=90
depth_min=0.493
depth_max=0.4942

#Stockes drift and wave data files

name_dir_out_nc="$(pwd)/GLOBAL_ANALYSIS_FORECAST_WAV_NC"
name_file_out="GLOBAL_ANALYSIS_FORECAST_WAVE_001_027-TDS"
mkdir -p $name_dir_out_nc
name_file_out_nc="GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS"
product_id="global-analysis-forecast-wav-001-027"
time_min="2021-01-23 21:00:00"
time_max="2021-01-24 00:00:00"
times=("2021-01-23 15:00:00" "2021-01-23 18:00:00" "2021-01-23 21:00:00" "2021-01-24 00:00:00")
for i in ${!times[@]};
do
  time_min=${times[$i]}
  time_max=$time_min
  time_stamp=$(echo $time_min | tr -s ' ' '_')
  name_file_out_nc="$name_file_out"_"$time_stamp"

python3 -m motuclient --motu http://nrt.cmems-du.eu/motu-web/Motu --service-id GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS --product-id $product_id --longitude-min $lon_min --longitude-max $lon_max --latitude-min $lat_min --latitude-max $lat_max --date-min $time_min --date-max $time_max --variable VPED --variable VSDX --variable VSDY --out-dir $name_dir_out_nc --out-name $name_file_out_nc".nc" --user  --pwd 
done
