# Author: Your Name, Student ID
# Champlain College Saint-Lambert - IoT: Design and Prototyping of Connected Devices
# Lab 06 – Motion Detection with Camera + Buzzer Alert

import json, time, random, logging, os, threading, cv2
from datetime import datetime
from pathlib import Path
import paho.mqtt.client as mqtt
from picamera2 import Picamera2
import board, adafruit_dht
from gpiozero import MotionSensor, TonalBuzzer
from gpiozero.tones import Tone

# ──────────────────────────────────────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DHT11 sensor on GPIO4
dhtDevice = adafruit_dht.DHT11(board.D4)

ENV_FEEDS = {"temperature": "temperature", "humidity": "humidity", "pressure": "pressure"}

class SensorSimulator:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.image_dir = 'captured_images'
        Path(self.image_dir).mkdir(parents=True, exist_ok=True)

        self.running = True
        self.mqtt_client, self.mqtt_connected = None, False
        self.setup_mqtt()

        # ──────────────────────────────────────────────────────────────────
        # PIR Motion Sensor Initialization
        # ──────────────────────────────────────────────────────────────────
        self.pir = None
        try:
            pir_pin = self.config.get("PIR_PIN", 7)
            self.pir = MotionSensor(pir_pin)
            logger.info(f"PIR motion sensor initialized on GPIO{pir_pin}")
        except Exception as e: 
            logger.warning(f"PIR init failed (no-motion mode): {e}")

        # ──────────────────────────────────────────────────────────────────
        # Passive Buzzer Initialization
        # ──────────────────────────────────────────────────────────────────
        self.buzzer = None
        try:
            buzzer_pin = self.config.get("BUZZER_PIN", 1)  # Passive buzzer on GPIO3
            self.buzzer = TonalBuzzer(buzzer_pin)
            logger.info(f"Passive buzzer initialized on GPIO{buzzer_pin}")
        except Exception as e:
            logger.warning(f"Buzzer init failed: {e}")

        # ──────────────────────────────────────────────────────────────────
        # Camera Initialization (Picamera2)
        # ──────────────────────────────────────────────────────────────────
        self.picam2 = None
        try:
            self.picam2 = Picamera2()
            self.picam2.configure(self.picam2.create_still_configuration())
            self.picam2.start()
            logger.info("Picamera2 started (camera initialized)")
        except Exception as e:
            logger.warning(f"Picamera2 init failed; fallback to placeholder files: {e}")
            self.picam2 = None

    # Load configuration
    def load_config(self, config_file):
        default = {
            "ADAFRUIT_IO_USERNAME": "username",
            "ADAFRUIT_IO_KEY": "userkey",
            "MQTT_BROKER": "io.adafruit.com",
            "MQTT_PORT": 1883,
            "MQTT_KEEPALIVE": 60,
            "devices": ["living_room_light", "bedroom_fan", "front_door", "garage_door"],
            "camera_enabled": True,
            "capturing_interval": 10,
            "flushing_interval": 10,
            "sync_interval": 300,
            "PIR_PIN": 17,
            "BUZZER_PIN": 3
        }
        try:
            with open(config_file, 'r') as f:
                return {**default, **json.load(f)}
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return default

    # MQTT setup
    def setup_mqtt(self):
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(
                self.config["ADAFRUIT_IO_USERNAME"],
                self.config["ADAFRUIT_IO_KEY"]
            )
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            self.mqtt_client.on_publish = self.on_mqtt_publish
            self.mqtt_client.connect(
                self.config["MQTT_BROKER"],
                self.config["MQTT_PORT"],
                self.config["MQTT_KEEPALIVE"]
            )
            self.mqtt_client.loop_start()
            logger.info("MQTT client setup completed")
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
            self.mqtt_connected = False

    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.mqtt_connected = (rc == 0)
        logger.info("Connected to MQTT broker" if rc == 0 else f"MQTT connect failed rc={rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.mqtt_connected = False
        logger.warning("Disconnected from MQTT broker")

    def on_mqtt_publish(self, client, userdata, mid):
        logger.debug(f"Message {mid} published")

    # Read DHT11 data + simulated pressure
    def generate_environmental_data(self):
        temperature_c, humidity, pressure = 0, 0, 0
        try:
            pressure = round(1013.25 + random.uniform(-10, 10), 2)
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
        except RuntimeError as e:
            logger.debug(f"DHT read issue: {e}")
            time.sleep(2.0)
        return {
            'timestamp': datetime.now().isoformat(),
            'temperature': temperature_c,
            'humidity': humidity,
            'pressure': pressure
        }

    # Motion Detection + Capture + Buzzer
    def generate_security_data(self):
        motion = False
        if self.pir is not None:
            motion = self.pir.motion_detected

        smoke = False
        image_path = None

        if motion:
            logger.info("Motion detected → capturing image and sounding buzzer")

            # Trigger passive buzzer for 3 seconds
            if self.buzzer:
                try:
                    self.buzzer.play(Tone(440))  # A4 tone
                    time.sleep(3)
                    self.buzzer.stop()
                    logger.info("Buzzer sounded successfully")
                except Exception as e:
                    logger.warning(f"Buzzer error: {e}")

            # Capture image
            if self.config.get('camera_enabled', True):
                image_path = self.capture_image()

        return {
            'timestamp': datetime.now().isoformat(),
            'motion_detected': motion,
            'smoke_detected': smoke,
            'image_path': image_path
        }

    def capture_image(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"{self.image_dir}/motion_{ts}.jpg"
        try:
            if self.picam2 is not None:
                frame = self.picam2.capture_array()
                cv2.imwrite(image_path, frame)
                logger.info(f"Image captured: {image_path}")
                return image_path
        except Exception as e:
            logger.warning(f"Picamera2 capture failed: {e}")
        fallback = f"{self.image_dir}/motion_{ts}.txt"
        with open(fallback, 'w') as f:
            f.write(f"Motion detected at {datetime.now().isoformat()} (no camera)")
        logger.info(f"Fallback note: {fallback}")
        return fallback

    # MQTT publish helpers
    def send_to_adafruit_io(self, feed_name, value):
        if not self.mqtt_connected or not self.mqtt_client:
            logger.warning("MQTT not connected")
            return False
        try:
            topic = f"{self.config['ADAFRUIT_IO_USERNAME']}/feeds/{feed_name}"
            result, _ = self.mqtt_client.publish(topic, str(value))
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published {value} to {topic}")
                return True
            logger.error(f"Publish failed result={result}")
            return False
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")
            return False

    def send_to_cloud(self, data, feeds):
        ok = True
        if not self.send_to_adafruit_io(feeds['temperature'], data['temperature']): ok = False
        if not self.send_to_adafruit_io(feeds['humidity'], data['humidity']): ok = False
        if not self.send_to_adafruit_io(feeds['pressure'], data['pressure']): ok = False
        time.sleep(self.config["capturing_interval"])
        return ok

    # Data collection loop
    def data_collection_loop(self):
        env_path = os.path.abspath("environmental_data.txt")
        sec_path = os.path.abspath("security_data.txt")
        dev_path = os.path.abspath("device_status.txt")
        logger.info(f"Writing to:\n  {env_path}\n  {sec_path}\n  {dev_path}")

        with open(env_path, "w", buffering=1) as f_env, \
             open(sec_path, "w", buffering=1) as f_sec, \
             open(dev_path, "w", buffering=1) as f_dev:

            last_fsync = time.time()
            while self.running:
                try:
                    env = self.generate_environmental_data()
                    f_env.write(json.dumps(env) + "\n")
                    _ = self.send_to_cloud(env, ENV_FEEDS)

                    sec = self.generate_security_data()
                    if sec['motion_detected'] or sec['smoke_detected']:
                        logger.warning(f"Security alert: {sec}")
                        f_sec.write(json.dumps(sec) + "\n")

                    dev_list = [{
                        'timestamp': datetime.now().isoformat(),
                        'device_name': d,
                        'status': 'off'
                    } for d in self.config['devices']]
                    f_dev.write(json.dumps(dev_list) + "\n")

                    if time.time() - last_fsync > self.config["flushing_interval"]:
                        for fh in (f_env, f_sec, f_dev):
                            fh.flush(); os.fsync(fh.fileno())
                        last_fsync = time.time()

                    logger.info(f"Sleeping for {self.config['capturing_interval']}s")
                    time.sleep(self.config["capturing_interval"])
                except Exception as e:
                    logger.error(f"Loop error: {e}", exc_info=True)
                    time.sleep(60)

    def start(self):
        self.running = True
        logger.info("Starting Raspberry Pi Sensor Simulator")
        t = threading.Thread(target=self.data_collection_loop)
        t.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down")
        finally:
            self.running = False
            t.join(timeout=10)
            if getattr(self, "picam2", None):
                try: self.picam2.stop()
                except Exception: pass
            logger.info("Stopped.")

if __name__ == "__main__":
    SensorSimulator('./config.json').start()
