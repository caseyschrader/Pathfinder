import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point, LineString
import pooch
import folium
from thefuzz import fuzz, process


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

def find_street_name(search_term):
    search_words = search_term.split()
    main_part = search_words[0]
    
    matches = []
    for street in street_names:
        if street:
            street_words = street.split()
            street_main = street_words[0]

            main_score = fuzz.partial_ratio(main_part.lower(), street_main.lower())
            if main_score >= 95:
                full_score = fuzz.ratio(search_term.lower(), street.lower())
                if full_score >= 70:
                    matches.append((street, main_score, full_score))
    
    matches.sort(key=lambda x: (x[1] + x[2])/2, reverse=True)
    if matches:
        return matches[0][0]
    else:
        return None

tests = ['State Street', '800 South', 'Main Street']
for test in tests:
    print(f"\nsearching for: {test}")
    results = find_street_name(test)
    print(f"results: {results}")