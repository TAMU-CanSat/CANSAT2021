import tkinter as tk
from random import random
# py2
#import Tkinter as tk

light1status = 0


def light1():
    global light1status

    if light1status == 0:
        strongboxlt.config(bg = "green")
        light1status = 1
    else:
        strongboxlt.config(bg = "red")
        light1status = 0

f = tk.Tk()

strongboxlt = tk.Button(command = light1, text = "Strngbx Light", fg = "black", bg = "red", padx = 20, pady = 20)
strongboxlt.place(x = 45, y= 75)

f.mainloop()