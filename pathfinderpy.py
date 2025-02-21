import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point, LineString
import pooch
import folium 


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
#visualizing road_network
bounds = slc_roads.total_bounds
center_lat = (bounds[1] + bounds[3]) / 2
center_long = (bounds[0] + bounds[2]) / 2

m = folium.Map(location=[center_lat, center_long], zoom_start=11)

folium.GeoJson(slc_roads).add_to(m)

#getting street names

street_names = set(nx.get_edge_attributes(graph, 'name').values())

#print("Number of street names in road network:", len(street_names))

#print("example street names")
#for street in list(street_names)[:5]:
#    print(street)

def find_street_name(street_name_search):
    search = street_name_search.lower()

    street_name_variations = {
        'street': ['st'],
        'avenue': ['ave'],
        'boulevard': ['blvd'],
        'road': ['rd'],
        'drive': ['dr'],
        'lane': ['ln',],
        'circle': ['cir'],
        'south': ['s'],
        'north': ['n'],
        'west': ['w'],
        'east': ['e']
    }

    search_variations = []
    words = search.split()

    for word in words:
        for street, var in street_name_variations.items():
            if word in var or word == street:
                search_variations.extend(var)
                break
        else:
            search_variations.append(word)

    street_names_lower = {}
    for street in street_names:
        if street:
            lower_case = street.lower()
            street_names_lower[lower_case] = street
    matches = []
    for street in street_names_lower:
        found_all_terms = True
        for search_var in search_variations:
            if search_var not in street:
                found_all_terms = False
                break
        if found_all_terms:
            matches.append(street_names_lower[street])

    if matches:
        return matches
    else:
        return "Street name not found"
    
result = find_street_name('State Street')
print(result)

result = find_street_name('800 South')
print(result)