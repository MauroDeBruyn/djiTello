#import dji library
from djitellopy import Tello

#we also need to import time.
import time

tello = Tello() # Tello object!
tello.connect() # MUST BE connected to the drone via laptop wifi

# Tello basic example commands
tello.takeoff()
tello.move_up(100)
tello.move_down(100)
tello.move_forward(100)
tello.move_back(100)
tello.move_left(100)
tello.move_right(100)
tello.rotate_counter_clockwise(360)
tello.rotate_clockwise(360)
tello.land()

tello.end()