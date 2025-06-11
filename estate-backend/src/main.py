from core_api.client import fetch_and_store_devices
from config import BACKEND_URL, BACKEND_KEY

from homes.arduino_interface import  ArduinoDevice
from mqtt.subscriber import run_mqtt, stop_mqtt
from db.database import get_db
from sqlalchemy.orm import Session

import threading
import time
import serial  # make sure serial is imported
import serial.tools.list_ports

def main():
    # fetch_and_store_devices()
    ports = serial.tools.list_ports.comports()
    devices = []

    for port in ports:
        if "ACM" in port.device and (
            "Arduino" in port.description or "ttyACM" in port.device
        ):
            devices.append(ArduinoDevice(port.device))
    threads = []
    mqtt_client = run_mqtt()

    try:
        for device in devices:
            t = device.start_threaded_monitoring()
            threads.append(t)

        print(f"[Main] Started monitoring {len(devices)} devices.")
        while True:
            time.sleep(1)  # Keep main thread alive

    except KeyboardInterrupt:
        stop_mqtt(mqtt_client)
        print("[Main] KeyboardInterrupt received. Exiting...")

if __name__ == "__main__":
    main()
