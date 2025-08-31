# Raspberry Pi Weather Clock / Slideshow Setup

## 1. Prepare Tools & OS
1. Download **Putty** and the latest **Raspberry Pi Imager**.
2. Install **Raspberry Pi OS Lite 32-bit**.
3. Edit settings:
   - Hostname: `rpi`
   - Username: `rpi`
   - Password: your choice
   - Configure WLAN
   - Set locale
   - Services: enable SSH, use password authentication
4. Flash SD card.
5. Boot Pi and connect via Putty SSH.

---

## 2. Update System
bash
sudo apt update && sudo apt upgrade -y
