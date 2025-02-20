import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point, LineString
import pooch

shapefile = pooch.retrieve("https://www2.census.gov/geo/tiger/TIGER2020/ROADS/tl_2020_49035_roads.zip", None)

slc_roads = gpd.read_file("zip://" + shapefile)

#display(slc_roads)
print(slc_roads.columns)

# creating a graph from the shapefile
graph = nx.Graph()
for idx, row in slc_roads.iterrows():
    geom = row['geometry']
    road_name = row['FULLNAME']
    road_type = row['RTTYP'] # Route Type Code describes type of road

    def calculate_distance(coord1, coord2):
        return LineString([coord1, coord2]).length

    if geom.geom_type == 'LineString':
        coords = list(geom.coords)
        for i in range(len(coords) - 1):
            start_node = coords[i]
            end_node = coords[i + 1]
            weight = calculate_distance(start_node, end_node)
            graph.add_edge(
                start_node,
                end_node,
                weight=weight,
                name=road_name,
                road_type=road_type
            )
    elif geom.geom_type == 'MultiLineString':
        for line in geom.geoms:
            coords = list(line.coords)
            for i in range(len(coords) - 1):
                start_node = coords[i]
                end_node = coords[i + 1]
                weight = calculate_distance(start_node, end_node)
                graph.add_edge(
                    start_node,
                    end_node,
                    weight=weight,
                    name=road_name,
                    road_type=road_type
                )