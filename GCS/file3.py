from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import tkinter

from datetime import datetime

#################################################################

# Graph config
GRAPH_MAX_DATAPOINTS = 50
GRAPH_DISPLAY_WIDTH_IN = 17
GRAPH_DISPLAY_HEIGHT_IN = 9
GRAPH_DISPLAY_DPI = None
GRAPH_STYLE = "ggplot"

# Window config
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 975

#################################################################

# Values which need to be set elsewhere
SP1_RELEASED = False
SP2_RELEASED = False

# GPS values
GPS_TIME = None
GPS_LATITUDE = None
GPS_LONGITUDE = None

#################################################################


# Sets the matplotlib style
style.use(GRAPH_STYLE)

# Define the pyplot figure
fig = plt.figure(figsize=(GRAPH_DISPLAY_WIDTH_IN, GRAPH_DISPLAY_HEIGHT_IN), dpi=GRAPH_DISPLAY_DPI)
fig.subplots_adjust(hspace=.3)

# Create four subplots in a 2x2 grid
ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)
plots = [ax1, ax2, ax3, ax4]


# Animation function for PyPlot graphs
def animate(i):
    for plot_ID in range(0, 4):
        # Open the graph data
        graph_data_file = open('datafiles\datafile{}.txt'.format(plot_ID), 'r')
        lines = graph_data_file.read().split('\n')

        # x and y data
        x_data = []
        y_data = []

        # Reverse lines so only most recent data is displayed
        lines.reverse()

        for line in lines:
            # If too many data points, continue and display
            if len(x_data) > GRAPH_MAX_DATAPOINTS:
                break

            # Catch empty line
            if len(line) <= 1:
                continue

            # Split on the comma
            x, y = line.split(',')

            x_data.append(float(x))
            y_data.append(float(y))

        # Reverse the x_data and y_data lists so they're in the correct order
        x_data.reverse()
        y_data.reverse()

        # Clear the old graph and create the new plot
        plots[plot_ID].clear()
        plots[plot_ID].plot(x_data, y_data, color="r")
        plots[plot_ID].set_xlabel("x-values")
        plots[plot_ID].set_ylabel("y-values")
        plots[plot_ID].set_title("Title")
        plots[plot_ID].set_facecolor('k')


# Check indicators
def indicators():
    global SP1_RELEASED, SP2_RELEASED, SP1_indicator, SP2_indicator

    # SP1 & SP2 checks
    if SP1_RELEASED:
        SP1_indicator.config(bg="green")
    if SP2_RELEASED:
        SP2_indicator.config(bg="green")

    # Have this function run again in .5 seconds
    global window
    window.after(500, indicators)

# tkinter window
window = tkinter.Tk()
window.pack_propagate(0)
window.wm_title("Primary Window")
window.configure(bg="#ffffff")

# Set the location on the screen where the window opens
# Source: https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
x_open = (window.winfo_screenwidth()/2) - (WINDOW_WIDTH/2)
y_open = (window.winfo_screenheight()/2) - (WINDOW_HEIGHT/2)
window.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, int(x_open), int(y_open)))  # Really not sure why it takes a string argument... weird

# Setup the canvas
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().grid(column=0, row=1)

# Setup indicators (buttons)
SP1_indicator = tkinter.Button(text="SP1 Released", fg="black", bg="red", padx=20, pady=20)
SP2_indicator = tkinter.Button(text="SP2 Released", fg="black", bg="red", padx=20, pady=20)

SP1_indicator.place(x=215, y=850)
SP2_indicator.place(x=365, y=850)

# Setup labels
GPS_TIME_VARIABLE = tkinter.StringVar()
GPS_TIME_label = tkinter.Label(window, textvariable=GPS_TIME_VARIABLE, relief=tkinter.RAISED)
GPS_TIME_label.place(x=1500, y=850)

GPS_LATITUDE_VARIABLE = tkinter.StringVar()
GPS_LATITUDE_label = tkinter.Label(window, textvariable=GPS_LATITUDE_VARIABLE, relief=tkinter.RAISED)
GPS_LATITUDE_label.place(x=1500, y=880)

GPS_LONGITUDE_VARIABLE = tkinter.StringVar()
GPS_LONGITUDE_label = tkinter.Label(window, textvariable=GPS_LONGITUDE_VARIABLE, relief=tkinter.RAISED)
GPS_LONGITUDE_label.place(x=1500, y=910)

# Run the animation
ani = animation.FuncAnimation(fig, animate, interval=100)

# Schedule tasks and run the main window
window.after(500, indicators)

### DEMO CODE
def dummy1():
    global SP1_RELEASED
    SP1_RELEASED = True
window.after(5000, dummy1)

def dummy2():
    global SP2_RELEASED
    SP2_RELEASED = True
window.after(15000, dummy2)

def time():
    global GPS_TIME_VARIABLE
    now = datetime.now()
    GPS_TIME_VARIABLE.set("GPS Time: " + now.strftime("%H:%M:%S"))
    global window
    window.after(1000, time)
window.after(5, time)

GPS_LATITUDE_VARIABLE.set("GPS Latitude: ")
GPS_LONGITUDE_VARIABLE.set("GPS Longitude: ")
### DEMO CODE

# Run the GUI mainloop
tkinter.mainloop()