# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BACKEND_URL = os.getenv("BACKEND_URL")
    BACKEND_KEY = os.getenv("BACKEND_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    HUB_NAME = os.getenv("HUB_NAME")

    # Starknet config
    STARKNET_PRIVATE_KEY = os.getenv("STARKNET_PRIVATE_KEY")
    STARKNET_ACCOUNT_ADDRESS = os.getenv("STARKNET_ACCOUNT_ADDRESS")
    SCT_CONTRACT_ADDRESS = os.getenv("SCT_CONTRACT_ADDRESS")
    SCT_OWNER = os.getenv("SCT_OWNER")
    STRK_CONTRACT_ADDRESS = os.getenv("STRK_CONTRACT_ADDRESS")
    STARKNET_RPC_URL = os.getenv("STARKNET_RPC_URL")

    # MQTT Broker details
    MQTT_BROKER = os.getenv('MQTT_BROKER')
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

    # MQTT Authentication
    MQTT_USERNAME = os.getenv('MQTT_USERNAME')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

settings = Settings()
