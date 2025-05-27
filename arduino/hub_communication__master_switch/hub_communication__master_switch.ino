#include <Keypad.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <EEPROM.h>

// Keypad setup
const byte row = 4;
const byte col = 4;
char keys[row][col] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'.','0','#','D'},
};
byte rowpins[4] = {9,8,7,6};
byte colpins[4] = {5,4,3,2};
Keypad keypad = Keypad(makeKeymap(keys), rowpins, colpins, row, col);

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2);

// LED pin
#define LED_PIN 10
#define MASTER_PIN 11

// Globals
char lastKey = ' ';
int mode = -1;
float current = 0.0;
bool ledState = false;
bool connectionStatus = false;
float accountBalance = 4.89;
String device_id = "H002";
String req = "read";

// Timers
unsigned long lastCurrentUpdate = 0;
const unsigned long currentInterval = 1000;
unsigned long lastSerialInputTime = 0;
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 1000;

// Variables to reduce flicker
int prevMode = -2;
float prevCurrent = -1.0;
float prevBatteryVoltage = 0.0;
bool prevConnectionStatus = false;
float prevAccountBalance = -1.0;
bool prevLedState = false;
String prevDeviceId = "";

// Variables voltage divider
const int analogPin = A1;       // Analog pin connected to voltage divider
const float R1 = 6700.0;        // 6.7k resistor
const float R2 = 4700.0;        // 4.7k resistor
float batteryVoltage = 0.0;

void setup() {
  Serial.begin(9600);
  while (!Serial);  // Wait for Serial connection

  lcd.init();
  lcd.backlight();

  EEPROM.get(0, ledState);  // safer EEPROM read
  pinMode(LED_PIN, OUTPUT);
  pinMode(MASTER_PIN, OUTPUT);
  digitalWrite(LED_PIN, ledState ? HIGH : LOW);
  digitalWrite(MASTER_PIN, HIGH);
}

void loop() {
  acceptSerialInput();
  acceptKeypadInput();
  updatePower();

  
  // === MASTER SWITCH CONTROL BASED ON BALANCE & CONNECTION ===
  if (accountBalance > 0 && connectionStatus) {
    digitalWrite(MASTER_PIN, HIGH); // Turn ON master switch
  } else {
    digitalWrite(MASTER_PIN, LOW);  // Turn OFF master switch
  }

  if (ledState != prevLedState || millis() - lastSendTime >= sendInterval) {
    sendSerialOutput();
    lastSendTime = millis();
    prevLedState = ledState;
  }

  displayLcd();
}

void acceptKeypadInput() {
  char input = keypad.getKey();
  if (!input) return;

  if (input == 'C') {
    mode = -1;
  } else if (input >= '0' && input <= '6') {
    mode = input - '0';
  } else if (input == 'A') {
    connectionStatus = !connectionStatus;
  }
}

void acceptSerialInput() {
  if (Serial.available()) {
    lastSerialInputTime = millis();

    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() > 0) {
      int commaIndex = input.indexOf(',');
      if (commaIndex > 0) {
        float receivedBalance = input.substring(0, commaIndex).toFloat();
        int receivedInstruction = input.substring(commaIndex + 1).toInt();

        accountBalance = receivedBalance;

        switch (receivedInstruction) {
          case 1:
            connectionStatus = true;
            break;
          case 0:
            connectionStatus = false;
            break;
          case 2:
            ledState = !ledState;
            digitalWrite(LED_PIN, ledState ? HIGH : LOW);
            EEPROM.update(0, ledState);
            break;
        }

      }
    }
  } else if (millis() - lastSerialInputTime > 20000) {
    connectionStatus = false;
  }
}

void updatePower() {
  if (millis() - lastCurrentUpdate >= currentInterval) {
    lastCurrentUpdate = millis();

    const int samples = 50;
    long currentSum = 0;
    long voltageSum = 0;

    for (int i = 0; i < samples; i++) {
      currentSum += analogRead(A0);  // Read current sensor
      voltageSum += analogRead(A1);  // Read voltage divider
      delay(2);  // Minimal delay for stability
    }

    // --- Calculate average values ---
    float avgCurrentADC = currentSum / (float)samples;
    float avgVoltageADC = voltageSum / (float)samples;

    // --- Convert ADC to real-world values ---
    float voltageCurrent = avgCurrentADC * (5.0 / 1023.0);
    current = (voltageCurrent - 2.5) / 0.185;  // Adjust based on sensor

    float voltageAtA1 = avgVoltageADC * (5.0 / 1023.0);
    batteryVoltage = voltageAtA1 * ((R1 + R2) / R2);
  }
}


void sendSerialOutput() {
  if (connectionStatus) {
    String message = "{";
    message += "\"current\":" + String(current, 2) + ",";
    message += "\"voltage\":" + String(batteryVoltage, 2) + ",";
    message += "\"req\":\"" + String(ledState ? "true" : "false") + "\"";
    message += "}";
    Serial.println(message);
  } else {
    Serial.println("{\"device_id\":\"" + device_id + "\"}");
  }
}

void displayLcd() {
  bool shouldUpdate = false;

  if (mode != prevMode) {
    shouldUpdate = true;
  } else {
    switch (mode) {
      case 1:
        if (connectionStatus != prevConnectionStatus) shouldUpdate = true;
        break;
      case 2:
        if (abs(current - prevCurrent) > 0.01) shouldUpdate = true;
        break;
      case 3:
        if (abs(accountBalance - prevAccountBalance) > 0.01 || connectionStatus != prevConnectionStatus)
          shouldUpdate = true;
        break;
      case 4:
        shouldUpdate = true;
        break;
      case 5:
        if (ledState != prevLedState) shouldUpdate = true;
        break;
      case 6:
        if (abs(batteryVoltage - prevBatteryVoltage) > 0.01) shouldUpdate = true;
        break;

      case 0:
        if (device_id != prevDeviceId) shouldUpdate = true;
        break;
    }
  }

  if (!shouldUpdate) return;

  prevMode = mode;
  prevCurrent = current;
  prevConnectionStatus = connectionStatus;
  prevAccountBalance = accountBalance;
  prevLedState = ledState;
  prevDeviceId = device_id;
  prevBatteryVoltage = batteryVoltage;  // Add this

  lcd.clear();

  switch (mode) {
    case 0:
      lcd.setCursor(0, 0);
      lcd.print("Device ID:");
      lcd.setCursor(0, 1);
      lcd.print(device_id);
      break;

    case 1:
      lcd.setCursor(0, 0);
      lcd.print("Connection:");
      lcd.setCursor(0, 1);
      lcd.print(connectionStatus ? "1 (ON)" : "0 (OFF)");
      break;

    case 2:
      lcd.setCursor(0, 0);
      lcd.print("Avg Current:");
      lcd.setCursor(0, 1);
      lcd.print(current, 2);
      lcd.print(" A");
      break;

    case 3:
      lcd.setCursor(0, 0);
      lcd.print("Balance:");
      lcd.setCursor(0, 1);
      if (connectionStatus) {
        lcd.print(accountBalance, 2);
        lcd.print(" SCT");
      } else {
        lcd.print("unable fetch");
      }
      break;

    case 4:
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState ? HIGH : LOW);
      EEPROM.update(0, ledState);
      lcd.setCursor(0, 0);
      lcd.print("LED Toggled");
      lcd.setCursor(0, 1);
      lcd.print(ledState ? "Now ON" : "Now OFF");
      mode = -1;  // Reset mode
      break;

    case 5:
      lcd.setCursor(0, 0);
      lcd.print("LED Status:");
      lcd.setCursor(0, 1);
      lcd.print(ledState ? "ON" : "OFF");
      break;

    case 6:
      lcd.setCursor(0, 0);
      lcd.print("Battery Voltage:");
      lcd.setCursor(0, 1);
      lcd.print(batteryVoltage, 2);
      lcd.print(" V");
      break;
  

    default:
      break;
  }
}
