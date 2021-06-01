// The following variables must be configured before launch
// Set to ground pressure before launch (make sure the number has an F on the end)
const float SEALEVEL_HPA = 1014.6F;  

// Set to 'true' when compiling for SP1 and 'false' when compiling for sp2
#define SP1 false

// Debugging, only set to true if you know what you're doing
// Serial only starts if this is true, and it will hang until it starts if true
#define DEBUG false 

// Misc debug flags, try to keep enabled flags to a minimum to reduce serial spam
#define DEBUG false
#define SERIAL_DEBUG false
#define DEBUG_2 false  // Used to debug command receipt for SPXON
#define DEBUG_3 false  // Used to track down weird packet issues


// Unchanging constants, ignore these
const short TEAM_ID = 2743;