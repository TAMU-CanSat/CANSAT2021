#include <EEPROM.h>
#include "memorymap.h"


void setup() {
  // Default EEPROM state
  EEPROM.update(ADDR_software_state, LAUNCH_WAIT);
  EEPROM.update(ADDR_packet_count, 0);
  EEPROM.update(ADDR_mode, 0);
  EEPROM.update(ADDR_sim_enabled, 0);
  EEPROM.update(ADDR_sp1_released, 0);
  EEPROM.update(ADDR_sp2_released, 0);
  EEPROM.update(ADDR_sp1_packet_count, 0);
  EEPROM.update(ADDR_sp2_packet_count, 0);
  
}

int ledPin = 13;
void loop() {
  // Blink to show completion
  digitalWrite(ledPin, HIGH);
  delay(1000);
  digitalWrite(ledPin, LOW);
  delay(1000);
}
