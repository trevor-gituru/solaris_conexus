# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# MQTT Broker details
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

# MQTT Authentication
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# MQTT Topics
MQTT_PUBLISH_TOPIC = os.getenv('MQTT_PUBLISH_TOPIC')
MQTT_SUBSCRIBE_TOPIC = os.getenv('MQTT_SUBSCRIBE_TOPIC')

