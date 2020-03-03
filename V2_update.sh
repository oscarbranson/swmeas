# raspberry pi logging upgrade for Gascard CO2 sensor

# remove old files
rm -r ~/swmeas/swmeas
rm -r ~/swmeas/rpi_scripts
rm -r ~/swmeas/systemd-services
rm ~/swmeas/setup.py

# copy update
cp -r /media/usb/TFR/swmeas/* ~/swmeas/

# install
cd ~/swmeas
sudo python setup.py develop
cd ~

# install systemd services
sudo cp ~/swmeas/systemd-services/* /lib/systemd/system/

# remove old services
sudo systemctl stop log-CO2.service
sudo systemctl disable log-CO2.service
sudo systemctl stop log-pH.service
sudo systemctl disable log-pH.service

# activate new services
sudo systemctl enable log-pH-CO2.service
sudo systemctl start log-pH-CO2.service

# check it's working
cat /media/usb/log_data/log_pH_CO2.csv

# adding PCF8523 RTC module (https://pimylifeup.com/raspberry-pi-rtc/)
sudo raspi-config
# 5 interfacing options > P5 I2C > Enable

sudo reboot

# install software
sudo apt-get install python-smbus i2c-tools

# check clock is detected
sudo i2cdetect -y 1

# update boot settings
sudo vim /boot/config.txt

# add line: dtoverlay=i2c-rtc,pcf8523

sudo reboot

# check detected
sudo i2cdetect -y 1  # should read UU

# remove fake-hwclock
sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove

# update clock settings
sudo vim /lib/udev/hwclock-set

# comment out:
# if [ -e /run/systemd/system ] ; then
#     exit 0
# fi

# synchronise the clock
sudo hwclock -D -r
date
sudo hwclock -w
sudo hwclock -r
