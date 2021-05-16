// Used to offset EEPROM addresses to not overstress individual bytes
const short EEPROM_OFFSET = 0;  

// Container memory map, each value is an eeprom addr
const short ADDR_software_state = 		0  + EEPROM_OFFSET;
const short ADDR_time_ss = 			1  + EEPROM_OFFSET;
const short ADDR_time_mm = 			2  + EEPROM_OFFSET;
const short ADDR_time_hh = 			3  + EEPROM_OFFSET;
const short ADDR_packet_count = 		4  + EEPROM_OFFSET;
const short ADDR_mission_time_ss = 	8  + EEPROM_OFFSET;
const short ADDR_mission_time_mm = 	9  + EEPROM_OFFSET;
const short ADDR_mission_time_hh = 	10 + EEPROM_OFFSET;
const short ADDR_mode = 				24 + EEPROM_OFFSET;
const short ADDR_sim_enabled = 		25 + EEPROM_OFFSET;
const short ADDR_sim_pressure = 		26 + EEPROM_OFFSET;
const short ADDR_sp1_released = 		30 + EEPROM_OFFSET;
const short ADDR_sp2_released = 		31 + EEPROM_OFFSET;
const short ADDR_sp1_packet_count = 	32 + EEPROM_OFFSET;
const short ADDR_sp2_packet_count = 	36 + EEPROM_OFFSET;

// State aliases
const byte LAUNCH_WAIT = 1;
const byte ASCENT_LAUNCHPAD = 2;
const byte DESCENT = 3;
const byte SP1_RELEASE = 4;
const byte SP2_RELEASE = 5;
const byte LANDED = 6;