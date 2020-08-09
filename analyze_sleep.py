
import datetime
import logging
import sys
import time
import numpy as np
from picamera import PiCamera
import matplotlib.pyplot as plt
import subprocess

camera_resolution = (1024, 768)
N_DAYS = 14
CAPTURE_BEGIN_HOUR = 0
CAPTURE_END_HOUR = 7
CAPTURE_SLEEP_INTERVAL_SECS = 60

logging.basicConfig(filename='logs/log_{}.log'.format(time.strftime("%Y%m%d-%H%M%S")),
                    level=logging.INFO)

def analyze(pic_array, d):
    N = len(pic_array)
    logging.info("Analyzing image sequence of len={}. ".format(N))

    deltas = []
    for i in range(N - 1):
        delta = np.mean(np.square(pic_array[i + 1] - pic_array[i]))
        deltas.append(delta)

    t = np.linspace(CAPTURE_BEGIN_HOUR, CAPTURE_END_HOUR, N - 1)
    fig, ax = plt.subplots()
    ax.plot(t, deltas)
    plt.xlabel('Hours')
    plt.ylabel('Neighboring delta')
    plt.margins(x=0)

    # Save plot to image format
    plt.savefig("analysis/images_Day-{}.png".format(d))

def take_picture(camera):
    output = np.empty((camera_resolution[1], camera_resolution[0], 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    output_float = (output.astype(np.float32) / 255.)
    logging.debug("Took image at {}. Min: {}, Max: {}. ".format(time.time(), output_float.min(), output_float.max()))
    return output_float

def capture_every_n_sec_until(camera):
    logging.info("Starting capturing with interval {}s until {}'th hour".format(CAPTURE_SLEEP_INTERVAL_SECS, CAPTURE_END_HOUR))
    pics = []
    while datetime.datetime.now().hour < CAPTURE_END_HOUR:
        pics.append(take_picture(camera))
        time.sleep(CAPTURE_SLEEP_INTERVAL_SECS)
    logging.info("Collected {} images. ".format(len(pics)))
    return np.array(pics)

def start_audio_recording(d):
    logging.info("Starting audio capture in separate thread using 'arecord'. ")
    # arecord --device=hw:1,0 --format S16_LE --rate 44100 -V mono -c1 voice.wav
    p = subprocess.Popen(["arecord --device=hw:1,0 --format S16_LE --rate 44100 -c1 audio/Day-{}.wav".format(d)])
    return p

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

        # Launch audio recording in separate thread
        start_audio_recording(d)

        # Start capturing until end hour
        images = capture_every_n_sec_until(camera)

        save_images(images, d)
        analyze(images, d)

def test():
    logging.info("Testing. ")
    images = np.random.rand(300, 256, 256)
    analyze(images, 0)
    exit()

if __name__ == '__main__':
    logging.info("Starting sleep analysis script, N_DAYS = {}. ".format(N_DAYS))
    camera = setup_camera()
    start_schedule(camera)



