import serial
import time

# Replace 'COM3' with your Arduino port (e.g., 'COM5' on Windows, '/dev/ttyUSB0' on Linux)
arduino_port = '/dev/ttyACM0'  
baud_rate = 9600        # Match the Arduino's Serial.begin(9600)
timeout = 1             # 1 second timeout for reading

# Create a serial connection
ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)

# Give it a bit of time to establish connection
time.sleep(2)

print("Starting to read from Arduino...")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: {line}")

except KeyboardInterrupt:
    print("Stopped reading.")
    ser.close()
