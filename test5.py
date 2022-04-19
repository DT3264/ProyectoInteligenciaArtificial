import cv2
import numpy as np
import numpy as np
import cv2
import imutils
import numpy as np
from PIL import Image
from torch import conv2d

from picamera2.picamera2 import *

cv2.startWindowThread()

picam2 = Picamera2()
picam2.start_preview()

preview_config = picam2.preview_configuration(main={"format": 'XRGB8888'})
picam2.configure(preview_config)
picam2.start()

while True:

    image = picam2.capture_array()


    # read image
    img = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    hh, ww = img.shape[:2]

    # convert to grayscale
    gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    
    # threshold
    thresh = cv2.threshold(gray,128, 255,cv2.THRESH_BINARY_INV)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    thresh = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel)

    # apply close and open morphology
    close = 7#3,11
    kernel = np.ones((close, close), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    open = 11#11,21
    kernel = np.ones((open, open), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # invert
    mask = 255 - mask

    # get largest contour
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)

    # draw green contour on input
    contour_img = img.copy()

    ## approx the contour, so the get the corner points
    arclen = cv2.arcLength(big_contour, True)
    l = 0.010
    r = 0.015
    m = (l+r)/2 #0.115
    # print(m)
    # approx = cv2.approxPolyDP(big_contour, 0.02* arclen, True)
    approx = cv2.approxPolyDP(big_contour, m* arclen, True)
    cv2.drawContours(contour_img, [approx], -1, (0,0,255), 1)
    cv2.drawContours(contour_img,[big_contour],0,(0,255,0),2)

    def getCropped(gray, baseImage, contour):
        mask = np.zeros(gray.shape,np.uint8)
        cv2.drawContours(mask, [contour],0,255,3,)
        cv2.bitwise_and(baseImage,baseImage,mask=mask)
        # Now crop
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        # topx=bott
        cropped = gray[topx:bottomx+1, topy:bottomy+1]
        
        mask2 = np.zeros(gray.shape,np.uint8)
        (x,y,w,h) = cv2.boundingRect(contour)
        cv2.rectangle(mask2, (x,y), (x+w,y+h), 255, 3)
        cropped2 = gray[y:y+h+1, x:x+w+1]

        return mask, cropped, mask2, cropped2

    m1, cropped1, mc1, c1 = getCropped(gray, image.copy(), approx)
    # m2, cropped2, mc2, c2 = getCropped(gray, image.copy(), big_contour)
    
    # images.append(cropped)

    images = [image, gray, thresh, mask, contour_img, 
    cropped1, m1, c1, mc1, 
    # cropped2, m2, c2, mc2
    ]

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
        if index % 5 == 0:
            height += 320
            width = 0
