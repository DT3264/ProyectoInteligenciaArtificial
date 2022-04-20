# Compila opencv
wget https://github.com/Qengineering/Install-OpenCV-Raspberry-Pi-64-bits/raw/main/OpenCV-4-5-4.sh
sudo chmod 755 ./OpenCV-4-5-4.sh
./OpenCV-4-5-4.sh

# Compilar picamera2
# Instalar paquetes necesarios
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

# Clonar libcamera
cd
git clone --branch picamera2 https://github.com/raspberrypi/libcamera.git
cd libcamera

# Configurar meson
meson build --buildtype=release -Dpipelines=raspberrypi -Dipas=raspberrypi -Dv4l2=true -Dgstreamer=enabled -Dtest=false -Dlc-compliance=disabled -Dcam=disabled -Dqcam=enabled -Ddocumentation=disabled -Dpycamera=enabled

# Compilar libcamera
ninja -C build 
sudo ninja -C build install

# Algunas librerias requeridas
cd
git clone https://github.com/tomba/kmsxx.git
cd kmsxx
git submodule update --init
sudo apt install -y libfmt-dev libdrm-dev
meson build
ninja -C build
cd
git clone https://github.com/RaspberryPiFoundation/python-v4l2.git

# Clonar el repo de picamera2
cd
sudo pip3 install pyopengl piexif
sudo apt install -y python3-pyqt5
git clone https://github.com/raspberrypi/picamera2.git

# Exportar librerias descargadas a python
cd
sudo echo "export PYTHONPATH=/home/pi/picamera2:/home/pi/libcamera/build/src/py:/home/pi/kmsxx/build/py:/home/pi/python-v4l2" >> .bashrc

# Clonar proyecto de la  materia
git clone https://github.com/DT3264/ProyectoInteligenciaArtificial.git
cd ProyectoInteligenciaArtificial
# Instalar dependencias requeridas
pip install -r requirements.txt
pip uninstall -y opencv-python-headless
pip install numpy --upgrade
# Instalar vs code
sudo apt install code
# Abrir esta carpeta en vs code
code .
