# src/local_hub_mqtt/publisher.py

from config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_PUBLISH_TOPIC
import paho.mqtt.client as mqtt
import json

def publish_power_consumptions(records: list):
    """
    Publishes a list of PowerConsumption SQLAlchemy objects to MQTT.
    
    Args:
        records (list): List of PowerConsumption instances.
    """
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()

        for record in records:
            device_id = record.device_id
            topic = f"{MQTT_PUBLISH_TOPIC}/{device_id}"

            payload = {
                "power": record.power,
                "timestamp": record.timestamp.isoformat() + "Z"
            }

            client.publish(topic, json.dumps(payload))
            print(f"Published to {topic}: {payload}")

    finally:
        client.loop_stop()
        client.disconnect()

