import os
import sys
import datetime
import csv

import arcpy

arcpy.CheckOutExtension("network")

# data locations

cwd = os.path.dirname(os.path.abspath(__file__))
nd_path = os.path.join(cwd, r'SanFrancisco.gdb\Transportation\Streets_ND')
nd_layer_name = "SanFrancisco"

arcpy.nax.MakeNetworkDatasetLayer(nd_path, nd_layer_name)

# create new OD solver

od = arcpy.nax.OriginDestinationCostMatrix(nd_layer_name)

# analysis settings

od.timeUnits = arcpy.nax.TimeUnits.Seconds
od.distanceUnits = arcpy.nax.DistanceUnits.Feet

# load data using insert cursors

origins_insert_cursor = od.insertCursor(arcpy.nax.OriginDestinationCostMatrixInputDataType.Origins, ["Name", "SHAPE@XY"])
destinations_insert_cursor = od.insertCursor(arcpy.nax.OriginDestinationCostMatrixInputDataType.Destinations, ["Name", "SHAPE@XY"])

locations = os.path.join(cwd, r'AddressesSF.csv')

with open(locations) as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        lon = row[0] 
        lat = row[1]
        name = row[2]
        origins_insert_cursor.insertRow([name, (float(lon), float(lat))])
        destinations_insert_cursor.insertRow([name, (float(lon), float(lat))])


# solve od

result = od.solve()

if not result.solveSucceeded:
    print("Solved failed")
    print(result.solverMessages(arcpy.nax.MessageSeverity.All))
    sys.exit(0)

# write a new csv file with rows for each od pair
# skip when origin is the same as the destination

csv_output = os.path.join(cwd, r'lines.csv')
csv_fields = ["OriginOID", "DestinationOID", "Total_Time", "Total_Distance"]

with open(csv_output, 'w+') as out_file:
    writer = csv.writer(out_file, lineterminator ='\n')
    writer.writerow(csv_fields)  # header row with field names
    with result.searchCursor(arcpy.nax.OriginDestinationCostMatrixOutputDataType.Lines, csv_fields) as cursor:
        for row in cursor:
            if row[0] != row[1]:
                writer.writerow([row[0], row[1], row[2], row[3]])

print("OD Done!")