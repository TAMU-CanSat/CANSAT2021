// Used to offset EEPROM addresses to not overstress individual bytes
short EEPROM_OFFSET = 0;  

// Container memory map, each value is an eeprom addr
short ADDR_software_state = 		0  + EEPROM_OFFSET;
short ADDR_time_ss = 			1  + EEPROM_OFFSET;
short ADDR_time_mm = 			2  + EEPROM_OFFSET;
short ADDR_time_hh = 			3  + EEPROM_OFFSET;
short ADDR_packet_count = 		4  + EEPROM_OFFSET;
short ADDR_mission_time_ss = 	8  + EEPROM_OFFSET;
short ADDR_mission_time_mm = 	9  + EEPROM_OFFSET;
short ADDR_mission_time_hh = 	10 + EEPROM_OFFSET;
short ADDR_mode = 				24 + EEPROM_OFFSET;
short ADDR_sim_enabled = 		25 + EEPROM_OFFSET;
short ADDR_sim_pressure = 		26 + EEPROM_OFFSET;
short ADDR_sp1_released = 		30 + EEPROM_OFFSET;
short ADDR_sp2_released = 		31 + EEPROM_OFFSET;
short ADDR_sp1_packet_count = 	32 + EEPROM_OFFSET;
short ADDR_sp2_packet_count = 	36 + EEPROM_OFFSET;

// State aliases
byte LAUNCH_WAIT = 1;
byte ASCENT_LAUNCHPAD = 2;
byte DESCENT = 3;
byte SP1_RELEASE = 4;
byte SP2_RELEASE = 5;
byte LANDED = 6;