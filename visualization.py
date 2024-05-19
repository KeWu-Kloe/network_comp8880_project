import os
import sys

import arcpy

arcpy.CheckOutExtension("network")

# create new vrp solver

vrp = arcpy.nax.VehicleRoutingProblem(nd_layer_name)

# analysis settings

vrp.distanceUnits = arcpy.nax.DistanceUnits.Miles
vrp.timeUnits = arcpy.nax.TimeUnits.Minutes
vrp.routeShapeType = arcpy.nax.RouteShapeType.TrueShape
vrp.returnStopShapes = True

# load input data from external system

input_orders = os.path.join(input_gdb, "Stores")
input_depots = os.path.join(input_gdb, "DistributionCenter")
input_routes = os.path.join(input_gdb, "SolveVehicleRoutingProblem_Routes")

# The order service time is in a field called "DeliveryDelay" and should default to 10 minutes
# if the field does not have a value.  Set up this field mapping:

field_mappings = vrp.fieldMappings(arcpy.nax.VehicleRoutingProblemInputDataType.Orders)
field_mappings["ServiceTime"].mappedFieldName = "DeliveryDelay"
field_mappings["ServiceTime"].defaultValue = 10

vrp.load(arcpy.nax.VehicleRoutingProblemInputDataType.Orders, input_orders, field_mappings)
vrp.load(arcpy.nax.VehicleRoutingProblemInputDataType.Depots, input_depots)
vrp.load(arcpy.nax.VehicleRoutingProblemInputDataType.Routes, input_routes)

# solve the analysis

vrp_result = vrp.solve()

if not vrp_result.solveSucceeded:
    print("Solved failed")
    print(vrp_result.solverMessages(arcpy.nax.MessageSeverity.All))
    sys.exit(0)

# update results in external system

output_stops = os.path.join(output_gdb, "AssignedStops")
output_routes = os.path.join(output_gdb, "Routes")

vrp_result.export(arcpy.nax.VehicleRoutingProblemOutputDataType.Stops, output_stops)
vrp_result.export(arcpy.nax.VehicleRoutingProblemOutputDataType.Routes, output_routes)

# send routes to drivers

route_data_file = os.path.join(cwd, "VRPRouteData.zip")

vrp_result.saveRouteData(route_data_file)

# uncomment to enable - disabled for UC demo while disconnected
# route_layer_item = arcpy.nax.ShareAsRouteLayers(route_data_file, share_with="MYORGANIZATION")
# print(f"Route layer item: {route_layer_item}")

print("VRP done!")