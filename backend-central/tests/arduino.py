import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)  # Change to your port
time.sleep(2)  # Wait for Arduino reset

while True:
    if ser.in_waiting:
        print("From Arduino:", ser.readline().decode().strip())

    # Send command every 5 seconds
    ser.write(b"15.2,0\n")
    time.sleep(5)

