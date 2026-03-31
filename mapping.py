import json
import math
import matplotlib.pyplot as plt

# ------------------- CONFIG -------------------
CAMERA_X_RANGE = (-2, 3)
CAMERA_Z_RANGE = (2, 7)
ROOM_WIDTH_FEET = 20
ROOM_DEPTH_FEET = 25
FEET_TO_METERS = 0.3048

# ------------------- UTILITIES -------------------
def feet_to_meters(width_feet, depth_feet):
    return width_feet * FEET_TO_METERS, depth_feet * FEET_TO_METERS

def get_bbox(parsed_geojson):
    xs, zs = [], []
    for feature in parsed_geojson['features']:
        geom = feature['geometry']
        if geom['type'] == 'Point':
            x, z = geom['coordinates']
            xs.append(x)
            zs.append(z)
    return min(xs), max(xs), min(zs), max(zs)

def create_dummy_geojson():
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0,0]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [10,0]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [10,10]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [0,10]}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [5,5]}}
        ]
    }

# ------------------- CAMERA SPACE SCALING -------------------
def scale_to_camera_space(parsed_geojson, x_range=CAMERA_X_RANGE, z_range=CAMERA_Z_RANGE):
    min_x, max_x, min_z, max_z = get_bbox(parsed_geojson)
    scale_x = (x_range[1] - x_range[0]) / (max_x - min_x)
    scale_z = (z_range[1] - z_range[0]) / (max_z - min_z)

    scaled_features = []
    for feature in parsed_geojson['features']:
        x, z = feature['geometry']['coordinates']
        x_new = (x - min_x) * scale_x + x_range[0]
        z_new = (z - min_z) * scale_z + z_range[0]
        scaled_features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [x_new, z_new]},
            'properties': feature['properties']
        })
    return {"type": "FeatureCollection", "features": scaled_features}

def return_camera_space_points(use_dummy=False):
    if use_dummy:
        parsed_geojson = create_dummy_geojson()
    else:
        with open("map.geojson", 'r') as file:
            parsed_geojson = json.load(file)
    camera_space_map = scale_to_camera_space(parsed_geojson)
    return camera_space_map

# ------------------- PLOTTING -------------------
def plot_triggered_points(triggered_file="triggered.json"):
    map_points = return_camera_space_points()
    
    with open(triggered_file, "r") as f:
        data = json.load(f)
    
    # Map points
    xs = [f['geometry']['coordinates'][0] for f in map_points['features']]
    zs = [f['geometry']['coordinates'][1] for f in map_points['features']]
    
    # Triggered points
    px = [entry["position"][0] for entry in data]
    pz = [entry["position"][2] for entry in data]
    colors = ["red" if entry.get("triggered", False) else "blue" for entry in data]
    
    plt.scatter(xs, zs, label="Map Points")
    plt.scatter(px, pz, c=colors, marker='x', label="People (red=triggered)")
    plt.legend()
    plt.title("Debug View (Camera Space)")
    plt.show()

# ------------------- INTERSECTION -------------------
def intersection(map_points, positions, radius=0.6):
    triggered = []
    px, _, pz = positions   # ignore Y
    
    for feature in map_points['features']:
        fx, fz = feature['geometry']['coordinates']
        dist = math.sqrt((px - fx)**2 + (pz - fz)**2)
        if dist <= radius:
            props = feature.get('properties', {})
            triggered.append({
                "position": [px, pz],
                "distance": dist,
                "image": props.get("image"),
                "audio": props.get("audio"),
                "triggered": True
            })
    return triggered
