import os
import sys

import arcpy

arcpy.CheckOutExtension("network")

# data locations

cwd = os.path.dirname(os.path.abspath(__file__))
nd_source = os.path.join(cwd, r'SanFrancisco.gdb\Transportation\Streets_ND')
# nd_source = "https://www.arcgis.com"

stops_path = os.path.join(cwd, r'SanFrancisco.gdb\Analysis\CentralDepots')

# create new route solver

route = arcpy.nax.Route(nd_source)

# analysis settings

nd_travel_modes = arcpy.nax.GetTravelModes(nd_source)
travel_mode = nd_travel_modes["Driving Time"]
route.travelMode = travel_mode

# load data

route.load(arcpy.nax.RouteInputDataType.Stops, stops_path)

# solve route

result = route.solve()

# export results

if result.solveSucceeded:
    result.export(arcpy.nax.RouteOutputDataType.Routes, "memory/exportRoutes")
else:
    print("Solved failed")
    print(result.solverMessages(arcpy.nax.MessageSeverity.All))
    sys.exit(0)

with arcpy.da.SearchCursor("memory/exportRoutes", ["Name", "Total_Kilometers"]) as cursor:
    for row in cursor:
        print(f'Route: {row[0]}')
        print(f'Total Distance: {row[1]:.2f} Kilometers')
