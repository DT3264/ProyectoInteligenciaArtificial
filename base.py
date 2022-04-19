import numpy as np
import cv2
from picamera2.picamera2 import *

cv2.startWindowThread()

picam2 = Picamera2()
picam2.start_preview()

preview_config = picam2.preview_configuration(main={"format": 'XRGB8888'})
picam2.configure(preview_config)
picam2.start()

while True:

    image = picam2.capture_array()

    images = [image]

    index = 0
    width = 0
    height = 0
    for img in images:
        window = f"Img {index}"
        cv2.namedWindow(window, cv2.WINDOW_KEEPRATIO) 
        cv2.imshow(window, img)
        cv2.resizeWindow(window, 275, 275)
        cv2.moveWindow(window,width,height)
        width += 320
        index += 1
        if index % 6 == 0:
            height += 320
            width = 0
