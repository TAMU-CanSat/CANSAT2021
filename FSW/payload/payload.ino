// Compiler flags
#define SERIAL_DEBUG true
#define SP1 true

// Libraries
#include <EEPROM.h>
#include <Wire.h>

// Hardware libraries
#include <Adafruit_BMP3XX.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_GPS.h>

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
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  float radsPS = g.gyro.z;
  int rpm = round(9.549297 * radsPS);
  return rpm;
}

Time get_time() {
  Time time_info;
  DateTime now = DateTime.now();

  time_info.seconds = now.second();
  time_info.minutes = now.minute();
  time_info.hours   = now.hour();

  return time_info;
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
  XBEE_CONTAINER.write(payload.c_str());

}

void update_software_state(const byte newState) {
  software_state = newState;
  EEPROM.update(ADDR_software_state, newState);
}

void XBee_receive() {
  // STEP 1: Loop until terminator (\n) found || 100 ms pass (junk and start over)
  // STEP 2: Process, if payload packet forward on as is
  // STEP 3: If GCS cmd, process as needed
  // STEP 4: Profit

  // Read characters from XBee if available
  String workingString = "";
  if (XBEE_CONTAINER.available()) {
    delay(25);
    char c;
    while (XBEE_CONTAINER.available()) {
      c = XBEE_CONTAINER.read();
      if (c != '\n'){
        workingString += c;
      } else {
        break;
      }
    }

    // Validate a cmd string
    if (workingString.startsWith("CMD")){
      // Remove 'CMD,2743,' (9 chars) to determine cmd type
      workingString.remove(9);

      #if SP1
        if (workingString.startsWith("SP1X,ON")){
          update_software_state(DEPLOYED);
          cmd_echo = "SP1XON";
        }
      #else
        if (workingString.startsWith("SP2X,ON")){
          update_software_state(DEPLOYED);
          cmd_echo = "SP2XON";
        }
      #endif
    }
  }
}



void setup() {
#if SERIAL_DEBUG
  Serial.begin(9600);
  while (!Serial);
#endif

  Wire.begin();
  Serial.println("WIRE BEGIN SUCCESS");

  // XBee init
  XBEE_CONTAINER.begin(9600);

#if SERIAL_DEBUG
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
  // END READ EEPROM

  // Update time
  mission_time = get_time();

#if SERIAL_DEBUG
      Serial.println("EEPROM READ COMPLETE");
      Serial.print("SOFTWARE_STATE: ");
      Serial.println(software_state);
#endif

if (!mpu.begin()){
  #if SERIAL_DEBUG
    Serial.println("INIT FAILED: MPU.BEGIN_I2C() RETURNED FALSE");
  #endif
    abort();
}

  mpu.setGyroRange(MPU6050_RANGE_500_DEG);

#if SERIAL_DEBUG
  Serial.println("MPU INIT COMPLETE SUCCESSFULLY");
#endif

if (!bmp.begin_I2C()){
  #if SERIAL_DEBUG
      Serial.println("INIT FAILED: BMP.BEGIN() RETURNED FALSE");
  #endif
    abort();
}


#if SERIAL_DEBUG
      Serial.println("BMP INIT COMPLETE SUCCESSFULLY");
      Serial.println("SETUP COMPLETE SUCCESSFULLY");
#endif

}

void loop() {
#if SERIAL_DEBUG
      Serial.println("LOOP - TOP");
#endif

  // Check for new packets received by the XBee, handle them as needed
  XBee_receive();

  if (software_state != NOT_DEPLOYED) {
      #if SERIAL_DEBUG
        Serial.println("DROP INTO TIME CHECK");
      #endif
    
    // Update time
    mission_time = get_time();

    // Check if it's time to send a new packet (second diff)
    // Theoretically we can miss a single cycle after a set time here, but I'm not concerned
    if (old_time.seconds != mission_time.seconds) {
      // Update last rtc time stored in memory
      EEPROM.update(ADDR_time_hh, mission_time.hours);
      EEPROM.update(ADDR_time_mm, mission_time.minutes);
      EEPROM.update(ADDR_time_ss, mission_time.seconds);

        #if SERIAL_DEBUG
          Serial.println("DROP TIME UPDATE");
        #endif
    } else {
        #if SERIAL_DEBUG
          Serial.println("DROP TIME NO UPDATE");
        #endif
      return;
    }
  }


#if SERIAL_DEBUG
  Serial.println("STEP 1");
#endif



switch (software_state){
  case NOT_DEPLOYED:
  {#if SERIAL_DEBUG
        Serial.println("DEBUG: NOT_DEPLOYED");
        delay(100);
#endif

        // Do nothing, wait for XBee command 'CXON'
        return;



    break;
  }

  case DEPLOYED:
  {
  EEPROM.write(
    // TODO IF JUST TRANSITIONTED, STORE END TRANSMISSION (CONSIDER ADDING IS END TRANSMISSION SET)
    // ELSE JUST SEND THE PACKET

    break;
  }

  case END_TRANSMISSION:
  {


    break;
  }
}












}
