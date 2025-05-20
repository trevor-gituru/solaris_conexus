from core_api.client import fetch_and_store_devices
from config import BACKEND_URL, BACKEND_KEY

# def task1():
#     print("Task 1 started, Syncing devices & their account balances...")
#     try:
#         fetch_and_store_devices()
#     except Exception as e:
#         print("Error in task1:", e)
#     print("Task 1 finished")

from homes.arduino_interface import  ArduinoDevice
from mqtt.subscriber import run_mqtt, stop_mqtt
from db.database import get_db
from sqlalchemy.orm import Session

import threading
import time
import serial  # make sure serial is imported

# def monitor_device(port):
#     while True:
#         try:
#             db: Session = next(get_db())  # Create fresh DB session each loop
#             arduino = ArduinoDevice(port)
#             arduino.start_monitoring_loop(db)  # Assuming this blocks with its own loop
#         except (serial.SerialException, OSError) as e:
#             print(f"[{port}] Device disconnected or error: {e}. Retrying in 5 seconds...")
#             time.sleep(5)
#         except Exception as e:
#             print(f"[{port}] Unexpected error: {e}. Retrying in 30 seconds...")
#             time.sleep(30)
#         finally:
#             # Close db session if your session requires explicit close
#             try:
#                 db.close()
#             except:
#                 pass

def main():
    ports = ["/dev/ttyACM0", "/dev/ttyACM1"]
    devices = [ArduinoDevice(port) for port in ports]
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

# def main():
#     mqtt_client = run_mqtt()

#     try:
#         print("[Main] MQTT client started.")
#         while True:
#             time.sleep(1)  # Keep main thread alive to keep MQTT running

#     except KeyboardInterrupt:
#         stop_mqtt(mqtt_client)
#         print("[Main] KeyboardInterrupt received. Exiting...")


if __name__ == "__main__":
    main()
