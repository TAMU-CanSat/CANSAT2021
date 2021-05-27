// Used to offset EEPROM addresses to not overstress individual bytes
const short EEPROM_OFFSET = 0;  

// Container memory map, each value is an eeprom addr
const short ADDR_software_state = 		0  + EEPROM_OFFSET;
const short ADDR_time_ss = 				1  + EEPROM_OFFSET;
const short ADDR_time_mm = 				2  + EEPROM_OFFSET;
const short ADDR_time_hh = 				3  + EEPROM_OFFSET;
const short ADDR_packet_count = 		4  + EEPROM_OFFSET;

// These aren't used since they'd be redundant over the RTC
// const short ADDR_mission_time_ss = 		8  + EEPROM_OFFSET;
// const short ADDR_mission_time_mm = 		9  + EEPROM_OFFSET;
// const short ADDR_mission_time_hh = 		10 + EEPROM_OFFSET;

const byte end_transmission_ss =        55 + EEPROM_OFFSET;
const byte end_transmission_mm =        56 + EEPROM_OFFSET;
const byte end_transmission_hh =        57 + EEPROM_OFFSET;

// software_state alises
const byte NOT_DEPLOYED = 1;
const byte DEPLOYED = 2;
const byte LANDED = 3;
const byte END_TRANSMISSION = 4;