import cv2
import imutils
import numpy as np
import pytesseract
from picamera2.picamera2 import *



cv2.startWindowThread()

picam2 = Picamera2()
picam2.start_preview()
# preview = NullPreview(picam2)
# picam2.configure(picam2.preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))

preview_config = picam2.preview_configuration(main={"format": 'XRGB8888'})
capture_config = picam2.still_configuration(main={"format": 'XRGB8888'})
picam2.configure(preview_config)
picam2.start()


while True:
    img = picam2.capture_array()
    baseImg = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale
    blurred = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise

    edged = cv2.Canny(blurred, 30, 200) #Perform Edge detection

    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

    cv2.drawContours(baseImg, cnts, -1, (0, 0, 255), 2)

    images = [img, gray, edged,]

    if len(cnts) > 0:
        # Masking the part other than the number plate
        mask = np.zeros(gray.shape,np.uint8)
        cv2.drawContours(mask, [cnts[0]],0,255,3,)
        cv2.bitwise_and(baseImg,baseImg,mask=mask)
        images.append(mask)

        # Now crop
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped = gray[topx:bottomx+1, topy:bottomy+1]
        images.append(cropped)

        psmMode = 8
        allowedChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789"
        # Read the number plate with tesseract
        tesseractConfig = "--psm {} -c tessedit_char_whitelist={} ".format(psmMode, allowedChars)

        text = pytesseract.image_to_string(cropped, config=tesseractConfig)
        print("Detected Number is:",text)
        # cv2.imshow('image',img)
        # cv2.imshow('Cropped',cropped)
    images.append(baseImg)

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
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
