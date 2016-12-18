#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import threading
from collections import deque
import argparse


def image_generator():
    global img_buffer, buffer_lock, buffer_full, buffer_empty, bw
    while True:
        #if bw:
        #    c = 1
        #else:
        #    c = 3
        #data = np.random.bytes(h*w*c)
        #img = np.frombuffer(data, dtype=np.uint8).reshape((h,w,c))
        if bw:
            data = np.random.bytes(h*w)
            img = np.frombuffer(data, dtype=np.uint8).reshape((h,w))
            img = np.dstack((img,img,img))
        else:
            data = np.random.bytes(h*w*3)
            img = np.frombuffer(data, dtype=np.uint8).reshape((h,w,3))
        buffer_lock.acquire()
        while not len(img_buffer) < img_buffer.maxlen:
            buffer_full.wait()
        img_buffer.append(img)
        buffer_empty.notify()
        buffer_lock.release()


# Parse command-line arguments 
parser = argparse.ArgumentParser(description="Generates random pixels on the screen.")
parser.add_argument('-b', action='store_true', help='black and white, instead of colors')
args = parser.parse_args()
bw = args.b

winname = "screensaver"
cv2.namedWindow(winname, cv2.WND_PROP_FULLSCREEN | cv2.WINDOW_OPENGL)          
cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

h, w = (1080, 1920)
N = 3
img_buffer = deque(maxlen=N)
buffer_lock = threading.Lock()
buffer_full = threading.Condition(buffer_lock)
buffer_empty = threading.Condition(buffer_lock)
imggenthread = threading.Thread(target=image_generator)
imggenthread.daemon = True
imggenthread.start()
while True:
    buffer_lock.acquire()
    while not len(img_buffer) > 0:
        buffer_empty.wait()
    img = img_buffer.popleft()
    cv2.imshow(winname, img)
    buffer_full.notify()
    buffer_lock.release()
    key = cv2.waitKey(33)
    if key > 0:
        break
buffer_lock.acquire()
buffer_full.notify()
buffer_lock.release()
