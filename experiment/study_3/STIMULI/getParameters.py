# creating stimuli parameter JSONs

from __future__ import division
import cv2
import numpy as np
import os
import math
import json
import wave
import contextlib
import spectral_centroid as scentroid
from scipy.signal import hilbert
from scipy.io import wavfile
from librosa import onset

cwd = os.getcwd()

## SHAPES

def get_boundingBox(image_path, area=False, rotate=True):
    # get the image
    im_in = cv2.imread(image_path,0)

    # Threshold.
    # Set values equal to or above 220 to 0.
    # Set values below 220 to 255.

    th, im_th = cv2.threshold(im_in, 225, 255, cv2.THRESH_BINARY_INV);

    # Copy the thresholded image.
    im_floodfill = im_th.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = im_th.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0,0), 255);

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    im_out = im_th | im_floodfill_inv

    im_out, contours,hierarchy = cv2.findContours(im_out, 1, 2)
    cnt = contours[0]
    cntArea = cv2.contourArea(cnt)

    if rotate:
        # Now get the bounding box
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        if area:
            return rect[1][0] * rect[1][1], int(cntArea)

        return im_out, box

    else:
        x,y,w,h = cv2.boundingRect(cnt)
        box = np.array([[x,y],[x,y+h],[x+w, y+h],[x+w,y]])

        if area:
            return w*h, int(cntArea)

        return im_out, box



images = {}
for zscore in range(13):
    images[zscore] = {}

    types = ["LC", "PS"]
    for method in types:
        for num in range(15):
            name = method + str(num)

            images[zscore][name] = []

for i in range(13):
    sc_dir = os.path.join(cwd, "images", str(i))

    for method in os.listdir(sc_dir):
        image_method = os.path.join(sc_dir, method)

        if method == ".DS_Store":
            os.remove(image_method)
            continue

        for num in range(15):
            imageFile = os.path.join(image_method, method + str(num))

            if imageFile == ".DS_Store" + str(num):
                os.remove(os.path.join(image_method, ".DS_Store"))
                continue

            area = get_boundingBox(imageFile, area=True, rotate=False)
            if area[0] <= 0:
                print "Bad: " + imageFile


            images[i][method + str(num)].append(i+1)
            images[i][method + str(num)].append(area[0])
            images[i][method + str(num)].append(area[1]/area[0])

imageParameters = os.path.join(os.path.dirname(cwd), "DATA", "imageParameters2.json")
with open(imageParameters, 'w') as f:
    json.dump(images, f, sort_keys=True, indent=4)



## SOUNDS
sounds = {}
for zscore in range(13):
    sounds[zscore] = {}

    types = ["LFO", "ROS", "SAW"]
    for method in types:
        for num in range(10):
            name = method + str(num)

            sounds[zscore][name] = []

for i in range(13):
    sc_dir = os.path.join(cwd, "sounds", str(i))

    for method in os.listdir(sc_dir):
        sound_method = os.path.join(sc_dir, method)

        if method == ".DS_Store":
            os.remove(sound_method)
            continue

        for num in range(10):
            sound_file = os.path.join(sound_method, method + str(num))

            if sound_file == ".DS_Store" + str(num):
                os.remove(os.path.join(sound_method, ".DS_Store"))
                continue

            spec = scentroid.mean_sc_for_file(sound_file)
            with contextlib.closing(wave.open(sound_file,'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)


            sounds[i][method + str(num)].append(spec)
            sounds[i][method + str(num)].append(duration)

            audio_ts = wavfile.read(sound_file)

            onset_data = onset.onset_detect(audio_ts[1], audio_ts[0])
            mean_strength = np.mean(onset.onset_strength(audio_ts[1],
                                                          audio_ts[0]))



            sounds[i][method + str(num)].append(len(onset_data))
            sounds[i][method + str(num)].append(mean_strength)

soundParameters = os.path.join(os.path.dirname(cwd), "DATA", "soundParameters2.json")
with open(soundParameters, 'w') as f:
    json.dump(sounds, f, sort_keys=True, indent=4)
