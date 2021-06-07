// The following variables must be configured before launch
// Set to ground pressure before launch (make sure the number has an F on the end)
const float SEALEVEL_HPA = 1014.6F;  


// Servo config
// NOTE: The current values are junk values and need to be set and tested
const short SERVO_RELEASE_SP1 = 75;
const short SERVO_RELEASE_SP2 = 105;
const short SERVO_DEFAULT     = 90;


// Debugging, only set to true if you know what you're doing
// Serial only starts if this is true, and it will hang until it starts if true
#define DEBUG false 

// Misc debug flags, try to keep enabled flags to a minimum to reduce serial spam
#define SERIAL_DEBUG false
#define DEBUG_1 false
#define DEBUG_2 false
#define DEBUG_3 false 
#define DEBUG_4 false


// Unchanging constants, ignore these
const short TEAM_ID = 2743;
