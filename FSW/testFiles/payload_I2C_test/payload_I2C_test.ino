
/* DELETE ANY INCLUDEs ABOVE THIS LINE
 * 
 * Step 1: Go to tools --> Manage libraries
 * Step 2: In the popup window, search "Adafruit bmp3xx" and install the most recent version
 * Step 3: In the popup window, search "Adafruit mpu6050" and install the latest version
 * Step 4: Go to sketch --> include library and include both bmp3xx and mpu6050
 * Step 5: Verify and upload the sketch
 * Step 6: Open the serial monitor, set baud rate to 9600
 */

#include <Adafruit_MPU6050.h>
#include <Adafruit_BMP3XX.h>

Adafruit_BMP3XX bmp;
Adafruit_MPU6050 mpu;

float get_rotation(){
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  float radsPS = g.gyro.z;
  int rpm = round(9.549297 * radsPS);
  return rpm;
}

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!mpu.begin()){
    Serial.println("INIT FAILED: MPU.BEGIN_I2C() RETURNED FALSE");
    abort();
  }

  
if (!bmp.begin_I2C()){
    Serial.println("INIT FAILED: BMP.BEGIN() RETURNED FALSE");
    abort();
}

}

void loop() {
  Serial.print("ALTITUDE:");
  Serial.println(String(bmp.readAltitude(1013.0F)));
  Serial.print("ROTATION: ");
  Serial.println(String(get_rotation()));
}
