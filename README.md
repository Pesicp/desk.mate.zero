# Instructions

Download putty

Download latest rpi imager

Install rpi os lite 32,

* Edit settings - hnoiuhuoi
* hostname rpi
* username rpi
* pass your choice
* configure wlan
* set locale
* enable ssh, use pass authentication

flash sd card

boot pi and connect via putty ssh

### Update
```
  sudo apt update && sudo apt upgrade -y
````
----------------------------------------------------------------------------

6: Run
--1: sudo apt install -y python3-pip python3-setuptools python3-venv
      
--2: first run:            python3 -m venv ~/weather_app/venv
     in that window run:   source ~/weather_app/venv/bin/activate
   
--3: pip3 install kivy   

--4: pip install requests tzdata kivy

----------------------------------------------------------------------------

7: mkdir ~/weather_app
   cd ~/weather_app
   
----------------------------------------------------------------------------

8: Run: 
   sudo nano  ~/weather_app/weather_script.py

 paste the script, in putty just press left mouse and the copied content will paste, 
 then ctrl+o to save, press enter to confirm, press ctrl+x to exit
 
----------------------------------------------------------------------------

9: Fix Missing Dependencies:
 
--1: sudo apt install -y libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils

----------------------------------------------------------------------------

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

----------------------------------------------------------------------------
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

----------------------------------------------------------------------------
12: MAKE FOLDER FOR SLIDESHOW PICTURES

--1: Make the directory:

mkdir /home/rpi/pictures/

--2: You can wget pictures directly to the folder:
First change directory:

cd /home/rpi/pictures/

--3: Then download via wget:

wget YourImageURL

-----Press enter. Done! Your picture is downloading to your picture folder!
----------------------------------------------------------------------------

Now final test:
Run the script:

python ~/weather_app/weather_script.py

TO SHUTDOWN THE SCRIPT ON YOUR SSH AND RETURN TO TERMINAL PRESS CTRL+C

----------------------------------------------------------------------------
----------------------------------------------------------------------------

IF YOU EXIT YOUR SSH FOR SOME REASON 
YOU NEDD TO RUN THIS BEFORE THE SCRIPT TO ACTIVATE VENV:

    source /home/rpi/weather_app/venv/bin/activate
	
----Then you can run your script

    python ~/weather_app/weather_script.py
	
ALSO IF PUTTY DOESNT BRING YOU TO LOGIN FOR YOUR PI; JUST EXIT AND RESTART PUTTY
	
----------------------------------------------------------------------------
----------------------------------------------------------------------------

MAKE IT AUTO BOOT:
Run: 

--1:  sudo nano /etc/systemd/system/weather_app.service

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

-------------------------------------------------
Now save with ctrl+o,Then press Enter,Then Ctrl+x
-------------------------------------------------

----------------------------------------------------------------------------

NOW WE ENABLE THE SERVICE TO START ON BOOT:

sudo systemctl enable weather_app.service

----------------------------------------------------------------------------

START THE SERVICE:

sudo systemctl start weather_app.service

----------------------------------------------------------------------------

NOW RUN THIS TO VERIFY ITS RUNNING:

sudo systemctl status weather_app.service

----------------------------------------------------------------------------

NOW TEST DOES IT RUN ON BOOT:

sudo reboot

AND EXIT YOUR SSH

DEVICE SHOULD NOW BOOT IN TO THE APP

____________________________________________________________________________
____________________________________________________________________________

OPTIONAL BUT IMPORTANT: 

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


-----4: Detect your subnet automatically to allow only local devices to access rpi SSH:

SUBNET=$(ip -o -f inet addr show wlan0 | awk '/scope global/ {print $4}')

echo $SUBNET


-----5: Allow only local subnet access for SSH:

sudo ufw allow from $SUBNET to any port 22 proto tcp


-----6: Allow outgoing connections (needed for weather fetching):

sudo ufw allow out 80,443/tcp


-----7: Enable the firewall:

sudo ufw enable
sudo ufw status verbose

Confirm with y (Yes)

DONE!

----------------------------------------------------------------------------
----------------------------------------------------------------------------

AUTO UPDATE YOUR DEVICE EVERY NIGHT AT 04:00, 
If it skips update for some reason then it will update on first reboot:

----------1: Create Update Script:

sudo nano /usr/local/bin/weather_safe_update.sh


PASTE THIS INSIDE:


#!/bin/bash
# Delay to allow the weather station to fully start
sleep 60

# Check the last update timestamp
LAST_UPDATE_FILE="/var/lib/weather_last_update"

if [ ! -f "$LAST_UPDATE_FILE" ]; then
    echo "$(date +%Y-%m-%d)" > "$LAST_UPDATE_FILE"
fi

LAST_RUN=$(cat "$LAST_UPDATE_FILE")
TODAY=$(date +%Y-%m-%d)

# If last update was before today, or if script is running at scheduled time, update
if [ "$LAST_RUN" != "$TODAY" ]; then
    # ====== Perform update safely here ======
    echo "Running safe update..."
    # Example update commands:
    # git -C /home/rpi/weather_app pull
    # pip3 install --upgrade -r /home/rpi/weather_app/requirements.txt
    # Any other silent update steps
    # =======================================

    # Update the timestamp
    echo "$TODAY" > "$LAST_UPDATE_FILE"
    echo "Update finished at $(date)"
else
    echo "Already updated today, skipping."
fi


----------------------------------------------------------------------------
----------2: Make it executable:

sudo chmod +x /usr/local/bin/weather_safe_update.sh


----------------------------------------------------------------------------
----------3: Create Systemd Service

sudo nano /etc/systemd/system/weather_safe_update.service

 
PASTE THIS INSIDE:

 
[Unit]
Description=Silent safe update for Weather Pi

[Service]
Type=oneshot
ExecStart=/usr/local/bin/weather_safe_update.sh %i

----------------------------------------------------------------------------
----------4: Create Systemd Timer

sudo nano /etc/systemd/system/weather_safe_update.timer


PASTE THIS INSIDE:


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

----------------------------------------------------------------------------
----------5: Create Systemd On-Boot Timer

sudo nano /etc/systemd/system/weather_safe_update-onboot.service


PASTE THIS INSIDE:


[Unit]
Description=Run safe update on boot if missed

[Service]
Type=oneshot
ExecStart=/usr/local/bin/weather_safe_update.sh boot


----------------------------------------------------------------------------
----------6: Create a corresponding timer

sudo nano /etc/systemd/system/weather_safe_update-onboot.timer

[Unit]
Description=Trigger safe update on boot if missed

[Timer]
OnBootSec=1min
Unit=weather_safe_update-onboot.service
Persistent=true

[Install]
WantedBy=timers.target


----------------------------------------------------------------------------
----------7: Enable Timers

sudo systemctl enable --now weather_safe_update.timer
sudo systemctl enable --now weather_safe_update-onboot.timer

if the device freezes just unplug the power it and plug it again, to me it only happend once
----------------------------------------------------------------------------
DONE!!

Updates run silently every day at 04:00, if wifi is connected.
If Pi is off at 04:00 → update runs 1 min after next boot.
Weather station is never interrupted.
Only logs errors
Logs are in /home/rpi/weather_update.log.
----------------------------------------------------------------------------
