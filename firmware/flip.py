from djitellopy import Tello
import time

#Connect to Tello
tello = Tello()
is_flying = False

try:
    tello.connect()

    battery = tello.get_battery()
    print("Battery:", battery, "%")

    #Check battery status
    if battery < 20:
        print("Battery too low for a flip.")
        raise SystemExit

    #Move up to safe height (a flip cose to the ground will result in a crash!!!)
    tello.takeoff()
    tello.move_up(100)
    is_flying = True

    time.sleep(2)

    #Flip commands
    print("Performing flips...")
    tello.flip_forward()
    time.sleep(2)
    tello.flip_back()
    time.sleep(2)
    tello.flip_left()
    time.sleep(2)
    tello.flip_right()
    time.sleep(2)

    tello.land()
    is_flying = False

finally:
    if is_flying:
        try:
            tello.land()
        except Exception:
            pass

    tello.end()
    print("Tello stopped")