#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
SoftwareSerial slaveSerial(10, 11); // RX = 10, TX = 11 (use TX only if sending back)

void setup() {
  Serial.begin(9600);       // To PC
  slaveSerial.begin(9600);  // To slave Arduino
  lcd.init();
  lcd.backlight();
}

void loop() {
  // Read master analog input
  const int samples = 50;
  long sum = 0;

  for (int i = 0; i < samples; i++) {
    sum += analogRead(A0);
    delay(2);
  }

  float avg_adc = sum / (float)samples;
  float voltage = avg_adc * 5.0 / 1023.0;
  float current_master = (voltage - 2.5) / 0.185;

  // Read data from slave
  String slaveData = "";
  if (slaveSerial.available()) {
    slaveData = slaveSerial.readStringUntil('\n');
  }

  // Display on Serial Monitor
  Serial.print("Master Current: ");
  Serial.print(current_master, 2);
  Serial.print(" A | Slave: ");
  Serial.println(slaveData); // slaveData should contain current in A

  // Display on LCD (master value)
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("M: ");
  lcd.print(current_master, 2);
  lcd.print(" A");

  lcd.setCursor(0, 1);
  lcd.print("S: ");
  lcd.print(slaveData);

  delay(1000);
}
