import pyzed.sl as sl
import cv2

def main():
    # Create camera
    zed = sl.Camera()

    # Init parameters
    init_params = sl.InitParameters()
    init_params.sdk_verbose = 0

    # Open camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Failed to open ZED:", err)
        return

    print("Camera opened")

    # Create image container
    image = sl.Mat()

    while True:
        # Grab frame
        if zed.grab() == sl.ERROR_CODE.SUCCESS:

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

    # Cleanup
    zed.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()