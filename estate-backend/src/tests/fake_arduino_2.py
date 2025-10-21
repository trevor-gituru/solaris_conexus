import random
import time
import threading
import serial

SERIAL_PORT = '/dev/pts/1'  # Change to match your virtual serial port
BAUDRATE = 9600

device_id = 'H002'
mode = 3
led_on = False
power = 0
balance = None
last_instruction = 0

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

def read_serial():
    global balance, last_instruction, led_on
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                parts = line.split(',')
                if len(parts) == 2:
                    balance = float(parts[0])
                    last_instruction = int(parts[1])
                    print(f"[Serial] Received balance: {balance}, instruction: {last_instruction}")
                    if last_instruction == 1:
                        led_on = False
                        print("[Serial] Instruction: Turn OFF LED")
        except Exception as e:
            print(f"[Serial Error] {e}")
            balance = None

def main_loop():
    global mode, led_on, power
    while True:
        if mode == 1:
            print(f"Device ID: {device_id}")
        elif mode == 2:
            state = "ON" if led_on else "OFF"
            print(f"LED {state}")
        elif mode == 3:
            power = random.randint(10, 100)
            print(f"Power: {power}W")
        elif mode == 4:
            if balance is not None:
                print(f"Balance: {balance}")
            else:
                print("Error fetching")

        # Send data over serial
        try:
            msg = f"{device_id},{power},{mode}\n"
            ser.write(msg.encode())
        except Exception as e:
            print(f"[Send Error] {e}")

        time.sleep(2)

def input_loop():
    global mode, led_on
    while True:
        cmd = input("Press 1=ID, 2=Toggle LED, 3=Power, 4=Balance, 5=LED state:\n")
        if cmd == '1':
            mode = 1
        elif cmd == '2':
            mode = 2
            led_on = not led_on
        elif cmd == '3':
            mode = 3
        elif cmd == '4':
            mode = 4
        elif cmd == '5':
            print(f"LED is {'ON' if led_on else 'OFF'}")
        else:
            print("Invalid input.")

# Start threads
threading.Thread(target=read_serial, daemon=True).start()
threading.Thread(target=main_loop, daemon=True).start()
input_loop()

