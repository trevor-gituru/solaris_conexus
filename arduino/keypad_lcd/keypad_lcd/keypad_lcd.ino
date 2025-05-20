#include <Keypad.h>
#include <LiquidCrystal_I2C.h>

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
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
}

void loop() {
  char input = keypad.getKey();
  if (input) {
    lcd.setCursor(0, 0);      // Always go to first column, first row
    lcd.print("                "); // Clear the whole line
    lcd.setCursor(0, 0);      // Reset cursor again
    lcd.print(input);         // Print new key
    Serial.println(input);
  }
}
