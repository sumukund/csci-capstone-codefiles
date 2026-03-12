import json
import geojson
from shapely.geometry import Point, Polygon


RESOLUTION_WIDTH = 1080 
RESOLUTION_HEIGHT = 720 
MARGIN = 10
def get_bbox(parsed_geojson):
    xs, ys = [], []
    for feature in parsed_geojson['features']:
        geom = feature['geometry']
        if geom['type'] == 'Point':
            x, y = geom['coordinates']
            xs.append(x)
            ys.append(y)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return min_x, max_x, min_y, max_y

def map_to_3d(x, y, bbox, scale=1.0, z_value=0.0):
    """
    x, y         : original GeoJSON coordinates
    bbox         : bounding box (min_x, max_x, min_y, max_y)
    scale        : meters per unit in the GeoJSON
    z_value      : height in meters (default 0 for ground)
    """
    min_x, max_x, min_y, max_y = bbox

    x_trans = (x - min_x) * scale
    y_trans = (y - min_y) * scale

    z_trans = z_value
    print(x_trans, y_trans, z_trans)
    return x_trans, y_trans, z_trans

def load(geojson_file):
        # Using geojson library
    with open(geojson_file, 'r') as file:
        parsed_geojson = geojson.load(file)
    
    return parsed_geojson

def create_map(parsed_geojson):
    return unscaled_map

def scale_map_to_3d(parsed_geojson, scale=1.0, default_z=0.0):
    bbox = get_bbox(parsed_geojson)
    scaled_features = []

    for feature in parsed_geojson['features']:
        geom = feature['geometry']
        if geom['type'] == 'Point':
            x, y = geom['coordinates']
            x3d, y3d, z3d = map_to_3d(x, y, bbox, scale, default_z)
            scaled_features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [x3d, y3d, z3d]
                },
                'properties': feature.get('properties', {})
            })

    return {
        'type': 'FeatureCollection',
        'features': scaled_features
    }



def return_3d_points():
    parsed_geojson = load("map.geojson")
    
    SCALE = 0.1
    
    scaled_map_3d = scale_map_to_3d(parsed_geojson, scale=SCALE, default_z=0.0)

    for feature in scaled_map_3d['features']:
        print("3D point:", feature['geometry']['coordinates'])

    return scaled_map_3d
