#include <Keypad.h>
#include <SoftwareSerial.h>

const byte row = 4;
const byte col = 4;

char keys[row][col] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'.','0','#','D'},
};

byte rowpins[4] = {12,11,10,9};
byte colpins[4] = {8,7,6,5};

Keypad keypad = Keypad(makeKeymap(keys), rowpins, colpins, row, col);

// Create software serial connection to Arduino B
SoftwareSerial link(10, 11); // RX, TX

void setup() {
  Serial.begin(9600);
  link.begin(9600);
}

void loop() {
  char key = keypad.getKey();
  if (key) {
    link.print(key);  // Send character to Arduino B
    Serial.println(key);
  }
}
