from netCDF4 import Dataset
import os 
import datetime

gps_epoch = datetime.datetime(1980, 1, 6)
f = open("my_bigdata.csv", "w")
f.write("longitude,latitude,altitude,ttj,critfreq,\n")
for file in os.listdir("data"):
    if file.endswith(".0001_nc"):
        rootgrp = Dataset("data/"+file, "r")
        lat = rootgrp.edmaxlat
        lon = rootgrp.edmaxlon
        alt = rootgrp.edmaxalt
        gps_seconds = rootgrp.edmaxtime
        cf = rootgrp.critfreq
        datetime_object = gps_epoch + datetime.timedelta(seconds=gps_seconds)
        dt_str = str(datetime_object)
        f.write(str(lon) + "," + str(lat) + "," + str(alt) + "," + dt_str + "," + str(cf)+"\n")
f.close()
