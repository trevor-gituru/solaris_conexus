# src/mqtt/client.py
import paho.mqtt.client as paho
from paho.mqtt.client import CallbackAPIVersion
from paho import mqtt
from src.config import settings
from src.utils.loggers import mqtt_logger
from src.db.database import get_db
from src.db.models import Device, PowerConsumption
import threading
import json
import time

streaming_flags = {}
class MqttClient:
    def __init__(self):
        self.client = paho.Client(
            client_id="",
            userdata=None,
            protocol=paho.MQTTv5,
            callback_api_version=CallbackAPIVersion.VERSION2
        )
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.client.tls_set()
        
        self.subscribe_topic = f"{settings.HUB_NAME}/commands"
        self.publish_topic = f"{settings.HUB_NAME}/power"
        self.device = None

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_publish = self.on_publish

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            client.subscribe(self.subscribe_topic, qos=1)
            mqtt_logger.info(f"Subscribed to {self.subscribe_topic}")
        else:
            mqtt_logger.error(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        # mqtt_logger.info(f"Message received on {msg.topic}: {msg.payload.decode()}")

        try:
            command = json.loads(msg.payload.decode())
            device_id = command["device"]
            device = None
            with get_db() as db:
                device = Device.find(db, id=device_id)
                self.device = device
                if device is None:
                    raise ValueError(f"[Receive] - Device ID [{device_id}[ not found in database.")
                if "instruction" in command:
                    device.update(db, {"instruction": 2})
                    mqtt_logger.info(f"[Receive] - [Toogle Load] - [{device.device_id}]")
                    return

            if command.get("command") == "stream":
                if not streaming_flags.get(device_id):
                    streaming_flags[device_id] = True
                    threading.Thread(target=self.stream_power, args=(device, client), daemon=True).start()
                    mqtt_logger.info(f"[Receive] - [Stream Start] - [{device.device_id}]")
                else:
                    mqtt_logger.warning(f"[Stream] Already streaming for device {device_id}")

            elif command.get("command") == "stop":
                streaming_flags[device_id] = False
                mqtt_logger.info(f"[Receive] - [Stream Stop] - [{device.device_id}]")

            else:
                mqtt_logger.info(f"[Receive] Unknown command: {command}")

        except json.JSONDecodeError:
            mqtt_logger.warning("[Receive] - Invalid JSON payload")
        except ValueError as e:
            mqtt_logger.warning(f"[Receive] - [Err] - {e}")

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        mqtt_logger.info(f"Subscription successful")

    def on_publish(self, client, userdata, mid, properties=None, extra=None):
        if userdata:
            mqtt_logger.info(f"Message published (mid={mid}), {userdata.get("power")}")

    def start(self):
        self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


    def stream_power(self, device, client):
        while streaming_flags.get(device.id):
            try:
                with get_db() as db:
                    power = PowerConsumption.latest(db, device.id)
                    if power:
                        message = {
                            "timestamp": str(power.timestamp),
                            "power": power.power
                        }
                        topic = f"{self.publish_topic}/{device.id}"
                        client.publish(topic, json.dumps(message))
                        mqtt_logger.info(f"[Publish] - [Stream] - [{device.device_id}] -  {message.get("power")} W")
                    time.sleep(3)  # Add delay between messages
            except Exception as e:
                mqtt_logger.error(f"[StreamError] {e}")


mqtt_client = MqttClient()
        
if __name__ == "__main__":
    import time
    
    try:
        mqtt_client.start()
        while True:
            pass
    except KeyboardInterrupt:
        mqtt_logger.warning("Keyboard interrupt detected. Shutting down gracefully...")
        mqtt_client.stop()
        time.sleep(5)
    finally:
        mqtt_logger.info("✅ Shutdown complete.")
