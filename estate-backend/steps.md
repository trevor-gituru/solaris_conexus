pip install pyserial
sudo apt install socat
socat -d -d pty,raw,echo=0 pty,raw,echo=0

Here is your updated Arduino sketch with the requested modes based on keypad input:
✅ Features:

    Typing 0: shows Device ID (H001)

    Typing 1: shows Connection status (0 = off, 1 = on)

    Typing 2: shows Average current

    Typing 3: shows Account balance, or "undable fetch" if disconnected

    Typing 4: toggles LED on pin 7

    Typing 5: displays LED on/off state



