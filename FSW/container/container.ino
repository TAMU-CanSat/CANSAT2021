// Compiler flags have moved to config.h

// Libraries
#include <EEPROM.h>
#include <Wire.h>
#include <RTClib.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GPS.h>
#include <Servo.h>
#include <SD.h>

// Other includes
#include "memorymap.h"
#include "pins.h"
#include "config.h"

// Sensors/Hardware declarations
RTC_PCF8523 rtc;
Adafruit_BMP280 bmp;
Adafruit_GPS gps(&Serial3);
Servo servo;

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
unsigned int  sp1_packet_count = 0;
unsigned int  sp2_packet_count = 0;

float altitude;

String cmd_echo = "";

File file;

// Other variables
short state_transition_tracker        = 0;  // Used to track cycles for transition points between states
short state_transition_tracker_state  = -1;

// FUNCTION DEFINITIONS
Time get_rtc_time() {
  Time time_info;
  DateTime now = rtc.now();
  
  time_info.seconds = now.second();
  time_info.minutes = now.minute();
  time_info.hours   = now.hour();


  return time_info;
}


float get_temperature() {
  return bmp.readTemperature();
}


float get_altitude() {
  // If sim_active (mode), return simulated data
  if (mode) {
    // Modified code from Adafruit_BMP280.cpp/readAltitude()
    float pressure = sim_pressure;

    #if SERIAL_DEBUG
    Serial.print("SIM PRESSURE : ");
    Serial.println(pressure);
    #endif
    
    float atmospheric = pressure / 100.0F;
    return 44330.0 * (1.0 - pow(atmospheric / SEALEVEL_HPA, 0.1903));

  } else {
    return bmp.readAltitude(SEALEVEL_HPA);
  }
}


GPS_struct get_gps() {
  GPS_struct gps_info;

  // Loop until we have a full NMEA sentence and it parses successfully
  char c;
  do {
    c = gps.read();
    while (!gps.newNMEAreceived()) {
      c = gps.read();
    }
  } while (!gps.parse(gps.lastNMEA()));

  #if DEBUG_3
  Serial.print("SECONDS SINCE FIX: ");
  Serial.println(gps.secondsSinceFix());
  #endif

  gps_info.time.seconds = gps.seconds;
  gps_info.time.minutes = gps.minute;
  gps_info.time.hours   = gps.hour;
  gps_info.latitude = gps.latitude;
  gps_info.longitude = gps.longitude;
  gps_info.altitude = gps.altitude;
  gps_info.sats = (byte)(unsigned int)gps.satellites;  // We do this double conversion to avoid signing issues

  return gps_info;
}


float get_voltage() {
  // TODO This is untested since we've been unable to test the system with a battery in
  float voltage = analogRead(VOLTAGE_PIN);

  // Map to range, 1023 = 7.4v
  return map(voltage, 0, 1023, 0, 7.4);
}


void send_packet_payload(byte payloadNum) {
  // Form payload
  String payload = "CMD," + String(TEAM_ID) + ",SP";
  if (payloadNum == 1) {
    payload = payload + "1";
  } else {
    payload = payload + "2";
  }
  payload = payload + "X,ON";

  payload = payload + "\n";

  // Send payload
  XBEE_PAYLOAD_SERIAL.write(payload.c_str());
}


void release_sp1(bool confirm) {
  if (confirm) {
    // TODO Servo values need to be tested
    // Release payload 1
    servo.write(SERVO_RELEASE_SP1);

    // Activate payload
    send_packet_payload(1);
  }
}


void release_sp2(bool confirm) {
  if (confirm) {
    // TODO Servo values need to be tested
    // Release payload 2
    servo.write(SERVO_RELEASE_SP2);

    // Activate payload
    send_packet_payload(2);
  }
}

void reset_prm(bool confirm) {
  if (confirm) {
        servo.write(SERVO_DEFAULT);
        
        sp1_released = false;
        EEPROM.update(ADDR_sp1_released, sp1_released);

        sp2_released = false;
        EEPROM.update(ADDR_sp2_released, sp2_released);
  }
}


void update_software_state(const byte newState) {
  software_state = newState;
  EEPROM.update(ADDR_software_state, newState);
}


void write_to_SD(const String packet) {
  // TODO This is untested, so test it dummy
  // If the file opened successfully, write the packet to it
  if (file){
    #if DEBUG_3
    Serial.println("Writing packet to SD Card");
    #endif

    file.print(packet);
  }
}


// Polls sensors and global variables before constructing and sending a new packet to GCS
void send_packet_gcs() {  
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
  payload += String(packet_count) + ",C,";

  // SIM mode info
  if (mode) {
    payload += "S,";
  } else {
    payload += "F,";
  }

  // Payload release status
  if (sp1_released) {
    payload += "R,";
  } else {
    payload += "N,";
  }
  if (sp2_released) {
    payload += "R,";
  } else {
    payload += "N,";
  }

  // Altitude
  payload += String(altitude) + ",";

  // Temperature
  float temp = get_temperature();
  payload += String(temp) + ",";

  // Voltage
  float voltage = get_voltage();
  payload += String(voltage) + ",";

  // GPS - Time
  GPS_struct GPS = get_gps();
  if (GPS.time.hours < 10) {
    payload += "0";
  }
  payload += String(GPS.time.hours) + ":";

  if (GPS.time.minutes < 10) {
    payload += "0";
  }
  payload += String(GPS.time.minutes) + ":";

  if (GPS.time.seconds < 10) {
    payload += "0";
  }
  payload += String(GPS.time.seconds) + ",";

  // GPS - Location
  payload += String(GPS.latitude) + "," + String(GPS.longitude) + "," + String(GPS.altitude) + ",";
  payload += String(GPS.sats) + ",";

  // Software state
  switch (software_state) {
    case LAUNCH_WAIT:
      payload += "LAUNCH_WAIT,";
      break;
    case ASCENT_LAUNCHPAD:
      payload += "ASCENT_LAUNCHPAD,";
      break;
    case DESCENT:
      payload += "DESCENT,";
      break;

    case SP1_RELEASE:
      payload += "SP1_RELEASE,";
      break;

    case SP2_RELEASE:
      payload += "SP2_RELEASE,";
      break;
    case LANDED:
      payload += "LANDED,";
      break;
  }

  // Payload packet counts
  payload += String(sp1_packet_count) + "," + String(sp2_packet_count) + ",";

  // cmd echo
  payload += cmd_echo + "\n";

  #if DEBUG_2
    Serial.print("PACKET: ");
    Serial.println(payload);
  #endif

  // Send the packet
  XBEE_GCS_SERIAL.write(payload.c_str());

  #if SERIAL_DEBUG
    Serial.println("PACKET SENT");
  #endif

  // Write to SD card
  write_to_SD(payload);
}

void XBee_receive() {
  // STEP 1: Loop until terminator (\n) found || 100 ms pass (junk and start over)
  // STEP 2: Process, if payload packet forward on as is
  // STEP 3: If GCS cmd, process as needed
  // STEP 4: Profit

  // Read characters from Payload XBee if available
  String workingString = "";
  if (XBEE_PAYLOAD_SERIAL.available()) {
    while (XBEE_PAYLOAD_SERIAL.available()) {
      workingString = XBEE_PAYLOAD_SERIAL.readStringUntil('\n');
      
      // Determine if this was from SP1 or SP2, update as needed
      if (workingString.indexOf("S1") > 0){
        sp1_packet_count += 1;
        EEPROM.update(ADDR_sp1_packet_count, sp1_packet_count);
      } else {
        sp2_packet_count += 1;
        EEPROM.update(ADDR_sp2_packet_count, sp2_packet_count);
      }
      
      // Relay and continue if more available
      #if DEBUG_4
      Serial.println();
      Serial.print("Relaying to ground: ");
      Serial.println(workingString);
      #endif

      XBEE_GCS_SERIAL.write(workingString.c_str());

      // Write to SD card
      write_to_SD(workingString);

    }
  }

  // Read characters from GCS XBee if available
  workingString = "";
  if (XBEE_GCS_SERIAL.available()) {
    delay(25);
    char c;

    #if SERIAL_DEBUG
    Serial.print("RECEIVED: ");
    #endif
    
    while (XBEE_GCS_SERIAL.available()) {
      c = XBEE_GCS_SERIAL.read();
      if (c != '\n'){
        workingString += c;
        
        #if SERIAL_DEBUG
        Serial.print(c);
        #endif
        
      } else {
        break;
      }
    }

    // Validate a cmd string
    if (workingString.startsWith("CMD")){
      // Check string at minimum contains 9 characters
      if (workingString.length()<= 9) {
        return;
      }
      
      // Remove 'CMD,2743,' (9 chars) to determine cmd type
      workingString.remove(0,9);
      
      #if SERIAL_DEBUG
      Serial.print("WORKING STRING2: ");
      Serial.println(workingString);
      Serial.flush();
      #endif

      if (workingString.startsWith("CX,ON")){
        // Update state, update CMD ECHO
        update_software_state(ASCENT_LAUNCHPAD);
        cmd_echo = "CXON";
      } else if (workingString.startsWith("CXOFF")) {
        update_software_state(LAUNCH_WAIT);

        cmd_echo = "CXOFF";
      
      } else if (workingString.startsWith("ST")){
        
        #if SERIAL_DEBUG
        Serial.println("IN ST");
        #endif

        // Check string is long enough to process as an ST
        if (workingString.length() < 11) {
          return;
        }
        
        String STpayloadCopy = "CMD," + String(TEAM_ID) + "," + workingString + "\n";
        
        workingString.remove(0,3);
        cmd_echo = "ST" + workingString;  // Out of place command echo to save on formatting
        
        // Form a new datetime object from the CMD, pass to the rtc
        DateTime stime = DateTime(2021, 1, 1, atoi(workingString.substring(0, 2).c_str()), atoi(workingString.substring(3, 5).c_str()), atoi(workingString.substring(6, 8).c_str()));
        rtc.adjust(stime);

        #if SERIAL_DEBUG
        Serial.println("ST SUCCESS");
        #endif

        // Pass ST to payload
        XBEE_PAYLOAD_SERIAL.write(STpayloadCopy.c_str());

      } else if (workingString.startsWith("SIM,")){
        // Check string is long enough to process as a SIM
        if (workingString.length() < 4) {
          return;
        }
        
        // Check for enable / active
        workingString.remove(0,4);
        if (workingString.startsWith("ENABLE")){
          sim_enable = true;
          EEPROM.update(ADDR_sim_enabled, sim_enable);

          cmd_echo = "SIMENABLE";
          
        } else if (workingString.startsWith("ACTIVATE")) {
          if (sim_enable) {
            mode = true;
            EEPROM.update(ADDR_mode, 1);
          }
          
          cmd_echo = "SIMACTIVATE";
          
        } else if (workingString.startsWith("DISABLE")) {
          mode = false;
          sim_enable = false;
          EEPROM.update(ADDR_sim_enabled, sim_enable);
          EEPROM.update(ADDR_mode, 0);
          
          cmd_echo = "SIMDISABLE";
            
        }
      } else if (workingString.startsWith("SIMP")) {
        // Check string is long enough to process as a SIMP
        if (workingString.length() < 6) {
          return;
        }
        
          #if SERIAL_DEBUG
          Serial.println("IN SIMP1");
          #endif
        
          // Remove text, cast to unsigned int, store
          workingString.remove(0,5);

          #if SERIAL_DEBUG
          Serial.print("PRESSURE FROM SIMP: ");
          Serial.print(workingString);
          #endif
          
          sim_pressure = atoi(workingString.c_str());
          EEPROM.update(ADDR_sim_pressure, sim_pressure);

          cmd_echo = "SIMP" + String(sim_pressure);

      } else if (workingString.startsWith("ZERO")) {
          // Set PRM state to default and reset payload release values
          reset_prm(true);
          
      } else if (workingString.startsWith("R_SP1")) {
          release_sp1(true);
          sp1_released = true;
          EEPROM.update(ADDR_sp1_released, 1);

          cmd_echo = "R_SP1";

      } else if (workingString.startsWith("R_SP2")) {
          release_sp2(true);
          sp2_released = true;
          EEPROM.update(ADDR_sp2_released, 1);

          cmd_echo = "R_SP2";
      }
    }
  }
}


// END FUNCTION DEFINITIONS


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
  XBEE_GCS_SERIAL.begin(9600);
  XBEE_PAYLOAD_SERIAL.begin(9600);
  XBEE_PAYLOAD_SERIAL.setTimeout(75);


#if DEBUG
      Serial.println("Waiting for XBEE GCS INIT");
#endif
  while (!XBEE_GCS_SERIAL);
#if DEBUG
      Serial.println("Waiting for XBEE PAYLOAD INIT");
#endif
  while (!XBEE_PAYLOAD_SERIAL);
#if DEBUG
      Serial.println("XBEE INIT COMPLETE");
#endif

//  delay(3000);

//  // RTC init
  if (!rtc.begin()) {
#if DEBUG
    Serial.println("INIT FAILED: RTC.BEGIN() RETURNED FALSE");
    Serial.flush();
//      XBEE_GCS_SERIAL.write('1');
#endif
    abort();
  }

#if DEBUG
      Serial.println("RTC INIT COMPLETE");
#endif

  // Servo init
  servo.attach(SERVO_PWM);
  
#if DEBUG
      Serial.println("SERVO ATTACHED");
#endif

  // BEGIN READ EEPROM
  rtc_time_old.seconds  = EEPROM.read(ADDR_time_ss);
  rtc_time_old.minutes  = EEPROM.read(ADDR_time_mm);
  rtc_time_old.hours    = EEPROM.read(ADDR_time_hh);
//  mission_time.seconds  = EEPROM.read(ADDR_mission_time_ss);
//  mission_time.minutes  = EEPROM.read(ADDR_mission_time_mm);
//  mission_time.hours    = EEPROM.read(ADDR_mission_time_hh);

  software_state        = EEPROM.read(ADDR_software_state);

  mode                  = EEPROM.read(ADDR_mode);
  sim_enable            = EEPROM.read(ADDR_sim_enabled);
  sp1_released          = EEPROM.read(ADDR_sp1_released);
  sp2_released          = EEPROM.read(ADDR_sp2_released);

  EEPROM.get(ADDR_sim_pressure,     sim_pressure);
  EEPROM.get(ADDR_packet_count,     packet_count);
  EEPROM.get(ADDR_sp1_packet_count, sp1_packet_count);
  EEPROM.get(ADDR_sp2_packet_count, sp2_packet_count);
  // END READ EEPROM

#if DEBUG
      Serial.println("EEPROM READ COMPLETE");
      Serial.print("SOFTWARE_STATE: ");
      Serial.println(software_state);
#endif

// Set the servo value to default if no payloads released
if (!sp1_released && !sp2_released) {
    servo.write(SERVO_DEFAULT);
}

  // Init GPS if we're not landed so it can get a fix asap
  if (software_state != LANDED) {
    // GPS
    if (!gps.begin(9600)) {
#if DEBUG
      Serial.println("INIT FAILED: GPS.BEGIN() RETURNED FALSE");
      Serial.flush();
//        XBEE_GCS_SERIAL.write('0');
#endif
      abort();
    }
    gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);  // Set recommended minimum data + altitude
    gps.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);  // Set update interval
  }



  // Init sensors if we're waiting for launch or landed
  if (software_state != LANDED ) {//&& software_state != LAUNCH_WAIT) {
    // BMP
    if (!bmp.begin()) {
#if DEBUG
      Serial.println("INIT FAILED: BMP.BEGIN() RETURNED FALSE");
      Serial.flush();
//    XBEE_GCS_SERIAL.write('1');
#endif
      abort();
    }

  }
#if DEBUG
      Serial.println("BMP INIT COMPLETE SUCCESSFULLY");
#endif

// Init SD card
if (!SD.begin(BUILTIN_SDCARD)){
  #if DEBUG_3
  Serial.println("INIT FAILED: SD.BEGIN() RETURNED FALSE");
  #endif
  
//  abort();
} else {
  // Open a file to write to with the current time
  Time now = get_rtc_time();
  const String fileName = String(now.hours) + "-" + String(now.minutes) + "-" + String(now.seconds) + ".csv";
  
  file = SD.open(fileName.c_str(), FILE_WRITE);
}

  #if DEBUG
  Serial.println("SETUP COMPLETE SUCCESSFULLY");
  #endif

}

// ---------------------
  
void loop() {  
  // Check for new packets received by the XBee, handle them as needed
  // Only if we're not landed
  if (software_state != LANDED){
    XBee_receive();
  }

  // Mission time is set before launch, so we only worry about it past LAUNCH_WAIT
  if (software_state != LAUNCH_WAIT) {    
    // Update time from RTC
    mission_time = get_rtc_time();

    // Check if it's time to send a new packet (second diff)
    // Theoretically we can miss a single cycle after a set time here, but I'm not concerned
      
    if (rtc_time_old.seconds != mission_time.seconds) {
      // Update last rtc time stored in memory
      EEPROM.update(ADDR_time_hh, mission_time.hours);
      EEPROM.update(ADDR_time_mm, mission_time.minutes);
      EEPROM.update(ADDR_time_ss, mission_time.seconds);

      rtc_time_old = mission_time;

    } else {
      return;
    }
  }

#if SERIAL_DEBUG
  Serial.println("void loop()::switch");
#endif


  switch (software_state) {
    case LAUNCH_WAIT:
      {
#if SERIAL_DEBUG
        Serial.println("DEBUG: LAUNCH_WAIT");
        delay(100);
#endif

        // Do nothing, wait for XBee command 'CXON'
        return;
      }
    case ASCENT_LAUNCHPAD:
      {
        #if SERIAL_DEBUG
          Serial.println("ASCENT_LAUNCHPAD");
        #endif

        
        // Check the transition tracker, update accordingly
        if (state_transition_tracker_state == -1) {
          #if SERIAL_DEBUG
            Serial.println("DROP IN");
          #endif
          
          // Just initialized, update to 0, set current altitude
          state_transition_tracker_state = 0;
          altitude = get_altitude();
          state_transition_tracker = 0;

          #if SERIAL_DEBUG
            Serial.println("PAST ALT");
          #endif

        } else if (state_transition_tracker_state == 0) {
          #if SERIAL_DEBUG
            Serial.println("DROP 3");
          #endif
          
          // State 1, check for decreasing altitude over time
          short new_altitude = get_altitude();

          #if DEBUG_1
          Serial.println("DOWN CHECK: new alt: " + String(new_altitude) + "Old alt: " + String(altitude));
          #endif
          
          if (new_altitude < altitude - 5) {
            state_transition_tracker += 1;

            // If we've seen decreasing altitude for 3 seconds, reset trackers and change software state
            if (state_transition_tracker == 3) {
              state_transition_tracker_state = 0;
              state_transition_tracker = 0;

              // Update software state
              update_software_state(DESCENT);
            }
          } else {
            state_transition_tracker = 0; 
          }

          altitude = new_altitude;  // Update altitude
        }

  #if SERIAL_DEBUG
    Serial.println("SENDING PACKET");
  #endif
        send_packet_gcs();
  #if SERIAL_DEBUG
    Serial.println("END SENDING PACKET");
  #endif
        break;
      }
    case DESCENT:
      {

        #if SERIAL_DEBUG
        Serial.println("DEBUG: DESCENT");
        #endif

        // If past 500m, transition to SP1_RELEASE
        altitude = get_altitude();
        if (altitude <= 500) {
          state_transition_tracker += 1;
          if (state_transition_tracker == 3){
            state_transition_tracker = 0;
            update_software_state(SP1_RELEASE);
          }
        } else {
          state_transition_tracker = 0;
        }

        send_packet_gcs();

        break;
      }
    case SP1_RELEASE:
      {
        #if SERIAL_DEBUG
        Serial.println("DEBUG: SP1_RELEASE");
        #endif
        
        if (!sp1_released) {
          release_sp1(true);
          sp1_released = true;
          EEPROM.update(ADDR_sp1_released, 1);
        } else {
          // Failsafe in the event of a poorly timed power outage
          release_sp1(true);
        }

        // If past 400m, transition to SP1_RELEASE
        altitude = get_altitude();
        if (altitude <= 400) {
          state_transition_tracker += 1;
          if (state_transition_tracker == 3){
            state_transition_tracker = 0;
            update_software_state(SP2_RELEASE);
          }
        } else {
          state_transition_tracker = 0;
        }

        send_packet_gcs();

        break;
      }
    case SP2_RELEASE:
      {
        #if SERIAL_DEBUG
        Serial.println("DEBUG: SP2_RELEASE");
        #endif
        
        if (!sp2_released) {
          release_sp2(true);
          sp2_released = true;
          EEPROM.update(ADDR_sp2_released, 1);
        } else {
          // Failsafe in the event of a poorly timed power outage
          release_sp2(true);
        }

        // Track altitude, watch for landing with assumed pressure flucutations of +- 3m
        float new_altitude = get_altitude();
        if (new_altitude < altitude + 2 && new_altitude > altitude - 2) {

          #if DEBUG_3
          Serial.print("INCREMENTING LANDING COUNTER WITH NEW_ALT | OLD_ALT: ");
          Serial.print(new_altitude);
          Serial.print(" | ");
          Serial.println(altitude);
          #endif
          
          state_transition_tracker += 1;

          // If we've seen negligible change over 3 seconds, move on to the next state
          if (state_transition_tracker == 4) {
            update_software_state(LANDED);
          }
        } else {
          state_transition_tracker = 0;
        }

        altitude = new_altitude;  // Update altitude



        send_packet_gcs();

        break;
      }
    case LANDED:
      {
        #if SERIAL_DEBUG
        Serial.println("DEBUG: LANDED");
        #endif
        
        // TODO Activate this before demonstrations
        // Activate the buzzer and hold forever
//        tone(AUDIO_BEACON, 500);
        while (true) { 
          #if SERIAL_DEBUG
          Serial.println("The eagle has landed");
          #endif

          // Delay for an extended period of time
          delay(10000);
  
          break;    
          }
      }
  }
}
