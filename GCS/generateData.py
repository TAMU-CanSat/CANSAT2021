import time
from random import random

i = 0
while True:
    i += 1

    file = open("datafiles\datafile.txt", "a")
    file.write(str(i) + "," + str(round(random() * 100, 2)) + "\n")
    file.close()

    # Sleep for a second
    time.sleep(1)