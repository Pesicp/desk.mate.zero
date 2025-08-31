markdown
1. Prepare Your SD Card

Download Raspberry Pi Imager
 and PuTTY.

Flash Raspberry Pi OS Lite 32-bit.

Configure settings before flashing:

Hostname: rpi

Username: rpi

Password: your choice

Configure Wi-Fi

Set locale

Enable SSH and password authentication

Flash the SD card and boot your Pi.

Connect via SSH using PuTTY.

2. Update Your Pi
sudo apt update && sudo apt upgrade -y

3. Install Python & Kivy
sudo apt install -y python3-pip python3-setuptools python3-venv


Create virtual environment:

python3 -m venv ~/weather_app/venv
source ~/weather_app/venv/bin/activate


Install dependencies:

pip install kivy requests tzdata

4. Create Weather App Folder
mkdir ~/weather_app
cd ~/weather_app

5. Add Your Weather Script
sudo nano ~/weather_app/weather_script.py


Paste your script.

Save with Ctrl+O, Enter, then exit Ctrl+X.

6. Fix Missing Dependencies
sudo apt install -y libmtdev1 libxrender1 libgles2-mesa libegl1-mesa libgl1-mesa-glx libsdl2-dev mesa-utils

7. Import Weather Icons

Create icon folder:

cd ~/weather_app
mkdir -p weather_icons
cd weather_icons


Download icons:

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


Optional: For high-quality icons, download @2x versions and rename:

for f in ~/weather_app/weather_icons/*@2x*.png; do
    [ -f "$f" ] && mv -v "$f" "${f//@2x/}"
done

8. Add Slideshow Pictures
mkdir /home/rpi/pictures
cd /home/rpi/pictures
wget <YourImageURL>

9. Run Your Script
source ~/weather_app/venv/bin/activate
python ~/weather_app/weather_script.py


Stop script: Ctrl+C.

10. Auto-Run on Boot

Create service:

sudo nano /etc/systemd/system/weather_app.service


Paste:

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


Enable service:

sudo systemctl enable weather_app.service
sudo systemctl start weather_app.service
sudo systemctl status weather_app.service


Test reboot:

markdown
sudo reboot
markdown

11. Optional System Cleanup & Firewall
sudo systemctl disable avahi-daemon bluetooth
sudo systemctl stop avahi-daemon bluetooth
sudo apt purge wolfram-engine libreoffice* minecraft-pi -y
sudo apt autoremove -y

sudo apt install ufw -y
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
SUBNET=$(ip -o -f inet addr show wlan0 | awk '/scope global/ {print $4}')
sudo ufw allow from $SUBNET to any port 22 proto tcp
sudo ufw allow out 80,443/tcp
sudo ufw enable
sudo ufw status verbose

12. Auto Update Every Night at 04:00

Create update script:

sudo nano /usr/local/bin/weather_safe_update.sh


Paste your update logic. Make executable:

sudo chmod +x /usr/local/bin/weather_safe_update.sh


Create services & timers as described in your instructions. Enable timers:

sudo systemctl enable --now weather_safe_update.timer
sudo systemctl enable --now weather_safe_update-onboot.timer
