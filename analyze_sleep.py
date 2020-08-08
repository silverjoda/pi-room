import logging
import time
import datetime

import numpy as np
from picamera import PiCamera

camera_resolution = (1024, 768)
N_DAYS = 14
CAPTURE_BEGIN_HOUR = 0
CAPTURE_END_HOUR = 7
CAPTURE_SLEEP_INTERVAL_SECS = 60

def analyze(pic_array):
    N = len(pic_array)
    logging.info("Analyzing image sequence of len={}. ".format(N))

    # TODO: Calc average delta between images and plot all deltas, as well as points with high delta which signify movement

def take_picture(camera):
    output = np.empty((camera_resolution[1], camera_resolution[0], 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    output_float = (output.astype(np.float32) / 255.)
    logging.debug("Took image at {}. Min: {}, Max: {}. ".format(time.time(), output_float.min(), output_float.max()))
    return output_float

def capture_every_n_sec_until(camera):
    logging.info("Started capturing with interval {}s until {}'th hour".format(CAPTURE_SLEEP_INTERVAL_SECS, CAPTURE_END_HOUR))
    pics = []
    while datetime.datetime.now().hour < CAPTURE_END_HOUR:
        pics.append(take_picture(camera))
        time.sleep(CAPTURE_SLEEP_INTERVAL_SECS)
    logging.info("Collected {} images. ".format(len(pics)))
    return np.array(pics)

def setup_camera():
    logging.info("Setting up camera. ")
    camera = PiCamera()
    camera.resolution = camera_resolution
    return camera

def save_images(images, d):
    logging.info("Saving images. ")
    save_dir = "raw_images/images_Day-{}.npy".format(d)
    np.save(save_dir, images)

def start_schedule(camera):
    logging.info("Starting schedule. Current time: {}. ".format(datetime.datetime.now()))

    for d in range(N_DAYS):
        logging.info("Day: {}, waiting until {}'th hour to start capture. ".format(d, CAPTURE_BEGIN_HOUR))

        # Wait for the initial capture hour to begin. Sleep in between so as not to waste CPU power
        while datetime.datetime.now().hour < CAPTURE_BEGIN_HOUR: time.sleep(10)

        # Start capturing until end hour
        images = capture_every_n_sec_until(camera)

        save_images(images, d)
        analyze(images)

if __name__ == '__main__':
    logging.info("Starting sleep analysis script, N_DAYS = {}. ".format(N_DAYS))
    camera = setup_camera()
    start_schedule(camera)



