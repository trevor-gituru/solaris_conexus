# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
    DATABASE_URL = os.getenv("DATABASE_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Nylas config
    NYLAS_CLIENT_ID = os.getenv("NYLAS_CLIENT_ID")
    NYLAS_API_KEY = os.getenv("NYLAS_API_KEY")
    NYLAS_API_URI = os.getenv("NYLAS_API_URI")
    NYLAS_SENDER_EMAIL = os.getenv("NYLAS_SENDER_EMAIL")
    NYLAS_GRANT_ID = os.getenv("NYLAS_GRANT_ID")

    # Blockchain config
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

    # M-Pesa config
    SAF_CONSUMER_KEY = os.getenv("SAF_CONSUMER_KEY")
    SAF_CONSUMER_SECRET = os.getenv("SAF_CONSUMER_SECRET")
    SAF_SHORTCODE = os.getenv("SAF_SHORTCODE")
    SAF_PASS_KEY = os.getenv("SAF_PASS_KEY")
    SAF_ACCESS_TOKEN_API = os.getenv("SAF_ACCESS_TOKEN_API")
    SAF_STK_PUSH_API = os.getenv("SAF_STK_PUSH_API")
    SAF_STK_PUSH_QUERY_API = os.getenv("SAF_STK_PUSH_QUERY_API")
    CALLBACK_URL = os.getenv("CALLBACK_URL")


    # MQTT config
    MQTT_BROKER = os.getenv("MQTT_BROKER")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    MQTT_PUBLISH_TOPIC = os.getenv("MQTT_PUBLISH_TOPIC")
    MQTT_SUBSCRIBE_TOPIC = os.getenv("MQTT_SUBSCRIBE_TOPIC")

    # Server config
    PORT = int(os.getenv("PORT", 8000))

    # Starknet config
    STARKNET_PRIVATE_KEY = os.getenv("STARKNET_PRIVATE_KEY")
    STARKNET_ACCOUNT_ADDRESS = os.getenv("STARKNET_ACCOUNT_ADDRESS")
    SCT_CONTRACT_ADDRESS = os.getenv("SCT_CONTRACT_ADDRESS")
    STRK_CONTRACT_ADDRESS = os.getenv("STRK_CONTRACT_ADDRESS")
    STARKNET_RPC_URL = os.getenv("STARKNET_RPC_URL")

    # Africas Talking
    SMS_USERNAME=os.getenv("SMS_USERNAME")
    SMS_API=os.getenv("SMS_API")

settings = Settings()

