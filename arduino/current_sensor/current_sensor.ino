  #include <Wire.h>
#include <LiquidCrystal_I2C.h>
int chargingPin = A5;
int ledPin = 13;
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
}

void loop() {
  const int samples = 50;   // Number of samples to average
  long sum = 0;

  // Take 50 readings
  for (int i = 0; i < samples; i++) {
    sum += analogRead(A0);
    delay(2);
  }

  // Calculate average ADC value
  float avg_adc = sum / (float)samples;
  float voltage = avg_adc * 5.0 / 1023.0;
  float current = (voltage - 2.5) / 0.185;

// 

  //Serial.print("Voltage: ");
  Serial.print(voltage, 2);
  Serial.print(", ");
  //Serial.print("Current: ");
  Serial.println(current, 2);
  //Serial.println(", ");

  // Display on LCD
  lcd.clear();          // Clear screen before writing new data

  lcd.setCursor(0, 0);   // First line
  lcd.print("V: ");
  lcd.print(voltage, 2);
  lcd.print(" V");

  lcd.setCursor(0, 1);   // Second line
  lcd.print("I: ");
  lcd.print(current, 2);
  lcd.print(" A");
  digitalWrite(ledPin, HIGH);

  //int state = analogRead(chargingPin);
  //Serial.println(state);

  delay(500);
}
