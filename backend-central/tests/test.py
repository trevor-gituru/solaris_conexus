import serial.tools.list_ports

# List all available serial ports
ports = serial.tools.list_ports.comports()

# Look for the Arduino ACM port
arduino_port = None
for port in ports:
    if 'ACM' in port.device:  # Check if ACM is in the port description
        arduino_port = port.device
        break

if arduino_port:
    print(f"Arduino found on {arduino_port}")
else:
    print("No Arduino found.")
