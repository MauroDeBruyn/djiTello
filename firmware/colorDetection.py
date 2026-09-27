from djitellopy import Tello
import cv2
import time

#Settings

FORWARD_SPEED = 15
SIDE_SPEED = 25
MIN_LINE_AREA = 300
YAW_SPEED = 10

#Connect to Tello
tello = Tello()

try:
    tello.connect()

    print("Connected to Tello")
    print("Battery:", tello.get_battery(), "%")

    #Start video stream
    tello.streamon()
    frame_read = tello.get_frame_read()

    time.sleep(2)

    #Take off
    tello.takeoff()
    tello.move_down(30) #Move down drone to get a clearer image of the line (camera can not face down)

    while True:
        #Get camera frame
        frame = frame_read.frame

        if frame is None:
            continue

        #Resize image
        frame = cv2.resize(frame, (640, 480))

        height, width, _ = frame.shape

        #Use only the lower part of the image
        roi_start = int(height * 0.55)
        roi = frame[roi_start:height, :]

        #Convert image from BGR to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        lower_line = (105, 150, 80)
        upper_line = (135, 255, 255)

        #Create color mask
        mask = cv2.inRange(
            hsv,
            lower_line,
            upper_line
        )

        #Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        #Default movement
        left_right = 0
        forward = FORWARD_SPEED
        yaw = 0

        if contours:
            #Select the largest detected contour
            line = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(line)

            if area > MIN_LINE_AREA:
                moments = cv2.moments(line)

                if moments["m00"] != 0:
                    #Calculate center of the line
                    center_x = int(
                        moments["m10"] / moments["m00"]
                    )

                    center_y = int(
                        moments["m01"] / moments["m00"]
                    )

                    #Center of the camera image
                    image_center_x = width // 2

                    #Difference between line center and image center
                    error = center_x - image_center_x

                    #Correct the drone's direction
                    if error < -40:
                        yaw = -YAW_SPEED

                    elif error > 40:
                        yaw = YAW_SPEED

                    else:
                        yaw = 0

                    #Draw detected line center
                    cv2.circle(
                        roi,
                        (center_x, center_y),
                        8,
                        (0, 255, 0),
                        -1
                    )

                    #Draw center line of the image
                    cv2.line(
                        roi,
                        (image_center_x, 0),
                        (image_center_x, roi.shape[0]),
                        (255, 0, 0),
                        2
                    )

                    #Display error value
                    cv2.putText(
                        frame,
                        f"Error: {error}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

        else:
            #No line detected: stop horizontal and forward movement
            forward = 0
            yaw = 0

            cv2.putText(
                frame,
                "LINE NOT DETECTED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        #Send movement command to the drone
        tello.send_rc_control(
            0,              #left/right
            forward,        #forward/backward
            0,              #up/down
            yaw             #rotation
        )

        #Show camera and mask
        cv2.imshow("Tello Camera", frame)
        cv2.imshow("Line Mask", mask)

        #Press Q to stop
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    #Land normally when Q is pressed
    tello.land()

finally:
    #Stop all movement
    tello.send_rc_control(0, 0, 0, 0)

    #Stop video and close windows
    tello.streamoff()
    cv2.destroyAllWindows()
    tello.end()

    print("Tello stopped")