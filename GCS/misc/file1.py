from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import style

import matplotlib.animation as animation

import tkinter
import numpy as np

def animate(i):
    pullData = open("datafile.txt")

window = tkinter.Tk()
window.wm_title("Plot test 1")

# DPI = dots per inch
fig = Figure(figsize=(5,4), dpi=100)

style.use("ggplot")

data = np.arange(0, 3, .01)
fig.add_subplot(111).plot(data, 2 * np.pi * data)

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.update()

def on_key_press(event):
    print("Pressed: {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    window.quit()
    window.destroy()


button = tkinter.Button(master=window, text="Quit", command=_quit)
button.pack()

tkinter.mainloop()
