# Prueba de segmentacion agresiva
# En img_res se ve claramente la zona donde esta la placa al menos en las imagenes de prueba

import cv2
import numpy as np
from picamera2.picamera2 import *

cv2.startWindowThread()

picam2 = Picamera2()
picam2.start_preview()

preview_config = picam2.preview_configuration(main={"format": 'XRGB8888'})
picam2.configure(preview_config)
picam2.start()

def unsharp_mask(img, blur_size, imgWeight, gaussianWeight):
    gaussian = cv2.GaussianBlur(img, blur_size, 0)
    return cv2.addWeighted(img, imgWeight, gaussian, gaussianWeight, 0)
def smoother_edges(img, first_blur_size, second_blur_size=(5, 5), imgWeight=1.5, gaussianWeight=-0.5):
    img = cv2.GaussianBlur(img, first_blur_size, 0)
    return unsharp_mask(img, second_blur_size, imgWeight, gaussianWeight)

while True:
    img = picam2.capture_array()
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img_res = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurPos = 50
    img_res = smoother_edges(img_res, (3 * 2 + 1, 3 * 2 + 1), (blurPos * 2 + 1, blurPos * 2 + 1))
    threshSize = 200
    _, img_res = cv2.threshold(img_res, threshSize, 255, 0)
    images = [img, img_res]
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
