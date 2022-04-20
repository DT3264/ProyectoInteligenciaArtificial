# Reduce el tamano del swap
echo "Reduciendo swap"
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=100/' /etc/dphys-swapfile
sudo sed -i 's/.*CONF_MAXSWAP=.*/CONF_MAXSWAP=100/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
echo "Listo, reiniciando"
sudo reboot
