# /src/homes/arduino_interface.py
import serial
import serial.tools.list_ports
import json
import time, threading, asyncio
import redis
from datetime import datetime
from zoneinfo import ZoneInfo
from src.db.database import SessionLocal, get_db 
from src.db.models import Device, PowerConsumption
from sqlalchemy.orm import Session
# from starknet.stark import consume, balanceOf
import asyncio
from src.utils.loggers import arduino_logger
from src.utils.redis import arduino_port_client, PowerClient
from src.utils.exception_handlers.function_handlers import arduino_fn_handler, central_fn_handler
from src.starknet.sct import sct_client
from src.central_api.client import central_client



class ArduinoClient:
    def __init__(self, port, baud=9600):
        self.port = port
        self.baud = baud
        self.serial = None
        self.device_id = None
        self.running = False
        self.current = 0.0
        self.voltage = 0.0
        self.timestamp = None
        self.status = "inactive"
        self.id = None  # DB Device.id numeric
        self.balance = 0
        self.instruction = 1  # Default instruction
        self.account_address = None
        self.consumeToken = 0
        self.connection_type = 0
        self.updateBalance = 0
        self.tokenConsumed = False
        self.threshold = 50
    
    def run(self):
            """
            This replaces the external monitor_device(). Continuously tries to connect
            and run the monitoring loop. Recovers from disconnections.
            """
            try:
                with get_db() as db:
                    self.connect(db)
                    central_fn_handler.run(central_client.activate_device, db, self.device_id)
                    self.start_monitoring_loop(db)
            except Exception as e:
                device_id = getattr(self, "device_id", None) or self.port
                if self.device_id and self.status == 'active':
                    with get_db() as db:
                        central_fn_handler.run(central_client.deactivate_device, db, self.device_id)
                arduino_logger.error(f"[{device_id}] -  [Disconnected] - {e}")
                arduino_port_client.delete(self.port)
    
    def connect(self, db: Session):
        """
        Reads serial input and sets the device ID from JSON until a 'current' reading is received.
        Keeps sending instructions during the connection handshake.
        """
        self.serial = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2)  # Allow Arduino to reset
        self.serial.flushInput()
        last_received = time.time()
        timeout_seconds = 2

        while True:
            if self.serial.in_waiting:
                try:
                    line = self.serial.readline().decode().strip()
                    if not line.startswith('{'):
                        continue  # Skip non-JSON lines

                    data = json.loads(line)
                    if "device_id" in data and self.device_id is None:
                        self.device_id = data["device_id"]
                        if self.id is None:
                            device = Device.find(db, device_id=self.device_id) 
                            if not device:
                                raise ValueError(f"[{self.device_id}] not found in database")
                            self.id = device.id
                            self.balance = device.token_balance
                            self.account_address = device.account_address
                            self.connection_type = device.connection_type

                        arduino_logger.info(f"[{self.device_id}] - [Detected] - in [{self.port}]")
                        self.send_data()  # Keep sending initial instruction
                        last_received = time.time()

                    # Exit condition when 'current' data is received
                    if "current" in data:
                        arduino_logger.info(f"[{self.device_id}] - [Connected]")
                        return

                except json.JSONDecodeError:
                    arduino_logger.warning("Ignoring Invalid JSON received")
            else:
                if time.time() - last_received > timeout_seconds:
                    raise ValueError(f"Timeout waiting for data.")
            time.sleep(0.1)

    def send_data(self):
        """
        Sends balance and instruction to Arduino as a comma-separated string.
        Format: "<balance>,<instruction>\n"
        """
        if self.instruction is None:
            self.instruction = 0
        message = f"{self.balance},{self.instruction}\n"
        try:
            self.serial.write(message.encode())
            instruction = ""
            if self.instruction == 2:
                instruction = "Toggle Load"
            else:
                instruction = "Persist Connection"
            arduino_logger.info(f"[{self.device_id}] - [Sent] - Balance: {self.balance} SCT | Instruction: {instruction}")
        except Exception as e:
            arduino_logger.error(f"[{self.device_id}] Failed to send data: {e}")
            raise


    def start_monitoring_loop(self, db: Session):
        """
        Starts the main loop for monitoring and communication with Arduino.
        """
        self.running = True
        power_client = PowerClient(self.device_id)
        while self.running:
            self.update_state(db)
            if self.status == 'inactive':
                raise ValueError("Device is inactive")
            self.read_power()
            self.save_power(db)
            if self.connection_type == 'Consumer' and self.balance != 0:
                self.increase_counter(power_client)
                if self.consumeToken:
                    arduino_fn_handler.run_no_wait(self.consume_tokens)
                    self.consumeToken = 0
            time.sleep(2)


    def update_state(self, db: Session):
        """
        Syncs local state from DB and sends instructions to Arduino accordingly.
        """
        device = Device.find(db, device_id=self.device_id)
        self.status = device.status
        if device:
            if self.updateBalance == "true" or self.tokenConsumed == True:
                self.instruction = 3
                self.tokenConsumed = False
                self.balance = arduino_fn_handler.run(sct_client.balanceOf, self.account_address, self.device_id)
                device.update(db, {"token_balance": self.balance})
                self.send_data()
                self.updateBalance = "false"
                return
            self.balance = device.token_balance
            self.instruction = device.instruction

            if self.instruction == 2:
                self.send_data()
                arduino_logger.info(f"[{self.device_id}] - [Load Toggled]")
                device.update(db, {"instruction": 1})
            elif self.instruction == 1:
                self.send_data()


    def clear_serial_buffer(self):
        """
        Clears the serial input buffer to avoid stale data.
        """
        self.serial.reset_input_buffer()  # or: self.serial.flushInput()
        time.sleep(1)  # Wait a bit for new data to come in


    def read_power(self):
        """
        Reads a JSON-formatted line from serial port.
        Updates current, voltage, timestamp, and request type.
        """
        self.clear_serial_buffer()
        if self.serial.in_waiting:
            try:
                line = self.serial.readline().decode().strip()
                if not line.startswith('{'):
                    arduino_logger.warning("Skipping Non-JSON line received.")
                    return

                data = json.loads(line)
                self.current = data.get("current")
                self.voltage = data.get("voltage")
                self.timestamp = datetime.now(ZoneInfo("Africa/Nairobi"))
                self.req = "ON" if data.get("req") == "true" else "OFF"
                self.updateBalance = data.get("update")

                arduino_logger.info(f"[{self.device_id}] - [Received] - Current: {self.current} A, Voltage: {self.voltage} V, Load Status: {self.req}, Update Balance: {self.updateBalance}")

            except json.JSONDecodeError:
                arduino_logger.warning(f"[{self.device_id}] -  Invalid JSON serial data recieved.")
        else:
            arduino_logger.warning(f"[{self.device_id}] - No serial data available to read.")

    def save_power(self, db_session: Session):
        """
        Inserts a PowerConsumption record into the database.
        Ensures device id is known.
        """
        device = Device.find(db_session, device_id=self.device_id)
        power_data = {
            "device_id": self.id,
            "voltage": self.voltage,
            "current": self.current,
            "timestamp": self.timestamp
        }

        try:
            power_record = PowerConsumption.create(db_session, power_data)
            arduino_logger.info(f"[{self.device_id}] - [Power consumption] - saved- [{power_record.id}]")
        except Exception as e:
            arduino_logger.error(f"[{self.device_id}] - [Power consumption] - Fail to save: {e}")


    def increase_counter(self, pow_client):
        try:
            power = self.current * self.voltage
            pow_client.set(power)
            total = pow_client.get()

            arduino_logger.info(f"[{self.device_id}] - [Power consumption] - [Accumulated] - {total} W")

            if total >= self.threshold:
                arduino_logger.info(f"[{self.device_id}] - [Power consumption] - [Threshold reached]")
                pow_client.reset(total - self.threshold)  # Reset counter
                self.consumeToken = 1
        except Exception as e:
            arduino_logger.error(f"[{self.device_id}] - [Redis] - increment failed: {e}")



    async def consume_tokens(self):
            result = await sct_client.consume(self.account_address, self.device_id)
            self.tokenConsumed = True
            token_consumption = {}
            token_consumption["device_id"] = self.device_id
            token_consumption["balance"] = self.balance - 1
            token_consumption["tx_hash"] = result
            central_client.consume_token(token_consumption)
    
    @classmethod
    def detect_ports(cls):
        devices = arduino_port_client.get()
        ports = serial.tools.list_ports.comports()
        new_devices = []
        for port in ports:
            if "ACM" in port.device and (
                "Arduino" in port.description or "ttyACM" in port.device
            ):
                if port.device not in devices:
                    arduino_logger.info(f"[Port Detected] - [{port.device}]")
                    new_devices.append(cls(port.device))
                    arduino_port_client.set(port.device)
        return new_devices

if __name__ == "__main__":
    from src.utils.helpers import start_daemon_thread
    import time

    arduino_port_client.clear()
    threads = []
    central_fn_handler.call(central_client.connect)
    with get_db() as db:
        central_fn_handler.run(central_client.sync_devices, db)

    try:
        # device = ArduinoClient('/dev/pts/6')
        # t = start_daemon_thread(device.run)
        # threads.append(t)
        while True:
            devices = ArduinoClient.detect_ports()
            for d in devices:
                t = start_daemon_thread(d.run)
                threads.append(t)
            # Check for new devices every 5 seconds (adjustable)
            time.sleep(5)

    except KeyboardInterrupt:
        print("[Main] KeyboardInterrupt received. Shutting Down...")
        with get_db() as db:
            central_fn_handler.call(central_client.shutdown, db)
        time.sleep(5)
        arduino_port_client.clear()

