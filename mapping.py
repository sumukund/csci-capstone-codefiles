import json
import geojson
from shapely.geometry import Point, Polygon


RESOLUTION_WIDTH = 1080 
RESOLUTION_HEIGHT = 720 


def load(geojson_file):
        # Using geojson library
    with open(geojson_file, 'r') as file:
        parsed_geojson = geojson.load(file)
    
    return parsed_geojson

def create_map(parsed_geojson):
    return map

def scale_map(map, RESOLUTION_WIDTH, RESOLUTION_HEIGHT)