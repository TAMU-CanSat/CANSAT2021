# Read packets over the serial interface
# Send commands over the serial interface

# Misc imports
import tkinter
import serial

# Time handling imports
from datetime import datetime
from calendar import timegm
from time import gmtime, sleep

# Performance profiling
import timeit

#################################################################
# Configuration items
TEAM_ID = 2992

# Disable before real flights to prevent operator error
SIM_ALLOWED = True

# Disable to disable safety buttons
SAFETY_BUTTONS = True

# Disable before real or test flights to open serial ports
TEST_MODE = True

# Serial port configuration
PORT = ""  # ex. COM5, COM6
BAUD = 9600  # Default 9600
PARITY = "N"  # Default N
STOPBITS = 1  # Default 1
TIMEOUT = .25  # None=Blocking, 0=Non_blocking, else timeout in seconds

# tkinter window configuration
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 800
WINDOW_BACKGROUND_COLOR = "#a2a7ab"
ICON_FILEPATH = "misc/icon.png"
#################################################################

# Setup the tkinter window
window = tkinter.Tk()
window.pack_propagate(0)
window.wm_title("Command Palette v0.1")
window.configure(bg=WINDOW_BACKGROUND_COLOR)

# Set tkinter window icon
icon = tkinter.PhotoImage(file=ICON_FILEPATH)
window.iconphoto(False, icon)

# Open the window towards the right edge of the screen
# Source: https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
x_open = ((window.winfo_screenwidth()/2) - (WINDOW_WIDTH/2)) * 2 - 50
y_open = (window.winfo_screenheight()/2) - (WINDOW_HEIGHT/2)
window.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, int(x_open), int(y_open)))

# Define button functions
command_queue = []
def enqueue_command(command):
    # Convert the string to bytes and add it to the back of the command queue (list)
    global command_queue
    command_queue.append(bytes(command, 'utf8'))


def CX_ON():
    command = "CMD," + str(TEAM_ID) + ",CX,ON"
    enqueue_command(command)


def CX_OFF():
    command = "CMD," + str(TEAM_ID) + ",CX,OFF"
    enqueue_command(command)


def ST():
    # TODO Setup to convert from timezone (configuration item) to UTC
    command = "CMD," + str(TEAM_ID) + ",ST," + datetime.now().strftime('%H:%M:%S')
    enqueue_command(command)


def SIM_ENABLE():
    command = "CMD," + str(TEAM_ID) + ",SIM,ENABLE"
    enqueue_command(command)


def SIM_ACTIVATE():
    command = "CMD," + str(TEAM_ID) + ",SIM,ACTIVATE"
    enqueue_command(command)


def SIM_DISABLE():
    command = "CMD," + str(TEAM_ID) + ",SIM,DISABLE"
    enqueue_command(command)


def ZERO():
    command = "CMD," + str(TEAM_ID) + ",ZERO"
    enqueue_command(command)


def R_SP1():
    command = "CMD," + str(TEAM_ID) + ",R_SP1"
    enqueue_command(command)


def R_SP2():
    command = "CMD," + str(TEAM_ID) + ",R_SP2"
    enqueue_command(command)


# Setup command buttons
button_CX_ON = tkinter.Button(text="(CX) Telemetry On", fg="black", padx=20, pady=20, height=1, width=20, command=CX_ON)
button_CX_OFF = tkinter.Button(text="(CX) Telemetry Off", fg="black", padx=20, pady=20, height=1, width=20, command=CX_OFF)
button_ST = tkinter.Button(text="(ST) Set Time", fg="black", padx=20, pady=20, height=1, width=20, command=ST)
button_SIM_ENABLE = tkinter.Button(text="(SIM) Simulation Enable", fg="black", padx=20, pady=20, height=1, width=20, command=SIM_ENABLE)
button_SIM_ACTIVATE = tkinter.Button(text="(SIM) Simulation Activate", fg="black", padx=20, pady=20, height=1, width=20, command=SIM_ACTIVATE)
button_SIM_DISABLE = tkinter.Button(text="(SIM) Simulation Disable", fg="black", padx=20, pady=20, height=1, width=20, command=SIM_DISABLE)
button_ZERO = tkinter.Button(text="(ZERO) Zero out sensors", fg="black", padx=20, pady=20, height=1, width=20, command=ZERO)
button_R_SP1 = tkinter.Button(text="(R_SP1) Release SP1", fg="black", padx=20, pady=20, height=1, width=20, command=R_SP1)
button_R_SP2 = tkinter.Button(text="(R_SP2) Release SP2", fg="black", padx=20, pady=20, height=1, width=20, command=R_SP2)



# If simulation mode is not allowed, disable sim buttons
if not SIM_ALLOWED:
    button_SIM_ENABLE.configure(state="disable")
    button_SIM_ACTIVATE.configure(state="disable")
    button_SIM_DISABLE.configure(state="disable")


# Place command buttons
button_CX_ON.place(x=20, y=20)
button_CX_OFF.place(x=20, y=95)
button_ST.place(x=20, y=170)
button_SIM_ENABLE.place(x=20, y=245)
button_SIM_ACTIVATE.place(x=20, y=320)
button_SIM_DISABLE.place(x=20, y=395)
button_ZERO.place(x=20, y=470)
button_R_SP1.place(x=20, y=545)
button_R_SP2.place(x=20, y=620)

# Define safety button functions
CX_ON_enabled = True
def safety_CX_ON():
    global CX_ON_enabled
    CX_ON_enabled = not CX_ON_enabled
    if CX_ON_enabled:
        button_CX_ON.configure(state="normal")
    else:
        button_CX_ON.configure(state="disable")


CX_OFF_enabled = True
def safety_CX_OFF():
    global CX_OFF_enabled
    CX_OFF_enabled = not CX_OFF_enabled
    if CX_OFF_enabled:
        button_CX_OFF.configure(state="normal")
    else:
        button_CX_OFF.configure(state="disable")


ST_enabled = True
def safety_ST():
    global ST_enabled
    ST_enabled = not ST_enabled
    if ST_enabled:
        button_ST.configure(state="normal")
    else:
        button_ST.configure(state="disable")


SIM_ENABLE_enabled = True
def safety_SIM_ENABLE():
    global SIM_ENABLE_enabled
    SIM_ENABLE_enabled = not SIM_ENABLE_enabled
    if SIM_ENABLE_enabled:
        button_SIM_ENABLE.configure(state="normal")
    else:
        button_SIM_ENABLE.configure(state="disable")


SIM_ACTIVATE_enabled = True
def safety_SIM_ACTIVATE():
    global SIM_ACTIVATE_enabled
    SIM_ACTIVATE_enabled = not SIM_ACTIVATE_enabled
    if SIM_ACTIVATE_enabled:
        button_SIM_ACTIVATE.configure(state="normal")
    else:
        button_SIM_ACTIVATE.configure(state="disable")


SIM_DISABLE_enabled = True
def safety_SIM_DISABLE():
    global SIM_DISABLE_enabled
    SIM_DISABLE_enabled = not SIM_DISABLE_enabled
    if SIM_DISABLE_enabled:
        button_SIM_DISABLE.configure(state="normal")
    else:
        button_SIM_DISABLE.configure(state="disable")


ZERO_enabled = True
def safety_ZERO():
    global ZERO_enabled
    ZERO_enabled = not ZERO_enabled
    if ZERO_enabled:
        button_ZERO.configure(state="normal")
    else:
        button_ZERO.configure(state="disable")


R_SP1_enabled = True
def safety_R_SP1():
    global R_SP1_enabled
    R_SP1_enabled = not R_SP1_enabled
    if R_SP1_enabled:
        button_R_SP1.configure(state="normal")
    else:
        button_R_SP1.configure(state="disable")


R_SP2_enabled = True
def safety_R_SP2():
    global R_SP2_enabled
    R_SP2_enabled = not R_SP2_enabled
    if R_SP2_enabled:
        button_R_SP2.configure(state="normal")
    else:
        button_R_SP2.configure(state="disable")



# Setup and place safety buttons
if SAFETY_BUTTONS:
    button_safety_CX_ON = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_CX_ON)
    button_safety_CX_OFF = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_CX_OFF)
    button_safety_ST = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_ST)
    button_safety_SIM_ENABLE = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_SIM_ENABLE)
    button_safety_SIM_ACTIVATE = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_SIM_ACTIVATE)
    button_safety_SIM_DISABLE = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_SIM_DISABLE)
    button_safety_ZERO = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_ZERO)
    button_safety_R_SP1 = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_R_SP1)
    button_safety_R_SP2 = tkinter.Button(text="Enable", fg="black", padx=20, pady=20, height=1, width=4, command=safety_R_SP2)

    # Place safety buttons
    button_safety_CX_ON.place(x=217, y=20)
    button_safety_CX_OFF.place(x=217, y=95)
    button_safety_ST.place(x=217, y=170)
    button_safety_SIM_ENABLE.place(x=217, y=245)
    button_safety_SIM_ACTIVATE.place(x=217, y=320)
    button_safety_SIM_DISABLE.place(x=217, y=395)
    button_safety_ZERO.place(x=217, y=470)
    button_safety_R_SP1.place(x=217, y=545)
    button_safety_R_SP2.place(x=217, y=620)

    # Default protected buttons to disabled
    safety_CX_ON()
    safety_CX_OFF()
    safety_ST()
    safety_SIM_ENABLE()
    safety_SIM_ACTIVATE()
    safety_SIM_DISABLE()
    safety_ZERO()
    safety_R_SP1()
    safety_R_SP2()

# Setup labels
strvar_lastSent = tkinter.StringVar()
strvar_lastReceived = tkinter.StringVar()
strvar_timeSinceLastPacket = tkinter.StringVar()
label_lastSent = tkinter.Label(window, textvariable=strvar_lastSent, relief=tkinter.RAISED)
label_lastReceived = tkinter.Label(window, textvariable=strvar_lastReceived, relief=tkinter.RAISED)
label_timeSinceLastPacket = tkinter.Label(window, textvariable=strvar_timeSinceLastPacket, relief=tkinter.RAISED)

# Place labels
label_lastSent.place(x=20, y=700)
label_lastReceived.place(x=20, y=730)
label_timeSinceLastPacket.place(x=20, y=760)

################################################################################
# Antenna communications
# Variables
lastCommandSent = "None"  # Populated with the last command sent to write_serial
lastCommandReceived = "None"  # Populated with the last command echo
time_lastReceived = 0  # Stored in seconds since epoch

# Attempt to open the serial port
num_attempts = 5
connected = False
while num_attempts > 0 and not TEST_MODE:
    try:
        CANSAT = serial.Serial(PORT, BAUD, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
        connected = True
        break
    except serial.SerialException:
        num_attempts -= 1
        print("WARNING: SerialException when trying to open serial port {}, will attempt {} more times".format(PORT, num_attempts))
        sleep(1)

# TODO Implement TEST_MODE serial functions using dummy serial class (and, you know, write that class)

if not connected and not TEST_MODE:
    print("ERROR: Could not open serial port. Exiting.")
    exit()

# Helper functions
def secondsSinceEpoch():
    return timegm(gmtime())


# TODO Write this function, determine best reading mode
def read_serial():
    global CANSAT
    print("N/A")


# TODO Write this function, should be a straightforward blocking read
def write_serial(command):
    global CANSAT, lastCommandSent
    lastCommandSent = command
    print("N/A")



# TODO Implement simulation mode (SIMP) functionality

# Dummy values for PDR
strvar_lastSent.set("Last command sent: CMD,2992,CX,ON")
strvar_lastReceived.set("Last command echo: CMD,2992,CX,ON")
strvar_timeSinceLastPacket.set("Last packet received: 1s ago")

# TODO Fill in main function
# Main function, runs a loop for receiving packets and sending commands
def main():
    while True:
        # Read serial, check for full packet
        # If packet is full, continue, else, read until full packet or timeout

        # Determine packet type, write to appropriate CSV

        # Check echo against last command sent
        # If two packets have been received since the command was sent and the echo hasn't updated, send again
        # Else if queue is populated, send next command in queue

        # If the proper amount of time has passed since the last command, send the next SIMP

        # Update labels
        # strvar_lastSent.set("Last command sent: " + )
        # strvar_lastReceived.set("Last command echo: " + )
        # strvar_timeSinceLastPacket.set("Last packet received: {}s ago".format())

        # Update the window
        window.update()


# Run main
main()
print("Antenna handler has stopped")

