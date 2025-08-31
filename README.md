# Raspberry Pi Weather Clock / Slideshow Setup

## 1: Download Putty and Latest RPi Imager
- Install RPi OS Lite 32-bit
- Edit settings:
  - Hostname: `rpi`
  - Username: `rpi`
  - Password: your choice
  - Configure WLAN
  - Set locale
  - Services: enable SSH, use password authentication
- Flash SD card
- Boot Pi and connect via Putty SSH

## 5: Update
sudo apt update && sudo apt upgrade -y

## 6: Install Python & Kivy
--1: Install required packages
sudo apt install -y python3-pip python3-setuptools python3-venv

--2: Create virtual environment and activate
python3 -m venv ~/weather_app/venv
source ~/weather_app/venv/bin/activate

--3: Install Kivy
pip install kivy

--4: Install other dependencies
pip install requests tzdata kivy

## 7: Create Weather App Folder
mkdir ~/weather_app
cd ~/weather_app

## 8: Add Weather Script
sudo nano ~/weather_app/weather_script.py
(Paste the script, then Ctrl+O to save, Enter to confirm, Ctrl+X to exit)

## 9: Fix Missing Dependencies
sudo apt install -y libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils

## 11: Import Weather Icons
cd ~/weather_app
mkdir -p weather_icons
cd weather_icons
wget https://openweathermap.org/img/wn/01d.png
wget https://openweathermap.org/img/wn/01n.png
wget https://openweathermap.org/img/wn/02d.png
wget https://openweathermap.org/img/wn/02n.png
wget https://openweathermap.org/img/wn/03d.png
wget https://openweathermap.org/img/wn/03n.png
wget https://openweathermap.org/img/wn/04d.png
wget https://openweathermap.org/img/wn/04n.png
wget https://openweathermap.org/img/wn/09d.png
wget https://openweathermap.org/img/wn/09n.png
wget https://openweathermap.org/img/wn/10d.png
wget https://openweathermap.org/img/wn/10n.png
wget https://openweathermap.org/img/wn/11d.png
wget https://openweathermap.org/img/wn/11n.png
wget https://openweathermap.org/img/wn/13d.png
wget https://openweathermap.org/img/wn/13n.png
wget https://openweathermap.org/img/wn/50d.png
wget https://openweathermap.org/img/wn/50n.png

## Optional: High-Quality Icons
cd ~/weather_app/weather_icons
rm -rf ~/weather_app/weather_icons/*
wget https://openweathermap.org/img/wn/01d@2x.png
wget https://openweathermap.org/img/wn/01n@2x.png
wget https://openweathermap.org/img/wn/02d@2x.png
wget https://openweathermap.org/img/wn/02n@2x.png
wget https://openweathermap.org/img/wn/03d@2x.png
wget https://openweathermap.org/img/wn/03n@2x.png
wget https://openweathermap.org/img/wn/04d@2x.png
wget https://openweathermap.org/img/wn/04n@2x.png
wget https://openweathermap.org/img/wn/09d@2x.png
wget https://openweathermap.org/img/wn/09n@2x.png
wget https://openweathermap.org/img/wn/10d@2x.png
wget https://openweathermap.org/img/wn/10n@2x.png
wget https://openweathermap.org/img/wn/11d@2x.png
wget https://openweathermap.org/img/wn/11n@2x.png
wget https://openweathermap.org/img/wn/13d@2x.png
wget https://openweathermap.org/img/wn/13n@2x.png
wget https://openweathermap.org/img/wn/50d@2x.png
wget https://openweathermap.org/img/wn/50n@2x.png
for f in ~/weather_app/weather_icons/*@2x*.png; do [ -f "$f" ] && mv -v "$f" "${f//@2x/}"; done

## 12: Create Folder for Slideshow Pictures
mkdir /home/rpi/pictures/
cd /home/rpi/pictures/
wget YourImageURL

## Final Test
python ~/weather_app/weather_script.py
(Press Ctrl+C to exit script)

## If SSH was exited
source /home/rpi/weather_app/venv/bin/activate
python ~/weather_app/weather_script.py

## Make Auto-Boot
sudo nano /etc/systemd/system/weather_app.service
(Paste the service content from instructions, save & exit)
sudo systemctl enable weather_app.service
sudo systemctl start weather_app.service
sudo systemctl status weather_app.service
sudo reboot

## Optional / Important
sudo systemctl disable avahi-daemon
sudo systemctl stop avahi-daemon
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
sudo apt purge wolfram-engine libreoffice* minecraft-pi -y
sudo apt autoremove -y
sudo apt update
sudo apt install ufw -y
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
SUBNET=$(ip -o -f inet addr show wlan0 | awk '/scope global/ {print $4}')
echo $SUBNET
sudo ufw allow from $SUBNET to any port 22 proto tcp
sudo ufw allow out 80,443/tcp
sudo ufw enable
sudo ufw status verbose

## Auto Update Every Night
sudo nano /usr/local/bin/weather_safe_update.sh
(Paste script content, save & exit)
sudo chmod +x /usr/local/bin/weather_safe_update.sh
sudo nano /etc/systemd/system/weather_safe_update.service
sudo nano /etc/systemd/system/weather_safe_update.timer
sudo nano /etc/systemd/system/weather_safe_update-onboot.service
sudo nano /etc/systemd/system/weather_safe_update-onboot.timer
sudo systemctl enable --now weather_safe_update.timer
sudo systemctl enable --now weather_safe_update-onboot.timer

# DONE!
