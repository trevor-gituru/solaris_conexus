#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);      // LCD object
SoftwareSerial comm(10, 11);            // RX, TX for slave comm

void setup() {
  Serial.begin(9600);                   // Serial Monitor to laptop
  comm.begin(9600);                     // From slave
  lcd.init();                           
  lcd.backlight();
  pinMode(A0, INPUT);                   // Current sensor
}

void loop() {
  // Read master's current
  const int samples = 50;
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(A0);
    delay(2);
  }

  float avg_adc = sum / (float)samples;
  float voltage = avg_adc * 5.0 / 1023.0;
  float currentMaster = (voltage - 2.5) / 0.185;
  if (currentMaster < 0.00) currentMaster *= -1;

  // Read slave's current if available
  float currentSlave = -1;
  if (comm.available()) {
    currentSlave = comm.parseFloat();
  }

  // Send to Serial Monitor
  Serial.print("M, ");
  Serial.println(currentMaster, 2);

  if (currentSlave >= 0) {
    Serial.print("S, ");
    Serial.println(currentSlave, 2);
  } else {
    Serial.println("S, ---");
  }

  // Display on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("M:");
  lcd.print(currentMaster, 2);
  lcd.print("A");

  lcd.setCursor(0, 1);
  lcd.print("S:");
  if (currentSlave >= 0)
    lcd.print(currentSlave, 2);
  else
    lcd.print("---");
  lcd.print("A");

  delay(1000);  // Wait 1 sec
}
