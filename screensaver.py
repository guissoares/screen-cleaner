#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import threading
from collections import deque

def image_generator():
    global img_buffer, buffer_lock, buffer_full, buffer_empty
    while True:
        data = np.random.bytes(3*h*w)
        img = np.frombuffer(data, dtype=np.uint8).reshape((h,w,3))
        buffer_lock.acquire()
        while not len(img_buffer) < img_buffer.maxlen:
            buffer_full.wait()
        img_buffer.append(img)
        buffer_empty.notify()
        buffer_lock.release()

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
