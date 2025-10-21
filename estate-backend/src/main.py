from src.central_api.client import central_client
from src.db.database import get_db
from src.utils.exception_handlers.function_handlers import central_fn_handler 

# from homes.arduino_interface import  ArduinoDevice
# from mqtt.subscriber import run_mqtt, stop_mqtt
# from sqlalchemy.orm import Session

# import threading
# import time
# import serial.tools.list_ports

def main():
    central_fn_handler.call(central_client.connect)
    with get_db() as db:
        central_fn_handler.run(central_client.sync_devices, db)
        central_fn_handler.run(central_client.shutdown, db)
    
import serial  # make sure serial is imported
import serial.tools.list_ports
def get_ports():
    devices = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "ACM" in port.device and (
            "Arduino" in port.description or "ttyACM" in port.device
        ):
            devices.append(port.device)
    return devices
    # threads = []
    # mqtt_client = run_mqtt()

    # try:
    #     # for device in devices:
    #     #     t = device.start_threaded_monitoring()
    #     #     threads.append(t)

    #     print(f"[Main] Started monitoring {len('devices')} devices.")
    #     while True:
    #         time.sleep(1)  # Keep main thread alive

    # except KeyboardInterrupt:
    #     stop_mqtt(mqtt_client)
    #     print("[Main] KeyboardInterrupt received. Exiting...")

if __name__ == "__main__":
    main()
