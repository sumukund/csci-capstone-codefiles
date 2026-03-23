import json
import geojson
import os


RESOLUTION_WIDTH = 1080 
RESOLUTION_HEIGHT = 720 
MARGIN = 10
ROOM_WIDTH = 20
ROOM_DEPTH = 20
FEET_TO_METERS = 0.3048


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

def map_to_3d(x, y, bbox, scale, z_value=0.0):
    min_x, max_x, min_y, max_y = bbox

    # Normalize
    x_norm = x - min_x
    y_norm = y - min_y

    # Apply scale
    x_scaled = x_norm * scale
    y_scaled = y_norm * scale

    return x_scaled, y_scaled, z_value

def create_dummy_geojson():
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [10, 0]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [10, 10]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 10]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [5, 5]}},
        ]
    }
    
def return_3d_points(use_dummy=False):
    if use_dummy:
        parsed_geojson = create_dummy_geojson()
    else:
        with open("map.geojson", 'r') as file:
            parsed_geojson = json.load(file)

    scaled_map_3d = scale_map_to_3d(parsed_geojson, default_z=0.0)

    for feature in scaled_map_3d['features']:
        print("3D point:", feature['geometry']['coordinates'])

    return scaled_map_3d

def convert_room_to_scale(ROOM_DEPTH, ROOM_WIDTH):
    room_width_m = ROOM_WIDTH * FEET_TO_METERS 
    room_depth_m = ROOM_DEPTH * FEET_TO_METERS
    
    return room_width_m, room_depth_m
    

def compute_scale_to_room(bbox, room_width_m, room_depth_m, margin=0.5):
    min_x, max_x, min_y, max_y = bbox
    
    data_width = max_x - min_x
    data_height = max_y - min_y

    usable_width = room_width_m - margin
    usable_depth = room_depth_m - margin

    scale_x = usable_width / data_width
    scale_y = usable_depth / data_height

    return min(scale_x, scale_y)

def scale_map_to_3d(parsed_geojson, default_z=0.0):
    bbox = get_bbox(parsed_geojson)

    room_width_m, room_depth_m = convert_room_to_scale(ROOM_DEPTH, ROOM_WIDTH)

    scale = compute_scale_to_room(bbox, room_width_m, room_depth_m)

    scaled_features = []

    for feature in parsed_geojson['features']:
        if feature['geometry']['type'] == 'Point':
            x, y = feature['geometry']['coordinates']

            x3d, y3d, z3d = map_to_3d(x, y, bbox, scale, default_z)

            scaled_features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [x3d, y3d, z3d]
                }
            })

    return {
        'type': 'FeatureCollection',
        'features': scaled_features
    }