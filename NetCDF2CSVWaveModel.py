# -*- coding: UTF-8 -*-

import sys, os
import netCDF4
import pandas as pd
import numpy as np
import csv

path_in_wave = "/home/eshchekinova/Documents/CMEMSPython/GLOBAL_ANALYSIS_FORECAST_WAV_NC/"
path_out_wave = "/home/eshchekinova/Documents/CMEMSPython/GLOBAL_ANALYSIS_FORECAST_WAV_CSV/"


if not os.path.exists(path_out_wave):
 os.makedirs(path_out_wave)

# read wave data model from global analysis and forecast data

file_names = os.listdir(path_in_wave)

for fullname in file_names:
    if os.path.isfile(os.path.join(path_in_wave, fullname)):
       filename=os.path.splitext(fullname)[0]
       print(filename)
       nc = netCDF4.Dataset(path_in_wave+filename+'.nc', mode='r')
       for var in nc.variables:
          print(var)
# get coordinates variables
       lats = nc.variables['latitude'][:]
       lons = nc.variables['longitude'][:]
       Stocks_u= nc.variables['VSDX'][:][:][:]
       Stocks_v= nc.variables['VSDY'][:][:][:]
       times = nc.variables['time'][:]
# convert date, how to store date only strip away time?
       units = nc.variables['time'].units
       dates = netCDF4.num2date (times[:], units=units, calendar='365_day')
#write to file
# os.chdir(path_out_curr)
       with open(path_out_wave+filename+'.csv', 'w') as csvFile:
            outputwriter = csv.writer(csvFile, delimiter=',')
        #    for time_index, time in enumerate(times): # pull the dates out for the header
        #        t = netCDF4.num2date(time, units = units, calendar='365_day')
        #        header.append(t)
        #    outputwriter.writerow(header)
            for latlon_index, (lat,lon) in enumerate(zip(lats, lons)):
                content = [lat, lon] # Put lat 2and lon into list
                for time_index, time in enumerate(times): # for a date
                   # extract the data
                    data = Stocks_u[time_index,latlon_index]
                    content.append(data)
                    outputwriter.writerow(content)
            for latlon_index, (lat,lon) in enumerate(zip(lats, lons)):
                content = [lat, lon] # Put lat 2and lon into list
                for time_index, time in enumerate(times): # for a date
                    data = Stocks_v[time_index,latlon_index]
                    content.append(data)
                    outputwriter.writerow(content)
# close the output file
       csvFile.close()
# close netcdf
       nc.close()
