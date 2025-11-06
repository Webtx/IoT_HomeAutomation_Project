import json
import time
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
import paho.mqtt.client as mqtt
# import cv2


import board
import adafruit_dht

import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the DHT device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D4)
# For DHT22:  dhtDevice = adafruit_dht.DHT22(board.D4)  # or board.D18, etc.

# Feed names for each sensor type
ENV_FEEDS = {  # Replace with your feed name
    "temperature": "temperature",
    "humidity": "humidity",
    "pressure": "pressure"
}


class SensorSimulator:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.image_dir = 'captured_images'
        self.running = True
        self.mqtt_client = None
        self.mqtt_connected = False
        self.setup_mqtt()

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "ADAFRUIT_IO_USERNAME": "username",
            "ADAFRUIT_IO_KEY": "userkey",
            "MQTT_BROKER": "io.adafruit.com",
            "MQTT_PORT": 1883,
            "MQTT_KEEPALIVE": 60,
            "devices": ["living_room_light", "bedroom_fan", "front_door", "garage_door"],
            "camera_enabled": True,
            "capturing_interval": 900,
            "flushing_interval": 10,
            "sync_interval": 300
        }

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return default_config

    def setup_mqtt(self):
        """Setup MQTT client for Adafruit IO"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(
                self.config["ADAFRUIT_IO_USERNAME"],
                self.config["ADAFRUIT_IO_KEY"]
            )

            # Set up callbacks
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            self.mqtt_client.on_publish = self.on_mqtt_publish

            # Connect to broker
            self.mqtt_client.connect(
                self.config["MQTT_BROKER"],
                self.config["MQTT_PORT"],
                self.config["MQTT_KEEPALIVE"]
            )

            # Start the network loop in a separate thread
            self.mqtt_client.loop_start()
            logger.info("MQTT client setup completed")

        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
            self.mqtt_connected = False

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback for when MQTT client connects"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("Connected to MQTT broker")
        else:
            self.mqtt_connected = False
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        """Callback for when MQTT client disconnects"""
        self.mqtt_connected = False
        logger.warning("Disconnected from MQTT broker")

    def on_mqtt_publish(self, client, userdata, mid):
        """Callback for when message is published"""
        logger.debug(f"Message {mid} published successfully")

    def generate_environmental_data(self):
        temperature_c, humidity, pressure = 0, 0, 0
        try:
            pressure = round(1013.25 + random.uniform(-10, 10), 2)
            # Read temperature and humidity
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity

            print(f"Temp: {temperature_c:.1f} C ({temperature_f:.1f} F)")
            print(f"Humidity: {humidity:.1f}%")

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)

        return {
            'timestamp': datetime.now().isoformat(),
            'temperature': temperature_c,
            'humidity': humidity,
            'pressure': pressure
        }

    def generate_security_data(self):
        """Generate simulated security sensor data"""
        # Motion detection probability (higher during day)
        hour = datetime.now().hour
        motion_prob = 0.1 if 22 <= hour or hour <= 6 else 0.3
        motion_detected = random.random() < motion_prob

        # Smoke detection (very rare)
        smoke_detected = random.random() < 0.001

        image_path = None
        if motion_detected and self.config['camera_enabled']:
            # image_path = self.capture_image()
            image_path = "./capture_image/motion_0001.jpg"

        return {
            'timestamp': datetime.now().isoformat(),
            'motion_detected': motion_detected,
            'smoke_detected': smoke_detected,
            'image_path': image_path
        }

    def capture_image(self):
        """Simulate camera image capture"""
        try:
            # Try to use actual camera if available
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"{self.image_dir}/motion_{timestamp}.jpg"
                cv2.imwrite(image_path, frame)
                logger.info(f"Image captured: {image_path}")
                return image_path
        except Exception as e:
            logger.warning(f"Camera capture failed: {e}")

        # Fallback: create a placeholder image file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"{self.image_dir}/motion_{timestamp}.txt"
        with open(image_path, 'w') as f:
            f.write(f"Motion detected at {datetime.now().isoformat()}")
        return image_path

    def generate_device_status(self):
        """Generate device status data based on last known state """
        device_data = []

        for device in self.config['devices']:
            status = 'off'  # default off
            device_data.append({
                'timestamp': datetime.now().isoformat(),
                'device_name': device,
                'status': status
            })

        return device_data

    # Send data to Adafruit IO
    def send_to_adafruit_io(self, feed_name, value):
        if not self.mqtt_connected or not self.mqtt_client:
            logger.warning("MQTT client not connected")
            return False

        try: 
            topic = f"{self.config['ADAFRUIT_IO_USERNAME']}/feeds/{feed_name}"
            self.mqtt_client.publish(topic, str(value))
            return True

        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
            return False

    def send_to_cloud(self, data, feeds):
        success = True
        timestamp = data['timestamp']
        logger.info(f"Processing env. reading from {timestamp}")

        # Send temperature
        if self.send_to_adafruit_io(feeds['temperature'], data['temperature']):
            logger.info(f"  Temperature: {data['temperature']} C ?")
        else:
            success = False
        # time.sleep(self.config["capturing_interval"])
        # Send humidity
        if self.send_to_adafruit_io(feeds['humidity'], data['humidity']):
            logger.info(f"  Humidity: {data['humidity']}% ?")
        else:
            success = False
        # time.sleep(self.config["capturing_interval"])
        # Send pressure
        if self.send_to_adafruit_io(feeds['pressure'], data['pressure']):
            logger.info(f"  Pressure: {data['pressure']} hPa ?")
        else:
            success = False
        time.sleep(self.config["capturing_interval"])
        return success

    def data_collection_loop(self, ):
        environmental_data_filename = os.path.abspath("environmental_data.txt")
        security_data_filename = os.path.abspath("security_data.txt")
        device_status_filename = os.path.abspath("device_status.txt")

        logger.info(
            f"Writing to:\n  {environmental_data_filename}\n  \
                                {security_data_filename}\n  \
                                {device_status_filename}")

        # Append mode + line buffering for faster flush on newline
        with open(environmental_data_filename, "w", buffering=1) as file1, \
                open(security_data_filename, "w", buffering=1) as file2, \
                open(device_status_filename, "w", buffering=1) as file3:

            last_fsync = time.time()
            while self.running:
                try:
                    # Environmental
                    env_data = self.generate_environmental_data()
                    file1.write(json.dumps(env_data) + "\n")
                    if self.send_to_cloud(data=env_data, feeds=ENV_FEEDS):
                        logger.info("sent to cloud")
                    else:
                        logger.info("offline, sent env data to local file. will sync later.")
                    logger.info(f"Environmental data: {env_data}")

                    # Security
                    sec_data = self.generate_security_data()
                    if sec_data['motion_detected'] or sec_data['smoke_detected']:
                        logger.warning(f"Security alert: {sec_data}")
                        file2.write(json.dumps(sec_data) + "\n")

                    # Device status: write each device on its own line
                    dev_data_list = self.generate_device_status()
                    file3.write(json.dumps(dev_data_list) + "\n")
                    logger.info(f"Device status updated: {len(dev_data_list)} devices")

                    # Ensure data is on-disk regularly (every ~10s)
                    if time.time() - last_fsync > self.config["flushing_interval"]:
                        for fh in (file1, file2, file3):
                            fh.flush()
                            os.fsync(fh.fileno())
                        last_fsync = time.time()

                    print("sleeping for ", self.config["capturing_interval"])
                    time.sleep(self.config["capturing_interval"])

                except Exception as e:
                    logger.error(f"Error in data collection loop: {e}", exc_info=True)
                    time.sleep(60)

    def start(self):
        """Start the sensor simulator"""
        self.running = True
        logger.info("Starting Raspberry Pi Sensor Simulator (file output)")

        # Non-daemon so it can shut down cleanly and close files
        data_thread = threading.Thread(target=self.data_collection_loop)
        data_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down sensor simulator")
        finally:
            self.running = False
            # Wait for thread to exit so with-context closes and flushes
            data_thread.join(timeout=10)
            logger.info("Stopped.")


if __name__ == "__main__":
    # Create default config file if it doesn't exist
    simulator = SensorSimulator(config_file='./config.json')  # flush every 10 seconds
    simulator.start()

