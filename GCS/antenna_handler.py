# Read packets over the serial interface
# Send commands over the serial interface

# Misc imports
import tkinter
from datetime import datetime

# Performance profiling
import timeit

#################################################################
# Configuration items
TEAM_ID = 2992
ICON_FILEPATH = "misc/icon.png"

# Disable before real flights to prevent operator error
SIM_ALLOWED = False

# tkinter window configuration
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 800
WINDOW_BACKGROUND_COLOR = "#a2a7ab"
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


# Setup command buttons
button_CX_ON = tkinter.Button(text="(CX) Telemetry On", fg="black", padx=20, pady=20, height=1, width=20, command=CX_ON)
button_CX_OFF = tkinter.Button(text="(CX) Telemetry Off", fg="black", padx=20, pady=20, height=1, width=20, command=CX_OFF)
button_ST = tkinter.Button(text="(ST) Set Time", fg="black", padx=20, pady=20, height=1, width=20, command=ST)
button_SIM_ENABLE = tkinter.Button(text="(SIM) Simulation Enable", fg="black", padx=20, pady=20, height=1, width=20, command=SIM_ENABLE)
button_SIM_ACTIVATE = tkinter.Button(text="(SIM) Simulation Activate", fg="black", padx=20, pady=20, height=1, width=20, command=SIM_ACTIVATE)
button_SIM_DISABLE = tkinter.Button(text="(SIM) Simulation Disable", fg="black", padx=20, pady=20, height=1, width=20, command=SIM_DISABLE)

# If simulation mode is not allowed, disable sim buttons
if not SIM_ALLOWED:
    button_SIM_ENABLE.configure(state="disable")
    button_SIM_ACTIVATE.configure(state="disable")
    button_SIM_DISABLE.configure(state="disable")


# Place command buttons
button_CX_ON.place(x=20, y=20)
button_CX_OFF.place(x=20, y=120)
button_ST.place(x=20, y=220)
button_SIM_ENABLE.place(x=20, y=320)
button_SIM_ACTIVATE.place(x=20, y=420)
button_SIM_DISABLE.place(x=20, y=520)



# Main function, runs a loop for receiving packets and sending commands
def main():
    while True:
        print(command_queue)
        window.update()


# Run main
main()
print("Antenna handler has stopped")

