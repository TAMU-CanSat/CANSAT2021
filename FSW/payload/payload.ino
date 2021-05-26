// Compiler flags
#define SERIAL_DEBUG true
#define SP1 true

// Libraries
#include <EEPROM.h>
#include <Wire.h>

// Hardware libraries
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_GPS.h>

// Sensors/Hardware declarations
Adafruit_BMP280 bmp;
Adafruit_MPU6050 mpu;

// Structs
struct Time {
  byte seconds;
  byte minutes;
  byte hours;
};

// Variable declarations
Time          last_time;

byte          software_state = 0;

unsigned int  packet_count;

float altitude;
float rotation_rate;

String cmd_echo = "";

// Constants
#include "memorymap.h"  // Includes addresses for EEPROM and Serial aliases
#include "pins.h"
const short TEAM_ID = 2743;
const float SEALEVEL_HPA = 1014.2235055;  // !NOTE: Set to sealevel pressure in hPa!


// Functions
float get_temperature() {
  return bmp.readTemperature();
}

float get_altitude() {
  return bmp.readAltitude(SEALEVEL_HPA);
}

float get_voltage() {
  // TODO Waiting for EE FOR EXACT PIN, UPDATE IN 'pins.h'
  float voltage = analogRead(VOLTAGE_PIN);

  // Map to range, 1023 = 7.2v
  return map(voltage, 0, 1023, 0, 7.2);
}

float get_rotation(){
  // TODO WRITE ME
}

// Polls sensors and global variables before constructing and sending a new packet to GCS
void send_packet() {
  String payload = String(TEAM_ID) + ",";

  // Mission time
  Time mtime = mission_time;
  if (mtime.hours < 10) {
    payload += "0";
  }
  payload += String(mtime.hours) + ":";

  if (mtime.minutes < 10) {
    payload += "0";
  }
  payload += String(mtime.minutes) + ":";

  if (mtime.seconds < 10) {
    payload += "0";
  }
  payload += String(mtime.seconds) + ",";

  // Packet info
  packet_count += 1;
  EEPROM.put(ADDR_packet_count, packet_count);

#if SP1
  payload += String(packet_count) + ",SP1,";
#else
  payload += String(packet_count) + ",SP2,";
#endif

  // Altitude
  payload += String(altitude) + ",";

  // Temperature
  float temp = get_temperature();
  payload += String(temp) + ",";

  // Rotation rate
  float rr = get_rotation();
  payload += String(rr) + ",";

  // Voltage
  float voltage = get_voltage();
  payload += String(voltage) + ",";

  // cmd echo
  payload += cmd_echo + "\n";

  // Send the packet
  XBEE_SERIAL.write(payload.c_str());

}


void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}
