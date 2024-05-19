import os
import datetime

import arcpy

arcpy.CheckOutExtension("network")

# data locations

cwd = os.path.dirname(os.path.abspath(__file__))
nd_path = os.path.join(cwd, r'SanFrancisco.gdb\Transportation\Streets_ND')
nd_layer_name = "SanFrancisco"

arcpy.nax.MakeNetworkDatasetLayer(nd_path, nd_layer_name)

# create network dataset object

network_dataset = arcpy.nax.NetworkDataset(nd_layer_name)

# sum up the Meters attribute values for all edges

total_distance_in_meters = 0
edge_count = 0
oneway_count = 0

for edge in network_dataset.edges([], ["Meters", "Oneway"]):
    total_distance_in_meters += edge[0]
    edge_count += 1
    if edge[1]:
        oneway_count += 1

print(f"Total network edges distance: {total_distance_in_meters/1000:.2f} kilometers")
print(f"Total edge count: {edge_count}")
print(f"Oneway edge count: {oneway_count}")
print(f"Oneway edge percentage: {oneway_count/edge_count*100:.2f}%")