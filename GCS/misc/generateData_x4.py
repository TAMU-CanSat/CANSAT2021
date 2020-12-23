import time
from random import random

i = 0
while True:
    i += 1

    # Add some data to all four files
    for ID in range(0, 4):
        file = open("datafiles\datafile{}.txt".format(ID), "a")
        file.write(str(i) + "," + str(round(random() * 100, 2)) + "\n")
        file.close()

    # Sleep for a second
    time.sleep(1)