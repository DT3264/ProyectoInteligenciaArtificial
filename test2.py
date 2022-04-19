import numpy as np
import cv2
from easyocr import Reader
import re

from picamera2.picamera2 import *

cv2.startWindowThread()

picam2 = Picamera2()
picam2.start_preview()

preview_config = picam2.preview_configuration(main={"format": 'XRGB8888'})
picam2.configure(preview_config)
picam2.start()

def analize(plateImage):
    # initialize the reader object
    reader = Reader(['en'])
    # Characters allowed
    allowlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
    # detect the text from the license plate
    detection = reader.readtext(plateImage, allowlist=allowlist, batch_size=4)

    text = f"Detectados: {len(detection)}"
    print(text)
    if len(detection) == 0:
        # if the text couldn't be read, show a custom message
        text = "Impossible to read the text from the license plate"
        print(text)
    else:
        # draw the contour and write the detected text on the image
        # cv2.drawContours(image, [n_plate_cnt], -1, (0, 255, 0), 3)
        for d in detection:
            plate = d[1].replace(" ", "")
            if not re.match("[A-Z]{3}-[0-9]{3}-[A-Z]", plate):
                continue
            prob = f"{d[2] * 100:.2f}%"
            text = f"{plate} -  {prob}"
            print(text)
            # unpack the bounding box
            (tl, tr, br, bl) = d[0]
            tl = (int(tl[0]), int(tl[1]))
            tr = (int(tr[0]), int(tr[1]))
            br = (int(br[0]), int(br[1]))
            bl = (int(bl[0]), int(bl[1]))
            # cleanup the text and draw the box surrounding the text along
            # with the OCR'd text itself
            cv2.rectangle(image, tl, br, (0, 255, 0), 2)
            cv2.putText(image, text, (tl[0], tl[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (64, 128, 255), 2)

while True:
    image = picam2.capture_array()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray, (5,5), 0) 
    edged = cv2.Canny(blur, 10, 200) 
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]

    # analize(gray)

    n_plate_cnt = None
    # loop over the contours
    for c in contours:
        # approximate each contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if the contour has 4 points, we can say
        # that we have found our license plate
        if len(approx) == 4:
            n_plate_cnt = approx
            break        

    # get the bounding box of the contour and 
    # extract the license plate from the image
    if n_plate_cnt is not None:
        (x, y, w, h) = cv2.boundingRect(n_plate_cnt)
        license_plate = gray[y:y + h, x:x + w]
        analize(license_plate)

    images = [image, gray, blur, edged]

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

