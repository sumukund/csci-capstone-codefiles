import json
import math
import matplotlib.pyplot as plt
import time
import cv2
import numpy as np
from collections import deque

# ------------------- CONFIG -------------------
CAMERA_X_RANGE = (-2, 3)
CAMERA_Z_RANGE = (2, 10)
ROOM_WIDTH_FEET = 20
ROOM_DEPTH_FEET = 25
FEET_TO_METERS = 0.3048
last_head_y = None
last_head_time = 0
HEAD_TIMEOUT = 0.5  # seconds
CAMERA_Y_RANGE = (-0.5, 4)  # adjust to your setup
HEAD_MIN = -0.3
HEAD_MAX = 0.7
# ------------------- UTILITIES -------------------

class RollingAverageFilter:
    def __init__(self, size=60):
        self.size = size
        self.buffer = deque(maxlen=size)

    def add(self, value):
        if value is None:
            return

        # Convert numpy arrays → list
        if hasattr(value, "tolist"):
            value = value.tolist()

        # Validate numbers
        if isinstance(value, (list, tuple)):
            if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in value):
                return
        else:
            if isinstance(value, float) and math.isnan(value):
                return

        self.buffer.append(value)

    def get_average(self):
        if not self.buffer:
            return None

        first = self.buffer[0]

        # Scalar case
        if isinstance(first, (int, float)):
            return sum(self.buffer) / len(self.buffer)

        # Vector case
        arr = np.array(self.buffer, dtype=np.float32)
        return np.mean(arr, axis=0).tolist()
    
#


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

# camera space scaling for 0 to 1 
def camera_to_unit_space(camera_geojson, x_range=CAMERA_X_RANGE, z_range=CAMERA_Z_RANGE):
    x_min, x_max = x_range
    z_min, z_max = z_range

    range_x = x_max - x_min
    range_z = z_max - z_min

    normalized_features = []
    for feature in camera_geojson['features']:
        x, z = feature['geometry']['coordinates']

        x_norm = (x - x_min) / range_x
        z_norm = (z - z_min) / range_z

        normalized_features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [x_norm, z_norm]},
            'properties': feature.get('properties', {})
        })

    return {"type": "FeatureCollection", "features": normalized_features}

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
    unit_space_map = camera_to_unit_space(camera_space_map)
    return unit_space_map

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

def intersection(map_points, positions, radius=0.2):
    triggered = []

    px, _, pz = positions  # ignore Y

    # normalize position into 0–1 space
    x_min, x_max = CAMERA_X_RANGE
    z_min, z_max = CAMERA_Z_RANGE

    px = (px - x_min) / (x_max - x_min)
    pz = (pz - z_min) / (z_max - z_min)

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
                "emotional_layer": props.get("emotional_layer"),
                "id": feature.get("id"),
                "triggered": True
            })

    return triggered





def get_filtered_vel(velocity, velocity_filter):
    velocity_filter.add(velocity)
    smooth_velocity = velocity_filter.get_average()
    return math.sqrt(smooth_velocity[0]*smooth_velocity[0] + smooth_velocity[1]*smooth_velocity[1] + smooth_velocity[2]*smooth_velocity[2])

def head_position_scaling(head_pos, head_filter):
    if head_pos is None or math.isnan(head_pos):
        last = head_filter.get_average()
        return last if last is not None else 0.0


    head_filter.add(head_pos)
    smooth_head_y = head_filter.get_average()

    if smooth_head_y is None:
        return 0.0



    hy = (smooth_head_y - HEAD_MIN) / (HEAD_MAX - HEAD_MIN)
    hy = max(0.0, min(1.0, hy))

    return hy

def body_position_scaling(position, body_filter):
    body_filter.add(position)
    smooth_body = body_filter.get_average()
    px, _, pz = smooth_body  # ignore Y

    # normalize position into 0–1 space
    x_min, x_max = CAMERA_X_RANGE
    z_min, z_max = CAMERA_Z_RANGE

    px = (px - x_min) / (x_max - x_min)
    pz = (pz - z_min) / (z_max - z_min)
    px = max(0.0, min(1.0, px))
    pz = max(0.0, min(1.0, pz))

    return [px, pz]

def is_valid_point(p):
    if p is None:
        return False
    try:
        return all(not math.isnan(v) for v in p)
    except (TypeError, ValueError):
        return False


def hand_position_scaling_distance_calc(right_hand, left_hand, hand_dist_filter):
    if not (is_valid_point(right_hand) and is_valid_point(left_hand)):
        last = hand_dist_filter.get_average()
        return last if last is not None else 0.0

    hand_dist_filter.add([right_hand, left_hand])
    # normalized
    dist_avg = hand_dist_filter.get_average()
    rhx, rhy, rhz = dist_avg[0]
    lhx, lhy, lhz = dist_avg[1]

    dist = math.sqrt(
        (rhx - lhx) ** 2 +
        (rhy - lhy) ** 2 +
        (rhz - lhz) ** 2
    )
    print("dist", dist)
    smooth_dist = max(0.0, min(1.0, dist))
    return smooth_dist

def load_image(name):
    path = f"avg_images/{name}"
    img = cv2.imread(path)

    return img

def apply_brightness(image, brightness):
    img = image.astype("float32") * brightness
    return np.clip(img, 0, 255).astype("uint8")