// Compiler flags, CRITICAL NOTE: SET ALL TO FALSE BEFORE PUSHING FOR FLIGHT OR IT WILL HANG IN SETUP
#define DEBUG true
#define SERIAL_DEBUG true
#define DEBUG_2 true  // Used to debug command receipt for SPXON

// CRITICAL NOTE: SP1 COMPILER FLAG NEEDS TO BE TRUE WHEN COMPILING FOR SP1 AND FALSE WHEN COMPILING FOR SP2
#define SP1 false

// Libraries
#include <EEPROM.h>
#include <Wire.h>
#include <TimeLib.h>

// Hardware libraries
#include <Adafruit_BMP3XX.h>
#include <Adafruit_MPU6050.h>

// Sensors/Hardware declarations
Adafruit_BMP3XX bmp;
Adafruit_MPU6050 mpu;


// Structs
struct Time {
  byte seconds;
  byte minutes;
  byte hours;
};


// Variable declarations
Time          old_time;
Time          mission_time;
Time          end_transmission;

byte          software_state = 0;

unsigned int  packet_count = 0;

float altitude;
float rotation_rate;

String cmd_echo = "";

short transition_tracker = 0;


// Constants
#include "memorymap.h"  // Includes addresses for EEPROM and Serial aliases
#include "pins.h"
const short TEAM_ID = 2743;
const float SEALEVEL_HPA = 1014.6F;  // CRITICAL NOTE: Set to sealevel pressure in hPa!


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
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  float radsPS = g.gyro.z;
  int rpm = round(9.549297 * radsPS);

  // We only want to report positive RPMs, direction isn't important
  if (rpm < 0){
    rpm = rpm * -1;
  }
  
  return rpm;
}


Time get_time() {
  Time time_info;

  time_info.seconds = second();
  time_info.minutes = minute();
  time_info.hours   = hour();

  return time_info;
}


// Polls sensors and global variables before constructing and sending a new packet to GCS
void send_packet() {
   #if DEBUG_2
   Serial.print("SOFTWARE_STATE: ");
   Serial.println(software_state);
   #endif

  
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
    payload += String(packet_count) + ",S1,";
  #else
    payload += String(packet_count) + ",S2,";
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
  XBEE_CONTAINER.write(payload.c_str());

  #if SERIAL_DEBUG
    Serial.print("PACKET: ");
    Serial.println(payload);
  #endif

  #if SERIAL_DEBUG
    Serial.println("PACKET SENT");
  #endif

}


void update_software_state(const byte newState) {
  software_state = newState;
  EEPROM.update(ADDR_software_state, newState);
}


void SetEndTransmission(){
  Time now = get_time();
  end_transmission.seconds = now.seconds;

  if (now.minutes < 55){
    end_transmission.minutes = now.minutes + 5;
    end_transmission.hours = now.hours;
  } else {
    end_transmission.minutes = now.minutes - 55;
    end_transmission.hours = now.hours + 1;
  }

  EEPROM.update(end_transmission_ss, end_transmission.seconds);
  EEPROM.update(end_transmission_mm, end_transmission.minutes);
  EEPROM.update(end_transmission_hh, end_transmission.hours);

}


void XBee_receive() {
  // STEP 1: Loop until terminator (\n) found || 100 ms pass (junk and start over)
  // STEP 2: Process, if payload packet forward on as is
  // STEP 3: If GCS cmd, process as needed
  // STEP 4: Profit

  // Read characters from XBee if available
  String workingString = "";
  if (XBEE_CONTAINER.available()) {
    delay(50);
    char c;
    while (XBEE_CONTAINER.available()) {
      c = XBEE_CONTAINER.read();
      if (c != '\n'){
        workingString += c;
      } else {
        break;
      }
    }

    #if SERIAL_DEBUG
      Serial.print("PACKET RECEIVED: ");
      Serial.println(workingString);
    #endif

    // Validate a cmd string
    if (workingString.startsWith("CMD")){
      // Check string at minimum contains 9 characters
      if (workingString.length()<= 9) {
        return;
      }
      
      // Remove 'CMD,2743,' (9 chars) to determine cmd type
      workingString.remove(0,9);

    #if SP1
      if (workingString.startsWith("SP1X,ON")){
        
        update_software_state(DEPLOYED);
        cmd_echo = "SP1XON";
        SetEndTransmission();
      }
    #else
      if (workingString.startsWith("SP2X,ON")){
        update_software_state(DEPLOYED);
        cmd_echo = "SP2XON";
        SetEndTransmission();
      }
    #endif
      else if (workingString.startsWith("ST")) {
        // Check string is long enough to process as an ST
        if (workingString.length() < 11) {
          return;
        }
        
        String STpayloadCopy = "CMD," + String(TEAM_ID) + "," + workingString + "\n";
        
        workingString.remove(0,3);
        cmd_echo = "ST" + workingString;  // Out of place command echo to save on formatting

        int sec = atoi(workingString.substring(6, 8).c_str());
        int min = atoi(workingString.substring(3, 5).c_str());
        int hr = atoi(workingString.substring(0, 2).c_str());

        // Set time (we really don't care about the date)
        setTime(hr, min, sec, 1, 1, 2021);
      }
    } 
  }
}


// End function definitions


void setup() {
  #if DEBUG
  Serial.begin(9600);
  while (!Serial);
  #endif

  #if DEBUG
  Wire.begin();
  Serial.println("WIRE BEGIN SUCCESS");
  #endif

  // XBee init
  XBEE_CONTAINER.begin(9600);

  #if DEBUG
  Serial.println("XBEE INIT COMPLETE");
  #endif

  // BEGIN READ EEPROM
  old_time.seconds  = EEPROM.read(ADDR_time_ss);
  old_time.minutes  = EEPROM.read(ADDR_time_mm);
  old_time.hours    = EEPROM.read(ADDR_time_hh);

  end_transmission.seconds  = EEPROM.read(end_transmission_ss);
  end_transmission.minutes  = EEPROM.read(end_transmission_mm);
  end_transmission.hours    = EEPROM.read(end_transmission_hh);


  software_state        = EEPROM.read(ADDR_software_state);

  EEPROM.get(ADDR_packet_count,     packet_count);

  #if DEBUG_2
  Serial.print("PACKET COUNT FROM EEPROM: ");
  Serial.println(packet_count);
  #endif
  
  // END READ EEPROM

  // Update time
  mission_time = get_time();

  #if DEBUG
  Serial.println("EEPROM READ COMPLETE");
  Serial.print("SOFTWARE_STATE: ");
  Serial.println(software_state);
  #endif

if (!mpu.begin()){
  #if DEBUG
    Serial.println("INIT FAILED: MPU.BEGIN_I2C() RETURNED FALSE");
  #endif
    abort();
}

  mpu.setGyroRange(MPU6050_RANGE_500_DEG);

  #if DEBUG
  Serial.println("MPU INIT COMPLETE SUCCESSFULLY");
  #endif

if (!bmp.begin_I2C()){
  #if DEBUG
      Serial.println("INIT FAILED: BMP.BEGIN() RETURNED FALSE");
  #endif
    abort();
}

#if DEBUG
      Serial.println("BMP INIT COMPLETE SUCCESSFULLY");
      Serial.println("SETUP COMPLETE SUCCESSFULLY");
#endif
}


void loop() {
  // Check for new packets received by the XBee, handle them as needed
  XBee_receive();

  if (software_state == DEPLOYED || software_state == LANDED) {
    // Update time
    mission_time = get_time();

    // Check if it's time to send a new packet (second diff)
    // Theoretically we can miss a single cycle after a set time here, but I'm not concerned
    if (old_time.seconds != mission_time.seconds) {
      // Update local old_time
      old_time = mission_time;
      
      // Update last rtc time stored in memory
      EEPROM.update(ADDR_time_hh, mission_time.hours);
      EEPROM.update(ADDR_time_mm, mission_time.minutes);
      EEPROM.update(ADDR_time_ss, mission_time.seconds);

    } else {
      return;
    }
  }


#if SERIAL_DEBUG
  Serial.println("void loop()::switch");
#endif

switch (software_state){
  case NOT_DEPLOYED:
  {
    #if SERIAL_DEBUG
    Serial.println("DEBUG: NOT_DEPLOYED");
    delay(100);
    #endif

    // Do nothing, wait for XBee command 'CXON'
    return;
  }

  case DEPLOYED:
  {
    #if SERIAL_DEBUG
    Serial.println("DEBUG: DEPLOYED");
    delay(100);
    #endif

    // Check if landed
    float new_altitude = get_altitude();
    if (new_altitude < altitude + 3 && new_altitude > altitude - 3) {
      transition_tracker += 1;

      if (transition_tracker == 3) {
        update_software_state(LANDED);
      }
    } else {
      transition_tracker = 0;
    }

    altitude = new_altitude;
    
    send_packet();
    break;
  }

  case LANDED:
  {
    // Check for end transmission
    if (end_transmission.seconds == mission_time.seconds){
      if (end_transmission.minutes == mission_time.minutes){
        if(end_transmission.hours == mission_time.hours){
          update_software_state(END_TRANSMISSION);
        }
      }
    }
  
    altitude = get_altitude();
    send_packet();

    break;
  }

  case END_TRANSMISSION:
  {
    delay(1000);
    #if SERIAL_DEBUG
    Serial.println("END_TRANSMISSION");
    #endif
    break;
  }
}}
