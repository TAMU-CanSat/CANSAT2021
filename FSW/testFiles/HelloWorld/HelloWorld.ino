// Simple Hello World script to verify functionality

void setup() {
  // Wait for the serial monitor to report ready
  while (!Serial);
  Serial.begin(9600); // USB is always 12 or 480 Mbit/sec
}

void loop() {
  Serial.println("Howdy World! You should be receiving this message. If you are not, welp, too bad I guess...");
  delay(1000);  // do not print too fast!
}
