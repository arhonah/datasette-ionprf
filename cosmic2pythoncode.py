from netCDF4 import Dataset
import numpy as np
import sys
rootgrp = Dataset("data/ionPrf_C2E4.2024.203.00.33.G26_0001.0001_nc", "r")
rootgrp.variables.keys()
lat = rootgrp.variables["GEO_lat"]
lon = rootgrp.variables["GEO_lon"]
latlon = np.dstack((lat, lon))
f = open("my_data2.csv", "w")
f.write("latitude,longitude\n")
for ll in latlon:
    for mm in ll:
        f.write(str(mm[0]) + "," + str(mm[1]) + "\n")
f.close()
exit()
