# define XBEE_GCS_SERIAL Serial1
# define XBEE_PAYLOAD_SERIAL Serial2

// Can't use define since we need a reference
// # define GPS_SERIAL Serial3

const byte XBEE_GCS_RX = 		0;
const byte XBEE_GCS_TX = 		1;
const byte SERVO_PWM = 			6;
const byte XBEE_PAYLOAD_RX = 	7;
const byte XBEE_PAYLOAD_TX = 	8;
const byte GPS_TX = 			14;
const byte GPS_RX = 			15;
const byte GPS_ENABLE = 		16;
const byte I2C_SDA = 			18;
const byte I2C_SCL = 			19;

// TODO WAITING TO HEAR THE EXACT PIN FROM EE
const byte VOLTAGE_PIN = 		23;

const byte AUDIO_BEACON =       4;
