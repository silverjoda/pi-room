import logging
import time

import numpy as np
from picamera import PiCamera

camera_resolution = (1024, 768)

def analyze():
    pass

def take_picture(camera):
    output = np.empty((camera_resolution[1], camera_resolution[0], 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    output_float = (output.astype(np.float32) / 255.)
    return output_float

def capture_every_n_until(camera, until, sleep_interval):
    pics = []
    while time.time() < until:
        pics.append(take_picture(camera))
        time.sleep(sleep_interval)
    logging.info("Collected {} images".format(len(pics)))
    return np.array(pics)

def setup_camera():
    camera = PiCamera()
    camera.resolution = camera_resolution
    return camera

def start_schedule():
    pass

if __name__ == '__main__':
    logging.info("Starting sleep analysis script")

    logging.info("Setting up camera")
    setup_camera()

    logging.info("Starting schedule")
    start_schedule()



