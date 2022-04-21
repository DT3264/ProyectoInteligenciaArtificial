# Prueba de segmentacion agresiva
# En img_res se ve claramente la zona donde esta la placa al menos en las imagenes de prueba

import cv2
import numpy as np
from picamera2.picamera2 import *
import imutils

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
    # Extrae contornos
    contours = cv2.findContours(img_res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    # Obtiene y dibuja el contorno mas grande
    big_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(img, [big_contour], -1, (0,255,0), 3)
    # Obtiene y dibuja el rectangulo mas pequeno que contiene al contorno
    x,y,w,h = cv2.boundingRect(big_contour)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0,0,255), 3)


    images = [img, img_res]

    if len(contours) > 0:
        # Crea una mascara con el contorno de la placa
        baseImage = img.copy()
        mask = np.zeros(img_res.shape,np.uint8)
        cv2.drawContours(mask, [big_contour],0,255,3)
        images.append(mask)
        cv2.bitwise_and(baseImage,baseImage,mask=mask)
        # Now crop
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped = img[topx:bottomx+1, topy:bottomy+1]
        images.append(cropped)
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
