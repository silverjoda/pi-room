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
import yaml

class SleepCapturer:
    def __init__(self, config):
        self.config = config
        self.camera = self.setup_camera()

    def setup_camera(self):
        logging.info("Setting up camera. ")
        self.camera = PiCamera()
        self.camera_resolution = eval(config["camera_resolution"])
        self.resized_resolution = eval(config["resized_resolution"])
        self.camera.resolution = self.camera_resolution

    def take_picture(self):
        im = np.empty((self.camera_resolution[1], self.camera_resolution[0], 3), dtype=np.uint8)
        self.camera.capture(im, 'rgb', resize=(self.resized_resolution[0], self.resized_resolution[1]))
        logging.debug("Took image at {}. Min: {}, Max: {}. ".format(time.time(), im.min(), im.max()))
        return im

    def capture_image_every_interval_until(self, day):
        logging.info("Starting camera capturing with interval {}s until {}'th hour".format(self.config["capture_sleep_interval_secs"],
                                                                                           self.config["capture_end_hour"]))
        pics_list_gs = []
        while datetime.datetime.now().hour < self.config["capture_end_hour"]:
            im = self.take_picture()

            # Make grayscale image and append to list
            im_gs = np.mean(im, 2)
            pics_list_gs.append(im_gs)

            # Save image raw to disk
            save_path = f"raw_images/day-{day}/hour_{datetime.datetime.now().hour}_img{len(pics_list_gs)}"
            im_pil = Image.fromarray(im)
            im_pil.save(save_path)

            time.sleep(self.config["capture_sleep_interval_secs"])
        logging.info("Collected {} images. ".format(len(pics_list_gs)))
        return np.array(pics_list_gs, dtype=np.uint8)

    def start_audio_recording(self, day):
        logging.info("Starting audio capture in separate thread using 'arecord'. ")
        for i in range(self.config["capture_end_hour"] - self.config["capture_begin_hour"]):
            duration = 3600
            save_path = f"audio/day-{day}/hour-{i + self.config['capture_begin_hour']}.wav"
            subprocess.Popen(f"arecord -D plughw:1,0 --duration={duration} --format S16_LE --rate 8000 -V mono -c1 {save_path}", shell=True)

    def start_schedule(self):
        logging.info(f"Starting sleep capture schedule, n_days = {config['n_days']}, current time: {datetime.datetime.now()}. ")

        for day in range(self.config["n_days"]):
            # Make dirs for that day
            data_folders = [f"raw_images/day-{day}", f"audio/day-{day}"]
            for df in data_folders:
                if not os.path.exists(df):
                    os.makedirs(df)

            logging.info("Day: {}, waiting until {}'th hour to start capture. ".format(day, self.config["capture_begin_hour"]))

            # Wait for the initial capture hour to begin. Sleep in between so as not to waste CPU power
            while datetime.datetime.now().hour < self.config["capture_begin_hour"]: time.sleep(10)

            # Launch audio recording in separate thread
            #thread = Thread(target=start_audio_recording, args = (d, ))
            #thread.start()

            # Start capturing until end hour
            images = self.capture_image_every_interval_until(day)

            # Save compressed images for future analysis
            logging.info("Saving images. ")
            save_dir = f"npz_images/compressed_images_day-{day}.npz"
            np.savez(save_dir, images)

            # Perform analysis on daily images
            self.analyze(images, day)

            # Wait for audio thread to join
            logging.debug("Waiting for audio thread to join. ")
            #thread.join()

    def analyze(self, images, day):
        N = len(images)
        logging.info(f"Analyzing image sequence of len={N}. ")

        deltas = []
        for i in range(N - 1):
            delta = np.mean(np.square(images[i + 1] - images[i]))
            deltas.append(delta)

        t = np.linspace(self.config["capture_begin_hour"], self.config["capture_end_hour"], N - 1)
        fig, ax = plt.subplots()
        ax.plot(t, deltas)
        plt.xlabel('Hours')
        plt.ylabel('Neighboring delta')
        plt.margins(x=0)

        # Save plot to image format
        plt.savefig("analysis/images-day-{}.png".format(day))

    def test_shoot_and_save(self, path="tst.png"):
        im = self.take_picture()
        im_pil = Image.fromarray(im)
        im_pil.save(path)
        print(f"Shot and saved image to {path}")

if __name__ == '__main__':
    data_folders = ["audio", "logs", "raw_images", "npz_images", "analysis", "scripts"]
    for df in data_folders:
        if not os.path.exists(df):
            os.makedirs(df)

    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Setup logging
    logging.basicConfig(filename='logs/log_{}.log'.format(time.strftime("%Y%m%d-%H%M%S")), level=logging.DEBUG)

    capturer = SleepCapturer(config)
    capturer.start_schedule()
    logging.info("Done. ")
