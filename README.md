

Raspberry Pi Weather Display Setup
1️⃣ Initial Setup

1: download putty and latest rpi imager, install rpi os lite 32,
2: edit settings: hostname rpi, username rpi, pass your choice
    configure wlan
    set locale
    services: enable ssh, use pass authentication
3: flash sd card
4: boot pi and connect via putty ssh

2️⃣ Update System

5: update

sudo apt update && sudo apt upgrade -y

3️⃣ Python Setup

6: Run
--1: sudo apt install -y python3-pip python3-setuptools python3-venv

--2: first run: python3 -m venv ~/weather_app/venv
    in that window run: source ~/weather_app/venv/bin/activate

--3: pip3 install kivy

--4: pip install requests tzdata kivy

4️⃣ Create Weather App Folder

7: mkdir ~/weather_app
    cd ~/weather_app

5️⃣ Add Weather Script

8: Run:

sudo nano  ~/weather_app/weather_script.py


paste the script, in putty just press left mouse and the copied content will paste,
then ctrl+o to save, press enter to confirm, press ctrl+x to exit

6️⃣ Fix Missing Dependencies

9: Fix Missing Dependencies:
--1: sudo apt install -y libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils

7️⃣ Import Weather Icons
Standard Icons

11: We need to import weather icons
Run:
--1: cd ~/weather_app
    mkdir -p weather_icons
    cd weather_icons

--2: Download icons:

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

High-Quality Icons (Optional)

IF YOU WANT BETTER QUALITY ICONS USE THIS:
BUT YOU MUST RENAME THEM SAME LIKE THE ONES ABOVE SO THE SCRIPT WORKS,

--1: Change to folder if not allready:

cd ~/weather_app/weather_icons


--2: Delete all files from the folder:

rm -rf ~/weather_app/weather_icons/*


--3: Download high quality icons

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


--4: Auto rename all icons in folder:

for f in ~/weather_app/weather_icons/*@2x*.png; do [ -f "$f" ] && mv -v "$f" "${f//@2x/}"; done

8️⃣ Slideshow Pictures

12: MAKE FOLDER FOR SLIDESHOW PICTURES

--1: Make the directory:

mkdir /home/rpi/pictures/


--2: You can wget pictures directly to the folder:
First change directory:

cd /home/rpi/pictures/


--3: Then download via wget:

wget YourImageURL


-----Press enter. Done! Your picture is downloading to your picture folder!

9️⃣ Run the Script

Now final test:

python ~/weather_app/weather_script.py


TO SHUTDOWN THE SCRIPT ON YOUR SSH AND RETURN TO TERMINAL PRESS CTRL+C

IF YOU EXIT YOUR SSH FOR SOME REASON
YOU NEDD TO RUN THIS BEFORE THE SCRIPT TO ACTIVATE VENV:

source /home/rpi/weather_app/venv/bin/activate


----Then you can run your script

python ~/weather_app/weather_script.py


ALSO IF PUTTY DOESNT BRING YOU TO LOGIN FOR YOUR PI; JUST EXIT AND RESTART PUTTY

🔟 Auto-Boot Weather App

MAKE IT AUTO BOOT:
--1: sudo nano /etc/systemd/system/weather_app.service

paste this inside:

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


Now save with ctrl+o,Then press Enter,Then Ctrl+x

Enable the service to start on boot:

sudo systemctl enable weather_app.service


Start the service:

sudo systemctl start weather_app.service


Verify it’s running:

sudo systemctl status weather_app.service


Test boot:

sudo reboot


AND EXIT YOUR SSH
DEVICE SHOULD NOW BOOT IN TO THE APP

⚡ Optional but Important

-----1: Disable unneeded services:

sudo systemctl disable avahi-daemon
sudo systemctl stop avahi-daemon
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
sudo apt purge wolfram-engine libreoffice* minecraft-pi -y
sudo apt autoremove -y


-----2: Install Firewall:

sudo apt update
sudo apt install ufw -y


-----3: Reset Firewall to defaults:

sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing


-----4: Detect your subnet automatically:

SUBNET=$(ip -o -f inet addr show wlan0 | awk '/scope global/ {print $4}')
echo $SUBNET


-----5: Allow only local subnet access for SSH:

sudo ufw allow from $SUBNET to any port 22 proto tcp


-----6: Allow outgoing connections:

sudo ufw allow out 80,443/tcp


-----7: Enable firewall:

sudo ufw enable
sudo ufw status verbose

🕒 Auto Update Every Night at 04:00
1: Create Update Script
sudo nano /usr/local/bin/weather_safe_update.sh


Paste the script exactly as provided in your instructions (see original).

2: Make it executable
sudo chmod +x /usr/local/bin/weather_safe_update.sh

3–7: Create Systemd Services and Timers

Follow your original instructions exactly to create:

weather_safe_update.service

weather_safe_update.timer

weather_safe_update-onboot.service

weather_safe_update-onboot.timer

Enable timers:

sudo systemctl enable --now weather_safe_update.timer
sudo systemctl enable --now weather_safe_update-onboot.timer


If the device freezes just unplug the power it and plug it again, to me it only happend once

DONE!!
Updates run silently every day at 04:00, if wifi is connected.
If Pi is off at 04:00 → update runs 1 min after next boot.
Weather station is never interrupted.
Only logs errors
Logs are in /home/rpi/weather_update.log.
