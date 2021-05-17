// Compiler flags
#define SERIAL_DEBUG true

// Libraries
#include <EEPROM.h>
#include <Wire.h>
#include <Servo.h>

// Hardware libraries
#include <RTClib.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GPS.h>
#include <XBee.h>

// Sensors/Hardware declarations
RTC_PCF8523 rtc;
Adafruit_BMP280 bmp;
Adafruit_GPS gps(&Wire);
XBee xbee_gcs;
XBee xbee_payload;


// Structs
struct Time {
  byte seconds;
  byte minutes;
  byte hours;
};

struct GPS_struct {  // Used to encapsulate GPS information
  float latitude;
  float longitude;
  float altitude;
  byte sats;
  Time time;
};


// Constants
#include "memorymap.h"  // Includes addresses for EEPROM & software_state alises
const short TEAM_ID = 2743;
const float SEALEVEL_HPA = 1014.2235055;  // !NOTE: Set to sealevel pressure in hPa!

// Variable declarations
Time          rtc_time_old;  // Tracks rtc time before last shutdown
Time          mission_time;

byte          software_state = 0;

bool          mode = false;  // Alias sim_active
bool          sim_enable = false;
bool          sp1_released = false;
bool          sp2_released = false;

unsigned int  sim_pressure = 0;
unsigned int  packet_count;
unsigned int  sp1_packet_count;
unsigned int  sp2_packet_count;

GPS_struct    GPS_data;

float altitude;

// Other variables
short state_transition_tracker        = 0;  // Used to track cycles for transition points between states
short state_transition_tracker_state  = -1;

void setup() {
#if SERIAL_DEBUG
  Serial.begin(9600);
  while (!Serial);
#endif
  
// RTC init
if (!rtc.begin()) {
    #if SERIAL_DEBUG
      Serial.println("INIT FAILED: RTC.BEGIN() RETURNED FALSE");
      Serial.flush();
    #endif
    abort();
  }


//TODO XBee init








// BEGIN READ EEPROM
rtc_time_old.seconds  = EEPROM.read(ADDR_time_ss);
rtc_time_old.minutes  = EEPROM.read(ADDR_time_mm);
rtc_time_old.hours    = EEPROM.read(ADDR_time_hh);
mission_time.seconds  = EEPROM.read(ADDR_mission_time_ss);
mission_time.minutes  = EEPROM.read(ADDR_mission_time_mm);
mission_time.hours    = EEPROM.read(ADDR_mission_time_hh);

software_state        = EEPROM.read(ADDR_software_state);

mode                  = EEPROM.read(ADDR_mode);
sim_enable            = EEPROM.read(ADDR_sim_enabled);
sp1_released          = EEPROM.read(ADDR_sp1_released);
sp2_released          = EEPROM.read(ADDR_sp2_released);

EEPROM.get(ADDR_sim_pressure, sim_pressure);
EEPROM.get(ADDR_packet_count,     packet_count);
EEPROM.get(ADDR_sp1_packet_count, sp1_packet_count);
EEPROM.get(ADDR_sp2_packet_count, sp2_packet_count);
// END READ EEPROM



// Init sensors if we're waiting for launch or landed
if (software_state != LAUNCH_WAIT && software_state != LANDED){
  // BMP
    if (!bmp.begin()) {
    #if SERIAL_DEBUG
      Serial.println("INIT FAILED: BMP.BEGIN() RETURNED FALSE");
      Serial.flush();
    #endif
    abort();
  }

  // GPS
  if (!gps.begin(0x10)) {
    #if SERIAL_DEBUG
      Serial.println("INIT FAILED: GPS.BEGIN() RETURNED FALSE");
      Serial.flush();
    #endif
    abort();
  }
  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);  // Set recommended minimum data + altitude
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);  // Set update interval
  
}}

// ---------------------

void loop() {
switch (software_state){
case LAUNCH_WAIT:
  // Do nothing, wait for XBee command 'CXON'
  return;

break;
case ASCENT_LAUNCHPAD:
  // Check the transition tracker, update accordingly
  if (state_transition_tracker_state == -1){
    // Just initialized, update to 0, set current altitude
    state_transition_tracker_state = 0;
    altitude = get_altitude();
    state_transition_tracker = altitude;
    
  } else if (state_transition_tracker_state == 0){
    // State 0, check for rapidly increasing altitude over time
    short new_altitude = get_altitude();
    if (new_altitude > altitude + 5){
      state_transition_tracker += 1;

      // If we've seen rapidly increasing altitude for 3 seconds, move on to the next state
      if (state_transition_tracker == 3){
        state_transition_tracker_state = 1;
        state_transition_tracker = 0;
      }
    }

    altitude = new_altitude;  // Update altitude
    
  } else if (state_transition_tracker_state == 1){
    // State 1, check for decreasing altitude over time
    short new_altitude = get_altitude();
    if (new_altitude < altitude - 1){
      state_transition_tracker += 1;

      // If we've seen decreasing altitude for 3 seconds, reset trackers and change software state
      if (state_transition_tracker == 3){
        state_transition_tracker_state = -1;
        state_transition_tracker = -1;

        // Update software state
        software_state = DESCENT;
        EEPROM.write(ADDR_software_state, software_state);
      }
    }

    altitude = new_altitude;  // Update altitude
  }

  
  send_packet_gcs();

break;
case DESCENT:





break;
case SP1_RELEASE:
  if (!sp1_released){
    release_sp1();
    
  }




break;
case SP2_RELEASE:
  if (!sp2_released){
    release_sp2();
    sp2_released = true;
    EEPROM.write(ADDR_sp2_released, 1);
  }




break;
case LANDED:






break;

// Mission time is set before launch, so we only worry about it in the Ascent/Launchpad state
if (software_state != LAUNCH_WAIT){
  // TODO Update time stuff

  
}
}}




Time get_rtc_time(){
  Time time_info;
  DateTime now = rtc.now();
  
  time_info.seconds = now.second();
  time_info.minutes = now.minute();
  time_info.hours   = now.hour();
  
  return time_info;
}


float get_temperature(){
  return bmp.readTemperature();
}

float get_pressure(){
  return bmp.readPressure();
}

float get_altitude(){
  return bmp.readAltitude(SEALEVEL_HPA);
}

GPS_struct get_gps(){
  GPS_struct gps_info;

  // Loop until we have a full NMEA sentence and it parses successfully
  char c;
  do {
    c = gps.read();
    while (!gps.newNMEAreceived()) {
      c = gps.read();
      }
  } while (!gps.parse(gps.lastNMEA()));

  gps_info.time.seconds = gps.seconds;
  gps_info.time.minutes = gps.minute;
  gps_info.time.hours   = gps.hour;
  gps_info.latitude = gps.latitude;
  gps_info.longitude = gps.longitude;
  gps_info.altitude = gps.altitude;
  gps_info.sats = (byte)(unsigned int)gps.satellites;  // We do this double conversion to avoid signing issues

  return gps_info;
}

float get_voltage(){
  float voltage;
  // TODO Work with Logan to determine which pins need to be read and what equations need to be used
  return voltage;
}


void release_sp1(bool confirm){
  if (confirm){
    //TODO Release payload 1

  }
}


void release_sp2(bool confirm){
  if (confirm){
    //TODO Release payload 2
    
  }
}

// Polls sensors and global variables before constructing and sending a new packet to GCS
void send_packet_gcs(){
  

}
