
import board
import json
import time
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
import threading
from dotenv import load_dotenv
# import my code
from MQTT_communicator import MQTT_communicator
from environmental_module import environmental_module
from security_module import security_module
from device_control_module import device_control_module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Feed names for each sensor type
ENV_FEEDS = {  # Replace with your feed name
    "temperature": "temperature",
    "humidity": "humidity",
    "pressure": "pressure"
}

SECURITY_FEEDS = {  # Replace with your feed name
    "motion_count": "motion_feed",
    "smoke_count": "smoke_feed",
}

class DomiSafeApp:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        """Collect security data every 5 seconds, send summary every 60 seconds"""

        self.security_check_interval = self.config.get("security_check_interval", 5)
        self.security_send_interval = self.config.get("security_send_interval", 60)
        self.env_interval = self.config.get("env_interval", 30)

        self.running = True

        self.mqtt_agent = MQTT_communicator(config_file)
        self.env_data = environmental_module(config_file)
        self.security_data = security_module(config_file)
        self.device_control = device_control_module(config_file)


    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "ADAFRUIT_IO_USERNAME": "username",
            "ADAFRUIT_IO_KEY": "userkey",
            "MQTT_BROKER": "io.adafruit.com",
            "MQTT_PORT": 1883,
            "MQTT_KEEPALIVE": 60,
            "flushing_interval": 10  # default flush interval in seconds
        }
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return {**default_config, **config}
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return default_config

    def send_to_cloud(self, data, feeds):
        """Send data to Adafruit IO by looping through feeds"""
        success = True
        timestamp = data.get('timestamp', datetime.now().isoformat())
        logger.info(f"Processing reading from {timestamp}")
        for feed_name, feed_key in feeds.items():
            if feed_name not in data:
                continue
            try:
                self.mqtt_agent.send_to_adafruit_io(feed_key, data[feed_name])
            except Exception as e:
                logger.error(f"Failed to send {feed_name}: {e}")
                success = False
            time.sleep(0.5)  
        return success

    def collect_environmental_data(self, current_time, timers, file_handle):
       
        if current_time - timers['env_check'] >= self.env_interval:
            env_data = self.env_data.get_environmental_data()

            # Write to file
            file_handle.write(json.dumps(env_data) + "\n")
            if self.send_to_cloud(data=env_data, feeds=ENV_FEEDS):
                logger.info("Environmental data sent to cloud")
            else:
                logger.info("Offline, env data saved locally. Will sync later.")
            logger.info(f"Environmental data: {env_data}")
            timers['env_check'] = current_time

    def collect_security_data(self, current_time, timers, security_counts, file_handle):
        # Check security every 5 seconds
        if current_time - timers['security_check'] >= self.security_check_interval:
            sec_data = self.security_data.get_security_data()
            if sec_data['motion_detected']:
                security_counts['motion'] += 1
                logger.warning(f"Motion detected! Total: {security_counts['motion']}")
            if sec_data['smoke_detected']:
                security_counts['smoke'] += 1
                logger.warning(f"Smoke detected! Total: {security_counts['smoke']}")
            if sec_data['motion_detected'] or sec_data['smoke_detected']:
                file_handle.write(json.dumps(sec_data) + "\n")
            timers['security_check'] = current_time

        # Send summary to cloud every 60 seconds
        print(current_time - timers['security_send'], self.security_send_interval)
        if current_time - timers['security_send'] >= self.security_send_interval:
            security_summary = {
                'timestamp': datetime.now().isoformat(),
                'motion_count': security_counts['motion'],
                'smoke_count': security_counts['smoke']
            }
            print("security summary = ", security_summary)
            if self.send_to_cloud(data=security_summary, feeds=SECURITY_FEEDS):
                logger.info(f"Security summary sent: {security_counts['motion']} motion, {security_counts['smoke']} smoke")
            else:
                logger.warning("Failed to send security summary")
            # Reset counters
            security_counts['motion'] = 0
            security_counts['smoke'] = 0
            timers['security_send'] = current_time

    def data_collection_loop(self):
        timestamp = datetime.now().strftime("%Y%m%d")
        environmental_data_filename = os.path.abspath(f"{timestamp}_environmental_data.txt")
        security_data_filename = os.path.abspath(f"{timestamp}_security_data.txt")
        device_status_filename = os.path.abspath(f"{timestamp}_device_status.txt")
        logger.info(f"Writing to:\n {environmental_data_filename}\n {security_data_filename}\n {device_status_filename}")

        with open(environmental_data_filename, "a", buffering=1) as file1, \
             open(security_data_filename, "a", buffering=1) as file2, \
             open(device_status_filename, "a", buffering=1) as file3:

            last_fsync = time.time()
            timers = {
                'env_check': 0,
                'security_check': 0,
                'security_send': 0
            }
            security_counts = {'motion': 0, 'smoke': 0}

            while self.running:
                try:
                    current_time = time.time()
                    # Security and environmental checks
                    self.collect_security_data(current_time, timers, security_counts, file2)
                    self.collect_environmental_data(current_time, timers, file1)

                    # Device status is only sent on-demand
                    # Flush files regularly
                    if current_time - last_fsync > self.config["flushing_interval"]:
                        for fh in (file1, file2, file3):
                            fh.flush()
                            os.fsync(fh.fileno())
                        last_fsync = current_time

                    time.sleep(self.security_check_interval)
                except Exception as e:
                    logger.error(f"Error in data collection loop: {e}", exc_info=True)
                    time.sleep(5)  # Retry faster for security monitoring

    def start(self):
        """Start the sensor simulator"""
        self.running = True
        logger.info("Starting Raspberry Pi Sensor Simulator (file output)")
        data_thread = threading.Thread(target=self.data_collection_loop)
        data_thread.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down sensor simulator")
        finally:
            self.running = False
            data_thread.join(timeout=10)
            # cleanup if using picamera or cv2
            try:
                import picamera2
                import cv2
                picamera2.stop()
                cv2.destroyAllWindows()
            except Exception:
                pass
            logger.info("Stopped.")


if __name__ == "__main__":
    simulator = DomiSafeApp(config_file='./config.json')
    simulator.start()
