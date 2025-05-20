#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);


void setup() {
  lcd.init();
  lcd.backlight();
  Serial.begin(9600);
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);
}

void loop() {
  const int samples = 50;
  long sum = 0;

  for (int i = 0; i < samples; i++) {
    sum += analogRead(A0);
    delay(2);
  }

  float avg_adc = sum / (float)samples;
  float voltage = avg_adc / 1023.0;
  float current = (voltage - 2.5) / 0.185;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Avg I: ");
  lcd.print(current, 2);
  lcd.print(" A");
  Serial.println(current, 2);

  delay(500);
}
