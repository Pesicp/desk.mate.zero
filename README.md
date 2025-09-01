# Weather Display App - Raspberry Pi Installation Guide

This guide will walk you through setting up the Weather Display App on a Raspberry Pi (tested with RPi Zero 2W and Spotpear touchscreen).  
All commands are designed for Raspberry Pi OS Lite (32-bit) with Python 3.

## 1. Preparation

- Download and install [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) (for SSH access).
- Download and install the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
- Using Raspberry Pi Imager:
  - Select device: **Raspberry Pi Zero 2W**
  - Select OS: **Raspberry Pi OS Lite (32-bit)**
  - Edit settings, If there is no settings it will appear when you press **NEXT**
    - Hostname: `rpi`
    - Enable SSH (password authentication)
    - Username: `rpi` (better to leave it so, script and folders include this Username)
    - Password: `yourpassword`
    - Configure WiFi (Here write your network name and password)
    - Set country, locale, timezone, keyboard layout
  - Flash the SD card and insert into your Pi.
- Boot the Pi and connect via SSH using PuTTY.

---

# 2. System Setup

## Update system and install required packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-setuptools python3-venv python3-dbus network-manager \
    libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils
```
## Enable and start Network Manager
```bash
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```
# 3. Python Environment and App Setup
# Create weather_app folder and Python virtual environment
```bash
mkdir -p ~/weather_app
python3 -m venv ~/weather_app/venv
```
# Activate virtual environment
```bash
source ~/weather_app/venv/bin/activate
```
# Install Python dependencies
```bash
pip install kivy requests tzdata feedparser
```

---

## 4. Weather Script

```bash
# Create and edit the weather script
nano ~/weather_app/weather_script.py
# (Paste the complete script here, save with Ctrl+O, Enter, exit with Ctrl+X)
```

---

## 5. Weather Icons

```bash
# Create icons folder
mkdir -p ~/weather_app/weather_icons
cd ~/weather_app/weather_icons

# Download standard icons
wget https://openweathermap.org/img/wn/{01d,01n,02d,02n,03d,03n,04d,04n,09d,09n,10d,10n,11d,11n,13d,13n,50d,50n}.png

# For high quality icons (optional), run:
rm -rf ~/weather_app/weather_icons/*
wget https://openweathermap.org/img/wn/{01d,01n,02d,02n,03d,03n,04d,04n,09d,09n,10d,10n,11d,11n,13d,13n,50d,50n}@2x.png
for f in *@2x.png; do mv "$f" "${f/@2x/}"; done
```

---

## 6. Slideshow Pictures

```bash
# Create folder for pictures
mkdir -p /home/rpi/pictures/
cd /home/rpi/pictures/

# Download your pictures with wget, for example:
wget https://yourdomain.com/image1.jpg
# (Repeat for additional images)
```

---

## 7. Missing Dependencies (if needed)

```bash
sudo apt install -y libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils
```

---

## 8. Run the App

```bash
# Activate venv (if not already active)
source ~/weather_app/venv/bin/activate

# Run the app
python ~/weather_app/weather_script.py

# To exit, press Ctrl+C in the terminal.
```

---

## 9. Auto-Start on Boot (systemd service)

```bash
sudo nano /etc/systemd/system/weather_app.service
```

Paste this:
```
[Unit]
Description=Weather Display App
After=network.target

[Service]
ExecStart=/home/rpi/weather_app/venv/bin/python /home/rpi/weather_app/weather_script.py
WorkingDirectory=/home/rpi/weather_app
User=rpi
Group=rpi
Environment="PATH=/home/rpi/weather_app/venv/bin:/usr/bin"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

_Save and exit (Ctrl+O, Enter, Ctrl+X)_

```bash
# Enable and start the service
sudo systemctl enable weather_app.service
sudo systemctl start weather_app.service

# Check status
sudo systemctl status weather_app.service

# Reboot to test auto-start
sudo reboot
```

---

## 10. Security (Optional but Recommended)

```bash
# Disable unneeded services
sudo systemctl disable --now avahi-daemon bluetooth
sudo apt purge -y wolfram-engine libreoffice* minecraft-pi
sudo apt autoremove -y

# Install and configure UFW firewall
sudo apt install ufw -y
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH only from your local subnet
SUBNET=$(ip -o -f inet addr show wlan0 | awk '/scope global/ {print $4}')
sudo ufw allow from $SUBNET to any port 22 proto tcp

# Allow outgoing traffic for weather updates
sudo ufw allow out 80,443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status verbose
```

---

## 11. Auto-Update Script (Optional)

```bash
# Create update script
sudo nano /usr/local/bin/weather_safe_update.sh
```
Paste:
```bash
#!/bin/bash
sleep 60
LAST_UPDATE_FILE="/var/lib/weather_last_update"
[ ! -f "$LAST_UPDATE_FILE" ] && echo "$(date +%Y-%m-%d)" > "$LAST_UPDATE_FILE"
LAST_RUN=$(cat "$LAST_UPDATE_FILE")
TODAY=$(date +%Y-%m-%d)
if [ "$LAST_RUN" != "$TODAY" ]; then
    # Example update commands:
    # git -C /home/rpi/weather_app pull
    # pip3 install --upgrade -r /home/rpi/weather_app/requirements.txt
    echo "$TODAY" > "$LAST_UPDATE_FILE"
    echo "Update finished at $(date)"
else
    echo "Already updated today, skipping."
fi
```
_Save and exit. Then:_
```bash
sudo chmod +x /usr/local/bin/weather_safe_update.sh
```

Create systemd timer and service files as needed (see advanced systemd documentation).

---

## Troubleshooting

- If the device freezes, unplug and replug power.
- To manually start:  
  `source ~/weather_app/venv/bin/activate && python ~/weather_app/weather_script.py`
- To check logs:  
  `sudo journalctl -u weather_app.service`
- Update logs (if enabled): `/home/rpi/weather_update.log`

---

## Notes

- All steps are needed for a working install.
- For best results, use high quality icons and your own images.
- For SSH problems, restart PuTTY and reconnect.

---

**Enjoy your Weather Display App!**
