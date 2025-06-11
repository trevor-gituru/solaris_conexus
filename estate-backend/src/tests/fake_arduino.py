import serial
import time
import json
import random

# Use your actual virtual port here
SERIAL_PORT = "/dev/pts/3"  # Or COM3 on Windows
BAUD_RATE = 9600

account_balance = 4.89
connection_status = False
led_state = False
device_id = "H001"
current = 0.0
battery_voltage = 3.7

def get_current():
    return round(random.uniform(0.2, 0.6), 2)

def get_battery_voltage():
    return round(random.uniform(3.5, 4.2), 2)

def build_status_message():
    return json.dumps({
        "current": current,
        "voltage": battery_voltage,
        "req": "true" if led_state else "false"
    })

def build_idle_message():
    return json.dumps({
        "device_id": device_id
    })

def main():
    global current, battery_voltage, connection_status, account_balance, led_state
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    
    last_send = time.time()
    last_recv = time.time()

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"[Estate Hub → Simulated Arduino] {line}")
                    last_recv = time.time()
                    try:
                        if "," in line:
                            balance_str, instruction_str = line.split(",")
                            account_balance = float(balance_str)
                            instruction = int(instruction_str)

                            if instruction == 0:
                                connection_status = False
                            elif instruction == 1:
                                connection_status = True
                            elif instruction == 2:
                                led_state = not led_state

                    except Exception as e:
                        print("Error parsing serial input:", e)

            # Auto-disconnect after 10s of inactivity
            if time.time() - last_recv > 10:
                connection_status = False

            # Send data every second
            if time.time() - last_send > 1:
                current = get_current()
                battery_voltage = get_battery_voltage()
                if connection_status:
                    ser.write((build_status_message() + "\n").encode())
                    print("[Arduino → Estate Hub] Sent status.")
                else:
                    ser.write((build_idle_message() + "\n").encode())
                    print("[Arduino → Estate Hub] Sent ID only.")
                last_send = time.time()

            time.sleep(0.1)

    except KeyboardInterrupt:
        ser.close()
        print("Serial closed. Exiting...")

if __name__ == "__main__":
    main()


