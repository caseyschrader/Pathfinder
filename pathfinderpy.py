import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point, LineString
import pooch
import folium
from thefuzz import fuzz, process


slc_geojson = pooch.retrieve("https://hub.arcgis.com/api/v3/datasets/7834e3d0c53646569ad897d4aa2d084e_0/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1", None)

slc_roads = gpd.read_file(slc_geojson)

def find_street_name(graph, search_term):
    street_names = set(nx.get_edge_attributes(graph, 'name').values())
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


def find_intersection(graph, street1, street2):
    street1_name = find_street_name(graph, street1)
    street2_name = find_street_name(graph, street2)

    print(f"Matched {street1} to {street1_name}")
    print(f"Matched {street2} to {street2_name}")

    if not street1_name or not street2_name:
        print(f"Could not find one or both streets: {street1}, {street2}")
        return None

    street1_edges = []
    street2_edges = []
    for u, v, data in graph.edges(data=True):
        if data.get('name') == street1_name:
            street1_edges.append((u,v))
        if data.get('name') == street2_name:
            street2_edges.append((u,v))

    street1_nodes = set()
    street2_nodes = set()
    for u, v in street1_edges:
        street1_nodes.add(u)
        street1_nodes.add(v)
    for u, v in street2_edges:
        street2_nodes.add(u)
        street2_nodes.add(v)

    print(f"Found {len(street1_edges)} edges for {street1_name}")
    print(f"Found {len(street2_edges)} edges for {street2_name}")


    intersection = street1_nodes.intersection(street2_nodes)
    return intersection

def mark_intersection(graph, street1, street2, map):
    
    intersection_nodes = find_intersection(graph, street1, street2)

    if not intersection_nodes:
        return None
    
    for node in intersection_nodes:
        folium.Marker(
            location=[node[1], node[0]], # folium takes lat/long
            popup=f"Intersection of {street1} and {street2}",
            icon=folium.Icon(color='red')
        ).add_to(map)
    
    return intersection_nodes


def dijkstra(graph, src, dest):
    distances = {src: 0}
    predecessors = {}
    unvisited = [(0, src)] 
    visited = set()
    
    while unvisited:

        current_distance, current_node = min(unvisited)
        unvisited.remove((current_distance, current_node))
        
        if current_node == dest:
            return {
                'nodes': get_path(dest, predecessors),
                'edges': get_path_edges(get_path(dest, predecessors))
            }
        
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        for neighbor in graph[current_node]:
            if neighbor in visited:
                continue
            edge_weight = graph[current_node][neighbor]['weight']
            distance = current_distance + edge_weight
            
            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                
                unvisited.append((distance, neighbor))
    print("No path found between source and destination")
    return None

def get_path(dest, predecessors):
    path = []
    pred = dest
    while pred is not None:
        path.append(pred)
        pred = predecessors.get(pred, None)
    path.reverse()
    return path

def get_path_edges(path):
    edges = []
    for i in range(len(path) - 1):
        edges.append((path[i], path[i + 1]))
    return edges


def get_min_dist_node(distances, unvisited):
    min_dist = float("inf")
    min_dist_node = None
    for v in unvisited:
        distance_so_far = distances[v]
        if distance_so_far < min_dist:
            min_dist = distance_so_far
            min_dist_node = v
    return min_dist_node

def visualize_path(graph, path_edges, map):
    for u, v in path_edges:
        coords = [u, v]
        folium.PolyLine(
            locations=[(y, x) for x, y in coords],
            color='red',
            weight=4,
            opacity=0.8
        ).add_to(map)

def pathfinder(graph, street1_a, street2_a, street1_b, street2_b, map, output_file='slc_path.html'):
    intersection_a = mark_intersection(graph, street1_a, street2_a, map)
    intersection_b = mark_intersection(graph, street1_b, street2_b, map)

    if not intersection_a or not intersection_b:
        return None
    
    source = list(intersection_a)[0]
    destination = list(intersection_b)[0]

    path_result = dijkstra(graph, source, destination)

    if not path_result:
        return None
    
    visualize_path(graph, path_result['edges'], map)

    map.save(output_file)

    return path_result


def pathfinder_prompt():
    print("\nWelcome to SLC Pathfinder!")
    print("-------------------------")

    source_location = input("Enter your starting location (format: street name, street name):")
    street1_a, street1_b = [street.strip() for street in source_location.split(',')]

    destination_location = input("Enter your destination (format: street name, street name):")
    street2_a, street2_b = [street.strip() for street in destination_location.split(',')]

    print(f"\nPlanning route from {street1_a} & {street1_b} to {street2_a} & {street2_b}...")

    graph = nx.Graph()
    for idx, row in slc_roads.iterrows():
        geom = row['geometry']
        road_name = row['LABEL']
        object_id = row['OBJECTID']

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
                    object_id=object_id
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
                        object_id=object_id
                    )
    bounds = slc_roads.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_long = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_long], zoom_start=11)
    
    output_file = "slc_path.html"
    path = pathfinder(graph, street1_a, street1_b, street2_a, street2_b, m, output_file)

    if path:
        print(f"Path found! Saving map to {output_file}")
    else:
        print(f"Could not find a path between your source location and destination.")

if __name__ == "__main__":
    pathfinder_prompt()


    
