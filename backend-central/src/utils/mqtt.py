# /src/utils/mqtt.py

import paho.mqtt.client as mqtt
import threading
import json
from src.config import settings 
import asyncio
mqtt_event_loop = None  # Global asyncio loop

# Global client instance
mqtt_client = None
mqtt_lock = threading.Lock()

# Store listeners for topic-based callbacks
topic_callbacks = {}

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    # Subscribe to any topics that were registered before connection
    for topic in topic_callbacks.keys():
        client.subscribe(topic)
        print(f"[MQTT] Subscribed to {topic}")

def on_message(client, userdata, msg):
    callback = topic_callbacks.get(msg.topic)
    if callback:
        payload = msg.payload.decode()
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = payload

        # If it's a coroutine, run it in the asyncio event loop
        if asyncio.iscoroutinefunction(callback):
            if mqtt_event_loop is not None:
                asyncio.run_coroutine_threadsafe(callback(data), mqtt_event_loop)
            else:
                print("[MQTT] No asyncio loop registered")
        else:
            callback(data)
    else:
        print(f"[MQTT] No callback registered for topic {msg.topic}")

def init_mqtt():
    global mqtt_client
    with mqtt_lock:
        if mqtt_client is None:
            client = mqtt.Client()
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
            client.tls_set()

            client.on_connect = on_connect
            client.on_message = on_message

            client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            client.loop_start()
            mqtt_client = client
        return mqtt_client

def publish_command(topic: str, payload: dict):
    client = init_mqtt()
    message = json.dumps(payload)
    client.publish(topic, message)
    print(f"[MQTT] Published to {topic}: {message}")

def register_listener(topic: str, callback, loop=None):
    global mqtt_event_loop
    mqtt_event_loop = loop  # Save the loop for later thread-safe use

    client = init_mqtt()
    topic_callbacks[topic] = callback
    client.subscribe(topic)
    print(f"[MQTT] Listener registered for {topic}")


