# DESK MATE ZERO
# Description
- **Picture slideshow** - New picture every 60 minutes, Picture changes on touch.
- **Fullscreen Clock** - Wifi on, it always shows time from the first weather card. Wifi off, shows time from network.
- **Weather Forecast** - Shows temp, current condition, weather, hourly 9 hours in advance, daily 5 days, and current.
  - Also shows time in selected city. When wifi is off the clock keeps ticking, the weather dissapears. Has a manual refresh button.
- **Add City** - Add and remove cities. Limit is 10 cities for better performance. Douplicates cant be added.
- **Power, Wifi** - Power off, Reboot. Turn Wifi on or off, connect, disconnect, forget networks with ease.
- Double press/touch to lock/unlock the screen, its disabled for add city card. Its set up realy fast to avoid accidental lock, 0.2 seconds. With 2 fingers it works best. 
---
# Installation Guide
I used Raspberry Pi Zero 2W and [Spotpear](https://de.aliexpress.com/item/1005004999310505.html?spm=a2g0o.productlist.main.1.343c79d0O9bxr5&algo_pvid=21ccbcee-6f60-4764-ae89-6e865c7c0ebb&algo_exp_id=21ccbcee-6f60-4764-ae89-6e865c7c0ebb-0&pdp_ext_f=%7B%22order%22%3A%22104%22%2C%22eval%22%3A%221%22%7D&pdp_npi=6%40dis%21EUR%2137.77%2127.99%21%21%2143.14%2131.97%21%4021039a5b17567712736503882e0838%2112000031298315802%21sea%21DE%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3Ad409efa6%3Bm03_new_user%3A-29895%3BpisId%3A5000000174220118&curPageLogUid=ota5QVADPla9&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005004999310505%7C_p_origin_prod%3A) RPI-Touch-Case bundle, 7 inch touchscreen. 
- All commands are designed for Raspberry Pi OS Lite (32-bit) with Python 3.
- You only need screws that comes with the touchscreen in RPI-Touch-Case bundle
- Case stl files can be found on [Printables](https://www.printables.com/model/1402602)
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
**1. Update system and install required packages**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-setuptools python3-venv python3-dbus network-manager 
    libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils
```
**2. Enable and start Network Manager** (just in case)
```
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```
---
## 3. Python Environment and App Setup
**1. Create weather_app folder and Python virtual environment**
```bash
mkdir -p ~/weather_app
python3 -m venv ~/weather_app/venv
```
**2. Activate virtual environment**
```
source ~/weather_app/venv/bin/activate
```
**3. Install Python dependencies**
```
pip install kivy requests tzdata feedparser
```
---
## 4. Script
**1. Create and edit the weather script**
```bash
nano ~/weather_app/weather_script.py
```
- **Copy the script content. You can find the script above the instructions under the name weather_script.py or go [HERE](https://github.com/Pesicp/desk.mate.zero/blob/main/weather_script.py)**
- **Paste the complete script inside, just copy it and inside terminal press right mouse to paste, save with Ctrl+O, Enter, exit with Ctrl+X**
---
## 5. Weather Icons
**1. Create icons folder**
```bash
mkdir -p ~/weather_app/weather_icons
cd ~/weather_app/weather_icons
```
**2. Download weather icons**
```
wget https://openweathermap.org/img/wn/{01d,01n,02d,02n,03d,03n,04d,04n,09d,09n,10d,10n,11d,11n,13d,13n,50d,50n}.png
```
**3. For high quality icons (optional), run:**
```
rm -rf ~/weather_app/weather_icons/*
wget https://openweathermap.org/img/wn/{01d,01n,02d,02n,03d,03n,04d,04n,09d,09n,10d,10n,11d,11n,13d,13n,50d,50n}@2x.png
for f in *@2x.png; do mv "$f" "${f/@2x/}"; done
```
---
## 6. Slideshow Pictures
**1. Create pictures folder**
```bash
mkdir -p /home/rpi/pictures/
cd /home/rpi/pictures/
```
**2. Download your pictures with wget, for example:**
```
wget https://yourpictureurl.com/image.jpg
```
**Here are some nice pictures for start**
```
wget https://images.wallpaperscraft.com/image/single/waterfall_cliff_stone_141850_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/sea_sunset_horizon_131804_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/boat_mountains_lake_135258_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/ocean_beach_aerial_view_134429_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/mountains_lake_grass_137616_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/sea_sunset_art_131736_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/autumn_forest_park_128379_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/sunflowers_field_sunset_123231_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/landscape_mountains_sun_140434_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/lake_mountains_solitude_124541_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/bench_autumn_park_125807_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/autumn_path_foliage_131773_1024x600.jpg
wget https://images.wallpaperscraft.com/image/single/tree_horizon_sunset_128367_1024x600.jpg
```
---
## 7. Run the App
**1. Activate venv (if not already active)**
```bash
source ~/weather_app/venv/bin/activate
```
**2. Run the app**
```
python ~/weather_app/weather_script.py
```
**3. To exit, press Ctrl+C in the terminal**

---
## 8. Make it Auto-Start on Boot
**1. Run:**
```bash
sudo nano /etc/systemd/system/weather_app.service
```
**2. Paste this inside, then Save and exit (Ctrl+O, Enter, Ctrl+X)**
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
**3. Enable and start the service**
```bash
sudo systemctl enable weather_app.service
sudo systemctl start weather_app.service
```
**4. Check status**
```
sudo systemctl status weather_app.service
```
**5. Reboot to test auto-start**
```
sudo reboot
```
---
## 9. Security (Optional but Recommended)
**1. Disable unneeded services**
```bash
sudo systemctl disable avahi-daemon
sudo systemctl stop avahi-daemon
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
sudo apt purge wolfram-engine libreoffice* minecraft-pi -y
sudo apt autoremove -y
```
**2. Install and configure UFW firewall**
```
sudo apt install ufw -y
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
```
**3. Allow SSH only from your local subnet**
```
SUBNET=$(ip -o -f inet addr show wlan0 | awk '/scope global/ {print $4}')
sudo ufw allow from $SUBNET to any port 22 proto tcp
```
**4. Allow outgoing traffic for weather updates**
```
sudo ufw allow out 80,443/tcp
```
**5. Enable firewall**
```
sudo ufw enable
sudo ufw status verbose
```
**Confirm with y (Yes)**
---

## 10. Auto-Update in background every night at 04:00 (Optional)
**1. Create update script**
```bash
sudo nano /usr/local/bin/weather_safe_update.sh
```
**2. Paste this inside, save and exit (Ctrl+O, Enter, Ctrl+X)**
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
**3. Make it executable**
```bash
sudo chmod +x /usr/local/bin/weather_safe_update.sh
```
**4. Create Systemd Service**
```
sudo nano /etc/systemd/system/weather_safe_update.service
```
**5. Paste this inside**
```
[Unit]
Description=Silent safe update for Weather Pi

[Service]
Type=oneshot
ExecStart=/usr/local/bin/weather_safe_update.sh %i
```
**6. Create Systemd Timer**
```
sudo nano /etc/systemd/system/weather_safe_update.timer
```
**7. Paste this inside, save and exit (Ctrl+O, Enter, Ctrl+X)**
```
[Unit]
Description=Daily timer for Weather Pi safe update

[Timer]
# Run daily at 04:00 local time
OnCalendar=*-*-* 04:00:00
# Run once after boot if missed
Persistent=true
# Add small delay on boot
AccuracySec=1min

[Install]
WantedBy=timers.target
```
**8. Create Systemd On-Boot Timer**
```
sudo nano /etc/systemd/system/weather_safe_update-onboot.service
```
**9. Paste this inside, save and exit (Ctrl+O, Enter, Ctrl+X)**
```
[Unit]
Description=Run safe update on boot if missed

[Service]
Type=oneshot
ExecStart=/usr/local/bin/weather_safe_update.sh boot
```
**10. Create a corresponding timer**
```
sudo nano /etc/systemd/system/weather_safe_update-onboot.timer
````
**11 Paste this inside, save and exit (Ctrl+O, Enter, Ctrl+X)**
```
[Unit]
Description=Trigger safe update on boot if missed

[Timer]
OnBootSec=1min
Unit=weather_safe_update-onboot.service
Persistent=true

[Install]
WantedBy=timers.target
```
**12. Enable Timers**
```
sudo systemctl enable --now weather_safe_update.timer
sudo systemctl enable --now weather_safe_update-onboot.timer
```
**if the device freezes just unplug the power it and plug it again, to me it only happend once**
- Updates run silently every day at 04:00, if wifi is connected.
- If Pi is off at 04:00 → update runs 1 min after next boot.
- Weather station is never interrupted.
---
## Troubleshooting
- **If the device freezes, unplug and replug power**
- **If you exit SSH for some reason, you must run this first to activate venv**
```
source /home/rpi/weather_app/venv/bin/activate
```	
- **Then you can run your script again**
```
python ~/weather_app/weather_script.py
```	
- **If Putty doesnt show you login screen just restart it**
---
# I made this with help of ai, i am a hobyst not a programmer, if you have some tips to optimise the script and the setup, be my guest.
# **Enjoy**
