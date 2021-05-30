#include <EEPROM.h>
#include "memorymap.h"


void setup() {
  unsigned int unsInt = 0;
  
  // Default EEPROM state
  EEPROM.update(ADDR_software_state, NOT_DEPLOYED);
  EEPROM.put(ADDR_packet_count, unsInt);
}

int ledPin = 13;
void loop() {
  // Blink to show completion
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}
