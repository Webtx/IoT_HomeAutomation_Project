import json
import time
import random
import threading
from datetime import datetime
from gpiozero import LED
import logging
from environmental_module import environmental_module
from security_module import security_module
from MQTT_communicator import MQTT_communicator

# -----------------------
# Logging
# -----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------
# Devices (Lab08)
# -----------------------
DEVICES = {
    'led1': {'device': LED(16), 'name': 'Yellow LED', 'state': False},
    'led2': {'device': LED(23), 'name': 'Red LED', 'state': False},
    'led3': {'device': LED(24), 'name': 'Green LED', 'state': False},
    'fan':  {'device': LED(22), 'name': 'Fan', 'state': False},
    'relay':{'device': LED(18), 'name': 'Relay', 'state': False}
}

party_mode_active = False
party_thread = None

# -----------------------
# IoT App
# -----------------------
ENV_FEEDS = {"temperature": "temperature", "humidity": "humidity", "pressure": "pressure"}
SECURITY_FEEDS = {"motion_count": "motion_feed", "smoke_count": "smoke_feed"}

class DomiSafeApp:
    def __init__(self):
        self.mqtt_agent = MQTT_communicator()
        self.env_data = environmental_module()
        self.security_data = security_module()
        self.running = True
        self.security_check_interval = 5
        self.security_send_interval = 60
        self.env_interval = 30

    def send_to_cloud(self, data, feeds):
        for k, v in feeds.items():
            if k in data:
                try:
                    self.mqtt_agent.send_to_adafruit_io(v, data[k])
                except Exception as e:
                    logger.error(f"Failed to send {k}: {e}")

    def data_loop(self):
        timers = {'env_check': 0, 'security_check': 0, 'security_send': 0}
        security_counts = {'motion': 0, 'smoke': 0}

        while self.running:
            now = time.time()

            # Environmental
            if now - timers['env_check'] >= self.env_interval:
                env = self.env_data.get_environmental_data()
                self.send_to_cloud(env, ENV_FEEDS)
                logger.info(f"Env data: {env}")
                timers['env_check'] = now

            # Security
            if now - timers['security_check'] >= self.security_check_interval:
                sec = self.security_data.get_security_data()
                if sec['motion_detected']:
                    security_counts['motion'] += 1
                if sec['smoke_detected']:
                    security_counts['smoke'] += 1
                timers['security_check'] = now

            if now - timers['security_send'] >= self.security_send_interval:
                summary = {
                    'timestamp': datetime.now().isoformat(),
                    'motion_count': security_counts['motion'],
                    'smoke_count': security_counts['smoke']
                }
                self.send_to_cloud(summary, SECURITY_FEEDS)
                logger.info(f"Security summary: {summary}")
                security_counts = {'motion': 0, 'smoke': 0}
                timers['security_send'] = now

            time.sleep(1)

    def start(self):
        t = threading.Thread(target=self.data_loop, daemon=True)
        t.start()

# -----------------------
# Device Control Functions
# -----------------------
def toggle_device(device_id):
    dev = DEVICES[device_id]
    dev['state'] = not dev['state']
    if dev['state']:
        dev['device'].on()
    else:
        dev['device'].off()
    print(f"{dev['name']} turned {'ON' if dev['state'] else 'OFF'}")

def show_status():
    for dev in DEVICES.values():
        print(f"{dev['name']}: {'ON' if dev['state'] else 'OFF'}")

def turn_all(state):
    for dev in DEVICES.values():
        dev['state'] = state
        if state:
            dev['device'].on()
        else:
            dev['device'].off()
    print(f"All devices {'ON' if state else 'OFF'}")

def party_mode():
    global party_mode_active
    leds = ['led1', 'led2', 'led3']
    while party_mode_active:
        led = random.choice(leds)
        DEVICES[led]['state'] = not DEVICES[led]['state']
        if DEVICES[led]['state']:
            DEVICES[led]['device'].on()
        else:
            DEVICES[led]['device'].off()
        time.sleep(0.2)

def toggle_party_mode():
    global party_mode_active, party_thread
    if party_mode_active:
        party_mode_active = False
        if party_thread:
            party_thread.join()
    else:
        party_mode_active = True
        party_thread = threading.Thread(target=party_mode, daemon=True)
        party_thread.start()

def cleanup():
    global party_mode_active
    party_mode_active = False
    for dev in DEVICES.values():
        dev['device'].off()
    print("GPIO cleaned up. Goodbye!")

# -----------------------
# Main Loop
# -----------------------
def main():
    app = DomiSafeApp()
    app.start()  # Start sensor thread

    device_keys = list(DEVICES.keys())
    try:
        while True:
            print("\nDevice Menu:")
            for i, k in enumerate(device_keys, 1):
                print(f"{i}. {DEVICES[k]['name']} ({'ON' if DEVICES[k]['state'] else 'OFF'})")
            print("s=Status | a=All ON | o=All OFF | p=Party | q=Quit")

            cmd = input("Command: ").strip().lower()
            if cmd == 'q':
                break
            elif cmd == 's':
                show_status()
            elif cmd == 'a':
                turn_all(True)
            elif cmd == 'o':
                turn_all(False)
            elif cmd == 'p':
                toggle_party_mode()
            elif cmd.isdigit() and 1 <= int(cmd) <= len(device_keys):
                toggle_device(device_keys[int(cmd)-1])
            else:
                print("Invalid command")
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        app.running = False

if __name__ == "__main__":
    main()
