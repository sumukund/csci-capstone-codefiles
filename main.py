########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

# import pyzed.sl as sl
# import cv2
# import numpy as np
import mapping
import matplotlib.pyplot as plt
import math

def plot_points(map_points, positions):
    xs = [f['geometry']['coordinates'][0] for f in map_points['features']]
    ys = [f['geometry']['coordinates'][1] for f in map_points['features']]

    px = [p[0] for p in positions]
    py = [p[1] for p in positions]

    plt.scatter(xs, ys, label="Map Points")
    plt.scatter(px, py, label="People", marker='x')

    plt.legend()
    plt.title("Debug View")
    plt.show()
def intersection(map_points, positions, radius=0.5):
    triggered = []

    for pos in positions:
        px, py, pz = pos

        for feature in map_points['features']:
            fx, fy, fz = feature['geometry']['coordinates']

            # Euclidean distance
            dist = math.sqrt(
                (px - fx)**2 +
                (py - fy)**2 +
                (pz - fz)**2
            )

            if dist <= radius:
                props = feature.get('properties', {})

                triggered.append({
                    "position": pos,
                    "distance": dist,
                    "image": props.get("image"),
                    "audio": props.get("audio")
                })

    return triggered

def fake_body_positions():
    return [
        [0.5, 0.5, 0],
        [1.0, 1.0, 3],
        [2.0, 2.0, 6],
        [2.798, 2.798, 0.0],
    ]
    
def main():
    map_points = mapping.return_3d_points(use_dummy=False)

    dummy_positions = fake_body_positions()

    print("\nTesting intersections:\n")

    for pos in dummy_positions:
        print(f"Person at: {pos}") 
    triggered = intersection(map_points, dummy_positions)   
    
    print(triggered)
    plot_points(map_points, dummy_positions)
    
# def main():
#     # Create a Camera object
#     zed = sl.Camera()
#     map_points = mapping.return_3d_points()

#     # Create a InitParameters object and set configuration parameters
#     init_params = sl.InitParameters()
#     init_params.camera_resolution = sl.RESOLUTION.HD720  # Use HD720 video mode
#     init_params.depth_mode = sl.DEPTH_MODE.NEURAL
#     init_params.coordinate_units = sl.UNIT.METER
#     init_params.sdk_verbose = 1
#     print(f"init param {init_params.camera_resolution}")
#     # Open the camera
#     err = zed.open(init_params)
#     if err > sl.ERROR_CODE.SUCCESS:
#         print("Camera Open : "+repr(err)+". Exit program.")
#         exit()
#     # Get camera information
#     camera_info = sl.CameraInformation(zed)

#     print(f"ZED camera resolution: {camera_info.camera_configuration.resolution.width} {camera_info.camera_configuration.resolution.height}")
#     body_params = sl.BodyTrackingParameters()
#     # Different model can be chosen, optimizing the runtime or the accuracy
#     body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
#     body_params.enable_tracking = True
#     body_params.enable_segmentation = False
#     # Optimize the person joints position, requires more computations
#     body_params.enable_body_fitting = True

#     if body_params.enable_tracking:
#         positional_tracking_param = sl.PositionalTrackingParameters()
#         # positional_tracking_param.set_as_static = True
#         positional_tracking_param.set_floor_as_origin = True
#         zed.enable_positional_tracking(positional_tracking_param)

#     print("Body tracking: Loading Module...")

#     err = zed.enable_body_tracking(body_params)
#     if err > sl.ERROR_CODE.SUCCESS:
#         print("Enable Body Tracking : "+repr(err)+". Exit program.")
#         zed.close()
#         exit()
#     bodies = sl.Bodies()
#     body_runtime_param = sl.BodyTrackingRuntimeParameters()
#     # For outdoor scene or long range, the confidence should be lowered to avoid missing detections (~20-30)
#     # For indoor scene or closer range, a higher confidence limits the risk of false positives and increase the precision (~50+)
#     body_runtime_param.detection_confidence_threshold = 40
#     i = 0 
#     while i < 100:
#         if zed.grab() <= sl.ERROR_CODE.SUCCESS:
#             err = zed.retrieve_bodies(bodies, body_runtime_param)
#             if bodies.is_new:
#                 body_array = bodies.body_list
#                 print(str(len(body_array)) + " Person(s) detected\n")
#                 if len(body_array) > 0:
#                     first_body = body_array[0]
#                     print("First Person attributes:")
#                     print(" Confidence (" + str(int(first_body.confidence)) + "/100)")
#                     if body_params.enable_tracking:
#                         print(" Tracking ID: " + str(int(first_body.id)) + " tracking state: " + repr(
#                             first_body.tracking_state) + " / " + repr(first_body.action_state))
#                     position = first_body.position
#                     velocity = first_body.velocity
#                     dimensions = first_body.dimensions
#                     print(" 3D position: [{0},{1},{2}]\n Velocity: [{3},{4},{5}]\n 3D dimentions: [{6},{7},{8}]".format(
#                         position[0], position[1], position[2], velocity[0], velocity[1], velocity[2], dimensions[0],
#                         dimensions[1], dimensions[2]))
#                     if first_body.mask.is_init():
#                         print(" 2D mask available")

#                     print(" Keypoint 2D ")
#                     keypoint_2d = first_body.keypoint_2d
#                     for it in keypoint_2d:
#                         print("    " + str(it))
#                     print("\n Keypoint 3D ")
#                     keypoint = first_body.keypoint
#                     for it in keypoint:
#                         print("    " + str(it))
#         i+=1
#     # Close the camera
#     zed.disable_body_tracking()
#     zed.close()


if __name__ == "__main__":
    main()