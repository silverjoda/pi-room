import logging
import time
import datetime

import numpy as np
from picamera import PiCamera

camera_resolution = (1024, 768)
N_DAYS = 14
NOW = datetime.datetime.now()
CAPTURE_BEGIN_TIME = datetime.datetime(2009, 12, 2, 9, 30)
CAPTURE_END_TIME = datetime.datetime(2009, 12, 2, 9, 30)


def analyze():
    logging.info("Analyzing image sequence. ")

def take_picture(camera):
    output = np.empty((camera_resolution[1], camera_resolution[0], 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    output_float = (output.astype(np.float32) / 255.)
    logging.debug("Took image at {}. Min: {}, Max: {}. ".format(time.time(), output_float.min(), output_float.max()))
    return output_float

def capture_every_n_until(camera, until, sleep_interval):
    pics = []
    while datetime.datetime.now() < until:
        pics.append(take_picture(camera))
        time.sleep(sleep_interval)
    logging.info("Collected {} images. ".format(len(pics)))
    return np.array(pics)

def setup_camera():
    logging.info("Setting up camera. ")
    camera = PiCamera()
    camera.resolution = camera_resolution
    return camera

def start_schedule():
    logging.info("Starting schedule. ")

    for d in range(N_DAYS):
        logging.info("Day: {}. ".format(d+1))

        # Start capturing
        pass

if __name__ == '__main__':
    logging.info("Starting sleep analysis script, N_DAYS = {}. ".format(N_DAYS))
    setup_camera()
    start_schedule()



