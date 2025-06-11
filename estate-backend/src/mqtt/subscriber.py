# src/mqtt/subscriber.py

import paho.mqtt.client as mqtt
import json
import threading
import time
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Device, PowerConsumption
from config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_SUBSCRIBE_TOPIC, MQTT_PUBLISH_TOPIC

# Global dict to track streaming flags per device
streaming_flags = {}

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    client.subscribe(MQTT_SUBSCRIBE_TOPIC)
    print(f"[MQTT] Subscribed to {MQTT_SUBSCRIBE_TOPIC}")

def on_message(client, userdata, msg):
    print(f"[MQTT] Message received on {msg.topic}: {msg.payload.decode()}")

    try:
        command = json.loads(msg.payload.decode())

        if "device" in command and "update_balance" in command:
            device_id = command["device"]
            amount = command["update_balance"]

            db_generator = get_db()
            db: Session = next(db_generator)
            try:
                device = db.query(Device).filter(Device.id == device_id).first()
                if device:
                    token_balance = device.token_balance + amount
                    device.token_balance = token_balance
                    db.commit()
                    print(f"[MQTT] Updated token balance for device {device.device_id} by {amount}")
                else:
                    print(f"[MQTT] Device ID {device_id} not found in database.")
            finally:
                db.close()
                # Close the generator to trigger the generator's finally block if any
                try:
                    next(db_generator)
                except StopIteration:
                    pass

        elif "device" in command and "instruction" in command:
            device_id = command["device"]
            instruction = command["instruction"]

            db_generator = get_db()
            db: Session = next(db_generator)
            try:
                device = db.query(Device).filter(Device.id == device_id).first()
                if device:
                    device.instruction = instruction
                    db.commit()
                    print(f"[MQTT] Updated instruction for device {device_id} to {instruction}")
                else:
                    print(f"[MQTT] Device ID {device_id} not found in database.")
            finally:
                db.close()
                # Close the generator to trigger the generator's finally block if any
                try:
                    next(db_generator)
                except StopIteration:
                    pass

        elif command.get("command") == "stream":
            device_id = command["device"]
            if not streaming_flags.get(device_id):
                streaming_flags[device_id] = True
                threading.Thread(target=stream_power_data, args=(device_id, client), daemon=True).start()
                print(f"[Stream] Started streaming for device {device_id}")
            else:
                print(f"[Stream] Already streaming for device {device_id}")

        elif command.get("command") == "stop":
            device_id = command["device"]
            streaming_flags[device_id] = False
            print(f"[Stream] Stopped streaming for device {device_id}")

        else:
            print(f"[MQTT] Unknown command: {command}")

    except json.JSONDecodeError:
        print("[MQTT] Invalid JSON payload")

def stream_power_data(device_id, client):
    while streaming_flags.get(device_id):
        try:
            db: Session = next(get_db())
            power = PowerConsumption.latest(db, device_id)
            if power:
                message = {
                    "device": device_id,
                    "timestamp": str(power.timestamp),
                    "voltage": power.voltage,
                    "current": power.current,
                    "power": power.power
                }
                topic = f"{MQTT_PUBLISH_TOPIC}/{device_id}"
                client.publish(topic, json.dumps(message))
                print(f"[Stream] Published for device {device_id}: {message}")
            time.sleep(3)  # Add delay between messages
        except Exception as e:
            print(f"[StreamError] {e}")

def run_mqtt():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    return client

def stop_mqtt(client):
    client.loop_stop()
    client.disconnect()
