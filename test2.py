from qt_gl_preview import *
from picamera2 import *
from gpiozero import Button
from datetime import datetime
os.chdir("../proyecto")
button = Button(24)
picam2 = Picamera2()
preview = QtGlPreview(picam2)
preview_config = picam2.preview_configuration()
capture_config = picam2.still_configuration()
picam2.configure(preview_config)
picam2.start()
while True:    
    button.wait_for_press()
    fecha = datetime.date(datetime.now())
    # Despues del punto son los milisegundos, no son necesarios
    hora = str(datetime.time(datetime.now())).split(".")[0]
    # Pendiente
    placa = "placa"
    nombre = f"{fecha}_{hora}_{placa}.jpg"
    if not picam2.async_operation_in_progress:
      picam2.switch_mode_and_capture_file(capture_config, nombre, wait=False, signal_function=None)
