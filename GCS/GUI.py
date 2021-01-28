# matplotlib imports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib import style

# misc imports
import tkinter
import os

# Performance profiling
import timeit

# TODO Add a quit button which exports the plots

#################################################################

# Graph config
GRAPH_DISPLAY_WIDTH = 17
GRAPH_DISPLAY_HEIGHT = 9
GRAPH_STYLE = "ggplot"  # Reference: https://matplotlib.org/3.2.1/gallery/style_sheets/style_sheets_reference
GRAPH_LINE_STYLE = "-o"
GRAPH_MAX_TICKS_X = 6

# TODO Consider using Google Maps API to dynamically grab map image/create external script for that task
# GPS graph configuration
GPS_IMAGE_FILEPATH = "misc/map8.png"
GPS_BOTTOM_LEFT = [30.610252837146604, -96.355542911837]  # Coordinates of bottom left corner of map image
GPS_TOP_RIGHT = [30.621074225490286, -96.33900977620632]  # Coordinates of top right corner of map image

# Hex colors for CANSAT, SP1, and SP2 on the GUI
COLOR_CANSAT = "#03fc39"
COLOR_SP1 = "#ebae00"
COLOR_SP2 = "#ff6361"

# tkinter window configuration
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 975
WINDOW_BACKGROUND_COLOR = "#a2a7ab"
ICON_FILEPATH = "misc/icon.png"

# TODO Pull TEAM_ID, icon, etc from a .env file, carry changes across all files
# Other config
TEAM_ID = 2992

#################################################################
# TODO Print important config options (ex. TEAM_ID, GPS image file name)
# Print configuration options for user clarity



#################################################################
# Sets the matplotlib style
style.use(GRAPH_STYLE)

# Define the pyplot figure
graph_container = plt.figure(figsize=(GRAPH_DISPLAY_WIDTH, GRAPH_DISPLAY_HEIGHT))
graph_container.subplots_adjust(hspace=.3)

# Create five plots in a 2x3 (2 rows, 3 columns) grid
graph_alt = graph_container.add_subplot(2, 3, 1)
graph_rotation = graph_container.add_subplot(2, 3, 2)
graph_gps = graph_container.add_subplot(2, 3, 3)
graph_temp = graph_container.add_subplot(2, 3, 4)
graph_voltage = graph_container.add_subplot(2, 3, 5)
graph_container.subplots_adjust(left=0.05, bottom=0.07, right=0.98, top=0.97)

# Configure container
graph_container.set_facecolor(WINDOW_BACKGROUND_COLOR)

# Add all plots to a list
graphs = [graph_alt, graph_rotation, graph_gps, graph_temp, graph_voltage]

# Set plot information up in a list for later processing
graphs_xlabels = ["Time", "Time", "Latitude", "Time", "Time"]
graphs_ylabels = ["Altitude (m)", "Rotation (rpm)", "Longitude", "Temperature (C)", "Voltage (V)"]
graphs_titles = ["Altitude", "Rotation", "GPS Location", "Temperature", "Battery Voltage"]

# Setup the tkinter window
window = tkinter.Tk()
window.pack_propagate(0)
window.wm_title("Falling With Style GUI v0.1")
window.configure(bg=WINDOW_BACKGROUND_COLOR)

# Open the window in the center of the screen
# Source: https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
x_open = (window.winfo_screenwidth()/2) - (WINDOW_WIDTH/2)
y_open = (window.winfo_screenheight()/2) - (WINDOW_HEIGHT/2)
window.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, int(x_open), int(y_open)))

# Setup the canvas with the graph container
canvas = FigureCanvasTkAgg(graph_container, master=window)
canvas.get_tk_widget().grid(column=0, row=1)

# Setup payload release indicators (buttons)
indicator_sp1 = tkinter.Button(text="SP1 Released", fg="black", bg="red", padx=20, pady=20)
indicator_sp2 = tkinter.Button(text="SP2 Released", fg="black", bg="red", padx=20, pady=20)
indicator_sp1.place(x=1200, y=450)
indicator_sp2.place(x=1200, y=535)

# TODO Stylize labels
# TODO Do the time values from the payloads also need to be displayed (probably)

# Setup labels for mission time and gps time
time_gps_variable = tkinter.StringVar()
time_mission_variable = tkinter.StringVar()
time_gps_label = tkinter.Label(window, textvariable=time_gps_variable, relief=tkinter.RAISED)
time_mission_label = tkinter.Label(window, textvariable=time_mission_variable, relief=tkinter.RAISED)
time_gps_label.place(x=1430, y=450)
time_mission_label.place(x=1430, y=480)

# Setup labels for state
state_variable = tkinter.StringVar()
state_label = tkinter.Label(window, textvariable=state_variable, relief=tkinter.RAISED)
state_label.place(x=1430, y=510)

# Setup labels for packet counts
packets_cansat_received_variable = tkinter.StringVar()
packets_sp1_received_variable = tkinter.StringVar()
packets_sp2_received_variable = tkinter.StringVar()

packets_cansat_received_label = tkinter.Label(window, textvariable=packets_cansat_received_variable, relief=tkinter.RAISED)
packets_sp1_received_label = tkinter.Label(window, textvariable=packets_sp1_received_variable, relief=tkinter.RAISED)
packets_sp2_received_label = tkinter.Label(window, textvariable=packets_sp2_received_variable, relief=tkinter.RAISED)

# Setup labels for lost packets
packets_cansat_lost_variable = tkinter.StringVar()
packets_sp1_lost_variable = tkinter.StringVar()
packets_sp2_lost_variable = tkinter.StringVar()

packets_cansat_lost_label = tkinter.Label(window, textvariable=packets_cansat_lost_variable, relief=tkinter.RAISED)
packets_sp1_lost_label = tkinter.Label(window, textvariable=packets_sp1_lost_variable, relief=tkinter.RAISED)
packets_sp2_lost_label = tkinter.Label(window, textvariable=packets_sp2_lost_variable, relief=tkinter.RAISED)

# Place the packet labels
packets_cansat_received_label.place(x=1200, y=650)
packets_sp1_received_label.place(x=1200, y=680)
packets_sp2_received_label.place(x=1200, y=710)
packets_cansat_lost_label.place(x=1430, y=650)
packets_sp1_lost_label.place(x=1430, y=680)
packets_sp2_lost_label.place(x=1430, y=710)


# Check a file exists and has any data, False if file has no data or does not exist, else True
# Source: https://stackoverflow.com/questions/2507808/how-to-check-whether-a-file-is-empty-or-not
def hasData(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


# Set tkinter window icon
icon = tkinter.PhotoImage(file=ICON_FILEPATH)
window.iconphoto(False, icon)

# Variables to track last packets received and lost packets
packets_received_cansat = 0
packets_received_sp1 = 0
packets_received_sp2 = 0
packets_lost_cansat = 0
packets_lost_sp1 = 0
packets_lost_sp2 = 0

# Define telemetry file names
filename_cansat = "datafiles/Flight_" + str(TEAM_ID) + "_C.csv"
filename_sp1 = "datafiles/Flight_" + str(TEAM_ID) + "_SP1.csv"
filename_sp2 = "datafiles/Flight_" + str(TEAM_ID) + "_SP2.csv"

# Main function(loop), updates tkinter window auto-magically, updates graphs, buttons, labels, etc.
# TODO Add a quit button with any needed cleanup code
stop = False
while not stop:
    # Check if the files have any data & exist
    if not hasData(filename_cansat):
        # If the container hasn't relayed any telemetry, loop until we have data
        window.update()
        continue

    # TODO Create files in initialization code above
    # Open datafiles, assume all files exist even if empty
    file_cansat = open(filename_cansat, 'r')
    file_sp1 = open(filename_sp1, 'r')
    file_sp2 = open(filename_sp2, 'r')

    # Grab data out of the files
    data_cansat = file_cansat.readlines()
    data_sp1 = file_sp1.readlines()
    data_sp2 = file_sp2.readlines()

    # Close the files
    file_cansat.close()
    file_sp1.close()
    file_sp2.close()

    # Clear and re-configure plots
    graph_alt.clear()
    for i in range(0, len(graphs)):
        graphs[i].clear()
        graphs[i].set_xlabel(graphs_xlabels[i])
        graphs[i].set_ylabel(graphs_ylabels[i])
        graphs[i].set_title(graphs_titles[i])

        # Set the maximum tick marks on the x-axis
        graphs[i].xaxis.set_major_locator(plt.MaxNLocator(GRAPH_MAX_TICKS_X))

    # Special configuration for GPS plot
    # Source: https://stackoverflow.com/questions/34458251/plot-over-an-image-background-in-python
    # Source: https://stackoverflow.com/questions/13384653/imshow-extent-and-aspect
    gps_img = plt.imread(GPS_IMAGE_FILEPATH)
    graph_gps.imshow(gps_img, extent=[GPS_BOTTOM_LEFT[1], GPS_TOP_RIGHT[1], GPS_BOTTOM_LEFT[0], GPS_TOP_RIGHT[0]], aspect="auto")
    graph_gps.grid(False)

    # Define arrays to be used in plot creation
    time_values = []
    altitude_values = []
    temp_values = []
    voltage_values = []
    gps_lat = []
    gps_long = []

    # TODO Add capability to handle empty/invalid data
    # Fill out the data sets from the cansat data
    packets_received_cansat = 0
    for line in data_cansat:
        # Catch empty line
        if len(line) == 0:
            continue

        # Split the data
        data = line.replace("\n", " ").split(",")

        # Counter for packets received
        packets_received_cansat += 1

        # Grab values from the data
        time_values.append(data[1])                 # Mission time
        altitude_values.append(float(data[7]))      # Altitude
        temp_values.append(float(data[8]))          # Temperature
        voltage_values.append(float(data[9]))       # Battery voltage
        gps_lat.append(float(data[11]))             # Latitude
        gps_long.append(float(data[12]))            # Longitude

    # Plot CANSAT data
    graph_alt.plot(time_values, altitude_values, GRAPH_LINE_STYLE, color=COLOR_CANSAT)
    graph_gps.plot(gps_long, gps_lat, GRAPH_LINE_STYLE, color=COLOR_CANSAT)
    graph_temp.plot(time_values, temp_values, GRAPH_LINE_STYLE, color=COLOR_CANSAT)
    graph_voltage.plot(time_values, voltage_values, GRAPH_LINE_STYLE, color=COLOR_CANSAT)

    # Annotate CANSAT data points
    graph_alt.annotate("CANSAT", (time_values[len(time_values) - 1], altitude_values[len(altitude_values) - 1]))
    graph_gps.annotate("CANSAT", (gps_long[len(gps_long) - 1], gps_lat[len(gps_lat) - 1]), color="white")
    graph_temp.annotate("CANSAT", (time_values[len(time_values) - 1], temp_values[len(temp_values) - 1]))
    graph_voltage.annotate("CANSAT", (time_values[len(time_values) - 1], voltage_values[len(voltage_values) - 1]))

    # Grab the most recent data from the cansat datafile
    cansat_recent = data_cansat[len(data_cansat) - 1].replace('\n', '').split(',')

    # Check the SP1_RELEASE and SP2_RELEASE status columns
    if "Y" in cansat_recent[5]:
        indicator_sp1.config(bg="green")

    if "Y" in cansat_recent[6]:
        indicator_sp2.config(bg="green")

    # Count missing packets
    if int(packets_received_cansat) != int(cansat_recent[2]):
        packets_lost_cansat = int(cansat_recent[2]) - int(packets_received_cansat)

    # Update CANSAT labels
    time_mission_variable.set("Mission Time: " + str(cansat_recent[1]))
    time_gps_variable.set("GPS Time: " + str(cansat_recent[10]))
    packets_cansat_received_variable.set("Packets Received - CANSAT: " + str(packets_received_cansat - packets_lost_cansat))
    packets_cansat_lost_variable.set("Packets Lost - CANSAT: " + str(packets_lost_cansat))
    state_variable.set("Software State: " + str(cansat_recent[15]))

    # Create data sets from sp1 data
    if hasData(filename_sp1) and len(data_sp1) != 0:
        # Clear arrays
        time_values.clear()
        temp_values.clear()
        altitude_values.clear()
        rotation_values = []
        gps_lat.clear()
        gps_long.clear()
        voltage_values.clear()

        # Loop through sp1 data and add to arrays for graphing
        packets_received_sp1 = 0
        for line in data_sp1:
            # Catch empty line
            if len(line) == 0:
                continue

            # Split the data
            data = line.replace("\n", " ").split(",")

            # Counter for packets received
            packets_received_sp1 += 1

            # Grab values from the data
            time_values.append(data[1])  # Mission time
            altitude_values.append(float(data[4]))  # Altitude
            temp_values.append(float(data[5]))  # Temperature
            rotation_values.append(float(data[6]))  # Rotation rate
            voltage_values.append(float(data[7]))  # Battery voltage
            gps_lat.append(float(data[8]))  # Latitude
            gps_long.append(float(data[9]))  # Longitude

        # Plot SP1 data
        graph_alt.plot(time_values, altitude_values, GRAPH_LINE_STYLE, color=COLOR_SP1)
        graph_gps.plot(gps_long, gps_lat, GRAPH_LINE_STYLE, color=COLOR_SP1)
        graph_temp.plot(time_values, temp_values, GRAPH_LINE_STYLE, color=COLOR_SP1)
        graph_voltage.plot(time_values, voltage_values, GRAPH_LINE_STYLE, color=COLOR_SP1)
        graph_rotation.plot(time_values, rotation_values, GRAPH_LINE_STYLE, color=COLOR_SP1)

        # Annotate SP1 data points
        graph_alt.annotate("SP1", (time_values[len(time_values) - 1], altitude_values[len(altitude_values) - 1]))
        graph_gps.annotate("SP1", (gps_long[len(gps_long) - 1], gps_lat[len(gps_lat) - 1]), color="white")
        graph_temp.annotate("SP1", (time_values[len(time_values) - 1], temp_values[len(temp_values) - 1]))
        graph_voltage.annotate("SP1", (time_values[len(time_values) - 1], voltage_values[len(voltage_values) - 1]))
        graph_rotation.annotate("SP1", (time_values[len(time_values) - 1], rotation_values[len(rotation_values) - 1]))

        # Grab the most recent data from the sp1 datafile
        sp1_recent = data_sp1[len(data_sp1) - 1].replace('\n', '').split(',')

        # Count missing packets
        if int(packets_received_sp1) != int(sp1_recent[2]):
            packets_lost_sp1 = int(sp1_recent[2]) - int(packets_received_sp1)

        # Update SP1 labels
        packets_sp1_received_variable.set("Packets Received - SP1: " + str(packets_received_sp1 - packets_lost_sp1))
        packets_sp1_lost_variable.set("Packets Lost - SP1: " + str(packets_lost_sp1))

    # Create data sets from sp2 data
    if hasData(filename_sp2) and len(data_sp2) != 0:
        # Clear arrays
        time_values.clear()
        temp_values.clear()
        altitude_values.clear()
        rotation_values = []
        gps_lat.clear()
        gps_long.clear()
        voltage_values.clear()

        # Loop through sp2 data and add to arrays for graphing
        packets_received_sp2 = 0
        for line in data_sp2:
            # Catch empty line
            if len(line) == 0:
                continue

            # Split the data
            data = line.replace("\n", " ").split(",")

            # Counter for packets received
            packets_received_sp2 += 1

            # Grab values from the data
            time_values.append(data[1])  # Mission time
            altitude_values.append(float(data[4]))  # Altitude
            temp_values.append(float(data[5]))  # Temperature
            rotation_values.append(float(data[6]))  # Rotation rate
            voltage_values.append(float(data[7]))  # Battery voltage
            gps_lat.append(float(data[8]))  # Latitude
            gps_long.append(float(data[9]))  # Longitude

        # Plot sp2 data
        graph_alt.plot(time_values, altitude_values, GRAPH_LINE_STYLE, color=COLOR_SP2)
        graph_gps.plot(gps_long, gps_lat, GRAPH_LINE_STYLE, color=COLOR_SP2)
        graph_temp.plot(time_values, temp_values, GRAPH_LINE_STYLE, color=COLOR_SP2)
        graph_voltage.plot(time_values, voltage_values, GRAPH_LINE_STYLE, color=COLOR_SP2)
        graph_rotation.plot(time_values, rotation_values, GRAPH_LINE_STYLE, color=COLOR_SP2)

        # Annotate SP2 data points
        graph_alt.annotate("SP2", (time_values[len(time_values) - 1], altitude_values[len(altitude_values) - 1]))
        graph_gps.annotate("SP2", (gps_long[len(gps_long) - 1], gps_lat[len(gps_lat) - 1]), color="white")
        graph_temp.annotate("SP2", (time_values[len(time_values) - 1], temp_values[len(temp_values) - 1]))
        graph_voltage.annotate("SP2", (time_values[len(time_values) - 1], voltage_values[len(voltage_values) - 1]))
        graph_rotation.annotate("SP2", (time_values[len(time_values) - 1], rotation_values[len(rotation_values) - 1]))

        # Grab the most recent data from the sp2 datafile
        sp2_recent = data_sp2[len(data_sp2) - 1].replace('\n', '').split(',')

        # Count missing packets
        if int(packets_received_sp2) != int(sp2_recent[2]):
            packets_lost_sp2 = int(sp2_recent[2]) - int(packets_received_sp2)

        # Update sp2 labels
        packets_sp2_received_variable.set("Packets Received - SP2: " + str(packets_received_sp2 - packets_lost_sp2))
        packets_sp2_lost_variable.set("Packets Lost - SP2: " + str(packets_lost_sp2))

    # Update the window
    time = timeit.default_timer()
    graph_container.canvas.draw()

    # Performance profiling
    print("canvas.draw(): " + str(round(timeit.default_timer() - time, 4)))

    graph_container.canvas.flush_events()
    window.update()

    # Sleep for .25 seconds
    #time.sleep(.25)
