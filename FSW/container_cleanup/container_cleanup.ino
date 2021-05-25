#include <EEPROM.h>

// COPY FROM MEMORYMAP.h IN CONTAINER
const short EEPROM_OFFSET = 0;  

// Container memory map, each value is an eeprom addr
const short ADDR_software_state =     0  + EEPROM_OFFSET;
// END COPIED REGION


void setup() {
  // Default EEPROM state
  EEPROM.update(ADDR_software_state, 1);
}

int ledPin = 13;
void loop() {
  // Blink to show completion
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}
