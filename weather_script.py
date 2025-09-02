#Imports
from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'dock')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.core.window import Window
Window.show_cursor = False

from kivy.animation import Animation
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock as KivyClock
from kivy.uix.behaviors import ButtonBehavior
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests, os, time, random, subprocess, threading, socket

#Weather icons location, update path based on your folder structure if needed
ICON_PATH = "/home/rpi/weather_app/weather_icons"

#Default cities added, add/remove cities to appear on every reboot, use same format as below!
DEFAULT_CITIES = [
    {"name": "New York City", "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
]

#Weather icons and descriptions
WEATHER_ICON = {
    0: "01", 1: "01", 2: "02", 3: "03", 45: "50", 48: "50", 51: "09", 53: "09", 55: "09",
    61: "10", 63: "10", 65: "10", 71: "13", 73: "13", 75: "13", 95: "11", 99: "11",
    80: "10", 81: "10", 82: "10"
}

WEATHER_DESC = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Heavy drizzle", 61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow", 95: "Thunderstorm", 99: "Thunderstorm+hail",
    80: "Rain showers: slight", 81: "Rain showers: moderate", 82: "Rain showers: violent"
}

#Fetch forecast via free open-meteo api
def fetch_forecast(lat, lon):
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,weathercode&daily=temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset"
            "&current_weather=true&timezone=auto",
            timeout=5
        ).json()
        current = r.get("current_weather", {})
        tz = r.get("timezone", "UTC")
        daily = [{
            "date": d,
            "temp_max": r["daily"]["temperature_2m_max"][i],
            "temp_min": r["daily"]["temperature_2m_min"][i],
            "weathercode": r["daily"]["weathercode"][i],
            "sunrise": r["daily"]["sunrise"][i],
            "sunset": r["daily"]["sunset"][i]
        } for i, d in enumerate(r["daily"]["time"][:5])]
        hourly = [{"time": r["hourly"]["time"][i],
                   "temp": r["hourly"]["temperature_2m"][i],
                   "weathercode": r["hourly"]["weathercode"][i]}
                  for i in range(len(r["hourly"]["time"]))]

        return daily, current, hourly, tz
    except:
        return [], {}, [], "UTC"

def search_city(name):
    try:
        return requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count=5", timeout=5).json().get("results", [])
    except:
        return []

#Big Clock Card:
class ClockSlide(BoxLayout):
    def __init__(self, carousel, **kw):
        super().__init__(orientation='vertical', **kw)
        self.carousel = carousel
        self.padding = 50
        self.spacing = 20

        #Clock display
        self.clock_label = Label(font_size=240, color=(1, 1, 1, 1), halign='center', size_hint=(1, None), height=240)
        self.date_label = Label(font_size=30, color=(1, 1, 1, 1), halign='center', size_hint=(1, None), height=30)
        
        #Adding widgets in the proper order
        self.add_widget(BoxLayout(size_hint_y=1))
        self.add_widget(self.clock_label)
        self.add_widget(BoxLayout(size_hint_y=None, height=10))
        self.add_widget(self.date_label)
        self.add_widget(BoxLayout(size_hint_y=1))

        #Schedule to update clock in seconds (2 seconds setup to reduce pc load)
        KivyClock.schedule_interval(self.update_clock, 2)

    def update_clock(self, dt):
        wifi_available = self.check_wifi()
        
        weather_cards = [s for s in self.carousel.slides if isinstance(s, WeatherCard)]
        
		#Use timezone of first weather card
        if wifi_available and weather_cards:
            now = datetime.now(weather_cards[0].timezone)
        else:
            now = datetime.now() #Fallback to system/network time

        self.clock_label.text = now.strftime("%H:%M")
        self.date_label.text = now.strftime("%A, %d.%m")
    
    def check_wifi(self):
        try:

            socket.create_connection(("1.1.1.1", 53), timeout=1)
            return True
        except OSError:
            return False

#Weather card
REFRESH_INTERVAL = 1800  # 30 minutes

class WeatherCard(BoxLayout):
    def __init__(self, city, **kw):
        super().__init__(orientation="vertical", **kw)
        self.city = city
        self.last_forecast = []
        self.timezone = ZoneInfo(city.get("timezone", "UTC"))

        self.time_offset = datetime.now(self.timezone).utcoffset()
        self.padding = [10] * 4
        self.spacing = 10

        top = BoxLayout(orientation='horizontal', size_hint_y=None, height=200, spacing=5)
        self.today_icon = Image(size_hint=(None, None), size=(140, 160), allow_stretch=True, keep_ratio=True)
        top.add_widget(self.today_icon)

        ci = BoxLayout(orientation='vertical', size_hint=(None, 1), width=300)
        self.city_label = Label(text=city["name"], font_size=40, size_hint_y=None, height=50)
        self.temp_label = Label(font_size=24, size_hint_y=None, height=30)
        self.code_label = Label(font_size=24, size_hint_y=None, height=30)

        update_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)
        self.update_label = Label(font_size=24)
        refresh_btn = Button(text="R", size_hint=(None, 1), width=50, font_size=24,
                             background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1))
        refresh_btn.bind(on_press=lambda i: self._safe_update_weather())
        update_box.add_widget(self.update_label)
        update_box.add_widget(refresh_btn)

        for w in [self.city_label, self.temp_label, self.code_label, update_box]:
            ci.add_widget(w)
        top.add_widget(ci)
        top.add_widget(BoxLayout(size_hint_x=1))

        clock_box = BoxLayout(orientation='vertical', size_hint=(None, 1), width=200, spacing=5)
        self.clock_label = Label(font_size=72)
        self.date_label = Label(font_size=30)
        clock_box.add_widget(BoxLayout(size_hint_y=2))
        clock_box.add_widget(Label(size_hint_y=None, height=2))
        clock_box.add_widget(self.clock_label)
        clock_box.add_widget(Label(size_hint_y=None, height=20))
        clock_box.add_widget(self.date_label)
        clock_box.add_widget(BoxLayout(size_hint_y=1))
        top.add_widget(clock_box)

        self.add_widget(top)
        self.add_widget(BoxLayout(size_hint_y=1))

        self.hourly_box = ScrollView(size_hint_y=None, height=120, do_scroll_x=False, do_scroll_y=False)
        self.hourly_layout = BoxLayout(orientation="horizontal", size_hint_x=None, spacing=5)
        self.hourly_layout.bind(minimum_width=self.hourly_layout.setter('width'))
        self.hourly_box.add_widget(self.hourly_layout)
        self.add_widget(self.hourly_box)

        self.forecast_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=140)
        self.add_widget(self.forecast_box)

        self.update_weather()
        KivyClock.schedule_interval(lambda dt: self.update_clock(), 2)
        KivyClock.schedule_interval(lambda dt: self._safe_update_weather(), REFRESH_INTERVAL)

    def update_clock(self):
        try:
            #Check if online
            try:
                socket.create_connection(("1.1.1.1", 53), timeout=1)
                #When online, update from timezone and store offset
                now = datetime.now(self.timezone)
                self.time_offset = now.utcoffset()
            except OSError:
                
				#When offline, use stored offset
                utc_now = datetime.now(timezone.utc)
                now = utc_now + self.time_offset

            self.clock_label.text = now.strftime("%H:%M")
            self.date_label.text = now.strftime("%A, %d.%m")
        except Exception as e:
            print(f"Clock update error: {e}")
            
			#Fallback to stored offset
            try:
                utc_now = datetime.now(timezone.utc)
                now = utc_now + self.time_offset
                self.clock_label.text = now.strftime("%H:%M")
                self.date_label.text = now.strftime("%A, %d.%m")
            except Exception as e2:
                print(f"Fallback clock update error: {e2}")

    #Safe refresh: only updates if Wi-Fi is available
    def _safe_update_weather(self):
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=1)
            wifi_on = True
        except OSError:
            wifi_on = False

        if wifi_on:
            self.update_weather()
            #Show all widgets normally
            self.temp_label.opacity = 1
            self.code_label.opacity = 1
            self.update_label.opacity = 1
            self.clock_label.opacity = 1
            self.date_label.opacity = 1
            self.hourly_box.opacity = 1
            self.forecast_box.opacity = 1
        else:
            #Offline: hide everything except city, clock, and last update
            self.temp_label.opacity = 0
            self.code_label.opacity = 0
            self.update_label.opacity = 1
            self.clock_label.opacity = 1
            self.date_label.opacity = 1
            self.hourly_box.opacity = 0
            self.forecast_box.opacity = 0

    def update_weather(self):
        f, c, h, tz = fetch_forecast(self.city["lat"], self.city["lon"])
        self.timezone = ZoneInfo(tz)
        if f:
            self.last_forecast = f
            today = f[0]
            cur_code = c.get("weathercode", today.get("weathercode", 0))
            cur_temp = c.get("temperature", today.get("temp_max", ""))
        else:
            today = {}
            cur_code = 0
            cur_temp = ""

        #Day/Night icon logic for current weather
        current_time = datetime.now(self.timezone).hour
        icon_path = os.path.join(ICON_PATH, WEATHER_ICON.get(cur_code, "01") +
                                 ("d" if 6 <= current_time < 18 else "n") + ".png")
        self.today_icon.source = icon_path if os.path.exists(icon_path) else os.path.join(ICON_PATH, "01d.png")
        
        self.temp_label.text = f"{int(cur_temp)}°C" if isinstance(cur_temp, (int, float)) else cur_temp
        self.code_label.text = WEATHER_DESC.get(cur_code, f"Code {cur_code}")
        self.update_label.text = f"Last Update: {datetime.now(self.timezone).strftime('%H:%M')}"

        #Hourly forecast
        self.hourly_layout.clear_widgets()
        now = datetime.now(self.timezone)
        start_index = 0
        for i, hh in enumerate(h):
            if "time" in hh:
                dt = datetime.fromisoformat(hh["time"]).replace(tzinfo=self.timezone)
                if dt > now:
                    start_index = i
                    break

        for hh in h[start_index:start_index + 9]:
            if "time" in hh:
                dt = datetime.fromisoformat(hh["time"]).replace(tzinfo=self.timezone)
                b = BoxLayout(orientation="vertical", size_hint=(None, 1), width=80)
                hh_hour = dt.hour
                ip = os.path.join(ICON_PATH, WEATHER_ICON.get(hh["weathercode"], "01") +
                                  ("d" if 6 <= hh_hour < 18 else "n") + ".png")
                b.add_widget(Label(text=f"{int(hh['temp'])}°C", size_hint_y=None, height=30, font_size=16))
                b.add_widget(Image(source=ip if os.path.exists(ip) else os.path.join(ICON_PATH, "01d.png"),
                                   size_hint_y=None, height=60, allow_stretch=True, keep_ratio=True))
                b.add_widget(Label(text=dt.strftime("%H:%M"), size_hint_y=None, height=30, font_size=16))
                self.hourly_layout.add_widget(b)

        #5-day forecast
        self.forecast_box.clear_widgets()
        for d in f:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            b = BoxLayout(orientation="vertical", size_hint=(1, 1))
            ip = os.path.join(ICON_PATH, WEATHER_ICON.get(d["weathercode"], "01") + "d.png")
            b.add_widget(Image(source=ip if os.path.exists(ip) else os.path.join(ICON_PATH, "01d.png"),
                               size_hint_y=None, height=100, allow_stretch=True, keep_ratio=True))
            b.add_widget(Label(text=dt.strftime("%a"), size_hint_y=None, height=30))
            b.add_widget(Label(text=f"{int(d['temp_max'])}°C/{int(d['temp_min'])}°C", size_hint_y=None, height=30))
            self.forecast_box.add_widget(b)
			
#Photo Slide card
class PhotoSlide(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 0
        self.spacing = 0

        #Set black background
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.pics_folder = "/home/rpi/pictures/"
        self.images = [os.path.join(self.pics_folder, f) for f in os.listdir(self.pics_folder)
                       if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        self.image_widget = Image(allow_stretch=True, keep_ratio=True)
        self.add_widget(self.image_widget)

        #Show first random image immediately
        self.show_random_image(initial=True)

        #Auto-change every 60 minutes
        KivyClock.schedule_interval(lambda dt: self.show_random_image(), 3600)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def show_random_image(self, initial=False):
        if not self.images:
            return
        new_source = random.choice(self.images)
        self.image_widget.source = new_source
        self.image_widget.opacity = 1

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.show_random_image()
            return True
        return super().on_touch_down(touch)

#Manage Cities card
class ManageCitiesCard(BoxLayout):
    def __init__(self, carousel, **kw):
        super().__init__(orientation="horizontal", **kw)
        self.carousel = carousel

        #Left side: Add City
        l = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        add_btn = Button(text="+", font_size=120, size_hint=(1, 0.5))
        add_btn.bind(on_press=self.show_add_city_popup)
        l.add_widget(add_btn)
        l.add_widget(Label(text="Add City", font_size=40, size_hint_y=None, height=60))
        self.add_widget(l)

        #Right side: Remove Cities
        r = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        r.add_widget(Label(text="Remove Cities", font_size=40, size_hint_y=None, height=60))
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        r.add_widget(self.scroll)
        self.add_widget(r)

        self.refresh_city_list()

    def refresh_city_list(self):
        self.grid.clear_widgets()
        for c in DEFAULT_CITIES:
            b = BoxLayout(orientation="horizontal", size_hint_y=None, height=60)
            lbl = Label(text=c["name"], font_size=32)
            btn = Button(text="X", size_hint_x=None, width=60, font_size=32)
            btn.bind(on_press=lambda i, cc=c: self.remove_city(cc))
            b.add_widget(lbl)
            b.add_widget(btn)
            self.grid.add_widget(b)

    def remove_city(self, c):
        if c in DEFAULT_CITIES:
            DEFAULT_CITIES.remove(c)

        #Remove corresponding WeatherCard from carousel
        for slide in list(self.carousel.slides):
            if isinstance(slide, WeatherCard) and slide.city == c:
                self.carousel.remove_widget(slide)
                break

        self.refresh_city_list()

    def show_add_city_popup(self, instance):
        if len(DEFAULT_CITIES) >= 10:
            self.show_warning_popup("City list is full. Cannot add more cities.")
            return

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        ti = TextInput(hint_text="Type city name", multiline=False, font_size=32, size_hint_y=None, height=50)
        btn = Button(text="Search", size_hint_y=None, height=50)
        layout.add_widget(ti)
        layout.add_widget(btn)
        popup = Popup(title="Add New City", content=layout, size_hint=(0.8, 0.5))
        popup.open()
        btn.bind(on_press=lambda i: self._search_city(ti, popup))

    def _search_city(self, ti, popup):
        results = search_city(ti.text.strip())
        if results:
            popup.dismiss()
            self.show_city_choices(results)
        else:
            ti.text = ""
            ti.hint_text = "No matches found"

    def show_city_choices(self, results):
        layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))
        for res in results:
            btn = Button(text=f"{res.get('name', '')}, {res.get('country', '')}", size_hint_y=None, height=60)
            btn.bind(on_press=lambda i, r=res, b=btn: self._add_city(r, b))
            layout.add_widget(btn)
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(layout)
        Popup(title="Select City", content=scroll, size_hint=(0.8, 0.6)).open()

    def _add_city(self, r, btn):
        try:
            #Enforce city limit
            if len(DEFAULT_CITIES) >= 10:
                self.show_warning_popup("City list is full. Cannot add more cities.")
                return

            city_name = r.get('name', 'Unknown')
            city_country = r.get('country', '')

            #Avoid duplicates
            exists = any(
                city["name"] == city_name and city.get("country", "") == city_country
                for city in DEFAULT_CITIES
            )
            if exists:
                self.show_warning_popup(f"{city_name}, {city_country} is already added.")
                return

            tz = r.get("timezone") or "UTC"
            lat = r.get('latitude', 0)
            lon = r.get('longitude', 0)
            new_city = {
                "name": city_name,
                "lat": lat,
                "lon": lon,
                "timezone": tz,
                "country": city_country
            }

            DEFAULT_CITIES.append(new_city)

            #Insert WeatherCard before ManageCitiesCard
            manage_index = next((i for i, s in enumerate(self.carousel.slides)
                                 if isinstance(s, ManageCitiesCard)), len(self.carousel.slides))
            try:
                wc = WeatherCard(new_city)
                self.carousel.add_widget(wc, index=manage_index)
            except Exception as e:
                print("Failed to create WeatherCard:", e)

            btn.background_color = (0, 1, 0, 1)
            self.refresh_city_list()

        except Exception as e:
            print("Error in _add_city:", e)
            self.show_warning_popup(f"Could not add city: {e}")

    def show_warning_popup(self, message):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        lbl = Label(text=message, font_size=32, size_hint_y=None, height=50)
        btn = Button(text="OK", size_hint_y=None, height=50)
        layout.add_widget(lbl)
        layout.add_widget(btn)
        popup = Popup(title="Warning", content=layout, size_hint=(0.8, 0.5))
        popup.open()
        btn.bind(on_press=popup.dismiss)

#Shutdown,Reboot,Wifi card
class ShutdownRebootTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 90
        self.spacing = 50

        #Store current network info
        self.current_network = self.get_current_network()

        #Top row: Shutdown, Reboot buttons
        top_row = BoxLayout(size_hint_y=None, height=100)
        self.shutdown_button = Button(
            text="Shutdown", 
            font_size=40, 
            background_color=(1, 0, 0, 1),
            size_hint=(0.5, 1),
            pos_hint={'top': 1, 'right': 1}
        )
        self.reboot_button = Button(
            text="Reboot", 
            font_size=40, 
            background_color=(0, 1, 0, 1),
            size_hint=(0.5, 1),
            pos_hint={'top': 1, 'left': 0}
        )
        self.shutdown_button.bind(on_press=self.shutdown_device)
        self.reboot_button.bind(on_press=self.reboot_device)
        top_row.add_widget(self.reboot_button)
        top_row.add_widget(self.shutdown_button)
        self.add_widget(top_row)

        self.add_widget(BoxLayout())

        #Bottom row: WiFi controls
        bottom_row = BoxLayout(size_hint_y=None, height=100)
        self.wifi_on = Button(
            text="Wi-Fi ON",
            size_hint=(0.3, 1),
            pos_hint={'bottom': 1, 'left': 0}
        )
        self.scan_btn = Button(
            text="Scan Networks",
            size_hint=(0.4, 1),
            pos_hint={'bottom': 1, 'center_x': 0.5}
        )
        self.wifi_off = Button(
            text="Wi-Fi OFF",
            size_hint=(0.3, 1),
            pos_hint={'bottom': 1, 'right': 1}
        )
        
        self.wifi_on.bind(on_press=lambda x: self.toggle_wifi(True))
        self.wifi_off.bind(on_press=lambda x: self.toggle_wifi(False))
        self.scan_btn.bind(on_press=self.show_networks_popup)
        
        bottom_row.add_widget(self.wifi_on)
        bottom_row.add_widget(self.scan_btn)
        bottom_row.add_widget(self.wifi_off)
        self.add_widget(bottom_row)

    def get_current_network(self):
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'device', 'wifi'],
                                 capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if line.startswith('yes:'):
                    return line.split(':')[1]
        except:
            return None
        return None

    def show_networks_popup(self, instance):

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        current_net = self.get_current_network()
        if current_net:
            current_label = Label(
                text=f"Connected to: {current_net}",
                size_hint_y=None,
                height=40,
                color=(0, 1, 0, 1)
            )
            content.add_widget(current_label)

        #Network list
        scroll = ScrollView(size_hint=(1, 0.9))
        network_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        network_layout.bind(minimum_height=network_layout.setter('height'))

        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'device', 'wifi', 'list'],
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                networks = result.stdout.strip().split('\n')
                for network in networks:
                    if ':' in network:
                        parts = network.split(':')
                        if len(parts) >= 3 and parts[0]:
                            ssid, signal, security = parts[0], parts[1], parts[2]
                            
                            #Network button with info
                            net_box = BoxLayout(size_hint_y=None, height=50, spacing=5)
                            btn_text = f"{ssid} ({signal}%) {'Locked' if security else 'Free'}"
                            btn = Button(
                                text=btn_text,
                                size_hint=(0.7, 1),
                                background_color=(0, 1, 0, 0.3) if ssid == current_net else (1, 1, 1, 1)
                            )
                            btn.bind(on_press=lambda x, s=ssid: self.show_connection_popup(s))
                            net_box.add_widget(btn)
                            network_layout.add_widget(net_box)

        except Exception as e:
            print(f"Error scanning networks: {e}")
            network_layout.add_widget(Label(text="Failed to scan networks"))

        scroll.add_widget(network_layout)
        content.add_widget(scroll)

        rescan_btn = Button(
            text="Rescan",
            size_hint_y=None,
            height=40
        )
        content.add_widget(rescan_btn)

        popup = Popup(
            title='Available Networks',
            content=content,
            size_hint=(0.8, 0.8)
        )

        rescan_btn.bind(on_press=lambda x: (popup.dismiss(), self.show_networks_popup(None)))
        
        popup.open()

    def show_connection_popup(self, ssid):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        current_net = self.get_current_network()
        is_current = ssid == current_net
        
        content.add_widget(Label(text=f"{'Currently connected to' if is_current else 'Connect to'} {ssid}"))
        
        if not is_current:
            password_box = BoxLayout(size_hint_y=None, height=40)
            self.password_input = TextInput(
                password=True,
                multiline=False,
                hint_text='Enter Password',
                size_hint=(0.8, 1)
            )
            show_pass_btn = Button(
                text='Show',
                size_hint=(0.2, 1)
            )
            show_pass_btn.bind(on_press=self.toggle_password_visibility)
            password_box.add_widget(self.password_input)
            password_box.add_widget(show_pass_btn)
            content.add_widget(password_box)
        
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        if is_current:

            disconnect_btn = Button(text='Disconnect')
            disconnect_btn.bind(on_press=lambda x: self.disconnect_network(ssid, popup))
            btn_box.add_widget(disconnect_btn)
        else:

            connect_btn = Button(text='Connect')
            connect_btn.bind(on_press=lambda x: self.connect_to_network(ssid, self.password_input.text if hasattr(self, 'password_input') else '', popup))
            btn_box.add_widget(connect_btn)
        
        forget_btn = Button(text='Forget')
        forget_btn.bind(on_press=lambda x: self.forget_network(ssid, popup))
        cancel_btn = Button(text='Cancel')
        
        popup = Popup(
            title='Network Options',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        btn_box.add_widget(forget_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        
        popup.open()

    def toggle_password_visibility(self, instance):
        self.password_input.password = not self.password_input.password
        instance.text = 'Hide' if not self.password_input.password else 'Show'

    def connect_to_network(self, ssid, password, popup):
        try:
            if password:
                result = subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                                     capture_output=True, text=True)
            else:
                result = subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid],
                                     capture_output=True, text=True)
            
            if result.returncode == 0:
                popup.dismiss()
                self.show_popup(f"Connected to {ssid}")
                self.current_network = ssid
            else:
                self.show_popup(f"Failed to connect: {result.stderr}")
        except Exception as e:
            self.show_popup(f"Connection error: {str(e)}")
            print(f"Connection error: {e}")

    def disconnect_network(self, ssid, popup):
        try:
            result = subprocess.run(['sudo', 'nmcli', 'device', 'disconnect', 'wlan0'],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                popup.dismiss()
                self.show_popup(f"Disconnected from {ssid}")
                self.current_network = None
            else:
                self.show_popup(f"Failed to disconnect: {result.stderr}")
        except Exception as e:
            self.show_popup(f"Failed to disconnect: {str(e)}")
            print(f"Disconnect error: {e}")

    def forget_network(self, ssid, popup=None):
        try:
            result = subprocess.run(['sudo', 'nmcli', 'connection', 'delete', ssid],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                if popup:
                    popup.dismiss()
                self.show_popup(f"Forgot network {ssid}")
                if self.current_network == ssid:
                    self.current_network = None
            else:
                self.show_popup(f"Failed to forget network: {result.stderr}")
        except Exception as e:
            self.show_popup(f"Failed to forget network: {str(e)}")
            print(f"Forget network error: {e}")

    def toggle_wifi(self, enable=True):
        try:
            if enable:
                subprocess.run(['sudo', 'nmcli', 'radio', 'wifi', 'on'])
                subprocess.run(['sudo', 'rfkill', 'unblock', 'wifi'])
                self.show_popup("Wi-Fi Enabled")
                KivyClock.schedule_once(lambda dt: self.show_networks_popup(None), 2)
            else:
                subprocess.run(['sudo', 'nmcli', 'radio', 'wifi', 'off'])
                subprocess.run(['sudo', 'rfkill', 'block', 'wifi'])
                self.show_popup("Wi-Fi Disabled")
                self.current_network = None
        except Exception as e:
            print(f"Error toggling WiFi: {e}")
            self.show_popup(f"Failed to {'enable' if enable else 'disable'} Wi-Fi")

    def shutdown_device(self, instance):
        subprocess.run(["sudo", "shutdown", "now"])

    def reboot_device(self, instance):
        subprocess.run(["sudo", "reboot"])

    def show_popup(self, message):
        popup = Popup(
            title="Info",
            content=Label(text=message),
            size_hint=(0.6, 0.4)
        )
        popup.open()

        KivyClock.schedule_once(lambda dt: popup.dismiss(), 2)
		
#Weather Display App
class WeatherDisplayApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.2, 1)
        self.root_layout = FloatLayout()
        self.carousel = Carousel(direction="right", size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.root_layout.add_widget(self.carousel)

        self.locked = False
        self.lock_label = None
        self.last_touch_time = 0

        #Add PhotoSlide first
        self.carousel.add_widget(PhotoSlide())

        #Main slides
        self.clock_slide = ClockSlide(self.carousel)
        self.carousel.add_widget(self.clock_slide)

        #Add default cities to the carousel
        [self.carousel.add_widget(WeatherCard(cit)) for cit in DEFAULT_CITIES]

        #Add the city management card
        self.carousel.add_widget(ManageCitiesCard(self.carousel))

        #Add the Shutdown, Reboot tab
        self.carousel.add_widget(ShutdownRebootTab())

        #Lock detection
        Window.bind(on_touch_down=self.on_touch_down)

        #Auto weather refresh
        KivyClock.schedule_interval(lambda dt: [s.update_weather() for s in self.carousel.slides if isinstance(s, WeatherCard)], REFRESH_INTERVAL)

        return self.root_layout

    def on_touch_down(self, window, touch):
        if isinstance(self.carousel.slides[self.carousel.index], ManageCitiesCard):
            return False
        
        now = time.time()
        if now - getattr(self, "last_touch_time", 0) < 0.1:
            if self.locked:
                self.unlock_screen()
            else:
                self.lock_screen()
        self.last_touch_time = now
        if self.locked and self.lock_label:
            self.lock_label.opacity = 1
            KivyClock.schedule_once(self.hide_lock_label, 10)
        return self.locked

    def lock_screen(self):
        if not self.locked:
            self.locked = True
            if not self.lock_label:
                self.lock_label = Label(
                    text="Double tap to unlock",
                    font_size=24,
                    size_hint=(1, None),
                    height=50,
                    pos_hint={"top": 1},
                    color=(1, 1, 1, 0.8)
                )
                self.root_layout.add_widget(self.lock_label)
            else:
                self.lock_label.opacity = 1
            KivyClock.schedule_once(self.hide_lock_label, 10)

    def hide_lock_label(self, dt=None):
        if self.lock_label:
            self.lock_label.opacity = 0

    def unlock_screen(self):
        if self.locked:
            self.locked = False
            if self.lock_label:
                self.root_layout.remove_widget(self.lock_label)
                self.lock_label = None

if __name__ == "__main__":
    WeatherDisplayApp().run()
