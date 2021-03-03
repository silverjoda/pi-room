import datetime
import logging
import sys
import time
import numpy as np
from picamera import PiCamera
import matplotlib.pyplot as plt
import subprocess
import os
from PIL import Image
from threading import Thread

camera_resolution = (640, 480)
N_DAYS = 1
CAPTURE_BEGIN_HOUR = 0  # 0
CAPTURE_END_HOUR = 7  # 7
CAPTURE_SLEEP_INTERVAL_SECS = 60

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
    pic = take_picture(cam)
    im = Image.fromarray((pic * 255).astype(np.uint8))
    im = im.resize((320, 240))
    logging.debug("Took image at {}. Min: {}, Max: {}. ".format(time.time(), im.min(), im.max()))
    return im

def capture_every_n_sec_until(camera):
    logging.info("Starting camera capturing with interval {}s until {}'th hour".format(CAPTURE_SLEEP_INTERVAL_SECS,
                                                                                       CAPTURE_END_HOUR))
    pics = []
    pic_ctr = 0
    while datetime.datetime.now().hour < CAPTURE_END_HOUR:
        im = take_picture(camera)
        pics.append(im)
        im.save()
        time.sleep(CAPTURE_SLEEP_INTERVAL_SECS)
    logging.info("Collected {} images. ".format(len(pics)))
    return np.array(pics)

def start_audio_recording(d):
    logging.info("Starting audio capture in separate thread using 'arecord'. ")
    for i in range(CAPTURE_END_HOUR - CAPTURE_BEGIN_HOUR):
        duration = 3600
        p = subprocess.Popen(f"arecord -D plughw:1,0 --duration={duration} --format S16_LE --rate 8000 -V mono -c1 audio/Day-{d}-hour-{i + CAPTURE_BEGIN_HOUR}.wav", shell=True)
    return p

def setup_camera():
    logging.info("Setting up camera. ")
    camera = PiCamera()
    camera.resolution = camera_resolution
    return camera

def save_images(images, d):
    logging.info("Saving images. ")
    save_dir = "npz_images/images_Day-{}.npy".format(d)
    np.savez(save_dir, images)

def start_schedule(camera):
    logging.info("Starting schedule. Current time: {}. ".format(datetime.datetime.now()))

    for d in range(N_DAYS):
        logging.info("Day: {}, waiting until {}'th hour to start capture. ".format(d, CAPTURE_BEGIN_HOUR))

        # Wait for the initial capture hour to begin. Sleep in between so as not to waste CPU power
        while datetime.datetime.now().hour < CAPTURE_BEGIN_HOUR: time.sleep(10)

        # Launch audio recording in separate thread
        #thread = Thread(target=start_audio_recording, args = (d, ))
        #thread.start()

        # Start capturing until end hour
        images = capture_every_n_sec_until(camera)

        save_images(images, d)
        analyze(images, d)

        thread.join()

def shoot_and_save(img_path):
    cam = setup_camera()
    pic = take_picture(cam)
    im = Image.fromarray((pic * 255).astype(np.uint8))
    im = im.resize((320, 240))
    im.save(img_path)
    print(f"Shot and saved image to {img_path}")

def test():
    logging.info("Testing. ")
    images = np.random.rand(300, 256, 256)
    analyze(images, 0)
    exit()

if __name__ == '__main__':
    data_folders = ["audio", "logs", "raw_images"]
    for df in data_folders:
        if not os.path.exists(df):
            os.makedirs(df)

    logging.basicConfig(filename='logs/log_{}.log'.format(time.strftime("%Y%m%d-%H%M%S")), level=logging.INFO)
    camera = setup_camera()

    logging.info("Starting sleep analysis, N_DAYS = {}. ".format(N_DAYS))
    start_schedule(camera)

    logging.info("Done. ")
