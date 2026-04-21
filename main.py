

import pyzed.sl as sl
import cv2
import mapping
import keyboard 
import triggered_audio
import json
import os
import integrate_OSC 

def main():
    # Create a Camera object
    zed = sl.Camera()
    filename = "triggered.json"

    # create an OSC client 

    client = integrate_OSC.initialize()

    #buffers 

    velocity_filter = mapping.RollingAverageFilter(60)
    head_filter = mapping.RollingAverageFilter(60)
    body_filter = mapping.RollingAverageFilter(60)
    hand_dist_filter = mapping.RollingAverageFilter(60)
    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720  # Use HD720 video mode
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.METER
    init_params.camera_fps = 60
    init_params.sdk_verbose = 1
    HEAD_INDEX = 0  

    RIGHT_HAND_INDEX = 4
    LEFT_HAND_INDEX = 7

    print(f"init param {init_params.camera_resolution}")
    # Open the camera
    err = zed.open(init_params)
    if err > sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(err)+". Exit program.")
        exit()
    # Get camera information
    camera_info = sl.CameraInformation(zed)

    # load in images for cache 
    image_cache = {}
      
    body_params = sl.BodyTrackingParameters()
    detection_parameters = sl.BodyTrackingParameters()
    detection_parameters.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE  
    detection_parameters.enable_tracking = True
    detection_parameters.enable_body_fitting = True
    detection_parameters.body_format = sl.BODY_FORMAT.BODY_34

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
            
            # initialization
            
            print("Pose", zed.get_position(pose, sl.REFERENCE_FRAME.WORLD))
            origin = pose.get_translation().get()  # [x, y, z]
            print("Map origin:", origin)
            if pose != "SEARCHING FLOOR PLANE":    
                # Draw map points
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
                        # HEAD index (works for BODY_18 and BODY_34)
                        keypoints = first_body.keypoint
                        head_pos = keypoints[HEAD_INDEX]
                        right_hand_pos = keypoints[RIGHT_HAND_INDEX]
                        left_hand_pos = keypoints[LEFT_HAND_INDEX]

                        print(" 3D position: [{0},{1},{2}]\n Velocity: [{3},{4},{5}]\n 3D dimentions: [{6},{7},{8}]".format(
                            position[0], position[1], position[2], velocity[0], velocity[1], velocity[2], dimensions[0],
                            dimensions[1], dimensions[2]))
                        triggered = mapping.intersection(map_scaled, position)

                        smoothed_velocity = mapping.get_filtered_vel(velocity, velocity_filter)
                        scaled_position = mapping.body_position_scaling(position.tolist(), body_filter)
                        scaled_head_pos = mapping.head_position_scaling(head_pos[1], head_filter)
                        hand_distance = mapping.hand_position_scaling_distance_calc(right_hand_pos, left_hand_pos, hand_dist_filter)
                        
                        new_entry = {
                            "triggered": triggered,
                            "position_camera_space": position.tolist(),
                            "position_unit_space": scaled_position,
                            "dimensions": dimensions.tolist(),
                            "head_position": scaled_head_pos,
                            "hand_distance": hand_distance, 
                            "acceleration": smoothed_velocity                    
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

                        # # if triggered, send data to picture to show on projector
                        # if len(triggered) > 0:
                        #     avg_img = mapping.load_image(triggered[0].get("image"))


                        #     cv2.imshow("Illuminated Average", avg_img)

                        # brightness = mapping.apply_brightness(image, scaled_position)
                        
                        integrate_OSC.send_data_to_server(client, new_entry)

                        with open(filename, "w") as file:
                            json.dump(data, file, indent=4)

    # Close the camera
    zed.disable_body_tracking()
    zed.close()

if __name__ == "__main__":
    main()