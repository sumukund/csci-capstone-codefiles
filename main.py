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

import pyzed.sl as sl
import cv2
import numpy as np
import mapping
import matplotlib.pyplot as plt
import math
import keyboard 
import triggered_audio
import json
import os
    
def main():
    # Create a Camera object
    zed = sl.Camera()
    filename = "triggered.json"

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720  # Use HD720 video mode
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.METER
    init_params.sdk_verbose = 1
    print(f"init param {init_params.camera_resolution}")
    # Open the camera
    err = zed.open(init_params)
    if err > sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(err)+". Exit program.")
        exit()
    # Get camera information
    camera_info = sl.CameraInformation(zed)

    print(f"ZED camera resolution: {camera_info.camera_configuration.resolution.width} {camera_info.camera_configuration.resolution.height}")
    body_params = sl.BodyTrackingParameters()
    # Different model can be chosen, optimizing the runtime or the accuracy
    body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
    body_params.enable_tracking = True
    body_params.enable_segmentation = False
    # Optimize the person joints position, requires more computations
    body_params.enable_body_fitting = True

    if body_params.enable_tracking:
        positional_tracking_param = sl.PositionalTrackingParameters()
        # positional_tracking_param.set_as_static = True
        positional_tracking_param.set_floor_as_origin = True
        zed.enable_positional_tracking(positional_tracking_param)

    print("Body tracking: Loading Module...")

    err = zed.enable_body_tracking(body_params)
    if err > sl.ERROR_CODE.SUCCESS:
        print("Enable Body Tracking : "+repr(err)+". Exit program.")
        zed.close()
        exit()
    bodies = sl.Bodies()
    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    # For outdoor scene or long range, the confidence should be lowered to avoid missing detections (~20-30)
    # For indoor scene or closer range, a higher confidence limits the risk of false positives and increase the precision (~50+)
    body_runtime_param.detection_confidence_threshold = 60
    image = sl.Mat()
    pose = sl.Pose()
    depth_map = sl.Mat()
    runtime_parameters = sl.RuntimeParameters()
   
    while True:
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            print('You Pressed A Key!')
            break  # finishing the loop
        if zed.grab() <= sl.ERROR_CODE.SUCCESS:
            err = zed.retrieve_bodies(bodies, body_runtime_param)
                        # Retrieve left image
            zed.retrieve_image(image, sl.VIEW.LEFT)
            # Convert to numpy
            frame = image.get_data()

            # Convert BGRA → BGR (IMPORTANT)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Show image
            cv2.imshow("ZED Camera", frame)

            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # Draw map points
            # Optional: draw lines
            print("Pose", zed.get_position(pose, sl.REFERENCE_FRAME.WORLD))
            origin = pose.get_translation().get()  # [x, y, z]
            print("Map origin:", origin)
            map_scaled = mapping.return_camera_space_points(use_dummy=False)
                      
            if bodies.is_new:
                body_array = bodies.body_list
                print(str(len(body_array)) + " Person(s) detected\n")
                if len(body_array) > 0:
                    first_body = body_array[0]
                    print("First Person attributes:")
                    print(" Confidence (" + str(int(first_body.confidence)) + "/100)")
                    if body_params.enable_tracking:
                        print(" Tracking ID: " + str(int(first_body.id)) + " tracking state: " + repr(
                            first_body.tracking_state) + " / " + repr(first_body.action_state))
                    position = first_body.position
                    velocity = first_body.velocity
                    dimensions = first_body.dimensions
                    print(" 3D position: [{0},{1},{2}]\n Velocity: [{3},{4},{5}]\n 3D dimentions: [{6},{7},{8}]".format(
                        position[0], position[1], position[2], velocity[0], velocity[1], velocity[2], dimensions[0],
                        dimensions[1], dimensions[2]))
                    triggered = mapping.intersection(map_scaled, position)

                    new_entry = {
                        "triggered": triggered,
                        "position": position.tolist(),
                        "velocity" : velocity.tolist(),
                    }

                    # Load existing data if file exists
                    if os.path.exists(filename):
                        with open(filename, "r") as file:
                            data = json.load(file)
                    else:
                        data = []
                    # Append new entry
                    data.append(new_entry)
                    print(f"triggered: {triggered}")
                    # Play audio based on triggered points
                    triggered_audio.play_triggered_audio(new_entry)                    
                    with open(filename, "w") as file:
                        json.dump(data, file, indent=4)

    # Close the camera
    zed.disable_body_tracking()
    zed.close()

if __name__ == "__main__":
    main()