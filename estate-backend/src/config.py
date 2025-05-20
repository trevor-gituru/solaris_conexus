# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
BACKEND_KEY = os.getenv("BACKEND_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
WALLET_PUB = os.getenv('WALLET_PUB')
WALLET_PRIV = os.getenv('WALLET_PRIV')
NODE_URL = os.getenv('NODE_URL')
SCT_ADDRESS = os.getenv('SCT_ADDRESS')

# MQTT Broker details
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

# MQTT Authentication
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

# MQTT Topics
MQTT_PUBLISH_TOPIC = os.getenv('MQTT_PUBLISH_TOPIC')
MQTT_SUBSCRIBE_TOPIC = os.getenv('MQTT_SUBSCRIBE_TOPIC')

