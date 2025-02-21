import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point, LineString
import pooch
import folium 


class RoadNetwork:
    def __init__(self, county_id: str = '49035', year: str = '2020'):
        self.county_id = county_id # https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tiger2006se/app_a03.pdf
        self.year = year
        self.graph = nx.Graph()
        self.roads_gdf = self._load_shapfile()

    def _load_shapefile(self):
        url = f"https://ww2.census.gov/geo/tiger/TIGER{self.year}/ROAD/tl_{self.year}_{self.county_id}_roads.zip"
        shapefile = pooch.retrieve (url, None)
        return gpd.read_file("zip//" + shapefile)
    
    def _calculate_distance(self, coord1, coord2):
        return LineString([coord1, coord2]).length
    
    def build_graph(self):
        for idx, row in self.roads_gdf.iterrows():
            geom = row['geometry']
            road_name = row['FULLNAME']
            road_type = row['RTTYP']

            if geom.geom_type == 'LineString':
                self._add_line_to_graph(geom, road_name, road_type)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms:
                    self._add_line_to_graph(geom, road_name, road_type)
    def _add_line_to_graph(self, line, road_name, road_type):


