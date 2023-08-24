#include <LiquidCrystal.h>

LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.print("Start!");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      lcd.setCursor(0, 1); // Move to the next line of the LCD.
    } else if (c == '\r') {
      lcd.clear();        // Clear the LCD.
      lcd.setCursor(0, 0); // Move back to the beginning.
    } else {
      lcd.print(c);       // Print received character to the LCD.
    }
  }
}