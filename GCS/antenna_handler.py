# Read packets over the serial interface
# Send commands over the serial interface

# Misc imports
import tkinter
import serial
import threading
import MQTT
import wipe_flight_files

# Time handling imports
from datetime import datetime, timezone
from calendar import timegm
from time import gmtime, sleep

# Performance profiling
import timeit

#################################################################
# Configuration items
TEAM_ID = 2743

# Disable before real flights to prevent operator error
SIM_ALLOWED = True
SIMP_FILE = "datafiles/simp_example.csv"

# Disable to disable safety buttons
SAFETY_BUTTONS = True

# Disable before real or test flights to open serial ports
TEST_MODE = False

# Allow the wiping and archiving of flight data files on boot
ALLOW_WIPE = True

# Serial port configuration
PORT = "COM3"  # ex. COM5, COM6
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
# Print configuration options for user clarity
print("Configuration options:")
print("Team ID = {}".format(TEAM_ID))
print("Serial Port = {}".format(PORT))
print("TEST MODE =", TEST_MODE)
print("SIMULATION MODE ALLOWED =", SIM_ALLOWED)
print("SIMP FILE =", SIMP_FILE)
print("SAFETY BUTTONS ENABLED =", SAFETY_BUTTONS)
print()

# Before anything else, ask and wipe flight data files
if ALLOW_WIPE:
    print("WIPE AND ARCHIVE FLIGHT FILES (Y/N)? ", end="")
    source = input()

    if source == 'Y':
        wipe_flight_files.wipe_and_archive()
    else:
        print("Flight data files have not been modified\n")

#################################################################
# Setup the tkinter window
window = tkinter.Tk()
window.pack_propagate(0)
window.wm_title("Command Palette v0.7")
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
    UTCNow = datetime.now(timezone.utc)
    command = "CMD," + str(TEAM_ID) + ",ST," + UTCNow.strftime('%H:%M:%S')
    enqueue_command(command)


def SIM_ENABLE():
    command = "CMD," + str(TEAM_ID) + ",SIM,ENABLE"
    enqueue_command(command)


simp_thread = None
def SIM_ACTIVATE():
    command = "CMD," + str(TEAM_ID) + ",SIM,ACTIVATE"
    enqueue_command(command)

    # Start simp thread
    global simp_thread
    simp_thread.start()



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
lastCommandSent = "DEFAULT"  # Populated with the last command sent to write_serial
lastCommandReceived = "DEFAULT"  # Populated with the last command echo

# TODO Update this value correctly
time_lastReceived = -1  # Stored in seconds since epoch

# Attempt to open the serial port
num_attempts = 5
connected = False
CANSAT = None
while num_attempts > 0 and not TEST_MODE:
    try:
        CANSAT = serial.Serial(PORT, BAUD, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
        connected = True
        break
    except serial.SerialException:
        num_attempts -= 1
        print("WARNING: SerialException when trying to open serial port {}, will attempt {} more times".format(PORT, num_attempts))
        sleep(1)

if not connected and not TEST_MODE:
    print("ERROR: Could not open serial port. Exiting.")
    exit()


# Helper functions
def secondsSinceEpoch():
    return timegm(gmtime())


# Note: each telemetry transmission is concluded by a \n
def read_serial():
    if not TEST_MODE:
        global CANSAT
        found_start = False
        incoming_packet = b""

        if CANSAT.in_waiting:
            sleep(.2)
            incoming_packet += CANSAT.read_all()
        else:
            return None

        if incoming_packet.startswith(b"2743,"):
            return incoming_packet.replace(b'\n', b'').decode()
        elif b"2743," in incoming_packet:
            return incoming_packet.split(b'2743,')[1] + b'2743,'



def write_serial(command):
    if not TEST_MODE:
        global CANSAT, lastCommandSent
        lastCommandSent = command
        CANSAT.write(command)
        print("SENT COMMAND: {}".format(command))
        sleep(0.25)
    else:
        print("TEST_MODE: Command written: {}".format(command))


def process_packet(packet):
    global lastCommandReceived
    print("PROCESSING PACKET: {}".format(packet))

    # Split packet
    split = packet.split(',')
    print("SPLIT PACKET: {}".format(split))

    # Determine packet packetType and write to file
    packetType = None

    if len(split) < 4:
        print("WARNING: PACKET SPLIT LENGTH < 4, COULD NOT PROCESS\n")
        return
    else:
        if split[3] == "C":
            print("PACKET TYPE: CONTAINER, WRITING TO FILE")
            packetType = 'C'
            telemetry_cansat = open("datafiles/Flight_" + str(TEAM_ID) + "_C.csv", 'a')
            telemetry_cansat.write(packet + "\n")
            telemetry_cansat.close()
        elif split[3] == "S1":
            packetType = 'S1'
            print("PACKET TYPE: PAYLOAD S1, WRITING TO FILE")
            telemetry_sp1 = open("datafiles/Flight_" + str(TEAM_ID) + "_SP1.csv", 'a')
            telemetry_sp1.write(packet + "\n")
            telemetry_sp1.close()
        elif split[3] == "S2":
            packetType = 'S2'
            print("PACKET TYPE: PAYLOAD S2, WRITING TO FILE")
            telemetry_sp2 = open("datafiles/Flight_" + str(TEAM_ID) + "_SP2.csv", 'a')
            telemetry_sp2.write(packet + "\n")
            telemetry_sp2.close()
        else:
            print("WARNING: INVALID PACKET TYPE {}\n".format(split[3]))

    # Find the command echo and store it
    if packetType == "C" and len(split) >= 19:
        lastCommandReceived = split[18]
    elif (packetType == "S1" or packetType == "S2") and len(split) >= 9:
        lastCommandReceived = split[8]

        print("TEST PAYLOAD SPLIT: {}".format(packet.rsplit(b',', 2)[0]))

    # Upload to MQTT
    MQTT.MQTT_publish(packet)


def simp():
    global command_queue
    file = open(SIMP_FILE, 'r')
    lines = file.readlines()
    file.close()
    for line in lines:
        if line.startswith('#') or line == '' or line == '\n':
            continue

        enqueue_command(line.replace('$', str(TEAM_ID)))
        sleep(1)


simp_thread = threading.Thread(target=simp, args=())
# Dummy values for PDR
# strvar_lastSent.set("Last command sent: CMD,2992,CX,ON")
# strvar_lastReceived.set("Last command echo: CMD,2992,CX,ON")
# strvar_timeSinceLastPacket.set("Last packet received: 1s ago")

# Main function, runs a loop for receiving packets and sending commands
def main():
    global command_queue
    while True:
        # If we have commands to send, send them
        while len(command_queue) != 0:
            write_serial(command_queue.pop(0))

        # Check for a packet, process as needed
        packet = read_serial()
        if packet is not None:
            process_packet(packet)

        # Update labels
        strvar_lastSent.set("Last command sent: {}".format(lastCommandSent))
        strvar_lastReceived.set("Last command echo: {}".format(lastCommandReceived))
        strvar_timeSinceLastPacket.set("Last packet received: {}s ago".format(time_lastReceived))

        # Update the window
        window.update()


# Run main
main()
print("Antenna handler has stopped")

