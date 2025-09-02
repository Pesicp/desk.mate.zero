# DESK MATE ZERO
# Description

- **Picture slideshow** - New picture every 60 minutes, Picture changes on touch.
- **Fullscreen Clock** - Wifi on, it always shows time from the first weather card. Wifi off, shows time from network.
- **Weather Forecast** - Shows temp, current condition, weather, hourly 9 hours in advance, daily 5 days, and current. Also shows time in selected city. When wifi is off the clock keeps ticking, the weather dissapears. Has a refresh button for manual refresh.
- **Add City** - Add and remove cities. Limit is 10 cities for better performance. Douplicates cant be added.
- **Power, Wifi** - Power off, Reboot. Turn Wifi on or off, connect, disconnect, forget networks with ease.
- Double press/touch to lock/unlock the screen, its disabled for add city card. Its set up realy fast to avoid accidental lock, 0.2 seconds. With 2 fingers it works best. 

---

# Installation Guide

I used Raspberry Pi Zero 2W and [Spotpear](https://de.aliexpress.com/item/1005004999310505.html?spm=a2g0o.productlist.main.1.343c79d0O9bxr5&algo_pvid=21ccbcee-6f60-4764-ae89-6e865c7c0ebb&algo_exp_id=21ccbcee-6f60-4764-ae89-6e865c7c0ebb-0&pdp_ext_f=%7B%22order%22%3A%22104%22%2C%22eval%22%3A%221%22%7D&pdp_npi=6%40dis%21EUR%2137.77%2127.99%21%21%2143.14%2131.97%21%4021039a5b17567712736503882e0838%2112000031298315802%21sea%21DE%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3Ad409efa6%3Bm03_new_user%3A-29895%3BpisId%3A5000000174220118&curPageLogUid=ota5QVADPla9&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005004999310505%7C_p_origin_prod%3A) RPI-Touch-Case bundle, 7 inch touchscreen. 
- All commands are designed for Raspberry Pi OS Lite (32-bit) with Python 3.
- You only need screws that comes with the touchscreen in RPI-Touch-Case bundle
## Case stl files can be found on [Printables](https://www.printables.com/model/1402602)

# 1. Preparation

- Download and install [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) (for SSH access).
- Download and install the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
- Using Raspberry Pi Imager:
  - Select **Raspberry Pi Other - Raspberry Pi OS Lite (32-bit)**
  - Edit settings ⚙️  **If you dont have settings icon, when you press **next** it will apear**
    - Hostname: `rpi`
    - Enable SSH (password authentication)
    - Username: `rpi` (better to leave it, as all folder structure and script is made with this username)
    - Password: `yourpassword`
    - Configure WiFi (Input name and password of your network)
    - Set country, locale, timezone, keyboard layout
  - Flash the SD card and insert into your Pi.
  - Connect your PI to the display
- Boot the Pi and connect via SSH using PuTTY.
    - If you cant connect with your username via putty, use your local ip adress, you can find it on the pi display  

---

## 2. System Setup
1. Update system and install required packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-setuptools python3-venv python3-dbus network-manager 
    libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils
```
2. Enable and start Network Manager (just in case)
```
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

---

## 3. Python Environment and App Setup
1. Create weather_app folder and Python virtual environment
```bash
mkdir -p ~/weather_app
python3 -m venv ~/weather_app/venv
```
2. Activate virtual environment
```
source ~/weather_app/venv/bin/activate
```
3. Install Python dependencies
```
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

## 9. Make it Auto-Start on Boot

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

## 11. Auto-Update in background every night at 04:00 (Optional)

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

**Enjoy**
