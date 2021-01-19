import numpy as np
# size of data for a surface layer for two variables u, v , domain cover - global
# model - GLOBAL_ANALYSIS_FORECAST_PHY, time resolution one-hourly instantaneous, spatial resolution 1/12 grad

single_time_stamp_size=33.659
number_hours=24*365

# take entire year, 50 depth layers
total_size =single_time_stamp_size*number_hours*50

print(total_size)
#294852.84 MB = 294 852 840 000 bytes ~ 295 GB size of data for full domain , single depth layer, one year period
# 14742642 MB = 14.7 TB size of data for full domain, one year period and 50 depth layers

# size of data for a surface layer for two variables u, v , domain cover - global
# model - GLOBAL_ANALYSIS_FORECAST_WAV, time resolution three-hourly instantaneous, spatial resolution 1/12 grad

#single_time_stamp_size=33.683 # only Stockes drift components
single_time_stamp_size=285.943 # all variables for wave model

number_hours=24*365

total_size =single_time_stamp_size*number_hours

print(total_size)
#295063.08 MB ~ 295 GB size of data for full domain , single depth layer, one year period, only Stockes drift compoments
#2504860.68 MB ~ 2.4 TB size of data for full domain, surface layer, all variables for wave model 
