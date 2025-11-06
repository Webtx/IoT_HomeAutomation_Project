import sys
import paho.mqtt.client as paho
from paho.mqtt.enums import CallbackAPIVersion
# Updated for latest paho-mqtt version (2.0+)
client = paho.Client(callback_api_version=CallbackAPIVersion.VERSION2)
if client.connect("localhost", 1883, 60) != 0:
 print("Couldn't connect to the mqtt broker")
 sys.exit(1)
client.publish("test_topic", "Hi, paho mqtt client works fine!", qos=0)
client.disconnect() 
