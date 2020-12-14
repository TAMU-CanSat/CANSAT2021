import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

#################################################################

# Globals
MAX_DATAPOINTS = 50
DISPLAY_WIDTH_IN = 17
DISPLAY_HEIGHT_IN = 9
DISPLAY_DPI = None
PLOT_STYLE = "ggplot"

#################################################################

# Sets the matplotlib style
style.use(PLOT_STYLE)

# Define the pyplot figure
fig = plt.figure(figsize=(DISPLAY_WIDTH_IN, DISPLAY_HEIGHT_IN), dpi=DISPLAY_DPI)
fig.subplots_adjust(hspace=.3)

# Create four subplots in a 2x2 grid
ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)
plots = [ax1, ax2, ax3, ax4]

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
            if len(x_data) > MAX_DATAPOINTS:
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


# Run the animation
ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()
