#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD I2C address 0x27, 16 columns, 2 rows
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();         // Specify dimension
  lcd.backlight();          // Turn on backlight
  lcd.setCursor(2, 0);      // Start at top-left
  lcd.print("Hello WWWWWWWW");       // Print to LCD
}

void loop() {

}
