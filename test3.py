import numpy as np
import cv2
import imutils
from easyocr import Reader
import re
from gpiozero import Button, LEDBoard
from time import sleep
from datetime import datetime
from picamera2.picamera2 import *
import pytesseract
from pytesseract import Output

os.makedirs("placas", exist_ok=True)
# Todas las imagenes se guardaran en la carpeta 'placas' ubicada donde se encuentre este archivo
os.chdir("placas")

# Inicializa valores requeridos a nivel global
button = Button(24)
leds = LEDBoard(26, 19, 13)
picam2 = Picamera2()

# Inicializa la camara y el hilo que muestra las previas de opencv
def initializeCamera():
    cv2.startWindowThread()
    picam2.start_preview()

    preview_config = picam2.preview_configuration(main={"format": 'XRGB8888'})
    picam2.configure(preview_config)
    picam2.start()

# Muestra cada previa de manera ordenada
def showPreviews():
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

# Enciende multiples led simulando que la pluma de la caseta sube y baja
def pushBarUpAndDown():
    values = [0, 0, 0]
    for i in range(3):
        values[i] = 1
        leds.value = values
        sleep(1)
    for i in range(2, -1, -1):
        values[i] = 0
        leds.value = values
        sleep(1)

# Analiza y retorna el texto detectado en la imagen
def analize(plateImage, image):
    # Prueba con tesseract
    # print("Tesseract")
    # for i in [8, 9, 13]:
    #     print(f"Mode: {i}")
    #     allowedChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789"
    #     # Read the number plate with tesseract
    #     tesseractConfig = "--psm {} -c tessedit_char_whitelist={} ".format(i, allowedChars)
    #     text = pytesseract.image_to_string(plateImage, config=tesseractConfig)
    #     text = text.replace("\n", "")
    #     print(f"String: *{text}*")
    #     d = pytesseract.image_to_data(plateImage, config=tesseractConfig, output_type=Output.DICT)
    #     for t in d["text"]:
    #         if len(t)>0:
    #             print(t)
    
    # print("EasyOCR")
    # initialize the reader object
    reader = Reader(['en'])
    # Characters allowed
    allowlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
    # detect the text from the license plate
    detection = reader.readtext(plateImage, allowlist=allowlist, batch_size=4)

    # text = f"Detectados: {len(detection)}"
    if len(detection) > 0:
        print("Se encontro texto")
        for d in detection:
            # remueve espacios detectados
            plate = d[1].replace(" ", "")
            # Convierte la probabilidad de [0, 1] a [0, 100]
            prob = f"{d[2] * 100:.2f}%"
            text = f"Detected: {plate} -  {prob}"
            print(text)
            
            # El patron de las placas es (en el estandar actual de Guanajuato)
            # 3 letras, 3 digitos y 1 letra si es carro
            # 2 letras, 4 digitos y 1 letra si es camioneta
            # El ultimo guion y letra son opcionales (puede ser el simbolo de discapacidad)
            patron = "[A-Z]{2,3}-[0-9]{3,4}(-[A-Z])?"
            if not re.match(patron, plate):
                continue # Si no se encuentra, sigue buscando
            prob = f"{d[2] * 100:.2f}%"
            text = f"Match: {plate} -  {prob}"
            print(text)

            # desempaqueta la caja detectada
            (tl, _, br, _) = d[0]
            tl = (int(tl[0]), int(tl[1]))
            br = (int(br[0]), int(br[1]))
            # Dibuja una caja donde el texto detectado se ubica
            cv2.rectangle(image, tl, br, (0, 255, 0), 2)
            # Dibuja el texto en la esquina superior izquierda de la caja
            cv2.putText(image, text, (tl[0], tl[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (64, 128, 255), 2)

            # Hay match correcto, retorna el numero de placa
            return plate

    # Si se llega a esta seccion, no se encontro texto o no se encontro el patron de las placas
    print("No se encontro el patron")
    return "NA"

# Obtiene la placa dentro de la imagen
def getPlate():
    # Preprocesa imagen
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Extrae contornos
    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    # Obtiene y dibuja el contorno mas grande
    big_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(image, [big_contour], -1, (0,255,0), 3)
    # Obtiene y dibuja el rectangulo mas pequeno que contiene al contorno
    x,y,w,h = cv2.boundingRect(big_contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0,0,255), 3)

    # images.append(image)
    images.append(gray)
    images.append(binary)

    if len(contours) > 0:
        # Crea una mascara con el contorno de la placa
        baseImage = image.copy()
        mask = np.zeros(gray.shape,np.uint8)
        cv2.drawContours(mask, [big_contour],0,255,3)
        images.append(mask)
        cv2.bitwise_and(baseImage,baseImage,mask=mask)
        # Now crop
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped = gray[topx:bottomx+1, topy:bottomy+1]
        images.append(cropped)
        return cropped
    return None

# Seccion principal
initializeCamera()

while True:
    images = []

    image = picam2.capture_array()
    untouched = image.copy()

    images.append(image)
    plate = getPlate()

    if plate is not None and button.is_active:
        print("analizing")
        fecha = str(datetime.date(datetime.now())).replace("-", "")
        hora = str(datetime.time(datetime.now())).split(".")[0].replace(":", "") # Separa hasta el '.' previo a los milisegundos y toma hasta antes del '.'
        textoPlaca = analize(plate, image)
        nombre = f"{fecha}_{hora}_{textoPlaca}.jpg"
        cv2.imwrite(nombre, untouched)
        pushBarUpAndDown()
        print("done")
    
    showPreviews()
