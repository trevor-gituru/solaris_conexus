import serial
import json
import time, threading
from datetime import datetime
from db.database import SessionLocal, get_db 
from db.models import Device, PowerConsumption
from sqlalchemy.orm import Session


class ArduinoDevice:
    def __init__(self, port, baud=9600):
        self.port = port
        self.baud = baud
        self.serial = None
        self.device_id = None
        self.current = 0.0
        self.voltage = 0.0
        self.timestamp = None
        self.id = None  # DB Device.id numeric
        self.balance = 0.0
        self.instruction = 1  # Default instruction

    def connect_with_retry(self):
        """Try to connect to the Arduino port every 5 seconds until successful."""
        while self.serial is None:
            try:
                print(f"[Info] Trying to connect to {self.port}...")
                self.serial = serial.Serial(self.port, self.baud, timeout=1)
                time.sleep(2)  # Allow Arduino to reset
                print(f"[Success] Connected to {self.port}")
            except serial.SerialException:
                print(f"[Warning] {self.port} not available. Retrying in 30 seconds...")
                time.sleep(30)

    def connect(self, db_session: Session):
        """
        Reads serial input and sets the device ID from JSON until a 'current' reading is received.
        Keeps sending instructions during the connection handshake.
        """
        self.serial.flushInput()
        last_received = time.time()
        timeout_seconds = 2

        while True:
            if self.serial.in_waiting:
                try:
                    line = self.serial.readline().decode().strip()
                    print(f"[Raw] {line}")
                    
                    if not line.startswith('{'):
                        continue  # Skip non-JSON lines

                    data = json.loads(line)

                    if "device_id" in data and self.device_id is None:
                        self.device_id = data["device_id"]

                        # Lookup device in DB if not already done
                        if self.id is None:
                            device = db_session.query(Device).filter(Device.device_id == self.device_id).first()
                            if not device:
                                print(f"[Error] Device with device_id '{self.device_id}' not found in DB.")
                                return None
                            self.id = device.id
                            self.balance = device.token_balance

                        print(f"[Info] Received device ID: {self.device_id}")
                        self.send_data()  # Keep sending initial instruction
                        last_received = time.time()

                    # Exit condition when 'current' data is received
                    if "current" in data:
                        print("[Info] Received 'current' reading; exiting connect()")
                        return

                except json.JSONDecodeError:
                    print("[Warning] Invalid JSON received, ignoring...")
                except Exception as e:
                    print(f"[Error] Exception in connect(): {e}")
            else:
                if time.time() - last_received > timeout_seconds:
                    print(f"[Info] Timeout waiting for data. Last device_id: {self.device_id}")
                    return
            time.sleep(0.1)

    def send_data(self):
        """
        Sends balance and instruction to Arduino as a comma-separated string.
        Format: "<balance>,<instruction>\n"
        """
        message = f"{self.balance},{self.instruction}\n"
        try:
            self.serial.write(message.encode())
            print(f"[Sent] {message.strip()}")
        except Exception as e:
            print(f"[Error] Failed to send data: {e}")

    def read_power(self):
        """
        Reads a JSON-formatted line from serial port.
        Updates current, voltage, timestamp, and request type.
        """
        self.clear_serial_buffer()
        if self.serial.in_waiting:
            try:
                line = self.serial.readline().decode().strip()
                print(f"[Raw] {line}")
                
                if not line.startswith('{'):
                    print("[Info] Non-JSON line received; skipping...")
                    return

                data = json.loads(line)
                self.current = data.get("current", 0.0)
                self.voltage = data.get("voltage", 0.0)
                self.timestamp = datetime.utcnow()
                self.req = data.get("req")

                print(f"[Decoded] Current: {self.current} A, Voltage: {self.voltage} V, Request: {self.req}")

            except json.JSONDecodeError:
                print("[Warning] Invalid JSON received while reading power.")
            except Exception as e:
                print(f"[Error] Exception in read_power(): {e}")
        else:
            print("[Info] No serial data available to read.")

    def add_power_consumption(self, db_session: Session):
        """
        Inserts a PowerConsumption record into the database.
        Ensures device id is known.
        """
        if self.id is None:
            device = db_session.query(Device).filter(Device.device_id == self.device_id).first()
            if not device:
                print(f"[Error] Device with device_id '{self.device_id}' not found in DB.")
                return None
            self.id = device.id

        timestamp = self.timestamp or datetime.utcnow()

        power_data = {
            "device_id": self.id,
            "voltage": self.voltage,
            "current": self.current,
            "timestamp": timestamp
        }

        try:
            power_record = PowerConsumption.create(db_session, power_data)
            print("[Info] Power consumption recorded successfully:", {power_record.id})
            return power_record
        except Exception as e:
            print(f"[Error] Failed to add power consumption: {e}")
            return None

    def update_state(self, db: Session):
        """
        Syncs local state from DB and sends instructions to Arduino accordingly.
        """
        device = db.query(Device).filter(Device.device_id == self.device_id).first()
        if device:
            self.balance = device.token_balance
            self.instruction = device.instruction

            if self.instruction == 2:
                self.send_data()
                device.instruction = 1  # Reset instruction in DB
                db.commit()
            elif self.instruction == 1:
                self.send_data()

    def start_monitoring_loop(self, db: Session):
        """
        Starts the main loop for monitoring and communication with Arduino.
        """
        self.connect_with_retry()
        self.connect(db)

        while True:
            self.update_state(db)
            self.read_power()
            self.add_power_consumption(db)
            time.sleep(2)

    def clear_serial_buffer(self):
        """
        Clears the serial input buffer to avoid stale data.
        """
        self.serial.reset_input_buffer()  # or: self.serial.flushInput()
        time.sleep(1)  # Wait a bit for new data to come in

    def run_with_retry(self):
        """
        This replaces the external monitor_device(). Continuously tries to connect
        and run the monitoring loop. Recovers from disconnections.
        """
        while True:
            try:
                db: Session = next(get_db())  # Fresh DB session each cycle
                self.connect_with_retry()
                self.connect(db)
                self.start_monitoring_loop(db)
            except (serial.SerialException, OSError) as e:
                print(f"[{self.port}] Disconnected or error: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                print(f"[{self.port}] Unexpected error: {e}. Retrying in 30 seconds...")
                time.sleep(30)
            finally:
                try:
                    db.close()
                except:
                    pass

    def start_threaded_monitoring(self):
        """
        Spawns a daemon thread to run monitor with retries.
        """
        t = threading.Thread(target=self.run_with_retry, daemon=True)
        t.start()
        return t  # Optional: return thread if you want to keep track


