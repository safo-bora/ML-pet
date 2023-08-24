#define LED_PIN_13 13
#define LED_PIN_12 12
#define LED_PIN_11 11
#define LED_PIN_10 10
#define LED_PIN_9 9

void setup() {
  Serial.begin(9600); // Start serial at 9600 bps

  pinMode(LED_PIN_13, OUTPUT);
  pinMode(LED_PIN_12, OUTPUT);
  pinMode(LED_PIN_11, OUTPUT);
  pinMode(LED_PIN_10, OUTPUT);
  pinMode(LED_PIN_9, OUTPUT);
}


void loop() {
  if (Serial.available()) {  // check if there's incoming data
    char c = Serial.read();  // read the incoming data

    switch(c) {
      case '1': digitalWrite(LED_PIN_13, !digitalRead(LED_PIN_13)); break; // Toggle LED_PIN_13
      case '2': digitalWrite(LED_PIN_12, !digitalRead(LED_PIN_12)); break; // Toggle LED_PIN_12
      case '3': digitalWrite(LED_PIN_11, !digitalRead(LED_PIN_11)); break; // Toggle LED_PIN_11
      case '4': digitalWrite(LED_PIN_10, !digitalRead(LED_PIN_10)); break; // Toggle LED_PIN_10
      case '5': digitalWrite(LED_PIN_9, !digitalRead(LED_PIN_9)); break; // Toggle LED_PIN_9

      case 'a': digitalWrite(LED_PIN_13, LOW); break; // Turn off LED_PIN_13
      case 'b': digitalWrite(LED_PIN_12, LOW); break; // Turn off LED_PIN_12
      case 'c': digitalWrite(LED_PIN_11, LOW); break; // Turn off LED_PIN_11
      case 'd': digitalWrite(LED_PIN_10, LOW); break; // Turn off LED_PIN_10
      case 'e': digitalWrite(LED_PIN_9, LOW); break; // Turn off LED_PIN_9

      case 'A': // Command to turn off all LEDs
        digitalWrite(LED_PIN_13, LOW);
        digitalWrite(LED_PIN_12, LOW);
        digitalWrite(LED_PIN_11, LOW);
        digitalWrite(LED_PIN_10, LOW);
        digitalWrite(LED_PIN_9, LOW);
        break;
    }
  }
}
