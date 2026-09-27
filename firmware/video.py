from djitellopy import Tello
import cv2
import time

#Connect to Tello
tello = Tello()
is_flying = False

try:
    tello.connect()

    battery = tello.get_battery()
    print("Battery:", battery, "%")

    #Turn on stream
    tello.streamon()
    frame_read = tello.get_frame_read()

    tello.takeoff()
    is_flying = True

    time.sleep(2)

    tello.move_up(150)
    time.sleep(2)


    while True:
        frame = frame_read.frame

        if frame is None:
            continue

        #Read battery level
        battery = tello.get_battery()

        ##Display battery level
        cv2.putText(
            frame,
            f"Battery: {battery}%",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Press Q to land",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.imshow("Tello camera", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    if is_flying:
        tello.land()
        is_flying = False

finally:
    try:
        tello.send_rc_control(0, 0, 0, 0)
    except Exception:
        pass

    try:
        if is_flying:
            tello.land()
    except Exception:
        pass

    try:
        tello.streamoff()
    except Exception:
        pass

    cv2.destroyAllWindows()
    tello.end()

    print("Tello stopped")