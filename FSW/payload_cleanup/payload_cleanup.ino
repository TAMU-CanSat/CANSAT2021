#include <EEPROM.h>
#include "memorymap.h"


void setup() {
  // Default EEPROM state
  EEPROM.update(ADDR_software_state, NOT_DEPLOYED);
  EEPROM.update(ADDR_packet_count, 0);
  EEPROM.update(ADDR_sim_enabled, 0);
}

int ledPin = 13;
void loop() {
  // Blink to show completion
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}
