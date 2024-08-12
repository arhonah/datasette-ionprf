from netCDF4 import Dataset
import os
f = open("my_bigdata.csv", "w")
f.write("longitude,latitude,altitude,ttj\n")
for file in os.listdir("data"):
    if file.endswith(".0001_nc"):
        rootgrp = Dataset("data/"+file, "r")
        lat = rootgrp.edmaxlat
        lon = rootgrp.edmaxlon
        alt = rootgrp.edmaxalt
        time = rootgrp.edmaxtime
        f.write(str(lon) + "," + str(lat) + "," + str(alt) + "," + str(time)+"\n")
f.close()
