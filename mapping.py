import json
import math
import matplotlib.pyplot as plt
import cv2

# ------------------- CONFIG -------------------
RESOLUTION_WIDTH = 1080
RESOLUTION_HEIGHT = 720
ROOM_WIDTH_FEET = 12
ROOM_DEPTH_FEET = 12
FEET_TO_METERS = 0.3048

DEFAULT_Z = 0.06 # Default height for map points
# ---------------------------------------------

# ------------------- UTILITIES -------------------
def feet_to_meters(width_feet, depth_feet):
    return width_feet * FEET_TO_METERS, depth_feet * FEET_TO_METERS

def get_bbox(parsed_geojson):
    xs, ys = [], []
    for feature in parsed_geojson['features']:
        geom = feature['geometry']
        if geom['type'] == 'Point':
            x, y = geom['coordinates']
            xs.append(x)
            ys.append(y)
    return min(xs), max(xs), min(ys), max(ys)

def compute_scale_to_room(bbox, room_width_m, room_depth_m, margin=0.5):
    min_x, max_x, min_y, max_y = bbox
    data_width = max_x - min_x
    data_height = max_y - min_y
    usable_width = room_width_m - margin
    usable_depth = room_depth_m - margin
    scale_x = usable_width / data_width
    scale_y = usable_depth / data_height
    return min(scale_x, scale_y)

def map_to_3d(x, y, bbox, scale, map_origin, z_value=DEFAULT_Z):
    min_x, max_x, min_y, max_y = bbox
    # Map coordinates relative to origin
    x_rel = x - min_x
    y_rel = y - min_y
    # Scale and offset by map origin
    x3d = x_rel * scale + map_origin[0]
    y3d = y_rel * scale + map_origin[1]
    z3d = z_value + map_origin[2]
    return x3d, y3d, z3d

def create_dummy_geojson():
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [10, 0]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [10, 10]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 10]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [5, 5]}}
        ]
    }

# ------------------- MAP SCALING -------------------
def scale_map_to_3d(map_origin, parsed_geojson, room_width_feet=ROOM_WIDTH_FEET, room_depth_feet=ROOM_DEPTH_FEET, default_z=DEFAULT_Z):
    bbox = get_bbox(parsed_geojson)
    room_width_m, room_depth_m = feet_to_meters(room_width_feet, room_depth_feet)
    scale = compute_scale_to_room(bbox, room_width_m, room_depth_m)

    scaled_features = []
    for feature in parsed_geojson['features']:
        if feature['geometry']['type'] == 'Point':
            x, y = feature['geometry']['coordinates']
            x3d, y3d, z3d = map_to_3d(x, y, bbox, scale, map_origin, default_z)
            scaled_features.append({
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [x3d, y3d, z3d]}
            })

    return {"type": "FeatureCollection", "features": scaled_features}

def extract_points_array(scaled_map_3d):
    return [f['geometry']['coordinates'] for f in scaled_map_3d['features']]

def return_3d_points(map_origin, use_dummy=False):
    if use_dummy:
        parsed_geojson = create_dummy_geojson()
    else:
        with open("map.geojson", 'r') as file:
            parsed_geojson = json.load(file)
    scaled_map_3d = scale_map_to_3d(map_origin, parsed_geojson)
    return scaled_map_3d, extract_points_array(scaled_map_3d)

# ------------------- PLOTTING -------------------
# def plot_triggered_points(triggered_file="triggered.json"):
def plot_triggered_points(triggered_json):

    map_origin = [ 0.03365466, -0.59217155,  0.06798545]

    map_points, _ = return_3d_points(map_origin)
    # with open(triggered_file, "r") as f:
    data = triggered_json
    
    # Map points
    xs = [f['geometry']['coordinates'][0] for f in map_points['features']]
    ys = [f['geometry']['coordinates'][1] for f in map_points['features']]
    
    # Triggered points
    px = [entry["position"][0] for entry in data]
    py = [entry["position"][1] for entry in data]
    colors = ["red" if entry.get("triggered", False) else "blue" for entry in data]
    
    plt.scatter(xs, ys, label="Map Points")
    plt.scatter(px, py, c=colors, marker='x', label="People (red=triggered)")
    plt.legend()
    plt.title("Debug View")
    plt.show()

# ------------------- INTERSECTION -------------------
def intersection(map_points, positions, radius=0.6):
    triggered = []
    px, _, pz = positions   # ignore Y

    for feature in map_points['features']:
        fx, _, fz = feature['geometry']['coordinates']  # ignore Y

        dist = math.sqrt((px - fx)**2 + (pz - fz)**2)

        if dist <= radius:
            props = feature.get('properties', {})
            triggered.append({
                "position": [px, pz],  # optional: cleaner
                "distance": dist,
                "image": props.get("image"),
                "audio": props.get("audio"),
                "triggered": True
            })
    return triggered
