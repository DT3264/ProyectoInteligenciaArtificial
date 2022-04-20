# Contenido
- [Contenido](#contenido)
- [Script con todo automatizado](#script-con-todo-automatizado)
- [Instalación del sistema](#instalación-del-sistema)
- [Compilación de opencv](#compilación-de-opencv)
  - [Pasos](#pasos)
    - [1) Aumentar la memoria swap](#1-aumentar-la-memoria-swap)
    - [2) Descargar y ejecucar el script de intalación](#2-descargar-y-ejecucar-el-script-de-intalación)
    - [3) Reducir la memoria swap](#3-reducir-la-memoria-swap)
- [Compilación de picamera2](#compilación-de-picamera2)
    - [1) clonar libcamera compatible con picamera2](#1-clonar-libcamera-compatible-con-picamera2)
    - [2) configurar meson](#2-configurar-meson)
    - [3) compilar libcamera compatible con picamera2](#3-compilar-libcamera-compatible-con-picamera2)
    - [4) some DRM/KMS bindings (?)](#4-some-drmkms-bindings-)
    - [5) El modulo python-v4l2](#5-el-modulo-python-v4l2)
    - [6) clonar el repo de picamera2](#6-clonar-el-repo-de-picamera2)
    - [7) exportar las librerias a python](#7-exportar-las-librerias-a-python)
- [Instalación de librerías de python requeridas](#instalación-de-librerías-de-python-requeridas)
- [Ejecucion del programa](#ejecucion-del-programa)
- [Referencias](#referencias)

# Script con todo automatizado
Si prefieren que el sistema haga todo, descargar y ejecutar el script con todos los comandos mencionados con lo siguiente.
```
git clone git@github.com:DT3264/ProyectoInteligenciaArtificial.git
cd ProyectoInteligenciaArtificial
sudo chmod 755 ./incrementaSwap.sh
sudo chmod 755 ./reduceSwap.sh
sudo chmod 755 ./script.sh
./incrementaSwap.sh
```
## Despues de reiniciar ejecutar lo siguiente
```
cd ProyectoInteligenciaArtificial
./script.sh
```

## Posterior a que se instaló todo, se recomienda ejecutar el siguiente código
```
cd ProyectoInteligenciaArtificial
./reduceSwap.sh
```

# Instalación del sistema
Asegurese de instalar una distribución (recomendado Raspberry Pi OS, no la versión Lite) de 64 bits. 
Una versión de 64 bits es requerida debido a que el paquete easyocr sólo está disponible en distribuciones de 64 bits.

# Compilación de opencv
Debido a que al instalar opencv ya sea con pip o con apt la versión instalada es de 32 bits, esto acarrea detalles y/o problemas durante su uso en una distro de 64 bits. Por esto es necesario compilar opencv manualmente para 64 bits.

## Pasos
### 1) Aumentar la memoria swap
Debido a que la compilación de opencv requiere de muchso recursos, es necesario aumentar la memoria swap, de otra manera la compilación fallará, esto se logra de la siguiente manera.

+ Deshabilitar la memoria swap 
```
sudo dphys-swapfile swapoff
```

+ Modificar el tamaño del swap
```
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=4096/' /etc/dphys-swapfile
sudo sed -i 's/.*CONF_MAXSWAP=.*/CONF_MAXSWAP=4096/' /etc/dphys-swapfile
```
+ Configurar el archivo swap 
```
sudo dphys-swapfile setup
```

+ Habilitar la memoria swap 
```
sudo dphys-swapfile swapon
```

### 2) Descargar y ejecucar el script de intalación
+ Descargar el script 
```
wget https://github.com/Qengineering/Install-OpenCV-Raspberry-Pi-64-bits/raw/main/OpenCV-4-5-4.sh
```
+ Darle permisos de ejecución 
```
sudo chmod 755 ./OpenCV-4-5-4.sh
```
+ Ejecutar el script (Tardará entre 1 a 1.e horas en completar)
```
./OpenCV-4-5-x.sh
```

### 3) Reducir la memoria swap
La memoria swap reside en la tarjeta SD, entonces mientras más grande sea la memoria swap, más lectura/escritura habrá en la tarjeta SD resultando en un corto tiempo de vida. 

Se recomienda seguir las instriccuiones del paso 1 pero definir ``CONF_SWAPSIZE=100`` y ``CONF_MAXSWAP=100`` que es su valor predeterminado en la raspberry 4b.

# Compilación de picamera2
Instalar paquetes necesarios
```
sudo apt install -y libcamera-dev libepoxy-dev libjpeg-dev libtiff5-dev
sudo apt install -y python3-pip git
sudo pip3 install jinja2
sudo apt install -y libboost-dev
sudo apt install -y libgnutls28-dev openssl libtiff5-dev
sudo apt install -y qtbase5-dev libqt5core5a libqt5gui5 libqt5widgets5
sudo apt install -y meson
sudo pip3 install pyyaml ply
sudo pip3 install --upgrade meson
sudo apt install -y libglib2.0-dev libgstreamer-plugins-base1.0-dev
```

### 1) clonar libcamera compatible con picamera2
```
cd
git clone --branch picamera2 https://github.com/raspberrypi/libcamera.git
cd libcamera
```

### 2) configurar meson
```
meson build --buildtype=release -Dpipelines=raspberrypi -Dipas=raspberrypi -Dv4l2=true -Dgstreamer=enabled -Dtest=false -Dlc-compliance=disabled-Dcam=disabled -Dqcam=enabled -Ddocumentation=disabled -Dpycamera=enabled
```

### 3) compilar libcamera compatible con picamera2
(Toma unos 10 minutos)
```
ninja -C build 
sudo ninja -C build install
```

### 4) Clonar e instalar otras librerias necesarias
```
cd
git clone https://github.com/tomba/kmsxx.git
cd kmsxx
git submodule update --init
sudo apt install -y libfmt-dev libdrm-dev
meson build
ninja -C build
cd
git clone https://github.com/RaspberryPiFoundation/python-v4l2.git
```

### 5) clonar el repo de picamera2
```
cd
sudo pip3 install pyopengl piexif
sudo apt install -y python3-pyqt5
git clone https://github.com/raspberrypi/picamera2.git
```

### 6) exportar las librerias a python
```
cd
echo "export PYTHONPATH=/home/pi/picamera2:/home/pi/libcamera/build/src/py:/home/pi/kmsxx/build/py:/home/pi/python-v4l2" >> .bashrc
```

# Instalación de librerías de python requeridas para los codigos
```
git clone https://github.com/DT3264/ProyectoInteligenciaArtificial.git
cd ProyectoInteligenciaArtificial
pip install -r requirements.txt
sudo apt install -y tesseract-ocr
pip uninstall -y opencv-python-headless
pip install numpy --upgrade
```

# Instalacion y ejecucion de vscode para ejecutar el codigo
```
sudo apt install code
code .
```

# Referencias
[Install-OpenCV-Raspberry-Pi-64-bits](https://github.com/Qengineering/Install-OpenCV-Raspberry-Pi-64-bits)

[PiCamera2](https://github.com/raspberrypi/picamera2)
